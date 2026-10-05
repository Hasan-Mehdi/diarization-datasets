# VoxConverse v0.3

YouTube clips of political debates, panel shows, news and talk shows: 448 recordings (216 dev, 232 test),
~64 h, 1 to 21 speakers. Labels are diarization-oriented and human-verified, and the dataset has had two public
correction rounds. It is the standard free "in-the-wild broadcast" benchmark. Mostly English, with a few clips in
other languages.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-4.0 ([link](https://creativecommons.org/licenses/by/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free download, no registration (audio CC BY 4.0 for research; copyright remains with video owners). |
| Source version used | joonson/voxconverse master (v0.3 RTTMs) |
| Domain | in-the-wild media (broadcast / YouTube) |
| Views (normalized) | `default`: Original single-channel YouTube audio, 16 kHz |
| Reference used as primary RTTM | Manual annotation (semi-automatic pipeline + human verification/correction), v0.3 corrections. |
| Ground-truth rating | **B+** - Human-verified diarization-oriented labels (pauses > 0.25 s split), overlap annotated, two public correction rounds (v0.2, v0.3). Created with an audio-visual pipeline then manually checked, so some short backchannels/off-screen speech can be missing. |
| Prepared splits (sessions) | dev: 216, test: 232 |
<!-- /auto:meta -->

## Source and access

- Annotations: <https://github.com/joonson/voxconverse> (`master` = v0.3; `ver0.2` branch keeps the old labels).
- Audio: official zips at <https://www.robots.ox.ac.uk/~vgg/data/voxconverse/> (dev 2.0 GB, test 4.3 GB). The
  server delivered ~0.25 MB/s when tested, so the recipe takes the identical 16 kHz WAVs from the CC-BY Hugging Face
  mirror [`diarizers-community/voxconverse`](https://huggingface.co/datasets/diarizers-community/voxconverse)
  (file names preserved). `--opt audio_source=official` switches back to the official zips.
- Lhotse recipe: `lhotse.recipes.prepare_voxconverse`.

## Annotation methodology

Chung et al. (Interspeech 2020) built candidate segments with an audio-visual pipeline (active speaker detection,
face tracks, speaker verification) and then had annotators verify and correct them, including off-screen speech.
Diarization-oriented conventions: pauses longer than ~0.25 s split segments, and overlap is labelled. v0.2 and v0.3
fixed errors that were found in the test RTTMs.

## Known issues and errata

- **v0.3 is the version to use.** The maintainers report errors in some v0.2 test RTTMs, fixed in `master`.
- Some recordings have **only one speaker** (37 of 448 in our count), so not every file is a multi-speaker test.
- Broadcast material contains music, applause and jingles. The energy-VAD cross-check flags these as
  "unlabelled energy", which is mostly correct non-speech, not missing labels (see validation).
- A few clips are not in English. VoxConverse has no language labels.
- **Training-data contamination:** VoxConverse v0.3 dev *and* test are in the training data of
  Nemotron 3 Diarization (and of several other recent diarizers). Scores on it are no longer held-out.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| dev | 216 | 20.3 | 18.91 | 0.932 | 0.037 | 0.0016 | 1/4/20 | 0.44/3.84/33.732 | 0.0011 | 2.04 | 3.81 |
| test | 232 | 43.54 | 38.99 | 0.895 | 0.031 | 0.0011 | 1/6/21 | 0.45/2.84/30.32 | 0.0001 | 1.96 | 4.23 |
| ALL | 448 | 63.83 | 57.89 | 0.907 | 0.033 | 0.0012 | 1/5/21 | 0.45/3.16/31.12 | 0.0004 | 1.98 | 4.09 |

Computed by `python -m diards stats voxconverse` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.voxconverse.md`](../../results/stats/stats.voxconverse.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 448 sessions, **0 errors**, 277 warnings (normalized files); 24 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: beyond_audio_end = 22, seconds_beyond_audio_end = 1.33, same_speaker_overlap = 2
- checks that fired (sessions): `info:segments_under_50ms` 3, `info:silence_over_30s` 9, `info:speaker_under_1s` 27, `warning:fewer_than_two_speakers` 37, `warning:possible_unannotated_speech` 98, `warning:segments_over_60s` 142
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 3.5% of reference speech; reference speech without energy = 0.9%. Most-flagged sessions: `voxconverse__pqmho` (5.41), `voxconverse__tucrg` (3.17), `voxconverse__zztbo` (0.86), `voxconverse__mxdpo` (0.68), `voxconverse__xtdcl` (0.67)
- full report: [`results/validation/validation.voxconverse.default.md`](../../results/validation/validation.voxconverse.default.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (test) | 232 | 43.54 | primary | **8.39** | 1.87 | 3.24 | 3.27 | 29.03 | 5.74 | 53% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/voxconverse.*/results.md`.

> **Training-data overlap:** VoxConverse v0.3 dev AND test are in the model's training data: these scores are NOT held-out.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 232 | 2.47 | 0.62 | 1.85 | 1.26 | 0.53 | 0.73 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 12 of 37 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (20.7 of 60.6 s). Examples: `voxconverse__kzmyi` 0.3-3.8 s: "That is very disturbing for people who are standing up here."; `voxconverse__gcvrb` 9.3-12.1 s: "I can be blamed, just you"; `voxconverse__gcvrb` 13.5-15.8 s: "So I do it like you"
<!-- /auto:diagnosis -->

**Reading the VoxConverse numbers.** 8.4% DER at collar 0 on the test set is close to published numbers for this
model, but the model was trained on these files. Of the 37 longest audible "false alarms", Whisper finds
intelligible speech in 12 (20.7 of 60.6 s). These are mostly short unlabelled stretches at the start of clips, e.g.
`xggbk` 5.6-7.0 s *"Question number one, Mr Speaker."* and `kzmyi` 0.3-3.8 s. The rest is laughter, applause and
music, where Whisper only hallucinates ("on and on and on"). So VoxConverse has a small amount of unlabelled speech,
consistent with its semi-automatic origin. The energy-VAD outliers (`pqmho`, `tucrg`) are music and background
sound, not missing speakers. Speaker counting is the weak point (53% exact on test, with up to 21 speakers).


## Quality rating

**B+.** Human-verified, diarization-oriented, with overlap, and corrected twice in public. Points off for the
semi-automatic origin (short backchannels and off-screen interjections can be missed), single-speaker files, and
being part of many models' training data.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare voxconverse            # download (resumable) + normalize (idempotent)
python -m diards validate voxconverse --vad     # ground-truth checks
python -m diards stats voxconverse
python -m diards export voxconverse --format nemo      # or pyannote / lhotse
python -m diards evaluate voxconverse --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("voxconverse", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

J. S. Chung, J. Huh, A. Nagrani, T. Afouras, A. Zisserman, "Spot the conversation: speaker diarisation in the wild", Interspeech 2020.
