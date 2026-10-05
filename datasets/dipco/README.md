# DiPCo (Dinner Party Corpus)

Amazon's dinner-party corpus: 10 sessions of four volunteers eating and talking around a table in a lab dining
room (5.3 h), with headsets and five 7-microphone devices. Background music is played from a fixed point in each
session. It is small, permissively licensed (CDLA-Permissive), and a cleaner, shorter companion to CHiME-6.

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- Zenodo record [8122551](https://zenodo.org/records/8122551): `DipCo.tgz`, 13.4 GB, md5 `2297eb9334f3b90e02b54b708e501b24`
  (Zenodo delivered ~1 MB/s when tested; the recipe resumes interrupted downloads).
- Also part of CHiME-7 DASR (sessions renamed with an offset of 24 there). HF mirror: `huckiyang/DiPCo`.
  Lhotse recipe: `lhotse.recipes.prepare_dipco`.

## Annotation methodology

Each headset was transcribed manually with utterance boundaries. Per the README, transcribers split long stretches
of speech at "logical" points such as sentence starts, into segments of up to 10 s (15 s if necessary). So the
segments are **ASR-oriented**: pauses inside a segment are labelled as speech. Times are given per device and are
identical across devices (synchronised).

The recipe also writes a diagnostic `rttm_alt/closetalk_activity`: per-headset activity (level threshold calibrated
on each headset), restricted to within 0.5 s of that speaker's labelled utterances so crosstalk is not counted.
This shows how much of the labelled time is silent.

## Known issues and errata

- Loose, sentence-level segment boundaries (see above). Horiguchi et al. (ASRU 2025) list DiPCo among the
  "ASR-oriented" corpora.
- Each session begins with participants reading "speaker one", "speaker two"... (enrolment), which *is* labelled.
- Music playback in the second part of every session affects far-field audio only.
- Small: 5 eval sessions. The DiPCo dev sessions are in Nemotron 3 Diarization's training data, the eval sessions are not.

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

**B.** Complete close-talk transcription with overlap, permissive license. The 10-15 s segments overstate speech
time; prefer collar 0.25 s or the close-talk activity reference when you need tight boundaries.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

M. Van Segbroeck et al., "DiPCo - Dinner Party Corpus", Interspeech 2020.
