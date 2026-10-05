import numpy as np
import pytest

from diards.annotation import Segment
from diards.vad_assist import (
    apply_pieces,
    fill_from_probs,
    gate,
    map_back,
    probs_to_segments,
    score,
    trim_plan,
    uem_span,
    uem_speech,
    zero_outside,
)
from diards.vad_audit import best_lag, boundary_offsets, coverage, coverage_metrics, dilate
from diards.vads import frames_to_intervals, postprocess, to_raster


def test_frames_to_intervals_and_raster_roundtrip():
    act = np.array([0, 1, 1, 0, 0, 1, 0, 1, 1, 1], bool)
    ivs = frames_to_intervals(act, 0.01)
    assert ivs == [(0.01, 0.03), (0.05, 0.06), (0.07, 0.1)]
    assert (to_raster(ivs, len(act), 0.01) == act).all()
    # frame longer than hop (e.g. 30 ms frames every 10 ms)
    assert frames_to_intervals(np.array([1, 1, 0], bool), 0.01, 0.03) == [(0.0, 0.04)]


def test_postprocess_bridges_drops_and_pads():
    ivs = [(1.0, 1.2), (1.25, 1.5), (3.0, 3.1), (5.0, 6.0)]
    assert postprocess(ivs, min_silence=0.1, min_speech=0.25, pad=0.05, duration=6.02) == [(0.95, 1.55), (4.95, 6.02)]


def test_coverage_and_dilate():
    ivs = [(0.0, 1.0), (2.0, 3.0)]
    assert coverage(ivs, 0.5, 2.5) == pytest.approx(0.5)
    assert coverage(ivs, 1.0, 2.0) == 0.0
    assert dilate(ivs, 0.6) == [(0.0, 3.6)]


def test_coverage_metrics_flags_unannotated_and_padded_speech():
    ref = [(0.0, 4.0), (10.0, 12.0)]           # 0-4: speech only 0-2 (padded), 10-12 fine
    vad = [(0.0, 2.0), (6.0, 8.0), (10.0, 12.0)]  # 6-8 unannotated
    m = coverage_metrics(ref, vad, tol=0.25, min_len=0.5)
    assert m["ref_s"] == 6 and m["vad_s"] == 6
    assert m["fa_s"] == pytest.approx(2.0) and m["miss_s"] == pytest.approx(2.0)
    assert m["unref_s"] == pytest.approx(2.0)      # 6-8 is far from any reference speech
    assert m["unvoiced_s"] == pytest.approx(1.75)  # 2.25-4: reference speech far from VAD speech


def test_boundary_offsets_sign_convention():
    ref = [(1.0, 3.0), (10.0, 12.0)]
    vad = [(1.2, 2.9), (9.9, 12.3)]
    b = boundary_offsets(ref, vad)
    assert b["islands"] == 2 and b["islands_without_vad"] == 0
    # positive = reference wider than the VAD
    assert b["onsets"] == pytest.approx([0.2, -0.1])
    assert b["offsets"] == pytest.approx([0.1, -0.3])
    # VAD speech bridging two islands makes the inner boundaries ambiguous -> skipped
    b = boundary_offsets([(1.0, 2.0), (2.5, 4.0)], [(1.1, 3.9)])
    assert b["onsets"] == pytest.approx([0.1]) and b["offsets"] == pytest.approx([0.1])


def test_best_lag_recovers_shift():
    rng = np.random.default_rng(0)
    t, vad = 0.0, []
    while t < 300:
        a = t + rng.uniform(0.5, 3)
        b = a + rng.uniform(0.5, 4)
        vad.append((a, b))
        t = b
    ref = [(a - 0.6, b - 0.6) for a, b in vad]  # reference 0.6 s early
    r = best_lag(ref, vad, 310.0)
    assert r["best_lag_s"] == pytest.approx(0.6) and r["gain"] > 0.05


def test_gate_and_fill():
    hyp = [Segment(0.0, 2.0, "a"), Segment(1.5, 4.0, "b")]
    assert gate(hyp, [(1.0, 3.0)]) == [Segment(1.0, 2.0, "a"), Segment(1.5, 3.0, "b")]
    assert gate(hyp, [(1.0, 3.0)], pad=0.5) == [Segment(0.5, 2.0, "a"), Segment(1.5, 3.5, "b")]
    probs = np.zeros((10, 2), np.float32)
    probs[0:3, 0] = 0.9
    probs[3:6, 1] = 0.3   # below threshold: filled inside VAD speech only
    probs[8:10, 0] = 0.9  # outside VAD speech: removed by gate_too
    assert probs_to_segments(probs > 0.5, 0.1) == [Segment(0.0, 0.3, "spk0"), Segment(0.8, 1.0, "spk0")]
    filled = fill_from_probs(probs, 0.1, [(0.0, 0.6)])
    assert filled == [Segment(0.0, 0.3, "spk0"), Segment(0.3, 0.6, "spk1"), Segment(0.8, 1.0, "spk0")]
    assert fill_from_probs(probs, 0.1, [(0.0, 0.6)], gate_too=True) == filled[:2]


