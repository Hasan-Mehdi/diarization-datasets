"""MSDWild, English subset (research-only license agreement; no redistribution).

MSDWild has 3,143 vlog-style video clips (~80 h) in many languages, with no language labels. This recipe keeps the
clips whose speech Whisper large-v3 identifies as English (P(en) >= 0.7; see diards.lid) and stores the per-clip
language probabilities in ``metadata/msdwild_lid.json`` so the subset is reproducible.

Splits: the official ``few.train`` / ``few.val`` / ``many.val`` RTTMs (few = 2-4 speakers, many = 5+ speakers).
Files with negative names (~90) are skipped as instructed by the maintainers. UEM: whole clip.
Before downloading, read and accept ``MSDWILD_license_agreement.pdf`` (research use only, no redistribution).
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import soundfile as sf

from ..annotation import Segment, read_rttm
from ..audio import is_normalized, write_array
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import file_hash, git_clone
from .. import lid as lidmod

REPO = "https://github.com/X-LANCE/MSDWILD.git"
WAV_GDRIVE = "1I5qfuPPGBM9keJKz0VN-OYEeRMJ7dgpl"
WAV_MD5 = "0057f82daaddf2ce993d1bf0679929c4"
LID_CACHE = Path(__file__).resolve().parents[2] / "metadata" / "msdwild_lid.json"
SPLITS = {"few.train": "few.train.rttm", "few.val": "few.val.rttm", "many.val": "many.val.rttm"}

META = DatasetMeta(
    name="msdwild_en",
    title="MSDWild (English subset)",
    homepage="https://github.com/X-LANCE/MSDWILD",
    license="MSDWild license agreement (research only, no redistribution)",
    license_url="https://github.com/X-LANCE/MSDWILD/blob/master/MSDWILD_license_agreement.pdf",
    citation="T. Liu et al., 'MSDWild: Multi-modal Speaker Diarization Dataset in the Wild', Interspeech 2022.",
    source_version="X-LANCE/MSDWILD (git HEAD rttms) + wav archive (Google Drive, md5 0057f82d...)",
    description="Daily-life vlog clips (~25 s to a few minutes) with natural conversation and frequent overlap.",
    access="Free download (Google Drive); accept the research-only license agreement.",
    reference="Manual audio-visual annotation (pauses > 0.25 s split), later corrections credited in the repo.",
    default_view="default",
    views={"default": "Clip audio, mono 16 kHz"},
    gt_rating="B",
    gt_rating_reason=("Human, diarization-oriented labels with overlap, but short clips, no language tags, and the "
                      "maintainers withdrew ~90 files; label quality checked below."),
    choices=["English subset by Whisper large-v3 LID (P(en) >= 0.7).", "Speaker ids: <clip>_<label>.",
             "UEM: whole clip.", "Files with negative ids skipped."],
    domain="vlogs (in-the-wild media)",
)


def _wav_zip(base: Path) -> Path:
    z = base / "msdwild_wavs.zip"
    if not z.exists():
        import gdown

        gdown.download(id=WAV_GDRIVE, output=str(z), quiet=False)
        if file_hash(z) != WAV_MD5:
            raise RuntimeError("MSDWild wav archive md5 mismatch")
    return z


def prepare(root=None, raw=None, splits=None, views=None, limit=None, lid_threshold=lidmod.THRESHOLD, **kw):
    base = raw_root(raw) / "msdwild"
    git_clone(REPO, base / "repo")
    lid_cache = lidmod.load_cache(LID_CACHE)
    lid = None
    w = DatasetWriter(META, root)
    zf = None
    names = {}
    kept = total = 0
    for split in splits or list(SPLITS):
        refs = read_rttm(base / "repo" / "rttms" / SPLITS[split])
        for fid in sorted(refs)[: limit or None]:
            if fid.startswith("-"):
                continue
            total += 1
            segs = [Segment(s.start, s.end, f"{fid}_{s.speaker}") for s in refs[fid]]
            sid = w.session_id(fid)
            x = None
            if fid not in lid_cache or (lid_cache[fid]["p_en"] >= lid_threshold and not is_normalized(w.audio_path(sid))):
                if zf is None:
                    zf = zipfile.ZipFile(_wav_zip(base))
                    names = {Path(n).stem: n for n in zf.namelist() if n.endswith(".wav")}
                if fid not in names:
                    print(f"  [msdwild] {fid}: no audio in archive")
                    continue
                import io

                x, sr = sf.read(io.BytesIO(zf.read(names[fid])), dtype="float32", always_2d=True)
                x = x.mean(axis=1)
                if sr != 16000:
                    import soxr

                    x = soxr.resample(x, sr, 16000)
            if fid not in lid_cache:
                lid = lid or lidmod.WhisperLID()
                lid_cache[fid] = lidmod.detect(lid, x, segs)
                if total % 50 == 0:
                    lidmod.save_cache(LID_CACHE, lid_cache)
            if lid_cache[fid]["p_en"] < lid_threshold:
                continue
            if not is_normalized(w.audio_path(sid)):
                write_array(w.audio_path(sid), x, 16000)
            w.add_session(fid, split, segs, extra={"lid": lid_cache[fid]})
            kept += 1
        lidmod.save_cache(LID_CACHE, lid_cache)
        print(f"  [msdwild] {split}: kept {kept} English clips so far (of {total})", flush=True)
    w.finalize([{"url": REPO}, {"url": f"https://drive.google.com/file/d/{WAV_GDRIVE}"}])
