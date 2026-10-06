# Earnings-21

44 public earnings calls from 2020 (39 h, nine sectors), released by Rev.com for ASR benchmarking. Speakers are
an operator, company executives and sell-side analysts on the phone. Rev added RTTMs in 2023, so it can serve as
a long-form, many-speaker (up to 20) "business call" diarization test with almost no overlap.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-SA-4.0 ([link](https://creativecommons.org/licenses/by-sa/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free download from GitHub, no registration. |
| Source version used | revdotcom/speech-datasets main (release 202408) |
| Domain | earnings calls (telephone/broadcast) |
| Views (normalized) | `default`: Original call audio (mp3, 24-44.1 kHz) resampled to 16 kHz mono |
| Reference used as primary RTTM | Rev RTTMs (2023) derived from professional human transcripts; timing method undocumented. |
| Ground-truth rating | **B-** - Professional human transcripts with speaker labels (reviewed by senior transcriptionists); segment timings come from an undocumented automatic step. Very little overlap, so labels are easy to keep consistent; short backchannels/crosstalk tend to be absent. |
| Prepared splits (sessions) | eval10: 11, other: 33 |
<!-- /auto:meta -->

## Source and access

- <https://github.com/revdotcom/speech-datasets/tree/main/earnings21> (CC BY-SA 4.0): `media/*.mp3`,
  `transcripts/nlp_references/*.nlp` (token + speaker), `rttms/*.rttm`, `eval10-file-metadata.csv`.
- HF mirror: [`argmaxinc/earnings21`](https://huggingface.co/datasets/argmaxinc/earnings21). Lhotse recipe: `lhotse.recipes.prepare_earnings21`.
- Earnings-22 (125 calls, 119 h, global accents) has no RTTMs and no token timings, so it is not usable for
  diarization scoring without your own alignment.

## Annotation methodology

Professional Rev transcriptionists transcribed each call and senior transcriptionists reviewed it. The `.nlp` files
carry a speaker index per token but **no timestamps**. The 2023 RTTMs give segment timings; Rev does not document how
they were produced (most likely forced alignment of the human transcripts). Release 202408 fixed an off-by-one
speaker-labelling issue in file 4341191.

## Known issues and errata

- Timing method undocumented (see above).
- Calls contain long hold music or operator instructions, and Q&A over phone lines of varying quality.
- Nearly no overlap is labelled; backchannels and crosstalk tend to be absent.
- Split: Rev's `eval10` subset (10 files) plus the remaining 34 (`other`). There is no train/test split.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| eval10 | 11 | 10.32 | 8.44 | 0.818 | 0.0 | 0.0 | 5/11/15 | 0.405/2.582/6.784 | 0.0227 | 0.456 | 1.37 |
| other | 33 | 28.94 | 24.38 | 0.842 | 0.0 | 0.0 | 2/10/20 | 0.456/2.936/9.281 | 0.0186 | 0.472 | 1.22 |
| ALL | 44 | 39.26 | 32.82 | 0.836 | 0.0 | 0.0 | 2/10/20 | 0.439/2.818/8.454 | 0.0198 | 0.456 | 1.26 |

Computed by `python -m diards stats earnings21` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.earnings21.md`](../../results/stats/stats.earnings21.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 44 sessions, **0 errors**, 8 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- checks that fired (sessions): `info:segments_under_50ms` 36, `info:silence_over_30s` 4, `info:speaker_under_1s` 2, `warning:possible_unannotated_speech` 2, `warning:segments_over_60s` 6
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 1.0% of reference speech; reference speech without energy = 1.3%. Most-flagged sessions: `earnings21__4387383` (0.27), `earnings21__4384964` (0.12), `earnings21__4384198` (0.04), `earnings21__4394084` (0.02), `earnings21__4384683` (0.02)
- full report: [`results/validation/validation.earnings21.default.md`](../../results/validation/validation.earnings21.default.md)
- **Silero VAD x2 audit** (view `default`, from the [VAD study](../../docs/silero_vad_study.md)): 3.12% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.43% of reference speech; Whisper finds intelligible speech in 20 of the 20 longest such regions.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (eval10, other) | 44 | 39.26 | primary | **19.54** | 3.56 | 3.99 | 11.99 | 48.01 | 15.90 | 20% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/earnings21.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 44 | 3.97 | 0.56 | 3.41 | 3.35 | 0.86 | 2.49 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 35 of 40 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (74.3 of 80.2 s). Examples: `earnings21__4368670` 1009.0-1012.1 s: "this was due to timing effects from hatching activities"; `earnings21__4394084` 1706.7-1709.7 s: "He missed your dad. He was always fun. He's a good guy."; `earnings21__4346923` 1647.7-1650.6 s: "I didn't hear the second part of the question."

**Time-offset check (default):** 0 of 44 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.05 s.
<!-- /auto:diagnosis -->

**Reading the Earnings-21 numbers: this is mostly a model limit.** DER is 19.5% at collar 0, and **12 points of it
are speaker confusion**. Only 20% of calls get the right speaker count (mean absolute error 3.5 speakers). Earnings
calls in this set have 2-20 labelled speakers (median 10; 31 of 44 calls have more than 8), and Nemotron 3
Diarization outputs **at most 8**: it
returned 8 speakers on 28 of the 44 calls. Analysts who ask one question each get merged into existing speakers.
Speech detection is fine (FA 3.6%, miss 4.0%). Earnings-21 is therefore a good test of *many-speaker* long-form
diarization, which is exactly where 4- and 8-speaker end-to-end models fall short; it is not evidence of bad labels.

One exception found by the Silero VAD study: call **4384964** has fluent speech worth about 12% of its reference
speech with no label at all (confirmed by Nemotron and Whisper; also flagged by the energy-VAD check above, together
with 4387383).



## Quality rating

**B-.** Careful human transcripts and speaker labels on long real calls with many speakers (2-20, median 10). The
segment timing is of unknown provenance and overlap/backchannels are essentially absent, so it tests speaker
counting and long-form tracking more than overlap handling.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare earnings21            # download (resumable) + normalize (idempotent)
python -m diards validate earnings21 --vad     # ground-truth checks
python -m diards stats earnings21
python -m diards export earnings21 --format nemo      # or pyannote / lhotse
python -m diards evaluate earnings21 --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("earnings21", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

M. Del Rio et al., "Earnings-21: A Practical Benchmark for ASR in the Wild", Interspeech 2021.
