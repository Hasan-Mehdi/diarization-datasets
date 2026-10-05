"""Are reference timestamps shifted against the audio? Lag search between reference and model speech activity.

For each session, speech activity (speaker-agnostic union) of the reference and of the cached Nemotron hypothesis
is rasterised at 50 ms. The agreement (frames where both say speech or both say silence) is computed for lags
from -max_lag to +max_lag seconds. A best lag far from 0 with a clear gain means the reference is offset in time
(a labelling/conversion error), something DER alone cannot distinguish from missed speech plus false alarms.

Usage: python scripts/check_offsets.py <dataset> [--view V] [--max-lag 5]
Output: results/diagnosis/offsets.<dataset>.<view>.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diards.annotation import merge_intervals, read_rttm_single  # noqa: E402
from diards.config import work_root  # noqa: E402
from diards.core import NormalizedDataset  # noqa: E402

STEP = 0.05


def raster(ivs, n):
    m = np.zeros(n, bool)
    for a, b in ivs:
        m[int(a / STEP): int(b / STEP)] = True
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--view")
    ap.add_argument("--max-lag", type=float, default=5.0)
    a = ap.parse_args()
    ds = NormalizedDataset(a.dataset)
    view = a.view or ds.default_view
    hyp_dir = work_root() / "nemotron" / f"{a.dataset}.{view}" / "hyp"
    rows = []
    lags = np.arange(-a.max_lag, a.max_lag + 1e-9, STEP)
    for s in ds.sessions(view=view):
        hp = hyp_dir / f"{s.session_id}.rttm"
        if not hp.exists():
            continue
        n = int(s.duration / STEP) + 1
        ref = raster(merge_intervals((g.start, g.end) for g in s.segments), n)
        hyp = raster(merge_intervals((g.start, g.end) for g in read_rttm_single(hp)), n)
        agree = []
        for lag in lags:
            k = int(round(lag / STEP))
            # shift the reference by +lag seconds (reference too early -> positive best lag)
            if k >= 0:
                r, h = ref[: n - k], hyp[k:]
            else:
                r, h = ref[-k:], hyp[: n + k]
            agree.append(float(np.mean(r == h)) if len(r) else 0.0)
        agree = np.array(agree)
        i0 = int(np.argmin(np.abs(lags)))
        ib = int(np.argmax(agree))
        rows.append({"session_id": s.session_id, "best_lag_s": round(float(lags[ib]), 2),
                     "agreement_at_0": round(float(agree[i0]), 4), "agreement_best": round(float(agree[ib]), 4),
                     "gain": round(float(agree[ib] - agree[i0]), 4)})
    shifted = [r for r in rows if abs(r["best_lag_s"]) >= 0.3 and r["gain"] >= 0.02]
    out = {"dataset": a.dataset, "view": view, "sessions": len(rows),
           "median_abs_best_lag_s": round(float(np.median([abs(r["best_lag_s"]) for r in rows])), 3) if rows else None,
           "sessions_shifted": len(shifted),
           "criterion": "|best lag| >= 0.3 s and agreement gain >= 2 points",
           "shifted": sorted(shifted, key=lambda r: -r["gain"]), "all": rows}
    p = Path("results/diagnosis") / f"offsets.{a.dataset}.{view}.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")
    print(f"{a.dataset}/{view}: {len(shifted)}/{len(rows)} sessions look time-shifted; median |best lag| "
          f"{out['median_abs_best_lag_s']} s; worst: " + ", ".join(f"{r['session_id']} ({r['best_lag_s']:+.2f} s, "
                                                                   f"+{100 * r['gain']:.1f} pts)" for r in out["shifted"][:5]))


if __name__ == "__main__":
    main()
