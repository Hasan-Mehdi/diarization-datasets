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
            rows_ref = [x for x in r["per_session"] if f"{ref}@0.0" in x]
            n_ref, h_ref = len(rows_ref), round(sum(x["duration"] for x in rows_ref) / 3600, 2)
            out.append(f"| {tag} ({', '.join(splits)}) | {n_ref} | {h_ref} | {ref} | **{100 * v['der']:.2f}** | "
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


def block_diagnosis(name):
    files = sorted((REPO / "results" / "diagnosis").glob(f"diagnosis.{name}.*.json"))
    if not files:
        return "_Not run yet._"
    audits = []
    out = ["| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for f in files:
        s = json.loads(f.read_text(encoding="utf-8"))["summary"]
        out.append(f"| {s['hyp_view']} | {s['vad_view']} | {s['sessions']} | {s['miss_pct']} | {s['miss_in_silence_pct']} | "
                   f"{s['miss_with_energy_pct']} | {s['fa_pct']} | {s['fa_with_energy_pct']} | {s['fa_in_silence_pct']} |")
        audits.append((s["hyp_view"], REPO / "results" / "diagnosis" / f"fa_audit.{name}.{s['hyp_view']}.json"))
    out.append("")
    out.append("Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, "
               "split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per "
               "session). \"Miss in silence\" is a lower bound on reference padding; \"FA with energy\" mixes unlabelled "
               "speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).")
    for view, ap in audits:
        if ap.exists():
            a = json.loads(ap.read_text(encoding="utf-8"))
            ex = [r for r in a["regions"] if r["speech"]][:3]
            out.append("")
            out.append(f"**Whisper audit of the longest audible false alarms ({view}):** {a['regions_with_speech']} of "
                       f"{a['regions_checked']} regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; "
                       f"Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label "
                       f"({a['seconds_with_speech']} of {a['seconds_checked']} s)."
                       + (" Examples: " + "; ".join(f"`{r['session_id']}` {r['start']:.1f}-{r['end']:.1f} s: " + chr(34) + r['whisper'][:80] + chr(34) for r in ex) if ex else ""))
        op = REPO / "results" / "diagnosis" / f"offsets.{name}.{view}.json"
        if op.exists():
            o = json.loads(op.read_text(encoding="utf-8"))
            worst = ", ".join(f"`{r['session_id']}` ({r['best_lag_s']:+.2f} s)" for r in o["shifted"][:3])
            out.append("")
            out.append(f"**Time-offset check ({view}):** {o['sessions_shifted']} of {o['sessions']} sessions look shifted "
                       f"against the audio ({o['criterion']}); median best lag {o['median_abs_best_lag_s']} s"
                       + (f"; shifted: {worst}" if worst else "") + ".")
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


# Catalog order (ranked) and static facts that are not in the recipe metadata.
CATALOG = [
    # name, size of what you download, granularity of the reference, main known issue (ranked by GT rating)
    ("maptask", "~2 GB", "word-level timed units, per close-talk channel", "task dialogue, studio audio; licence ambiguity (use NC)"),
    ("notsofar1", "~10 GB (eval+dev: close-talk + 1 far-field device)", "utterances + word times (human, close-talk)", "utterances keep short pauses; device differs per room"),
    ("ami", "~30 GB (all meetings, 2 views)", "forced-aligned words (MFA) from manual transcripts", "4 meetings with known timing failures (2 in test)"),
    ("chime6", "23 GB tarballs (dev+eval; only needed channels kept)", "forced-aligned utterances (official Track 2)", "enrolment minute unannotated (UEM fixes); very hard audio"),
    ("voxconverse", "7.3 GB (HF mirror)", "human-verified diarization turns", "in many models' training data; 37 single-speaker files"),
    ("icsi", "~15 GB (2 views)", "manual transcriber segments (+ word times)", "padded segments; 9-13% of words untimed; in Nemotron training data"),
    ("dipco", "13.4 GB tarball", "manual utterances up to 10-15 s", "pauses inside segments; only 10 sessions"),
    ("easycom", "~22 GB (glasses audio + labels, per-file LFS)", "human VAD per utterance (50 ms frames)", "loudspeaker noise; missing (redacted) minutes"),
    ("msdwild_en", "8.1 GB (all clips)", "human diarization turns", "research-only licence; English by LID; short clips"),
    ("ava_avd_en", "~5 GB (minutes 15-30 of 117 movies via HTTP range)", "human identity turns", "music/effects-heavy audio, many speakers; English by LID"),
    ("earnings21", "~1.5 GB", "RTTM from human transcripts (timing method undocumented)", "almost no overlap/backchannels"),
    ("sbcsae", "6.2 GB", "intonation units (ms bullets), tiled", "pauses inside units; CC BY-ND (no derived RTTMs shared)"),
    ("callhome_eng", "2.3 GB (HF parquet)", "turn bullets (LDC transcripts via TalkBank)", "loose turns, backchannels incomplete"),
    ("scotus", "~0.7 GB (12-case sample)", "Oyez turn sync, tiled, no overlap", "interruptions never marked as overlap"),
    ("callfriend_eng", "1.2 GB (HF parquet)", "turn bullets (TalkBank)", "tiled bullets, 3,074 same-speaker overlaps"),
    ("afrispeech_dialog", "~0.8 GB", "hand-typed turn times (~1 s precision)", "coarse times, no overlap, 3/49 untimed"),
    ("primock57", "~1 GB", "padded utterances per channel (+ our channel-activity RTTM)", "10-14% of labelled time is silence"),
    ("libricss", "6.4 GB", "exact playback times (synthetic)", "read speech replayed; not real conversation"),
]


MIRRORS = {'notsofar1': 'HF microsoft/NOTSOFAR; Azure blob', 'ami': 'Edinburgh mirror; HF diarizers-community/ami, edinburghcstr/ami', 'chime6': 'OpenSLR SLR150 (+ELDA, CN mirrors); HF argmaxinc/chime-6', 'maptask': 'Edinburgh; LDC93S12 (paid)', 'voxconverse': 'Oxford VGG; HF diarizers-community/voxconverse', 'icsi': 'Edinburgh; HF argmaxinc/icsi-meetings', 'dipco': 'Zenodo 8122551; HF huckiyang/DiPCo', 'easycom': 'GitHub LFS + release archive', 'msdwild_en': 'Google Drive (+Baidu/Quark)', 'earnings21': 'GitHub revdotcom/speech-datasets; HF argmaxinc/earnings21', 'ava_avd_en': 'GitHub + Google Drive + CVDF S3; HF argmaxinc/ava-avd', 'sbcsae': 'OpenSLR SLR155 (+ELDA); UCSB; TalkBank; LDC (paid)', 'callhome_eng': 'HF talkbank/callhome (gated); TalkBank (login)', 'callfriend_eng': 'HF talkbank/callfriend; TalkBank', 'scotus': 'Oyez API; vcon-dev pack', 'afrispeech_dialog': 'HF intronhealth/afrispeech-dialog', 'primock57': 'GitHub (LFS)', 'libricss': 'Google Drive'}


def _stats(name):
    p = REPO / "results" / "stats" / f"stats.{name}.json"
    return json.loads(p.read_text(encoding="utf-8"))["summary"]["ALL"] if p.exists() else None


def _best_nemotron(name):
    """(label, DER@0, DER@0.25, hours, sessions) for the primary reference of each evaluated view."""
    rows = []
    for d in sorted((REPO / "results" / "nemotron").glob(f"{name}.*")):
        f = d / "results.json"
        if not f.exists():
            continue
        r = json.loads(f.read_text(encoding="utf-8"))
        p0 = r["summary"].get("primary@0.0")
        p25 = r["summary"].get("primary@0.25")
        alts = {k.split("@")[0]: v for k, v in r["summary"].items() if k.endswith("@0.0") and not k.startswith("primary")}
        rows.append((d.name[len(name) + 1:], r, p0, p25, alts))
    return rows


def block_catalog():
    lines = ["| # | dataset | domain | hours | recs | spk min/med/max | overlap | reference | GT | licence | access | size | mirrors | known issue |",
             "|---:|---|---|---:|---:|---|---:|---|---|---|---|---|---|---|"]
    for i, (name, size, gran, issue) in enumerate(CATALOG, 1):
        m = get_recipe(name).META
        st = _stats(name)
        hours = st["hours"] if st else "-"
        recs = st["sessions"] if st else "-"
        spk = f"{st['speakers_min']}/{st['speakers_median']:g}/{st['speakers_max']}" if st else "-"
        ovl = f"{100 * st['overlap_ratio']:.1f}%" if st and st["overlap_ratio"] is not None else "-"
        lines.append(f"| {i} | [{name}](datasets/{name}/README.md) | {m.domain} | {hours} | {recs} | {spk} | {ovl} | {gran} | "
                     f"**{m.gt_rating}** | {m.license} | {m.access} | {size} | {MIRRORS.get(name, '')} | {issue} |")
    return "\n".join(lines)


def block_nemotron_summary():
    lines = ["| dataset | view (subset) | sessions | hours | DER % c=0 (primary ref) | DER % c=0.25 | other references (DER % c=0) | spk-count acc | held-out? |",
             "|---|---|---:|---:|---:|---:|---|---:|---|"]
    for name, *_ in CATALOG:
        for tag, r, p0, p25, alts in _best_nemotron(name):
            if not p0:
                continue
            alt = "; ".join(f"{k} {100 * v['der']:.1f}" for k, v in sorted(alts.items(), key=lambda kv: kv[1]["der"]))
            held = "NO (in training data)" if name in ("icsi", "voxconverse") else ("unclear" if name == "callhome_eng" else "yes")
            splits = ",".join(sorted({x["split"] for x in r["per_session"]}))
            lines.append(f"| [{name}](datasets/{name}/README.md) | {tag} ({splits}) | {r['sessions']} | {r['hours']} | "
                         f"{100 * p0['der']:.2f} | {100 * p25['der']:.2f} | {alt} | {100 * r['speaker_count_accuracy']:.0f}% | {held} |")
    return "\n".join(lines)


README_BLOCKS = {"catalog": block_catalog, "nemotron_summary": block_nemotron_summary}


BLOCKS = {"meta": block_meta, "stats": block_stats, "validation": block_validation, "nemotron": block_nemotron,
          "diagnosis": block_diagnosis, "prepare": block_prepare}


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
    for target in (REPO / "README.md", REPO / "results" / "SUMMARY.md"):
        if target.exists():
            text = target.read_text(encoding="utf-8")
            for b, fn in README_BLOCKS.items():
                pat = re.compile(rf"(<!-- auto:{b} -->)(.*?)(<!-- /auto:{b} -->)", re.S)
                content = fn()
                text = pat.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)
            target.write_text(text, encoding="utf-8", newline="\n")
            print(f"[cards] {target.name} updated")
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
