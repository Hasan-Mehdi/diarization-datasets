# CHiME-6 (CHiME-5 dinner parties)

Twenty real dinner parties in people's homes (kitchen, dining room, living room), four participants each, about
2.5 h per session. Recorded with six Kinect arrays and a binaural close-talk mic per participant. This is the
hardest free English conversational benchmark: lots of overlap, far-field, moving speakers, real home noise.
Since 2024 it is CC BY-SA 4.0, so it can also be used commercially.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-SA-4.0 ([link](https://creativecommons.org/licenses/by-sa/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free download from OpenSLR (dev 11 GB, eval 12 GB, train 97 GB), no registration. |
| Source version used | OpenSLR SLR150 (CHiME6_dev/eval.tar.gz, CHiME6_transcriptions.tar.gz); nateanl/chime6_rttm |
| Domain | dinner party (home, far-field) |
| Views (normalized) | `farfield`: Channel 1 of the session's most frequent reference Kinect array; `ihm-mix`: Sum of the 4 participants' binaural close-talk microphones |
| Reference used as primary RTTM | Official Track 2 forced-alignment RTTM (primary); manual utterance segments (alternative). |
| Ground-truth rating | **A-** - Every participant wore a binaural mic and was transcribed manually; the official diarization reference is forced-aligned (pauses removed), overlap fully covered. Highly overlapped, far-field, very challenging. Enrolment minute not annotated (handled by UEM). |
| Prepared splits (sessions) | dev: 2, eval: 2 |
<!-- /auto:meta -->

## Source and access

- OpenSLR [SLR150](https://www.openslr.org/150/): `CHiME6_dev.tar.gz` (11 GB), `CHiME6_eval.tar.gz` (12 GB),
  `CHiME6_train.tar.gz` (97 GB), `CHiME6_transcriptions.tar.gz` (2.4 MB). The EU mirror `openslr.elda.org` was ~6x
  faster than `www.openslr.org` when tested. The recipe streams only the needed channels out of the tarballs.
- Official Track 2 diarization references ("alignment RTTM"): <https://github.com/nateanl/chime6_rttm>.
  Forced-alignment segmentation for train (CHiME-7): <https://github.com/chimechallenge/CHiME6_falign>.
- Data-generation scripts used by CHiME-7/8 DASR: <https://github.com/chimechallenge/chime-utils>.
- HF mirror (audio): [`argmaxinc/chime-6`](https://huggingface.co/datasets/argmaxinc/chime-6). Lhotse recipe: `lhotse.recipes.prepare_chime6`.

## Annotation methodology

Every participant's binaural mic was transcribed manually with utterance start/end times. CHiME-6 re-synchronised
all devices (fixing CHiME-5's drift) and published two diarization references: the **annotation RTTM** (human
utterance boundaries, which include intra-utterance pauses) and the **alignment RTTM** (triphone GMM-HMM forced
alignment of the transcripts inside the manual segments, silence removed). The alignment RTTM is the official
Track 2 reference and is the primary reference here. The human one is in `rttm_alt/annotation`.

## Known issues and errata

- **First minute not annotated.** Each session starts with a speaker-enrolment section that was not transcribed but
  was *scored* in CHiME-6, inflating false alarms. CHiME-7/8 fixed this with UEMs that start at the first annotated
  utterance; this recipe does the same.
- CHiME-7 moved S19/S20 from train to eval and harmonised transcription conventions. Results on "CHiME-6" from
  different years are not directly comparable.
- Some arrays are missing or faulty in some sessions. The `farfield` view uses CH1 of the array most often marked
  as the utterance reference array (`ref`) in the transcription JSON.
- The audio tarball for transcriptions has trailing garbage (gzip warns); members extract fine.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| dev | 2 | 4.46 | 3.39 | 0.764 | 0.286 | 0.0521 | 4/4/4 | 0.17/0.95/4.702 | 0.0619 | 1.42 | 33.66 |
| eval | 2 | 5.21 | 3.46 | 0.667 | 0.226 | 0.0447 | 4/4/4 | 0.18/0.92/3.83 | 0.058 | 2.11 | 30.95 |
| ALL | 4 | 9.67 | 6.85 | 0.712 | 0.255 | 0.0484 | 4/4/4 | 0.18/0.93/4.25 | 0.0599 | 1.76 | 32.2 |

Computed by `python -m diards stats chime6` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.chime6.md`](../../results/stats/stats.chime6.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `ihm-mix`: 4 sessions, **0 errors**, 2 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- checks that fired (sessions): `info:segments_under_50ms` 4, `info:silence_over_30s` 2, `warning:possible_unannotated_speech` 2
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 4.2% of reference speech; reference speech without energy = 8.7%. Most-flagged sessions: `chime6__S21` (0.08), `chime6__S01` (0.06), `chime6__S02` (0.02), `chime6__S09` (0.01)
- full report: [`results/validation/validation.chime6.ihm-mix.md`](../../results/validation/validation.chime6.ihm-mix.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| farfield (eval) | 2 | 5.21 | primary | **37.63** | 8.27 | 21.29 | 8.07 | 39.40 | 25.61 | 0% |
| farfield (eval) | 2 | 5.21 | annotation | **43.62** | 1.49 | 36.15 | 5.98 | 46.85 | 34.28 | 0% |
| ihm-mix (eval) | 2 | 5.21 | primary | **32.76** | 10.12 | 16.60 | 6.05 | 33.78 | 22.49 | 50% |
| ihm-mix (eval) | 2 | 5.21 | annotation | **37.81** | 1.90 | 31.65 | 4.25 | 40.11 | 29.04 | 50% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/chime6.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| farfield | ihm-mix | 3 | 9.22 | 2.03 | 7.19 | 5.62 | 3.45 | 2.17 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).
<!-- /auto:diagnosis -->

## Quality rating

**A-.** Everyone was on a close-talk mic and transcribed manually, and the official reference is forced-aligned
with silences removed. Overlap is fully represented. Minus: forced alignment rather than hand-placed boundaries,
and the enrolment-minute issue (handled by the UEM).

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare chime6            # download (resumable) + normalize (idempotent)
python -m diards validate chime6 --vad     # ground-truth checks
python -m diards stats chime6
python -m diards export chime6 --format nemo      # or pyannote / lhotse
python -m diards evaluate chime6 --view farfield  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("chime6", view="farfield"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

The train split (97 GB) is not prepared by default; add `--split train` to include it.

## Citation

- J. Barker et al., "The fifth 'CHiME' Speech Separation and Recognition Challenge", Interspeech 2018.
- S. Watanabe et al., "CHiME-6 Challenge: Tackling Multispeaker Speech Recognition for Unsegmented Recordings", 2020.
