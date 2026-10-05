"""VoxConverse v0.3 (CC BY 4.0 annotations; audio from YouTube, copyright with the owners).

Audio: the official zips at robots.ox.ac.uk are very slow (~0.25 MB/s when tested), so by default the audio is
taken from the CC-BY Hugging Face mirror ``diarizers-community/voxconverse`` (same 16 kHz WAVs, file names kept),
and the references from the official GitHub repository (master = v0.3, which fixed errors in the test RTTMs).
Pass ``--opt audio_source=official`` to download the official zips instead.
"""
from __future__ import annotations

from pathlib import Path

from ..annotation import Segment, read_rttm_single
from ..audio import convert, is_normalized, write_array
from ..config import raw_root
from ..core import DatasetMeta, DatasetWriter
from ..download import download, extract, git_clone
from ._hf_audio import decode_audio, iter_parquet_rows, list_repo_files

REPO = "https://github.com/joonson/voxconverse.git"
HF_REPO = "diarizers-community/voxconverse"
OFFICIAL = {"dev": "https://www.robots.ox.ac.uk/~vgg/data/voxconverse/data/voxconverse_dev_wav.zip",
            "test": "https://www.robots.ox.ac.uk/~vgg/data/voxconverse/data/voxconverse_test_wav.zip"}

META = DatasetMeta(
    name="voxconverse",
    title="VoxConverse v0.3",
    homepage="https://www.robots.ox.ac.uk/~vgg/data/voxconverse/",
    license="CC-BY-4.0",
    license_url="https://creativecommons.org/licenses/by/4.0/",
    annotation_redistributable=True,
    citation="J. S. Chung, J. Huh, A. Nagrani, T. Afouras, A. Zisserman, 'Spot the conversation: speaker diarisation in the wild', Interspeech 2020.",
    source_version="joonson/voxconverse master (v0.3 RTTMs)",
    description="YouTube clips (political debates, news, talk shows), 216 dev + 232 test recordings, 1-21 speakers.",
    access="Free download, no registration (audio CC BY 4.0 for research; copyright remains with video owners).",
    reference="Manual annotation (semi-automatic pipeline + human verification/correction), v0.3 corrections.",
    default_view="default",
    views={"default": "Original single-channel YouTube audio, 16 kHz"},
    gt_rating="B+",
    gt_rating_reason=("Human-verified diarization-oriented labels (pauses > 0.25 s split), overlap annotated, "
                      "two public correction rounds (v0.2, v0.3). Created with an audio-visual pipeline then "
                      "manually checked, so some short backchannels/off-screen speech can be missing."),
    choices=["Splits: official dev (216) / test (232).",
             "Speaker ids: <file>_<spkNN> (VoxConverse labels are per file).",
             "UEM: whole file (VoxConverse has no official UEM).",
             "Audio: HF mirror diarizers-community/voxconverse by default (identical 16 kHz WAVs)."],
    domain="in-the-wild media (broadcast / YouTube)",
)


def prepare(root=None, raw=None, splits=None, views=None, limit=None, audio_source="hf", **kw):
    base = raw_root(raw) / "voxconverse"
    git_clone(REPO, base / "repo")
    w = DatasetWriter(META, root)
    splits = splits or ["dev", "test"]
    for split in splits:
        rttms = sorted((base / "repo" / split).glob("*.rttm"))[: limit or None]
        wanted = {p.stem for p in rttms}
        todo = {fid for fid in wanted if not is_normalized(w.audio_path(w.session_id(fid)))}
        if todo and audio_source == "official":
            z = download(OFFICIAL[split], base / Path(OFFICIAL[split]).name)
            extract(z, base / "official" / split)
            for fid in sorted(todo):
                src = next((base / "official" / split).rglob(f"{fid}.wav"))
                convert(src, w.audio_path(w.session_id(fid)))
        elif todo:
            files = list_repo_files(HF_REPO, f"data/{split}-")
            for row in iter_parquet_rows(HF_REPO, files, base / "hf", columns=["audio"],
                                         want=lambda r: Path(r["audio"]["path"]).stem in todo):
                fid = Path(row["audio"]["path"]).stem
                x, sr = decode_audio(row["audio"])
                write_array(w.audio_path(w.session_id(fid)), x, sr)
                todo.discard(fid)
                if not todo:
                    break
        for p in rttms:
            fid = p.stem
            segs = [Segment(s.start, s.end, f"{fid}_{s.speaker}") for s in read_rttm_single(p)]
            w.add_session(fid, split, segs)
        print(f"  [voxconverse] {split}: {len(rttms)} sessions", flush=True)
    w.finalize([{"url": REPO}, {"url": f"https://huggingface.co/datasets/{HF_REPO}"}])
