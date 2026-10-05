# VAD study progress (branch `vad-study`)

Second, focused session answering Hasan's question: *could Silero VAD help this project at all?* Answered with
experiments, not opinion. Deliverable: [docs/silero_vad_study.md](docs/silero_vad_study.md); numbers in
[results/vad/](results/vad/). The main agent's PROGRESS.md is not touched from this branch.

## Current status

_Last updated: 2026-10-05 16:53 EDT (system clock)_

- **Now doing:** computing Silero / WebRTC / energy VAD on every dataset (background, CPU, 8 workers);
  writing the audit module.
- **Next:** audit (coverage + boundaries) on all datasets, Whisper spot-checks of flagged regions, VAD-assisted
  Nemotron scoring, data-prep checks, write-up.

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
