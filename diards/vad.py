"""A deliberately simple energy VAD, used only as an independent sanity check of reference speech coverage.

It is not meant to be accurate on noisy far-field audio; it is meant to be *transparent*: speech = frames whose
log-energy is well above the recording's own noise floor. Regions where it fires but the reference has no speech
(and the opposite) are listed so a human can listen to them.
"""
from __future__ import annotations

import numpy as np

from .annotation import merge_intervals

FRAME = 0.030
HOP = 0.010


def frame_energy_db(x: np.ndarray, sr: int = 16000) -> np.ndarray:
    n, h = int(FRAME * sr), int(HOP * sr)
    if len(x) < n:
        return np.zeros(0)
    count = 1 + (len(x) - n) // h
    # cumulative sum of squares -> O(N) framed energy
    c = np.concatenate([[0.0], np.cumsum(x.astype(np.float64) ** 2)])
    starts = np.arange(count) * h
    e = (c[starts + n] - c[starts]) / n
    return 10 * np.log10(e + 1e-12)


def energy_vad(x: np.ndarray, sr: int = 16000, min_rise_db: float = 9.0, rel: float = 0.3,
               min_speech: float = 0.15, fill_gap: float = 0.3) -> tuple[list[tuple[float, float]], dict]:
    """Return (speech intervals, info). Threshold = floor + max(min_rise_db, rel * (p99 - floor)),
    floor = 10th percentile of frame energies (digital silence frames excluded)."""
    e = frame_energy_db(x, sr)
    if e.size == 0:
        return [], {"floor_db": None, "threshold_db": None}
    valid = e[e > -100]
    if valid.size == 0:
        return [], {"floor_db": None, "threshold_db": None}
    floor = float(np.percentile(valid, 10))
    top = float(np.percentile(valid, 99))
    thr = floor + max(min_rise_db, rel * (top - floor))
    active = e > thr
    # 5-frame majority smoothing
    k = 5
    sm = np.convolve(active.astype(float), np.ones(k) / k, mode="same") > 0.5
    ivs = []
    start = None
    for i, a in enumerate(sm):
        if a and start is None:
            start = i
        elif not a and start is not None:
            ivs.append((start * HOP, i * HOP + FRAME))
            start = None
    if start is not None:
        ivs.append((start * HOP, len(sm) * HOP + FRAME))
    ivs = merge_intervals(ivs, gap=fill_gap)
    ivs = [(a, b) for a, b in ivs if b - a >= min_speech]
    return ivs, {"floor_db": round(floor, 1), "threshold_db": round(thr, 1), "p99_db": round(top, 1)}
