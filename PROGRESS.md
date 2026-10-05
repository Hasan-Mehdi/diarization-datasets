# PROGRESS

Running log for the unattended build of this repo. Work is tracked here, not in GitHub issues (by design).

## Current status

_Last updated: 2026-10-05 16:01 EDT (from the system clock)_

- **Now doing:** batch Nemotron evaluation (`scripts/run_nemotron_all.sh`) and batch validation with energy VAD
  (`scripts/validate_all.sh`) over all prepared datasets; CHiME-6 eval split and EasyCom still preparing.
- **Done so far:** `diards` package (layout, loader, validator, stats, scorer, Nemotron harness, NeMo/pyannote/Lhotse
  exports, tests). 19 recipes. Prepared and normalized: AMI, ICSI, NOTSOFAR-1, CHiME-6 (dev), DiPCo, LibriCSS,
  VoxConverse, CallHome Eng, CallFriend Eng, Earnings-21, MSDWild-en (894 clips), AVA-AVD-en (96 clips), SBCSAE, Map Task,
  AfriSpeech-Dialog, PriMock57, SCOTUS sample. Dataset cards drafted for all 18 (auto-filled numbers pending).
  [PRIMOCK57.md](PRIMOCK57.md) done. Appendix of excluded / sign-up / paid datasets: [docs/OTHER_DATASETS.md](docs/OTHER_DATASETS.md).
- **Next:** finish evaluations + validation, fill cards (`scripts/make_cards.py`), interpret surprising scores per
  dataset, write README catalog + recommendations, final DONE.
- **Needs Hasan (optional, for later):** free sign-ups I could not do unattended: Ego4D, MMCSG, CHiME-9 ECHI (DUA),
  Fearless Steps, MLC-SLM (Nexdata). Details in docs/OTHER_DATASETS.md, section A.

## Environment decisions

- Data root (audio, caches, envs, model weights): `D:\diarization-data` (C: has ~30 GB free).
  Normalized datasets: `D:\diarization-data\normalized\<dataset>\`; raw downloads: `D:\diarization-data\raw\<dataset>\`.
- Caches: `HF_HOME`, `TORCH_HOME`, `PIP_CACHE_DIR`, `TEMP/TMP` all point under `D:\diarization-data\cache`.
  The HF token from Hasan's other cache (`D:\hf-cache\token`, account `Hmehdi515`) was copied into the new HF_HOME.
- Conda env: `D:\diarization-data\envs\diar` (Python 3.12, because NeMo Speech 3.x requires >= 3.12), not the base env.
- PyTorch 2.11.0+cu128 (supports sm_120 / Blackwell). Transformers 5.19.0.dev0 from source (Nemotron 3 Diarization support).
- WSL is not installed; everything runs natively on Windows.
- Nemotron inference uses the Transformers port in offline mode, which chunks exactly like the model card's
  30.4 s "very high latency" NeMo configuration (chunk 340, right context 40, FIFO 40, update period 300, cache 264).
- Slow official mirrors are replaced by verified mirrors where available (VoxConverse audio from the CC-BY HF mirror:
  the Oxford server delivered ~0.25 MB/s).

## Status

| Area | State |
|---|---|
| Repo skeleton + GitHub (private) | done |
| Candidate research | first pass done (~35 corpora, `docs/research_notes.md`), continuing |
| Conda env + PyTorch CUDA | done |
| Nemotron install (Transformers) | done; NeMo install optional, not attempted yet |
| Normalized layout + `diards` package (prepare/validate/stats/evaluate) | done (core), recipes in progress |
| Recipes verified | ami (test/dev), voxconverse, callfriend_eng, earnings21, afrispeech_dialog; running: notsofar1, icsi, ava_avd_en, maptask, callhome_eng, chime6 (waiting for download) |
| PriMock57 ground-truth analysis | not started |
| Exports (NeMo / pyannote / Lhotse) + tests | not started |
| Nemotron evaluation | harness done; 2-meeting AMI smoke test done |
| Dataset cards | not started |
| README catalog + recommendations | not started (final polish at the end, per Hasan) |

## Log

Times before 13:27 are approximate (reconstructed from commit times).

- ~12:56: created repo skeleton and this file; pushed private repo `Hasan-Mehdi/diarization-datasets`.
- ~13:00: conda env created (first attempt landed in a mangled path `D:\diarization-dataenvsdiar` because of
  bash backslash escaping; deleted it and recreated with PowerShell). Python 3.12 instead of 3.11 because NeMo needs it.
- ~13:00: found the model ("Nemotron 3 Diarization" = `nvidia/Nemotron-3-Diarization`).
- ~13:04: INBOX message from Hasan (13:05: status block + normalization spec) read and acknowledged; adopting it.
- ~13:16: committed the `diards` package (layout, loader, AMI + VoxConverse recipes, validator, stats, scorer, eval).
- 13:27: INBOX message (13:08: use real timestamps) read and acknowledged; log times corrected to commit times.
- 13:27: VoxConverse (448 files), CallFriend English (40 calls) normalized, validated (with energy VAD) and profiled.
  CallHome English blocked on the HF access form (see "Needs Hasan").

- 2026-10-05 13:38: INBOX 13:36 (CallHome access works) read and acknowledged; callhome_eng prepare started.
- 2026-10-05 13:38: recipes added: NOTSOFAR-1, Earnings-21, ICSI, CHiME-6, AVA-AVD (English LID), MSDWild (English LID), Map Task, AfriSpeech-Dialog.

- 13:51: PriMock57 audit committed (PRIMOCK57.md).
- 13:51-15:41: paused by usage limit.
- 2026-10-05 15:42: resumed; all downloads (CHiME-6, DiPCo, SBCSAE, MSDWild) had completed; CHiME-6 + MSDWild prepare started.

- 2026-10-05 16:01: added recipes DiPCo, SBCSAE, LibriCSS, EasyCom (LFS per-file), SCOTUS (Oyez API); cards for all datasets; docs/FORMAT.md, docs/OTHER_DATASETS.md.

## Skipped / blocked (with reasons)

- (resolved 13:38) CallHome English: HF access works for Hasan's account; being prepared now.

## Open items

- Everything not marked done in the status table above.