def test_trim_and_map_back_roundtrip():
    sr = 100
    x = np.arange(20 * sr, dtype=np.float32)
    speech = [(2.0, 4.0), (10.0, 11.0)]
    pieces = trim_plan(speech, 20.0, max_sil=1.0, keep=0.5)
    assert pieces == [(0.0, 0.25), (1.75, 4.25), (9.75, 11.25), (19.75, 20.0)]
    y = apply_pieces(x, pieces, sr)
    assert len(y) == int(round(sum(b - a for a, b in pieces) * sr))
    # a segment covering the speech in trimmed time maps back to the original speech times
    t_speech2 = 0.25 + 2.5 + 0.25  # trimmed-time start of the piece containing (10, 11)
    segs = map_back([Segment(0.5, 2.5, "a"), Segment(t_speech2, t_speech2 + 1.0, "b")], pieces)
    assert segs == [Segment(2.0, 4.0, "a"), Segment(10.0, 11.0, "b")]
    # a segment spanning a cut is split at the cut
    assert map_back([Segment(2.5, 3.5, "a")], pieces) == [Segment(4.0, 4.25, "a"), Segment(9.75, 10.5, "a")]


def test_zero_outside_and_vad_uems():
    x = np.ones(1000, np.float32)
    y = zero_outside(x, [(0.02, 0.03)], margin=0.005, sr=1000)
    assert y.sum() == 20 and y[15] == 1 and y[14] == 0
    assert uem_span([(0.0, 100.0)], [(10.0, 20.0), (50.0, 60.0)]) == [(9.0, 61.0)]
    assert uem_speech([(0.0, 100.0)], [(10.0, 20.0), (50.0, 60.0)]) == [(9.5, 20.5), (49.5, 60.5)]


def test_score_matches_direct_scorer(tiny_dataset):
    from diards.core import NormalizedDataset
    from diards.score import Scorer

    sessions = NormalizedDataset("tiny", tiny_dataset).sessions(view="mix")
    hyps = {s.session_id: [Segment(g.start + 0.1, g.end, "x" + g.speaker) for g in s.segments] for s in sessions}
    r = score(sessions, hyps)
    direct = Scorer(0.0)
    for s in sessions:
        direct(s.session_id, s.segments, hyps[s.session_id], s.uem)
    assert r["summary"]["primary@0.0"]["der"] == pytest.approx(round(abs(direct.der), 4))
    assert set(r["summary"]) == {"primary@0.0", "primary@0.25"}


def test_cache_and_audit_end_to_end(tiny_dataset, tmp_path, monkeypatch):
    pytest.importorskip("silero_vad")
    pytest.importorskip("webrtcvad")
    from diards import vads
    from diards.core import NormalizedDataset
    from diards.vad_audit import audit_dataset

    monkeypatch.setenv("DIARDS_VAD_STUDY", str(tmp_path / "study"))
    jobs = vads.jobs_for("tiny", "mix", root=tiny_dataset)
    for j in jobs:
        vads._work(j)
    s = NormalizedDataset("tiny", tiny_dataset).sessions(view="mix")[0]
    c = vads.VadCache.load("tiny", "mix", s.session_id)
    assert c.duration == pytest.approx(12.0)
    assert len(c.silero_probs) == int(np.ceil(12.0 * 16000 / 512))
    assert 0 <= c.silero_probs.min() and c.silero_probs.max() <= 1
    r = audit_dataset("tiny", "mix", vads=("energy", "silero"), root=tiny_dataset, echo=False)
    assert r["sessions"] == 2
    rec2 = next(x for x in r["per_session"] if x["session_id"].endswith("rec2"))["refs"]["primary"]["energy"]
    # session 2 has loud bursts at 6-9 s that the reference does not label
    assert rec2["unref_s"] > 2.0


def test_silero_intervals_match_package():
    silero_vad = pytest.importorskip("silero_vad")
    import torch

    from diards import vads

    rng = np.random.default_rng(1)
    x = (0.05 * rng.standard_normal(16000 * 3)).astype(np.float32)
    p = vads.silero_probs(x)
    assert len(p) == int(np.ceil(len(x) / 512))
    ts = silero_vad.get_speech_timestamps(torch.from_numpy(x), vads.silero_model(), return_seconds=True,
                                          time_resolution=3)
    assert vads.silero_intervals(p, len(x)) == [(t["start"], t["end"]) for t in ts]


def test_silero_state_reset_windows():
    pytest.importorskip("silero_vad")
    from diards import vads

    rng = np.random.default_rng(2)
    x = (0.05 * rng.standard_normal(16000 * 5 + 100)).astype(np.float32)
    stock = vads.silero_probs(x)
    # a reset period longer than the file changes nothing
    assert np.array_equal(vads.silero_probs(x, reset_every=10.0), stock)
    r = vads.silero_probs(x, reset_every=1.0, warmup=0.5)
    assert r.shape == stock.shape
    # the first window has no warm-up and equals the stock run
    k = int(round(16000 / 512))
    assert np.array_equal(r[:k], stock[:k])
    # every later window equals a fresh run started 0.5 s earlier
    w = int(round(0.5 * 16000 / 512))
    fresh = vads.silero_probs(x[(2 * k - w) * 512:(3 * k) * 512])
    assert np.allclose(r[2 * k:3 * k], fresh[w:w + k])
