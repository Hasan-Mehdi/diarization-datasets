import json

import pytest

from diards import export
from diards.annotation import Segment
from diards.score import Scorer


def test_nemo_export(tiny_dataset):
    out = export.export("tiny", "nemo", root=tiny_dataset, view="mix")
    lines = [json.loads(x) for x in (out / "tiny.mix.test.json").read_text().splitlines()]
    assert lines[0]["num_speakers"] == 2 and lines[0]["rttm_filepath"].endswith("tiny__rec_1.rttm")
    assert set(lines[0]) >= {"audio_filepath", "offset", "duration", "rttm_filepath", "uem_filepath"}


def test_pyannote_export_loads(tiny_dataset):
    pytest.importorskip("pyannote.database")
    from pyannote.database import FileFinder, registry

    out = export.export("tiny", "pyannote", root=tiny_dataset)
    registry.load_database(str(out / "database.yml"))
    proto = registry.get_protocol("tiny_mix.SpeakerDiarization.default", preprocessors={"audio": FileFinder()})
    test_files = list(proto.test())
    dev_files = list(proto.development())
    assert [f["uri"] for f in test_files] == ["tiny__rec_1"]
    assert [f["uri"] for f in dev_files] == ["tiny__rec2"]
    assert sorted(test_files[0]["annotation"].labels()) == ["A", "B"]


def test_lhotse_export_loads(tiny_dataset):
    pytest.importorskip("lhotse")
    from lhotse import CutSet, load_manifest

    out = export.export("tiny", "lhotse", root=tiny_dataset, view="far")
    recs = load_manifest(out / "tiny_far_recordings_test.jsonl.gz")
    sups = load_manifest(out / "tiny_far_supervisions_test.jsonl.gz")
    cuts = CutSet.from_manifests(recordings=recs, supervisions=sups)
    cut = next(iter(cuts))
    assert cut.duration == pytest.approx(12.0) and len(cut.supervisions) == 3


def test_scorer_collar_convention():
    ref = [Segment(0, 10, "A"), Segment(10, 20, "B")]
    hyp = [Segment(0, 10.2, "x"), Segment(10.2, 20, "y")]
    s0 = Scorer(0.0)(None or "u", ref, hyp, [(0, 20)])
    assert s0["conf"] == pytest.approx(0.2 / 20)
    s25 = Scorer(0.25)("u", ref, hyp, [(0, 20)])  # 0.25 s each side of the boundary at 10 s is not scored
    assert s25["der"] == pytest.approx(0.0)


def test_afrispeech_parser(fixtures):
    from diards.datasets.afrispeech_dialog import parse_transcript

    turns = parse_transcript((fixtures / "afrispeech_transcript.txt").read_text())
    assert turns == [(2.02, 4.99, "Speaker 1"), (7.0, 32.98, "Speaker 2")]


def test_textgrid_parser(fixtures):
    from diards.datasets.primock57 import read_textgrid

    assert read_textgrid(fixtures / "sample.TextGrid") == [(2.5, 6.25, "Hello, how can I help?")]


def test_ami_relabel():
    from diards.datasets.ami import _relabel

    segs = _relabel([Segment(0, 1, "EN2002a.D"), Segment(1, 2, "MEE073")], "EN2002a", {"D": "MEE071"})
    assert [s.speaker for s in segs] == ["MEE071", "MEE073"]
