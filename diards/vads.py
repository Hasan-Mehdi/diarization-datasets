"""Voice-activity detectors for the Silero VAD study (docs/silero_vad_study.md), with a per-session cache.

Detectors (all run on the normalized 16 kHz mono audio, on CPU):

* ``silero``: Silero VAD (``pip install --no-deps silero-vad``, tested with 6.2.3; JIT model, one thread). Speech
  probabilities per 32 ms frame (512 samples) are cached; intervals come from the package's own post-processing
  (``get_speech_timestamps_from_probs``) with its documented defaults (:data:`SILERO_DEFAULTS`): threshold 0.5
  (exit threshold 0.35), min speech 250 ms, min silence 100 ms, 30 ms padding on each side.
* ``silero_r30``: the same model with its recurrent state reset every 30 s (each window warmed up on the preceding
  2 s). The stock streaming loop never resets the state, and on some long recordings with continuous speech the
  state drifts into a regime where the model outputs ~0 for minutes over clearly audible speech (seen on CallHome
  English, MSDWild); the reset removes that failure and otherwise changes < 1% of frames.
* ``webrtc``: WebRTC VAD (``webrtcvad``), 30 ms frames, aggressiveness 0-3 (all four cached as a bit mask), then the
  same min-silence / min-speech / padding rules as Silero.
* ``energy``: the repo's transparent energy VAD (:func:`diards.vad.energy_vad`, default settings, as used by
  ``diards validate --vad``); the 10 ms frame log-energies are cached too.
* ``nemotron``: speaker-agnostic union of a cached Nemotron 3 Diarization hypothesis (``diards evaluate``).
* ``pyannote``: pyannote segmentation-3.0 VAD pipeline, computed by ``scripts/vad_pyannote.py`` in a separate env
  and cached as ``<session_id>.pyannote.npz`` next to the main cache file (evaluated subsets only).

Cache: ``<study>/vad/<dataset>.<view>/<session_id>.npz`` with arrays ``silero`` (float16, 32 ms), ``webrtc`` (uint8
bit mask, 30 ms; bit m = mode m), ``energy_db`` (float16, 30 ms frames every 10 ms), ``energy_ivs`` (float32 [n, 2]),
``n_samples``. ``<study>`` is ``$DIARDS_VAD_STUDY`` or ``<base>/vad-study``.

Usage::

    python -m diards.vads <dataset> [--view V] [--split S ...] [--workers 8]
    python -m diards.vads primock57 --channels        # doctor / patient channels of the raw download
"""
from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .annotation import merge_intervals, read_rttm_single
from .config import _base

SR = 16000
SILERO_HOP = 512 / SR          # 32 ms
WEBRTC_HOP = 0.030
ENERGY_HOP = 0.010
SILERO_DEFAULTS = dict(threshold=0.5, neg_threshold=None, min_speech_duration_ms=250, min_silence_duration_ms=100,
                       speech_pad_ms=30)
WEBRTC_DEFAULTS = dict(mode=2, min_silence=0.1, min_speech=0.25, pad=0.03)

RESET_EVERY = 30.0
RESET_WARMUP = 2.0

_SILERO = None


def study_root() -> Path:
    return Path(os.environ.get("DIARDS_VAD_STUDY", _base() / "vad-study"))


def cache_path(dataset: str, view: str, session_id: str) -> Path:
    return study_root() / "vad" / f"{dataset}.{view}" / f"{session_id}.npz"


# ----------------------------------------------------------------------------- frame helpers

def frames_to_intervals(active: np.ndarray, hop: float, frame: float | None = None) -> list[tuple[float, float]]:
    """Runs of True frames -> ``(start, end)`` seconds; frame i covers ``[i * hop, i * hop + frame)``."""
    frame = hop if frame is None else frame
    d = np.diff(np.concatenate([[0], np.asarray(active, dtype=np.int8), [0]]))
    starts, ends = np.flatnonzero(d == 1), np.flatnonzero(d == -1)
    return [(round(float(a * hop), 3), round(float((b - 1) * hop + frame), 3)) for a, b in zip(starts, ends)]


def postprocess(ivs, min_silence: float = 0.1, min_speech: float = 0.25, pad: float = 0.03,
                duration: float | None = None) -> list[tuple[float, float]]:
    """Bridge gaps shorter than ``min_silence``, drop chunks shorter than ``min_speech``, pad both sides."""
    ivs = [(a, b) for a, b in merge_intervals(ivs, gap=min_silence) if b - a >= min_speech]
    hi = duration if duration is not None else float("inf")
    return merge_intervals((max(0.0, a - pad), min(hi, b + pad)) for a, b in ivs)


def to_raster(ivs, n: int, step: float) -> np.ndarray:
    """Boolean raster of ``n`` frames of ``step`` seconds (frame i active if its start lies in an interval)."""
    m = np.zeros(n, bool)
    for a, b in ivs:
        m[max(0, int(np.ceil(a / step - 1e-9))): max(0, int(np.ceil(b / step - 1e-9)))] = True
    return m


