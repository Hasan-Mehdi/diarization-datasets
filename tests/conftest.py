import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures():
    return FIXTURES


def tone_with_speech(spans, duration=12.0, sr=16000, seed=0):
    """Low noise floor plus loud noise bursts in ``spans`` (stand-in for speech)."""
    rng = np.random.default_rng(seed)
    x = 0.001 * rng.standard_normal(int(duration * sr))
    for a, b in spans:
        n = int((b - a) * sr)
        t = np.arange(n) / sr
        x[int(a * sr): int(a * sr) + n] += 0.3 * np.sin(2 * np.pi * 220 * t) * (0.5 + 0.5 * rng.random(n))
    return x.astype(np.float32)


@pytest.fixture
def tiny_dataset(tmp_path):
    """A two-session normalized dataset written through the public writer API."""
    from diards.annotation import Segment
    from diards.audio import write_array
    from diards.core import DatasetMeta, DatasetWriter

    meta = DatasetMeta(name="tiny", title="Tiny", homepage="", license="CC0", license_url="", citation="",
                       source_version="test", default_view="mix", views={"mix": "mix", "far": "far"})
    w = DatasetWriter(meta, tmp_path)
    # session 1: two speakers, 1 s overlap, plus a same-speaker overlap in the raw labels
    s1 = [Segment(1.0, 4.0, "A"), Segment(3.0, 6.0, "B"), Segment(5.5, 7.0, "B"), Segment(8.0, 9.0, "A")]
    sid = w.session_id("rec 1")  # space -> sanitized
    for view in ("mix", "far"):
        write_array(w.audio_path(sid, view), tone_with_speech([(1, 7), (8, 9)]))
    w.add_session("rec 1", "test", s1, words=[{"start": 1.0, "end": 1.5, "speaker": "A", "word": "hi"}])
    # session 2: speech at 2-4 s labelled, speech at 6-9 s NOT labelled (to be caught by the VAD check)
    sid2 = w.session_id("rec2")
    for view in ("mix", "far"):
        write_array(w.audio_path(sid2, view), tone_with_speech([(2, 4), (6, 9)], seed=1))
    w.add_session("rec2", "dev", [Segment(2.0, 4.0, "C"), Segment(2.5, 3.5, "D")])
    w.finalize()
    return tmp_path
