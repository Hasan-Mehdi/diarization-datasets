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
| Ground-truth rating | **B** - Human-labelled identities including off-screen speakers on hard movie audio; built on top of visual active-speaker tracks; scoring region cropped to the labelled extent. |
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

- The `.lab` speech-activity files are exactly the union of the RTTM segments (checked on all 351 clips: 0 s of
  lab-only speech), so they add no information. Note that the RTTM lines are not sorted by time.
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
View `default`: 96 sessions, **0 errors**, 94 warnings (normalized files); 4 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: same_speaker_overlap = 2, beyond_audio_end = 1, seconds_beyond_audio_end = 0.37, negative_start = 1
- checks that fired (sessions): `info:silence_over_30s` 40, `info:speaker_under_1s` 43, `warning:possible_unannotated_speech` 94
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 55.7% of reference speech; reference speech without energy = 2.7%. Most-flagged sessions: `ava_avd_en__fD6VkIRlIRI_c_01` (3.63), `ava_avd_en__9mLYmkonWZQ_c_01` (3.60), `ava_avd_en__fD6VkIRlIRI_c_02` (3.24), `ava_avd_en__x-6CtPWVi6E_c_03` (2.87), `ava_avd_en__N0Dt9i9IUNg_c_02` (2.52)
- full report: [`results/validation/validation.ava_avd_en.default.md`](../../results/validation/validation.ava_avd_en.default.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (test, val) | 29 | 2.42 | primary | **49.79** | 11.78 | 23.30 | 14.70 | 67.44 | 33.98 | 21% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/ava_avd_en.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 29 | 19.61 | 5.49 | 14.12 | 11.71 | 3.63 | 8.08 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 2 of 5 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (4.3 of 10.5 s). Examples: `ava_avd_en__fD6VkIRlIRI_c_03` 248.6-251.2 s: "Come on! Let's go!"; `ava_avd_en__o4xQ-BEa3Ss_c_02` 242.6-244.3 s: "Hey, Marie, bring it on."

**Time-offset check (default):** 0 of 29 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.05 s.
<!-- /auto:diagnosis -->

**Reading the AVA-AVD numbers: mostly model error on hard audio.** DER is 49.8% at collar 0 (34.0% at 0.25 s) on the
29 English test/val clips, in line with public results for this model on AVA-AVD (~45%). The diagnosis points at
the model rather than the labels: 14 of the 20 points of missed speech are *audible* (dialogue under music and
effects, whispering, distant speakers), most false alarms fall in quiet stretches, only 2 of the 5 long audible
false alarms contain words, and no clip is time-shifted. Speaker confusion is high (14.7%) and the model finds the
right number of speakers in only 21% of clips (up to 24 labelled speakers per clip, while the model outputs at most
8). Use it as a stress test, not as a typical-conditions benchmark.


## Quality rating

**B.** Human identity labels on hard, in-the-wild movie audio with many speakers; the checks found no label problems. Minus: unlabelled speech regions
(see the diagnosis: most errors are model errors on hard movie audio), LID-derived English subset, video-centric
annotation origin.

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
