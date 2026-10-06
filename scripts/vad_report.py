"""Collect the Silero VAD study outputs into results/vad/README.md (tables) and results/vad/summary.json.

Inputs (all produced by the commands listed in results/vad/README.md):
  results/vad/audit/audit.<dataset>.<view>.json       python -m diards.vad_audit
  results/vad/whisper/whisper.<dataset>.<view>.json   scripts/vad_whisper_check.py
  results/vad/pipeline/posthoc.<tag>.json             python -m diards.vad_assist posthoc
  results/vad/pipeline/rerun.<tag>.json               python -m diards.vad_assist rerun
  results/vad/primock57/primock57_channels.json       scripts/vad_primock57_channels.py
  results/vad/dataprep.json                           scripts/vad_dataprep.py
  results/nemotron/<tag>/results.json                 the main benchmark (Nemotron error per reference)

Usage: python scripts/vad_report.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from diards.core import NormalizedDataset  # noqa: E402

V = ROOT / "results" / "vad"
DETECTORS = ("silero_x2", "silero", "silero_r30", "webrtc", "energy", "pyannote", "nemotron")
LABEL = {"silero_x2": "Silero x2", "silero_r30": "Silero (30 s reset)", "silero": "Silero (stock)", "webrtc": "WebRTC (mode 2)",
         "energy": "energy", "pyannote": "pyannote seg-3.0", "nemotron": "Nemotron (union)"}
CMDS = """```bash
# Windows 11, D:\\diarization-data\\envs\\diar: Python 3.12.15, torch 2.11.0+cu128, numpy 2.5.3, pyannote.metrics 4.1,
# transformers 5.19.0.dev0; plus `pip install --no-deps silero-vad==6.2.3` and webrtcvad-wheels 2.0.14.post1.
# pyannote.audio 4.0.7 only in a separate venv: python -m venv --system-site-packages D:\\diarization-data\\envs\\vad
# DIARDS_BASE=D:\\diarization-data (VAD cache: <base>/vad-study/vad, override with DIARDS_VAD_STUDY)
WORKERS=8 bash scripts/vad_compute_all.sh                    # Silero (stock + 30 s reset) / WebRTC / energy cache, CPU
<envs/vad python> scripts/vad_pyannote.py                    # pyannote segmentation-3.0 on evaluated subsets, GPU
for d in <each of the 18 datasets>; do
  python -m diards.vad_audit $d                              # results/vad/audit/audit.<dataset>.<view>.json
  python scripts/vad_whisper_check.py $d                     # results/vad/whisper/whisper.<dataset>.<view>.json (GPU)
done
python scripts/vad_whisper_check.py --rescore                # transcript classes + summaries
JOBS=6 bash scripts/vad_pipeline_all.sh                      # results/vad/pipeline/posthoc.<tag>.json (CPU)
for t in <each results/nemotron tag>; do
  python -m diards.vad_assist rerun $t --max-hours 1.0       # results/vad/pipeline/rerun.<tag>.json (GPU)
done
python scripts/vad_reset_check.py                            # results/vad/reset_check.json (Silero drop-outs)
python scripts/vad_primock57_channels.py --whisper           # results/vad/primock57/
python scripts/vad_dataprep.py                               # results/vad/dataprep.json
python scripts/vad_uem_check.py                              # results/vad/uem_check.json
python scripts/vad_worst_cases.py                            # results/vad/worst_cases.md
python scripts/vad_report.py                                 # this README + results/vad/summary.json
```"""


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def f(x, nd=1, pct=False):
    if x is None:
        return "-"
    return f"{100 * x:.{nd}f}" if pct else f"{x:.{nd}f}"


def grade(name):
    try:
        return NormalizedDataset(name).meta.get("gt_rating", "")
    except Exception:
        return ""


def audits():
    out = {}
    for p in sorted((V / "audit").glob("audit.*.json")):
        r = load(p)
        out[r["dataset"]] = r
    return out


def nemotron_results():
    out = {}
    for p in sorted((ROOT / "results" / "nemotron").glob("*/results.json")):
        out[p.parent.name] = load(p)
    return out


def table_audit(A):
    lines = ["| dataset | view | GT | sessions | ref speech h | Silero speech h | FA % | miss % | unannotated % | "
             "silent-ref % | onset p50 s | offset p50 s | time-shifted sessions |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, r in A.items():
        x = r["summary"]["primary"].get("silero_x2")
        if not x:
            continue
        lines.append(f"| {name} | {r['view']} | {grade(name)} | {x['sessions']} | {x['ref_h']:.2f} | {x['vad_h']:.2f} | "
                     f"{x['fa_pct']:.1f} | {x['miss_pct']:.1f} | {x['unref_pct']:.2f} | {x['unvoiced_pct']:.2f} | "
                     f"{f(x['onset'].get('p50'), 3)} | {f(x['offset'].get('p50'), 3)} | {x['sessions_time_shifted']} |")
    return "\n".join(lines)


def table_detectors(A, key):
    """Every detector on the same sessions (those with pyannote and Nemotron outputs, i.e. the evaluated subset)."""
    dets = [d for d in DETECTORS]
    lines = ["| dataset | sessions | " + " | ".join(LABEL[d] for d in dets) + " |", "|---|---:|" + "---:|" * len(dets)]
    for name, r in A.items():
        c = r.get("common_subset", {"sessions": r["sessions"], "summary": r["summary"]})
        s = c["summary"]["primary"]
        lines.append(f"| {name} | {c['sessions']} | " + " | ".join(f(s[d][key], 2) if d in s else "-" for d in dets) + " |")
    return "\n".join(lines)


def whisper_rows():
    out = {}
    for p in sorted((V / "whisper").glob("whisper.*.json")):
        r = load(p)
        out[r["dataset"]] = r
    return out


def table_whisper(W):
    """Cells: strict speech / verbal (strict + 1-2 words or fillers) / regions checked; laughter in brackets."""
    kinds = [("unref", "silero_x2"), ("unref", "energy"), ("unref", "webrtc"),
             ("unvoiced", "silero_x2"), ("unvoiced", "energy"), ("unvoiced", "webrtc"), ("control", None)]
    head = ["unannotated: Silero", "unannotated: energy", "unannotated: WebRTC",
            "silent-ref: Silero", "silent-ref: energy", "silent-ref: WebRTC", "control (both silent)"]
    lines = ["| dataset | " + " | ".join(head) + " |", "|---|" + "---:|" * len(head)]
    tot = {k: [0, 0, 0, 0] for k in kinds}
    for name, r in W.items():
        cells = []
        for kind, vad in kinds:
            key = f"{kind}:{vad}" if vad else "control"
            d = r["summary"].get(key)
            if d:
                c = d["classes"]
                verbal = c["speech"] + c["short"]
                cells.append(f"{c['speech']} / {verbal} / {d['regions']}" + (f" ({c['laughter']} laugh)" if c["laughter"] else ""))
                for i, v in enumerate((c["speech"], verbal, c["laughter"], d["regions"])):
                    tot[(kind, vad)][i] += v
            else:
                cells.append("-")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines.append("| **all** | " + " | ".join(
        f"**{a} / {v} / {n}** ({100 * a / n:.0f}% / {100 * v / n:.0f}%)" if n else "-" for a, v, l, n in tot.values()) + " |")
    return "\n".join(lines), {f"{k}:{v}": dict(zip(("speech", "verbal", "laughter", "regions"), t))
                              for (k, v), t in tot.items()}


def table_refs(A, N):
    """Boundary offsets per reference variant vs Silero, next to Nemotron's error against the same reference."""
    lines = ["| dataset | reference | ref speech h | onset p25 / p50 / p75 s | offset p25 / p50 / p75 s | "
             "ref speech Silero calls silence % | Nemotron miss % | Nemotron FA % | Nemotron DER % (c=0) |",
             "|---|---|---:|---|---|---:|---:|---:|---:|"]
    pairs = []
    for name, r in A.items():
        tags = [t for t in N if t.split(".")[0] == name and t.split(".")[1] == r["view"]]
        for ref_name, by in r["summary"].items():
            x = by.get("silero_x2")
            if not x:
                continue
            nem = None
            for t in tags:
                nem = N[t]["summary"].get(f"{ref_name}@0.0")
                if nem:
                    break
            on, off = x["onset"], x["offset"]
            lines.append(f"| {name} | {ref_name} | {x['ref_h']:.2f} | {f(on.get('p25'), 2)} / {f(on.get('p50'), 2)} / "
                         f"{f(on.get('p75'), 2)} | {f(off.get('p25'), 2)} / {f(off.get('p50'), 2)} / {f(off.get('p75'), 2)} | "
                         f"{x['miss_pct']:.1f} | {f(nem and nem['miss'], 1, True)} | {f(nem and nem['fa'], 1, True)} | "
                         f"{f(nem and nem['der'], 1, True)} |")
    return "\n".join(lines)


