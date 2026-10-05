# PROGRESS

Running log for the unattended build of this repo. Work is tracked here, not in GitHub issues (by design).

## Current status

_Last updated: 2026-10-05 16:39 EDT (from the system clock)_

- **Now doing:** last Nemotron runs (CHiME-6 close-talk + dev, DiPCo, LibriCSS, EasyCom), then diagnosis of those,
  final card numbers, ratings, README findings, DONE.
- **Done:** all 18 datasets prepared, validated and profiled; Nemotron evaluated on 15 of them so far; diagnosis
  tools (energy split, Whisper audit of false alarms, time-offset check) run on most; NeMo cross-check; PRIMOCK57.md.
- **Headline results (Nemotron 3 Diarization, collar 0 / 0.25 s, primary reference):**
  Map Task 7.9 / 1.9; VoxConverse test 8.4 / 5.7 (in training data); AMI test close-talk 9.2 / 3.6 (model card: 9.25);
  AMI SDM 11.3 / 4.7; CallHome Eng 11.7 / 7.2; NOTSOFAR far-field 18.4 / 6.9; MSDWild-en 17.8 / 10.7;
  Earnings-21 19.5 / 15.9 (8-speaker model limit); PriMock57 24.2 / 16.0 (10.4 / 4.1 vs channel activity);
  AfriSpeech 26.7 / 24.5; SBCSAE 27.4 / 24.2; CallFriend 30.8 / 23.2; SCOTUS 31.7 / 30.3; CHiME-6 far-field eval
  37.6 / 25.6; AVA-AVD-en 49.8 / 34.0.
- **Reference problems found by the checks:** CallHome + CallFriend (TalkBank): missing turns (38/40 and 39/40 long
  false alarms are real speech); AfriSpeech: hand-typed times ~0.45 s early + missing turns; SBCSAE, SCOTUS,
  PriMock57, DiPCo, CallFriend: pauses labelled as speech; AMI MFA reference: whole utterances dropped in EN2002
  test meetings; ICSI: one segment ends 35 min after the audio; earlier AVA-AVD claim corrected (labels fine).
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

- 16:20: reproduction check: AMI test ihm-mix vs forced-aligned reference = 9.22% DER here vs 9.25% on the Nemotron model card (AMI Test MHM, 30.4 s config). AMI SDM: 11.35% here (OpenBench reports 0.11).

- CORRECTION: an earlier note said AVA-AVD's `.lab` files mark speech without speaker labels. Wrong: I misread an unsorted RTTM. Checked on all 351 clips, the labs equal the union of the RTTM segments. Card, recipe and catalog fixed.

## Skipped / blocked (with reasons)

- (resolved 13:38) CallHome English: HF access works for Hasan's account; being prepared now.

## Open items

- Everything not marked done in the status table above.
