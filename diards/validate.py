"""Ground-truth validator.

Two layers:

1. ``raw_label_issues`` runs on the *original* segments while a recipe normalizes them (results are stored in
   the manifest as ``label_issues``), so problems that normalization silently fixes (same-speaker overlaps,
   duplicates, zero/negative durations, segments past the end of the audio) are still reported.
2. ``validate_session`` / ``validate_dataset`` check the normalized files themselves (audio format and duration,
   RTTM/UEM consistency, speakers, words vs. segments) and, with ``vad=True``, compare reference speech with a
   simple energy VAD to find possibly unannotated speech and over-long reference segments.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np

from .annotation import (
    Segment,
    intersect,
    merge_intervals,
    speech_regions,
    subtract,
    total_duration,
)
from .audio import audio_info, load_mono16k
from .core import NormalizedDataset, Session

PLACEHOLDER = re.compile(r"^(unk|unknown|\?+|na|n/a|none|x+|spk\?|noise|music|overlap)$", re.I)


def raw_label_issues(segments: list[Segment], duration: float | None = None, tol: float = 0.05) -> dict:
    """Count label problems in the original segment list (before same-speaker merging)."""
    issues: Counter = Counter()
    examples: dict[str, list] = {}

    def add(code, seg):
        issues[code] += 1
        if len(examples.setdefault(code, [])) < 3:
            examples[code].append([round(seg.start, 3), round(seg.end, 3), seg.speaker])

    seen = set()
    by_spk: dict[str, list[Segment]] = {}
    for s in segments:
        if s.end < s.start:
            add("negative_duration", s)
        elif s.end == s.start:
            add("zero_duration", s)
        if s.start < 0:
            add("negative_start", s)
        if duration is not None and s.end > duration + tol:
            add("beyond_audio_end", s)
        key = (round(s.start, 3), round(s.end, 3), s.speaker)
        if key in seen:
            add("duplicate_segment", s)
        seen.add(key)
        by_spk.setdefault(s.speaker, []).append(s)
    for spk, segs in by_spk.items():
        segs.sort()
        for a, b in zip(segs, segs[1:]):
            if b.start < a.end - 1e-6 and (round(a.start, 3), round(a.end, 3)) != (round(b.start, 3), round(b.end, 3)):
                add("same_speaker_overlap", b)
    lower = Counter(s.lower() for s in by_spk)
    for spk in by_spk:
        if lower[spk.lower()] > 1:
            issues["speaker_case_variants"] += 1
        if PLACEHOLDER.match(spk.split("_")[-1]):
            issues["placeholder_speaker_label"] += 1
            examples.setdefault("placeholder_speaker_label", []).append(spk)
    if duration is not None:
        past = sum(max(0.0, s.end - max(duration, s.start)) for s in segments if s.end > duration + tol)
        if past:
            issues["seconds_beyond_audio_end"] = round(past, 3)
    out = {k: v for k, v in issues.items() if v}
    if examples:
        out["examples"] = {k: v for k, v in examples.items() if k in out}
    return out


def _issue(level, code, msg, **kw):
    d = {"level": level, "code": code, "message": msg}
    d.update(kw)
    return d


def silero_x2_intervals(s: Session, x=None) -> tuple[list[tuple[float, float]], dict]:
    """Silero VAD "x2" (frame-wise max of a stock run and a run with the state reset every 30 s; see
    docs/silero_vad_study.md). Uses the VAD-study cache when it exists, otherwise computes on CPU."""
    import numpy as np

    from . import vads

    try:
        cache = vads.VadCache.load(s.dataset, s.view, s.session_id)
        return cache.silero(variant="x2"), {"backend": "silero_x2", "source": "cache"}
    except Exception:
        pass
    if x is None:
        x = load_mono16k(s.audio_path)
    p = np.maximum(vads.silero_probs(x), vads.silero_probs(x, reset_every=30.0))
    return vads.silero_intervals(p, len(x)), {"backend": "silero_x2", "source": "computed"}


def validate_session(s: Session, vad: bool = False, vad_tolerance: float = 0.25, vad_backend: str = "energy") -> dict:
    issues = []
    metrics: dict = {}
    # ---- audio
    if not s.audio_path or not s.audio_path.exists():
        issues.append(_issue("error", "audio_missing", f"{s.audio_path} missing"))
        return {"session_id": s.session_id, "issues": issues, "metrics": metrics}
    info = audio_info(s.audio_path)
    if info["sample_rate"] != 16000 or info["channels"] != 1 or info["subtype"] != "PCM_16":
        issues.append(_issue("error", "audio_format", f"audio is {info}"))
    if abs(info["duration"] - s.duration) > 0.02:
        issues.append(_issue("error", "duration_mismatch", f"manifest {s.duration} vs audio {info['duration']:.3f}"))
    dur = info["duration"]
    # ---- rttm
    try:
        segs = s.segments
    except Exception as exc:
        issues.append(_issue("error", "rttm_parse", str(exc)))
        return {"session_id": s.session_id, "issues": issues, "metrics": metrics}
    file_ids = set()
    for line in s.rttm_path.read_text(encoding="utf-8").splitlines():
        p = line.split()
        if p and p[0] == "SPEAKER":
            file_ids.add(p[1])
    if file_ids and file_ids != {s.session_id}:
        issues.append(_issue("error", "rttm_file_id", f"RTTM file ids {sorted(file_ids)} != {s.session_id}"))
    if not segs:
        issues.append(_issue("error", "empty_reference", "no reference segments"))
    for code, n in raw_label_issues(segs, dur).items():
        if code != "examples":
            issues.append(_issue("error", f"normalized_{code}", f"{n} in normalized RTTM"))
    # ---- uem
    uem = s.uem
    if not uem:
        issues.append(_issue("error", "uem_missing", "empty UEM"))
        uem = [(0.0, dur)]
    for a, b in uem:
        if a < 0 or b > dur + 0.02 or b <= a:
            issues.append(_issue("error", "uem_range", f"UEM region ({a}, {b}) outside audio [0, {dur:.3f}]"))
    uem_m = merge_intervals(uem)
    ref_speech = speech_regions(segs)
    outside = total_duration(subtract(ref_speech, uem_m))
    if outside > 0.5:
        issues.append(_issue("warning", "speech_outside_uem", f"{outside:.1f} s of reference speech outside the UEM"))
    # ---- speakers
    spk_time: dict[str, float] = {}
    for g in segs:
        spk_time[g.speaker] = spk_time.get(g.speaker, 0.0) + g.duration
    n_spk = len(spk_time)
    metrics["num_speakers"] = n_spk
    if n_spk < 2:
        issues.append(_issue("warning", "fewer_than_two_speakers", f"{n_spk} speaker(s)"))
    tiny = [k for k, v in spk_time.items() if v < 1.0]
    if tiny:
        issues.append(_issue("info", "speaker_under_1s", f"{len(tiny)} speaker(s) with < 1 s of speech", speakers=tiny))
    short = sum(1 for g in segs if g.duration < 0.05)
    if short:
        issues.append(_issue("info", "segments_under_50ms", f"{short} segment(s) shorter than 50 ms"))
    long_ = [g for g in segs if g.duration > 60]
    if long_:
        issues.append(_issue("warning", "segments_over_60s", f"{len(long_)} segment(s) longer than 60 s (merged turns?)",
                             longest=round(max(g.duration for g in long_), 1)))
    # long unannotated stretches inside the UEM
    silence = subtract(uem_m, ref_speech)
    long_sil = [(a, b) for a, b in silence if b - a > 30]
    if long_sil:
        issues.append(_issue("info", "silence_over_30s", f"{len(long_sil)} stretch(es) > 30 s with no reference speech",
                             regions=[[round(a, 1), round(b, 1)] for a, b in long_sil[:5]]))
    # ---- words
    words = s.words
    if words:
        spk_ivs: dict[str, list] = {}
        for g in segs:
            spk_ivs.setdefault(g.speaker, []).append((g.start, g.end))
        spk_ivs = {k: merge_intervals(v) for k, v in spk_ivs.items()}
        unknown = {w["speaker"] for w in words} - set(spk_time)
        if unknown:
            issues.append(_issue("warning", "word_speaker_not_in_rttm", f"{len(unknown)} word speaker(s) absent from RTTM",
                                 speakers=sorted(unknown)[:5]))
        wt = sum(max(0.0, w["end"] - w["start"]) for w in words)
        uncovered = 0.0
        for spk in {w["speaker"] for w in words}:
            wivs = merge_intervals((w["start"], w["end"]) for w in words if w["speaker"] == spk)
            uncovered += total_duration(subtract(wivs, spk_ivs.get(spk, [])))
        metrics["word_time_outside_reference"] = round(uncovered / wt, 4) if wt else 0.0
        if wt and uncovered / wt > 0.02:
            issues.append(_issue("warning", "words_outside_reference",
                                 f"{100 * uncovered / wt:.1f}% of word time is outside same-speaker reference segments"))
    # ---- VAD cross-check
    if vad:
        from .vad import energy_vad

        x = load_mono16k(s.audio_path)
        if vad_backend == "silero_x2":
            v_ivs, vinfo = silero_x2_intervals(s, x)
        else:
            v_ivs, vinfo = energy_vad(x)
        v_ivs = intersect(v_ivs, uem_m)
        ref_padded = merge_intervals((max(0, a - vad_tolerance), b + vad_tolerance) for a, b in ref_speech)
        missing = [(a, b) for a, b in subtract(v_ivs, ref_padded) if b - a >= 0.5]
        ref_in_uem = intersect(ref_speech, uem_m)
        ref_silent = subtract(ref_in_uem, merge_intervals((a - vad_tolerance, b + vad_tolerance) for a, b in v_ivs))
        vt = total_duration(v_ivs)
        rt = total_duration(ref_in_uem)
        metrics["vad"] = {
            **vinfo,
            "vad_speech_s": round(vt, 1),
            "ref_speech_s": round(rt, 1),
            "vad_not_in_ref_s": round(total_duration(missing), 1),
            "vad_not_in_ref_frac_of_ref": round(total_duration(missing) / rt, 4) if rt else None,
            "ref_not_in_vad_s": round(total_duration(ref_silent), 1),
            "ref_not_in_vad_frac": round(total_duration(ref_silent) / rt, 4) if rt else None,
            "longest_vad_not_in_ref": [[round(a, 2), round(b, 2)] for a, b in
                                       sorted(missing, key=lambda iv: iv[0] - iv[1])[:10]],
        }
        if rt and total_duration(missing) / rt > 0.05:
            issues.append(_issue("warning", "possible_unannotated_speech",
                                 f"energy VAD finds {total_duration(missing):.0f} s of energy-speech (>= 0.5 s chunks) "
                                 f"outside reference speech (+/-{vad_tolerance} s): "
                                 f"{100 * total_duration(missing) / rt:.1f}% of reference speech"))
    return {"session_id": s.session_id, "issues": issues, "metrics": metrics}


def validate_dataset(name: str, root=None, view: str | None = None, vad: bool = False, out=None, vad_backend: str = "energy",
                     echo: bool = True) -> dict:
    ds = NormalizedDataset(name, root)
    sessions = ds.sessions(view=view)
    recs = {r["session_id"]: r for r in ds.records(view)}
    results = []
    for s in sessions:
        r = validate_session(s, vad=vad, vad_backend=vad_backend)
        raw = recs[s.session_id].get("label_issues") or {}
        r["raw_label_issues"] = raw
        results.append(r)
    counts = Counter()
    raw_tot = Counter()
    for r in results:
        for i in r["issues"]:
            counts[(i["level"], i["code"])] += 1
        for k, v in r["raw_label_issues"].items():
            if k != "examples":
                raw_tot[k] += v
    summary = {
        "dataset": name,
        "view": view or ds.default_view,
        "sessions": len(results),
        "errors": sum(v for (lvl, _), v in counts.items() if lvl == "error"),
        "warnings": sum(v for (lvl, _), v in counts.items() if lvl == "warning"),
        "issue_counts": {f"{lvl}:{code}": v for (lvl, code), v in sorted(counts.items())},
        "raw_label_issue_totals": dict(raw_tot),
        "sessions_with_raw_label_issues": sum(1 for r in results if any(k != "examples" for k in r["raw_label_issues"])),
    }
    if vad:
        vals = [r["metrics"]["vad"] for r in results if "vad" in r["metrics"]]
        ref = sum(v["ref_speech_s"] for v in vals)
        summary["vad"] = {
            "backend": vad_backend,
            "ref_speech_h": round(ref / 3600, 2),
            "vad_not_in_ref_frac": round(sum(v["vad_not_in_ref_s"] for v in vals) / ref, 4) if ref else None,
            "ref_not_in_vad_frac": round(sum(v["ref_not_in_vad_s"] for v in vals) / ref, 4) if ref else None,
            "worst_sessions": sorted(((r["session_id"], r["metrics"]["vad"]["vad_not_in_ref_frac_of_ref"]) for r in results
                                      if "vad" in r["metrics"] and r["metrics"]["vad"]["vad_not_in_ref_frac_of_ref"] is not None),
                                     key=lambda t: -t[1])[:10],
        }
    report = {"summary": summary, "sessions": results}
    if out:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        tag = f"{name}.{summary['view']}"
        (out / f"validation.{tag}.json").write_text(json.dumps(report, indent=1, default=float), encoding="utf-8", newline="\n")
        (out / f"validation.{tag}.md").write_text(_md(report), encoding="utf-8", newline="\n")
    if echo:
        print(_md(report, max_sessions=15))
    return report


def _md(report: dict, max_sessions: int | None = None) -> str:
    s = report["summary"]
    lines = [f"# Validation: {s['dataset']} (view: {s['view']})", "",
             f"- sessions: {s['sessions']}, errors: {s['errors']}, warnings: {s['warnings']}",
             f"- sessions whose ORIGINAL labels needed fixing during normalization: {s['sessions_with_raw_label_issues']}"]
    if s["raw_label_issue_totals"]:
        lines.append("- original-label issue totals: " + ", ".join(f"{k}={v}" for k, v in s["raw_label_issue_totals"].items()))
    if s["issue_counts"]:
        lines += ["", "| level:code | sessions |", "|---|---:|"]
        lines += [f"| {k} | {v} |" for k, v in s["issue_counts"].items()]
    if "vad" in s:
        v = s["vad"]
        lines += ["", f"VAD cross-check ({v.get('backend', 'energy')} VAD, same view audio):",
                  f"- reference speech: {v['ref_speech_h']} h",
                  f"- VAD speech outside reference (+/-0.25 s, chunks >= 0.5 s): {v['vad_not_in_ref_frac']} of reference speech",
                  f"- reference speech where the VAD sees no energy: {v['ref_not_in_vad_frac']}",
                  "- sessions with most VAD speech outside the reference: " +
                  ", ".join(f"{a} ({b})" for a, b in v["worst_sessions"])]
    shown = 0
    for r in report["sessions"]:
        notable = [i for i in r["issues"] if i["level"] in ("error", "warning")]
        if not notable:
            continue
        if max_sessions is not None and shown >= max_sessions:
            lines.append("- ... (more sessions in the JSON report)")
            break
        if shown == 0:
            lines += ["", "## Sessions with errors/warnings", ""]
        shown += 1
        lines.append(f"- **{r['session_id']}**: " + "; ".join(f"{i['code']} ({i['message']})" for i in notable))
    return "\n".join(lines) + "\n"
