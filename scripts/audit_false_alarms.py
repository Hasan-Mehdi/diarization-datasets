"""Do the model's "false alarms" contain real, unlabelled speech? Ask Whisper.

Takes the longest audible false-alarm regions (model says speech, reference says nobody, audio has energy) listed
by `python -m diards.diagnose`, transcribes each with Whisper large-v3 (English), and counts regions that yield at
least 3 words not in a list of common Whisper hallucinations. Such regions are strong evidence of speech missing
from the reference (an annotation error), since the reference claims nobody is talking there.

Usage: python scripts/audit_false_alarms.py <dataset> [--view V] [--max-regions 40] [--min-dur 1.0]
Output: results/diagnosis/fa_audit.<dataset>.<view>.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import soundfile as sf  # noqa: E402

from diards.core import NormalizedDataset  # noqa: E402

HALLUCINATIONS = {"thank you", "thanks for watching", "you", "bye", "thank you very much", "subtitles by",
                  "please subscribe", "music", "applause", "laughter", "on and on and on", "see you next week"}


def is_speech(text: str) -> bool:
    """>= 3 words, not a known hallucination, and not repetitive (Whisper loops on music/laughter/noise)."""
    w = words(text)
    if len(w) < 3:
        return False
    joined = " ".join(w)
    if any(h in joined for h in HALLUCINATIONS if len(h.split()) >= 3) or joined in HALLUCINATIONS:
        return False
    if len(set(w)) / len(w) < 0.6:
        return False
    return True


def words(text: str) -> list[str]:
    t = re.sub(r"[^a-z' ]", " ", text.lower())
    return [w for w in t.split() if w]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--view")
    ap.add_argument("--max-regions", type=int, default=40)
    ap.add_argument("--min-dur", type=float, default=1.0)
    ap.add_argument("--rescore", action="store_true", help="recompute the speech flags of an existing audit JSON")
    a = ap.parse_args()
    if a.rescore:
        view = a.view or NormalizedDataset(a.dataset).default_view
        p = Path("results/diagnosis") / f"fa_audit.{a.dataset}.{view}.json"
        out = json.loads(p.read_text(encoding="utf-8"))
        for r in out["regions"]:
            r["speech"] = is_speech(r["whisper"])
        _finish(out, p)
        return
    ds = NormalizedDataset(a.dataset)
    view = a.view or ds.default_view
    diag = json.loads((Path("results/diagnosis") / f"diagnosis.{a.dataset}.{view}.json").read_text(encoding="utf-8"))
    regions = [(e[1] - e[0], r["session_id"], e[0], e[1]) for r in diag["sessions"] for e in r["examples_fa_energy"]
               if e[1] - e[0] >= a.min_dur]
    regions.sort(reverse=True)
    regions = regions[: a.max_regions]
    sessions = {s.session_id: s for s in ds.sessions(view=view)}
    out = {"dataset": a.dataset, "view": view, "regions_checked": len(regions), "regions": []}
    if regions:
        import torch
        from transformers import pipeline

        asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", torch_dtype=torch.float16,
                       device="cuda" if torch.cuda.is_available() else "cpu")
        cache = {}
        for dur, sid, st, en in regions:
            if sid not in cache:
                cache.clear()
                cache[sid] = sf.read(str(sessions[sid].audio_path), dtype="float32")
            x, sr = cache[sid]
            text = asr({"raw": x[int(st * sr): int(en * sr)], "sampling_rate": sr},
                       generate_kwargs={"language": "en", "task": "transcribe"})["text"].strip()
            w = words(text)
            speech = is_speech(text)
            out["regions"].append({"session_id": sid, "start": st, "end": en, "dur": round(dur, 2),
                                   "whisper": text, "words": len(w), "speech": speech})
    _finish(out, Path("results/diagnosis") / f"fa_audit.{a.dataset}.{view}.json")


def _finish(out: dict, p: Path) -> None:
    n_speech = sum(r["speech"] for r in out["regions"])
    out["regions_with_speech"] = n_speech
    out["regions_checked"] = len(out["regions"])
    out["seconds_checked"] = round(sum(r["dur"] for r in out["regions"]), 1)
    out["seconds_with_speech"] = round(sum(r["dur"] for r in out["regions"] if r["speech"]), 1)
    p.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(f"{out['dataset']}/{out['view']}: {n_speech}/{len(out['regions'])} long audible false-alarm regions contain "
          f"intelligible speech ({out['seconds_with_speech']} of {out['seconds_checked']} s)")


if __name__ == "__main__":
    main()
