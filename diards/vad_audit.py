"""Audit a dataset's reference speech against independent voice-activity detectors (Silero VAD study).

Per session, reference speech ``R`` is the union of the RTTM segments inside the UEM and VAD speech ``V`` the
detector's intervals inside the UEM. Reported (seconds, and % of reference speech):

* ``fa`` = |V - R| and ``miss`` = |R - V|: frame-level disagreement at collar 0 (the VAD's speech-detection error
  if the reference were right).
* ``unref``: VAD speech farther than ``tol`` (0.25 s) from any reference speech, in chunks >= ``min_len`` (0.5 s).
  Candidates for unannotated speech (or VAD false alarms on noise, music, laughter).
* ``unvoiced``: reference speech farther than ``tol`` from any VAD speech, in chunks >= ``min_len``. Candidates for
  padded boundaries, pauses inside segments, non-speech labelled as speech (or VAD misses).
* boundary offsets of reference "islands" (reference speech separated by >= 0.3 s of silence) against the VAD
  speech overlapping them: ``onset = vad_start - ref_start`` and ``offset = ref_end - vad_end``, so positive means
  the reference is *wider* than the VAD. Onsets/offsets where the VAD speech runs into the neighbouring island
  are skipped (ambiguous).
* ``best_lag``: time shift of the reference that maximises frame agreement with the VAD (50 ms raster, +/- 5 s);
  a clear gain away from 0 means the reference is offset in time.

The longest ``unref`` / ``unvoiced`` regions are listed with evidence from the other witnesses: coverage by the
other VADs, by the cached Nemotron hypothesis, by word timings, and the region's level above the session's noise
floor, so they can be checked without listening.

Usage: python -m diards.vad_audit <dataset> [--view V] [--vads silero_r30,silero,webrtc,energy,nemotron] [--out results/vad/audit]
"""
from __future__ import annotations

import argparse
import bisect
import json
from pathlib import Path

import numpy as np

from .annotation import intersect, merge_intervals, read_rttm_single, subtract, total_duration
from .config import work_root
from .core import NormalizedDataset, Session
from .vads import ENERGY_HOP, SILERO_HOP, VadCache, cache_path, nemotron_intervals

AUDIT_VIEWS = {"ami": "ihm-mix", "icsi": "ihm-mix", "notsofar1": "ihm-mix", "chime6": "ihm-mix", "dipco": "ihm-mix",
               "libricss": "clean-mix", "easycom": "glasses", "primock57": "mix"}
DEFAULT_VADS = ("silero_r30", "silero", "webrtc", "energy", "pyannote", "nemotron")
TOL = 0.25
MIN_LEN = 0.5
ISLAND_GAP = 0.3


# ----------------------------------------------------------------------------- interval helpers

def dilate(ivs, d: float, lo: float = 0.0, hi: float = float("inf")):
    return merge_intervals((max(lo, a - d), min(hi, b + d)) for a, b in ivs)


def long_chunks(ivs, min_len: float):
    return [(a, b) for a, b in ivs if b - a >= min_len]


def coverage(ivs, a: float, b: float, starts=None) -> float:
    """Fraction of ``[a, b)`` covered by sorted, disjoint ``ivs`` (``starts`` = their start times, for bisect)."""
    if b <= a:
        return 0.0
    starts = starts if starts is not None else [s for s, _ in ivs]
    i = max(0, bisect.bisect_right(starts, a) - 1)
    cov = 0.0
    while i < len(ivs) and ivs[i][0] < b:
        cov += max(0.0, min(b, ivs[i][1]) - max(a, ivs[i][0]))
        i += 1
    return cov / (b - a)


def coverage_metrics(ref, vad, tol: float = TOL, min_len: float = MIN_LEN) -> dict:
    """``ref`` and ``vad`` already restricted to the UEM, sorted and merged."""
    unref = long_chunks(subtract(vad, dilate(ref, tol)), min_len)
    unvoiced = long_chunks(subtract(ref, dilate(vad, tol)), min_len)
    return {"ref_s": total_duration(ref), "vad_s": total_duration(vad),
            "fa_s": total_duration(subtract(vad, ref)), "miss_s": total_duration(subtract(ref, vad)),
            "unref_s": total_duration(unref), "unvoiced_s": total_duration(unvoiced),
            "_unref": unref, "_unvoiced": unvoiced}


