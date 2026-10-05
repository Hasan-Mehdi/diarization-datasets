# LibriCSS (SYNTHETIC: re-recorded simulated meetings)

60 ten-minute "meetings" built by concatenating LibriSpeech utterances of 8 speakers with a controlled amount of
overlap (0%, with short or long silences, and 10-40%), played through loudspeakers in a real meeting room and
recorded with a 7-channel array. The reference is exact by construction, but the conversation is fake: read
speech, no natural turn-taking, backchannels or laughter. **Use it to study overlap and far-field effects, not as
evidence of real-conversation performance.**

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-4.0 (LibriSpeech-derived) ([link](https://creativecommons.org/licenses/by/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free download (Google Drive, 6.4 GB). |
| Source version used | for_release.zip (Google Drive id 1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l) |
| Domain | synthetic meetings (read speech replayed in a room) |
| Views (normalized) | `sdm`: Channel 0 of the 7-channel room recording; `clean-mix`: Original digital mixture before playback |
| Reference used as primary RTTM | Exact playback times of each LibriSpeech utterance (by construction). |
| Ground-truth rating | **S (synthetic)** - Timing is exact by construction but covers whole read-speech utterances (with their silences); no natural turn-taking, backchannels or laughter; useful for controlled overlap studies only. |
| Prepared splits (sessions) | dev: 6, eval: 54 |
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

**S (synthetic).** Exact by construction, but not natural conversation; rated separately from real data.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare libricss            # download (resumable) + normalize (idempotent)
python -m diards validate libricss --vad     # ground-truth checks
python -m diards stats libricss
python -m diards export libricss --format nemo      # or pyannote / lhotse
python -m diards evaluate libricss --view sdm  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("libricss", view="sdm"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

Z. Chen et al., "Continuous speech separation: dataset and analysis", ICASSP 2020.
