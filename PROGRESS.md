# PROGRESS

Running log for the unattended build of this repo. Work is tracked here, not in GitHub issues (by design).

## Current status

_Last updated: 2026-10-05 21:13 EDT (from the system clock)_

- **State: COMPLETE.** All items of the brief and of every INBOX message are done and pushed, including the
  integration of the Silero VAD study (branch `vad-study` merged). DONE marker written.
- **Delivered:** 18 free English datasets downloaded, normalized (one layout, NeMo/pyannote/Lhotse exports), validated
  (label sanity + energy VAD), profiled, evaluated with Nemotron 3 Diarization (25 dataset/view runs, collar 0 and
  0.25 s, every reference variant), and diagnosed (energy split, Whisper audit of false alarms, time-offset check).
  Cards for every dataset, README catalog/recommendations/findings, PRIMOCK57.md, appendix of 20+ excluded datasets.
- **Headline results (Nemotron 3 Diarization, collar 0 / 0.25 s, primary reference):** Map Task 7.9 / 1.9;
  VoxConverse test 8.4 / 5.7 (in training data); AMI test close-talk 9.2 / 3.6 (model card 9.25); AMI SDM 11.3 / 4.7;
  CallHome Eng 11.7 / 7.2; LibriCSS room 14.3 / 13.0 (clean mix 5.1); NOTSOFAR far-field 18.4 / 6.9;
  MSDWild-en 17.8 / 10.7; Earnings-21 19.5 / 15.9; PriMock57 24.2 / 16.0 (9.85 / 2.55 vs Silero per-channel reference);
  AfriSpeech 25.0 / 22.8 (after UEM fix); SBCSAE 27.4 / 24.2; DiPCo close-talk 27.3 / 19.4; EasyCom 30.4 / 21.7;
  CallFriend 30.8 / 23.2; SCOTUS 31.7 / 30.3; CHiME-6 far-field 37.6 / 25.6; AVA-AVD-en 49.8 / 34.0.
- **Needs Hasan (optional):** free sign-ups I could not do unattended: Ego4D, MMCSG, CHiME-9 ECHI, Fearless Steps,
  MLC-SLM (steps in docs/OTHER_DATASETS.md section A). After signing up, add a recipe following diards/datasets/*.py.

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
| Candidate research | done: ~40 corpora checked (`docs/research_notes.md`, `docs/OTHER_DATASETS.md`) |
| Conda env + PyTorch CUDA | done |
| Nemotron (Transformers) + NeMo 3.1 cross-check | done (agree within ~1% DER) |
| Normalized layout + `diards` package (prepare/validate/stats/export/evaluate/diagnose) | done |
| Recipes (18 datasets, all prepared and normalized) | done |
| Validation (incl. energy VAD) + statistics, all datasets | done |
| Exports (NeMo / pyannote / Lhotse) + tests (19 passing) | done |
| PriMock57 ground-truth analysis (PRIMOCK57.md) | done |
| Nemotron evaluation on every dataset | done (25 dataset/view runs) |
| Diagnosis (energy split, Whisper false-alarm audit, time-offset check) | done for every evaluated dataset/view |
| Dataset cards (18) | done, auto blocks filled by `scripts/make_cards.py` |
| README catalog + recommendations + findings | done |

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

- 2026-10-05 16:47: CHiME-6 dev/eval, DiPCo, LibriCSS evaluated and diagnosed; ratings finalized; dataset.json refreshed; README TL;DR + recommendations + findings written; 0 broken links.

- 2026-10-05 16:49: EasyCom + LibriCSS evaluated and diagnosed; all cards and tables regenerated.

- 2026-10-05 16:49: INBOX 16:49 (parallel Silero VAD study in worktree `diarization-datasets-vad`, branch `vad-study`) read and
  acknowledged. I will not touch that worktree/branch or duplicate its audit, and will integrate its recommendations when
  it reports. Shared env: torch 2.11.0+cu128, torchaudio 2.11.0+cu128, numpy 2.5.3 unchanged since setup; packages I
  added to it: transformers (git), accelerate, pyannote.metrics/core/database, lhotse 1.33.0, gdown, pytest,
  soundfile, soxr, librosa, datasets (no torch/numpy changes). NeMo lives in a separate env (`envs/nemo`).

- 18:43-20:32: paused by usage limit (launcher waited).
- 2026-10-05 20:32: resumed; no VAD-study verdict in INBOX yet; waiting.

- 21:04: INBOX 21:03 (VAD study verdict) read and acknowledged. Merged `origin/vad-study` (fast-forward, files only
  added; 32 tests pass). Integrated its recommendations: ICSI and AfriSpeech-Dialog UEMs cut to the transcribed span
  +/- 1 s (AfriSpeech DER 26.7 -> 25.0%; ICSI unchanged for Nemotron); PriMock57 `rttm_alt/silero_channel`
  (Nemotron 9.85% / 2.55%); `diards validate --vad --vad-backend silero_x2` (energy remains default/fallback);
  optional `silero-vad` requirement (`--no-deps`); Silero metrics column in the catalog and Silero audit line in every
  card; card findings for AMI (MFA drops in train/dev, 36 meetings with speech outside the transcript), Earnings-21
  (call 4384964 ~12% unlabelled), ICSI, AfriSpeech, PriMock57; README section on the study. VAD_PROGRESS.md kept as
  the study's log.
- 2026-10-05 21:11: refresh of stats/validation/diagnosis for the re-prepared datasets.

- 2026-10-05 21:13: final refresh done (ICSI/AfriSpeech/PriMock57 stats, validation, diagnosis), numbers updated, 0 broken links, 32 tests pass; DONE written.

## Skipped / blocked (with reasons)

- **Free datasets needing a manual sign-up** (cannot be completed unattended; documented with steps in
  `docs/OTHER_DATASETS.md`, section A): Ego4D AVD (license + emailed AWS keys), MMCSG (Meta registration),
  CHiME-9 ECHI (HF gated, manual DUA; our token gets 403), Fearless Steps (NIST OpenSAT registration),
  MLC-SLM English (Nexdata registration), CHiME-9 MCoRec (HF DUA), This American Life (Kaggle account + dead audio links).
- **Paid / LDC-only**: listed in the README appendix, not downloaded (Fisher, Switchboard, CALLHOME SRE, DIHARD III,
  Mixer 6, RT meetings, ISL, CHIL, MGB).
- **Weak or automatic labels** (CANDOR, Seamless Interaction, M3SD, Buckeye, Fareez OSCE, Earnings-22): not prepared;
  reasons in `docs/OTHER_DATASETS.md` section C. Seamless Interaction was not sample-verified (27 TB, labels automatic).
- **CHiME-6 train (97 GB)** not downloaded; dev + eval are prepared and evaluated (recipe supports `--split train`).
- **Native-Windows NeMo**: the PyPI 3.0.0 release cannot load Nemotron 3 Diarization; NeMo from git works with
  `TORCHDYNAMO_DISABLE=1` and numpy inputs (documented in results/nemo_crosscheck). Evaluation uses Transformers.
- (resolved 13:38) CallHome English HF access.

## Open items

- None that can be done unattended. Possible future work: sample-verify Seamless Interaction (automatic labels), add
  recipes for the sign-up datasets once Hasan registers, re-align SBCSAE/AfriSpeech/SCOTUS transcripts with a
  forced aligner to produce tight references.
