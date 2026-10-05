"""How often does stock Silero VAD get stuck? Stock streaming probabilities vs the 30 s state-reset variant.

For every cached session (all datasets and views), compares speech decided by stock Silero (state never reset)
with ``silero_r30`` (state reset every 30 s, 2 s warm-up), both with the package's default post-processing.
A session counts as *stuck* when the reset variant finds at least 30 s more speech than the stock run and the
stock run has a >= 30 s stretch with no speech that the reset run fills by more than half.

Usage: python scripts/vad_reset_check.py [--out results/vad/reset_check.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from diards.annotation import intersect, merge_intervals, subtract, total_duration  # noqa: E402
from diards.vads import VadCache, study_root  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "results" / "vad" / "reset_check.json"))
    a = ap.parse_args()
    res = {}
    for d in sorted((study_root() / "vad").iterdir()):
        name, view = d.name.split(".", 1)
        acc = {"sessions": 0, "hours": 0.0, "stock_speech_h": 0.0, "reset_speech_h": 0.0, "disagree_h": 0.0,
               "stuck_sessions": [], "recovered_h": 0.0}
        for p in sorted(d.glob("*.npz")):
            if p.name.endswith(".pyannote.npz"):
                continue
            c = VadCache.from_path(p)
            if "silero_r30" not in c.data:
                continue
            dur = c.duration
            st, rs = merge_intervals(c.silero()), merge_intervals(c.silero(reset=True))
            acc["sessions"] += 1
            acc["hours"] += dur / 3600
            acc["stock_speech_h"] += total_duration(st) / 3600
            acc["reset_speech_h"] += total_duration(rs) / 3600
            only_r, only_s = subtract(rs, st), subtract(st, rs)
            acc["disagree_h"] += (total_duration(only_r) + total_duration(only_s)) / 3600
            gaps = [(x, y) for x, y in subtract([(0.0, dur)], st) if y - x >= 30]
            filled = [(x, y) for x, y in gaps if total_duration(intersect([(x, y)], rs)) > 0.5 * (y - x)]
            gain = total_duration(rs) - total_duration(st)
            if gain >= 30 and filled:
                rec = total_duration(intersect(filled, rs))
                acc["recovered_h"] += rec / 3600
                acc["stuck_sessions"].append({"session_id": p.stem, "duration_min": round(dur / 60, 1),
                                              "stock_speech_pct": round(100 * total_duration(st) / dur, 1),
                                              "reset_speech_pct": round(100 * total_duration(rs) / dur, 1),
                                              "recovered_s": round(rec, 1)})
        if not acc["sessions"]:
            continue
        acc["disagree_pct_of_audio"] = round(100 * acc["disagree_h"] / acc["hours"], 2)
        for k in ("hours", "stock_speech_h", "reset_speech_h", "disagree_h", "recovered_h"):
            acc[k] = round(acc[k], 3)
        acc["stuck_sessions"].sort(key=lambda r: -r["recovered_s"])
        res[d.name] = acc
        print(f"{d.name:26s} sessions {acc['sessions']:4d}  {acc['hours']:6.1f} h  speech stock {acc['stock_speech_h']:6.2f} h "
              f"reset {acc['reset_speech_h']:6.2f} h  disagree {acc['disagree_pct_of_audio']:5.2f}% of audio  "
              f"stuck sessions {len(acc['stuck_sessions']):3d} (recovered {acc['recovered_h'] * 60:5.1f} min)", flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
