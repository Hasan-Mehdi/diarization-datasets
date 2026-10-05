"""How often does Silero VAD go silent over clear speech? Stock streaming vs state-reset variants.

Silero's per-frame output depends on its recurrent state. On some recordings (telephone speech in particular) the
model is bistable: the same stretch of clear speech gets probabilities near 1 or near 0 depending on where the
stream started. This script measures that failure on the sessions Nemotron was evaluated on, using two independent
witnesses: a 10 s window is a *clear-speech window* when Nemotron's speech covers >= 50% of it and WebRTC VAD
(mode 3, the strictest) fires on >= 50% of its frames; Silero *drops out* on such a window when its maximum
probability in the window is < 0.2. Compared variants (all from the cache):

* ``stock``: the streaming loop as ``silero_vad.get_speech_timestamps`` runs it (state never reset);
* ``r30``: state reset every 30 s with a 2 s warm-up;
* ``max``: frame-wise maximum of the two (two different state histories).

It also reports, for all cached sessions, how much speech each variant finds.

Usage: python scripts/vad_reset_check.py [--out results/vad/reset_check.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from diards.annotation import merge_intervals, total_duration  # noqa: E402
from diards.vad_assist import RESULTS, hyp_dir, parse_tag, tag_sessions  # noqa: E402
from diards.vads import SILERO_HOP, WEBRTC_HOP, VadCache, nemotron_intervals, silero_intervals, to_raster  # noqa: E402

WIN = 10.0


def dropouts(probs: np.ndarray, webrtc: np.ndarray, nem_ivs, duration: float) -> tuple[int, int, list]:
    n = int(duration // WIN)
    nem = to_raster(nem_ivs, int(duration / 0.01) + 1, 0.01)
    clear, drop, where = 0, 0, []
    for i in range(n):
        a, b = i * WIN, (i + 1) * WIN
        w = (webrtc[int(a / WEBRTC_HOP): int(b / WEBRTC_HOP)] >> 3) & 1
        if nem[int(a / 0.01): int(b / 0.01)].mean() < 0.5 or not len(w) or w.mean() < 0.5:
            continue
        clear += 1
        p = probs[int(a / SILERO_HOP): int(b / SILERO_HOP)]
        if len(p) and p.max() < 0.2:
            drop += 1
            where.append(a)
    return clear, drop, where


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "results" / "vad" / "reset_check.json"))
    a = ap.parse_args()
    res = {}
    tags = sorted(p.name for p in RESULTS.iterdir() if (p / "results.json").exists())
    for tag in tags:
        name, view = parse_tag(tag)
        try:
            sessions = tag_sessions(tag)
            caches = {s.session_id: VadCache.load(name, view, s.session_id) for s in sessions}
        except FileNotFoundError:
            print(f"{tag}: cache incomplete, skipped", flush=True)
            continue
        acc = {"sessions": len(sessions), "hours": 0.0, "clear_windows": 0, "speech_h": {}, "dropout_windows": {},
               "worst_sessions": {}}
        for v in ("stock", "r30", "max"):
            acc["dropout_windows"][v] = 0
            acc["speech_h"][v] = 0.0
            acc["worst_sessions"][v] = []
        for s in sessions:
            c = caches[s.session_id]
            dur = c.duration
            acc["hours"] += dur / 3600
            nem = nemotron_intervals(hyp_dir(tag) / "hyp" / f"{s.session_id}.rttm")
            p0, p1 = c.data["silero"].astype(np.float32), c.data["silero_r30"].astype(np.float32)
            n_samples = int(c.data["n_samples"])
            first = True
            for v, p in (("stock", p0), ("r30", p1), ("max", np.maximum(p0, p1))):
                clear, drop, where = dropouts(p, c.data["webrtc"], nem, dur)
                if first:
                    acc["clear_windows"] += clear
                    first = False
                acc["dropout_windows"][v] += drop
                acc["speech_h"][v] += total_duration(merge_intervals(silero_intervals(p, n_samples))) / 3600
                if drop:
                    acc["worst_sessions"][v].append((s.session_id, drop, [round(t) for t in where[:5]]))
        for v in acc["worst_sessions"]:
            acc["worst_sessions"][v] = sorted(acc["worst_sessions"][v], key=lambda t: -t[1])[:5]
        cw = acc["clear_windows"] or 1
        acc["dropout_pct"] = {v: round(100 * d / cw, 2) for v, d in acc["dropout_windows"].items()}
        acc["hours"] = round(acc["hours"], 2)
        acc["speech_h"] = {v: round(x, 2) for v, x in acc["speech_h"].items()}
        res[tag] = acc
        print(f"{tag:26s} {acc['hours']:6.1f} h  clear-speech windows {acc['clear_windows']:5d}  Silero drop-outs: "
              + "  ".join(f"{v} {acc['dropout_windows'][v]} ({acc['dropout_pct'][v]}%)" for v in ("stock", "r30", "max")),
              flush=True)
    tot = {v: sum(r["dropout_windows"][v] for r in res.values()) for v in ("stock", "r30", "max")}
    cw = sum(r["clear_windows"] for r in res.values())
    out = {"definition": __doc__.split("Usage:")[0].strip(), "total_clear_windows": cw,
           "total_dropout_windows": tot, "total_dropout_pct": {v: round(100 * d / max(cw, 1), 3) for v, d in tot.items()},
           "per_tag": res}
    print("TOTAL", json.dumps(out["total_dropout_pct"]), "of", cw, "clear-speech windows")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
