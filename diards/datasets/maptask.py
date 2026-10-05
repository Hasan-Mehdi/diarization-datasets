"""HCRC Map Task Corpus: 128 task-oriented two-person dialogues (Scottish English), ~15 h.

Annotations: NXT release v2.1 (the download page states CC BY 4.0; the 00LICENSE file inside the zip and the
audio directory carry CC BY-NC-SA 2.5 - treat the stricter one as binding). Audio: the official stereo mixes of the
two speakers' close-talk channels (20 kHz) from groups.inf.ed.ac.uk/maptask/signals/dialogues.
Reference: timed units (word-level start/end times for each speaker, with silences and noises time-marked
separately); same-speaker words separated by less than 0.2 s are merged into one segment (DIHARD-style pause rule).
Speaker ids: the corpus' global participant ids (e.g. q1eta1), so a speaker keeps the same id across dialogues.
Split: a single split ``all`` (the corpus has no official train/test split).
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

NXT = "https://groups.inf.ed.ac.uk/maptask/hcrcmaptask.nxtformatv2-1.zip"
AUDIO = "https://groups.inf.ed.ac.uk/maptask/signals/dialogues/{id}.mix.wav"

META = DatasetMeta(
    name="maptask",
    title="HCRC Map Task Corpus",
    homepage="https://groups.inf.ed.ac.uk/maptask/",
    license="CC-BY-NC-SA-2.5 (audio + NXT zip); download page states CC BY 4.0 for annotations v2.1",
    license_url="https://groups.inf.ed.ac.uk/maptask/maptasknxt.html",
    citation="A. Anderson et al., 'The HCRC Map Task Corpus', Language and Speech 34(4), 1991.",
    source_version="NXT annotations v2.1 (2011-02-10); signals/dialogues *.mix.wav",
    description="Two-person route-giving dialogues (giver/follower) recorded in a studio with close-talk mics, Glasgow students.",
    access="Free download, no registration.",
    reference="Word-level timed units per speaker (silence and noise also time-marked).",
    default_view="default",
    views={"default": "Official stereo mix of the two close-talk channels, downmixed to mono 16 kHz"},
    gt_rating="A",
    gt_rating_reason=("Each speaker on a separate close-talk channel with word-level timings, silences explicitly "
                      "marked, overlap naturally represented; verified: 0.6% of reference speech in silence, no time "
                      "shifts, Nemotron DER 1.9% at collar 0.25 s. Task dialogue, studio audio."),
    choices=["Pause rule: same-speaker words < 0.2 s apart merged.", "Speaker ids: global participant ids.",
             "UEM: whole recording.", "Single split 'all'."],
    domain="two-person task dialogue (close-talk)",
)


def _speakers(data: Path) -> dict[str, dict[str, str]]:
    root = ET.parse(data / "corpus-resources" / "maptask-corpus.xml").getroot()
    out = {}
    for conv in root.iter("conv"):
        roles = {}
        for p in conv:
            m = re.search(r"#id\(([^)]+)\)", p.get("href", ""))
            if m:
                roles[p.get("role")] = m.group(1)
        out[conv.get("id")] = roles
    return out


def prepare(root=None, raw=None, splits=None, views=None, limit=None, pause=0.2, **kw):
    base = raw_root(raw) / "maptask"
    download(NXT, base / "hcrcmaptask.nxtformatv2-1.zip")
    extract(base / "hcrcmaptask.nxtformatv2-1.zip", base / "nxt")
    data = base / "nxt" / "maptaskv2-1" / "Data"
    spk = _speakers(data)
    dialogues = sorted(spk)[: limit or None]
    w = DatasetWriter(META, root)
    for d in dialogues:
        sid = w.session_id(d)
        dst = w.audio_path(sid)
        if not is_normalized(dst):
            try:
                src = download(AUDIO.format(id=d), base / "audio" / f"{d}.mix.wav", quiet=True)
            except Exception as exc:
                print(f"  [maptask] {d}: no audio ({exc})")
                continue
            convert(src, dst)
        segs, words = [], []
        for role in ("g", "f"):
            f = data / "timed-units" / f"{d}.{role}.timed-units.xml"
            if not f.exists():
                continue
            who = spk[d].get(role, f"{d}_{role}")
            ivs = []
            for el in ET.parse(f).getroot():
                if el.tag == "tu":
                    a, b = float(el.get("start")), float(el.get("end"))
                    if b > a:
                        ivs.append((a, b))
                        words.append({"start": a, "end": b, "speaker": who, "word": (el.text or "").strip()})
            segs += [Segment(a, b, who) for a, b in merge_intervals(ivs, gap=pause)]
        w.add_session(d, "all", segs, words=words, extra={"roles": spk[d]})
        print(f"  [maptask] {d} ok", flush=True)
    w.finalize([{"url": NXT}, {"url": AUDIO.format(id="<id>")}])
