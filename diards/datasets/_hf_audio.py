"""Helpers for corpora whose audio is mirrored on the Hugging Face Hub as parquet shards
(``audio`` struct with ``bytes`` + ``path``), e.g. the diarizers-community / talkbank conversions."""
from __future__ import annotations

import io
from pathlib import Path
from typing import Callable, Iterator

import numpy as np
import soundfile as sf

from ..download import hf_download


def list_repo_files(repo_id: str, prefix: str = "", repo_type: str = "dataset") -> list[str]:
    from huggingface_hub import list_repo_files as _lrf

    return sorted(f for f in _lrf(repo_id, repo_type=repo_type) if f.startswith(prefix) and f.endswith(".parquet"))


def iter_parquet_rows(repo_id: str, files: list[str], dest: Path, columns: list[str] | None = None,
                      want: Callable[[dict], bool] | None = None, delete_after: bool = False) -> Iterator[dict]:
    """Yield rows (as python dicts) from parquet shards, downloading each shard on demand."""
    import pyarrow.parquet as pq

    for f in files:
        local = hf_download(repo_id, f, dest)
        pf = pq.ParquetFile(local)
        for i in range(pf.num_row_groups):
            tbl = pf.read_row_group(i, columns=columns)
            for row in tbl.to_pylist():
                if want is None or want(row):
                    yield row
        if delete_after:
            Path(local).unlink(missing_ok=True)


def decode_audio(audio: dict) -> tuple[np.ndarray, int]:
    data, sr = sf.read(io.BytesIO(audio["bytes"]), dtype="float32", always_2d=True)
    return data.mean(axis=1), sr
