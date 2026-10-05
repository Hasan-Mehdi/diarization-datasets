"""NOTSOFAR-1 recorded meetings (Microsoft, CC BY 4.0), from the Hugging Face mirror ``microsoft/NOTSOFAR``.

Splits / versions (official names):
  * eval  <- eval_set/240825.1_eval_full_with_GT (129 meetings; held out from Nemotron 3 Diarization training)
  * dev   <- dev_set/240825.1_dev1
  * train <- train_set/240825.1_train
Views:
  * ``sc``      - the first single-channel far-field device listed in the meeting's devices.json
  * ``ihm-mix`` - sum of all close-talk (CT_*) recordings of the meeting
References:
  * primary: official utterance segments (gt_transcription.json start_time/end_time, human transcription with a
    multi-stage, machine-bias-mitigating annotation process)
  * rttm_alt/words_gap0.2: official word timings, same-speaker words merged across pauses < 0.2 s
  * rttm_alt/fastmss_mfa: Montreal-Forced-Aligner RTTMs published with FastMSS (used by the Nemotron model card),
    when available for the meeting (dev + eval_small subsets)
"""
from __future__ import annotations

import json
import tarfile
from pathlib import Path

from ..annotation import Segment, merge_intervals, read_rttm_single
from ..audio import convert, is_normalized, mix
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download, hf_download

REPO = "microsoft/NOTSOFAR"
VERSIONS = {"eval": "eval_set/240825.1_eval_full_with_GT", "dev": "dev_set/240825.1_dev1",
            "train": "train_set/240825.1_train"}
FASTMSS = "https://github.com/popcornell/FastMSS/raw/master/resources/notsofar1-sessions_mfa_rttms.tar.gz"

META = DatasetMeta(
    name="notsofar1",
    title="NOTSOFAR-1 recorded meetings",
    homepage="https://www.chimechallenge.org/challenges/chime8/task2/index",
    license="CC-BY-4.0",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    annotation_redistributable=True,
    citation="A. Vinnikov et al., 'NOTSOFAR-1 Challenge: New Datasets, Baseline, and Tasks for Distant Meeting Transcription', Interspeech 2024.",
    source_version="microsoft/NOTSOFAR on Hugging Face: 240825.1_eval_full_with_GT, 240825.1_dev1, 240825.1_train",
    description="~6-minute office meetings in 30 rooms, 3-8 participants (35 unique speakers), close-talk + many far-field devices.",
    access="Free download from Hugging Face (no gating) or Azure blob.",
    reference="Human transcription from close-talk mics with word-level timings (multi-stage annotation).",
    default_view="sc",
    views={"sc": "First single-channel far-field device in devices.json (commercial conference device)",
           "ihm-mix": "Sum of the participants' close-talk microphones"},
    gt_rating="A-",
    gt_rating_reason=("Every participant wore a close-talk mic and was transcribed; utterance boundaries are tight and "
                      "word timings are provided; overlap is fully represented. Utterances can include short internal "
                      "pauses; <ST/> (unintelligible) stretches have no word timings."),
    choices=["Speaker ids: NOTSOFAR participant aliases (stable across meetings).",
             "UEM: whole meeting.",
             "sc view: first single-channel device in devices.json (device differs by room/meeting)."],
    domain="meetings (far-field)",
)


def _file(base: Path, version: str, meeting: str, rel: str) -> Path:
    return hf_download(REPO, f"benchmark-datasets/{version}/MTG/{meeting}/{rel}", base / "hf")


def _meetings(version: str) -> list[str]:
    from huggingface_hub import list_repo_files

    pre = f"benchmark-datasets/{version}/MTG/"
    return sorted({f[len(pre):].split("/")[0] for f in list_repo_files(REPO, repo_type="dataset") if f.startswith(pre)})


def _fastmss(base: Path) -> dict[str, Path]:
    arc = download(FASTMSS, base / "fastmss_sessions.tar.gz")
    dest = base / "fastmss"
    if not dest.exists():
        with tarfile.open(arc) as t:
            t.extractall(dest)
    return {p.stem: p for p in dest.rglob("*.rttm")}


def prepare(root=None, raw=None, splits=None, views=None, limit=None, **kw):
    base = raw_root(raw) / "notsofar1"
    views = views or list(META.views)
    w = DatasetWriter(META, root)
    fa = _fastmss(base)
    for split in splits or ["eval", "dev"]:
        version = VERSIONS[split]
        meetings = _meetings(version)[: limit or None]
        for m in meetings:
            sid = w.session_id(m)
            gt = json.loads(_file(base, version, m, "gt_transcription.json").read_text(encoding="utf-8"))
            devices = json.loads(_file(base, version, m, "devices.json").read_text(encoding="utf-8"))
            audio = {}
            if "sc" in views:
                sc = [d for d in devices if not d["is_mc"] and not d["is_close_talk"]]
                if sc:
                    dst = w.audio_path(sid, "sc")
                    if not is_normalized(dst):
                        convert(_file(base, version, m, sc[0]["wav_file_names"]), dst)
                    audio["sc"] = dst
            if "ihm-mix" in views:
                ct = [d["wav_file_names"] for d in devices if d["is_close_talk"]]
                dst = w.audio_path(sid, "ihm-mix")
                if ct and not is_normalized(dst):
                    mix([_file(base, version, m, f) for f in ct], dst)
                if dst.exists():
                    audio["ihm-mix"] = dst
            segs, words = [], []
            for u in gt:
                spk = u["speaker_id"]
                if u["end_time"] > u["start_time"]:
                    segs.append(Segment(u["start_time"], u["end_time"], spk))
                for wd, a, b in u.get("word_timing") or []:
                    if b > a:
                        words.append({"start": a, "end": b, "speaker": spk, "word": wd})
            by_spk: dict[str, list] = {}
            for wd in words:
                by_spk.setdefault(wd["speaker"], []).append((wd["start"], wd["end"]))
            word_segs = [Segment(a, b, s) for s, ivs in by_spk.items() for a, b in merge_intervals(ivs, gap=0.2)]
            alt = {"words_gap0.2": word_segs}
            if m in fa:
                alt["fastmss_mfa"] = read_rttm_single(fa[m])
            w.add_session(m, split, segs, audio=audio, words=words, alt_refs=alt)
            print(f"  [notsofar1] {split} {m} ok", flush=True)
    w.finalize([{"url": f"https://huggingface.co/datasets/{REPO}"}, {"url": FASTMSS}])
