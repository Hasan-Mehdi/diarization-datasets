"""Audio conversion to the normalized format: 16 kHz, mono, 16-bit PCM WAV.

ffmpeg is used when available (handles mp3/mp4/flac/sph/raw); soundfile + soxr otherwise.
All writers are atomic (write ``*.tmp.wav`` then rename) so an interrupted run never leaves a truncated file
that a later idempotent run would mistake for a finished one.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

import numpy as np
import soundfile as sf

TARGET_SR = 16000


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def audio_info(path: str | Path) -> dict:
    info = sf.info(str(path))
    return {
        "sample_rate": info.samplerate,
        "channels": info.channels,
        "frames": info.frames,
        "duration": info.frames / info.samplerate if info.samplerate else 0.0,
        "subtype": info.subtype,
    }


def is_normalized(path: str | Path) -> bool:
    """True if ``path`` exists and is a 16 kHz mono PCM_16 WAV with at least one sample."""
    p = Path(path)
    if not p.exists() or p.stat().st_size <= 44:
        return False
    try:
        i = audio_info(p)
    except Exception:
        return False
    return i["sample_rate"] == TARGET_SR and i["channels"] == 1 and i["subtype"] == "PCM_16" and i["frames"] > 0


def _tmp(dst: Path) -> Path:
    return dst.with_name(dst.stem + ".tmp" + dst.suffix)


def convert(src: str | Path, dst: str | Path, channel: int | None = None, start: float | None = None,
            duration: float | None = None, extra_input_args: Sequence[str] = (), force: bool = False) -> Path:
    """Convert ``src`` to 16 kHz mono 16-bit WAV at ``dst``.

    ``channel``: 0-based channel to keep (default: average of all channels).
    ``start`` / ``duration``: optional excerpt in seconds.
    ``extra_input_args``: ffmpeg options placed before ``-i`` (e.g. raw PCM format description).
    """
    dst = Path(dst)
    if not force and is_normalized(dst):
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = _tmp(dst)
    if have_ffmpeg():
        cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y"]
        if start is not None:
            cmd += ["-ss", f"{start:.3f}"]
        if duration is not None:
            cmd += ["-t", f"{duration:.3f}"]
        cmd += list(extra_input_args) + ["-i", str(src), "-vn"]
        if channel is not None:
            cmd += ["-af", f"pan=mono|c0=c{channel}"]
        cmd += ["-ac", "1", "-ar", str(TARGET_SR), "-c:a", "pcm_s16le", "-f", "wav", str(tmp)]
        subprocess.run(cmd, check=True)
    else:
        data, sr = sf.read(str(src), always_2d=True, dtype="float32")
        if start is not None:
            data = data[int(start * sr):]
        if duration is not None:
            data = data[: int(duration * sr)]
        mono = data[:, channel] if channel is not None else data.mean(axis=1)
        _write(tmp, _resample(mono, sr))
    os.replace(tmp, dst)
    return dst


def _resample(x: np.ndarray, sr: int) -> np.ndarray:
    if sr == TARGET_SR:
        return x
    import soxr

    return soxr.resample(x, sr, TARGET_SR)


def _write(path: Path, x: np.ndarray) -> None:
    sf.write(str(path), np.clip(x, -1.0, 1.0), TARGET_SR, subtype="PCM_16", format="WAV")


def load_mono16k(src: str | Path, channel: int | None = None) -> np.ndarray:
    """Load any audio as float32 mono 16 kHz (uses ffmpeg for formats soundfile cannot read)."""
    try:
        data, sr = sf.read(str(src), always_2d=True, dtype="float32")
        mono = data[:, channel] if channel is not None else data.mean(axis=1)
        return _resample(mono, sr).astype(np.float32)
    except Exception:
        if not have_ffmpeg():
            raise
        cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vn"]
        if channel is not None:
            cmd += ["-af", f"pan=mono|c0=c{channel}"]
        cmd += ["-ac", "1", "-ar", str(TARGET_SR), "-f", "f32le", "-"]
        out = subprocess.run(cmd, check=True, capture_output=True).stdout
        return np.frombuffer(out, dtype=np.float32).copy()


def mix(srcs: Sequence[str | Path], dst: str | Path, channel: int | None = None, force: bool = False,
        peak: float = 0.9) -> Path:
    """Sum several recordings (e.g. close-talk headsets) into one 16 kHz mono WAV.

    Signals are summed sample-aligned from t=0 and the result is scaled down only if it would clip
    (peak normalised to ``peak``). Shorter inputs are zero-padded.
    """
    dst = Path(dst)
    if not force and is_normalized(dst):
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    signals = [load_mono16k(s, channel) for s in srcs]
    n = max(len(s) for s in signals)
    acc = np.zeros(n, dtype=np.float64)
    for s in signals:
        acc[: len(s)] += s
    m = np.abs(acc).max() if n else 0.0
    if m > peak:
        acc *= peak / m
    tmp = _tmp(dst)
    _write(tmp, acc.astype(np.float32))
    os.replace(tmp, dst)
    return dst


def write_array(dst: str | Path, x: np.ndarray, sr: int = TARGET_SR) -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = _tmp(dst)
    _write(tmp, _resample(np.asarray(x, dtype=np.float32), sr))
    os.replace(tmp, dst)
    return dst
