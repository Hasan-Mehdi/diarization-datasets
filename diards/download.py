"""Resumable downloads with optional checksums, plus small helpers for archives, Hugging Face and git.

Every helper is idempotent: if the target already exists (and matches the checksum when one is given),
nothing is downloaded again.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tarfile
import time
import zipfile
from pathlib import Path

import requests

CHUNK = 1 << 20
USER_AGENT = "diards/0.1 (+https://github.com/Hasan-Mehdi/diarization-datasets)"


def file_hash(path: str | Path, algo: str = "md5") -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def _check(path: Path, md5: str | None, sha256: str | None) -> bool:
    if md5 and file_hash(path, "md5") != md5.lower():
        return False
    if sha256 and file_hash(path, "sha256") != sha256.lower():
        return False
    return True


def download(url: str, dst: str | Path, md5: str | None = None, sha256: str | None = None,
             retries: int = 5, headers: dict | None = None, quiet: bool = False) -> Path:
    """Download ``url`` to ``dst`` with HTTP range resume. Verifies md5/sha256 when given."""
    dst = Path(dst)
    part = dst.with_name(dst.name + ".part")
    if dst.exists():
        if md5 or sha256:
            if not _check(dst, md5, sha256):
                raise RuntimeError(f"checksum mismatch for existing file {dst}; delete it to re-download")
            return dst
        expected = remote_size(url, headers)
        if expected is None or dst.stat().st_size >= expected:
            return dst
        # a truncated file (e.g. left by an interrupted external tool): resume it
        print(f"  [download] {dst.name} is incomplete ({dst.stat().st_size} < {expected}); resuming", flush=True)
        os.replace(dst, part)
    dst.parent.mkdir(parents=True, exist_ok=True)
    hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
    for attempt in range(1, retries + 1):
        try:
            have = part.stat().st_size if part.exists() else 0
            h = dict(hdrs)
            if have:
                h["Range"] = f"bytes={have}-"
            with requests.get(url, headers=h, stream=True, timeout=60, allow_redirects=True) as r:
                if r.status_code == 416:  # already complete
                    break
                r.raise_for_status()
                mode = "ab" if have and r.status_code == 206 else "wb"
                total = r.headers.get("Content-Length")
                total = int(total) + (have if mode == "ab" else 0) if total else None
                done = have if mode == "ab" else 0
                t0 = time.time()
                last = 0.0
                with open(part, mode) as fh:
                    for block in r.iter_content(CHUNK):
                        fh.write(block)
                        done += len(block)
                        if not quiet and time.time() - last > 30:
                            last = time.time()
                            rate = (done - have) / max(1e-6, last - t0) / 1e6
                            pct = f"{100 * done / total:.1f}%" if total else f"{done / 1e6:.0f} MB"
                            print(f"  [download] {dst.name}: {pct} ({rate:.1f} MB/s)", flush=True)
            break
        except (requests.RequestException, OSError) as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if attempt == retries or (status is not None and 400 <= status < 500 and status not in (408, 429)):
                raise  # missing files (404/403/410) will not appear by retrying
            print(f"  [download] {dst.name}: attempt {attempt} failed ({exc}); retrying", flush=True)
            time.sleep(min(60, 5 * attempt))
    if (md5 or sha256) and not _check(part, md5, sha256):
        raise RuntimeError(f"checksum mismatch for {url}")
    os.replace(part, dst)
    return dst


def remote_size(url: str, headers: dict | None = None) -> int | None:
    """Content-Length of ``url`` via HEAD (following redirects), or None if unknown."""
    try:
        r = requests.head(url, headers={"User-Agent": USER_AGENT, **(headers or {})}, allow_redirects=True, timeout=30)
        if r.ok and r.headers.get("Content-Length"):
            return int(r.headers["Content-Length"])
    except requests.RequestException:
        pass
    return None


def extract(archive: str | Path, dest: str | Path, marker: str | None = None, members: list[str] | None = None) -> Path:
    """Extract a zip/tar archive once (a ``.extracted-<name>`` marker file records completion)."""
    archive, dest = Path(archive), Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    mark = dest / (marker or f".extracted-{archive.name}")
    if mark.exists():
        return dest
    name = archive.name.lower()
    if name.endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            z.extractall(dest, members=members)
    elif any(name.endswith(s) for s in (".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")):
        with tarfile.open(archive) as t:
            sel = [m for m in t.getmembers() if members is None or m.name in members]
            try:
                t.extractall(dest, members=sel, filter="data")
            except TypeError:  # Python < 3.12
                t.extractall(dest, members=sel)
    else:
        raise ValueError(f"unknown archive type: {archive}")
    mark.write_text("ok\n")
    return dest


def git_clone(url: str, dest: str | Path, ref: str | None = None, sparse: list[str] | None = None,
              lfs: bool = False) -> Path:
    """Shallow clone (optionally sparse) of a git repository; no-op if ``dest`` already has a checkout."""
    dest = Path(dest)
    if (dest / ".git").exists():
        return dest
    env = dict(os.environ)
    if not lfs:
        env["GIT_LFS_SKIP_SMUDGE"] = "1"
    cmd = ["git", "clone", "--depth", "1"]
    if ref:
        cmd += ["--branch", ref]
    if sparse:
        cmd += ["--filter=blob:none", "--sparse"]
    subprocess.run(cmd + [url, str(dest)], check=True, env=env)
    if sparse:
        subprocess.run(["git", "-C", str(dest), "sparse-checkout", "set", *sparse], check=True, env=env)
    return dest


def hf_download(repo_id: str, filename: str, dest_dir: str | Path, repo_type: str = "dataset",
                revision: str | None = None) -> Path:
    """Download one file from the Hugging Face Hub (resumable, uses the HF cache and token)."""
    from huggingface_hub import hf_hub_download

    return Path(hf_hub_download(repo_id, filename, repo_type=repo_type, revision=revision,
                                local_dir=str(dest_dir)))


def hf_snapshot(repo_id: str, dest_dir: str | Path, allow_patterns: list[str] | None = None,
                repo_type: str = "dataset", revision: str | None = None) -> Path:
    from huggingface_hub import snapshot_download

    return Path(snapshot_download(repo_id, repo_type=repo_type, revision=revision, local_dir=str(dest_dir),
                                  allow_patterns=allow_patterns))


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"required tool '{name}' not found on PATH")
    return path
