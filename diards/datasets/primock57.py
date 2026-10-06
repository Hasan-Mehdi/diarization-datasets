"""PriMock57 (Babylon Health, CC BY 4.0): 57 mock primary-care consultations (remote video calls), ~8.6 h.

Included as the reference point for the "poor ground truth" complaint; see PRIMOCK57.md for the analysis.

Audio: doctor and patient were recorded on separate channels (from the video-call streams). The ``mix`` view sums
them (like the repo's ``scripts/mix_audio.sh``); the separate channels are kept under the raw directory.
References:
  * primary: the official utterance-level TextGrid transcripts (one tier per channel; empty intervals = no speech).
  * rttm_alt/channel_activity: when each speaker is actually making sound, measured on their *own* channel
    (the channels are isolated by ~50 dB). Level threshold halfway (in dB) between the channel's median level inside
    and outside its labelled utterances; 10 ms frames, 5-frame smoothing, gaps < 0.2 s bridged, < 0.1 s dropped.
    Not human ground truth, but a much tighter speech/non-speech reference; see PRIMOCK57.md.
  * rttm_alt/silero_channel: Silero VAD ("x2": max of a stock run and a run with the state reset every 30 s) on each
    speaker's own channel, from the Silero VAD study (results/vad/primock57/silero_channel_rttm, CC BY 4.0). It
    ignores breaths and noise that the energy-based channel_activity counts; see docs/silero_vad_study.md.
Speaker ids: <consultation>_doctor / <consultation>_patient (doctor identities are not published per file).
Split: ``all``. UEM: whole recording.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from ..annotation import Segment, read_rttm_single
from ..audio import is_normalized, load_mono16k, write_array
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download, git_clone
from ..annotation import merge_intervals
from ..vad import HOP, frame_energy_db

REPO = "https://github.com/babylonhealth/primock57.git"
REPO_ROOT = Path(__file__).resolve().parents[2]
MEDIA = "https://media.githubusercontent.com/media/babylonhealth/primock57/main/audio/{name}"

META = DatasetMeta(
    name="primock57",
    title="PriMock57 (primary-care mock consultations)",
    homepage="https://github.com/babylonhealth/primock57",
    license="CC-BY-4.0",
    license_url="https://github.com/babylonhealth/primock57/blob/main/LICENSE.md",
    annotation_redistributable=True,
    citation="A. Papadopoulos Korfiatis et al., 'PriMock57: A Dataset Of Primary Care Mock Consultations', ACL 2022.",
    source_version="babylonhealth/primock57 (git HEAD)",
    description="Remote (video-call) mock GP consultations: 7 clinicians, 57 staff acting as patients from case cards.",
    access="Free download from GitHub (audio in Git LFS).",
    reference="Utterance-level TextGrid transcripts per channel (made for ASR evaluation).",
    default_view="mix",
    views={"mix": "Doctor + patient channels summed (as scripts/mix_audio.sh)"},
    gt_rating="D (official) / B (channel-based RTTMs)",
    gt_rating_reason="Utterance-level, ASR-oriented timings; see PRIMOCK57.md for measured problems.",
    choices=["Speaker ids: <consultation>_doctor / _patient.", "UEM: whole recording.",
             "Alternative reference rttm_alt/channel_activity from calibrated per-channel activity (diagnostic)."],
    domain="medical consultations (remote, 2 speakers)",
)


def channel_activity(x: np.ndarray, labelled: list[tuple[float, float]], fill: float = 0.2,
                     min_len: float = 0.1) -> tuple[list[tuple[float, float]], float]:
    """Own-channel activity with a level threshold calibrated on the labelled vs unlabelled level medians."""
    e = frame_energy_db(x)
    lab = np.zeros(len(e), bool)
    for a, b in labelled:
        lab[int(a / HOP): int(b / HOP)] = True
    if not lab.any() or lab.all():
        return [], float("nan")
    thr = (float(np.median(e[lab])) + float(np.median(e[~lab]))) / 2
    act = np.convolve((e > thr).astype(float), np.ones(5) / 5, mode="same") > 0.5
    d = np.diff(np.concatenate([[0], act.astype(np.int8), [0]]))
    ivs = [(a * HOP, b * HOP) for a, b in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1))]
    ivs = merge_intervals(ivs, gap=fill)
    return [(a, b) for a, b in ivs if b - a >= min_len], thr


def read_textgrid(path: Path) -> list[tuple[float, float, str]]:
    txt = path.read_text(encoding="utf-8", errors="replace")
    out = []
    for m in re.finditer(r"xmin = ([\d.eE+-]+)\s*\n\s*xmax = ([\d.eE+-]+)\s*\n\s*text = \"(.*?)\"\s*\n", txt, re.S):
        a, b, t = float(m.group(1)), float(m.group(2)), m.group(3).strip()
        if t and b > a:
            out.append((a, b, t))
    return out


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "primock57"
    repo = git_clone(REPO, base / "repo")
    consults = sorted({p.name.rsplit("_", 1)[0] for p in (repo / "transcripts").glob("*.TextGrid")})[: limit or None]
    w = DatasetWriter(META, root)
    for c in consults:
        sid = w.session_id(c)
        chans = {}
        for role in ("doctor", "patient"):
            src = download(MEDIA.format(name=f"{c}_{role}.wav"), base / "audio" / f"{c}_{role}.wav", quiet=True)
            chans[role] = load_mono16k(src)
        n = max(len(x) for x in chans.values())
        if not is_normalized(w.audio_path(sid)):
            mixed = np.zeros(n, dtype=np.float64)
            for x in chans.values():
                mixed[: len(x)] += x
            m = np.abs(mixed).max()
            if m > 0.9:
                mixed *= 0.9 / m
            write_array(w.audio_path(sid), mixed.astype(np.float32))
        segs, act_segs = [], []
        for role in ("doctor", "patient"):
            spk = f"{c}_{role}"
            utts = [(a, b) for a, b, t in read_textgrid(repo / "transcripts" / f"{c}_{role}.TextGrid")]
            segs += [Segment(a, b, spk) for a, b in utts]
            ivs, _ = channel_activity(chans[role], utts)
            act_segs += [Segment(a, b, spk) for a, b in ivs]
        alt = {"channel_activity": act_segs}
        silero = REPO_ROOT / "results" / "vad" / "primock57" / "silero_channel_rttm" / f"{sid}.rttm"
        if silero.exists():
            alt["silero_channel"] = read_rttm_single(silero)
        w.add_session(c, "all", segs, alt_refs=alt)
        print(f"  [primock57] {c} ok", flush=True)
    w.finalize([{"url": REPO}])
