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
DETECTORS = ("silero_r30", "silero", "webrtc", "energy", "pyannote", "nemotron")
LABEL = {"silero_r30": "Silero (30 s reset)", "silero": "Silero (stock)", "webrtc": "WebRTC (mode 2)",
         "energy": "energy", "pyannote": "pyannote seg-3.0", "nemotron": "Nemotron (union)"}
CMDS = """```bash
# env: D:\\diarization-data\\envs\\diar (+ silero-vad 6.2.3 installed with --no-deps); pyannote in envs\\vad
WORKERS=8 bash scripts/vad_compute_all.sh                       # Silero / WebRTC / energy VAD cache (CPU)
<envs/vad python> scripts/vad_pyannote.py                       # pyannote segmentation-3.0 baseline (GPU, ~6 min)
for d in <every dataset>; do python -m diards.vad_audit $d; done   # coverage, boundaries, lag, evidence
for d in <every dataset>; do python scripts/vad_whisper_check.py $d; done   # Whisper check of flagged regions
JOBS=6 bash scripts/vad_pipeline_all.sh                         # post-hoc VAD-assisted Nemotron variants (CPU)
for t in <tags>; do python -m diards.vad_assist rerun $t --max-hours 1.0; done   # trim / zero re-inference (GPU)
python scripts/vad_primock57_channels.py --whisper              # PriMock57 per-channel analysis
python scripts/vad_dataprep.py                                  # trimming potential, VAD-derived UEMs
python scripts/vad_report.py                                    # this README + summary.json
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
        x = r["summary"]["primary"].get("silero_r30")
        if not x:
            continue
        lines.append(f"| {name} | {r['view']} | {grade(name)} | {x['sessions']} | {x['ref_h']:.2f} | {x['vad_h']:.2f} | "
                     f"{x['fa_pct']:.1f} | {x['miss_pct']:.1f} | {x['unref_pct']:.2f} | {x['unvoiced_pct']:.2f} | "
                     f"{f(x['onset'].get('p50'), 3)} | {f(x['offset'].get('p50'), 3)} | {x['sessions_time_shifted']} |")
    return "\n".join(lines)


def table_detectors(A, key):
    dets = [d for d in DETECTORS]
    lines = ["| dataset | " + " | ".join(LABEL[d] for d in dets) + " |", "|---|" + "---:|" * len(dets)]
    for name, r in A.items():
        s = r["summary"]["primary"]
        lines.append(f"| {name} | " + " | ".join(f(s[d][key], 2) if d in s else "-" for d in dets) + " |")
    return "\n".join(lines)


def whisper_rows():
    out = {}
    for p in sorted((V / "whisper").glob("whisper.*.json")):
        r = load(p)
        out[r["dataset"]] = r
    return out


def table_whisper(W):
    kinds = [("unref", "silero_r30"), ("unref", "energy"), ("unref", "webrtc"),
             ("unvoiced", "silero_r30"), ("unvoiced", "energy"), ("unvoiced", "webrtc"), ("control", None)]
    head = ["unannotated: Silero", "unannotated: energy", "unannotated: WebRTC",
            "silent-ref: Silero", "silent-ref: energy", "silent-ref: WebRTC", "control (both silent)"]
    lines = ["| dataset | " + " | ".join(head) + " |", "|---|" + "---:|" * len(head)]
    tot = {k: [0, 0] for k in kinds}
    for name, r in W.items():
        cells = []
        for kind, vad in kinds:
            key = f"{kind}:{vad}" if vad else "control"
            d = r["summary"].get(key)
            if d:
                cells.append(f"{d['with_speech']}/{d['regions']}")
                tot[(kind, vad)][0] += d["with_speech"]
                tot[(kind, vad)][1] += d["regions"]
            else:
                cells.append("-")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    lines.append("| **all** | " + " | ".join(
        f"**{a}/{b} ({100 * a / b:.0f}%)**" if b else "-" for a, b in tot.values()) + " |")
    return "\n".join(lines), {f"{k}:{v}": t for (k, v), t in tot.items()}


def table_refs(A, N):
    """Boundary offsets per reference variant vs Silero, next to Nemotron's error against the same reference."""
    lines = ["| dataset | reference | ref speech h | onset p25 / p50 / p75 s | offset p25 / p50 / p75 s | "
             "ref speech Silero calls silence % | Nemotron miss % | Nemotron FA % | Nemotron DER % (c=0) |",
             "|---|---|---:|---|---|---:|---:|---:|---:|"]
    pairs = []
    for name, r in A.items():
        tags = [t for t in N if t.split(".")[0] == name and t.split(".")[1] == r["view"]]
        for ref_name, by in r["summary"].items():
            x = by.get("silero_r30")
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


