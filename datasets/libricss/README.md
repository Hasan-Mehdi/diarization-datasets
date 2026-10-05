# LibriCSS (SYNTHETIC: re-recorded simulated meetings)

60 ten-minute "meetings" built by concatenating LibriSpeech utterances of 8 speakers with a controlled amount of
overlap (0%, with short or long silences, and 10-40%), played through loudspeakers in a real meeting room and
recorded with a 7-channel array. The reference is exact by construction, but the conversation is fake: read
speech, no natural turn-taking, backchannels or laughter. **Use it to study overlap and far-field effects, not as
evidence of real-conversation performance.**

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- <https://github.com/chenzhuo1011/libri_css>, data `for_release.zip` (6.4 GB) on Google Drive
  (id `1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l`). LibriSpeech-derived, CC BY 4.0.
- Lhotse recipe: `lhotse.recipes.prepare_libricss`.

## Annotation methodology

`transcription/meeting_info.txt` lists, for every played utterance, its start/end time in the session, the
LibriSpeech speaker id and the text. These are the exact playback times. They include the leading and trailing
silences of each LibriSpeech utterance, so segments are slightly longer than the actual speech.

## Known issues and errata

- Read speech replayed by loudspeakers: no real interaction, loudspeaker directivity instead of human heads.
- Segment edges include LibriSpeech's own silence padding.
- Conditions: `0L` / `0S` (no overlap; long/short silences), `OV10`-`OV40` (target overlap ratio). Session 0 of each
  condition is used as dev, sessions 1-9 as eval.

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

**S (synthetic).** Exact by construction, but not natural conversation; rated separately from real data.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

Z. Chen et al., "Continuous speech separation: dataset and analysis", ICASSP 2020.
