# AVA-AVD (English subset)

AVA-AVD adds "who spoke when" labels to 351 five-minute clips (minutes 15-30 of 117 movies) of the AVA dataset:
dialogue in diverse scenes with off-screen speakers, music and sound effects. The movies are in many languages,
so this repo keeps the clips that Whisper large-v3 identifies as English (**96 of 351**). Per-clip language
probabilities: [`metadata/ava_avd_lid.json`](../../metadata/ava_avd_lid.json).

<!-- auto:meta -->
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
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
<!-- /auto:diagnosis -->

## Quality rating

**B-.** Human identity labels on hard, in-the-wild movie audio with many speakers. Minus: unlabelled speech regions
(the lab/RTTM mismatch), LID-derived English subset, video-centric annotation origin.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

E. Z. Xu et al., "AVA-AVD: Audio-Visual Speaker Diarization in the Wild", ACM Multimedia 2022.
