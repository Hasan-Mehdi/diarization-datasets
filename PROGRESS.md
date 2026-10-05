# PROGRESS

Running log for the unattended build of this repo. Work is tracked here, not in GitHub issues (by design).

## Current status

_Last updated: 2026-10-05 16:17 EDT (from the system clock)_

- **Now doing:** Nemotron batches (AMI, CHiME-6, DiPCo, LibriCSS, EasyCom, then MSDWild, AVA-AVD, SBCSAE, Map Task,
  AfriSpeech, SCOTUS), validation batch, and per-dataset "model error vs reference error" diagnosis + Whisper audit.
- **Done so far:** all 18 datasets prepared; `diards` package with exports/tests (19 passing); cards drafted with
  auto-filled numbers (`scripts/make_cards.py`); PRIMOCK57.md; appendix docs/OTHER_DATASETS.md.
  **NeMo 3.1 cross-check:** official NeMo inference and the Transformers port agree within ~1% DER
  ([results/nemo_crosscheck](results/nemo_crosscheck/README.md)).
- **Results so far (Nemotron, collar 0):** VoxConverse test 8.4% (but in training data), CallHome Eng 11.7%,
  NOTSOFAR-1 eval far-field 18.4% vs official utterances / 11.3% vs MFA reference; close-talk mix 14.5% / 9.6%;
  PriMock57 24.2% vs official / 10.4% vs channel activity.
- **New finding:** CallHome English (TalkBank HF version) has unlabelled turns: 38 of the 40 longest audible
  "false alarm" regions contain intelligible speech per Whisper (e.g. eng_037: 121 s of speech with no reference).
- **Next:** finish batches, diagnose every dataset, finalize cards + README recommendations, DONE.
- **Needs Hasan (optional):** free sign-ups for Ego4D, MMCSG, CHiME-9 ECHI, Fearless Steps, MLC-SLM (docs/OTHER_DATASETS.md A).

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

- 2026-10-05 16:17: NeMo 3.1.0 (git) installed in a separate env, cross-check done; diagnosis + Whisper false-alarm audit added; CallHome missing-turn finding.

## Skipped / blocked (with reasons)

- (resolved 13:38) CallHome English: HF access works for Hasan's account; being prepared now.

## Open items

- Everything not marked done in the status table above.
