"""CHiME-6 (CC BY-SA 4.0, OpenSLR SLR150): dinner parties in real homes, 4 participants each.

Splits: official CHiME-6 dev (S02, S09) and eval (S01, S21). (CHiME-7 DASR later moved S19/S20 from train to
eval; they live in the 97 GB train tarball and are not prepared by default - pass ``--split train``.)
Views:
  * ``farfield`` (default) - channel 1 of one Kinect array per session: the array most often marked as the
    utterance ``ref`` array in the transcription JSON (the "reference array" convention of CHiME-6 track 1).
  * ``ihm-mix``  - sum of the four participants' binaural close-talk recordings (both ears averaged).
References:
  * primary: the official CHiME-6 Track 2 "alignment RTTM" (triphone GMM-HMM forced alignment of the reference
    transcripts within the manual segments; github.com/nateanl/chime6_rttm, train from chimechallenge/CHiME6_falign).
  * rttm_alt/annotation: the human utterance segments from the transcription JSON ("annotation RTTM").
UEM: CHiME-7/8 DASR convention - from the first annotated utterance to the end of the recording, because the first
minute of each session (speaker enrolment) is not annotated but was scored in CHiME-6 (a known CHiME-6 issue).
"""
from __future__ import annotations

import collections
import json
import tarfile
from pathlib import Path

import requests

from ..annotation import Segment
from ..audio import convert, is_normalized, mix
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download, extract

SLR = "https://www.openslr.org/resources/150"
RTTM_URLS = {"dev": "https://raw.githubusercontent.com/nateanl/chime6_rttm/master/dev_rttm",
             "eval": "https://raw.githubusercontent.com/nateanl/chime6_rttm/master/eval_rttm"}
FALIGN_JSON = "https://raw.githubusercontent.com/chimechallenge/CHiME6_falign/main/{split}/{session}.json"
SESSIONS = {"dev": ["S02", "S09"], "eval": ["S01", "S21"],
            "train": ["S03", "S04", "S05", "S06", "S07", "S08", "S12", "S13", "S16", "S17", "S18", "S19", "S20",
                      "S22", "S23", "S24"]}

META = DatasetMeta(
    name="chime6",
    title="CHiME-6 (CHiME-5 dinner party corpus, synchronized)",
    homepage="https://www.chimechallenge.org/datasets/chime6",
    license="CC-BY-SA-4.0",
    license_url="https://creativecommons.org/licenses/by-sa/4.0/",
    annotation_redistributable=True,
    citation=("J. Barker et al., 'The fifth CHiME speech separation and recognition challenge', Interspeech 2018; "
              "S. Watanabe et al., 'CHiME-6 Challenge: Tackling multispeaker speech recognition for unsegmented recordings', 2020."),
    source_version="OpenSLR SLR150 (CHiME6_dev/eval.tar.gz, CHiME6_transcriptions.tar.gz); nateanl/chime6_rttm",
    description="20 real dinner parties in homes (kitchen, dining, living room), 4 participants, ~2.5 h each, 6 Kinect arrays.",
    access="Free download from OpenSLR (dev 11 GB, eval 12 GB, train 97 GB), no registration.",
    reference="Official Track 2 forced-alignment RTTM (primary); manual utterance segments (alternative).",
    default_view="farfield",
    views={"farfield": "Channel 1 of the session's most frequent reference Kinect array",
           "ihm-mix": "Sum of the 4 participants' binaural close-talk microphones"},
    gt_rating="A-",
    gt_rating_reason=("Every participant wore a binaural mic and was transcribed manually; the official diarization "
                      "reference is forced-aligned (pauses removed), overlap fully covered. Highly overlapped, "
                      "far-field, very challenging. Enrolment minute not annotated (handled by UEM)."),
    choices=["Splits: CHiME-6 dev / eval.", "Speaker ids: CHiME participant ids (P01-P32), global.",
             "UEM: first annotated utterance to end of recording (CHiME-7 convention).",
             "farfield view: CH1 of the session's most frequent 'ref' array."],
    domain="dinner party (home, far-field)",
)