def boundary_offsets(ref, vad, island_gap: float = ISLAND_GAP) -> dict:
    """Onset / offset deltas of reference islands vs the VAD (positive = reference wider). See module doc."""
    islands = merge_intervals(ref, gap=island_gap)
    vstarts = [a for a, _ in vad]
    onsets, offsets, unmatched = [], [], 0
    for i, (a, b) in enumerate(islands):
        prev_end = islands[i - 1][1] if i else -np.inf
        next_start = islands[i + 1][0] if i + 1 < len(islands) else np.inf
        j = max(0, bisect.bisect_right(vstarts, a) - 1)
        m = []
        while j < len(vad) and vad[j][0] < b:
            if vad[j][1] > a:
                m.append(vad[j])
            j += 1
        if not m:
            unmatched += 1
            continue
        if m[0][0] > prev_end:
            onsets.append(m[0][0] - a)
        if m[-1][1] < next_start:
            offsets.append(b - m[-1][1])
    return {"islands": len(islands), "islands_without_vad": unmatched, "onsets": onsets, "offsets": offsets}


def best_lag(ref, vad, duration: float, max_lag: float = 5.0, step: float = 0.05) -> dict:
    """Shift of the reference (seconds, positive = reference too early) that maximises agreement with the VAD."""
    n = int(duration / step) + 1

    def raster(ivs):
        m = np.zeros(n, bool)
        for a, b in ivs:
            m[int(a / step): int(b / step)] = True
        return m

    r, v = raster(ref), raster(vad)
    ks = np.arange(-int(round(max_lag / step)), int(round(max_lag / step)) + 1)
    agree = np.empty(len(ks))
    for i, k in enumerate(ks):
        rr, vv = (r[: n - k], v[k:]) if k >= 0 else (r[-k:], v[: n + k])
        agree[i] = np.mean(rr == vv) if len(rr) else 0.0
    i0, ib = int(np.argmin(np.abs(ks))), int(np.argmax(agree))
    return {"best_lag_s": round(float(ks[ib] * step), 2), "agreement_at_0": round(float(agree[i0]), 4),
            "gain": round(float(agree[ib] - agree[i0]), 4)}


def pct(x, qs=(10, 25, 50, 75, 90)) -> dict:
    if not len(x):
        return {}
    v = np.percentile(np.asarray(x), qs)
    return {f"p{q}": round(float(y), 3) for q, y in zip(qs, v)}


# ----------------------------------------------------------------------------- per session

def _words_ivs(s: Session):
    w = s.words
    return merge_intervals((x["start"], x["end"]) for x in w) if w else None


def _level(cache: VadCache, a: float, b: float, floor: float) -> float | None:
    e = cache.data["energy_db"]
    i, j = int(a / ENERGY_HOP), max(int(a / ENERGY_HOP) + 1, int(b / ENERGY_HOP))
    seg = e[i:j].astype(np.float32)
    return round(float(np.median(seg)) - floor, 1) if len(seg) else None


