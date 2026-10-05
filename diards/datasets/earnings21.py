"""Earnings-21 (Rev.com, CC BY-SA 4.0): 44 English earnings calls, 39 h.

Audio (mp3) and RTTMs come from github.com/revdotcom/speech-datasets (release 202408, which fixed an off-by-one
speaker labelling issue in 4341191). The RTTMs were added in 2023 "to evaluate diarization"; Rev does not document
how their timings were produced (the human .nlp transcripts carry speaker labels but no timestamps), so they are
most likely a forced alignment of the human transcripts.
Splits: ``eval10`` = Rev's representative 10-file subset, ``other`` = remaining 34 files.
"""
from __future__ import annotations

import csv
import io

import requests

from ..annotation import Segment, read_rttm_single
from ..audio import convert, is_normalized
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download

RAW = "https://raw.githubusercontent.com/revdotcom/speech-datasets/main/earnings21"
MEDIA = "https://github.com/revdotcom/speech-datasets/raw/main/earnings21/media"

META = DatasetMeta(
    name="earnings21",
    title="Earnings-21",
    homepage="https://github.com/revdotcom/speech-datasets/tree/main/earnings21",
    license="CC-BY-SA-4.0",
    license_url="https://creativecommons.org/licenses/by-sa/4.0/",
    annotation_redistributable=True,
    citation="M. Del Rio et al., 'Earnings-21: A Practical Benchmark for ASR in the Wild', Interspeech 2021.",
    source_version="revdotcom/speech-datasets main (release 202408)",
    description="Public company earnings calls from 2020 (9 sectors): operator, executives and analysts; telephone/VoIP quality.",
    access="Free download from GitHub, no registration.",
    reference="Rev RTTMs (2023) derived from professional human transcripts; timing method undocumented.",
    default_view="default",
    views={"default": "Original call audio (mp3, 24-44.1 kHz) resampled to 16 kHz mono"},
    gt_rating="B-",
    gt_rating_reason=("Professional human transcripts with speaker labels (reviewed by senior transcriptionists); "
                      "segment timings come from an undocumented automatic step. Very little overlap, so labels are "
                      "easy to keep consistent; short backchannels/crosstalk tend to be absent."),
    choices=["Splits: eval10 (Rev's subset) and other.", "Speaker ids: <file>_<rev speaker index>.",
             "UEM: whole file."],
    domain="earnings calls (telephone/broadcast)",
)


def _ids(name: str) -> list[str]:
    txt = requests.get(f"{RAW}/{name}", timeout=60).text
    return [r["file_id"] for r in csv.DictReader(io.StringIO(txt))]


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "earnings21"
    w = DatasetWriter(META, root)
    all_ids = _ids("earnings21-file-metadata.csv")
    eval10 = set(_ids("eval10-file-metadata.csv"))
    n = 0
    for fid in all_ids:
        split = "eval10" if fid in eval10 else "other"
        if splits and split not in splits:
            continue
        if limit and n >= limit:
            break
        n += 1
        sid = w.session_id(fid)
        rttm = download(f"{RAW}/rttms/{fid}.rttm", base / "rttms" / f"{fid}.rttm", quiet=True)
        if not is_normalized(w.audio_path(sid)):
            mp3 = download(f"{MEDIA}/{fid}.mp3", base / "media" / f"{fid}.mp3", quiet=True)
            convert(mp3, w.audio_path(sid))
        segs = [Segment(s.start, s.end, f"{fid}_{s.speaker}") for s in read_rttm_single(rttm)]
        w.add_session(fid, split, segs)
        print(f"  [earnings21] {split} {fid} ok", flush=True)
    w.finalize([{"url": "https://github.com/revdotcom/speech-datasets"}])
