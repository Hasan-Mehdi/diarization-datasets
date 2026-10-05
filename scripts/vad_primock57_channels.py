"""PriMock57 per channel: Silero VAD on each participant's isolated channel vs the TextGrids and the energy-based
channel-activity reference (PRIMOCK57.md).

Doctor and patient were recorded on separate channels, isolated by ~50 dB, so a VAD on each channel measures when
that person spoke. This script compares, per speaker:

  * TextGrid utterances (primary reference), energy channel activity (``rttm_alt/channel_activity``), and Silero
    (default settings with the 30 s state reset of ``diards.vads``, and without its 30 ms padding) on the
    speaker's own channel;
  * labelled time Silero calls silence, Silero speech with no label nearby, boundary offsets;
  * where energy activity and Silero disagree (breaths/coughs vs speech), checked with Whisper (``--whisper``);
  * Nemotron 3 Diarization (cached hypotheses on the mix) scored against each reference with ``diards.score``.

Needs: ``python -m diards.vads primock57 --channels`` (VAD cache) and the cached ``primock57.mix`` hypotheses.
Usage: python scripts/vad_primock57_channels.py [--whisper] [--out results/vad/primock57]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from diards.annotation import (  # noqa: E402
    Segment,
    merge_intervals,
    overlap_regions,
    read_rttm_single,
    subtract,
    total_duration,
    write_rttm,
)
from diards.config import raw_root, work_root  # noqa: E402
from diards.core import NormalizedDataset  # noqa: E402
from diards.vad_assist import score  # noqa: E402
from diards.vad_audit import boundary_offsets, dilate, long_chunks, pct  # noqa: E402
from diards.vads import VadCache  # noqa: E402

ROLES = ("doctor", "patient")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--whisper", action="store_true", help="transcribe energy-vs-Silero disagreements (GPU)")
    ap.add_argument("--per-kind", type=int, default=30)
    ap.add_argument("--out", default=str(ROOT / "results" / "vad" / "primock57"))
    a = ap.parse_args()
    out = Path(a.out)
    sessions = NormalizedDataset("primock57").sessions(view="mix")
    acc = {r: {k: 0.0 for k in ("label", "energy", "silero", "silero_nopad", "label_silero_silent",
                                "label_silero_silent_ge0.3", "label_energy_silent_ge0.3", "silero_unlabelled",
                                "energy_unlabelled", "energy_not_silero_ge0.3", "silero_not_energy_ge0.3")}
           for r in ROLES}
    deltas = {(r, ref, v): {"onsets": [], "offsets": []} for r in ROLES for ref in ("textgrid", "energy")
              for v in ("silero", "silero_nopad")}
    refs = {"silero_channel": {}, "silero_channel_nopad": {}}
    disagreements = []
    ovl = {"textgrid": 0.0, "energy": 0.0, "silero_channel": 0.0}
    speech_tot = dict(ovl)
    for s in sessions:
        c = s.original_id
        tg_all, en_all = s.segments, s.alt_segments("channel_activity")
        sil_segs, nopad_segs = [], []
        for r in ROLES:
            spk = f"{c}_{r}"
            tg = merge_intervals((g.start, g.end) for g in tg_all if g.speaker == spk)
            en = merge_intervals((g.start, g.end) for g in en_all if g.speaker == spk)
            cache = VadCache.load("primock57", "channels", f"{c}_{r}")
            sil = merge_intervals(cache.silero(reset=True))
            nopad = merge_intervals(cache.silero(reset=True, speech_pad_ms=0))
            sil_segs += [Segment(x, y, spk) for x, y in sil]
            nopad_segs += [Segment(x, y, spk) for x, y in nopad]
            d = acc[r]
            d["label"] += total_duration(tg)
            d["energy"] += total_duration(en)
            d["silero"] += total_duration(sil)
            d["silero_nopad"] += total_duration(nopad)
            d["label_silero_silent"] += total_duration(subtract(tg, sil))
            d["label_silero_silent_ge0.3"] += total_duration(long_chunks(subtract(tg, sil), 0.3))
            d["label_energy_silent_ge0.3"] += total_duration(long_chunks(subtract(tg, en), 0.3))
            d["silero_unlabelled"] += total_duration(long_chunks(subtract(sil, dilate(tg, 0.25)), 0.5))
            d["energy_unlabelled"] += total_duration(long_chunks(subtract(en, dilate(tg, 0.25)), 0.5))
            e_not_s = long_chunks(subtract(en, sil), 0.3)
            s_not_e = long_chunks(subtract(sil, en), 0.3)
            d["energy_not_silero_ge0.3"] += total_duration(e_not_s)
            d["silero_not_energy_ge0.3"] += total_duration(s_not_e)
            disagreements += [("energy_not_silero", f"{c}_{r}", x, y) for x, y in e_not_s]
            disagreements += [("silero_not_energy", f"{c}_{r}", x, y) for x, y in s_not_e]
            for ref_name, ref in (("textgrid", tg), ("energy", en)):
                for v, ivs in (("silero", sil), ("silero_nopad", nopad)):
                    b = boundary_offsets(ref, ivs)
                    deltas[(r, ref_name, v)]["onsets"] += b["onsets"]
                    deltas[(r, ref_name, v)]["offsets"] += b["offsets"]
        refs["silero_channel"][s.session_id] = sorted(sil_segs)
        refs["silero_channel_nopad"][s.session_id] = sorted(nopad_segs)
        for name, segs in (("textgrid", tg_all), ("energy", en_all), ("silero_channel", sil_segs)):
            speech_tot[name] += total_duration(merge_intervals((g.start, g.end) for g in segs))
            ovl[name] += total_duration(overlap_regions(segs))
        rttm_dir = out / "silero_channel_rttm"
        write_rttm(rttm_dir / f"{s.session_id}.rttm", s.session_id, sorted(sil_segs))

    result = {"per_speaker_role": {}, "boundaries": {}, "overlap_pct_of_speech": {}}
    for r, d in acc.items():
        lab = d["label"]
        result["per_speaker_role"][r] = {
            "labelled_h": round(lab / 3600, 3), "energy_activity_h": round(d["energy"] / 3600, 3),
            "silero_h": round(d["silero"] / 3600, 3), "silero_nopad_h": round(d["silero_nopad"] / 3600, 3),
            "labelled_silero_silent_pct": round(100 * d["label_silero_silent"] / lab, 2),
            "labelled_silero_silent_ge0.3s_pct": round(100 * d["label_silero_silent_ge0.3"] / lab, 2),
            "labelled_energy_silent_ge0.3s_pct": round(100 * d["label_energy_silent_ge0.3"] / lab, 2),
            "silero_unlabelled_min": round(d["silero_unlabelled"] / 60, 2),
            "energy_unlabelled_min": round(d["energy_unlabelled"] / 60, 2),
            "energy_not_silero_ge0.3s_min": round(d["energy_not_silero_ge0.3"] / 60, 2),
            "silero_not_energy_ge0.3s_min": round(d["silero_not_energy_ge0.3"] / 60, 2),
        }
    for (r, ref_name, v), x in deltas.items():
        result["boundaries"][f"{r}:{ref_name}_vs_{v}"] = {"onset": {**pct(x["onsets"]), "n": len(x["onsets"])},
                                                          "offset": {**pct(x["offsets"]), "n": len(x["offsets"])}}
    for name in ovl:
        result["overlap_pct_of_speech"][name] = round(100 * ovl[name] / speech_tot[name], 2)

    hd = work_root() / "nemotron" / "primock57.mix" / "hyp"
    hyps = {s.session_id: read_rttm_single(hd / f"{s.session_id}.rttm") for s in sessions}
    sc = score(sessions, hyps, extra_refs=refs)
    result["nemotron_vs_references"] = sc["summary"]

    if a.whisper:
        result["whisper_disagreements"] = whisper_check(disagreements, a.per_kind)

    out.mkdir(parents=True, exist_ok=True)
    (out / "primock57_channels.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8",
                                                 newline="\n")
    print(json.dumps({k: v for k, v in result.items() if k != "whisper_disagreements"}, indent=1))
    if "whisper_disagreements" in result:
        print(json.dumps(result["whisper_disagreements"]["summary"], indent=1))


def whisper_check(disagreements, per_kind):
    import soundfile as sf

    from audit_false_alarms import is_speech, words
    from vad_whisper_check import transcribe

    raw = raw_root() / "primock57" / "audio"
    todo = []
    for kind in ("energy_not_silero", "silero_not_energy"):
        regs = sorted((d for d in disagreements if d[0] == kind), key=lambda d: d[2] - d[3])[:per_kind]
        todo += regs
    todo.sort(key=lambda d: (d[1], d[2]))
    rows, cache = [], {}
    for kind, ch, a, b in todo:
        if ch not in cache:
            cache.clear()
            cache[ch] = sf.read(str(raw / f"{ch}.wav"), dtype="float32")
        x, sr = cache[ch]
        text = transcribe(x, sr, a, b)
        rows.append({"kind": kind, "channel": ch, "start": round(a, 2), "end": round(b, 2), "dur": round(b - a, 2),
                     "whisper": text, "words": len(words(text)), "speech": is_speech(text)})
    summ = {}
    for r in rows:
        d = summ.setdefault(r["kind"], {"regions": 0, "with_speech": 0, "with_any_word": 0})
        d["regions"] += 1
        d["with_speech"] += int(r["speech"])
        d["with_any_word"] += int(r["words"] > 0)
    return {"summary": summ, "regions": rows}


if __name__ == "__main__":
    main()
