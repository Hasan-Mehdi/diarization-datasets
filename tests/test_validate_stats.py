import json

from diards.annotation import read_rttm_single
from diards.core import NormalizedDataset, load_dataset
from diards.stats import dataset_stats, session_stats
from diards.validate import raw_label_issues, validate_dataset


def test_raw_label_issues_on_bad_rttm(fixtures):
    segs = read_rttm_single(fixtures / "bad.rttm")
    issues = raw_label_issues(segs, duration=10.0)
    assert issues["same_speaker_overlap"] == 1
    assert issues["zero_duration"] == 1
    assert issues["duplicate_segment"] == 1
    assert issues["beyond_audio_end"] == 1
    assert issues["speaker_case_variants"] == 2  # "B" and "b"
    assert issues["placeholder_speaker_label"] == 1


def test_writer_layout_and_loader(tiny_dataset):
    ds = NormalizedDataset("tiny", tiny_dataset)
    assert set(ds.views) == {"mix", "far"}
    assert (ds.dir / "manifest.jsonl").exists() and (ds.dir / "manifest.far.jsonl").exists()
    meta = json.loads((ds.dir / "dataset.json").read_text())
    assert meta["splits"] == {"dev": 1, "test": 1}
    sessions = load_dataset("tiny", root=tiny_dataset)
    s1 = next(s for s in sessions if s.original_id == "rec 1")
    assert s1.session_id == "tiny__rec_1"  # ASCII-sanitized
    # same-speaker overlap B(3-6)+B(5.5-7) merged, and recorded as an original-label issue
    assert [(x.start, x.end, x.speaker) for x in s1.segments if x.speaker == "B"] == [(3.0, 7.0, "B")]
    rec = next(r for r in ds.records() if r["session_id"] == s1.session_id)
    assert rec["label_issues"]["same_speaker_overlap"] == 1
    assert rec["num_speakers"] == 2
    # overlap 3-4 (A,B) = 1 s over 6+1 = 7 s of speech
    assert abs(rec["overlap_ratio"] - 1 / 7) < 1e-3
    assert s1.words[0]["word"] == "hi"
    assert s1.uem == [(0.0, 12.0)]


def test_validator_flags_unlabelled_speech(tiny_dataset):
    report = validate_dataset("tiny", root=tiny_dataset, vad=True, echo=False)
    by_id = {r["session_id"]: r for r in report["sessions"]}
    codes2 = {i["code"] for i in by_id["tiny__rec2"]["issues"]}
    assert "possible_unannotated_speech" in codes2  # 6-9 s is loud but unlabelled
    codes1 = {i["code"] for i in by_id["tiny__rec_1"]["issues"]}
    assert "possible_unannotated_speech" not in codes1
    assert report["summary"]["errors"] == 0


def test_stats(tiny_dataset):
    st = session_stats(load_dataset("tiny", root=tiny_dataset, split="test")[0].segments, [(0.0, 12.0)])
    assert st["num_speakers"] == 2 and abs(st["speech_s"] - 7.0) < 1e-6 and abs(st["overlap_s"] - 1.0) < 1e-6
    res = dataset_stats("tiny", root=tiny_dataset)
    assert res["summary"]["ALL"]["sessions"] == 2
