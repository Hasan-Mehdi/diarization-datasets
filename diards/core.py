"""The normalized dataset layout: writer (used by the prepare recipes) and loader (used by everything else).

Layout of one dataset under the data root::

    <root>/<dataset>/
        dataset.json                 license, citation, version, splits, views, ground-truth rating, choices made
        manifest.jsonl               one line per session for the default view
        manifest.<view>.jsonl        one file per additional view (e.g. far-field vs close-talk mix)
        audio/<view>/<session_id>.wav  16 kHz mono 16-bit PCM
        rttm/<session_id>.rttm       reference (shared by all views of a session)
        uem/<session_id>.uem         scoring region(s)
        words/<session_id>.jsonl     word timings, where the corpus has them
        rttm_alt/<variant>/<session_id>.rttm  alternative references (e.g. forced-aligned vs manual)

Session ids are ASCII ``<dataset>__<original_id>``. Speaker ids are unique within a dataset: the corpus' global
speaker ids when it has them, otherwise ``<original_id>_<local_label>``.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

from . import __version__
from .annotation import (
    Segment,
    clip_segments,
    intersect,
    merge_intervals,
    merge_same_speaker,
    overlap_regions,
    read_rttm_single,
    read_uem_single,
    read_words,
    speech_regions,
    total_duration,
    write_rttm,
    write_uem,
    write_words,
)
from .audio import audio_info
from .config import normalized_root

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize(s: str) -> str:
    s = _SAFE.sub("_", s.strip())
    return s.strip("_") or "x"


def make_session_id(dataset: str, original_id: str) -> str:
    return f"{dataset}__{sanitize(original_id)}"


def manifest_name(view: str, default_view: str) -> str:
    return "manifest.jsonl" if view == default_view else f"manifest.{view}.jsonl"


# ============================================================================= loader

@dataclass
class Session:
    session_id: str
    dataset: str
    split: str
    view: str
    original_id: str
    audio_path: Path
    rttm_path: Path
    uem_path: Path
    words_path: Path | None
    duration: float
    num_speakers: int
    overlap_ratio: float
    license: str
    alt_rttm: dict[str, Path] = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    @property
    def segments(self) -> list[Segment]:
        return read_rttm_single(self.rttm_path)

    def alt_segments(self, variant: str) -> list[Segment]:
        return read_rttm_single(self.alt_rttm[variant])

    @property
    def uem(self) -> list[tuple[float, float]]:
        return read_uem_single(self.uem_path)

    @property
    def words(self) -> list[dict] | None:
        return read_words(self.words_path) if self.words_path and self.words_path.exists() else None

    @classmethod
    def from_record(cls, rec: dict, base: Path) -> "Session":
        def p(key):
            v = rec.get(key)
            return (base / v) if v else None

        return cls(
            session_id=rec["session_id"], dataset=rec["dataset"], split=rec["split"], view=rec["view"],
            original_id=rec.get("original_id", rec["session_id"]), audio_path=p("audio_filepath"),
            rttm_path=p("rttm_filepath"), uem_path=p("uem_filepath"), words_path=p("words_filepath"),
            duration=rec["duration"], num_speakers=rec["num_speakers"], overlap_ratio=rec["overlap_ratio"],
            license=rec.get("license", ""), alt_rttm={k: base / v for k, v in (rec.get("alt_rttm") or {}).items()},
            extra=rec.get("extra") or {},
        )


class NormalizedDataset:
    """Read access to one normalized dataset.

    >>> ds = NormalizedDataset("ami")
    >>> for s in ds.sessions(split="test", view="sdm"):
    ...     s.audio_path, s.segments, s.uem, s.words
    """

    def __init__(self, name: str, root: str | Path | None = None):
        self.name = name
        self.dir = normalized_root(root) / name
        meta_path = self.dir / "dataset.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"{meta_path} not found; run `python -m diards prepare {name}` first")
        self.meta = json.loads(meta_path.read_text(encoding="utf-8"))

    @property
    def views(self) -> list[str]:
        return list(self.meta.get("views", {}))

    @property
    def default_view(self) -> str:
        return self.meta.get("default_view") or self.views[0]

    def manifest_path(self, view: str | None = None) -> Path:
        view = view or self.default_view
        return self.dir / manifest_name(view, self.default_view)

    def records(self, view: str | None = None) -> list[dict]:
        path = self.manifest_path(view)
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def sessions(self, split: str | None = None, view: str | None = None) -> list[Session]:
        out = []
        for rec in self.records(view):
            if split and rec["split"] != split:
                continue
            out.append(Session.from_record(rec, self.dir))
        return out

    def __iter__(self) -> Iterator[Session]:
        return iter(self.sessions())

    def __len__(self) -> int:
        return len(self.records())


def load_dataset(name: str, split: str | None = None, view: str | None = None,
                 root: str | Path | None = None) -> list[Session]:
    """Convenience: list the sessions of a normalized dataset."""
    return NormalizedDataset(name, root).sessions(split=split, view=view)


# ============================================================================= writer

@dataclass
class DatasetMeta:
    name: str
    title: str
    homepage: str
    license: str
    license_url: str
    citation: str
    source_version: str
    description: str = ""
    annotation_redistributable: bool = False
    access: str = ""
    reference: str = ""
    default_view: str = "default"
    views: dict[str, str] = field(default_factory=dict)  # view -> description
    gt_rating: str = ""
    gt_rating_reason: str = ""
    choices: list[str] = field(default_factory=list)
    language: str = "en"
    domain: str = ""
    extra: dict = field(default_factory=dict)


class DatasetWriter:
    """Writes sessions into the normalized layout. Idempotent: re-running overwrites annotations
    (cheap) and merges manifests by ``(session_id, view)``; audio conversion is skipped when the target
    WAV is already a valid 16 kHz mono PCM file (see :func:`diards.audio.is_normalized`)."""

    def __init__(self, meta: DatasetMeta, root: str | Path | None = None):
        self.meta = meta
        self.dir = normalized_root(root) / meta.name
        self.dir.mkdir(parents=True, exist_ok=True)
        self._records: dict[tuple[str, str], dict] = {}

    # -- paths
    def session_id(self, original_id: str) -> str:
        return make_session_id(self.meta.name, original_id)

    def audio_path(self, session_id: str, view: str | None = None) -> Path:
        return self.dir / "audio" / (view or self.meta.default_view) / f"{session_id}.wav"

    def rel(self, p: Path) -> str:
        return p.relative_to(self.dir).as_posix()

    # -- sessions
    def add_session(self, original_id: str, split: str, segments: Iterable[Segment],
                    audio: dict[str, Path] | None = None, uem: list[tuple[float, float]] | None = None,
                    words: list[dict] | None = None, alt_refs: dict[str, Iterable[Segment]] | None = None,
                    extra: dict | None = None, merge_gap: float = 0.0) -> str:
        """Register one session.

        ``audio`` maps view -> already-normalized WAV path (defaults to the standard location for every view
        declared in the dataset meta that has a file on disk). ``uem`` defaults to the whole file.
        Same-speaker overlapping segments are merged (``merge_gap`` can also bridge tiny gaps; default 0).
        """
        sid = self.session_id(original_id)
        if audio is None:
            audio = {v: self.audio_path(sid, v) for v in self.meta.views if self.audio_path(sid, v).exists()}
        if not audio:
            raise FileNotFoundError(f"no audio for session {sid}")
        durations = {v: audio_info(p)["duration"] for v, p in audio.items()}
        duration = min(durations.values())
        if uem is None:
            uem = [(0.0, duration)]
        uem = [(max(0.0, a), min(b, duration)) for a, b in uem if min(b, duration) > max(0.0, a)]
        segments = list(segments)
        from .validate import raw_label_issues  # local import: validate imports core

        label_issues = raw_label_issues(segments, duration)
        # drop impossible segments, clip to the audio, then merge same-speaker overlaps
        segments = [Segment(max(0.0, s.start), min(s.end, duration), s.speaker) for s in segments
                    if min(s.end, duration) > max(0.0, s.start)]
        segs = merge_same_speaker(segments, gap=merge_gap)

        rttm_path = self.dir / "rttm" / f"{sid}.rttm"
        uem_path = self.dir / "uem" / f"{sid}.uem"
        write_rttm(rttm_path, sid, segs)
        write_uem(uem_path, sid, uem)
        words_path = None
        if words:
            words_path = self.dir / "words" / f"{sid}.jsonl"
            write_words(words_path, words)
        alt = {}
        for variant, alt_segs in (alt_refs or {}).items():
            p = self.dir / "rttm_alt" / variant / f"{sid}.rttm"
            write_rttm(p, sid, merge_same_speaker(alt_segs))
            alt[variant] = self.rel(p)

        scored = [s for s in clip_segments(segs, uem[0][0], uem[-1][1])] if uem else segs
        speech = intersect(speech_regions(scored), merge_intervals(uem))
        ovl = intersect(overlap_regions(scored), merge_intervals(uem))
        sp = total_duration(speech)
        n_spk = len({s.speaker for s in scored})
        for view, path in audio.items():
            rec = {
                "session_id": sid,
                "dataset": self.meta.name,
                "split": split,
                "view": view,
                "original_id": original_id,
                "audio_filepath": self.rel(Path(path)),
                "rttm_filepath": self.rel(rttm_path),
                "uem_filepath": self.rel(uem_path),
                "words_filepath": self.rel(words_path) if words_path else None,
                "duration": round(durations[view], 3),
                "scored_duration": round(total_duration(merge_intervals(uem)), 3),
                "speech_duration": round(sp, 3),
                "num_speakers": n_spk,
                "overlap_ratio": round(total_duration(ovl) / sp, 4) if sp > 0 else 0.0,
                "license": self.meta.license,
            }
            if alt:
                rec["alt_rttm"] = alt
            if label_issues:
                rec["label_issues"] = label_issues
            if extra:
                rec["extra"] = extra
            self._records[(sid, view)] = rec
        return sid

    # -- finalize
    def finalize(self, sources: list[dict] | None = None) -> None:
        """Write manifests (merged with existing ones) and dataset.json."""
        by_view: dict[str, dict[str, dict]] = {}
        for view in set(self.meta.views) | {v for _, v in self._records}:
            path = self.dir / manifest_name(view, self.meta.default_view)
            existing = {}
            if path.exists():
                with open(path, encoding="utf-8") as fh:
                    for line in fh:
                        if line.strip():
                            r = json.loads(line)
                            existing[r["session_id"]] = r
            by_view[view] = existing
        for (sid, view), rec in self._records.items():
            by_view.setdefault(view, {})[sid] = rec
        splits: dict[str, int] = {}
        for view, recs in by_view.items():
            path = self.dir / manifest_name(view, self.meta.default_view)
            ordered = sorted(recs.values(), key=lambda r: (r["split"], r["session_id"]))
            if not ordered:
                continue
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                for r in ordered:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            if view == self.meta.default_view or not splits:
                splits = {}
                for r in ordered:
                    splits[r["split"]] = splits.get(r["split"], 0) + 1
        m = self.meta
        meta_path = self.dir / "dataset.json"
        old = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        doc = {
            "name": m.name,
            "title": m.title,
            "description": m.description,
            "language": m.language,
            "domain": m.domain,
            "homepage": m.homepage,
            "license": m.license,
            "license_url": m.license_url,
            "annotation_redistributable": m.annotation_redistributable,
            "access": m.access,
            "citation": m.citation,
            "source_version": m.source_version,
            "diards_version": __version__,
            "prepared_at": _dt.datetime.now().isoformat(timespec="seconds"),
            "default_view": m.default_view,
            "views": {v: {"manifest": manifest_name(v, m.default_view), "description": d}
                      for v, d in m.views.items() if (self.dir / manifest_name(v, m.default_view)).exists()},
            "splits": splits,
            "reference": m.reference,
            "gt_rating": m.gt_rating,
            "gt_rating_reason": m.gt_rating_reason,
            "normalization_choices": m.choices,
            "sources": sources if sources is not None else old.get("sources", []),
            **m.extra,
        }
        meta_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
