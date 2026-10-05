"""DER / JER scoring with pyannote.metrics.

Collar convention: ``collar`` here is the md-eval / NeMo / dscore *half-width* (seconds excluded on EACH side of
every reference boundary). pyannote.metrics expects the full width, so ``2 * collar`` is passed to it.
Overlapping speech is always scored (``skip_overlap=False``). Scoring is restricted to the session UEM.
"""
from __future__ import annotations

from typing import Iterable

from .annotation import Segment


def _annotation(segs: Iterable[Segment], uri: str):
    from pyannote.core import Annotation
    from pyannote.core import Segment as PSeg

    ann = Annotation(uri=uri)
    for i, s in enumerate(segs):
        if s.end > s.start:
            ann[PSeg(s.start, s.end), i] = s.speaker
    return ann


def _timeline(uem, uri: str):
    from pyannote.core import Segment as PSeg
    from pyannote.core import Timeline

    return Timeline([PSeg(a, b) for a, b in uem], uri=uri)


class Scorer:
    """Accumulates DER/JER over sessions for one collar value."""

    def __init__(self, collar: float = 0.0):
        from pyannote.metrics.diarization import DiarizationErrorRate, JaccardErrorRate

        self.collar = collar
        self.der = DiarizationErrorRate(collar=2 * collar, skip_overlap=False)
        self.jer = JaccardErrorRate(collar=2 * collar, skip_overlap=False)

    def __call__(self, uri: str, ref: list[Segment], hyp: list[Segment], uem) -> dict:
        r, h, u = _annotation(ref, uri), _annotation(hyp, uri), _timeline(uem, uri)
        d = self.der(r, h, uem=u, detailed=True)
        j = self.jer(r, h, uem=u, detailed=True)
        total = d["total"]
        return {
            "der": d["diarization error rate"],
            "fa": d["false alarm"] / total if total else 0.0,
            "miss": d["missed detection"] / total if total else 0.0,
            "conf": d["confusion"] / total if total else 0.0,
            "jer": j["jaccard error rate"],
            "ref_speech_s": total,
        }

    def summary(self) -> dict:
        acc = self.der.accumulated_
        total = acc["total"]
        return {
            "collar": self.collar,
            "der": abs(self.der),
            "fa": acc["false alarm"] / total if total else 0.0,
            "miss": acc["missed detection"] / total if total else 0.0,
            "conf": acc["confusion"] / total if total else 0.0,
            "jer": abs(self.jer),
            "ref_speech_h": total / 3600,
        }
