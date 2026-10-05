"""Transcribe specific regions with Whisper to check whether 'false alarm' regions contain real speech.

Usage: python scripts/listen_regions.py <dataset> <session_id> <start-end> [<start-end> ...] [--view V]
Prints, for each region, the reference segments that touch it and Whisper large-v3's transcription.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import soundfile as sf  # noqa: E402

from diards.core import NormalizedDataset  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("session")
    ap.add_argument("regions", nargs="+")
    ap.add_argument("--view")
    a = ap.parse_args()
    import torch
    from transformers import pipeline

    asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", torch_dtype=torch.float16,
                   device="cuda")
    s = next(x for x in NormalizedDataset(a.dataset).sessions(view=a.view) if x.session_id == a.session)
    x, sr = sf.read(str(s.audio_path), dtype="float32")
    for reg in a.regions:
        st, en = (float(v) for v in reg.split("-"))
        near = [g for g in s.segments if g.end > st - 1 and g.start < en + 1]
        text = asr({"raw": x[int(st * sr): int(en * sr)], "sampling_rate": sr},
                   generate_kwargs={"language": "en", "task": "transcribe"})["text"]
        print(f"[{st:.2f}-{en:.2f}] ref nearby: {[(round(g.start, 2), round(g.end, 2), g.speaker) for g in near]}")
        print(f"    whisper: {text.strip()!r}")


if __name__ == "__main__":
    main()
