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
