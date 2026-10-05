"""diards: free English speaker-diarization datasets in one normalized layout.

Quick use::

    from diards import load_dataset
    for s in load_dataset("ami", split="test", view="sdm"):
        print(s.session_id, s.audio_path, len(s.segments), s.uem)
"""
__version__ = "0.1.0"

from .core import NormalizedDataset, Session, load_dataset  # noqa: E402,F401
