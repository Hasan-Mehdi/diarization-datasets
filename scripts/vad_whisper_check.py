"""Are the regions a VAD audit flags real annotation problems or VAD errors? Ask Whisper.

Reads ``results/vad/audit/audit.<dataset>.<view>.json`` (``python -m diards.vad_audit``) and transcribes, with
Whisper large-v3 (English, fp16 on GPU), the longest flagged regions of each VAD:

* ``unref``: the VAD hears speech where the reference has none. Intelligible words (same criterion as
  ``scripts/audit_false_alarms.py``: >= 3 words, not a known hallucination, not repetitive) = speech missing from
  the reference; no words = a VAD false alarm (noise, music, laughter, breathing) or unintelligible speech.
* ``unvoiced``: the reference has speech where the VAD hears none. Words = the VAD missed speech; no words =
  padding / a pause inside a segment / non-speech labelled as speech.
* ``control``: random >= 1 s stretches where both the reference and Silero (silero_x2) say non-speech, to measure how often
  this Whisper check itself reports speech in silence.

Usage: python scripts/vad_whisper_check.py <dataset> [--view V] [--vads silero,energy,webrtc] [--per-kind 20]
Output: results/vad/whisper/whisper.<dataset>.<view>.json
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import soundfile as sf  # noqa: E402

from audit_false_alarms import is_speech, words  # noqa: E402
from diards.annotation import intersect, merge_intervals, subtract  # noqa: E402
from diards.core import NormalizedDataset  # noqa: E402
from diards.vad_audit import AUDIT_VIEWS, dilate  # noqa: E402
from diards.vads import VadCache  # noqa: E402

_ASR = None


def asr():
    global _ASR
    if _ASR is None:
        import torch
        from transformers import pipeline

        _ASR = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3", dtype=torch.float16,
                        device="cuda" if torch.cuda.is_available() else "cpu")
    return _ASR


def transcribe(x, sr, a, b, pad: float = 0.1) -> str:
    seg = x[max(0, int((a - pad) * sr)): int((b + pad) * sr)]
    if len(seg) > 30 * sr:  # Whisper's window; long regions: first 30 s
        seg = seg[: 30 * sr]
    return asr()({"raw": seg, "sampling_rate": sr}, generate_kwargs={"language": "en", "task": "transcribe"})["text"].strip()


def controls(ds_name, view, sessions, n, seed=0, min_len=1.0, max_len=5.0):
    rng = random.Random(seed)
    cands = []
    for s in sessions:
        try:
            v = merge_intervals(VadCache.load(ds_name, view, s.session_id).silero(variant="x2"))
        except FileNotFoundError:
            continue
        uem = merge_intervals(s.uem)
        ref = merge_intervals((g.start, g.end) for g in s.segments)
        quiet = subtract(subtract(uem, dilate(ref, 0.5)), dilate(v, 0.5))
        cands += [(s.session_id, a, min(b, a + max_len)) for a, b in quiet if b - a >= min_len]
    rng.shuffle(cands)
    return cands[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("--view")
    ap.add_argument("--vads", default="silero_x2,energy,webrtc")
    ap.add_argument("--per-kind", type=int, default=20)
    ap.add_argument("--min-dur", type=float, default=1.0)
    ap.add_argument("--audit-dir", default=str(ROOT / "results" / "vad" / "audit"))
    ap.add_argument("--out", default=str(ROOT / "results" / "vad" / "whisper"))
    a = ap.parse_args()
    ds = NormalizedDataset(a.dataset)
    view = a.view or AUDIT_VIEWS.get(a.dataset, ds.default_view)
    audit = json.loads((Path(a.audit_dir) / f"audit.{a.dataset}.{view}.json").read_text(encoding="utf-8"))
    sessions = {s.session_id: s for s in ds.sessions(view=view)}
    todo = []  # (kind, vad, session, start, end, evidence)
    for vad in a.vads.split(","):
        for kind in ("unref", "unvoiced"):
            regs = [(r["session_id"], e) for r in audit["per_session"]
                    for e in r["refs"]["primary"].get(vad, {}).get(f"top_{kind}", []) if e["dur"] >= a.min_dur]
            regs.sort(key=lambda t: -t[1]["dur"])
            todo += [(kind, vad, sid, e["start"], e["end"], e) for sid, e in regs[: a.per_kind]]
    todo += [("control", "silero_x2", sid, st, en, {}) for sid, st, en in
             controls(a.dataset, view, list(sessions.values()), a.per_kind)]
    todo.sort(key=lambda t: (t[2], t[3]))
    out = {"dataset": a.dataset, "view": view, "regions": []}
    cache = {}
    for kind, vad, sid, st, en, ev in todo:
        if sid not in cache:
            cache.clear()
            cache[sid] = sf.read(str(sessions[sid].audio_path), dtype="float32")
        x, sr = cache[sid]
        text = transcribe(x, sr, st, en)
        out["regions"].append({"kind": kind, "vad": vad, "session_id": sid, "start": st, "end": en,
                               "dur": round(en - st, 2), "whisper": text, "words": len(words(text)),
                               "speech": is_speech(text), "evidence": ev})
    summ = {}
    for r in out["regions"]:
        k = f"{r['kind']}:{r['vad']}" if r["kind"] != "control" else "control"
        d = summ.setdefault(k, {"regions": 0, "with_speech": 0, "seconds": 0.0, "seconds_with_speech": 0.0})
        d["regions"] += 1
        d["with_speech"] += int(r["speech"])
        d["seconds"] = round(d["seconds"] + r["dur"], 2)
        d["seconds_with_speech"] = round(d["seconds_with_speech"] + r["dur"] * r["speech"], 2)
    out["summary"] = summ
    p = Path(a.out)
    p.mkdir(parents=True, exist_ok=True)
    (p / f"whisper.{a.dataset}.{view}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False),
                                                        encoding="utf-8", newline="\n")
    print(a.dataset, view, json.dumps(summ))


if __name__ == "__main__":
    main()
