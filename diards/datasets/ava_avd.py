"""AVA-AVD, English subset (annotations: see repo license; videos: AVA / CVDF mirror of YouTube movies).

AVA-AVD labels "who spoke when" on 351 five-minute clips (minutes 15-30 of 117 movies from the AVA dataset).
The movies are multilingual, so this recipe keeps the clips whose speech Whisper large-v3 identifies as English
(P(en) >= 0.7, see diards.lid); the per-clip language probabilities are stored in
``metadata/ava_avd_lid.json`` in this repository.

Audio: only minutes 15-30 of each movie are fetched (ffmpeg seeks inside the CVDF S3 file over HTTP).
Splits: official train / val / test lists.
UEM: official AVA-AVD protocol - from the first to the last reference segment of the clip (the official scripts
crop each clip's audio to that extent).
Extra: the corpus also ships speech-activity ``.lab`` files. Speech marked there but not covered by any speaker
segment is recorded per clip as ``extra.lab_speech_without_speaker_s``; it is 0 for every clip (the labs are the
union of the RTTM segments).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from ..annotation import Segment, intersect, merge_intervals, read_rttm_single, speech_regions, subtract, total_duration
from ..audio import is_normalized, write_array
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import git_clone
from .. import lid as lidmod

REPO = "https://github.com/zcxu-eric/AVA-AVD.git"
ANN_GDRIVE = "18kjJJbebBg7e8umI6HoGE4_tI3OWufzA"
S3 = "https://s3.amazonaws.com/ava-dataset/trainval"
REPO_ROOT = Path(__file__).resolve().parents[2]
LID_CACHE = REPO_ROOT / "metadata" / "ava_avd_lid.json"

META = DatasetMeta(
    name="ava_avd_en",
    title="AVA-AVD (English subset)",
    homepage="https://github.com/zcxu-eric/AVA-AVD",
    license="Research use (AVA annotations CC BY 4.0; movies copyrighted, distributed by CVDF for research)",
    license_url="https://research.google.com/ava/download.html",
    citation="E. Z. Xu et al., 'AVA-AVD: Audio-Visual Speaker Diarization in the Wild', ACM MM 2022.",
    source_version="zcxu-eric/AVA-AVD (git HEAD) + annotations.tar.gz (Google Drive) + CVDF AVA trainval videos",
    description="Movie clips (5 min) from the AVA dataset: dialogue in diverse scenes, off-screen speakers, music/effects.",
    access="Free: annotations on GitHub/Google Drive, videos from the CVDF S3 mirror.",
    reference="Human audio-visual diarization labels on top of AVA-ActiveSpeaker.",
    default_view="default",
    views={"default": "Movie soundtrack, mono 16 kHz"},
    gt_rating="B-",
    gt_rating_reason=("Human-labelled identities including off-screen speakers on hard movie audio; built on top of "
                      "visual active-speaker tracks; scoring region cropped to the labelled extent."),
    choices=["English subset by Whisper large-v3 LID (P(en) >= 0.7 over up to 3 x 30 s windows on reference speech).",
             "Speaker ids: <clip>_<spkNN>.", "UEM: first to last reference segment (official AVA-AVD cropping).",
             "Times shifted so that 0 = start of the 5-minute clip window (900 + 300*(k-1) s into the movie)."],
    domain="movies (in-the-wild media)",
)


def _ensure_annotations(base: Path) -> Path:
    git_clone(REPO, base / "repo")
    if not (base / "rttms").exists():
        import tarfile

        import gdown

        arc = base / "annotations.tar.gz"
        if not arc.exists():
            gdown.download(id=ANN_GDRIVE, output=str(arc), quiet=False)
        with tarfile.open(arc) as t:  # actually an uncompressed tar despite the name
            t.extractall(base)
    return base


def _movie_block(base: Path, video: str) -> Path:
    """16 kHz mono audio of minutes 15-30 (900-1805 s) of the movie."""
    uid = video.split(".")[0]
    out = base / "audio" / f"{uid}.wav"
    if out.exists() and out.stat().st_size > 1000:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp.wav")
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-ss", "900", "-t", "905",
           "-i", f"{S3}/{video}", "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(tmp)]
    subprocess.run(cmd, check=True)
    tmp.replace(out)
    return out


def prepare(root=None, raw=None, splits=None, views=None, limit=None, lid_threshold=lidmod.THRESHOLD, **kw):
    base = _ensure_annotations(raw_root(raw) / "ava_avd")
    split_dir = base / "repo" / "dataset" / "split"
    videos = [v.strip() for v in (split_dir / "video.list").read_text().split() if v.strip()]
    by_uid = {v.split(".")[0]: v for v in videos}
    split_of = {}
    for split in ("train", "val", "test"):
        for c in (split_dir / f"{split}.list").read_text().split():
            split_of[c.strip()] = split
    lid_cache = lidmod.load_cache(LID_CACHE)
    lid = None
    w = DatasetWriter(META, root)
    clips = sorted(p.stem for p in (base / "rttms").glob("*.rttm"))
    if splits:
        clips = [c for c in clips if split_of.get(c) in splits]
    if limit:
        clips = clips[:limit]
    kept = 0
    for clip in clips:
        uid, k = clip[:-5], int(clip[-2:])
        start = 900.0 + 300.0 * (k - 1)
        segs_abs = read_rttm_single(base / "rttms" / f"{clip}.rttm")
        segs = [Segment(s.start - start, s.end - start, f"{clip}_{s.speaker}") for s in segs_abs]
        sid = w.session_id(clip)
        need_audio = clip not in lid_cache or (lid_cache[clip]["p_en"] >= lid_threshold and not is_normalized(w.audio_path(sid)))
        x = None
        if need_audio:
            try:
                block = _movie_block(base, by_uid[uid])
            except Exception as exc:
                print(f"  [ava_avd] {clip}: audio unavailable ({exc})")
                continue
            data, sr = sf.read(str(block), dtype="float32")
            x = data[int((start - 900.0) * sr): int((start - 900.0 + 300.0) * sr)]
        if clip not in lid_cache:
            lid = lid or lidmod.WhisperLID()
            lid_cache[clip] = lidmod.detect(lid, x, segs)
            lidmod.save_cache(LID_CACHE, lid_cache)
        if lid_cache[clip]["p_en"] < lid_threshold:
            continue
        if not is_normalized(w.audio_path(sid)):
            write_array(w.audio_path(sid), x, 16000)
        # unlabelled speech: .lab speech regions not covered by any speaker segment (inside the UEM)
        lo, hi = min(s.start for s in segs), max(s.end for s in segs)
        lab = base / "labs" / f"{clip}.lab"
        extra = {"lid": lid_cache[clip]}
        if lab.exists():
            lab_ivs = []
            for line in lab.read_text().splitlines():
                p = line.split()
                if len(p) >= 3 and p[2] == "speech":
                    lab_ivs.append((float(p[0]) - start, float(p[1]) - start))
            unl = subtract(intersect(merge_intervals(lab_ivs), [(lo, hi)]), speech_regions(segs))
            extra["lab_speech_without_speaker_s"] = round(total_duration(unl), 2)
        w.add_session(clip, split_of.get(clip, "unknown"), segs, uem=[(max(0.0, lo), hi)], extra=extra)
        kept += 1
        print(f"  [ava_avd] {split_of.get(clip)} {clip} kept (p_en={lid_cache[clip]['p_en']})", flush=True)
    print(f"  [ava_avd] kept {kept} English clips of {len(clips)}")
    w.finalize([{"url": REPO}, {"url": S3}])
