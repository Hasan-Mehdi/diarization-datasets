"""Santa Barbara Corpus of Spoken American English (CC BY-ND 3.0 US), OpenSLR SLR155.

60 naturally occurring recordings (~20 min each, ~20 h) of everyday American English: face-to-face conversation,
phone calls, classroom talk, sermons, story-telling, meetings. Transcripts (CHAT version) time-stamp every
intonation unit (IU) with a millisecond bullet ``start_end``.

Reference: one segment per IU line, speaker = the CHAT participant code. Excluded: the ``ENV`` (environment)
tier and any other non-human tier, and IUs without any lexical word (only breaths ``&=in``, laughter, pauses,
vocal noises). IU bullets in SBCSAE tile the timeline (an IU starts where the previous one ended), so pauses
before an IU are counted inside it: boundaries are loose by construction (see the dataset card).
Audio: the WAV files (22.05 kHz stereo) downmixed to mono 16 kHz. Split: ``all``.
UEM: from the first to the last transcribed intonation unit: several recordings have untranscribed speech at
the start or end (276 s in total, e.g. the last 28 s of SBC015), which would otherwise count as false alarms.
License: CC BY-ND 3.0 US -> derived RTTMs must not be redistributed; they are only written to your data root.
"""
from __future__ import annotations

import re
import tarfile
from pathlib import Path

from ..annotation import Segment
from ..audio import convert, is_normalized
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download

MIRRORS = ["https://openslr.elda.org/resources/155/SBCSAE.tar.gz", "https://www.openslr.org/resources/155/SBCSAE.tar.gz"]
BULLET = re.compile(r"\x15?(\d+)_(\d+)\x15?\s*$")
NON_HUMAN = {"ENV", "ENVI", "MANY", "X", "XX", "UNK"}
WORD = re.compile(r"[A-Za-z]")

META = DatasetMeta(
    name="sbcsae",
    title="Santa Barbara Corpus of Spoken American English",
    homepage="https://www.linguistics.ucsb.edu/research/santa-barbara-corpus-spoken-american-english",
    license="CC-BY-ND-3.0-US",
    license_url="https://creativecommons.org/licenses/by-nd/3.0/us/",
    annotation_redistributable=False,
    citation="J. W. Du Bois, W. L. Chafe, C. Meyer, S. A. Thompson, R. Englebretson, N. Martey (2000-2005), Santa Barbara Corpus of Spoken American English, Parts 1-4.",
    source_version="OpenSLR SLR155 SBCSAE.tar.gz (CHAT transcripts + WAV)",
    description="Naturally occurring everyday interaction across the US: conversation, phone calls, lectures, meetings, story-telling.",
    access="Free download from OpenSLR (6.2 GB), no registration.",
    reference="Linguist transcription, intonation units time-stamped (ms bullets), overlap bracketed.",
    default_view="default",
    views={"default": "Original recording (22.05 kHz stereo) downmixed to mono 16 kHz"},
    gt_rating="B-",
    gt_rating_reason=("Careful human transcription of every participant with overlap marked and IU-level timing, "
                      "but IU bullets tile the timeline (pauses inside units) and recordings vary widely in quality."),
    choices=["Segments: one per intonation unit with lexical content; ENV and non-word IUs dropped.",
             "Speaker ids: <recording>_<CHAT code>.", "Split: all.",
             "UEM: first to last transcribed IU (untranscribed heads/tails excluded).",
             "RTTMs are NOT redistributable (CC BY-ND); stats only are published."],
    domain="everyday conversation (mixed situations)",
)


def parse_cha(path: Path) -> list[tuple[float, float, str, str]]:
    """(start, end, speaker code, text) per bulleted line of a CHAT file."""
    out = []
    spk = None
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("*"):
            m = re.match(r"\*([^:]+):\s*(.*)$", raw)
            if not m:
                continue
            spk, text = m.group(1), m.group(2)
        elif raw.startswith("\t") and spk is not None:
            text = raw.strip()
        else:
            if raw.startswith("@") or raw.startswith("%"):
                spk = None if raw.startswith("@") else spk
            continue
        b = BULLET.search(text)
        if not b:
            continue
        a, e = int(b.group(1)) / 1000.0, int(b.group(2)) / 1000.0
        out.append((a, e, spk, text[: b.start()].strip()))
    return out


def has_words(text: str) -> bool:
    t = re.sub(r"&=\S+|&\{[^ ]*|&\}[^ ]*|\(\.+\)|\(\(.*?\)\)|[⌈⌉⌊⌋]|\+[./!?]+|[\[\]<>@%]", " ", text)
    return any(WORD.search(tok) and not tok.startswith("&") for tok in t.split())


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "sbcsae"
    tgz = base / "SBCSAE.tar.gz"
    if not tgz.exists():
        for url in MIRRORS:
            try:
                download(url, tgz)
                break
            except Exception as exc:
                print(f"  [sbcsae] {url} failed: {exc}")
    ex = base / "ex"
    if not (ex / "WAV").exists():
        with tarfile.open(tgz) as t:
            t.extractall(ex, members=[m for m in t.getmembers() if m.name.startswith(("CHAT/", "WAV/", "docs/"))])
    w = DatasetWriter(META, root)
    chas = sorted((ex / "CHAT").glob("SBC*.cha"))[: limit or None]
    for cha in chas:
        rec = cha.stem
        wav = ex / "WAV" / f"{rec}.wav"
        if not wav.exists():
            print(f"  [sbcsae] {rec}: no WAV")
            continue
        sid = w.session_id(rec)
        if not is_normalized(w.audio_path(sid)):
            convert(wav, w.audio_path(sid))
        segs = [Segment(a, e, f"{rec}_{spk}") for a, e, spk, text in parse_cha(cha)
                if spk not in NON_HUMAN and e > a and has_words(text)]
        lo, hi = min(g.start for g in segs), max(g.end for g in segs)
        w.add_session(rec, "all", segs, uem=[(lo, hi)])
        print(f"  [sbcsae] {rec} ok ({len(segs)} IUs)", flush=True)
    w.finalize([{"url": MIRRORS[0]}])
