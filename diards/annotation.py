"""Speaker segments, RTTM / UEM / word files, and the interval arithmetic used everywhere else.

Conventions
-----------
* Times are seconds (float). Files are written with millisecond precision.
* A *segment* is ``Segment(start, end, speaker)``; a reference is a list of segments, possibly overlapping
  across speakers. Same-speaker overlaps are merged by :func:`merge_same_speaker`.
* A *UEM* is a list of ``(start, end)`` scoring regions.
* Words are dicts ``{"start", "end", "speaker", "word"}`` (one JSON object per line on disk).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


@dataclass(frozen=True, order=True)
class Segment:
    start: float
    end: float
    speaker: str

    @property
    def duration(self) -> float:
        return self.end - self.start


# ----------------------------------------------------------------------------- RTTM

def read_rttm(path: str | Path) -> dict[str, list[Segment]]:
    """Read an RTTM file into ``{file_id: [Segment, ...]}``. Only ``SPEAKER`` lines are used."""
    out: dict[str, list[Segment]] = {}
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            parts = line.split()
            if not parts or parts[0].startswith(";") or parts[0] != "SPEAKER":
                continue
            if len(parts) < 8:
                raise ValueError(f"{path}:{lineno}: malformed RTTM line: {line.rstrip()}")
            file_id, start, dur, spk = parts[1], float(parts[3]), float(parts[4]), parts[7]
            out.setdefault(file_id, []).append(Segment(start, start + dur, spk))
    return out


def read_rttm_single(path: str | Path) -> list[Segment]:
    data = read_rttm(path)
    segs: list[Segment] = []
    for v in data.values():
        segs.extend(v)
    return sorted(segs)


def format_rttm(file_id: str, segments: Iterable[Segment], channel: int = 1) -> str:
    lines = []
    for s in sorted(segments):
        lines.append(
            f"SPEAKER {file_id} {channel} {s.start:.3f} {s.end - s.start:.3f} <NA> <NA> {s.speaker} <NA> <NA>"
        )
    return "\n".join(lines) + ("\n" if lines else "")


def write_rttm(path: str | Path, file_id: str, segments: Iterable[Segment]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(format_rttm(file_id, segments), encoding="utf-8", newline="\n")


# ----------------------------------------------------------------------------- UEM

def read_uem(path: str | Path) -> dict[str, list[tuple[float, float]]]:
    out: dict[str, list[tuple[float, float]]] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) < 4 or parts[0].startswith(";"):
                continue
            out.setdefault(parts[0], []).append((float(parts[2]), float(parts[3])))
    return out


def read_uem_single(path: str | Path) -> list[tuple[float, float]]:
    regions: list[tuple[float, float]] = []
    for v in read_uem(path).values():
        regions.extend(v)
    return sorted(regions)


def write_uem(path: str | Path, file_id: str, regions: Iterable[tuple[float, float]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    text = "".join(f"{file_id} 1 {a:.3f} {b:.3f}\n" for a, b in sorted(regions))
    Path(path).write_text(text, encoding="utf-8", newline="\n")


# ----------------------------------------------------------------------------- words

def write_words(path: str | Path, words: Iterable[dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for w in sorted(words, key=lambda w: (w["start"], w["end"])):
            rec = {"start": round(float(w["start"]), 3), "end": round(float(w["end"]), 3),
                   "speaker": w["speaker"], "word": w["word"]}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_words(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


# ----------------------------------------------------------------------------- interval arithmetic

def merge_intervals(intervals: Iterable[tuple[float, float]], gap: float = 0.0) -> list[tuple[float, float]]:
    """Union of intervals; intervals separated by at most ``gap`` seconds are joined."""
    ivs = sorted((a, b) for a, b in intervals if b > a)
    out: list[list[float]] = []
    for a, b in ivs:
        if out and a <= out[-1][1] + gap:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def total_duration(intervals: Iterable[tuple[float, float]]) -> float:
    return sum(b - a for a, b in intervals)


def intersect(a: Sequence[tuple[float, float]], b: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    """Intersection of two sorted, non-overlapping interval lists."""
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if hi > lo:
            out.append((lo, hi))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def subtract(a: Sequence[tuple[float, float]], b: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    """``a`` minus ``b`` for sorted, non-overlapping interval lists."""
    out = []
    j = 0
    for lo, hi in a:
        cur = lo
        while j < len(b) and b[j][1] <= cur:
            j += 1
        k = j
        while k < len(b) and b[k][0] < hi:
            if b[k][0] > cur:
                out.append((cur, b[k][0]))
            cur = max(cur, b[k][1])
            k += 1
        if cur < hi:
            out.append((cur, hi))
    return out


def merge_same_speaker(segments: Iterable[Segment], gap: float = 0.0) -> list[Segment]:
    """Merge overlapping (or closer than ``gap``) segments of the same speaker."""
    by_spk: dict[str, list[tuple[float, float]]] = {}
    for s in segments:
        by_spk.setdefault(s.speaker, []).append((s.start, s.end))
    out = [Segment(a, b, spk) for spk, ivs in by_spk.items() for a, b in merge_intervals(ivs, gap)]
    return sorted(out)


def speech_regions(segments: Iterable[Segment]) -> list[tuple[float, float]]:
    return merge_intervals((s.start, s.end) for s in segments)


def overlap_regions(segments: Iterable[Segment], min_speakers: int = 2) -> list[tuple[float, float]]:
    """Regions where at least ``min_speakers`` distinct speakers are active (same-speaker overlaps merged first)."""
    events = []
    for s in merge_same_speaker(segments):
        events.append((s.start, 1))
        events.append((s.end, -1))
    events.sort(key=lambda e: (e[0], e[1]))
    out = []
    count = 0
    start = None
    for t, d in events:
        prev = count
        count += d
        if prev < min_speakers <= count:
            start = t
        elif prev >= min_speakers > count and start is not None:
            if t > start:
                out.append((start, t))
            start = None
    return merge_intervals(out)


def clip_segments(segments: Iterable[Segment], lo: float, hi: float) -> list[Segment]:
    out = []
    for s in segments:
        a, b = max(s.start, lo), min(s.end, hi)
        if b > a:
            out.append(Segment(a, b, s.speaker))
    return out


def iter_speakers(segments: Iterable[Segment]) -> Iterator[str]:
    seen = set()
    for s in segments:
        if s.speaker not in seen:
            seen.add(s.speaker)
            yield s.speaker
