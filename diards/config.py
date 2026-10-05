"""Where data lives.

Everything large (raw downloads, normalized audio, model outputs) lives outside the repo.

* ``DIARDS_ROOT``  - root of the normalized datasets (one sub-directory per dataset).
* ``DIARDS_RAW``   - where raw downloads and extracted archives are kept.
* ``DIARDS_WORK``  - scratch space for evaluation outputs (hypothesis RTTMs, logs).

Defaults: on Windows, if ``D:\\diarization-data`` exists it is used (this repo was built on a machine whose C: drive
is nearly full); otherwise ``~/diarization-data``.
"""
from __future__ import annotations

import os
from pathlib import Path


def _base() -> Path:
    env = os.environ.get("DIARDS_BASE")
    if env:
        return Path(env)
    win_default = Path("D:/diarization-data")
    if os.name == "nt" and win_default.exists():
        return win_default
    return Path.home() / "diarization-data"


def normalized_root(override: str | os.PathLike | None = None) -> Path:
    if override:
        return Path(override)
    return Path(os.environ.get("DIARDS_ROOT", _base() / "normalized"))


def raw_root(override: str | os.PathLike | None = None) -> Path:
    if override:
        return Path(override)
    return Path(os.environ.get("DIARDS_RAW", _base() / "raw"))


def work_root(override: str | os.PathLike | None = None) -> Path:
    if override:
        return Path(override)
    return Path(os.environ.get("DIARDS_WORK", _base() / "work"))
