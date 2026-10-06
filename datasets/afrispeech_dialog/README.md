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
| Ground-truth rating | **D** - Human transcripts, but timestamps are hand-typed with ~1 s effective precision and are ~0.45 s early on median; overlap/backchannels absent; untimed speech; 3/49 files without times. |
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
| general | 29 | 4.93 | 4.76 | 0.974 | 0.001 | 0.0 | 2/2/2 | 0.026/7.02/94.374 | 0.0717 | 8.96 | 2.41 |
| medical | 17 | 1.7 | 1.4 | 0.87 | 0.002 | 0.0 | 2/2/2 | 0.03/2.05/13.014 | 0.0794 | 3.96 | 12.12 |
| ALL | 46 | 6.63 | 6.16 | 0.948 | 0.001 | 0.0 | 2/2/2 | 0.03/3.01/46.999 | 0.0765 | 4.05 | 4.82 |

Computed by `python -m diards stats afrispeech_dialog` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.afrispeech_dialog.md`](../../results/stats/stats.afrispeech_dialog.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 46 sessions, **0 errors**, 30 warnings (normalized files); 21 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: zero_duration = 63, same_speaker_overlap = 5, negative_duration = 16, negative_start = 1
- checks that fired (sessions): `info:segments_under_50ms` 20, `warning:possible_unannotated_speech` 2, `warning:segments_over_60s` 28
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 1.1% of reference speech; reference speech without energy = 4.7%. Most-flagged sessions: `afrispeech_dialog__392c7093-7347-40b8-ab37-db1dcc90945d` (0.10), `afrispeech_dialog__f533e2de-bac6-4866-8803-b33407813e92` (0.06), `afrispeech_dialog__eceb9468-7001-4ee0-9475-13486e5352ae` (0.04), `afrispeech_dialog__60344b07-b93e-4e14-8b1b-d544d9cd6a16` (0.04), `afrispeech_dialog__4fc2c19e-de60-4be0-91b5-7870f60f2d99` (0.03)
- full report: [`results/validation/validation.afrispeech_dialog.default.md`](../../results/validation/validation.afrispeech_dialog.default.md)
- **Silero VAD x2 audit** (view `default`, from the [VAD study](../../docs/silero_vad_study.md)): 13.86% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 2.59% of reference speech; Whisper finds intelligible speech in 19 of the 20 longest such regions.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (general, medical) | 46 | 6.63 | primary | **25.00** | 4.76 | 15.15 | 5.10 | 31.27 | 22.75 | 93% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/afrispeech_dialog.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 46 | 15.11 | 11.56 | 3.55 | 4.44 | 3.17 | 1.27 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 35 of 40 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (69.6 of 76.4 s). Examples: `afrispeech_dialog__60344b07-b93e-4e14-8b1b-d544d9cd6a16` 471.8-475.2 s: "celebrating their birthday, they were not being reminded that this was the day t"; `afrispeech_dialog__4fc2c19e-de60-4be0-91b5-7870f60f2d99` 533.2-536.4 s: "Okay, I'm going to go through what..."; `afrispeech_dialog__7e832fef-ddde-4f8b-8687-eefcf95fe1ce` 486.6-489.2 s: "worsening over time and change in Boer."

**Time-offset check (default):** 6 of 46 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.45 s; shifted: `afrispeech_dialog__94009039-0507-492f-8b26-e53d20642089` (+0.40 s), `afrispeech_dialog__d2f0bed6-f3e1-48a8-9fb2-ceb137670bc4` (+0.45 s), `afrispeech_dialog__5b8a8e4c-7463-47c4-858f-5cd8dd278d42` (+0.60 s).
<!-- /auto:diagnosis -->

**Reading the AfriSpeech-Dialog numbers: the reference is the main problem.** DER is 26.7% at collar 0 and still
24.5% at 0.25 s. Three independent checks point at the timestamps:
- **Pauses labelled as speech:** 11.6 of the 15.1 points of missed speech fall where the audio is silent (turn times
  are hand-typed around whole turns). In `304d6402...` the two speakers' turns cover 208 s of a 210 s file.
- **Missing speech:** 35 of the 40 longest audible false alarms contain intelligible speech per Whisper (turns
  without times, or times that end early).
- **Systematic shift:** the time-offset check finds the reference about **0.45 s early** (median best lag over
  46 files; 6 files individually clearly shifted, by 0.3-0.6 s). That is consistent with times typed by hand while
  listening.
The model's speaker counting is fine (93% exact). Do not use these timestamps for DER without re-alignment.

**UEM fix (from the Silero VAD study).** Five recordings continue for 48-100 s of conversation after the last
labelled turn (Whisper-confirmed). The UEM is now the transcribed span +/- 1 s, which lowers Nemotron's DER from
26.7% to 25.0% at collar 0 (24.5% to 22.8% at 0.25 s) and its false alarm from 6.4% to 4.8%; the tables above use
the corrected UEM. The study's Silero-based lag search independently confirms the ~0.45 s early reference
(7 of 46 sessions clearly shifted).



## Quality rating

**D.** Valuable domain (medical consultations, African accents), but timestamps at ~1 s precision, missing
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
