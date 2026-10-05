"""U.S. Supreme Court oral arguments from Oyez (court domain sample).

Audio: the Court's public-record argument recordings as served by Oyez (MP3 on S3). Transcripts: Oyez's
speaker-attributed transcripts, synchronised to the audio at turn level (each turn's start/stop and text-block
times). Oyez content is CC BY-NC 4.0 (<https://www.oyez.org/license>).

Reference: one segment per Oyez turn, speaker = Oyez speaker identifier (global: justices and advocates keep the
same id across cases). Oyez turns tile the timeline (each turn ends where the next begins) and overlap is never
marked, so this is a *coarse* reference; it is included to measure exactly that.
Sessions: the oral arguments of the first ``--opt n_cases=<N>`` cases (default 12) of the October Term given by
``--opt term=<year>`` (default 2022), in Oyez API order. Split: ``term<year>``. UEM: first to last turn.
"""
from __future__ import annotations

import requests

from ..annotation import Segment
from ..audio import convert, is_normalized
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download

API = "https://api.oyez.org"

META = DatasetMeta(
    name="scotus",
    title="U.S. Supreme Court oral arguments (Oyez) - court-domain sample",
    homepage="https://www.oyez.org/",
    license="Audio: public record; Oyez transcripts/sync: CC-BY-NC-4.0",
    license_url="https://www.oyez.org/license",
    citation="Oyez, a free law project by Justia and the Legal Information Institute of Cornell Law School (https://www.oyez.org).",
    source_version="api.oyez.org (fetched at prepare time)",
    description="Supreme Court oral arguments: 1 h each, 9 justices + 2-3 advocates, formal turn-taking with frequent interruptions.",
    access="Free public API, no registration.",
    reference="Oyez speaker-attributed transcript turns synchronised to the audio (no overlap).",
    default_view="default",
    views={"default": "Oyez MP3 (court recording) to mono 16 kHz"},
    gt_rating="C",
    gt_rating_reason=("Human-transcribed and speaker-attributed with stable global ids, but turn-level sync that tiles "
                      "the timeline and never marks the frequent interruptions/overlaps."),
    choices=["Sample of N cases of one term (default 12 cases of OT2022).", "Speaker ids: Oyez identifiers (global).",
             "UEM: first to last turn of each argument.", "One session per argument recording."],
    domain="court (oral arguments)",
)


def prepare(root=None, raw=None, splits=None, views=None, limit=None, term="2022", n_cases="12", **kw):
    base = raw_root(raw) / "scotus"
    w = DatasetWriter(META, root)
    cases = requests.get(f"{API}/cases", params={"per_page": 200, "filter": f"term:{term}"}, timeout=60).json()
    n_cases = int(limit or n_cases)
    done = 0
    for c in cases:
        if done >= n_cases:
            break
        detail = requests.get(c["href"], timeout=60).json()
        for oa in detail.get("oral_argument_audio") or []:
            media = requests.get(oa["href"], timeout=60).json()
            mp3 = next((m["href"] for m in media.get("media_file") or [] if m.get("mime") == "audio/mpeg"), None)
            turns = [t for s in (media.get("transcript") or {}).get("sections", []) for t in s.get("turns", [])]
            if not mp3 or not turns:
                continue
            oid = f"{term}_{c['docket_number']}_{media['id']}"
            sid = w.session_id(oid)
            if not is_normalized(w.audio_path(sid)):
                src = download(mp3, base / "audio" / f"{oid}.mp3", quiet=True)
                convert(src, w.audio_path(sid))
            segs = [Segment(float(t["start"]), float(t["stop"]), (t.get("speaker") or {}).get("identifier") or "unknown")
                    for t in turns if t.get("stop") is not None and float(t["stop"]) > float(t["start"])]
            lo, hi = min(s.start for s in segs), max(s.end for s in segs)
            w.add_session(oid, f"term{term}", segs, uem=[(lo, hi)], extra={"case": c.get("name"), "media_id": media["id"]})
            print(f"  [scotus] {oid} ok ({len(segs)} turns)", flush=True)
        done += 1
    w.finalize([{"url": API}])
