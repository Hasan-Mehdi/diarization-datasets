# VAD study progress (branch `vad-study`)

Second, focused session answering Hasan's question: *could Silero VAD help this project at all?* Answered with
experiments, not opinion. Deliverable: [docs/silero_vad_study.md](docs/silero_vad_study.md); numbers in
[results/vad/](results/vad/). The main agent's PROGRESS.md is not touched from this branch.

## Current status

_Last updated: 2026-10-05 21:05 EDT (system clock)_

- **Now doing:** nothing; the study is finished (DONE written).
- **Done:** everything in the brief. Write-up: [docs/silero_vad_study.md](docs/silero_vad_study.md); tables and
  exact commands: [results/vad/README.md](results/vad/README.md).
- **Verdict:** use Silero (run twice, stock + 30 s state reset, frame-wise max = "x2") as a witness for reference
  and UEM QA on close-talk / single-channel audio: its unannotated-speech flags are 70% intelligible speech
  (energy 42%, WebRTC 46%) and found real gaps in AMI, ICSI, Earnings-21, CallHome, CallFriend, AfriSpeech; its
  "% of reference speech called silence" predicts Nemotron's reference-induced miss (Pearson 0.74) and ranks GT
  grades best; it finds speech outside the transcribed span in 36 AMI, 6 ICSI and 5 AfriSpeech sessions (cutting
  the AfriSpeech UEMs lowers Nemotron DER 26.7 -> 25.1%); a Silero channel reference for PriMock57 beats the
  energy one. Do not use it in the Nemotron pipeline (gating worse on 25/25 tags, trimming on 22/25, zeroing on
  21/25, filling only imitates padding), not for VAD-made UEMs, not on far-field audio, and never stock (drop-outs).

## Environment decisions

- Shared env `D:\diarization-data\envs\diar` (Python 3.12.15, torch 2.11.0+cu128, numpy 2.5.3). Installed only
  `silero-vad==6.2.3` (latest on PyPI, 2026-10-05) with `pip install --no-deps`; its only hard dependencies
  (torch >= 1.12, packaging) were already present, so nothing else changed. onnxruntime is not needed: the JIT
  model runs on CPU. `webrtcvad-wheels 2.0.14.post1` was already installed (used as a baseline).
- Silero settings: the package defaults, which are also its documented recommendation (16 kHz, 512-sample
  windows = 32 ms, threshold 0.5, exit threshold 0.35, min speech 250 ms, min silence 100 ms, pad 30 ms).
  Our `silero_probs` + `get_speech_timestamps_from_probs` reproduces `get_speech_timestamps` exactly (checked on a
  PriMock57 session: 160/160 segments identical).