def _t(s: str) -> float:
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def _extract_members(tgz: Path, dest: Path, wanted: set[str]) -> None:
    missing = {m for m in wanted if not (dest / m).exists()}
    if not missing:
        return
    with tarfile.open(tgz, "r|gz") as t:  # streaming: one pass over the archive
        for m in t:
            if m.name in missing:
                t.extract(m, dest)
                missing.discard(m.name)
                if not missing:
                    break


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "chime6"
    views = views or list(META.views)
    trans = download(f"{SLR}/CHiME6_transcriptions.tar.gz", base / "CHiME6_transcriptions.tar.gz")
    tdir = base / "trans"
    if not any(tdir.rglob("*.json")):
        try:
            extract(trans, tdir)
        except Exception:
            pass  # the archive has trailing garbage; members are extracted before the error
    w = DatasetWriter(META, root)
    for split in splits or ["dev", "eval"]:
        sessions = SESSIONS[split][: limit or None]
        tgz = download(f"{SLR}/CHiME6_{split}.tar.gz", base / f"CHiME6_{split}.tar.gz")
        if split in RTTM_URLS:
            rttm_lines = requests.get(RTTM_URLS[split], timeout=60).text.splitlines()
        else:
            rttm_lines = []
        anns = {s: json.loads(next(tdir.rglob(f"{s}.json")).read_text(encoding="utf-8")) for s in sessions}
        refs = {s: collections.Counter(u.get("ref") for u in anns[s]).most_common(1)[0][0] for s in sessions}
        speakers = {s: sorted({u["speaker"] for u in anns[s]}) for s in sessions}
        wanted = set()
        for s in sessions:
            wanted.add(f"CHiME6_{split}/CHiME6/audio/{split}/{s}_{refs[s]}.CH1.wav")
            wanted |= {f"CHiME6_{split}/CHiME6/audio/{split}/{s}_{p}.wav" for p in speakers[s]}
        _extract_members(tgz, base / "extracted", wanted)
        adir = base / "extracted" / f"CHiME6_{split}" / "CHiME6" / "audio" / split
        for s in sessions:
            sid = w.session_id(s)
            audio = {}
            if "farfield" in views:
                dst = w.audio_path(sid, "farfield")
                if not is_normalized(dst):
                    convert(adir / f"{s}_{refs[s]}.CH1.wav", dst)
                audio["farfield"] = dst
            if "ihm-mix" in views:
                dst = w.audio_path(sid, "ihm-mix")
                if not is_normalized(dst):
                    mix([adir / f"{s}_{p}.wav" for p in speakers[s]], dst)
                audio["ihm-mix"] = dst
            manual = [Segment(_t(u["start_time"]), _t(u["end_time"]), u["speaker"]) for u in anns[s]
                      if _t(u["end_time"]) > _t(u["start_time"])]
            if rttm_lines:
                aligned = []
                for line in rttm_lines:
                    p = line.split()
                    if len(p) > 7 and p[0] == "SPEAKER" and p[1].split("_")[0] == s:
                        aligned.append(Segment(float(p[3]), float(p[3]) + float(p[4]), p[7]))
            else:
                fj = json.loads(requests.get(FALIGN_JSON.format(split=split, session=s), timeout=60).text)
                aligned = [Segment(_t(u["start_time"]) if isinstance(u["start_time"], str) else float(u["start_time"]),
                                   _t(u["end_time"]) if isinstance(u["end_time"], str) else float(u["end_time"]),
                                   u["speaker"]) for u in fj]
            first = min(x.start for x in manual)
            dur = min(__import__("soundfile").info(str(p)).duration for p in audio.values())
            words = []
            w.add_session(s, split, aligned, audio=audio, uem=[(first, dur)], alt_refs={"annotation": manual},
                          extra={"farfield_array": refs[s]})
            print(f"  [chime6] {split} {s} ok (array {refs[s]})", flush=True)
    w.finalize([{"url": f"{SLR}/"}, {"url": "https://github.com/nateanl/chime6_rttm"}])
