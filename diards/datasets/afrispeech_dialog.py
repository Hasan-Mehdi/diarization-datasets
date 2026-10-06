"""AfriSpeech-Dialog v1 (Intron Health, CC BY-NC-SA 4.0): African-accented English two-party conversations,
20 simulated doctor-patient consultations + 29 general-topic conversations (~7 h).

Only 30 of the 49 published conversations carry timestamps (9 medical, 21 general, as the dataset card states);
the others cannot be used for diarization scoring and are skipped. Transcripts look like::

    00:06:100
    [Speaker 2]: Doctor, I have been having ...
    00:32:98

i.e. a start time, the turn, an end time, written by hand as MM:SS:cc. The hundredths field clusters at 96-100
and 00-04, so the effective precision is about one second (and values such as ``100`` or ``-1`` occur).
Splits: ``medical`` / ``general`` (domain field).
UEM: the transcribed span +/- 1 s. Five recordings continue for 48-100 s of conversation after the last
labelled turn (found by the Silero VAD study, Whisper-confirmed; results/vad/uem_check.json).
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from ..annotation import Segment
from ..audio import convert, is_normalized
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import hf_download

REPO = "intronhealth/afrispeech-dialog"
TS = re.compile(r"^\s*\[?(-?\d{1,2}):(-?\d{1,2}):(-?\d{1,3})\]?\s*$")
SPK = re.compile(r"^\s*\[?(Speaker\s*\d+)\]?\s*:\s*(.*)$", re.I)

META = DatasetMeta(
    name="afrispeech_dialog",
    title="AfriSpeech-Dialog v1 (timestamped subset)",
    homepage="https://huggingface.co/datasets/intronhealth/afrispeech-dialog",
    license="CC-BY-NC-SA-4.0",
    license_url="https://creativecommons.org/licenses/by-nc-sa/4.0/",
    citation="M. Sanni et al., 'Afrispeech-Dialog: A Benchmark Dataset for Spontaneous English Conversations in Healthcare and Beyond', NAACL 2025.",
    source_version="huggingface.co/datasets/intronhealth/afrispeech-dialog (main)",
    description="Remote two-party conversations in Nigerian, Kenyan and South African accented English; simulated consultations and general chat.",
    access="Free on Hugging Face (not gated).",
    reference="Hand-typed turn start/end times (MM:SS:cc), one speaker turn per entry.",
    default_view="default",
    views={"default": "Original recording, mono 16 kHz"},
    gt_rating="D",
    gt_rating_reason=("Human transcripts, but timestamps are hand-typed with ~1 s effective precision and are "
                      "~0.45 s early on median; overlap/backchannels absent; untimed speech; 3/49 files without times."),
    choices=["Only the 30 conversations with timestamps are included.", "Times parsed as MM:SS + cc/100.",
             "Speaker ids: <file>_<Speaker N>.", "Splits: medical / general.",
             "UEM: transcribed span +/- 1 s (untranscribed tails excluded)."],
    domain="medical-like consultations + general conversation",
)


def _t(m) -> float:
    mm, ss, cc = (int(g) for g in m.groups())
    return mm * 60 + ss + cc / 100.0


def parse_transcript(text: str) -> list[tuple[float, float, str]]:
    """(start, end, speaker) for every turn that has a time line before and after it."""
    out = []
    last_t = None
    pending = None  # (start, speaker)
    for line in text.splitlines():
        m = TS.match(line)
        if m:
            t = _t(m)
            if pending is not None:
                out.append((pending[0], t, pending[1]))
                pending = None
            last_t = t
            continue
        s = SPK.match(line)
        if s:
            if pending is not None:  # turn without closing time: close at this turn's start (unknown)
                pending = None
            if last_t is not None:
                pending = (last_t, re.sub(r"\s+", " ", s.group(1)).title())
    return out


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "afrispeech_dialog"
    meta_csv = hf_download(REPO, "metadata.csv", base / "hf")
    df = pd.read_csv(meta_csv)
    w = DatasetWriter(META, root)
    n = 0
    for _, r in df.iterrows():
        if splits and r.domain not in splits:
            continue
        turns = parse_transcript(r.transcript)
        if not turns:
            continue
        if limit and n >= limit:
            break
        n += 1
        fid = Path(r.file_name).stem.split("_")[0]
        sid = w.session_id(fid)
        if not is_normalized(w.audio_path(sid)):
            src = hf_download(REPO, r.file_name, base / "hf")
            convert(src, w.audio_path(sid))
        segs = [Segment(a, b, f"{fid}_{s.replace(' ', '')}") for a, b, s in turns]
        lo, hi = min(g.start for g in segs), max(g.end for g in segs)
        w.add_session(fid, r.domain, segs, uem=[(max(0.0, lo - 1.0), hi + 1.0)], extra={"accent": r.accent, "country": r.country,
                                                  "original_file": r.file_name, "turns_with_times": len(turns)})
        print(f"  [afrispeech_dialog] {r.domain} {fid} ok ({len(turns)} turns)", flush=True)
    w.finalize([{"url": f"https://huggingface.co/datasets/{REPO}"}])
