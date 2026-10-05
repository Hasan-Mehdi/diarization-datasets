# EasyCom

Meta Reality Labs' "Easy Communications" dataset: 12 sessions (~5.3 h of the "high quality" part) of 3-5 people
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
_Statistics not computed yet._
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
_Validation not run yet._
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