- Speed: ~115-170x real time per CPU thread; 8 worker processes give ~700x real time.
- Outputs: `D:\diarization-data\vad-study\` (VAD cache `vad/`, logs `logs/`). Nothing under `normalized/`,
  `raw/` or the main agent's `work/` is modified.

## Log

- 2026-10-05 16:47: read README, PROGRESS.md, docs, diards package, results; scoring = `diards.score.Scorer`
  (pyannote.metrics, collar half-width 0 / 0.25 s, overlap scored, session UEM). Cached Nemotron hypotheses
  exist under `D:\diarization-data\work\nemotron\<dataset>.<view>\hyp` for every evaluated subset, so output
  gating experiments need no GPU.
- 2026-10-05 16:50: installed silero-vad 6.2.3 (`--no-deps`); added `diards/vads.py` (Silero / WebRTC / energy
  backends + per-session cache) and `scripts/vad_compute_all.sh`; started the full computation in the background.
- 2026-10-05 17:03: PriMock57 per channel (Silero on each isolated channel): TextGrid labels are 10.7% (doctor) /
  14.4% (patient) Silero-silent in >= 0.3 s stretches (energy method: 9.5% / 13.7%); Nemotron DER vs a Silero
  channel reference 9.8% (c=0) / 2.6% (c=0.25), vs energy channel activity 10.4% / 4.1%, vs TextGrids 24.2% / 16.0%.
- 2026-10-05 17:05: first audits (PriMock57, Map Task, CallHome, CallFriend, AfriSpeech, SCOTUS, SBCSAE) and a
  Whisper check on CallHome: all 20 longest Silero "unannotated speech" regions are real speech (missing turns),
  but 17/20 "reference speech Silero calls silence" regions are also real speech: Silero had failed there.
- 2026-10-05 17:09: diagnosed the failure: Silero's recurrent state drifts to a dead regime on long continuous
  speech (CallHome eng_125/eng_123/eng_134, MSDWild 02508, some SBCSAE); not level, band-limit or 8 kHz related
  (fresh state on the same audio gives 71% speech). Added `silero_r30` (state reset every 30 s, 2 s warm-up) to
  the cache and made it the default Silero variant for the audit and pipeline experiments; stock Silero is kept
  for comparison. Earlier audit/Whisper outputs deleted and will be regenerated.
- 2026-10-05 17:12: corrected the timestamps in this file to the system clock (an earlier edit had estimated them).
- 2026-10-05 17:15: pyannote.audio 4.0.7 installed in a separate venv `D:\diarization-data\envs\vad`
  (`python -m venv --system-site-packages`, so it reuses the shared torch; nothing installed into the shared env).
  segmentation-3.0 VAD computed on every evaluated subset on GPU (~800x real time, ~10 min of GPU in total).
- 2026-10-05 17:23: rebased onto origin/main (main agent finished EasyCom / LibriCSS evaluations).
- 2026-10-05 17:45: Whisper check on CallHome with the 30 s-reset variant: 18/20 longest "silent reference" regions
  were still clear speech; stock Silero had high probability there. Fresh starts 1-10 s apart on the same audio
  give either ~0.8 or ~0.0 speech fraction (eng_110, eng_121): the model is bistable on this audio.
- 2026-10-05 17:55: drop-out check (scripts/vad_reset_check.py) on all evaluated subsets; switched the main Silero
  variant to `silero_x2` (frame-wise max of stock and 30 s-reset runs). Outputs made with the earlier variant
  were deleted and the audits, Whisper checks and pipeline runs restarted.
- 2026-10-05 17:57: time-shift check made robust (ignores clips < 120 s and lags at the search edge; MSDWild clips
  produced spurious 3-5 s "shifts"). Silero confirms AfriSpeech-Dialog's ~0.45 s early reference (median lag).
- 2026-10-05 18:15-18:22: memory pressure (8 VAD workers + 6 scoring jobs + Whisper + a re-inference process that
  grew to 14 GB across tags) made the NOTSOFAR-1 sc and ICSI cache jobs fail with MemoryError; re-inference now
  runs one process per tag; missing caches recomputed with fewer workers.
- 2026-10-05 18:20-18:40: added collar-0.25 FA/miss to the audit, Whisper transcript classes (speech / short /
  laughter / none), per-detector correlation with Nemotron error (close-talk vs far-field).
- 2026-10-05 18:40-20:31: session interrupted (usage limit); background jobs kept running and finished the
  audits, Whisper checks, most post-hoc and all but one re-inference runs.
- 2026-10-05 20:32: resumed; INBOX checked (no new messages). Restarted the ICSI cache job and the CHiME-6 dev
  re-inference; wrote docs/silero_vad_study.md.
- 2026-10-05 20:47-20:55: ICSI cache, audit and Whisper check done; AMI post-hoc done (all 25 tags); CHiME-6 dev
  re-inference done. Baseline re-scoring reproduces results/nemotron on all 25 tags; re-running Nemotron on
  unmodified audio reproduces the cached outputs on all 25.
- 2026-10-05 20:50: new check `scripts/vad_uem_check.py`: Silero speech outside the transcribed span inside
  whole-file UEMs (AMI 36 sessions, ICSI 6 incl. test `Bmr013`, AfriSpeech 5; Whisper: all real speech).
  AfriSpeech-Dialog DER 26.69 -> 25.09% with those 5 UEMs cut to the transcribed span.
- 2026-10-05 21:00: results JSON compacted (39 MB -> 17 MB: no indentation, flagged-region evidence only for the
  three Whisper-checked detectors, per-session pipeline rows only for the main variants); report regenerated;
  docs/silero_vad_study.md finalised; 32 tests pass.
- 2026-10-05 21:03: rebased onto origin/main (only PROGRESS.md had changed there; no conflicts), 32 tests pass,
  pushed; appended the verdict and integration list to D:\diarization-data\_session\INBOX.md.
- 2026-10-05 21:05: wrote D:\diarization-data\_vad_session\DONE.