def audit_session(s: Session, vads, view: str, refs: dict, hyp_path: Path | None, top: int = 5) -> dict:
    cache = VadCache.load(s.dataset, view, s.session_id)
    uem = merge_intervals(s.uem)
    detected = {}
    for v in vads:
        if v == "nemotron":
            if hyp_path and hyp_path.exists():
                detected[v] = intersect(nemotron_intervals(hyp_path), uem)
        elif v == "pyannote":
            if "pyannote_ivs" in cache.data:
                detected[v] = intersect(merge_intervals(cache.get(v)), uem)
        else:
            detected[v] = intersect(merge_intervals(cache.get(v)), uem)
    e = cache.data["energy_db"].astype(np.float32)
    valid = e[e > -100]
    floor = float(np.percentile(valid, 10)) if valid.size else 0.0
    words = _words_ivs(s)
    row = {"session_id": s.session_id, "split": s.split, "duration": round(s.duration, 2),
           "uem_s": round(total_duration(uem), 2), "refs": {}}
    starts = {k: [a for a, _ in ivs] for k, ivs in detected.items()}
    for ref_name, segs in refs.items():
        ref = intersect(merge_intervals((g.start, g.end) for g in segs), uem)
        rr = {}
        for v, ivs in detected.items():
            m = coverage_metrics(ref, ivs)
            b = boundary_offsets(ref, ivs)
            rec = {k: round(x, 2) for k, x in m.items() if not k.startswith("_")}
            rec.update(islands=b["islands"], islands_without_vad=b["islands_without_vad"],
                       onsets=[round(x, 3) for x in b["onsets"]], offsets=[round(x, 3) for x in b["offsets"]])
            if ref_name == "primary":
                rec["lag"] = best_lag(ref, ivs, s.duration)
                if v not in ("nemotron", "pyannote"):
                    rstarts = [a for a, _ in ref]
                    rec["top_unref"] = [_evidence(a, b_, v, detected, starts, words, cache, floor, ref, rstarts)
                                        for a, b_ in sorted(m["_unref"], key=lambda t: t[0] - t[1])[:top]]
                    rec["top_unvoiced"] = [_evidence(a, b_, v, detected, starts, words, cache, floor, ref, rstarts)
                                           for a, b_ in sorted(m["_unvoiced"], key=lambda t: t[0] - t[1])[:top]]
            rr[v] = rec
        row["refs"][ref_name] = rr
    return row


def _evidence(a, b, me, detected, starts, words, cache, floor, ref, rstarts) -> dict:
    ev = {"start": round(a, 2), "end": round(b, 2), "dur": round(b - a, 2),
          "level_db_above_floor": _level(cache, a, b, floor),
          "ref_cov": round(coverage(ref, a, b, rstarts), 2)}
    for v, ivs in detected.items():
        if v != me:
            ev[f"{v}_cov"] = round(coverage(ivs, a, b, starts[v]), 2)
    if words is not None:
        ev["words_cov"] = round(coverage(words, a, b), 2)
    i, j = int(a / SILERO_HOP), max(int(a / SILERO_HOP) + 1, int(b / SILERO_HOP))
    for key in ("silero", "silero_r30"):
        p = cache.data[key]
        ev[f"{key}_mean_prob"] = round(float(np.mean(p[i:j].astype(np.float32))), 2) if j <= len(p) else None
    return ev


# ----------------------------------------------------------------------------- per dataset

def audit_dataset(name: str, view: str | None = None, vads=DEFAULT_VADS, root=None, out=None, splits=None,
                  hyp_view: str | None = None, echo: bool = True) -> dict:
    ds = NormalizedDataset(name, root)
    view = view or AUDIT_VIEWS.get(name, ds.default_view)
    hyp_dir = work_root() / "nemotron" / f"{name}.{hyp_view or view}" / "hyp"
    rows = []
    for s in ds.sessions(view=view):
        if splits and s.split not in splits:
            continue
        if not cache_path(name, view, s.session_id).exists():
            continue
        refs = {"primary": s.segments, **{k: s.alt_segments(k) for k in sorted(s.alt_rttm)}}
        rows.append(audit_session(s, vads, view, refs, hyp_dir / f"{s.session_id}.rttm"))
    summary = summarize(rows)
    for r in rows:  # keep the JSON small: per-session boundary deltas as medians only
        for by_vad in r["refs"].values():
            for x in by_vad.values():
                x["onset_p50"] = pct(x.pop("onsets"), (50,)).get("p50")
                x["offset_p50"] = pct(x.pop("offsets"), (50,)).get("p50")
    result = {"dataset": name, "view": view, "vads": list(vads), "tol_s": TOL, "min_len_s": MIN_LEN,
              "island_gap_s": ISLAND_GAP, "sessions": len(rows), "summary": summary, "per_session": rows}
    if out:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"audit.{name}.{view}.json").write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    if echo:
        for ref_name, by_vad in result["summary"].items():
            for v, x in by_vad.items():
                print(f"{name}.{view} [{ref_name}] {v:8s} sessions {x['sessions']:4d} ref {x['ref_h']:.2f} h  "
                      f"FA {x['fa_pct']:5.1f}%  miss {x['miss_pct']:5.1f}%  unref {x['unref_pct']:5.2f}%  "
                      f"unvoiced {x['unvoiced_pct']:5.2f}%  onset p50 {x['onset'].get('p50')}  "
                      f"offset p50 {x['offset'].get('p50')}", flush=True)
    return result


