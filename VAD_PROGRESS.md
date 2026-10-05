# VAD study progress (branch `vad-study`)

Second, focused session answering Hasan's question: *could Silero VAD help this project at all?* Answered with
experiments, not opinion. Deliverable: [docs/silero_vad_study.md](docs/silero_vad_study.md); numbers in
[results/vad/](results/vad/). The main agent's PROGRESS.md is not touched from this branch.

## Current status

_Last updated: 2026-10-05 17:12 EDT (system clock)_

- **Now doing:** VAD cache pass over all datasets (background, CPU, 8 workers), now with both stock Silero and
  Silero with a 30 s state reset (see finding below); the first ten datasets get the reset variant added after.
- **Done:** `diards/vads.py` (detectors + cache), `diards/vad_audit.py` (coverage, boundary offsets, lag, evidence
  for flagged regions), `diards/vad_assist.py` (VAD-assisted Nemotron variants scored with the repo's Scorer;
  baseline re-scoring reproduces results/nemotron exactly), `scripts/vad_whisper_check.py`,
  `scripts/vad_primock57_channels.py`, tests (13 passing).
- **Finding so far:** stock Silero (streaming loop, state never reset) gets stuck on some long recordings: on
  CallHome eng_125 its speech probability decays to 0.00 after ~50 s and stays there for most of the call while
  Whisper transcribes fluent speech (speech fraction 6% stock vs 68% with a state reset every 30 s). Also seen on
  eng_123 and MSDWild 02508. Resetting every 30 s (2 s warm-up) fixes it and changes < 1% of frames elsewhere.
- **Next:** audit on all datasets, Whisper spot-checks, post-hoc and re-inference pipeline variants, write-up.

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