FARFIELD_VIEWS = {"sdm", "sc", "farfield", "glasses"}
CORR_DETECTORS = ("silero_x2", "silero", "pyannote", "webrtc", "energy")


def correlation(N, root=None):
    """Across every (evaluated tag, reference) pair: does a detector's disagreement with the reference, computed on
    exactly the sessions and audio Nemotron was scored on, predict Nemotron's miss / FA against that reference?"""
    from diards.annotation import intersect, merge_intervals, subtract, total_duration
    from diards.vad_assist import tag_sessions
    from diards.vads import VadCache

    rows = []
    for tag, res in N.items():
        name, view = tag.split(".")[:2]
        try:
            sessions = tag_sessions(tag, root)
            caches = {s.session_id: VadCache.load(name, view, s.session_id) for s in sessions}
        except FileNotFoundError:
            continue
        dets = [d for d in CORR_DETECTORS if d != "pyannote" or all("pyannote_ivs" in c.data for c in caches.values())]
        speech = {d: {sid: merge_intervals(c.get(d)) for sid, c in caches.items()} for d in dets}
        refs = ["primary"] + sorted({k for s in sessions for k in s.alt_rttm})
        for ref_name in refs:
            nem = res["summary"].get(f"{ref_name}@0.0")
            if not nem:
                continue
            acc = {d: [0.0, 0.0] for d in dets}
            ref_s = 0.0
            for s in sessions:
                if ref_name != "primary" and ref_name not in s.alt_rttm:
                    continue
                segs = s.segments if ref_name == "primary" else s.alt_segments(ref_name)
                uem = merge_intervals(s.uem)
                ref = intersect(merge_intervals((g.start, g.end) for g in segs), uem)
                ref_s += total_duration(ref)
                for d in dets:
                    vad = intersect(speech[d][s.session_id], uem)
                    acc[d][0] += total_duration(subtract(ref, vad))
                    acc[d][1] += total_duration(subtract(vad, ref))
            if ref_s:
                row = {"tag": tag, "reference": ref_name, "farfield": view in FARFIELD_VIEWS,
                       "nemotron_miss_pct": round(100 * nem["miss"], 2), "nemotron_fa_pct": round(100 * nem["fa"], 2),
                       "nemotron_der_pct": round(100 * nem["der"], 2)}
                for d in dets:
                    row[f"{d}_miss_pct"] = round(100 * acc[d][0] / ref_s, 2)
                    row[f"{d}_fa_pct"] = round(100 * acc[d][1] / ref_s, 2)
                rows.append(row)
    stats = {}
    from scipy.stats import pearsonr, spearmanr

    for subset, keep in (("all", lambda r: True), ("close_talk_and_single_channel", lambda r: not r["farfield"]),
                         ("far_field", lambda r: r["farfield"])):
        sub = [r for r in rows if keep(r)]
        for d in CORR_DETECTORS:
            for a, b in ((f"{d}_miss_pct", "nemotron_miss_pct"), (f"{d}_fa_pct", "nemotron_fa_pct")):
                pts = [(r[a], r[b]) for r in sub if a in r]
                if len(pts) < 5:
                    continue
                x, y = np.array(pts).T
                stats.setdefault(subset, {})[f"{a}~{b}"] = {
                    "n": len(pts), "pearson": round(float(pearsonr(x, y)[0]), 3),
                    "spearman": round(float(spearmanr(x, y)[0]), 3)}
    return rows, stats


