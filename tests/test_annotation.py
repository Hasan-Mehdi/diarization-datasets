from diards.annotation import (
    Segment,
    format_rttm,
    intersect,
    merge_intervals,
    merge_same_speaker,
    overlap_regions,
    read_rttm,
    read_uem_single,
    subtract,
    total_duration,
    write_uem,
)


def test_merge_intervals_with_gap():
    assert merge_intervals([(0, 1), (1.1, 2), (5, 6)], gap=0.2) == [(0, 2), (5, 6)]
    assert merge_intervals([(0, 1), (1.1, 2)]) == [(0, 1), (1.1, 2)]


def test_intersect_subtract():
    a = [(0, 5), (10, 15)]
    b = [(3, 12)]
    assert intersect(a, b) == [(3, 5), (10, 12)]
    assert subtract(a, b) == [(0, 3), (12, 15)]
    assert total_duration(subtract(a, [])) == 10


def test_overlap_regions_ignores_same_speaker_overlap():
    segs = [Segment(0, 4, "A"), Segment(2, 6, "A"), Segment(3, 5, "B")]
    assert overlap_regions(segs) == [(3, 5)]
    assert overlap_regions(segs, 3) == []


def test_merge_same_speaker():
    segs = [Segment(0, 2, "A"), Segment(1.5, 3, "A"), Segment(1, 2, "B")]
    assert merge_same_speaker(segs) == [Segment(0, 3, "A"), Segment(1, 2, "B")]


def test_rttm_roundtrip(tmp_path):
    segs = [Segment(0.5, 1.25, "spk1"), Segment(2, 3.5, "spk2")]
    p = tmp_path / "x.rttm"
    p.write_text(format_rttm("file1", segs))
    assert read_rttm(p) == {"file1": segs}


def test_uem_roundtrip(tmp_path):
    p = tmp_path / "x.uem"
    write_uem(p, "f", [(1.0, 2.5), (0.0, 0.5)])
    assert read_uem_single(p) == [(0.0, 0.5), (1.0, 2.5)]
