"""PriMock57 (Babylon Health, CC BY 4.0): 57 mock primary-care consultations (remote video calls), ~8.6 h.

Included as the reference point for the "poor ground truth" complaint; see PRIMOCK57.md for the analysis.

Audio: doctor and patient were recorded on separate channels (from the video-call streams). The ``mix`` view sums
them (like the repo's ``scripts/mix_audio.sh``); the separate channels are kept under the raw directory.
References:
  * primary: the official utterance-level TextGrid transcripts (one tier per channel; empty intervals = no speech).
  * rttm_alt/channel_vad: speaker activity measured on each speaker's *own* channel with the energy VAD in
    diards.vad (min speech 0.15 s, gaps < 0.3 s bridged). This is not human ground truth; it shows how far the
    official timings are from what is actually audible on each channel.
Speaker ids: <consultation>_doctor / <consultation>_patient (doctor identities are not published per file).
Split: ``all``. UEM: whole recording.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from ..annotation import Segment
from ..audio import is_normalized, load_mono16k, write_array
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download, git_clone
from ..vad import energy_vad

REPO = "https://github.com/babylonhealth/primock57.git"
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
    gt_rating="D",
    gt_rating_reason="Utterance-level, ASR-oriented timings; see PRIMOCK57.md for measured problems.",
    choices=["Speaker ids: <consultation>_doctor / _patient.", "UEM: whole recording.",
             "Alternative reference rttm_alt/channel_vad from per-channel energy VAD (diagnostic only)."],
    domain="medical consultations (remote, 2 speakers)",
)


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
        segs, words, vad_segs = [], [], []
        for role in ("doctor", "patient"):
            spk = f"{c}_{role}"
            for a, b, t in read_textgrid(repo / "transcripts" / f"{c}_{role}.TextGrid"):
                segs.append(Segment(a, b, spk))
            ivs, _ = energy_vad(chans[role])
            vad_segs += [Segment(a, b, spk) for a, b in ivs]
        w.add_session(c, "all", segs, alt_refs={"channel_vad": vad_segs})
        print(f"  [primock57] {c} ok", flush=True)
    w.finalize([{"url": REPO}])
