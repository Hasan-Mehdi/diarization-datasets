"""pyannote segmentation-3.0 as a VAD baseline for the Silero study (cached next to the other detectors).

Runs ``pyannote.audio.pipelines.VoiceActivityDetection`` with ``pyannote/segmentation-3.0`` and the model card's
VAD hyper-parameters (min_duration_on = min_duration_off = 0) on the normalized audio of the sessions Nemotron was
evaluated on (``results/nemotron/<tag>``). Output: ``<study>/vad/<dataset>.<view>/<session_id>.pyannote.npz``
(``ivs``: float32 [n, 2] speech intervals), read by ``diards.vads.VadCache`` as detector ``pyannote``.

pyannote.audio 4 is not installed in the shared env; this runs in a separate venv that reuses its torch:
  python -m venv --system-site-packages D:\\diarization-data\\envs\\vad
  D:\\diarization-data\\envs\\vad\\Scripts\\python -m pip install pyannote.audio==4.0.7
Usage: <vad venv python> scripts/vad_pyannote.py [tag ...] [--device cuda] [--batch 32]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import soundfile as sf  # noqa: E402

from diards.core import NormalizedDataset  # noqa: E402
from diards.vads import cache_path  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="*")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--batch", type=int, default=32)
    a = ap.parse_args()
    import torch
    from pyannote.audio import Model
    from pyannote.audio.pipelines import VoiceActivityDetection

    model = Model.from_pretrained("pyannote/segmentation-3.0")
    pipe = VoiceActivityDetection(segmentation=model, batch_size=a.batch)
    pipe.instantiate({"min_duration_on": 0.0, "min_duration_off": 0.0})
    pipe.to(torch.device(a.device if torch.cuda.is_available() else "cpu"))
    res_dir = ROOT / "results" / "nemotron"
    tags = a.tags or sorted(p.name for p in res_dir.iterdir() if (p / "results.json").exists())
    for tag in tags:
        name, view = tag.split(".")[:2]
        ids = {r["session_id"] for r in json.loads((res_dir / tag / "results.json").read_text(encoding="utf-8"))["per_session"]}
        sessions = [s for s in NormalizedDataset(name).sessions(view=view) if s.session_id in ids]
        t0, audio_s = time.time(), 0.0
        for s in sessions:
            out = cache_path(name, view, s.session_id).with_suffix(".pyannote.npz")
            if out.exists():
                continue
            x, sr = sf.read(str(s.audio_path), dtype="float32")
            audio_s += len(x) / sr
            ann = pipe({"waveform": torch.from_numpy(x)[None], "sample_rate": sr})
            ivs = np.array([(seg.start, seg.end) for seg in ann.get_timeline().support()], np.float32).reshape(-1, 2)
            out.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(out, ivs=ivs)
        el = time.time() - t0
        print(f"[pyannote] {tag}: {len(sessions)} sessions, {audio_s / 3600:.2f} h computed in {el:.0f} s", flush=True)


if __name__ == "__main__":
    main()
