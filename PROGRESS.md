# PROGRESS

Running log for the unattended build of this repo. Work is tracked here, not in GitHub issues (by design).

## Current status

_Last updated: 2026-10-05 13:38 EDT (from the system clock)_

- **Now doing:** dataset recipes (running in background: AMI train split, NOTSOFAR-1, ICSI, AVA-AVD English LID,
  Map Task, CallHome English; downloading: CHiME-6 eval, DiPCo, SBCSAE, MSDWild). Next code: PriMock57, LibriCSS,
  SBCSAE, DiPCo recipes; NeMo / pyannote / Lhotse exports and tests.
- **Done so far:** env + model (Nemotron 3 Diarization via Transformers on the RTX 5080); `diards` package with
  normalized layout, loader, validator (incl. energy VAD), stats, DER/JER scorer, Nemotron harness.
  Verified recipes: AMI, VoxConverse, CallFriend English, Earnings-21, AfriSpeech-Dialog (stats + validation on disk).
- **Findings so far:** AMI forced-aligned vs manual-derived references change Nemotron DER from ~9% to ~18% (2 meetings);
  VoxConverse has 37/448 single-speaker files; CallFriend (TalkBank) turn bullets have 3,074 same-speaker overlaps;
  AfriSpeech-Dialog times are hand-typed with ~1 s effective precision; AVA-AVD has VAD-marked speech without
  speaker labels; CHiME-6's first (enrolment) minute is unannotated (CHiME-7 UEM fixes it).
- **Needs Hasan:** nothing right now (CallHome access confirmed working, thanks).

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

## Skipped / blocked (with reasons)

- (resolved 13:38) CallHome English: HF access works for Hasan's account; being prepared now.

## Open items

- Everything not marked done in the status table above.
