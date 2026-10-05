# PROGRESS

Running log for the unattended build of this repo. Newest entries at the bottom of each section.
Work is tracked here, not in GitHub issues (by design).

## Environment decisions

- Data root (audio, caches, envs, model weights): `D:\diarization-data` (C: has ~30 GB free).
- Caches: `HF_HOME`, `TORCH_HOME`, `PIP_CACHE_DIR`, `TEMP/TMP` all point under `D:\diarization-data\cache`.
- Conda env: `D:\diarization-data\envs\diar` (Python 3.11), not the base env.

## Status

| Area | State |
|---|---|
| Repo skeleton + GitHub (private) | in progress |
| Candidate research | not started |
| Conda env + NeMo/Sortformer install | not started |
| PriMock57 ground-truth analysis | not started |
| Per-dataset download/prepare scripts | not started |
| Validator + stats generator | not started |
| Nemotron/Sortformer evaluation | not started |
| Dataset cards | not started |
| README catalog + recommendations | not started |

## Log

- 2026-10-05: created repo skeleton and this file.

## Skipped / blocked (with reasons)

(none yet)

## Open items

- Everything in the status table above.
