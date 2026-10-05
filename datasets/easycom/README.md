# EasyCom

Meta Reality Labs' "Easy Communications" dataset: 12 sessions (~5.3 h of the "high quality" part; 4-6 labelled speakers per session) of people
talking around a table (introductions, ordering food, puzzles, games, reading) while restaurant noise plays from
loudspeakers. One participant wears AR glasses with a 6-microphone array, and the others wear close-talk mics.
Voice activity and transcripts are human-annotated per participant, including the glasses wearer. It is the free
egocentric / hearing-aid-style diarization test.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-NC-4.0 ([link](https://creativecommons.org/licenses/by-nc/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free (GitHub, Git LFS or a 70 GB split release archive). |
| Source version used | facebookresearch/EasyComDataset main (Git LFS files, release v1.0.0) |
| Domain | egocentric conversation in noise (AR glasses) |
| Views (normalized) | `glasses`: AR-glasses microphone array, channel 1, 1-minute files concatenated per session |
| Reference used as primary RTTM | Human transcription with per-utterance voice-activity frames (20 fps). |
| Ground-truth rating | **B** - Human-annotated voice activity per participant (including the glasses wearer), overlap present, but utterance-level with 50 ms frame quantization; noise is played from loudspeakers. |
| Prepared splits (sessions) | all: 12 |
<!-- /auto:meta -->

## Source and access

- <https://github.com/facebookresearch/EasyComDataset> (CC BY-NC 4.0). Files are in Git LFS and can be fetched
  one by one (`media.githubusercontent.com/media/facebookresearch/EasyComDataset/main/...`), so the 70 GB release
  archive (33 x 2 GB parts, mostly video) is not needed. The recipe downloads only `Main/Speech_Transcriptions` and
  `Main/Glasses_Microphone_Array_Audio` (~22 GB of 48 kHz int32 6-channel WAV).

## Annotation methodology

Per the README, transcriptions are human-annotated and include voice-activity start and end **video frames**
(20 fps, so 50 ms resolution) for each utterance, the participant id, and a target-of-speech label. The recording
is split into 1-minute files named by their start time in the session. The recipe concatenates them per session
(annotation times shifted accordingly), so a diarizer has to keep identities over ~25-30 minutes.

## Known issues and errata

- Some minutes are missing because of redactions, so the concatenated audio has jumps at those points.
- Close-mic audio sample rate drifts slightly (~48,008.6 Hz); not used here.
- Session 8 videos carry an incorrect participant-ID banner (video only).
- Extra sessions with recording errors (`Extra/`) are excluded.
- Utterance-level VAD at 50 ms frames: decent, not word-level.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| all | 12 | 5.3 | 4.11 | 0.775 | 0.17 | 0.0205 | 4/4/6 | 0.4/1.55/8.0 | 0.0027 | 2.6 | 15.78 |
| ALL | 12 | 5.3 | 4.11 | 0.775 | 0.17 | 0.0205 | 4/4/6 | 0.4/1.55/8.0 | 0.0027 | 2.6 | 15.78 |

Computed by `python -m diards stats easycom` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.easycom.md`](../../results/stats/stats.easycom.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `glasses`: 12 sessions, **0 errors**, 0 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- checks that fired (sessions): `info:segments_under_50ms` 1
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 0.0% of reference speech; reference speech without energy = 53.7%. Most-flagged sessions: `easycom__Session_3` (0.00), `easycom__Session_1` (0.00), `easycom__Session_10` (0.00), `easycom__Session_11` (0.00), `easycom__Session_12` (0.00)
- full report: [`results/validation/validation.easycom.glasses.md`](../../results/validation/validation.easycom.glasses.md)
<!-- /auto:validation -->

The energy-VAD cross-check is **not informative for EasyCom**: restaurant babble is played from loudspeakers
throughout, so the noise floor of the glasses audio is high and a simple energy detector misses about half of the
labelled speech. That is a limitation of the check, not of the labels. Use the Nemotron diagnosis below instead.


## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| glasses (all) | 12 | 5.3 | primary | **30.38** | 4.10 | 19.61 | 6.67 | 33.75 | 21.68 | 25% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/easycom.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| glasses | glasses | 12 | 11.3 | 5.35 | 5.95 | 3.56 | 0.72 | 2.84 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (glasses):** 0 of 0 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (0 of 0 s).

**Time-offset check (glasses):** 0 of 12 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.05 s.
<!-- /auto:diagnosis -->

**Reading the EasyCom numbers: hard audio plus utterance-level labels.** DER is 30.4% at collar 0 and 21.7% at
0.25 s on the 12 sessions (concatenated to 23-30 min each), mostly missed speech (19.6%). The speaker-agnostic split
is about even: 5.4 points of missed speech are in quieter stretches inside labelled utterances (utterance-level labels
at 50 ms frames), and 6.0 points are audible speech the model drops under the restaurant babble. The model also
over-counts: it reports one or two more speakers than are labelled in 9 of 12 sessions (exact in 25%). Plausible
causes are the glasses wearer's very close, loud voice being split from their distant speech, or babble from the
loudspeakers being taken as a talker; this was not verified by listening. No session is time-shifted, and there are no
long audible false alarms. Treat it as a hard egocentric test where both the labels' granularity and the model
contribute.


## Quality rating

**B.** Human per-participant voice activity in a hard, realistic egocentric setting with overlap. Minus:
utterance-level labels, 50 ms quantization, noise played from loudspeakers, non-commercial license.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare easycom            # download (resumable) + normalize (idempotent)
python -m diards validate easycom --vad     # ground-truth checks
python -m diards stats easycom
python -m diards export easycom --format nemo      # or pyannote / lhotse
python -m diards evaluate easycom --view glasses  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("easycom", view="glasses"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

J. Donley et al., "EasyCom: An Augmented Reality Dataset to Support Algorithms for Easy Communication in Noisy Environments", arXiv:2107.04174, 2021.
