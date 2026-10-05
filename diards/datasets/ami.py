"""AMI Meeting Corpus (CC BY 4.0).

Views
  * ``sdm``      - single distant microphone (Array1-01), the standard far-field condition.
  * ``ihm-mix``  - the official Mix-Headset recording (sum of the close-talk headsets).

References (all share the Full-corpus-ASR partition: 136 train / 18 dev / 16 test meetings)
  * primary ``rttm/``: forced alignment of the manual transcripts with MFA v3 (nttcslab-sp/diar-forced-alignment,
    Horiguchi et al., ASRU 2025). Tightest boundaries; used by the NVIDIA Nemotron 3 Diarization model card.
  * ``rttm_alt/only_words``: BUT AMI-diarization-setup, words from the manual annotation v1.6.2 (word timings
    there come from the original AMI forced alignment; pauses inside long words are absorbed).
  * ``rttm_alt/word_and_vocalsounds``: same plus vocal sounds (laughs, coughs...), inconsistently marked.
  * ``rttm_alt/segments``: the transcriber segment boundaries from the manual annotation (loose; ASR oriented).
Words: from the manual annotation v1.6.2 ``words/*.words.xml`` (speaker = global AMI participant id).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ..annotation import Segment, read_rttm_single
from ..audio import convert
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download, extract, git_clone

AMI_MIRROR = "https://groups.inf.ed.ac.uk/ami/AMICorpusMirror/amicorpus"
MANUAL_URL = "https://groups.inf.ed.ac.uk/ami/AMICorpusAnnotations/ami_public_manual_1.6.2.zip"
BUT_REPO = "https://github.com/BUTSpeechFIT/AMI-diarization-setup.git"
FA_REPO = "https://github.com/nttcslab-sp/diar-forced-alignment.git"
VIEW_FILES = {"sdm": "Array1-01", "ihm-mix": "Mix-Headset"}

META = DatasetMeta(
    name="ami",
    title="AMI Meeting Corpus",
    homepage="https://groups.inf.ed.ac.uk/ami/corpus/",
    license="CC-BY-4.0",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    annotation_redistributable=True,
    citation=("J. Carletta et al., 'The AMI Meeting Corpus: A Pre-announcement', MLMI 2005. "
              "Forced-aligned labels: S. Horiguchi et al., 'Can We Really Repurpose Multi-Speaker ASR Corpus for "
              "Speaker Diarization?', ASRU 2025. BUT setup: F. Landini et al., CSL 2022."),
    source_version="AMI manual annotations 1.6.2; BUT AMI-diarization-setup (git HEAD); nttcslab diar-forced-alignment (git HEAD)",
    description="100 h of English meetings (mostly scenario-based design meetings), 3-5 participants, recorded in 3 instrumented rooms.",
    access="Free download, no registration.",
    reference="Forced alignment (MFA v3) of the manual transcripts (primary); manual-annotation-derived alternatives in rttm_alt/.",
    default_view="sdm",
    views={"sdm": "Single distant microphone (Array1-01, 16 kHz)",
           "ihm-mix": "Official Mix-Headset (sum of individual headset microphones)"},
    gt_rating="A-",
    gt_rating_reason=("Manual word-level transcripts of every participant (close-talk), so all speech including "
                      "overlap and backchannels is covered; boundaries come from forced alignment (tight with MFA, "
                      "looser in the original release). Known timing problems in EN2002a, EN2002c, EN2003a, TS3009c."),
    choices=[
        "Splits: Full-corpus-ASR partition as listed by BUT AMI-diarization-setup (train/dev/test).",
        "Speaker ids: AMI global participant ids (e.g. MEE071) for every reference variant; forced-alignment labels "
        "(<meeting>.<channel letter>) are mapped through corpusResources/meetings.xml.",
        "UEM: whole recording (as in the BUT setup).",
        "Same-speaker overlapping/adjacent segments merged; no other smoothing.",
    ],
    domain="meetings",
)


def _raw(raw) -> Path:
    return raw_root(raw) / "ami"


def fetch_annotations(raw=None) -> Path:
    base = _raw(raw)
    download(MANUAL_URL, base / "ami_public_manual_1.6.2.zip")
    extract(base / "ami_public_manual_1.6.2.zip", base / "manual")
    git_clone(BUT_REPO, base / "AMI-diarization-setup")
    git_clone(FA_REPO, base / "diar-forced-alignment")
    return base


def split_lists(base: Path) -> dict[str, list[str]]:
    out = {}
    for split in ("train", "dev", "test"):
        lst = base / "AMI-diarization-setup" / "lists" / f"{split}.meetings.txt"
        out[split] = [x.strip() for x in lst.read_text().split() if x.strip()]
    return out


def agent_map(base: Path) -> dict[str, dict[str, str]]:
    """meeting -> {channel letter: global speaker id}"""
    tree = ET.parse(base / "manual" / "corpusResources" / "meetings.xml")
    out: dict[str, dict[str, str]] = {}
    for m in tree.getroot().iter("meeting"):
        obs = m.get("observation")
        out[obs] = {s.get("nxt_agent"): s.get("global_name") for s in m.iter("speaker")}
    return out


def _words(base: Path, meeting: str, agents: dict[str, str], vocal: bool = False) -> list[dict]:
    words = []
    for letter, spk in agents.items():
        f = base / "manual" / "words" / f"{meeting}.{letter}.words.xml"
        if not f.exists():
            continue
        for el in ET.parse(f).getroot():
            tag = el.tag.split("}")[-1]
            st, et = el.get("starttime"), el.get("endtime")
            if st is None or et is None:
                continue
            if tag == "w" and el.get("punc") != "true":
                words.append({"start": float(st), "end": float(et), "speaker": spk, "word": (el.text or "").strip()})
            elif vocal and tag == "vocalsound":
                words.append({"start": float(st), "end": float(et), "speaker": spk,
                              "word": f"<{el.get('type', 'vocalsound')}>"})
    return [w for w in words if w["end"] > w["start"]]


def _segments_xml(base: Path, meeting: str, agents: dict[str, str]) -> list[Segment]:
    segs = []
    for letter, spk in agents.items():
        f = base / "manual" / "segments" / f"{meeting}.{letter}.segments.xml"
        if not f.exists():
            continue
        for el in ET.parse(f).getroot():
            st, et = el.get("transcriber_start"), el.get("transcriber_end")
            if st and et and float(et) > float(st):
                segs.append(Segment(float(st), float(et), spk))
    return segs


def _relabel(segs: list[Segment], meeting: str, agents: dict[str, str]) -> list[Segment]:
    out = []
    for s in segs:
        m = re.match(rf"{re.escape(meeting)}\.([A-Z])$", s.speaker)
        spk = agents.get(m.group(1), s.speaker) if m else s.speaker
        out.append(Segment(s.start, s.end, spk))
    return out


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = fetch_annotations(raw)
    lists = split_lists(base)
    agents = agent_map(base)
    views = views or list(META.views)
    splits = splits or ["test", "dev", "train"]
    w = DatasetWriter(META, root)
    sources = [{"url": MANUAL_URL}, {"url": BUT_REPO}, {"url": FA_REPO}, {"url": AMI_MIRROR}]
    for split in splits:
        meetings = lists[split][: limit or None]
        for meeting in meetings:
            sid = w.session_id(meeting)
            audio = {}
            for view in views:
                src = base / "audio" / f"{meeting}.{VIEW_FILES[view]}.wav"
                try:
                    download(f"{AMI_MIRROR}/{meeting}/audio/{meeting}.{VIEW_FILES[view]}.wav", src, quiet=True)
                except Exception as exc:  # a few meetings lack some streams
                    print(f"  [ami] {meeting} {view}: download failed ({exc}); skipping view")
                    continue
                audio[view] = convert(src, w.audio_path(sid, view))
            if not audio:
                continue
            ag = agents[meeting]
            fa_file = base / "diar-forced-alignment" / "AMI" / split / f"{meeting}.rttm"
            ow = base / "AMI-diarization-setup" / "only_words" / "rttms" / split / f"{meeting}.rttm"
            wv = base / "AMI-diarization-setup" / "word_and_vocalsounds" / "rttms" / split / f"{meeting}.rttm"
            alt = {"only_words": read_rttm_single(ow), "word_and_vocalsounds": read_rttm_single(wv),
                   "segments": _segments_xml(base, meeting, ag)}
            if fa_file.exists():
                primary = _relabel(read_rttm_single(fa_file), meeting, ag)
                ref_name = "forced_alignment"
            else:  # fall back to the BUT reference if a meeting has no forced alignment
                primary = alt["only_words"]
                ref_name = "only_words (no forced alignment available)"
            w.add_session(meeting, split, primary, audio=audio, words=_words(base, meeting, ag), alt_refs=alt,
                          extra={"reference": ref_name})
            print(f"  [ami] {split} {meeting} ok", flush=True)
    w.finalize(sources)
