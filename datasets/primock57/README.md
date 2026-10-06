# PriMock57

57 mock primary-care consultations held as remote video calls (7 Babylon clinicians, 57 staff acting as patients
from case cards), ~8.6 h, with doctor and patient on **separate channels**. Released for ASR and note-generation
research. **Full ground-truth audit: [PRIMOCK57.md](../../PRIMOCK57.md).** In short, the official utterance
timings are padded and ASR-oriented, but the clean separate channels let us derive a much tighter reference.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-4.0 ([link](https://github.com/babylonhealth/primock57/blob/main/LICENSE.md)) |
| Annotations redistributable here | yes |
| Access | Free download from GitHub (audio in Git LFS). |
| Source version used | babylonhealth/primock57 (git HEAD) |
| Domain | medical consultations (remote, 2 speakers) |
| Views (normalized) | `mix`: Doctor + patient channels summed (as scripts/mix_audio.sh) |
| Reference used as primary RTTM | Utterance-level TextGrid transcripts per channel (made for ASR evaluation). |
| Ground-truth rating | **D (official) / B (channel-based RTTMs)** - Utterance-level, ASR-oriented timings; see PRIMOCK57.md for measured problems. |
| Prepared splits (sessions) | all: 57 |
<!-- /auto:meta -->

## Source and access

- <https://github.com/babylonhealth/primock57> (CC BY 4.0). Audio in Git LFS (`audio/<consultation>_{doctor,patient}.wav`,
  16 kHz); also downloadable per file from `media.githubusercontent.com`. Transcripts: `transcripts/*.TextGrid`.

## Annotation methodology

Per the repo: "The transcription is done on an utterance level; the transcriber first identified utterances in the
audio, then provided timings for the utterance along with a transcription." There is one Praat tier per channel.
Tags: `<UNSURE>`, `<UNIN/>`.

This repo adds `rttm_alt/channel_activity`: when each person is actually making sound, measured on their own
channel (the channels are isolated by ~50 dB). The same RTTMs are published under
[`results/primock57/channel_activity_rttm/`](../../results/primock57/channel_activity_rttm/) (CC BY 4.0 allows it).

The Silero VAD study added a second channel-based reference, `rttm_alt/silero_channel`: Silero VAD ("x2") on each
speaker's isolated channel ([`results/vad/primock57/silero_channel_rttm/`](../../results/vad/primock57/silero_channel_rttm/)).
It is more speech-specific (Whisper: 22 of the 30 longest regions that only the energy reference marks are breath or
noise), and Nemotron scores **9.85% / 2.55%** against it (collar 0 / 0.25 s). It is the best available reference
for PriMock57 diarization scoring.

## Known issues and errata (measured, see PRIMOCK57.md)

- 9.5% (doctor) / 13.7% (patient) of labelled time is silence of >= 0.3 s on the speaker's own channel.
- 607 utterances are longer than 10 s, up to 27 s, often several sentences with long pauses.
- Overlap is inflated: 6.3% of speech per the TextGrids vs 3.7% measured on the channels.
- Coverage and speaker attribution are good: only ~2.4 min of unlabelled own-channel activity in 8.6 h.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| all | 57 | 8.64 | 7.92 | 0.917 | 0.063 | 0.0 | 2/2/2 | 0.594/2.65/15.149 | 0.0 | 3.506 | 9.58 |
| ALL | 57 | 8.64 | 7.92 | 0.917 | 0.063 | 0.0 | 2/2/2 | 0.594/2.65/15.149 | 0.0 | 3.506 | 9.58 |

Computed by `python -m diards stats primock57` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.primock57.md`](../../results/stats/stats.primock57.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `mix`: 57 sessions, **0 errors**, 19 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- checks that fired (sessions): `warning:segments_over_60s` 19
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 0.3% of reference speech; reference speech without energy = 1.2%. Most-flagged sessions: `primock57__day4_consultation08` (0.01), `primock57__day4_consultation10` (0.01), `primock57__day1_consultation02` (0.01), `primock57__day4_consultation09` (0.01), `primock57__day1_consultation09` (0.01)
- full report: [`results/validation/validation.primock57.mix.md`](../../results/validation/validation.primock57.mix.md)
- **Silero VAD x2 audit** (view `mix`, from the [VAD study](../../docs/silero_vad_study.md)): 14.56% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.01% of reference speech; Whisper finds intelligible speech in 0 of the 1 longest such regions.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| mix (all) | 57 | 8.64 | primary | **24.15** | 0.10 | 24.00 | 0.05 | 24.92 | 15.99 | 84% |
| mix (all) | 57 | 8.64 | channel_activity | **10.38** | 1.12 | 9.15 | 0.11 | 10.55 | 4.08 | 84% |
| mix (all) | 57 | 8.64 | silero_channel | **9.85** | 1.74 | 7.99 | 0.12 | 10.08 | 2.55 | 84% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/primock57.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| mix | mix | 57 | 20.03 | 8.61 | 11.42 | 0.07 | 0.04 | 0.03 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (mix):** 0 of 0 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (0 of 0 s).

**Time-offset check (mix):** 0 of 57 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.05 s.
<!-- /auto:diagnosis -->

Against the official TextGrids almost all error is "missed speech", and 80% of it falls where the labelled
speaker's own microphone is silent. Against the channel-activity reference the DER drops from 24.2% to 10.4%
(collar 0). The model is fine here; the reference is the problem.

## Quality rating

**D** for the official TextGrids as a diarization reference (padded utterances, inflated overlap). **B** with the
channel-based references from this repo (`silero_channel` preferred; `channel_activity` also counts breaths and
coughs). Both are automatic, but measured on isolated close-talk channels.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare primock57            # download (resumable) + normalize (idempotent)
python -m diards validate primock57 --vad     # ground-truth checks
python -m diards stats primock57
python -m diards export primock57 --format nemo      # or pyannote / lhotse
python -m diards evaluate primock57 --view mix  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("primock57", view="mix"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

A. Papadopoulos Korfiatis, F. Moramarco, R. Sarac, A. Savkov, "PriMock57: A Dataset Of Primary Care Mock Consultations", ACL 2022.