def table_corr_stats(stats):
    lines = ["| subset | detector | n | miss vs Nemotron miss: Pearson / Spearman | FA vs Nemotron FA: Pearson / Spearman |",
             "|---|---|---:|---|---|"]
    for subset, st in stats.items():
        for d in CORR_DETECTORS:
            m, fa = st.get(f"{d}_miss_pct~nemotron_miss_pct"), st.get(f"{d}_fa_pct~nemotron_fa_pct")
            if m and fa:
                lines.append(f"| {subset} | {LABEL[d]} | {m['n']} | {m['pearson']:.2f} / {m['spearman']:.2f} | "
                             f"{fa['pearson']:.2f} / {fa['spearman']:.2f} |")
    return "\n".join(lines)


def table_corr(rows):
    lines = ["| tag | reference | Silero x2 miss % | pyannote miss % | Nemotron miss % | Silero x2 FA % | Nemotron FA % | "
             "Nemotron DER % |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in sorted(rows, key=lambda r: (r["farfield"], -r["silero_x2_miss_pct"])):
        lines.append(f"| {r['tag']} | {r['reference']} | {r['silero_x2_miss_pct']:.1f} | "
                     f"{f(r.get('pyannote_miss_pct'), 1)} | {r['nemotron_miss_pct']:.1f} | "
                     f"{r['silero_x2_fa_pct']:.1f} | {r['nemotron_fa_pct']:.1f} | {r['nemotron_der_pct']:.1f} |")
    return "\n".join(lines)


POSTHOC = ["gate:silero_x2", "gate+0.25:silero_x2", "gate:silero", "gate:silero_r30", "gate:webrtc", "gate:energy", "gate:pyannote",
           "gate+0.25:pyannote", "fill:silero_x2", "vad_decides:silero_x2"]


def table_posthoc(P, key):
    cols = [c for c in POSTHOC if any(c in r["variants"] for r in P.values())]
    lines = ["| tag | sessions | baseline DER % | " + " | ".join(cols) + " |", "|---|---:|---:|" + "---:|" * len(cols)]
    for tag, r in P.items():
        b = r["variants"]["baseline"]["summary"].get(key)
        if not b:
            continue
        cells = []
        for c in cols:
            v = r["variants"].get(c, {}).get("summary", {}).get(key)
            cells.append(f"{100 * (v['der'] - b['der']):+.2f}" if v else "-")
        lines.append(f"| {tag} | {r['sessions']} | {100 * b['der']:.2f} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def table_posthoc_components(P, key, variant):
    lines = ["| tag | baseline FA / miss / conf % | " + variant + " FA / miss / conf % |", "|---|---|---|"]
    for tag, r in P.items():
        b = r["variants"]["baseline"]["summary"].get(key)
        v = r["variants"].get(variant, {}).get("summary", {}).get(key)
        if b and v:
            lines.append(f"| {tag} | {100 * b['fa']:.2f} / {100 * b['miss']:.2f} / {100 * b['conf']:.2f} | "
                         f"{100 * v['fa']:.2f} / {100 * v['miss']:.2f} / {100 * v['conf']:.2f} |")
    return "\n".join(lines)


def table_uem_protocol(P):
    lines = ["| tag | official UEM h | uem_span h | uem_speech h | baseline DER % c=0 | uem_span | uem_speech |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for tag, r in P.items():
        b = r["variants"]["baseline"]["summary"]["primary@0.0"]["der"]
        us = r["variants"].get("uem_span:silero_x2", {}).get("summary", {}).get("primary@0.0")
        up = r["variants"].get("uem_speech:silero_x2", {}).get("summary", {}).get("primary@0.0")
        u = r.get("uem_hours", {})
        lines.append(f"| {tag} | {u.get('official', '-')} | {u.get('uem_span', '-')} | {u.get('uem_speech', '-')} | "
                     f"{100 * b:.2f} | {f(us and us['der'], 2, True)} | {f(up and up['der'], 2, True)} |")
    return "\n".join(lines)


def table_rerun(R):
    lines = ["| tag | sessions | hours | cached DER % c=0 | re-run, same audio | trim (audio kept %) | zero | "
             "cached DER % c=0.25 | re-run | trim | zero |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for tag, r in R.items():
        v = r["variants"]
        g = lambda name, k: v.get(name, {}).get("summary", {}).get(k)  # noqa: E731
        cells = []
        for k in ("primary@0.0", "primary@0.25"):
            b = g("baseline(cached)", k)
            row = [f"{100 * b['der']:.2f}" if b else "-"]
            for name in ("none", "trim", "zero"):
                x = g(name, k)
                txt = f"{100 * x['der']:.2f}" if x else "-"
                if name == "trim" and x and k == "primary@0.0" and r.get("audio_hours", {}).get("trim"):
                    txt += f" ({100 * r['audio_hours']['trim'] / r['hours']:.0f}%)"
                row.append(txt)
            cells += row
        lines.append(f"| {tag} | {len(r['sessions'])} | {r['hours']:.2f} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def table_dataprep(D):
    lines = ["| dataset | hours | Silero speech % | non-speech in stretches > 1 s % | > 5 s % | audio left after trim % | "
             "non-trivial UEMs reproduced within 2 s |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, r in D.items():
        u = r.get("non_trivial_uems")
        lines.append(f"| {name} | {r['hours']} | {r['silero_speech_pct']} | {r['nonspeech_gt1s_pct']} | "
                     f"{r['nonspeech_gt5s_pct']} | {r['trimmed_audio_pct_of_original']} | "
                     + (f"{u['within_2s_both_ends']}/{u['sessions']}" if u else "-") + " |")
    return "\n".join(lines)


def table_calibration(A):
    """VAD accuracy against the tightest references (frame level; collar 0 and 0.25 s around reference boundaries)."""
    tight = [("maptask", "primary", "word-level"), ("libricss", "primary", "exact playback times (synthetic)"),
             ("ami", "primary", "forced-aligned (MFA)"), ("notsofar1", "fastmss_mfa", "forced-aligned (MFA)"),
             ("primock57", "channel_activity", "per-channel energy (diagnostic)")]
    dets = [d for d in DETECTORS if d != "silero"]
    lines = ["| dataset | reference | " + " | ".join(f"{LABEL[d]}" for d in dets) +
             " | Silero x2 onset / offset p50 s |", "|---|---|" + "---|" * len(dets) + "---|"]
    for name, ref, desc in tight:
        r = A.get(name)
        if not r or ref not in r["summary"]:
            continue
        c = r.get("common_subset", {"summary": r["summary"]})["summary"].get(ref, r["summary"][ref])
        cells = [f"{c[d]['fa_pct']:.1f} / {c[d]['miss_pct']:.1f}; {f(c[d].get('fa_c25_pct'))} / {f(c[d].get('miss_c25_pct'))}"
                 if d in c else "-" for d in dets]
        x = c.get("silero_x2", {})
        lines.append(f"| {name} ({r['view']}) | {ref}: {desc} | " + " | ".join(cells) +
                     f" | {f(x.get('onset', {}).get('p50'), 3)} / {f(x.get('offset', {}).get('p50'), 3)} |")
    return "\n".join(lines)


def table_dropouts(Rc):
    lines = ["| tag | hours | clear-speech 10 s windows | stock Silero drop-outs | 30 s reset | Silero x2 (max of both) |",
             "|---|---:|---:|---:|---:|---:|"]
    for tag, x in Rc["per_tag"].items():
        d, p = x["dropout_windows"], x["dropout_pct"]
        lines.append(f"| {tag} | {x['hours']} | {x['clear_windows']} | {d['stock']} ({p['stock']}%) | {d['r30']} ({p['r30']}%) | "
                     f"{d['max']} ({p['max']}%) |")
    t, tp = Rc["total_dropout_windows"], Rc["total_dropout_pct"]
    lines.append(f"| **all** | | **{Rc['total_clear_windows']}** | **{t['stock']} ({tp['stock']}%)** | **{t['r30']} ({tp['r30']}%)** | "
                 f"**{t['max']} ({tp['max']}%)** |")
    return "\n".join(lines)


def main():
    A = audits()
    N = nemotron_results()
    W = whisper_rows()
    P = {p.name[len("posthoc."):-5]: load(p) for p in sorted((V / "pipeline").glob("posthoc.*.json"))}
    R = {p.name[len("rerun."):-5]: load(p) for p in sorted((V / "pipeline").glob("rerun.*.json"))}
    D = load(V / "dataprep.json") or {}
    pm = load(V / "primock57" / "primock57_channels.json")
    corr_rows, corr_stats = correlation(N)
    wt, wtot = table_whisper(W)
    parts = ["# Silero VAD study: results", "",
             "Produced by the code on branch `vad-study`; write-up and verdict: "
             "[docs/silero_vad_study.md](../../docs/silero_vad_study.md). Exact commands:", "", CMDS, "",
             "Conventions: reference speech = union of the RTTM segments inside the UEM; percentages are of reference "
             "speech time. *unannotated* = VAD speech >= 0.5 s long and > 0.25 s away from any reference speech; "
             "*silent-ref* = reference speech >= 0.5 s long and > 0.25 s away from any VAD speech; FA / miss = frame-level "
             "disagreement at collar 0. Boundary offsets: positive = the reference is wider than the VAD (starts "
             "earlier / ends later). Silero = `silero-vad` 6.2.3 defaults (threshold 0.5, min speech 250 ms, min "
             "silence 100 ms, pad 30 ms) applied to the frame-wise maximum of two runs (stock streaming, and state reset every 30 s): *Silero x2*. *stock* = the plain streaming run.", "",
             "## 1. Ground-truth audit (primary reference, Silero x2)", "", table_audit(A), "",
             "### Unannotated speech (% of reference speech) by detector", "", table_detectors(A, "unref_pct"), "",
             "### Silent reference speech (% of reference speech) by detector", "", table_detectors(A, "unvoiced_pct"), "",
             "### Whisper check of the longest flagged regions",
             "",
             "Cells: regions whose Whisper transcript is intelligible speech (>= 3 words, not a hallucination) / regions "
             "with any verbal content (also 1-2 words or fillers such as \"yeah\", \"um\") / regions checked. "
             "Unannotated + speech = the reference is missing speech; silent-ref + speech = the detector missed speech.",
             "",
             wt, "",
             "## 2. Boundary precision per reference variant (vs Silero) and Nemotron error against the same reference", "",
             table_refs(A, N), "",
             "### VAD accuracy against the tightest references",
             "",
             "Cells: FA / miss % at collar 0; FA / miss % outside +/- 0.25 s of reference boundaries (sessions where "
             "every detector is available).", "", table_calibration(A), "",
             "### Does Silero-vs-reference disagreement predict Nemotron's error? (every evaluated tag x reference)", "",
             table_corr_stats(corr_stats), "", table_corr(corr_rows), ""]
    Rc = load(V / "reset_check.json")
    if Rc:
        parts += ["## Silero drop-outs (stock vs state reset vs max of both)", "",
                  "A 10 s window is clear speech when Nemotron covers >= 50% of it and WebRTC (mode 3) fires on >= 50% "
                  "of its frames; Silero drops out when its maximum probability in the window is < 0.2 "
                  "(`scripts/vad_reset_check.py`).", "", table_dropouts(Rc), ""]
    if P:
        parts += ["## 3. VAD-assisted Nemotron (post-hoc on cached outputs): change in DER (points)", "",
                  "Primary reference, collar 0:", "", table_posthoc(P, "primary@0.0"), "",
                  "Primary reference, collar 0.25 s:", "", table_posthoc(P, "primary@0.25"), "",
                  "Error components, gate with Silero (collar 0):", "",
                  table_posthoc_components(P, "primary@0.0", "gate:silero_x2"), "",
                  "Protocol variants (scoring region changed; not comparable to official numbers):", "",
                  table_uem_protocol(P), ""]
    if R:
        parts += ["### Re-inference on VAD-modified audio (sample of sessions per tag)", "", table_rerun(R), ""]
    if pm:
        parts += ["## PriMock57 per channel", "", "```json",
                  json.dumps({k: v for k, v in pm.items() if k in ("per_speaker_role", "overlap_pct_of_speech")}, indent=1),
                  "```", "", "Nemotron 3 Diarization (cached, mix) against each reference:", "",
                  "| reference | DER % c=0 | FA | miss | DER % c=0.25 |", "|---|---:|---:|---:|---:|"]
        nv = pm["nemotron_vs_references"]
        for ref in ("primary", "channel_activity", "silero_channel", "silero_channel_nopad"):
            a, b = nv.get(f"{ref}@0.0"), nv.get(f"{ref}@0.25")
            if a and b:
                parts.append(f"| {ref} | {100 * a['der']:.2f} | {100 * a['fa']:.2f} | {100 * a['miss']:.2f} | {100 * b['der']:.2f} |")
        if "whisper_disagreements" in pm:
            parts += ["", "Energy-vs-Silero disagreements on the isolated channels (30 longest of each kind), Whisper "
                      "transcript classes:", "", "| kind | regions | seconds | speech | short | laughter | none |",
                      "|---|---:|---:|---:|---:|---:|---:|"]
            for k, d in pm["whisper_disagreements"]["summary"].items():
                c = d.get("classes", {})
                parts.append(f"| {k} | {d['regions']} | {d.get('seconds', '-')} | {c.get('speech', '-')} | "
                             f"{c.get('short', '-')} | {c.get('laughter', '-')} | {c.get('none', '-')} |")
        parts.append("")
    if D:
        parts += ["## 4. Data preparation", "",
                  "Silero x2 speech share, non-speech in long stretches, audio left by `trim_plan` (stretches > 1 s "
                  "shortened to 0.5 s), and whether a VAD span (first speech - 1 s .. last speech + 1 s) reproduces "
                  "official UEMs that are not the whole file (`scripts/vad_dataprep.py`).", "", table_dataprep(D), ""]
    U = load(V / "uem_check.json")
    if U:
        parts += ["### Untranscribed speech inside the UEM (before the first / after the last reference segment)", "",
                  "Silero x2 speech more than 1 s outside the transcribed span but inside the UEM "
                  "(`scripts/vad_uem_check.py`); it is scored as false alarm for any diarizer.", "",
                  "| dataset | sessions | speech before first segment s | after last segment s | sessions with >= 10 s | worst |",
                  "|---|---:|---:|---:|---:|---|"]
        for name, x in U.items():
            w = x["flagged"][0] if x["flagged"] else None
            parts.append(f"| {name} | {x['sessions']} | {x['speech_before_first_ref_s']} | {x['speech_after_last_ref_s']} | "
                         f"{x['sessions_flagged']} | " + (f"{w['session_id']} ({w['split']}): {w['silero_speech_before_s']} s "
                                                         f"before {w['first_ref_start']} s, {w['silero_speech_after_s']} s after "
                                                         f"{w['last_ref_end']} s" if w else "-") + " |")
        parts.append("")
    (V / "README.md").write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    summary = {"whisper_totals": wtot, "correlation": corr_stats, "correlation_rows": corr_rows}
    (V / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
    print((V / "README.md").read_text(encoding="utf-8")[:3000])


if __name__ == "__main__":
    main()
