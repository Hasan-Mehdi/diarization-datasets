# VAD study progress (branch `vad-study`)

Second, focused session answering Hasan's question: *could Silero VAD help this project at all?* Answered with
experiments, not opinion. Deliverable: [docs/silero_vad_study.md](docs/silero_vad_study.md); numbers in
[results/vad/](results/vad/). The main agent's PROGRESS.md is not touched from this branch.

## Current status

_Last updated: 2026-10-05 17:57 EDT (system clock)_

- **Now doing:** VAD cache for AMI (all meetings) and ICSI (background, CPU); audits + Whisper checks, post-hoc
  pipeline variants (CPU) and re-inference variants (GPU, ~1 h sample per tag) for every other dataset, all with
  the final Silero configuration `silero_x2`.
- **Done:** detectors + cache (`diards/vads.py`), audit (`diards/vad_audit.py`), VAD-assisted scoring
  (`diards/vad_assist.py`, reproduces results/nemotron exactly), Whisper / PriMock57 / data-prep / drop-out /
  report scripts, pyannote segmentation-3.0 baseline (separate venv `envs/vad`), tests (13 passing).
- **Main finding so far:** Silero VAD 6.2.3 is *bistable* on some audio: the same stretch of clear speech gets
  probabilities near 1 or near 0 depending on where the stream started, and a bad state can last minutes. On
  10 s windows that Nemotron and WebRTC (mode 3) both call speech, stock Silero is silent on 0.40% overall,
  25% on CHiME-6 far-field eval, 9% on AVA-AVD, 1.9% on MSDWild, 1.05% on CallHome. Resetting the state every
  30 s gives 0.14%; the frame-wise max of the stock and reset runs (`silero_x2`) 0.07%. On CallHome the 8 kHz
  model path is also stable (1 bad window vs 77 stock). `silero_x2` is now the main Silero variant.
- **Next:** AMI/ICSI audits and pipeline, PriMock57 channel Whisper check, data-prep, report tables, write-up,
  rebase, INBOX message for the main agent.

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
- 2026-10-05 17:23: rebased onto origin/main (main agent finished EasyCom / LibriCSS evaluations).
- 2026-10-05 17:15: pyannote.audio 4.0.7 installed in a separate venv `D:\diarization-data\envs\vad`
  (`python -m venv --system-site-packages`, so it reuses the shared torch; nothing installed into the shared env).
  segmentation-3.0 VAD computed on every evaluated subset on GPU (~800x real time, ~10 min of GPU in total).
- 2026-10-05 17:45: Whisper check on CallHome with the 30 s-reset variant: 18/20 longest "silent reference" regions
  were still clear speech; stock Silero had high probability there. Fresh starts 1-10 s apart on the same audio
  give either ~0.8 or ~0.0 speech fraction (eng_110, eng_121): the model is bistable on this audio.
- 2026-10-05 17:55: drop-out check (scripts/vad_reset_check.py) on all evaluated subsets; switched the main Silero
  variant to `silero_x2` (frame-wise max of stock and 30 s-reset runs). Outputs made with the earlier variant
  were deleted and the audits, Whisper checks and pipeline runs restarted.
- 2026-10-05 17:57: time-shift check made robust (ignores clips < 120 s and lags at the search edge; MSDWild clips
  produced spurious 3-5 s "shifts"). Silero confirms AfriSpeech-Dialog's ~0.45 s early reference (median lag).
