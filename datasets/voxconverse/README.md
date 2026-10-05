# VoxConverse v0.3

YouTube clips of political debates, panel shows, news and talk shows: 448 recordings (216 dev, 232 test),
~64 h, 1 to 21 speakers. Labels are diarization-oriented and human-verified, and the dataset has had two public
correction rounds. It is the standard free "in-the-wild broadcast" benchmark. Mostly English, with a few clips in
other languages.

<!-- auto:meta -->
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
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
<!-- /auto:nemotron -->

## Quality rating

**B+.** Human-verified, diarization-oriented, with overlap, and corrected twice in public. Points off for the
semi-automatic origin (short backchannels and off-screen interjections can be missed), single-speaker files, and
being part of many models' training data.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

J. S. Chung, J. Huh, A. Nagrani, T. Afouras, A. Zisserman, "Spot the conversation: speaker diarisation in the wild", Interspeech 2020.
