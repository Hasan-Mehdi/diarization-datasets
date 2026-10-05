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
                  "please subscribe", "music", "applause", "laughter"}


def words(text: str) -> list[str]:
    t = re.sub(r"[^a-z' ]", " ", text.lower())
    return [w for w in t.split() if w]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--view")
    ap.add_argument("--max-regions", type=int, default=40)
    ap.add_argument("--min-dur", type=float, default=1.0)
    a = ap.parse_args()
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
            speech = len(w) >= 3 and " ".join(w) not in HALLUCINATIONS
            out["regions"].append({"session_id": sid, "start": st, "end": en, "dur": round(dur, 2),
                                   "whisper": text, "words": len(w), "speech": speech})
    n_speech = sum(r["speech"] for r in out["regions"])
    out["regions_with_speech"] = n_speech
    out["seconds_checked"] = round(sum(r["dur"] for r in out["regions"]), 1)
    out["seconds_with_speech"] = round(sum(r["dur"] for r in out["regions"] if r["speech"]), 1)
    p = Path("results/diagnosis") / f"fa_audit.{a.dataset}.{view}.json"
    p.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(f"{a.dataset}/{view}: {n_speech}/{len(regions)} long audible false-alarm regions contain >= 3 words "
          f"({out['seconds_with_speech']} of {out['seconds_checked']} s)")


if __name__ == "__main__":
    main()
