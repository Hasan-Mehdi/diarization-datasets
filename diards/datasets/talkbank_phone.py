"""CallHome English and CallFriend English telephone conversations, as converted by TalkBank on the Hugging Face Hub.

* ``callhome_eng``  <- ``talkbank/callhome`` config ``eng`` (gated: click "Agree and access" on the HF page;
  the form asks for company and country). CC BY-NC-SA 4.0 per the HF card.
* ``callfriend_eng`` <- ``talkbank/callfriend`` configs ``eng-n`` (North American) and ``eng-s`` (Southern US).
  Not gated; the HF card states no license, the TalkBank ground rules (cite, non-commercial research) apply.

The HF conversion (made with the `diarizers` scripts) keeps only the transcribed part of each call and gives
per-turn timestamps from the TalkBank CHAT media bullets. Original file names are not preserved in the parquet,
so sessions are named ``<config>_<row index>``.
"""
from __future__ import annotations

from types import SimpleNamespace

from ..annotation import Segment
from ..audio import is_normalized, write_array
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ._hf_audio import decode_audio, iter_parquet_rows, list_repo_files

COMMON_CHOICES = [
    "One split ('data') as published on the Hub; no official train/test split in the TalkBank release.",
    "Session ids: <config>_<row index> (the parquet does not keep original file names).",
    "Speaker ids: <session>_<CHAT speaker code>.",
    "UEM: whole (already trimmed) audio.",
]

CALLHOME = DatasetMeta(
    name="callhome_eng",
    title="CallHome American English (TalkBank CABank version)",
    homepage="https://ca.talkbank.org/access/CallHome/eng.html",
    license="CC-BY-NC-SA-4.0",
    license_url="https://creativecommons.org/licenses/by-nc-sa/4.0/",
    citation=("Canavan, Graff & Zipperlen (1997) CALLHOME American English Speech LDC97S42; "
              "Linguistic Data Consortium (2008) CABank English CallHome Corpus, TalkBank, doi:10.21415/T5KP54."),
    source_version="huggingface.co/datasets/talkbank/callhome (config eng)",
    description="Telephone calls between family members/friends (mostly US to overseas), transcribed 5-10 min excerpts.",
    access="Free, gated on Hugging Face (click-through form asking company + country).",
    reference="LDC transcripts re-formatted by TalkBank (CHAT), per-turn time bullets.",
    default_view="default",
    views={"default": "Telephone audio (both channels summed), 8 kHz source upsampled to 16 kHz"},
    gt_rating="C+",
    gt_rating_reason="Human transcription with turn-level bullets; see dataset card for measured boundary quality.",
    choices=COMMON_CHOICES,
    domain="telephone (2+ speakers)",
)

CALLFRIEND = DatasetMeta(
    name="callfriend_eng",
    title="CallFriend English (North American + Southern US, TalkBank CABank version)",
    homepage="https://ca.talkbank.org/access/CallFriend/",
    license="TalkBank ground rules (research, cite); HF card states no license",
    license_url="https://talkbank.org/share/rules.html",
    citation="Canavan & Zipperlen (1996) CALLFRIEND American English LDC96S46/LDC96S47; TalkBank CABank CallFriend.",
    source_version="huggingface.co/datasets/talkbank/callfriend (configs eng-n, eng-s)",
    description="Telephone calls between friends/family within North America, 40 calls with TalkBank transcripts.",
    access="Free on Hugging Face (not gated).",
    reference="TalkBank CHAT transcripts with per-turn time bullets.",
    default_view="default",
    views={"default": "Telephone audio (channels summed), 16 kHz"},
    gt_rating="C",
    gt_rating_reason="Human transcription with turn-level bullets; see dataset card for measured boundary quality.",
    choices=COMMON_CHOICES,
    domain="telephone (2+ speakers)",
)

SPECS = {
    "callhome_eng": (CALLHOME, "talkbank/callhome", ["eng"]),
    "callfriend_eng": (CALLFRIEND, "talkbank/callfriend", ["eng-n", "eng-s"]),
}


def _prepare(name, root=None, raw=None, splits=None, views=None, limit=None, **kw):
    meta, repo, configs = SPECS[name]
    w = DatasetWriter(meta, root)
    base = raw_root(raw) / "talkbank" / name
    for cfg in configs:
        files = list_repo_files(repo, f"{cfg}/")
        n = 0
        for row in iter_parquet_rows(repo, files, base):
            oid = f"{cfg}_{n:03d}"
            n += 1
            sid = w.session_id(oid)
            if not is_normalized(w.audio_path(sid)):
                x, sr = decode_audio(row["audio"])
                write_array(w.audio_path(sid), x, sr)
            segs = [Segment(float(a), float(b), f"{oid}_{s}")
                    for a, b, s in zip(row["timestamps_start"], row["timestamps_end"], row["speakers"])]
            w.add_session(oid, "data", segs, extra={"config": cfg})
            if limit and n >= limit:
                break
        print(f"  [{name}] {cfg}: {n} sessions", flush=True)
    w.finalize([{"url": f"https://huggingface.co/datasets/{repo}"}])


def get_recipe(name):
    return SimpleNamespace(META=SPECS[name][0], prepare=lambda **kw: _prepare(name, **kw))