def summarize(rows) -> dict:
    out: dict = {}
    for r in rows:
        for ref_name, by_vad in r["refs"].items():
            for v, x in by_vad.items():
                acc = out.setdefault(ref_name, {}).setdefault(v, {"sessions": 0, "ref_s": 0.0, "vad_s": 0.0, "fa_s": 0.0,
                                                                  "miss_s": 0.0, "unref_s": 0.0, "unvoiced_s": 0.0,
                                                                  "islands": 0, "islands_without_vad": 0,
                                                                  "onsets": [], "offsets": [], "uem_s": 0.0,
                                                                  "lags": []})
                acc["sessions"] += 1
                acc["uem_s"] += r["uem_s"]
                for k in ("ref_s", "vad_s", "fa_s", "miss_s", "unref_s", "unvoiced_s", "islands", "islands_without_vad"):
                    acc[k] += x[k]
                acc["onsets"] += x["onsets"]
                acc["offsets"] += x["offsets"]
                if "lag" in x:
                    acc["lags"].append(x["lag"])
    summary: dict = {}
    for ref_name, by_vad in out.items():
        for v, a in by_vad.items():
            ref = a["ref_s"] or 1.0
            per = {r["session_id"]: r["refs"][ref_name][v] for r in rows if v in r["refs"].get(ref_name, {})}
            on, off = np.asarray(a["onsets"]), np.asarray(a["offsets"])
            shifted = [x for x in a["lags"] if abs(x["best_lag_s"]) >= 0.3 and x["gain"] >= 0.02]
            summary.setdefault(ref_name, {})[v] = {
                "sessions": a["sessions"], "ref_h": round(a["ref_s"] / 3600, 3), "vad_h": round(a["vad_s"] / 3600, 3),
                "uem_h": round(a["uem_s"] / 3600, 3),
                "fa_pct": round(100 * a["fa_s"] / ref, 2), "miss_pct": round(100 * a["miss_s"] / ref, 2),
                "unref_pct": round(100 * a["unref_s"] / ref, 2), "unvoiced_pct": round(100 * a["unvoiced_s"] / ref, 2),
                "islands": a["islands"],
                "islands_without_vad_pct": round(100 * a["islands_without_vad"] / max(a["islands"], 1), 2),
                "onset": {**pct(on), "n": len(on), "frac_gt_0.25": round(float(np.mean(on > 0.25)), 3) if len(on) else None,
                          "frac_lt_-0.25": round(float(np.mean(on < -0.25)), 3) if len(on) else None},
                "offset": {**pct(off), "n": len(off), "frac_gt_0.25": round(float(np.mean(off > 0.25)), 3) if len(off) else None,
                           "frac_lt_-0.25": round(float(np.mean(off < -0.25)), 3) if len(off) else None},
                "sessions_time_shifted": len(shifted),
                "worst_unref": sorted(((k, round(100 * x["unref_s"] / x["ref_s"], 2) if x["ref_s"] else None)
                                       for k, x in per.items()), key=lambda t: -(t[1] or 0))[:10],
                "worst_unvoiced": sorted(((k, round(100 * x["unvoiced_s"] / x["ref_s"], 2) if x["ref_s"] else None)
                                          for k, x in per.items()), key=lambda t: -(t[1] or 0))[:10],
                "shifted": sorted(((k, x["lag"]["best_lag_s"], x["lag"]["gain"]) for k, x in per.items()
                                   if "lag" in x and abs(x["lag"]["best_lag_s"]) >= 0.3 and x["lag"]["gain"] >= 0.02),
                                  key=lambda t: -t[2])[:10],
            }
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset")
    ap.add_argument("--view")
    ap.add_argument("--hyp-view", help="view whose cached Nemotron hypotheses to use (default: --view)")
    ap.add_argument("--split", action="append", dest="splits")
    ap.add_argument("--vads", default=",".join(DEFAULT_VADS))
    ap.add_argument("--root")
    ap.add_argument("--out", default="results/vad/audit")
    a = ap.parse_args(argv)
    audit_dataset(a.dataset, a.view, tuple(a.vads.split(",")), a.root, a.out, a.splits, a.hyp_view)


if __name__ == "__main__":
    main()
