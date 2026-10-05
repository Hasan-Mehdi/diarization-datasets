"""Export adapters: normalized dataset -> NeMo manifests, pyannote.database protocol, Lhotse manifests.

All exports read the normalized manifests (one view at a time) and point at the normalized files with absolute
paths, so they always use exactly the references, UEMs and audio that ``diards evaluate`` uses.

Default output directory: ``<root>/<dataset>/exports/<format>/``.

* NeMo:     ``<dataset>.<view>.<split>.json`` - one JSON object per line with audio_filepath, offset, duration,
            label, text, num_speakers, rttm_filepath, uem_filepath (the format of NeMo's diarization scripts,
            e.g. e2e_diarize_speech.py / speaker diarization inference).
* pyannote: ``database.yml`` declaring one database + ``SpeakerDiarization`` protocol per view, named
            ``<dataset>_<view>`` (``-`` replaced by ``_``) with task ``default``; per-subset uri lists, RTTM and UEM
            files. Load with ``PYANNOTE_DATABASE_CONFIG=<path>/database.yml`` and
            ``get_protocol("<dataset>_<view>.SpeakerDiarization.default")``.
* Lhotse:   ``<dataset>_<view>_recordings_<split>.jsonl.gz`` and ``..._supervisions_<split>.jsonl.gz``
            (one supervision per RTTM speaker segment). A generic converter is used for every dataset, so no
            corpus-specific Lhotse code is duplicated; see docs/FORMAT.md for the native Lhotse recipes that exist
            for some of these corpora and how they differ.
"""
from __future__ import annotations

import json
from pathlib import Path

from .core import NormalizedDataset, Session

PYANNOTE_SUBSET = {"train": "train", "few.train": "train",
                   "dev": "development", "val": "development", "development": "development", "dev1": "development",
                   "few.val": "development",
                   "test": "test", "eval": "test", "many.val": "test", "eval10": "test"}


def pyannote_subset(split: str, all_splits: set[str]) -> str:
    if split in PYANNOTE_SUBSET:
        return PYANNOTE_SUBSET[split]
    return "test"  # single-split corpora ('all', 'data', 'medical', 'other', ...) are evaluation material


def _views(ds: NormalizedDataset, view: str | None) -> list[str]:
    return [view] if view else ds.views


def export(name: str, fmt: str, root=None, view: str | None = None, out=None) -> Path:
    ds = NormalizedDataset(name, root)
    out = Path(out) if out else ds.dir / "exports" / fmt
    out.mkdir(parents=True, exist_ok=True)
    {"nemo": export_nemo, "pyannote": export_pyannote, "lhotse": export_lhotse}[fmt](ds, out, view)
    print(f"[export] {name} -> {fmt}: {out}")
    return out


# ----------------------------------------------------------------------------- NeMo

def nemo_record(s: Session) -> dict:
    return {
        "audio_filepath": str(s.audio_path.resolve()),
        "offset": 0,
        "duration": s.duration,
        "label": "infer",
        "text": "-",
        "num_speakers": s.num_speakers,
        "rttm_filepath": str(s.rttm_path.resolve()),
        "uem_filepath": str(s.uem_path.resolve()),
        "ctm_filepath": None,
    }


def export_nemo(ds: NormalizedDataset, out: Path, view=None) -> None:
    for v in _views(ds, view):
        by_split: dict[str, list[Session]] = {}
        for s in ds.sessions(view=v):
            by_split.setdefault(s.split, []).append(s)
        for split, sessions in by_split.items():
            path = out / f"{ds.name}.{v}.{split}.json"
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                for s in sessions:
                    fh.write(json.dumps(nemo_record(s)) + "\n")


# ----------------------------------------------------------------------------- pyannote

def protocol_name(ds_name: str, view: str) -> str:
    return f"{ds_name}_{view}".replace("-", "_").replace(".", "_")


def export_pyannote(ds: NormalizedDataset, out: Path, view=None) -> None:
    import yaml

    databases, protocols = {}, {}
    for v in _views(ds, view):
        pname = protocol_name(ds.name, v)
        sessions = ds.sessions(view=v)
        if not sessions:
            continue
        databases[pname] = str((ds.dir / "audio" / v).resolve() / "{uri}.wav").replace("\\", "/")
        splits = {s.split for s in sessions}
        subsets: dict[str, list[Session]] = {}
        for s in sessions:
            subsets.setdefault(pyannote_subset(s.split, splits), []).append(s)
        # speaker ids are unique within a dataset (global corpus ids or <session>_<label>)
        proto: dict = {"scope": "database"}
        for subset, items in subsets.items():
            names = {ext: f"{pname}.{subset}.{ext}" for ext in ("lst", "rttm", "uem")}
            (out / names["lst"]).write_text("".join(f"{s.session_id}\n" for s in items), encoding="utf-8")
            with open(out / names["rttm"], "w", encoding="utf-8", newline="\n") as fh:
                for s in items:
                    fh.write(s.rttm_path.read_text(encoding="utf-8"))
            with open(out / names["uem"], "w", encoding="utf-8", newline="\n") as fh:
                for s in items:
                    fh.write(s.uem_path.read_text(encoding="utf-8"))
            proto[subset] = {"uri": names["lst"], "annotation": names["rttm"], "annotated": names["uem"]}
        protocols[pname] = {"SpeakerDiarization": {"default": proto}}
    doc = {"Databases": databases, "Protocols": protocols}
    (out / "database.yml").write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


# ----------------------------------------------------------------------------- Lhotse

def export_lhotse(ds: NormalizedDataset, out: Path, view=None) -> None:
    from lhotse import AudioSource, Recording, RecordingSet, SupervisionSegment, SupervisionSet

    for v in _views(ds, view):
        by_split: dict[str, list[Session]] = {}
        for s in ds.sessions(view=v):
            by_split.setdefault(s.split, []).append(s)
        for split, sessions in by_split.items():
            recs, sups = [], []
            for s in sessions:
                import soundfile as sf

                info = sf.info(str(s.audio_path))
                recs.append(Recording(id=s.session_id, sampling_rate=info.samplerate, num_samples=info.frames,
                                      duration=info.frames / info.samplerate,
                                      sources=[AudioSource(type="file", channels=[0], source=str(s.audio_path.resolve()))]))
                for i, seg in enumerate(s.segments):
                    sups.append(SupervisionSegment(id=f"{s.session_id}-{i:05d}", recording_id=s.session_id,
                                                   start=round(seg.start, 3), duration=round(seg.duration, 3),
                                                   channel=0, speaker=seg.speaker, language="English"))
            tag = f"{ds.name}_{v}".replace("-", "_")
            RecordingSet.from_recordings(recs).to_file(out / f"{tag}_recordings_{split}.jsonl.gz")
            SupervisionSet.from_segments(sups).to_file(out / f"{tag}_supervisions_{split}.jsonl.gz")
