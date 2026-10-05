"""Fill the auto-generated blocks of every dataset card and write results/SUMMARY.md.

Each ``datasets/<name>/README.md`` is hand-written, except for blocks delimited by
``<!-- auto:<block> -->`` ... ``<!-- /auto:<block> -->`` which this script regenerates from:

* the normalized ``dataset.json`` / manifests (``--root``),
* ``results/stats/stats.<name>.json``,
* ``results/validation/validation.<name>.<view>.json``,
* ``results/nemotron/<name>.<view>*/results.json``.

Blocks: ``meta`` (license/access/version), ``stats`` (verified statistics), ``validation``, ``nemotron``, ``prepare``.

Usage: python scripts/make_cards.py [--root D:/diarization-data/normalized]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from diards.config import normalized_root  # noqa: E402
from diards.datasets import RECIPES, get_recipe  # noqa: E402

# Datasets whose test material overlaps Nemotron 3 Diarization's training data (model card, 2026-09-23).
CONTAMINATION = {
    "icsi": "ICSI (full corpus) is in the model's training data: these scores are NOT held-out.",
    "voxconverse": "VoxConverse v0.3 dev AND test are in the model's training data: these scores are NOT held-out.",
    "ami": "AMI train+dev were used for training; the test split scored here is held out.",
    "notsofar1": "NOTSOFAR-1 train+dev were used for training; the eval set scored here is held out.",
    "dipco": "DiPCo dev was used for training; the eval split scored here is held out.",
    "callhome_eng": ("The model was trained on NIST SRE 2000 CALLHOME part 1, which contains CallHome calls in several "
                     "languages; overlap with these CallHome English calls cannot be ruled out."),
}


def fmt(x, nd=2):
    return "-" if x is None else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def block_meta(name, meta):
    rec = get_recipe(name).META
    lines = [
        f"| | |", "|---|---|",
        f"| License | {rec.license} ([link]({rec.license_url})) |",
        f"| Annotations redistributable here | {'yes' if rec.annotation_redistributable else 'no (scripts only)'} |",
        f"| Access | {rec.access} |",
        f"| Source version used | {rec.source_version} |",
        f"| Domain | {rec.domain} |",
        f"| Views (normalized) | " + "; ".join(f"`{k}`: {v}" for k, v in rec.views.items()) + " |",
        f"| Reference used as primary RTTM | {rec.reference} |",
        f"| Ground-truth rating | **{rec.gt_rating}** - {rec.gt_rating_reason} |",
    ]
    if meta and meta.get("splits"):
        lines.append("| Prepared splits (sessions) | " + ", ".join(f"{k}: {v}" for k, v in meta["splits"].items()) + " |")
    return "\n".join(lines)


def block_stats(name):
    p = REPO / "results" / "stats" / f"stats.{name}.json"
    if not p.exists():
        return "_Statistics not computed yet._"
    st = json.loads(p.read_text(encoding="utf-8"))
    rows = ["| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | "
            "segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |",
            "|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|"]
    order = sorted(k for k in st["summary"] if k != "ALL") + ["ALL"]
    for k in order:
        a = st["summary"].get(k)
        if not a:
            continue
        sd = a["segment_s"]
        rows.append(f"| {k} | {a['sessions']} | {a['hours']} | {a['speech_hours']} | {a['speech_ratio']} | {a['overlap_ratio']} | "
                    f"{a['overlap3plus_ratio']} | {a['speakers_min']}/{a['speakers_median']:g}/{a['speakers_max']} | "
                    f"{sd['p5']}/{sd['p50']}/{sd['p95']} | {a['segments_under_0.2s_frac']} | "
                    f"{a['same_speaker_pause_s']['p50']} | {a['speaker_changes_per_min']} |")
    rows.append("")
    rows.append(f"Computed by `python -m diards stats {name}` from the normalized primary reference inside each UEM "
                "(overlap ratio = time with >= 2 speakers / speech time). Source: "
                f"[`results/stats/stats.{name}.md`](../../results/stats/stats.{name}.md).")
    return "\n".join(rows)


def block_validation(name):
    files = sorted((REPO / "results" / "validation").glob(f"validation.{name}.*.json"))
    if not files:
        return "_Validation not run yet._"
    out = []
    for f in files:
        rep = json.loads(f.read_text(encoding="utf-8"))
        s = rep["summary"]
        out.append(f"View `{s['view']}`: {s['sessions']} sessions, **{s['errors']} errors**, {s['warnings']} warnings "
                   f"(normalized files); {s['sessions_with_raw_label_issues']} sessions had problems in the ORIGINAL labels "
                   f"that normalization fixed.")
        if s.get("raw_label_issue_totals"):
            out.append("- original-label issues: " + ", ".join(f"{k} = {fmt(v)}" for k, v in s["raw_label_issue_totals"].items()))
        if s.get("issue_counts"):
            out.append("- checks that fired (sessions): " + ", ".join(f"`{k}` {v}" for k, v in s["issue_counts"].items()))
        if s.get("vad"):
            v = s["vad"]
            out.append(f"- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = "
                       f"{fmt(100 * v['vad_not_in_ref_frac'], 1)}% of reference speech; reference speech without energy = "
                       f"{fmt(100 * v['ref_not_in_vad_frac'], 1)}%. Most-flagged sessions: "
                       + ", ".join(f"`{a}` ({b:.2f})" for a, b in v["worst_sessions"][:5]))
        out.append(f"- full report: [`results/validation/{f.stem}.md`](../../results/validation/{f.stem}.md)")
    return "\n".join(out)


def block_nemotron(name):
    dirs = sorted(p for p in (REPO / "results" / "nemotron").glob(f"{name}.*") if (p / "results.json").exists())
    if not dirs:
        return "_Not evaluated yet._"
    out = ["| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |",
           "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|"]
    for d in dirs:
        r = json.loads((d / "results.json").read_text(encoding="utf-8"))
        tag = d.name[len(name) + 1:]
        splits = sorted({x["split"] for x in r["per_session"]})
        for key, v in r["summary"].items():
            ref, c = key.split("@")
            if c != "0.0":
                continue
            v25 = r["summary"].get(f"{ref}@0.25", {})
            out.append(f"| {tag} ({', '.join(splits)}) | {r['sessions']} | {r['hours']} | {ref} | **{100 * v['der']:.2f}** | "
                       f"{100 * v['fa']:.2f} | {100 * v['miss']:.2f} | {100 * v['conf']:.2f} | {100 * v['jer']:.2f} | "
                       f"{100 * v25.get('der', float('nan')):.2f} | {100 * r['speaker_count_accuracy']:.0f}% |")
    out.append("")
    out.append("Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no "
               "post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. "
               "Per-session tables: `results/nemotron/" + name + ".*/results.md`.")
    if name in CONTAMINATION:
        out.append("")
        out.append(f"> **Training-data overlap:** {CONTAMINATION[name]}")
    return "\n".join(out)


def block_prepare(name):
    rec = get_recipe(name).META
    views = list(rec.views)
    return "\n".join([
        "```bash",
        f"python -m diards prepare {name}            # download (resumable) + normalize (idempotent)",
        f"python -m diards validate {name} --vad     # ground-truth checks",
        f"python -m diards stats {name}",
        f"python -m diards export {name} --format nemo      # or pyannote / lhotse",
        f"python -m diards evaluate {name} --view {views[0]}  # Nemotron 3 Diarization + DER/JER",
        "```",
        "",
        "```python",
        "from diards import load_dataset",
        f"for s in load_dataset(\"{name}\", view=\"{views[0]}\"):",
        "    s.audio_path, s.segments, s.uem, s.words",
        "```",
    ])


BLOCKS = {"meta": block_meta, "stats": block_stats, "validation": block_validation, "nemotron": block_nemotron,
          "prepare": block_prepare}


def fill(text: str, name: str, meta) -> str:
    for b, fn in BLOCKS.items():
        pat = re.compile(rf"(<!-- auto:{b} -->)(.*?)(<!-- /auto:{b} -->)", re.S)
        content = fn(name, meta) if b == "meta" else fn(name)
        text = pat.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    args = ap.parse_args()
    root = normalized_root(args.root)
    for name in sorted(RECIPES):
        card = REPO / "datasets" / name / "README.md"
        if not card.exists():
            print(f"[cards] no card for {name}")
            continue
        mp = root / name / "dataset.json"
        meta = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else None
        card.write_text(fill(card.read_text(encoding="utf-8"), name, meta), encoding="utf-8", newline="\n")
        print(f"[cards] {name} updated")


if __name__ == "__main__":
    main()
