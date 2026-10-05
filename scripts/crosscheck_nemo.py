"""Cross-check: official NeMo inference vs the Transformers port used by `diards evaluate`.

Runs `nvidia/Nemotron-3-Diarization` through NeMo's `SortformerEncLabelModel.diarize()` with the model card's
30.4 s configuration on a few normalized sessions, writes RTTMs, and scores (a) NeMo vs reference, (b) Transformers
vs reference, (c) NeMo vs Transformers (DER between the two hypotheses).

Run with a Python that has nemo-toolkit[asr] installed (a separate env is fine; it only needs this repo on the path):
    python scripts/crosscheck_nemo.py --sessions ami:sdm:ami__ES2004a,callfriend_eng:default:callfriend_eng__eng-n_000
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diards.annotation import Segment, read_rttm_single, write_rttm  # noqa: E402
from diards.config import work_root  # noqa: E402
from diards.core import NormalizedDataset  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", required=True, help="comma list of dataset:view:session_id")
    ap.add_argument("--out", default="results/nemo_crosscheck")
    args = ap.parse_args()
    from nemo.collections.asr.models import SortformerEncLabelModel

    model = SortformerEncLabelModel.from_pretrained("nvidia/Nemotron-3-Diarization")
    model.eval()
    sm = model.sortformer_modules
    sm.chunk_len, sm.chunk_right_context, sm.fifo_len, sm.spkcache_update_period, sm.spkcache_len = 340, 40, 40, 300, 264
    model._check_streaming_parameters()
    from diards.score import Scorer

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for item in args.sessions.split(","):
        name, view, sid = item.split(":")
        s = next(x for x in NormalizedDataset(name).sessions(view=view) if x.session_id == sid)
        import soundfile as sf

        x, sr = sf.read(str(s.audio_path), dtype="float32")
        # numpy input avoids NeMo's temporary manifest file, which Windows refuses to delete while it is open
        segs = model.diarize(audio=[x], batch_size=1, sample_rate=sr)[0]
        hyp = []
        for seg in segs:
            if isinstance(seg, str):
                a, b, spk = seg.split()
            else:
                a, b, spk = seg
            hyp.append(Segment(float(a), float(b), str(spk)))
        write_rttm(work_root() / "nemo_crosscheck" / f"{sid}.nemo.rttm", sid, hyp)
        hf = read_rttm_single(work_root() / "nemotron" / f"{name}.{view}" / "hyp" / f"{sid}.rttm")
        r = {"session": sid, "view": view,
             "nemo_vs_ref": Scorer(0.0)(sid, s.segments, hyp, s.uem)["der"],
             "hf_vs_ref": Scorer(0.0)(sid, s.segments, hf, s.uem)["der"],
             "nemo_vs_hf": Scorer(0.0)(sid, hf, hyp, s.uem)["der"]}
        rows.append({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
        print(rows[-1], flush=True)
    (out / "crosscheck.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
