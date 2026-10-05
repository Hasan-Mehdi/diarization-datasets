"""Spoken-language identification used to carve English subsets out of multilingual corpora (MSDWild, AVA-AVD).

Whisper large-v3 language detection (the same approach SDBench used) on up to three 30-second windows placed on
the reference speech of each recording; window probabilities are averaged. A recording is kept as English when
P(en) >= 0.7. The per-recording probabilities are saved so the subset is reproducible without re-running LID.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .annotation import Segment, speech_regions

MODEL = "openai/whisper-large-v3"
THRESHOLD = 0.7


class WhisperLID:
    def __init__(self, model_id: str = MODEL, device: str = "cuda"):
        import torch
        from transformers import WhisperForConditionalGeneration, WhisperProcessor

        self.torch = torch
        self.processor = WhisperProcessor.from_pretrained(model_id)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_id, dtype=torch.float16).to(device).eval()
        self.device = device
        tok = self.processor.tokenizer
        self.lang_ids = {}
        for t, i in tok.get_vocab().items():
            if t.startswith("<|") and t.endswith("|>") and 2 <= len(t) - 4 <= 3 and t[2:-2].isalpha() and t[2:-2].islower():
                self.lang_ids[t[2:-2]] = i

    def lang_probs(self, x: np.ndarray, sr: int = 16000) -> dict[str, float]:
        torch = self.torch
        feats = self.processor(x, sampling_rate=sr, return_tensors="pt").input_features.to(self.device, torch.float16)
        dec = torch.tensor([[self.model.config.decoder_start_token_id]], device=self.device)
        with torch.inference_mode():
            logits = self.model(input_features=feats, decoder_input_ids=dec).logits[0, -1]
        ids = list(self.lang_ids.values())
        p = torch.softmax(logits[ids].float(), dim=-1).cpu().numpy()
        return dict(zip(self.lang_ids.keys(), p.tolist()))


def windows_on_speech(segs: list[Segment], duration: float, n: int = 3, width: float = 30.0) -> list[tuple[float, float]]:
    """Pick up to ``n`` 30-s windows covering the most reference speech (non-overlapping)."""
    sp = speech_regions(segs)
    if not sp:
        return [(0.0, min(duration, width))]
    starts = np.arange(0.0, max(duration - width, 0.0) + 1e-6, 5.0)
    cover = []
    for s in starts:
        e = s + width
        cover.append(sum(max(0.0, min(b, e) - max(a, s)) for a, b in sp))
    order = np.argsort(cover)[::-1]
    chosen: list[tuple[float, float]] = []
    for k in order:
        s = float(starts[k])
        if cover[k] <= 0:
            break
        if all(abs(s - c[0]) >= width for c in chosen):
            chosen.append((s, s + width))
        if len(chosen) >= n:
            break
    return chosen or [(0.0, min(duration, width))]


def detect(lid: WhisperLID, audio: np.ndarray, segs: list[Segment], sr: int = 16000) -> dict:
    dur = len(audio) / sr
    probs = []
    for a, b in windows_on_speech(segs, dur):
        probs.append(lid.lang_probs(audio[int(a * sr): int(b * sr)], sr))
    mean = {k: float(np.mean([p[k] for p in probs])) for k in probs[0]}
    top = max(mean, key=mean.get)
    return {"top": top, "p_top": round(mean[top], 4), "p_en": round(mean.get("en", 0.0), 4), "windows": len(probs)}


def load_cache(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def save_cache(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(sorted(data.items())), indent=1), encoding="utf-8")
