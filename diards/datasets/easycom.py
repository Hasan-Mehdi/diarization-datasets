"""EasyCom (Meta Reality Labs, CC BY-NC 4.0): conversations around a table in simulated restaurant noise,
recorded with AR glasses (6-mic array) worn by one participant, plus close-talk mics for the others.

12 main sessions (~5.3 h of "high quality" data), 3-5 participants each, recorded as 1-minute files
(``MM-SS-mmm`` = start time within the session; some minutes are missing because of redactions).
Annotations: human transcriptions with voice-activity start/end *video frames* (20 fps -> 50 ms resolution)
per participant, including the glasses wearer.

Normalization: each session's 1-minute files are concatenated in time order into one recording (annotation times
are shifted by the cumulative duration), so speaker identity has to be tracked over the whole ~30 min session.
View ``glasses`` = channel 1 (first channel) of the glasses array, 48 kHz int32 -> 16 kHz.
Files are fetched one by one from the repository's Git LFS storage (the 70 GB release archive is not needed).
Split: ``all``. Speaker ids: ``P<Participant_ID>`` (consistent within the corpus). UEM: whole concatenated session.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import requests

from ..annotation import Segment
from ..audio import is_normalized, load_mono16k, write_array
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download

API = "https://api.github.com/repos/facebookresearch/EasyComDataset/contents/Main/{dir}/{session}"
LFS = "https://media.githubusercontent.com/media/facebookresearch/EasyComDataset/main/Main/{dir}/{session}/{name}"
FPS = 20.0

META = DatasetMeta(
    name="easycom",
    title="EasyCom (AR-glasses conversations in restaurant noise)",
    homepage="https://github.com/facebookresearch/EasyComDataset",
    license="CC-BY-NC-4.0",
    license_url="https://creativecommons.org/licenses/by-nc/4.0/",
    annotation_redistributable=True,
    citation="J. Donley et al., 'EasyCom: An Augmented Reality Dataset to Support Algorithms for Easy Communication in Noisy Environments', arXiv:2107.04174, 2021.",
    source_version="facebookresearch/EasyComDataset main (Git LFS files, release v1.0.0)",
    description="Egocentric multi-party conversations (introductions, ordering food, puzzles, games) with loudspeaker restaurant noise.",
    access="Free (GitHub, Git LFS or a 70 GB split release archive).",
    reference="Human transcription with per-utterance voice-activity frames (20 fps).",
    default_view="glasses",
    views={"glasses": "AR-glasses microphone array, channel 1, 1-minute files concatenated per session"},
    gt_rating="B",
    gt_rating_reason=("Human-annotated voice activity per participant (including the glasses wearer), overlap present, "
                      "but utterance-level with 50 ms frame quantization; noise is played from loudspeakers."),
    choices=["Sessions = concatenated 1-minute files (Main/ only; Extra/ sessions with recording errors excluded).",
             "View glasses = array channel 1.", "Speaker ids: P<Participant_ID>.", "UEM: whole session."],
    domain="egocentric conversation in noise (AR glasses)",
)


def _read_text(p: Path) -> str:
    raw = p.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:  # a few transcription files are cp1252-encoded
        return raw.decode("cp1252")


def _list(dirname: str, session: str) -> list[str]:
    r = requests.get(API.format(dir=dirname, session=session), timeout=60)
    r.raise_for_status()
    return sorted(x["name"] for x in r.json())


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "easycom"
    w = DatasetWriter(META, root)
    sessions = [f"Session_{i}" for i in range(1, 13)][: limit or None]
    for sess in sessions:
        sid = w.session_id(sess)
        names = [n[:-5] for n in _list("Speech_Transcriptions", sess) if n.endswith(".json")]
        segs, chunks, offset = [], [], 0.0
        need_audio = not is_normalized(w.audio_path(sid))
        for n in names:
            ann = download(LFS.format(dir="Speech_Transcriptions", session=sess, name=f"{n}.json"),
                           base / "Speech_Transcriptions" / sess / f"{n}.json", quiet=True)
            wav = download(LFS.format(dir="Glasses_Microphone_Array_Audio", session=sess, name=f"{n}.wav"),
                           base / "Glasses_Microphone_Array_Audio" / sess / f"{n}.wav", quiet=True)
            import soundfile as sf

            dur = sf.info(str(wav)).duration
            if need_audio:
                chunks.append(load_mono16k(wav, channel=0))
            for u in json.loads(_read_text(ann)):
                a, b = u["Start_Frame"] / FPS, u["End_Frame"] / FPS
                if b > a:
                    segs.append(Segment(offset + a, offset + min(b, dur), f"P{u['Participant_ID']}"))
            offset += dur
        if need_audio:
            write_array(w.audio_path(sid), np.concatenate(chunks))
        w.add_session(sess, "all", segs, extra={"minutes": len(names)})
        print(f"  [easycom] {sess} ok ({len(names)} minutes)", flush=True)
    w.finalize([{"url": "https://github.com/facebookresearch/EasyComDataset"}])
