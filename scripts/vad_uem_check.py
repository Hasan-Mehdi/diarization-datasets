"""Does any scored region (UEM) contain untranscribed speech before the first or after the last reference segment?

A whole-file UEM is only right if the transcription covers the whole file. For every session of every audited
dataset (audit view), this counts Silero (``silero_x2``) speech inside the UEM but more than 1 s before the first
or after the last reference segment, and lists sessions with >= 10 s of it. Such speech is scored as false alarm
for any diarizer; the fix is to cut the UEM to the transcribed span (or to transcribe the tail).

Usage: python scripts/vad_uem_check.py [--out results/vad/uem_check.json]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from diards.annotation import intersect, merge_intervals, total_duration  # noqa: E402
from diards.config import normalized_root  # noqa: E402
from diards.core import NormalizedDataset  # noqa: E402
from diards.vad_audit import AUDIT_VIEWS  # noqa: E402
from diards.vads import VadCache, cache_path  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-s", type=float, default=10.0)
    ap.add_argument("--out", default=str(ROOT / "results" / "vad" / "uem_check.json"))
    a = ap.parse_args()
    res = {}
    for name in sorted(os.listdir(normalized_root())):
        ds = NormalizedDataset(name)
        view = AUDIT_VIEWS.get(name, ds.default_view)
        flagged, tot_head, tot_tail, n = [], 0.0, 0.0, 0
        for s in ds.sessions(view=view):
            if not cache_path(name, view, s.session_id).exists():
                continue
            segs = s.segments
            if not segs:
                continue
            n += 1
            uem = merge_intervals(s.uem)
            first, last = min(g.start for g in segs), max(g.end for g in segs)
            sp = intersect(merge_intervals(VadCache.load(name, view, s.session_id).silero(variant="x2")), uem)
            head = total_duration(intersect(sp, [(0.0, max(0.0, first - 1.0))]))
            tail = total_duration(intersect(sp, [(last + 1.0, float("inf"))]))
            tot_head += head
            tot_tail += tail
            if head + tail >= a.min_s:
                flagged.append({"session_id": s.session_id, "split": s.split, "duration": round(s.duration, 1),
                                "uem": [[round(x, 2), round(y, 2)] for x, y in uem],
                                "first_ref_start": round(first, 2), "last_ref_end": round(last, 2),
                                "silero_speech_before_s": round(head, 1), "silero_speech_after_s": round(tail, 1)})
        flagged.sort(key=lambda r: -(r["silero_speech_before_s"] + r["silero_speech_after_s"]))
        res[name] = {"view": view, "sessions": n, "speech_before_first_ref_s": round(tot_head, 1),
                     "speech_after_last_ref_s": round(tot_tail, 1), "sessions_flagged": len(flagged),
                     "flagged": flagged}
        print(f"{name:18s} sessions {n:4d}  Silero speech outside the transcribed span: before {tot_head:7.1f} s, "
              f"after {tot_tail:7.1f} s; sessions >= {a.min_s:.0f} s: {len(flagged)}"
              + (f"  worst: {flagged[0]['session_id']} ({flagged[0]['silero_speech_before_s'] + flagged[0]['silero_speech_after_s']:.0f} s)"
                 if flagged else ""), flush=True)
    Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
