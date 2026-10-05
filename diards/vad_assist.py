"""Does a VAD help Nemotron 3 Diarization? VAD-assisted variants, scored exactly like ``diards evaluate``.

Post-hoc variants use the cached Nemotron outputs (hypothesis RTTMs and 10 ms speaker probabilities written by
``diards evaluate``) and need no GPU:

* ``gate`` / ``gate+P``: hypothesis speech is kept only inside VAD speech (dilated by P seconds); for Silero (with
  and without the 30 s state reset), WebRTC (mode 2) and the energy VAD.
* ``fill``: frames inside VAD speech where no speaker is above 0.5 get the speaker with the highest probability.
* ``vad_decides``: ``gate`` + ``fill``, i.e. the VAD decides speech / non-speech and the model only decides who.

Protocol variants change the scoring region, not the hypothesis (reported separately; not comparable to the
official numbers): ``uem_span`` (UEM cut to first VAD speech - 1 s .. last VAD speech + 1 s) and ``uem_speech``
(UEM restricted to VAD speech +/- 0.5 s).

VAD-derived variants other than ``gate`` use ``silero_r30`` (Silero with the 30 s state reset, see diards.vads).

Re-inference variants run Nemotron (GPU, same settings as ``diards evaluate``) on modified audio for a sample of
sessions: ``trim`` (VAD non-speech longer than 1 s shortened to 0.5 s, output mapped back to original time) and
``zero`` (audio outside VAD speech +/- 0.25 s replaced by digital silence, same timeline).

Scoring: :class:`diards.score.Scorer`, collars 0 and 0.25 s (half-width), overlap scored, per-session UEM,
primary reference plus every ``rttm_alt`` variant; the baseline (cached hypotheses) is re-scored with the same code
and must reproduce ``results/nemotron/<tag>/results.json``.

Usage:
  python -m diards.vad_assist posthoc [--tags ami.sdm,...] [--out results/vad/pipeline]
  python -m diards.vad_assist rerun <tag> [--variants trim,zero,none] [--max-hours 1.0]
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from .annotation import Segment, intersect, merge_intervals, read_rttm_single, subtract, total_duration, write_rttm
from .config import work_root
from .core import NormalizedDataset, Session
from .evaluate import COLLARS, select_sessions
from .score import Scorer
from .vads import VadCache, frames_to_intervals, study_root, to_raster

RESULTS = Path(__file__).resolve().parents[1] / "results" / "nemotron"
VADS = ("silero_r30", "silero", "webrtc", "energy", "pyannote")


# ----------------------------------------------------------------------------- tags (= main agent's evaluations)

def parse_tag(tag: str) -> tuple[str, str]:
    """``chime6.farfield.dev`` -> (``chime6``, ``farfield``)."""
    name, view = tag.split(".")[:2]
    return name, view


def tag_sessions(tag: str, root=None) -> list[Session]:
    """The sessions the main agent scored for this tag (from its results.json), in its order."""
    name, view = parse_tag(tag)
    r = json.loads((RESULTS / tag / "results.json").read_text(encoding="utf-8"))
    ids = [row["session_id"] for row in r["per_session"]]
    by_id = {s.session_id: s for s in NormalizedDataset(name, root).sessions(view=view)}
    return [by_id[i] for i in ids]


def hyp_dir(tag: str) -> Path:
    name, view = parse_tag(tag)
    return work_root() / "nemotron" / f"{name}.{view}"


# ----------------------------------------------------------------------------- hypothesis transforms

def gate(hyp: list[Segment], speech, pad: float = 0.0) -> list[Segment]:
    keep = merge_intervals((max(0.0, a - pad), b + pad) for a, b in speech)
    out = []
    for spk in sorted({h.speaker for h in hyp}):
        ivs = merge_intervals((h.start, h.end) for h in hyp if h.speaker == spk)
        out += [Segment(round(a, 3), round(b, 3), spk) for a, b in intersect(ivs, keep)]
    return sorted(out)


def probs_to_segments(active: np.ndarray, frame: float) -> list[Segment]:
    segs = []
    for k in range(active.shape[1]):
        segs += [Segment(a, b, f"spk{k}") for a, b in frames_to_intervals(active[:, k], frame)]
    return sorted(segs)


def hyp_raster(hyp: list[Segment], n: int, frame: float) -> np.ndarray:
    """Frame x speaker activity of a Nemotron hypothesis (speakers are named ``spk<k>`` = probability column k)."""
    active = np.zeros((n, 0), bool)
    for h in hyp:
        k = int(h.speaker[3:])
        if k >= active.shape[1]:
            active = np.pad(active, ((0, 0), (0, k + 1 - active.shape[1])))
        active[:, k] |= to_raster([(h.start, h.end)], n, frame)
    return active


def fill_from_probs(probs: np.ndarray, frame: float, speech, threshold: float = 0.5,
                    gate_too: bool = False, hyp: list[Segment] | None = None) -> list[Segment]:
    """Threshold the speaker probabilities (or take the cached hypothesis ``hyp``, which avoids float16 rounding
    at the threshold); inside VAD speech, frames with no active speaker get the argmax speaker. With ``gate_too``
    frames outside VAD speech are cleared as well."""
    active = probs > threshold
    if hyp is not None:
        h = hyp_raster(hyp, len(probs), frame)
        active = np.zeros_like(active)
        active[:, : h.shape[1]] = h[:, : active.shape[1]]
    inside = to_raster(speech, len(probs), frame)
    empty = inside & ~active.any(axis=1)
    idx = np.flatnonzero(empty)
    active[idx, np.argmax(probs[idx], axis=1)] = True
    if gate_too:
        active &= inside[:, None]
    return probs_to_segments(active, frame)


def _same(a: list[Segment], b: list[Segment], tol: float = 1e-6) -> bool:
    return len(a) == len(b) and all(x.speaker == y.speaker and abs(x.start - y.start) < tol and abs(x.end - y.end) < tol
                                    for x, y in zip(a, b))


def uem_span(uem, speech, margin: float = 1.0):
    if not speech:
        return uem
    return intersect(merge_intervals(uem), [(max(0.0, speech[0][0] - margin), speech[-1][1] + margin)])


def uem_speech(uem, speech, margin: float = 0.5):
    return intersect(merge_intervals(uem), merge_intervals((max(0.0, a - margin), b + margin) for a, b in speech))


# ----------------------------------------------------------------------------- audio transforms (re-inference)

def trim_plan(speech, duration: float, max_sil: float = 1.0, keep: float = 0.5) -> list[tuple[float, float]]:
    """Pieces of the original timeline to keep: every non-speech stretch longer than ``max_sil`` is shortened to
    ``keep`` seconds (``keep / 2`` kept on each side)."""
    sil = subtract([(0.0, duration)], merge_intervals(speech))
    cut = [(a + keep / 2, b - keep / 2) for a, b in sil if b - a > max_sil]
    return subtract([(0.0, duration)], cut)


def apply_pieces(x: np.ndarray, pieces, sr: int = 16000) -> np.ndarray:
    return np.concatenate([x[int(round(a * sr)): int(round(b * sr))] for a, b in pieces]) if pieces else x[:0]


def map_back(segs: list[Segment], pieces) -> list[Segment]:
    """Map segments on the concatenated (trimmed) timeline back to original time, splitting at cuts."""
    offs, t = [], 0.0
    for a, b in pieces:
        offs.append((t, t + (b - a), a))
        t += b - a
    out = []
    for s in segs:
        for lo, hi, src in offs:
            a, b = max(s.start, lo), min(s.end, hi)
            if b > a:
                out.append(Segment(round(src + a - lo, 3), round(src + b - lo, 3), s.speaker))
    return sorted(out)


def zero_outside(x: np.ndarray, speech, margin: float = 0.25, sr: int = 16000) -> np.ndarray:
    y = np.zeros_like(x)
    for a, b in merge_intervals((max(0.0, a - margin), b + margin) for a, b in speech):
        i, j = int(a * sr), min(len(x), int(np.ceil(b * sr)))
        y[i:j] = x[i:j]
    return y


# ----------------------------------------------------------------------------- scoring (as diards.evaluate)

def score(sessions: list[Session], hyps: dict[str, list[Segment]], uems: dict | None = None,
          extra_refs: dict[str, dict[str, list[Segment]]] | None = None) -> dict:
    """``extra_refs``: additional references, ``{name: {session_id: segments}}``, scored like ``rttm_alt`` ones."""
    extra_refs = extra_refs or {}
    variants = sorted({k for s in sessions for k in s.alt_rttm} | set(extra_refs))
    scorers = {(ref, c): Scorer(c) for ref in ["primary", *variants] for c in COLLARS}
    rows = []
    for s in sessions:
        hyp = hyps[s.session_id]
        uem = (uems or {}).get(s.session_id, s.uem)
        row = {"session_id": s.session_id}
        for ref_name in ["primary", *variants]:
            if ref_name in extra_refs:
                if s.session_id not in extra_refs[ref_name]:
                    continue
                ref = extra_refs[ref_name][s.session_id]
            elif ref_name != "primary" and ref_name not in s.alt_rttm:
                continue
            else:
                ref = s.segments if ref_name == "primary" else s.alt_segments(ref_name)
            for c in COLLARS:
                row[f"{ref_name}@{c}"] = {k: round(v, 4) for k, v in scorers[(ref_name, c)](s.session_id, ref, hyp, uem).items()}
        rows.append(row)
    summary = {f"{ref}@{c}": {k: round(v, 4) for k, v in sc.summary().items()}
               for (ref, c), sc in scorers.items() if sc.der.accumulated_.get("total", 0)}
    return {"summary": summary, "per_session": rows}


# ----------------------------------------------------------------------------- experiments

def posthoc(tag: str, root=None, vads=VADS) -> dict:
    name, view = parse_tag(tag)
    sessions = tag_sessions(tag, root)
    hd = hyp_dir(tag)
    base = {s.session_id: read_rttm_single(hd / "hyp" / f"{s.session_id}.rttm") for s in sessions}
    caches = {s.session_id: VadCache.load(name, view, s.session_id) for s in sessions}
    vads = [v for v in vads if v != "pyannote" or all("pyannote_ivs" in c.data for c in caches.values())]
    speech = {v: {sid: merge_intervals(c.get(v)) for sid, c in caches.items()} for v in vads}
    out = {"tag": tag, "sessions": len(sessions), "hours": round(sum(s.duration for s in sessions) / 3600, 2),
           "variants": {}}

    def run(label, hyps, uems=None):
        t0 = time.time()
        out["variants"][label] = score(sessions, hyps, uems)
        p = out["variants"][label]["summary"]["primary@0.0"]
        print(f"  {tag:28s} {label:22s} DER {100 * p['der']:6.2f}  FA {100 * p['fa']:5.2f}  MISS {100 * p['miss']:5.2f}  "
              f"CONF {100 * p['conf']:5.2f}  ({time.time() - t0:.0f} s)", flush=True)

    run("baseline", base)
    for v in vads:
        run(f"gate:{v}", {sid: gate(h, speech[v][sid]) for sid, h in base.items()})
        run(f"gate+0.25:{v}", {sid: gate(h, speech[v][sid], 0.25) for sid, h in base.items()})
    probs = {}
    for s in sessions:
        p = hd / "probs" / f"{s.session_id}.npz"
        if p.exists():
            with np.load(p) as z:
                probs[s.session_id] = (z["probs"].astype(np.float32), float(z["frame_s"]))
    if len(probs) == len(sessions):
        sp = speech["silero_r30"]
        run("fill:silero_r30", {sid: fill_from_probs(pr, fr, sp[sid], hyp=base[sid]) for sid, (pr, fr) in probs.items()})
        run("vad_decides:silero_r30", {sid: fill_from_probs(pr, fr, sp[sid], gate_too=True, hyp=base[sid])
                                   for sid, (pr, fr) in probs.items()})
        # sanity: the rasterised cached hypothesis must give back the cached hypothesis
        out["hyp_raster_roundtrip"] = all(_same(probs_to_segments(hyp_raster(base[sid], len(pr), fr), fr), base[sid])
                                          for sid, (pr, fr) in list(probs.items())[:3])
    else:
        out["note"] = f"probabilities cached for {len(probs)}/{len(sessions)} sessions; fill variants skipped"
    uems = {s.session_id: s.uem for s in sessions}
    sp = speech["silero_r30"]
    run("uem_span:silero_r30", base, {sid: uem_span(u, sp[sid]) for sid, u in uems.items()})
    run("uem_speech:silero_r30", base, {sid: uem_speech(u, sp[sid]) for sid, u in uems.items()})
    out["uem_hours"] = {
        "official": round(sum(total_duration(merge_intervals(u)) for u in uems.values()) / 3600, 3),
        "uem_span": round(sum(total_duration(uem_span(u, sp[sid])) for sid, u in uems.items()) / 3600, 3),
        "uem_speech": round(sum(total_duration(uem_speech(u, sp[sid])) for sid, u in uems.items()) / 3600, 3),
    }
    return out


def rerun(tag: str, variants=("none", "trim", "zero"), max_hours: float = 1.0, limit: int | None = None,
          root=None, diarizer=None) -> dict:
    """Re-run Nemotron on VAD-modified audio for a deterministic sample of the tag's sessions."""
    import soundfile as sf

    from .evaluate import NemotronDiarizer

    name, view = parse_tag(tag)
    sessions = select_sessions(tag_sessions(tag, root), limit=limit, max_hours=max_hours)
    base = {s.session_id: read_rttm_single(hyp_dir(tag) / "hyp" / f"{s.session_id}.rttm") for s in sessions}
    dz = diarizer or NemotronDiarizer()
    work = study_root() / "rerun" / tag
    out = {"tag": tag, "sessions": [s.session_id for s in sessions],
           "hours": round(sum(s.duration for s in sessions) / 3600, 3), "variants": {}, "audio_hours": {}}
    out["variants"]["baseline(cached)"] = score(sessions, base)
    for var in variants:
        hyps, t_proc, n_audio = {}, 0.0, 0.0
        for s in sessions:
            hp = work / var / f"{s.session_id}.rttm"
            x, sr = sf.read(str(s.audio_path), dtype="float32")
            speech = merge_intervals(VadCache.load(name, view, s.session_id).silero(reset=True))
            pieces = None
            if var == "trim":
                pieces = trim_plan(speech, len(x) / sr)
                y = apply_pieces(x, pieces, sr)
            elif var == "zero":
                y = zero_outside(x, speech)
            else:
                y = x
            n_audio += len(y) / sr
            if hp.exists():
                hyps[s.session_id] = read_rttm_single(hp)
                continue
            t0 = time.time()
            segs = dz.segments(dz.probs(y))
            t_proc += time.time() - t0
            if pieces is not None:
                segs = map_back(segs, pieces)
            write_rttm(hp, s.session_id, segs)
            hyps[s.session_id] = segs
        out["variants"][var] = score(sessions, hyps)
        out["audio_hours"][var] = round(n_audio / 3600, 3)
        p = out["variants"][var]["summary"]["primary@0.0"]
        print(f"  {tag:28s} rerun:{var:6s} DER {100 * p['der']:6.2f} FA {100 * p['fa']:5.2f} MISS {100 * p['miss']:5.2f} "
              f"CONF {100 * p['conf']:5.2f}  audio {n_audio / 3600:.2f} h  gpu {t_proc:.0f} s", flush=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("posthoc")
    p.add_argument("--tags", help="comma-separated results/nemotron tags (default: all)")
    p.add_argument("--out", default="results/vad/pipeline")
    p = sub.add_parser("rerun")
    p.add_argument("tag")
    p.add_argument("--variants", default="none,trim,zero")
    p.add_argument("--max-hours", type=float, default=1.0)
    p.add_argument("--limit", type=int)
    p.add_argument("--out", default="results/vad/pipeline")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "posthoc":
        tags = a.tags.split(",") if a.tags else sorted(p.name for p in RESULTS.iterdir() if (p / "results.json").exists())
        for tag in tags:
            try:
                r = posthoc(tag)
            except FileNotFoundError as exc:
                print(f"  {tag}: skipped ({exc})", flush=True)
                continue
            (out / f"posthoc.{tag}.json").write_text(json.dumps(r, indent=1), encoding="utf-8", newline="\n")
    else:
        r = rerun(a.tag, tuple(a.variants.split(",")), a.max_hours, a.limit)
        (out / f"rerun.{a.tag}.json").write_text(json.dumps(r, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
