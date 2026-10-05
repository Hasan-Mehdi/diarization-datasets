"""Data preparation with a VAD: how much silence could be trimmed, and could a VAD write the UEMs?

Per dataset (audit view, all sessions), from the cached Silero VAD with the 30 s state reset (``silero_r30``):

* non-speech time in stretches longer than 1 / 2 / 5 s, and the audio kept by ``diards.vad_assist.trim_plan``
  (stretches > 1 s shortened to 0.5 s), i.e. how much shorter the audio fed to a diarizer would be;
* leading / trailing non-speech (before the first and after the last VAD speech);
* for datasets whose official UEM is not the whole file: how well a VAD-derived UEM (first VAD speech - 1 s ..
  last VAD speech + 1 s) reproduces it, and how much VAD speech / reference speech lies outside the official UEM.

Usage: python scripts/vad_dataprep.py [dataset ...] [--out results/vad/dataprep.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from diards.annotation import intersect, merge_intervals, subtract, total_duration  # noqa: E402
from diards.config import normalized_root  # noqa: E402
from diards.core import NormalizedDataset  # noqa: E402
from diards.vad_assist import trim_plan, uem_span  # noqa: E402
from diards.vad_audit import AUDIT_VIEWS  # noqa: E402
from diards.vads import VadCache, cache_path  # noqa: E402


def dataset_prep(name: str) -> dict:
    ds = NormalizedDataset(name)
    view = AUDIT_VIEWS.get(name, ds.default_view)
    acc = {k: 0.0 for k in ("dur", "speech", "sil_gt1", "sil_gt2", "sil_gt5", "kept", "lead", "trail")}
    uem_rows = []
    n = 0
    for s in ds.sessions(view=view):
        if not cache_path(name, view, s.session_id).exists():
            continue
        n += 1
        c = VadCache.load(name, view, s.session_id)
        dur = c.duration
        sp = merge_intervals(c.silero(reset=True))
        sil = subtract([(0.0, dur)], sp)
        acc["dur"] += dur
        acc["speech"] += total_duration(sp)
        for k, t in (("sil_gt1", 1), ("sil_gt2", 2), ("sil_gt5", 5)):
            acc[k] += total_duration([(a, b) for a, b in sil if b - a > t])
        acc["kept"] += total_duration(trim_plan(sp, dur))
        if sp:
            acc["lead"] += sp[0][0]
            acc["trail"] += dur - sp[-1][1]
        uem = merge_intervals(s.uem)
        if abs(total_duration(uem) - dur) > 1.0:
            ref = merge_intervals((g.start, g.end) for g in s.segments)
            vu = uem_span([(0.0, dur)], sp)
            uem_rows.append({
                "session_id": s.session_id, "duration": round(dur, 2),
                "official_uem": [[round(a, 2), round(b, 2)] for a, b in uem],
                "vad_uem": [[round(a, 2), round(b, 2)] for a, b in vu],
                "start_diff_s": round(vu[0][0] - uem[0][0], 2) if vu else None,
                "end_diff_s": round(vu[-1][1] - uem[-1][1], 2) if vu else None,
                "vad_speech_outside_uem_s": round(total_duration(subtract(sp, uem)), 2),
                "ref_speech_outside_uem_s": round(total_duration(subtract(ref, uem)), 2),
                "ref_speech_outside_vad_uem_s": round(total_duration(subtract(intersect(ref, uem), vu)), 2),
            })
    d = acc["dur"] or 1.0
    out = {"dataset": name, "view": view, "sessions": n, "hours": round(acc["dur"] / 3600, 2),
           "silero_speech_pct": round(100 * acc["speech"] / d, 1),
           "nonspeech_gt1s_pct": round(100 * acc["sil_gt1"] / d, 1),
           "nonspeech_gt2s_pct": round(100 * acc["sil_gt2"] / d, 1),
           "nonspeech_gt5s_pct": round(100 * acc["sil_gt5"] / d, 1),
           "trimmed_audio_pct_of_original": round(100 * acc["kept"] / d, 1),
           "leading_nonspeech_s_mean": round(acc["lead"] / max(n, 1), 1),
           "trailing_nonspeech_s_mean": round(acc["trail"] / max(n, 1), 1)}
    if uem_rows:
        sd = np.array([abs(r["start_diff_s"]) for r in uem_rows if r["start_diff_s"] is not None])
        ed = np.array([abs(r["end_diff_s"]) for r in uem_rows if r["end_diff_s"] is not None])
        out["non_trivial_uems"] = {
            "sessions": len(uem_rows),
            "median_abs_start_diff_s": round(float(np.median(sd)), 2) if len(sd) else None,
            "median_abs_end_diff_s": round(float(np.median(ed)), 2) if len(ed) else None,
            "within_2s_both_ends": int(sum(1 for r in uem_rows if r["start_diff_s"] is not None
                                           and abs(r["start_diff_s"]) <= 2 and abs(r["end_diff_s"]) <= 2)),
            "vad_speech_outside_official_uem_h": round(sum(r["vad_speech_outside_uem_s"] for r in uem_rows) / 3600, 3),
            "ref_speech_outside_official_uem_h": round(sum(r["ref_speech_outside_uem_s"] for r in uem_rows) / 3600, 3),
            "ref_speech_outside_vad_uem_s": round(sum(r["ref_speech_outside_vad_uem_s"] for r in uem_rows), 1),
            "per_session": uem_rows,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("datasets", nargs="*")
    ap.add_argument("--out", default=str(ROOT / "results" / "vad" / "dataprep.json"))
    a = ap.parse_args()
    names = a.datasets or sorted(os.listdir(normalized_root()))
    res = {}
    for name in names:
        res[name] = dataset_prep(name)
        r = res[name]
        print(f"{name:18s} {r['hours']:6.1f} h  speech {r['silero_speech_pct']:5.1f}%  non-speech>1s {r['nonspeech_gt1s_pct']:5.1f}%  "
              f">5s {r['nonspeech_gt5s_pct']:5.1f}%  trimmed audio {r['trimmed_audio_pct_of_original']:5.1f}%"
              + (f"  UEMs: {r['non_trivial_uems']['within_2s_both_ends']}/{r['non_trivial_uems']['sessions']} within 2 s"
                 if "non_trivial_uems" in r else ""), flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
