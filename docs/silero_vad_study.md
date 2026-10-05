# Could Silero VAD help this project? A measured answer

<!-- results sections are filled in from results/vad/ (scripts/vad_report.py) -->

## The question

Hasan asked whether [Silero VAD](https://github.com/snakers4/silero-vad) is useful for this catalog of
diarization datasets, and wanted the answer from experiments. Five possible uses were tested, each against
alternatives (a simple energy VAD, WebRTC VAD, pyannote segmentation-3.0, and Nemotron's own speech activity):

1. **Ground-truth auditing**: does VAD speech missing from a reference reveal unannotated speech, and does
   reference speech with no VAD speech reveal padding or mislabelled non-speech?
2. **Boundary precision**: how tight are reference boundaries, and does that explain the DER gaps between
   reference variants of the same recordings?
3. **Diarization pipeline**: does Silero, combined with Nemotron 3 Diarization (gating its output, filling its
   gaps, feeding it trimmed or silenced audio, or deriving UEMs), lower DER/JER?
4. **Data preparation**: UEMs where datasets lack them, trimming long silences, a catalog quality metric.
5. **Baselines**: is Silero better at any of this than the cheaper or stronger alternatives?

## Method

### Detectors

| detector | version / settings | where it runs |
|---|---|---|
| **Silero VAD** | `silero-vad` 6.2.3 (latest on PyPI on 2026-10-05), JIT model, 16 kHz, 32 ms frames, package defaults = its documented recommendation: threshold 0.5 (exit 0.35), min speech 250 ms, min silence 100 ms, 30 ms padding | CPU, 1 thread per process, ~115-170x real time per process |
| **Silero, 30 s reset** (`silero_r30`) | same model and post-processing, but the recurrent state is reset every 30 s (each window warmed up on the preceding 2 s); see "A Silero failure mode" below | CPU |
| WebRTC VAD | `webrtcvad` 2.0.14, 30 ms frames, aggressiveness 2, then the same min-silence / min-speech / padding rules | CPU |
| energy VAD | this repo's `diards.vad.energy_vad` (threshold relative to the recording's noise floor), as used by `diards validate --vad` | CPU |
| pyannote | `pyannote/segmentation-3.0` VAD pipeline (pyannote.audio 4.0.7, min_duration_on/off 0 as on the model card), in a separate venv | GPU, ~800x real time |
| Nemotron | speaker-agnostic union of the cached Nemotron 3 Diarization output (the main benchmark) | cached |

All detectors run on the normalized 16 kHz mono audio. For datasets with a close-talk view (AMI, ICSI,
NOTSOFAR-1, CHiME-6, DiPCo: `ihm-mix`; LibriCSS: `clean-mix`) the audit uses that view, because annotations
were made from close-talk audio; the pipeline experiments use the view Nemotron was scored on.

### Audit metrics (`python -m diards.vad_audit`)

Reference speech = union of the RTTM segments inside the UEM; VAD speech likewise. Per session and dataset:

* **FA / miss** (collar 0): VAD speech outside the reference and reference speech outside VAD speech, as a
  percentage of reference speech.
* **unannotated**: VAD speech chunks >= 0.5 s that are more than 0.25 s from any reference speech (candidates for
  speech missing from the reference).
* **silent reference** (silent-ref): reference speech chunks >= 0.5 s more than 0.25 s from any VAD speech
  (candidates for padding, pauses inside segments, non-speech labelled as speech).
* **boundary offsets**: for each reference "island" (speech separated by >= 0.3 s silence), onset = VAD start -
  reference start and offset = reference end - VAD end, so positive = the reference is wider than the VAD.
* **time shift**: lag (+/- 5 s, 50 ms raster) that maximises agreement between reference and VAD speech.
* For the five longest flagged regions per session: coverage by every other detector, by word timings, by
  Nemotron, and the level above the noise floor.

### Verification (`scripts/vad_whisper_check.py`)

For each dataset and detector, the 20 longest "unannotated" and 20 longest "silent reference" regions were
transcribed with Whisper large-v3 (the main benchmark's criterion: >= 3 words, not a known hallucination, not
repetitive). Words in an "unannotated" region mean the reference really is missing speech; words in a "silent
reference" region mean the detector missed speech. 20 random stretches where both the reference and Silero say
non-speech are the control for the check itself.

### Pipeline experiments (`python -m diards.vad_assist`)

Scored with the repo's `diards.score.Scorer` exactly as `diards evaluate` does (pyannote.metrics, overlap
scored, per-session UEM, collars 0 and 0.25 s half-width, primary and alternative references) on exactly the
sessions of each `results/nemotron/<tag>`. Re-scoring the cached hypotheses with this code reproduces every
number in `results/nemotron` exactly (checked).

* post-hoc, all evaluated sessions: `gate` (keep hypothesis speech only inside VAD speech), `gate+0.25` (VAD
  speech dilated by 0.25 s), `fill` (inside VAD speech, frames where no speaker passes 0.5 get the most probable
  speaker from Nemotron's cached probabilities), `vad_decides` (gate + fill);
* re-inference on a deterministic ~1 h sample per tag (GPU): `trim` (VAD non-speech longer than 1 s shortened to
  0.5 s, output mapped back) and `zero` (audio outside VAD speech +/- 0.25 s set to digital silence); re-running
  on unmodified audio reproduces the cached hypotheses exactly;
* protocol variants (they change what is scored, so they are not improvements): UEM cut to the VAD speech span,
  or to VAD speech +/- 0.5 s.

## A Silero failure mode found on the way: drop-outs from its recurrent state

The first Whisper check on CallHome English showed that 17 of the 20 longest "reference speech that Silero calls
silence" regions were fluent, loud speech that Nemotron, WebRTC, the energy VAD and pyannote all detected. The
cause is Silero's recurrent state. `get_speech_timestamps` runs the model frame by frame and never resets the
state; on some audio the model is **bistable**: the same stretch of clear speech gets probabilities near 1 or near
0 depending on where the stream started, and the bad state can last for minutes. Per-minute speech fraction on
CallHome `eng_125` (12.4 min):

| detector | min 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Silero, stock streaming | 44 | 0 | 0 | 1 | 0 | 4 | 35 | 8 | 0 | 0 | 3 | 0 | 0 |
| Silero, state reset every 30 s | 72 | 79 | 72 | 77 | 81 | 69 | 76 | 74 | 75 | 75 | 79 | 49 | 79 |
| Nemotron 3 Diarization | 80 | 81 | 72 | 77 | 80 | 69 | 78 | 74 | 77 | 75 | 77 | 81 | 77 |
| WebRTC (mode 2) | 84 | 87 | 78 | 86 | 86 | 76 | 83 | 80 | 82 | 82 | 85 | 87 | 85 |
| reference | 89 | 90 | 82 | 84 | 88 | 70 | 81 | 88 | 88 | 92 | 90 | 94 | 95 |

It is not the level, the telephone band or a decoding problem: a fresh model state started 1-10 s apart on
the same audio gives either ~80% or ~0% speech for the same 20 s (CallHome `eng_110`, `eng_121`), and resetting
every 30 s creates new drop-outs elsewhere. Measured on every evaluated subset (`scripts/vad_reset_check.py`):
a 10 s window counts as clear speech when Nemotron covers >= 50% of it and WebRTC in its strictest mode fires on
>= 50% of its frames; Silero *drops out* when its maximum probability in such a window is below 0.2.
