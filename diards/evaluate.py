"""Run NVIDIA Nemotron 3 Diarization on normalized sessions and score it.

Inference uses the Hugging Face Transformers port of ``nvidia/Nemotron-3-Diarization`` in *offline* mode: the
model chunks the recording itself with chunk_length=340, chunk_right_context=40, fifo_length=40,
speaker_cache_update_period=300, speaker_cache_length=264 (80 ms frames), i.e. exactly the "very high latency
(30.4 s)" configuration of the model card. Frame probabilities are thresholded at 0.5 with no other
post-processing (same as ``processor.extract_speaker_dict``).

Outputs (under ``--out``, default ``<work>/nemotron/<dataset>.<view>``):
  hyp/<session>.rttm        hypotheses
  probs/<session>.npz       float16 speaker probabilities at 10 ms (for later analysis)
  results.json / results.md per-session and overall DER/JER at collar 0 and 0.25 s (+ alternative references)
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from .annotation import Segment, read_rttm_single, write_rttm
from .config import work_root
from .core import NormalizedDataset, Session
from .score import Scorer

COLLARS = (0.0, 0.25)
DEFAULT_MODEL = "nvidia/Nemotron-3-Diarization"


class NemotronDiarizer:
    def __init__(self, model_id: str = DEFAULT_MODEL, device: str = "cuda", dtype: str = "float32"):
        import torch
        from transformers import AutoModelForAudioFrameClassification, AutoProcessor

        self.torch = torch
        self.model_id = model_id
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForAudioFrameClassification.from_pretrained(
            model_id, device_map=device, dtype=getattr(torch, dtype))
        self.model.eval()
        self.sr = self.processor.feature_extractor.sampling_rate
        self.frame = self.processor.feature_extractor.hop_length / self.sr
        cfg = self.model.config
        self.config = {k: getattr(cfg, k, None) for k in
                       ("chunk_length", "chunk_right_context", "fifo_length", "speaker_cache_update_period")}
        self.config["speaker_cache_length"] = getattr(cfg.streaming_config, "speaker_cache_length", None)
        self.config["dtype"] = dtype
        try:
            from huggingface_hub import model_info

            self.revision = model_info(model_id).sha
        except Exception:
            self.revision = None

    def probs(self, audio: np.ndarray) -> np.ndarray:
        torch = self.torch
        inputs = self.processor(audio, sampling_rate=self.sr)
        inputs = inputs.to(self.model.device, dtype=self.model.dtype)
        with torch.inference_mode():
            logits = self.model(**inputs).logits
        return logits[0].float().sigmoid().cpu().numpy()

    def segments(self, probs: np.ndarray, threshold: float = 0.5) -> list[Segment]:
        active = probs > threshold
        segs = []
        pad = np.zeros((1, active.shape[1]), dtype=bool)
        d = np.diff(np.concatenate([pad, active, pad]).astype(np.int8), axis=0)
        for spk in range(active.shape[1]):
            starts = np.flatnonzero(d[:, spk] == 1)
            ends = np.flatnonzero(d[:, spk] == -1)
            segs += [Segment(round(a * self.frame, 2), round(b * self.frame, 2), f"spk{spk}") for a, b in zip(starts, ends)]
        return sorted(segs)


def select_sessions(sessions: list[Session], splits=None, limit=None, max_hours=None, ids=None) -> list[Session]:
    if ids:
        wanted = set(ids)
        return [s for s in sessions if s.session_id in wanted or s.original_id in wanted]
    if splits:
        sessions = [s for s in sessions if s.split in splits]
    # deterministic but well-mixed order
    sessions = sorted(sessions, key=lambda s: hashlib.md5(s.session_id.encode()).hexdigest())
    out, hours = [], 0.0
    for s in sessions:
        if limit and len(out) >= limit:
            break
        if max_hours and hours >= max_hours:
            break
        out.append(s)
        hours += s.duration / 3600
    return sorted(out, key=lambda s: s.session_id)


def evaluate_dataset(name: str, root=None, view=None, splits=None, limit=None, max_hours=None,
                     model_id: str = DEFAULT_MODEL, out=None, sessions=None, diarizer=None,
                     save_probs: bool = True) -> dict:
    ds = NormalizedDataset(name, root)
    view = view or ds.default_view
    chosen = select_sessions(ds.sessions(view=view), splits, limit, max_hours, sessions)
    if not chosen:
        raise SystemExit(f"no sessions selected for {name}/{view}")
    out = Path(out) if out else work_root() / "nemotron" / f"{name}.{view}"
    (out / "hyp").mkdir(parents=True, exist_ok=True)
    (out / "probs").mkdir(parents=True, exist_ok=True)
    dz = diarizer or NemotronDiarizer(model_id)
    variants = sorted({k for s in chosen for k in s.alt_rttm})
    scorers = {(ref, c): Scorer(c) for ref in ["primary", *variants] for c in COLLARS}
    rows = []
    t_audio = t_proc = 0.0
    for s in chosen:
        hyp_path = out / "hyp" / f"{s.session_id}.rttm"
        prob_path = out / "probs" / f"{s.session_id}.npz"
        if hyp_path.exists():
            hyp = read_rttm_single(hyp_path)
            proc = None
        else:
            x, sr = sf.read(str(s.audio_path), dtype="float32")
            assert sr == 16000, sr
            t0 = time.time()
            p = dz.probs(x)
            proc = time.time() - t0
            t_proc += proc
            t_audio += len(x) / sr
            hyp = dz.segments(p)
            write_rttm(hyp_path, s.session_id, hyp)
            if save_probs:
                np.savez_compressed(prob_path, probs=p.astype(np.float16), frame_s=dz.frame)
        row = {"session_id": s.session_id, "split": s.split, "duration": s.duration,
               "ref_speakers": s.num_speakers, "hyp_speakers": len({h.speaker for h in hyp}),
               "overlap_ratio": s.overlap_ratio, "rtfx": round(s.duration / proc, 1) if proc else None}
        uem = s.uem
        for ref_name in ["primary", *variants]:
            if ref_name != "primary" and ref_name not in s.alt_rttm:
                continue
            ref = s.segments if ref_name == "primary" else s.alt_segments(ref_name)
            for c in COLLARS:
                r = scorers[(ref_name, c)](s.session_id, ref, hyp, uem)
                key = f"{ref_name}@{c}"
                row[key] = {k: round(v, 4) for k, v in r.items()}
        rows.append(row)
        prim = row["primary@0.0"]
        print(f"  [eval] {s.session_id}: DER {100 * prim['der']:.2f} (FA {100 * prim['fa']:.1f} MISS {100 * prim['miss']:.1f} "
              f"CONF {100 * prim['conf']:.1f}) JER {100 * prim['jer']:.1f} spk ref/hyp {row['ref_speakers']}/{row['hyp_speakers']}",
              flush=True)
    summary = {}
    for (ref_name, c), sc in scorers.items():
        if sc.der.accumulated_.get("total", 0):
            summary[f"{ref_name}@{c}"] = {k: round(v, 4) for k, v in sc.summary().items()}
    n = len(rows)
    sca = sum(1 for r in rows if r["ref_speakers"] == r["hyp_speakers"]) / n
    mae = sum(abs(r["ref_speakers"] - r["hyp_speakers"]) for r in rows) / n
    result = {
        "dataset": name, "view": view, "model": dz.model_id, "model_revision": dz.revision,
        "inference": {"implementation": "transformers (offline mode)", **dz.config, "threshold": 0.5,
                      "postprocessing": "none (threshold only)"},
        "scoring": {"tool": "pyannote.metrics", "collars_half_width_s": list(COLLARS), "overlap": "included",
                    "uem": "per-session UEM from the normalized dataset"},
        "sessions": n, "hours": round(sum(r["duration"] for r in rows) / 3600, 2),
        "speaker_count_accuracy": round(sca, 4), "speaker_count_mae": round(mae, 4),
        "rtfx_overall": round(t_audio / t_proc, 1) if t_proc else None,
        "summary": summary, "per_session": rows,
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(),
                        "gpu": _gpu_name()},
        "command": "python -m diards " + " ".join(sys.argv[1:]) if sys.argv and sys.argv[0].endswith("__main__.py") else None,
    }
    (out / "results.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    (out / "results.md").write_text(results_markdown(result), encoding="utf-8")
    print(results_markdown(result))
    return result


def _gpu_name():
    try:
        import torch

        return torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
    except Exception:
        return None


def results_markdown(r: dict) -> str:
    lines = [f"# Nemotron 3 Diarization on {r['dataset']} (view: {r['view']})", "",
             f"- model: `{r['model']}` (revision {r['model_revision']}); {r['inference']['implementation']}, "
             f"chunk {r['inference'].get('chunk_length')} / right ctx {r['inference'].get('chunk_right_context')} / "
             f"fifo {r['inference'].get('fifo_length')} / update {r['inference'].get('speaker_cache_update_period')} / "
             f"spk cache {r['inference'].get('speaker_cache_length')}, threshold 0.5",
             f"- sessions: {r['sessions']} ({r['hours']} h); speaker-count accuracy {100 * r['speaker_count_accuracy']:.1f}%, "
             f"MAE {r['speaker_count_mae']:.2f}; RTFx {r['rtfx_overall']}",
             "- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds", "",
             "| reference | collar | DER % | FA % | Miss % | Conf % | JER % | ref speech h |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for key, v in r["summary"].items():
        ref, c = key.split("@")
        lines.append(f"| {ref} | {c} | {100 * v['der']:.2f} | {100 * v['fa']:.2f} | {100 * v['miss']:.2f} | "
                     f"{100 * v['conf']:.2f} | {100 * v['jer']:.2f} | {v['ref_speech_h']:.2f} |")
    lines += ["", "Per session (primary reference, collar 0):", "",
              "| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in r["per_session"]:
        p = row["primary@0.0"]
        lines.append(f"| {row['session_id']} | {row['split']} | {row['duration'] / 60:.1f} | {row['ref_speakers']} | "
                     f"{row['hyp_speakers']} | {row['overlap_ratio']:.3f} | {100 * p['der']:.2f} | {100 * p['fa']:.2f} | "
                     f"{100 * p['miss']:.2f} | {100 * p['conf']:.2f} | {100 * p['jer']:.2f} |")
    return "\n".join(lines) + "\n"
