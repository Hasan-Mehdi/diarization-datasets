# PROGRESS

Running log for the unattended build of this repo. Work is tracked here, not in GitHub issues (by design).

## Current status

_Last updated: 2026-10-05 13:40 (local)_

- **Now doing:** designing the normalized dataset layout + `diards` package (prepare / validate / stats / export / loader),
  while downloading the first annotation packages (AMI, VoxConverse, CHiME-6, Map Task, MSDWild, AVA-AVD, PriMock57).
- **Done so far:** private repo created; conda env on D: (Python 3.12, PyTorch 2.11 + CUDA 12.8, RTX 5080 visible);
  identified the model: `nvidia/Nemotron-3-Diarization` (released 2026-09-23, Sortformer successor, 8 speakers);
  first research pass over ~30 candidate corpora (see `docs/research_notes.md`).
- **Next:** core library + tests; per-dataset prepare commands starting with AMI, VoxConverse, CallHome (TalkBank),
  CHiME-6, DiPCo, NOTSOFAR-1; PriMock57 analysis; Nemotron install and first runs.
- **Needs Hasan:** nothing yet.
- **Key early finding:** Nemotron 3 Diarization was trained on ICSI (all), VoxConverse dev+test, AMI train/dev,
  DiPCo dev, NOTSOFAR train/dev, CALLHOME part 1, DIHARD III dev. Scores on those sets are not held-out and will be flagged.

## Environment decisions

- Data root (audio, caches, envs, model weights): `D:\diarization-data` (C: has ~30 GB free).
  Normalized datasets: `D:\diarization-data\normalized\<dataset>\`; raw downloads: `D:\diarization-data\raw\<dataset>\`.
- Caches: `HF_HOME`, `TORCH_HOME`, `PIP_CACHE_DIR`, `TEMP/TMP` all point under `D:\diarization-data\cache`.
- Conda env: `D:\diarization-data\envs\diar` (Python 3.12, because NeMo Speech 3.x requires >= 3.12), not the base env.
- PyTorch 2.11.0+cu128 (supports sm_120 / Blackwell).
- WSL is not installed; everything runs natively on Windows.

## Status

| Area | State |
|---|---|
| Repo skeleton + GitHub (private) | done |
| Candidate research | first pass done, continuing (notes in `docs/research_notes.md`) |
| Conda env + PyTorch CUDA | done |
| Nemotron install (Transformers / NeMo) | in progress |
| Normalized layout + `diards` package | in progress |
| PriMock57 ground-truth analysis | not started |
| Per-dataset prepare commands | not started |
| Validator + stats generator | not started |
| Exports (NeMo / pyannote / Lhotse) + tests | not started |
| Nemotron evaluation | not started |
| Dataset cards | not started |
| README catalog + recommendations | not started (final polish at the end, per Hasan) |

## Log

- 2026-10-05 12:55: created repo skeleton and this file; pushed private repo `Hasan-Mehdi/diarization-datasets`.
- 2026-10-05 13:10: conda env created (first attempt landed in a mangled path `D:\diarization-dataenvsdiar` because of
  bash backslash escaping; deleted it and recreated with PowerShell). Python 3.12 instead of 3.11 because NeMo needs it.
- 2026-10-05 13:20: found the model ("Nemotron 3 Diarization" = `nvidia/Nemotron-3-Diarization`).
- 2026-10-05 13:40: INBOX message from Hasan (13:05: status block + normalization spec) read and acknowledged; adopting it.

## Skipped / blocked (with reasons)

(none yet)

## Open items

- Everything not marked done in the status table above.
