"""Dataset statistics computed from the normalized references (inside each session's UEM)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .annotation import (
    clip_segments,
    intersect,
    merge_intervals,
    overlap_regions,
    speech_regions,
    subtract,
    total_duration,
)
from .core import NormalizedDataset


def _pct(values, qs=(5, 25, 50, 75, 95)):
    if len(values) == 0:
        return {f"p{q}": None for q in qs}
    arr = np.asarray(values, dtype=float)
    return {f"p{q}": round(float(np.percentile(arr, q)), 3) for q in qs}


def session_stats(segs, uem) -> dict:
    uem_m = merge_intervals(uem)
    lo, hi = (uem_m[0][0], uem_m[-1][1]) if uem_m else (0.0, 0.0)
    segs = clip_segments(segs, lo, hi)
    scored = total_duration(uem_m)
    sp = intersect(speech_regions(segs), uem_m)
    ov = intersect(overlap_regions(segs), uem_m)
    ov3 = intersect(overlap_regions(segs, 3), uem_m)
    speech = total_duration(sp)
    spk_time: dict[str, float] = {}
    by_spk: dict[str, list] = {}
    for s in segs:
        spk_time[s.speaker] = spk_time.get(s.speaker, 0.0) + s.duration
        by_spk.setdefault(s.speaker, []).append((s.start, s.end))
    pauses = []
    for ivs in by_spk.values():
        ivs = merge_intervals(ivs)
        pauses += [b[0] - a[1] for a, b in zip(ivs, ivs[1:])]
    silences = [b - a for a, b in subtract(uem_m, sp)]
    # speaker changes: order merged single-speaker regions by time
    turns = sorted((s.start, s.speaker) for s in segs)
    changes = sum(1 for a, b in zip(turns, turns[1:]) if a[1] != b[1])
    dom = max(spk_time.values()) / sum(spk_time.values()) if spk_time else 0.0
    return {
        "scored_s": scored,
        "speech_s": speech,
        "overlap_s": total_duration(ov),
        "overlap3_s": total_duration(ov3),
        "num_speakers": len(spk_time),
        "num_segments": len(segs),
        "seg_durations": [s.duration for s in segs],
        "same_speaker_pauses": pauses,
        "silences": silences,
        "speaker_changes": changes,
        "dominant_speaker_share": dom,
    }


def dataset_stats(name: str, root=None, view: str | None = None, out=None, echo: bool = False,
                  splits: list[str] | None = None) -> dict:
    ds = NormalizedDataset(name, root)
    sessions = ds.sessions(view=view)
    if splits:
        sessions = [s for s in sessions if s.split in splits]
    per_split: dict[str, list] = {}
    rows = []
    for s in sessions:
        st = session_stats(s.segments, s.uem)
        st["session_id"], st["split"], st["duration"] = s.session_id, s.split, s.duration
        per_split.setdefault(s.split, []).append(st)
        per_split.setdefault("ALL", []).append(st)
        rows.append({k: (round(v, 3) if isinstance(v, float) else v) for k, v in st.items()
                     if not isinstance(v, list)})
    summary = {split: _aggregate(items) for split, items in per_split.items()}
    result = {"dataset": name, "view": view or ds.default_view, "summary": summary, "sessions": rows}
    if out:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        tag = f"{name}"
        (out / f"stats.{tag}.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
        (out / f"stats.{tag}.md").write_text(to_markdown(result), encoding="utf-8")
    if echo:
        print(to_markdown(result))
    return result


def _aggregate(items: list[dict]) -> dict:
    segd = [d for it in items for d in it["seg_durations"]]
    pauses = [p for it in items for p in it["same_speaker_pauses"]]
    sil = [p for it in items for p in it["silences"]]
    spk = [it["num_speakers"] for it in items]
    speech = sum(it["speech_s"] for it in items)
    scored = sum(it["scored_s"] for it in items)
    ovl = sum(it["overlap_s"] for it in items)
    return {
        "sessions": len(items),
        "hours": round(sum(it["duration"] for it in items) / 3600, 2),
        "scored_hours": round(scored / 3600, 2),
        "speech_hours": round(speech / 3600, 2),
        "speech_ratio": round(speech / scored, 3) if scored else None,
        "overlap_ratio": round(ovl / speech, 3) if speech else None,
        "overlap3plus_ratio": round(sum(it["overlap3_s"] for it in items) / speech, 4) if speech else None,
        "speakers_min": int(min(spk)) if spk else None,
        "speakers_median": float(np.median(spk)) if spk else None,
        "speakers_max": int(max(spk)) if spk else None,
        "sessions_with_1_speaker": sum(1 for x in spk if x < 2),
        "segments": len(segd),
        "segment_s": {**_pct(segd), "mean": round(float(np.mean(segd)), 3) if segd else None},
        "segments_under_0.2s_frac": round(float(np.mean(np.asarray(segd) < 0.2)), 4) if segd else None,
        "same_speaker_pause_s": _pct(pauses),
        "pauses_under_0.25s_frac": round(float(np.mean(np.asarray(pauses) < 0.25)), 4) if pauses else None,
        "silence_gap_s": _pct(sil),
        "speaker_changes_per_min": round(sum(it["speaker_changes"] for it in items) / max(1e-9, scored / 60), 2),
        "dominant_speaker_share_median": round(float(np.median([it["dominant_speaker_share"] for it in items])), 3)
        if items else None,
    }


def to_markdown(result: dict) -> str:
    lines = [f"# Statistics: {result['dataset']} (view: {result['view']})", "",
             "Computed from the normalized reference RTTMs inside each session's UEM. "
             "Overlap ratio = time with >= 2 active speakers / speech time.", "",
             "| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk overlap | spk min/med/max |"
             " segments | seg p5/p50/p95 (s) | <0.2 s segs | same-spk pause p50 (s) | pauses <0.25 s | spk changes/min |",
             "|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---:|---:|---:|"]
    order = sorted(k for k in result["summary"] if k != "ALL") + (["ALL"] if "ALL" in result["summary"] else [])
    for split in order:
        a = result["summary"][split]
        sd = a["segment_s"]
        lines.append(
            f"| {split} | {a['sessions']} | {a['hours']} | {a['speech_hours']} | {a['speech_ratio']} | {a['overlap_ratio']} | "
            f"{a['overlap3plus_ratio']} | {a['speakers_min']}/{a['speakers_median']:g}/{a['speakers_max']} | {a['segments']} | "
            f"{sd['p5']}/{sd['p50']}/{sd['p95']} | {a['segments_under_0.2s_frac']} | {a['same_speaker_pause_s']['p50']} | "
            f"{a['pauses_under_0.25s_frac']} | {a['speaker_changes_per_min']} |")
    return "\n".join(lines) + "\n"
