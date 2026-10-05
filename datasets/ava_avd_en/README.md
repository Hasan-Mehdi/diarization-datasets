# AVA-AVD (English subset)

AVA-AVD adds "who spoke when" labels to 351 five-minute clips (minutes 15-30 of 117 movies) of the AVA dataset:
dialogue in diverse scenes with off-screen speakers, music and sound effects. The movies are in many languages,
so this repo keeps the clips that Whisper large-v3 identifies as English (**96 of 351**). Per-clip language
probabilities: [`metadata/ava_avd_lid.json`](../../metadata/ava_avd_lid.json).

<!-- auto:meta -->
| | |
|---|---|
| License | Research use (AVA annotations CC BY 4.0; movies copyrighted, distributed by CVDF for research) ([link](https://research.google.com/ava/download.html)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free: annotations on GitHub/Google Drive, videos from the CVDF S3 mirror. |
| Source version used | zcxu-eric/AVA-AVD (git HEAD) + annotations.tar.gz (Google Drive) + CVDF AVA trainval videos |
| Domain | movies (in-the-wild media) |
| Views (normalized) | `default`: Movie soundtrack, mono 16 kHz |
| Reference used as primary RTTM | Human audio-visual diarization labels on top of AVA-ActiveSpeaker. |
| Ground-truth rating | **B-** - Human-labelled identities including off-screen speakers, but labels were built on top of visual active-speaker tracks; some speech marked in the VAD labels has no speaker label. |
| Prepared splits (sessions) | test: 9, train: 67, val: 20 |
<!-- /auto:meta -->

## Source and access

- Repo and splits: <https://github.com/zcxu-eric/AVA-AVD> (`dataset/split/{train,val,test}.list`, `video.list`).
- Annotations: `annotations.tar.gz` on Google Drive (id `18kjJJbebBg7e8umI6HoGE4_tI3OWufzA`; despite the name it
  is an uncompressed tar): `rttms/`, `labs/` (speech activity), `tracks/`.
- Movies: CVDF mirror of AVA, `https://s3.amazonaws.com/ava-dataset/trainval/<video>`. The recipe uses ffmpeg HTTP
  seeking to fetch only minutes 15-30 of each movie, so it never downloads the full ~50 GB of video.
- HF mirror: [`argmaxinc/ava-avd`](https://huggingface.co/datasets/argmaxinc/ava-avd).

## Annotation methodology

Xu et al. (ACM MM 2022) annotated speaker identities for every speech segment on top of AVA-ActiveSpeaker, including
off-screen speakers. RTTM times are absolute movie times; the official preprocessing crops each clip from its first
to its last labelled segment, and the UEM here follows that convention.

## English subset (our derivation)

Whisper large-v3 LID on up to three 30-s windows of reference speech per clip, P(en) >= 0.7. For example, the
movie `1j20qq1JyX4` is code-switched Yoruba/English and is excluded.

## Known issues and errata

- The `.lab` speech-activity files mark speech that has **no speaker label** in the RTTM (e.g. 900.06-902.88 s in
  `0f39OWEqJ24_c_01`). The amount per clip inside the UEM is stored as `extra.lab_speech_without_speaker_s`.
- Movie audio: music, effects, dubbing, whispering; the reference covers dialogue only.
- Scoring region = first to last labelled segment (official), not the whole 5-minute window.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| test | 9 | 0.75 | 0.38 | 0.511 | 0.054 | 0.0027 | 5/7/10 | 0.311/1.0/3.328 | 0.0053 | 1.04 | 11.08 |
| train | 67 | 5.58 | 2.29 | 0.433 | 0.032 | 0.0003 | 2/7/24 | 0.314/0.97/3.16 | 0.0041 | 1.252 | 10.14 |
| val | 20 | 1.67 | 0.56 | 0.357 | 0.038 | 0.012 | 3/6/15 | 0.315/0.944/2.876 | 0.0034 | 1.548 | 9.06 |
| ALL | 96 | 8.0 | 3.24 | 0.425 | 0.036 | 0.0026 | 2/7/24 | 0.314/0.97/3.129 | 0.0041 | 1.279 | 10.01 |

Computed by `python -m diards stats ava_avd_en` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.ava_avd_en.md`](../../results/stats/stats.ava_avd_en.md).
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

**B-.** Human identity labels on hard, in-the-wild movie audio with many speakers. Minus: unlabelled speech regions
(the lab/RTTM mismatch), LID-derived English subset, video-centric annotation origin.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare ava_avd_en            # download (resumable) + normalize (idempotent)
python -m diards validate ava_avd_en --vad     # ground-truth checks
python -m diards stats ava_avd_en
python -m diards export ava_avd_en --format nemo      # or pyannote / lhotse
python -m diards evaluate ava_avd_en --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("ava_avd_en", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

E. Z. Xu et al., "AVA-AVD: Audio-Visual Speaker Diarization in the Wild", ACM Multimedia 2022.
