"""Audit of PriMock57's diarization ground truth using its separate doctor/patient channels.

PriMock57 recorded each participant on a separate channel and the channels are almost perfectly isolated
(the other speaker sits ~60 dB below), so per-channel energy tells us when each person was actually making sound.
We compare that with the official utterance-level TextGrids:

  1. channel isolation (level of the other speaker on each channel)
  2. silence inside labelled utterances (own channel silent for >= 0.3 s inside a TextGrid interval)
  3. sound outside any utterance (own channel active for >= 0.5 s with no TextGrid interval within 0.25 s)
  4. boundary offsets (TextGrid start/end vs first/last own-channel activity inside the interval +/- 1 s)
  5. overlap according to TextGrid vs according to the channels
  6. where Nemotron 3 Diarization's "missed speech" (scored against the TextGrids) lies

Per-channel activity uses a level threshold halfway (in dB) between the channel's median level inside and
outside its labelled utterances (the labels calibrate levels only, not boundaries), 10 ms frames, 5-frame
smoothing, gaps < 0.2 s bridged, activity < 0.1 s dropped.

Usage:  python scripts/analyze_primock57.py [--hyp-dir <nemotron hyp dir>] [--out results/primock57]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diards.annotation import (  # noqa: E402
    Segment,
    intersect,
    merge_intervals,
    overlap_regions,
    read_rttm_single,
    subtract,
    total_duration,
)
from diards.audio import load_mono16k  # noqa: E402
from diards.config import raw_root, work_root  # noqa: E402
from diards.datasets.primock57 import channel_activity, read_textgrid  # noqa: E402
from diards.vad import HOP, frame_energy_db  # noqa: E402

ROLES = ("doctor", "patient")




def frames(ivs, n):
    m = np.zeros(n, bool)
    for a, b in ivs:
        m[int(a / HOP): int(b / HOP)] = True
    return m


def analyze(consult: str, raw: Path, hyp_dir: Path | None) -> dict:
    ch = {r: load_mono16k(raw / "audio" / f"{consult}_{r}.wav") for r in ROLES}
    e = {r: frame_energy_db(x) for r, x in ch.items()}
    n = min(len(v) for v in e.values())
    e = {r: v[:n] for r, v in e.items()}
    tg = {r: [(a, b) for a, b, _ in read_textgrid(raw / "repo" / "transcripts" / f"{consult}_{r}.TextGrid")] for r in ROLES}
    texts = {r: read_textgrid(raw / "repo" / "transcripts" / f"{consult}_{r}.TextGrid") for r in ROLES}
    out = {"consultation": consult, "duration_s": n * HOP}
    act = {}
    for r in ROLES:
        other = ROLES[1 - ROLES.index(r)]
        lab = frames(tg[r], n)
        lab_other = frames(tg[other], n)
        own_med = float(np.median(e[r][lab])) if lab.any() else float("nan")
        out_med = float(np.median(e[r][~lab])) if (~lab).any() else float("nan")
        act[r], thr = channel_activity(ch[r], tg[r])
        only_other = lab_other & ~lab
        lab_ivs = merge_intervals(tg[r])
        # 2. silence >= 0.3 s inside labelled utterances
        silent_inside = [(a, b) for a, b in subtract(lab_ivs, act[r]) if b - a >= 0.3]
        # 3. own-channel activity >= 0.5 s with no utterance within 0.25 s
        lab_pad = merge_intervals((a - 0.25, b + 0.25) for a, b in lab_ivs)
        unlabelled = [(a, b) for a, b in subtract(act[r], lab_pad) if b - a >= 0.5]
        # 4. boundary offsets
        starts, ends = [], []
        for a, b in tg[r]:
            inner = intersect(act[r], [(a - 1.0, b + 1.0)])
            if inner:
                starts.append(inner[0][0] - a)
                ends.append(b - inner[-1][1])
        long_utts = [(a, b, t) for a, b, t in texts[r] if b - a > 10]
        out[r] = {
            "level_own_speech_db": round(own_med, 1),
            "level_outside_db": round(out_med, 1),
            "level_when_only_other_speaks_db": round(float(np.median(e[r][only_other])), 1) if only_other.any() else None,
            "threshold_db": round(thr, 1),
            "labelled_s": round(total_duration(lab_ivs), 1),
            "active_s": round(total_duration(act[r]), 1),
            "silent_inside_labels_s": round(total_duration(silent_inside), 1),
            "silent_inside_labels_frac": round(total_duration(silent_inside) / max(1e-9, total_duration(lab_ivs)), 4),
            "active_outside_labels_s": round(total_duration(unlabelled), 1),
            "active_outside_labels_n": len(unlabelled),
            "active_outside_examples": [[round(a, 2), round(b, 2)] for a, b in sorted(unlabelled, key=lambda t: t[0] - t[1])[:5]],
            "start_offset_s": [round(x, 3) for x in starts],
            "end_offset_s": [round(x, 3) for x in ends],
            "utterances": len(tg[r]),
            "utterances_over_10s": len(long_utts),
            "longest_utterance_s": round(max((b - a for a, b in tg[r]), default=0.0), 1),
        }
    tg_segs = [Segment(a, b, r) for r in ROLES for a, b in tg[r]]
    act_segs = [Segment(a, b, r) for r in ROLES for a, b in act[r]]
    tg_speech = total_duration(merge_intervals((s.start, s.end) for s in tg_segs))
    act_speech = total_duration(merge_intervals((s.start, s.end) for s in act_segs))
    out["overlap_textgrid_s"] = round(total_duration(overlap_regions(tg_segs)), 1)
    out["overlap_channels_s"] = round(total_duration(overlap_regions(act_segs)), 1)
    out["speech_textgrid_s"] = round(tg_speech, 1)
    out["speech_channels_s"] = round(act_speech, 1)
    # 6. Nemotron misses vs TextGrid: how much of it is silent on the labelled speaker's own channel
    if hyp_dir is not None:
        hp = hyp_dir / f"primock57__{consult}.rttm"
        if hp.exists():
            hyp_sp = merge_intervals((s.start, s.end) for s in read_rttm_single(hp))
            missed = subtract(merge_intervals((s.start, s.end) for s in tg_segs), hyp_sp)
            silent_any = merge_intervals(
                [iv for r in ROLES for iv in subtract(merge_intervals(tg[r]), act[r])])
            silent_all = intersect(missed, silent_any)
            out["nemotron_missed_vs_textgrid_s"] = round(total_duration(missed), 1)
            out["nemotron_missed_where_channel_silent_s"] = round(total_duration(silent_all), 1)
    out["_activity"] = {r: [[round(a, 3), round(b, 3)] for a, b in act[r]] for r in ROLES}
    return out


def summarize(rows: list[dict]) -> dict:
    s = {}
    for r in ROLES:
        lab = sum(x[r]["labelled_s"] for x in rows)
        s[r] = {
            "labelled_h": round(lab / 3600, 2),
            "active_h": round(sum(x[r]["active_s"] for x in rows) / 3600, 2),
            "silent_inside_labels_frac": round(sum(x[r]["silent_inside_labels_s"] for x in rows) / lab, 4),
            "active_outside_labels_min": round(sum(x[r]["active_outside_labels_s"] for x in rows) / 60, 1),
            "active_outside_labels_n": sum(x[r]["active_outside_labels_n"] for x in rows),
            "median_level_own_db": round(float(np.median([x[r]["level_own_speech_db"] for x in rows])), 1),
            "median_level_other_db": round(float(np.median([x[r]["level_when_only_other_speaks_db"] for x in rows
                                                            if x[r]["level_when_only_other_speaks_db"] is not None])), 1),
            "start_offset_p50_s": round(float(np.median([v for x in rows for v in x[r]["start_offset_s"]])), 3),
            "end_offset_p50_s": round(float(np.median([v for x in rows for v in x[r]["end_offset_s"]])), 3),
            "start_offset_p90_abs_s": round(float(np.percentile(np.abs([v for x in rows for v in x[r]["start_offset_s"]]), 90)), 3),
            "end_offset_p90_abs_s": round(float(np.percentile(np.abs([v for x in rows for v in x[r]["end_offset_s"]]), 90)), 3),
            "utterances": sum(x[r]["utterances"] for x in rows),
            "utterances_over_10s": sum(x[r]["utterances_over_10s"] for x in rows),
        }
    s["speech_textgrid_h"] = round(sum(x["speech_textgrid_s"] for x in rows) / 3600, 2)
    s["speech_channels_h"] = round(sum(x["speech_channels_s"] for x in rows) / 3600, 2)
    s["overlap_textgrid_frac_of_speech"] = round(sum(x["overlap_textgrid_s"] for x in rows) / sum(x["speech_textgrid_s"] for x in rows), 4)
    s["overlap_channels_frac_of_speech"] = round(sum(x["overlap_channels_s"] for x in rows) / sum(x["speech_channels_s"] for x in rows), 4)
    if all("nemotron_missed_vs_textgrid_s" in x for x in rows):
        m = sum(x["nemotron_missed_vs_textgrid_s"] for x in rows)
        s["nemotron_missed_vs_textgrid_h"] = round(m / 3600, 2)
        s["nemotron_missed_where_channel_silent_frac"] = round(sum(x["nemotron_missed_where_channel_silent_s"] for x in rows) / m, 4)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=None)
    ap.add_argument("--hyp-dir", default=str(work_root() / "nemotron" / "primock57.mix" / "hyp"))
    ap.add_argument("--out", default="results/primock57")
    args = ap.parse_args()
    raw = raw_root(args.raw) / "primock57"
    consults = sorted({p.name.rsplit("_", 1)[0] for p in (raw / "repo" / "transcripts").glob("*.TextGrid")})
    hyp = Path(args.hyp_dir) if args.hyp_dir else None
    rows = [analyze(c, raw, hyp if hyp and hyp.exists() else None) for c in consults]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    act = {x["consultation"]: x.pop("_activity") for x in rows}
    summary = summarize(rows)
    (out / "primock57_audit.json").write_text(json.dumps({"summary": summary, "consultations": rows}, indent=1), encoding="utf-8")
    # channel-activity RTTMs (derived; PriMock57 is CC BY 4.0 so these can be shared)
    rdir = out / "channel_activity_rttm"
    rdir.mkdir(exist_ok=True)
    for c, a in act.items():
        lines = [f"SPEAKER primock57__{c} 1 {s:.3f} {e - s:.3f} <NA> <NA> {c}_{r} <NA> <NA>"
                 for r in ROLES for s, e in a[r]]
        (rdir / f"primock57__{c}.rttm").write_text("\n".join(sorted(lines, key=lambda l: float(l.split()[3]))) + "\n",
                                                  encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
