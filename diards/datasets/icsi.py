"""ICSI Meeting Corpus (CC BY 4.0): 75 real research-group meetings, ~72 h, 3-10 participants.

Audio from the AMI/ICSI mirror at Edinburgh:
  * ``ihm-mix`` (default) - ICSIsignals/NXT/<meeting>.interaction.wav (headset mix)
  * ``sdm``               - ICSIsignals/SPH/<meeting>/chan6.sph (a table-top PZM microphone, as in Lhotse/Kaldi)
Annotations from ICSI_core_NXT.zip (v1.0, 2016):
  * primary: manual transcriber segments (Segments/*.segs.xml) that contain at least one word; segments made
    only of non-speech events (mike noise, breath, laughter without words) are dropped.
  * rttm_alt/words: word timings (forced alignment shipped with the corpus), same-speaker adjacent words merged
    (no pause bridging), words without timing skipped.
Splits: the Kaldi/Lhotse partition (train 70 / dev 2 / test 3 meetings).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ..annotation import Segment, merge_intervals
from ..audio import convert, is_normalized
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download, extract

BASE_URL = "https://groups.inf.ed.ac.uk/ami"
NXT_ZIP = f"{BASE_URL}/ICSICorpusAnnotations/ICSI_core_NXT.zip"
PARTITIONS = {
    "train": ["Bdb001", "Bed002", "Bed003", "Bed004", "Bed005", "Bed006", "Bed008", "Bed009", "Bed010", "Bed011",
              "Bed012", "Bed013", "Bed014", "Bed015", "Bed016", "Bed017", "Bmr001", "Bmr002", "Bmr003", "Bmr005",
              "Bmr006", "Bmr007", "Bmr008", "Bmr009", "Bmr010", "Bmr011", "Bmr012", "Bmr014", "Bmr015", "Bmr016",
              "Bmr019", "Bmr020", "Bmr022", "Bmr023", "Bmr024", "Bmr025", "Bmr026", "Bmr027", "Bmr028", "Bmr029",
              "Bmr030", "Bmr031", "Bns002", "Bns003", "Bro003", "Bro004", "Bro005", "Bro007", "Bro008", "Bro010",
              "Bro011", "Bro012", "Bro013", "Bro014", "Bro015", "Bro016", "Bro017", "Bro018", "Bro019", "Bro022",
              "Bro023", "Bro024", "Bro025", "Bro026", "Bro027", "Bro028", "Bsr001", "Btr001", "Btr002", "Buw001"],
    "dev": ["Bmr021", "Bns001"],
    "test": ["Bmr013", "Bmr018", "Bro021"],
}

META = DatasetMeta(
    name="icsi",
    title="ICSI Meeting Corpus",
    homepage="https://groups.inf.ed.ac.uk/ami/icsi/",
    license="CC-BY-4.0",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    annotation_redistributable=True,
    citation="A. Janin et al., 'The ICSI Meeting Corpus', ICASSP 2003.",
    source_version="ICSI core NXT annotations v1.0 (2016-07-22)",
    description="Natural research-group meetings at ICSI Berkeley (2000-2002), 3-10 participants, many non-native speakers.",
    access="Free download, no registration.",
    reference="Manual transcriber segments (MRT) per participant; forced-aligned word times as alternative.",
    default_view="ihm-mix",
    views={"ihm-mix": "Headset mix (<meeting>.interaction.wav)",
           "sdm": "Table-top microphone channel 6 (chan6.sph)"},
    gt_rating="B",
    gt_rating_reason=("All participants on headsets and fully transcribed (overlap and backchannels included); "
                      "segment boundaries are hand-placed but transcription-oriented (padding, merged pauses)."),
    choices=["Splits: Kaldi/Lhotse ICSI partition.", "Speaker ids: ICSI participant ids (e.g. me013), global.",
             "UEM: whole meeting.", "Segments without any word (noise/breath/laugh only) are excluded."],
    domain="meetings",
)


def _words_index(path: Path) -> tuple[list[str], dict[str, ET.Element]]:
    order, by_id = [], {}
    if not path.exists():
        return order, by_id
    for el in ET.parse(path).getroot():
        i = el.get("{http://nite.sourceforge.net/}id")
        order.append(i)
        by_id[i] = el
    return order, by_id


_HREF = re.compile(r"#id\(([^)]+)\)(?:\.\.id\(([^)]+)\))?")


def _parse_meeting(nxt: Path, meeting: str):
    segs, word_segs, words = [], [], []
    for segfile in sorted((nxt / "Segments").glob(f"{meeting}.*.segs.xml")):
        letter = segfile.name.split(".")[1]
        order, by_id = _words_index(nxt / "Words" / f"{meeting}.{letter}.words.xml")
        pos = {i: k for k, i in enumerate(order)}
        spk_words = []
        for seg in ET.parse(segfile).getroot():
            spk = seg.get("participant")
            st, et = seg.get("starttime"), seg.get("endtime")
            has_word = False
            for child in seg:
                m = _HREF.search(child.get("href", ""))
                if not m:
                    continue
                a, b = m.group(1), m.group(2) or m.group(1)
                if a not in pos or b not in pos:
                    continue
                for wid in order[pos[a]: pos[b] + 1]:
                    el = by_id[wid]
                    if el.tag.split("}")[-1] == "w":
                        has_word = True
                        ws, we = el.get("starttime"), el.get("endtime")
                        if ws and we and float(we) > float(ws):
                            spk_words.append((float(ws), float(we)))
                            words.append({"start": float(ws), "end": float(we), "speaker": spk,
                                          "word": (el.text or "").strip()})
            if has_word and st and et and float(et) > float(st):
                segs.append(Segment(float(st), float(et), spk))
        if spk_words and segs:
            spk = segs[-1].speaker
            word_segs += [Segment(a, b, spk) for a, b in merge_intervals(spk_words)]
    return segs, word_segs, words


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "icsi"
    download(NXT_ZIP, base / "ICSI_core_NXT.zip")
    extract(base / "ICSI_core_NXT.zip", base / "nxt")
    nxt = base / "nxt" / "ICSI"
    views = views or list(META.views)
    w = DatasetWriter(META, root)
    for split in splits or ["test", "dev", "train"]:
        for meeting in PARTITIONS[split][: limit or None]:
            sid = w.session_id(meeting)
            audio = {}
            if "ihm-mix" in views:
                dst = w.audio_path(sid, "ihm-mix")
                if not is_normalized(dst):
                    src = download(f"{BASE_URL}/ICSIsignals/NXT/{meeting}.interaction.wav",
                                   base / "audio" / f"{meeting}.interaction.wav", quiet=True)
                    convert(src, dst)
                audio["ihm-mix"] = dst
            if "sdm" in views:
                dst = w.audio_path(sid, "sdm")
                try:
                    if not is_normalized(dst):
                        src = download(f"{BASE_URL}/ICSIsignals/SPH/{meeting}/chan6.sph",
                                       base / "audio" / f"{meeting}.chan6.sph", quiet=True)
                        convert(src, dst)
                    audio["sdm"] = dst
                except Exception as exc:
                    print(f"  [icsi] {meeting}: sdm unavailable ({exc})")
            segs, word_segs, words = _parse_meeting(nxt, meeting)
            w.add_session(meeting, split, segs, audio=audio, words=words, alt_refs={"words": word_segs})
            print(f"  [icsi] {split} {meeting} ok", flush=True)
    w.finalize([{"url": NXT_ZIP}, {"url": f"{BASE_URL}/ICSIsignals/"}])
