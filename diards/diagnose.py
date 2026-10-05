"""Attribute diarization errors to the model or to the reference, using the audio as an independent witness.

For every evaluated session (cached Nemotron hypotheses), speech-detection errors are split by what an energy VAD
says about the audio (close-talk view when the dataset has one, where energy means "someone near a mic is making
sound"). The level threshold is calibrated per session halfway (in dB) between the median frame energy inside and
outside the reference speech (the reference sets the levels only, never the boundaries); see
``diards.datasets.primock57.channel_activity``:

* **missed speech in silence**: the reference says speech, the model says none, and the audio is silent there
  (no energy within 0.1 s). Most likely padding or pauses inside reference segments, i.e. annotation looseness.
* **missed speech with energy**: the model missed audible sound the reference labels as speech. Most likely a
  model miss (or a non-speech sound such as a breath that the reference counts).
* **false alarm with energy**: the model says speech, the reference has none, the audio has energy. Either
  unlabelled speech in the reference or the model firing on noise/music. Listen to the examples to decide.
* **false alarm in silence**: the model says speech in silent audio: a model error (boundary overshoot).

Speaker confusion is left to the model. These are heuristics; the per-session JSON lists the longest regions of
each kind so they can be checked by ear.

Usage: python -m diards.diagnose <dataset> --view <hyp view> [--vad-view <view>] [--out results/diagnosis]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .annotation import intersect, merge_intervals, read_rttm_single, subtract, total_duration
from .audio import load_mono16k
from .config import work_root
from .core import NormalizedDataset
from .datasets.primock57 import channel_activity

CLOSE_TALK = {"ami": "ihm-mix", "icsi": "ihm-mix", "notsofar1": "ihm-mix", "chime6": "ihm-mix", "dipco": "ihm-mix",
              "libricss": "clean-mix"}


def diagnose(name: str, view: str | None = None, vad_view: str | None = None, root=None, out=None,
             hyp_dir=None, tol: float = 0.1) -> dict:
    ds = NormalizedDataset(name, root)
    view = view or ds.default_view
    vad_view = vad_view or CLOSE_TALK.get(name, view)
    if vad_view not in ds.views:
        vad_view = view
    hyp_dir = Path(hyp_dir) if hyp_dir else work_root() / "nemotron" / f"{name}.{view}" / "hyp"
    vad_audio = {s.session_id: s.audio_path for s in ds.sessions(view=vad_view)}
    rows = []
    tot = {k: 0.0 for k in ("ref", "miss", "miss_silent", "miss_energy", "fa", "fa_energy", "fa_silent")}
    for s in ds.sessions(view=view):
        hp = hyp_dir / f"{s.session_id}.rttm"
        if not hp.exists() or s.session_id not in vad_audio:
            continue
        uem = merge_intervals(s.uem)
        ref = intersect(merge_intervals((g.start, g.end) for g in s.segments), uem)
        hyp = intersect(merge_intervals((g.start, g.end) for g in read_rttm_single(hp)), uem)
        energy, _ = channel_activity(load_mono16k(vad_audio[s.session_id]), ref, fill=0.1, min_len=0.05)
        energy_pad = merge_intervals((a - tol, b + tol) for a, b in energy)
        miss = subtract(ref, hyp)
        fa = subtract(hyp, ref)
        r = {
            "session_id": s.session_id, "ref": total_duration(ref),
            "miss": total_duration(miss), "fa": total_duration(fa),
            "miss_silent": total_duration(subtract(miss, energy_pad)),
            "fa_energy": total_duration(intersect(fa, energy)),
        }
        r["miss_energy"] = r["miss"] - r["miss_silent"]
        r["fa_silent"] = r["fa"] - r["fa_energy"]
        r["examples_miss_silent"] = [[round(a, 2), round(b, 2)] for a, b in
                                     sorted(subtract(miss, energy_pad), key=lambda t: t[0] - t[1])[:5]]
        r["examples_fa_energy"] = [[round(a, 2), round(b, 2)] for a, b in
                                   sorted(intersect(fa, energy), key=lambda t: t[0] - t[1])[:5]]
        for k in tot:
            tot[k] += r[k]
        rows.append({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})
    ref = tot["ref"] or 1.0
    summary = {
        "dataset": name, "hyp_view": view, "vad_view": vad_view, "sessions": len(rows),
        "ref_speech_h": round(tot["ref"] / 3600, 2),
        "miss_pct": round(100 * tot["miss"] / ref, 2),
        "miss_in_silence_pct": round(100 * tot["miss_silent"] / ref, 2),
        "miss_with_energy_pct": round(100 * tot["miss_energy"] / ref, 2),
        "fa_pct": round(100 * tot["fa"] / ref, 2),
        "fa_with_energy_pct": round(100 * tot["fa_energy"] / ref, 2),
        "fa_in_silence_pct": round(100 * tot["fa_silent"] / ref, 2),
        "note": "speech-detection errors only (speaker-agnostic union of segments), % of reference speech time",
    }
    result = {"summary": summary, "sessions": rows}
    if out:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / f"diagnosis.{name}.{view}.json").write_text(json.dumps(result, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps(summary))
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset")
    ap.add_argument("--view")
    ap.add_argument("--vad-view")
    ap.add_argument("--root")
    ap.add_argument("--out", default="results/diagnosis")
    a = ap.parse_args()
    diagnose(a.dataset, a.view, a.vad_view, a.root, a.out)


if __name__ == "__main__":
    main()