# ----------------------------------------------------------------------------- detectors

def silero_model():
    global _SILERO
    if _SILERO is None:
        import torch
        from silero_vad import load_silero_vad

        torch.set_num_threads(1)
        _SILERO = load_silero_vad()
    return _SILERO


def silero_probs(x: np.ndarray, reset_every: float | None = None, warmup: float = RESET_WARMUP) -> np.ndarray:
    """Per-32 ms-frame speech probabilities, exactly as ``silero_vad.get_speech_timestamps`` computes them.

    With ``reset_every`` the model state is reset every ``reset_every`` seconds; each window is processed from
    ``warmup`` seconds earlier and the warm-up outputs are discarded."""
    if reset_every:
        n = (len(x) + 511) // 512
        out = np.empty(n, np.float32)
        step, w = int(round(reset_every * SR / 512)), int(round(warmup * SR / 512))
        for f0 in range(0, n, step):
            a = max(0, f0 - w)
            p = silero_probs(x[a * 512:(f0 + step) * 512])
            out[f0:f0 + step] = p[f0 - a:f0 - a + step][: len(out[f0:f0 + step])]
        return out
    import torch

    model = silero_model()
    model.reset_states()
    n = len(x)
    pad = (-n) % 512
    xt = torch.from_numpy(np.concatenate([np.asarray(x, np.float32), np.zeros(pad, np.float32)]))
    out = np.empty(len(xt) // 512, np.float32)
    with torch.no_grad():
        for i in range(len(out)):
            out[i] = model(xt[i * 512:(i + 1) * 512], SR).item()
    return out


def silero_intervals(probs: np.ndarray, n_samples: int | None = None, **params) -> list[tuple[float, float]]:
    """Silero speech intervals (seconds) from cached probabilities, via the package's own post-processing."""
    from silero_vad import get_speech_timestamps_from_probs

    p = {**SILERO_DEFAULTS, **params}
    ts = get_speech_timestamps_from_probs(list(map(float, probs)), sampling_rate=SR, return_seconds=True,
                                          time_resolution=3, audio_length_samples=n_samples, **p)
    return [(t["start"], t["end"]) for t in ts]


def webrtc_mask(x: np.ndarray) -> np.ndarray:
    """uint8 per 30 ms frame; bit m set when WebRTC VAD in aggressiveness mode m calls the frame speech."""
    import webrtcvad

    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    n = int(WEBRTC_HOP * SR)
    count = len(pcm) // n
    vads = [webrtcvad.Vad(m) for m in range(4)]
    out = np.zeros(count, np.uint8)
    for i in range(count):
        fr = pcm[i * n:(i + 1) * n].tobytes()
        for m, v in enumerate(vads):
            if v.is_speech(fr, SR):
                out[i] |= 1 << m
    return out


def webrtc_intervals(mask: np.ndarray, mode: int = 2, duration: float | None = None, **params):
    p = {**WEBRTC_DEFAULTS, **params, "mode": mode}
    raw = frames_to_intervals((mask >> p["mode"]) & 1, WEBRTC_HOP)
    return postprocess(raw, p["min_silence"], p["min_speech"], p["pad"], duration)


def nemotron_intervals(hyp_rttm: str | Path) -> list[tuple[float, float]]:
    return merge_intervals((s.start, s.end) for s in read_rttm_single(hyp_rttm))


def compute(x: np.ndarray) -> dict:
    from .vad import frame_energy_db, energy_vad

    t0 = time.time()
    out = {"n_samples": np.int64(len(x)), "silero": silero_probs(x).astype(np.float16),
           "silero_r30": silero_probs(x, RESET_EVERY).astype(np.float16)}
    t1 = time.time()
    out["webrtc"] = webrtc_mask(x)
    out["energy_db"] = frame_energy_db(x).astype(np.float16)
    ivs, _ = energy_vad(x)
    out["energy_ivs"] = np.asarray(ivs, np.float32).reshape(-1, 2)
    out["seconds"] = np.array([t1 - t0, time.time() - t1], np.float32)
    return out


# ----------------------------------------------------------------------------- cache reader

@dataclass
class VadCache:
    """Cached detector outputs for one session; every accessor returns sorted ``(start, end)`` seconds."""
    path: Path
    data: dict

    @classmethod
    def load(cls, dataset: str, view: str, session_id: str) -> "VadCache":
        return cls.from_path(cache_path(dataset, view, session_id))

    @classmethod
    def from_path(cls, p: Path) -> "VadCache":
        with np.load(p) as z:
            data = {k: z[k] for k in z.files}
        side = p.with_suffix(".pyannote.npz")
        if side.exists():
            with np.load(side) as z:
                data["pyannote_ivs"] = z["ivs"]
        return cls(p, data)

    @property
    def duration(self) -> float:
        return int(self.data["n_samples"]) / SR

    @property
    def silero_probs(self) -> np.ndarray:
        return self.data["silero"].astype(np.float32)

    def silero(self, reset: bool = False, **params) -> list[tuple[float, float]]:
        p = self.data["silero_r30" if reset else "silero"].astype(np.float32)
        return silero_intervals(p, int(self.data["n_samples"]), **params)

    def webrtc(self, mode: int = 2, **params) -> list[tuple[float, float]]:
        return webrtc_intervals(self.data["webrtc"], mode, self.duration, **params)

    def energy(self) -> list[tuple[float, float]]:
        return [(float(a), float(b)) for a, b in self.data["energy_ivs"]]

    def get(self, vad: str) -> list[tuple[float, float]]:
        """``silero`` / ``silero_r30`` / ``silero@0.3`` (threshold) / ``webrtc`` / ``webrtc@3`` (mode) / ``energy`` /
        ``pyannote``."""
        name, _, arg = vad.partition("@")
        if name in ("silero", "silero_r30"):
            return self.silero(reset=name == "silero_r30", **({"threshold": float(arg)} if arg else {}))
        if name == "webrtc":
            return self.webrtc(int(arg) if arg else WEBRTC_DEFAULTS["mode"])
        if name == "energy":
            return self.energy()
        if name == "pyannote":
            if "pyannote_ivs" not in self.data:
                raise FileNotFoundError(self.path.with_suffix(".pyannote.npz"))
            return [(float(a), float(b)) for a, b in self.data["pyannote_ivs"]]
        raise KeyError(vad)


# ----------------------------------------------------------------------------- batch computation

CACHE_KEYS = ("silero", "silero_r30", "webrtc", "energy_db", "energy_ivs", "n_samples")


def _complete(path: Path) -> bool:
    if not path.exists():
        return False
    with np.load(path) as z:
        return all(k in z.files for k in CACHE_KEYS)


def _work(job):
    audio_path, out_path, channel = job
    from .audio import load_mono16k

    out_path = Path(out_path)
    if _complete(out_path):
        return str(out_path), 0.0, 0.0
    x = load_mono16k(audio_path, channel)
    if out_path.exists():  # older cache without the state-reset variant: add it
        with np.load(out_path) as z:
            res = {k: z[k] for k in z.files}
        t0 = time.time()
        res["silero_r30"] = silero_probs(x, RESET_EVERY).astype(np.float16)
        res["seconds"] = np.array([time.time() - t0, 0.0], np.float32)
    else:
        res = compute(x)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_name(out_path.stem + ".tmp.npz")
    np.savez_compressed(tmp, **res)
    os.replace(tmp, out_path)
    return str(out_path), len(x) / SR, float(res["seconds"].sum())


def jobs_for(dataset: str, view: str | None = None, splits=None, root=None, channels: bool = False):
    from .config import raw_root
    from .core import NormalizedDataset

    if channels:
        if dataset != "primock57":
            raise SystemExit("--channels is only implemented for primock57")
        audio = raw_root() / "primock57" / "audio"
        return [(str(p), str(cache_path("primock57", "channels", p.stem)), None) for p in sorted(audio.glob("*.wav"))]
    ds = NormalizedDataset(dataset, root)
    view = view or ds.default_view
    return [(str(s.audio_path), str(cache_path(dataset, view, s.session_id)), None)
            for s in ds.sessions(view=view) if not splits or s.split in splits]


def run_jobs(jobs, workers: int = 8, label: str = "") -> None:
    from concurrent.futures import ProcessPoolExecutor, as_completed

    todo = [j for j in jobs if not _complete(Path(j[1]))]
    print(f"[vads] {label}: {len(jobs)} sessions, {len(todo)} to compute, {workers} workers", flush=True)
    if not todo:
        return
    t0, audio_s = time.time(), 0.0
    # longest first, so the pool does not end on one long file
    todo.sort(key=lambda j: -Path(j[0]).stat().st_size)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_work, j) for j in todo]
        for i, f in enumerate(as_completed(futs), 1):
            path, dur, sec = f.result()
            audio_s += dur
            if i % 25 == 0 or i == len(todo):
                el = time.time() - t0
                print(f"[vads] {label}: {i}/{len(todo)} done, {audio_s / 3600:.1f} h audio in {el / 60:.1f} min "
                      f"({audio_s / max(el, 1e-9):.0f}x real time overall)", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset")
    ap.add_argument("--view")
    ap.add_argument("--split", action="append", dest="splits")
    ap.add_argument("--root")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--channels", action="store_true", help="PriMock57: per-channel raw audio")
    a = ap.parse_args(argv)
    jobs = jobs_for(a.dataset, a.view, a.splits, a.root, a.channels)
    run_jobs(jobs, a.workers, f"{a.dataset}.{'channels' if a.channels else a.view or 'default'}")


if __name__ == "__main__":
    from diards.vads import main as _main  # functions pickled for the workers must come from diards.vads

    _main()
