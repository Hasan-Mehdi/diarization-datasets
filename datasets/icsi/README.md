# ICSI Meeting Corpus

75 real (not role-played) research-group meetings recorded at ICSI Berkeley in 2000-2002: ~72 h, 3-10
participants, many of them non-native speakers. Everyone wore a headset and was transcribed. It is older audio,
but natural, long (~1 h) meetings with many speakers; that is rare among free data.

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- <https://groups.inf.ed.ac.uk/ami/icsi/> (CC BY 4.0). Annotations: `ICSI_core_NXT.zip` (v1.0, 2016). Audio:
  `ICSIsignals/NXT/<meeting>.interaction.wav` (headset mix) and `ICSIsignals/SPH/<meeting>/chan*.sph` (per channel).
- HF mirror: [`argmaxinc/icsi-meetings`](https://huggingface.co/datasets/argmaxinc/icsi-meetings) (used in SDBench).
  Lhotse recipe: `lhotse.recipes.prepare_icsi` (source of the train/dev/test partition used here).

## Annotation methodology

The original MRT transcripts were made per headset channel with hand-placed segment boundaries. The 2016 NXT
release adds word timings from forced alignment (not every word received a timing). Primary reference: the
transcriber segments that contain at least one word. Segments made only of non-speech events ("mike noise",
breaths, laughter without words) are dropped. Alternative `rttm_alt/words_gap0.2`: word timings, same-speaker
words merged across pauses < 0.2 s.

## Known issues and errata

- Transcriber segments are transcription-oriented. Segment and dialogue-act timing provenance is mixed
  (`timing-provenance="segment"` vs `"dialogueact"` in the NXT files).
- Some words have no timing in the NXT release (the share per meeting is stored as `extra.untimed_word_frac`), so
  the word-based reference under-covers speech.
- Many segments contain only noise or vocal-sound events; using all segments would label mic noise as speech.
- The Kaldi/Lhotse test split is only 3 meetings.
- **Training-data contamination:** ICSI (full corpus) is in Nemotron 3 Diarization's training data, so scores here
  are not held-out results.

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

**B.** Natural meetings, complete headset transcription with overlap and backchannels, hand-placed boundaries.
Points off for transcription-oriented (padded) segments, incomplete word timings, and old audio.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

A. Janin et al., "The ICSI Meeting Corpus", ICASSP 2003.
