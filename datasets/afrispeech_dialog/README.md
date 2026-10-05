# AfriSpeech-Dialog v1

Intron Health's African-accented English conversations (Nigeria, Kenya, South Africa; 11 accents): 20 simulated
doctor-patient consultations and 29 general-topic conversations (~7 h), recorded remotely. It is one of very few
free *medical-like* two-party English datasets with speaker turns. **The timestamps are weak**: hand-typed, about
1 s effective precision, and missing in a few files.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-NC-SA-4.0 ([link](https://creativecommons.org/licenses/by-nc-sa/4.0/)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free on Hugging Face (not gated). |
| Source version used | huggingface.co/datasets/intronhealth/afrispeech-dialog (main) |
| Domain | medical-like consultations + general conversation |
| Views (normalized) | `default`: Original recording, mono 16 kHz |
| Reference used as primary RTTM | Hand-typed turn start/end times (MM:SS:cc), one speaker turn per entry. |
| Ground-truth rating | **D+** - Human transcripts, but timestamps are hand-typed with ~1 s effective precision, overlap and backchannels are not annotated, and only 30/49 conversations have timestamps. |
| Prepared splits (sessions) | general: 29, medical: 17 |
<!-- /auto:meta -->

## Source and access

- Hugging Face (not gated): [`intronhealth/afrispeech-dialog`](https://huggingface.co/datasets/intronhealth/afrispeech-dialog),
  CC BY-NC-SA 4.0: `data/*.wav` + `metadata.csv` (transcript with embedded times, domain, accent, country).
- Paper: Sanni et al., NAACL 2025 (arXiv:2502.03945). Diarization study: arXiv:2509.21554.

## Annotation methodology

Professional annotators transcribed each conversation and typed a start and end time around every speaker turn,
as `MM:SS:cc` lines before and after `[Speaker N]: text`.

## Known issues and errata

- **Coarse, hand-typed times.** The hundredths field is almost always 96-100 or 00-04 (e.g. `00:06:100`), so the
  times are effectively whole seconds with jitter. A negative value (`00:00:-1`) also occurs.
- **3 of 49 conversations have no timestamps** (46 usable; the card claims 30 timestamped files, 9 medical + 21
  general, but 46 parse in the current release).
- Some general conversations have very few, very long turns (e.g. 5 turns in 6 minutes), so the other speaker's
  backchannels are not separately labelled.
- Overlap is essentially not annotated (0.1% of speech).
- Remote recordings, varying quality.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| general | 29 | 4.93 | 4.76 | 0.965 | 0.001 | 0.0 | 2/2/2 | 0.026/7.02/94.374 | 0.0717 | 8.96 | 2.39 |
| medical | 17 | 1.7 | 1.4 | 0.822 | 0.002 | 0.0 | 2/2/2 | 0.03/2.05/13.014 | 0.0794 | 3.96 | 11.45 |
| ALL | 46 | 6.63 | 6.16 | 0.928 | 0.001 | 0.0 | 2/2/2 | 0.03/3.01/46.999 | 0.0765 | 4.05 | 4.71 |

Computed by `python -m diards stats afrispeech_dialog` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.afrispeech_dialog.md`](../../results/stats/stats.afrispeech_dialog.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 46 sessions, **0 errors**, 35 warnings (normalized files); 21 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: zero_duration = 63, same_speaker_overlap = 5, negative_duration = 16, negative_start = 1
- checks that fired (sessions): `info:segments_under_50ms` 20, `info:silence_over_30s` 5, `warning:possible_unannotated_speech` 7, `warning:segments_over_60s` 28
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 2.8% of reference speech; reference speech without energy = 4.7%. Most-flagged sessions: `afrispeech_dialog__4fc2c19e-de60-4be0-91b5-7870f60f2d99` (0.26), `afrispeech_dialog__c46ac19c-edf5-4bc2-8162-110ff52ef78b` (0.22), `afrispeech_dialog__7e832fef-ddde-4f8b-8687-eefcf95fe1ce` (0.12), `afrispeech_dialog__392c7093-7347-40b8-ab37-db1dcc90945d` (0.11), `afrispeech_dialog__ebcde1b4-bd3b-49b7-b777-e7d87a7cb7f3` (0.09)
- full report: [`results/validation/validation.afrispeech_dialog.default.md`](../../results/validation/validation.afrispeech_dialog.default.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
_Not evaluated yet._
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
_Not run yet._
<!-- /auto:diagnosis -->

## Quality rating

**D+.** Valuable domain (medical consultations, African accents), but timestamps at ~1 s precision, missing
overlap/backchannels, and long merged turns make it unsuitable for precise DER. Use it for speaker-attributed ASR or
coarse turn-level checks, or re-time it (e.g. forced alignment of the transcripts) before scoring diarization.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare afrispeech_dialog            # download (resumable) + normalize (idempotent)
python -m diards validate afrispeech_dialog --vad     # ground-truth checks
python -m diards stats afrispeech_dialog
python -m diards export afrispeech_dialog --format nemo      # or pyannote / lhotse
python -m diards evaluate afrispeech_dialog --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("afrispeech_dialog", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

M. Sanni et al., "Afrispeech-Dialog: A Benchmark Dataset for Spontaneous English Conversations in Healthcare and Beyond", NAACL 2025.
