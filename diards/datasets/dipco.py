"""DiPCo - Dinner Party Corpus (Amazon, CDLA-Permissive-1.0), Zenodo record 8122551.

10 sessions (dev: S02 S04 S05 S09 S10; eval: S01 S03 S06 S07 S08), 4 participants each, 5.3 h, recorded in a lab
dining room with headsets plus five 7-mic devices; music is played from a given point in each session.
Views:
  * ``farfield`` (default) - device U01, channel 1
  * ``ihm-mix``  - sum of the four close-talk headsets
References:
  * primary: the human utterance segments of the transcription JSON (close-talk times; the README says long
    stretches of speech were split into segments of up to 10-15 s at "logical" points, so boundaries are loose).
  * rttm_alt/closetalk_activity: diagnostic per-headset activity (level threshold halfway between each headset's
    median level inside/outside its labelled utterances, gaps < 0.2 s bridged, < 0.1 s dropped), intersected with
    the speaker's labelled utterances +/- 0.5 s so that crosstalk from neighbours is not counted.
UEM: whole session. Speaker ids: DiPCo participant ids (P01-P32), global.
"""
from __future__ import annotations

import json
import tarfile
from pathlib import Path

from ..annotation import Segment, intersect, merge_intervals
from ..audio import convert, is_normalized, load_mono16k, mix
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download
from .primock57 import channel_activity

URL = "https://zenodo.org/api/records/8122551/files/DipCo.tgz/content"
MD5 = "2297eb9334f3b90e02b54b708e501b24"
SESSIONS = {"dev": ["S02", "S04", "S05", "S09", "S10"], "eval": ["S01", "S03", "S06", "S07", "S08"]}

META = DatasetMeta(
    name="dipco",
    title="DiPCo - Dinner Party Corpus",
    homepage="https://zenodo.org/records/8122551",
    license="CDLA-Permissive-1.0",
    license_url="https://cdla.dev/permissive-1-0/",
    annotation_redistributable=True,
    citation="M. Van Segbroeck et al., 'DiPCo - Dinner Party Corpus', Interspeech 2020.",
    source_version="Zenodo 8122551 DipCo.tgz (md5 2297eb93...)",
    description="Simulated dinner parties of 4 Amazon volunteers in a lab dining room, headsets + 5 far-field arrays, background music in part of each session.",
    access="Free download from Zenodo (13.4 GB), no registration.",
    reference="Human transcription of each headset, utterance segments of up to 10-15 s.",
    default_view="farfield",
    views={"farfield": "Device U01, channel 1 (far-field)", "ihm-mix": "Sum of the 4 close-talk headsets"},
    gt_rating="B",
    gt_rating_reason=("Every participant on a headset and transcribed, overlap fully covered, but segments are "
                      "ASR-oriented (split only at 'logical' points, up to 10-15 s), so pauses are labelled as speech."),
    choices=["Splits: official dev / eval.", "Speaker ids: P01-P32 (global).", "UEM: whole session.",
             "farfield view: U01.CH1.", "Times: the 'close-talk' entry of start_time/end_time (identical for all devices)."],
    domain="dinner party (lab, far-field)",
)


def _t(s: str) -> float:
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def _extract(tgz: Path, dest: Path, wanted: set[str]) -> None:
    missing = {m for m in wanted if not (dest / m).exists()}
    if not missing:
        return
    with tarfile.open(tgz, "r|gz") as t:
        for m in t:
            if m.name in missing:
                t.extract(m, dest)
                missing.discard(m.name)
                if not missing:
                    break


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "dipco"
    tgz = download(URL, base / "DipCo.tgz", md5=None)
    views = views or list(META.views)
    ex = base / "ex"
    w = DatasetWriter(META, root)
    for split in splits or ["dev", "eval"]:
        sessions = SESSIONS[split][: limit or None]
        wanted = {f"Dipco/transcriptions/{split}/{s}.json" for s in sessions}
        _extract(tgz, ex, wanted)
        anns = {s: json.loads((ex / f"Dipco/transcriptions/{split}/{s}.json").read_text(encoding="utf-8")) for s in sessions}
        spks = {s: sorted({u["speaker_id"] for u in anns[s]}) for s in sessions}
        for s in sessions:
            wanted |= {f"Dipco/audio/{split}/{s}_U01.CH1.wav"} | {f"Dipco/audio/{split}/{s}_{p}.wav" for p in spks[s]}
        _extract(tgz, ex, wanted)
        adir = ex / "Dipco" / "audio" / split
        for s in sessions:
            sid = w.session_id(s)
            audio = {}
            if "farfield" in views:
                dst = w.audio_path(sid, "farfield")
                if not is_normalized(dst):
                    convert(adir / f"{s}_U01.CH1.wav", dst)
                audio["farfield"] = dst
            if "ihm-mix" in views:
                dst = w.audio_path(sid, "ihm-mix")
                if not is_normalized(dst):
                    mix([adir / f"{s}_{p}.wav" for p in spks[s]], dst)
                audio["ihm-mix"] = dst
            segs = [Segment(_t(u["start_time"]["close-talk"]), _t(u["end_time"]["close-talk"]), u["speaker_id"])
                    for u in anns[s] if _t(u["end_time"]["close-talk"]) > _t(u["start_time"]["close-talk"])]
            act = []
            for p in spks[s]:
                lab = [(x.start, x.end) for x in segs if x.speaker == p]
                ivs, _ = channel_activity(load_mono16k(adir / f"{s}_{p}.wav"), lab)
                near = merge_intervals((a - 0.5, b + 0.5) for a, b in lab)
                act += [Segment(a, b, p) for a, b in intersect(merge_intervals(ivs), near)]
            w.add_session(s, split, segs, audio=audio, alt_refs={"closetalk_activity": act})
            print(f"  [dipco] {split} {s} ok", flush=True)
    w.finalize([{"url": URL, "md5": MD5}])