def correlation(N, root=None):
    """Across every (evaluated tag, reference) pair: does Silero-vs-reference disagreement, computed on exactly the
    sessions and audio Nemotron was scored on, predict Nemotron's miss / FA against that reference?"""
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
        refs = ["primary"] + sorted({k for s in sessions for k in s.alt_rttm})
        for ref_name in refs:
            nem = res["summary"].get(f"{ref_name}@0.0")
            if not nem:
                continue
            ref_s = miss_s = fa_s = 0.0
            for s in sessions:
                if ref_name != "primary" and ref_name not in s.alt_rttm:
                    continue
                segs = s.segments if ref_name == "primary" else s.alt_segments(ref_name)
                uem = merge_intervals(s.uem)
                ref = intersect(merge_intervals((g.start, g.end) for g in segs), uem)
                vad = intersect(merge_intervals(caches[s.session_id].silero(reset=True)), uem)
                ref_s += total_duration(ref)
                miss_s += total_duration(subtract(ref, vad))
                fa_s += total_duration(subtract(vad, ref))
            if ref_s:
                rows.append({"tag": tag, "reference": ref_name, "silero_miss_pct": round(100 * miss_s / ref_s, 2),
                             "silero_fa_pct": round(100 * fa_s / ref_s, 2), "nemotron_miss_pct": round(100 * nem["miss"], 2),
                             "nemotron_fa_pct": round(100 * nem["fa"], 2), "nemotron_der_pct": round(100 * nem["der"], 2)})
    stats = {}
    if len(rows) >= 3:
        from scipy.stats import pearsonr, spearmanr

        for a, b in (("silero_miss_pct", "nemotron_miss_pct"), ("silero_fa_pct", "nemotron_fa_pct"),
                     ("silero_miss_pct", "nemotron_der_pct")):
            x = np.array([r[a] for r in rows])
            y = np.array([r[b] for r in rows])
            stats[f"{a}~{b}"] = {"n": len(rows), "pearson": round(float(pearsonr(x, y)[0]), 3),
                                 "spearman": round(float(spearmanr(x, y)[0]), 3)}
    return rows, stats


def table_corr(rows):
    lines = ["| tag | reference | Silero miss % | Nemotron miss % | Silero FA % | Nemotron FA % | Nemotron DER % |",
             "|---|---|---:|---:|---:|---:|---:|"]
    for r in sorted(rows, key=lambda r: -r["silero_miss_pct"]):
        lines.append(f"| {r['tag']} | {r['reference']} | {r['silero_miss_pct']:.1f} | {r['nemotron_miss_pct']:.1f} | "
                     f"{r['silero_fa_pct']:.1f} | {r['nemotron_fa_pct']:.1f} | {r['nemotron_der_pct']:.1f} |")
    return "\n".join(lines)


POSTHOC = ["gate:silero_r30", "gate+0.25:silero_r30", "gate:silero", "gate:webrtc", "gate:energy", "gate:pyannote",
           "gate+0.25:pyannote", "fill:silero_r30", "vad_decides:silero_r30"]


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
        us = r["variants"].get("uem_span:silero_r30", {}).get("summary", {}).get("primary@0.0")
        up = r["variants"].get("uem_speech:silero_r30", {}).get("summary", {}).get("primary@0.0")
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
    """VAD accuracy against the tightest references (frame level, collar 0)."""
    tight = [("maptask", "primary", "word-level"), ("libricss", "primary", "exact (synthetic)"),
             ("ami", "primary", "forced-aligned (MFA)"), ("notsofar1", "fastmss_mfa", "forced-aligned (MFA)"),
             ("primock57", "channel_activity", "per-channel energy (diagnostic)")]
    dets = [d for d in DETECTORS if d != "silero"]
    lines = ["| dataset | reference | " + " | ".join(f"{LABEL[d]} FA / miss %" for d in dets) +
             " | Silero onset / offset p50 s |", "|---|---|" + "---|" * len(dets) + "---|"]
    for name, ref, desc in tight:
        r = A.get(name)
        if not r or ref not in r["summary"]:
            continue
        s = r["summary"][ref]
        cells = [f"{s[d]['fa_pct']:.1f} / {s[d]['miss_pct']:.1f}" if d in s else "-" for d in dets]
        x = s.get("silero_r30", {})
        lines.append(f"| {name} ({r['view']}) | {ref}: {desc} | " + " | ".join(cells) +
                     f" | {f(x.get('onset', {}).get('p50'), 3)} / {f(x.get('offset', {}).get('p50'), 3)} |")
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
             "silence 100 ms, pad 30 ms) with its state reset every 30 s unless marked *stock*.", "",
             "## 1. Ground-truth audit (primary reference, Silero with 30 s reset)", "", table_audit(A), "",
             "### Unannotated speech (% of reference speech) by detector", "", table_detectors(A, "unref_pct"), "",
             "### Silent reference speech (% of reference speech) by detector", "", table_detectors(A, "unvoiced_pct"), "",
             "### Whisper check of the longest flagged regions (regions with intelligible speech / regions checked)", "",
             wt, "",
             "## 2. Boundary precision per reference variant (vs Silero) and Nemotron error against the same reference", "",
             table_refs(A, N), "",
             "### VAD accuracy against the tightest references (frame level, collar 0)", "", table_calibration(A), "",
             "### Does Silero-vs-reference disagreement predict Nemotron's error? (every evaluated tag x reference)", "",
             "```json", json.dumps(corr_stats, indent=1), "```", "", table_corr(corr_rows), ""]
    if P:
        parts += ["## 3. VAD-assisted Nemotron (post-hoc on cached outputs): change in DER (points)", "",
                  "Primary reference, collar 0:", "", table_posthoc(P, "primary@0.0"), "",
                  "Primary reference, collar 0.25 s:", "", table_posthoc(P, "primary@0.25"), "",
                  "Error components, gate with Silero (collar 0):", "",
                  table_posthoc_components(P, "primary@0.0", "gate:silero_r30"), "",
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
            parts += ["", "Energy-vs-Silero disagreements on the isolated channels, checked with Whisper:", "", "```json",
                      json.dumps(pm["whisper_disagreements"]["summary"], indent=1), "```"]
        parts.append("")
    if D:
        parts += ["## 4. Data preparation", "", table_dataprep(D), ""]
    (V / "README.md").write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    summary = {"whisper_totals": wtot, "correlation": corr_stats, "correlation_rows": corr_rows}
    (V / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
    print((V / "README.md").read_text(encoding="utf-8")[:3000])


if __name__ == "__main__":
    main()
