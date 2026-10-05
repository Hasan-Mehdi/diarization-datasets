# Santa Barbara Corpus of Spoken American English (SBCSAE)

60 recordings (~20 min each, ~20 h) of naturally occurring American English from across the US: face-to-face
conversation, phone calls, classroom lectures, sermons, story-telling, business meetings. Carefully transcribed by
linguists, with every intonation unit time-stamped and overlap marked. Free, but licensed **CC BY-ND 3.0**, so
derived RTTMs may not be redistributed. This repo ships only the scripts and statistics.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-ND-3.0-US ([link](https://creativecommons.org/licenses/by-nd/3.0/us/)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free download from OpenSLR (6.2 GB), no registration. |
| Source version used | OpenSLR SLR155 SBCSAE.tar.gz (CHAT transcripts + WAV) |
| Domain | everyday conversation (mixed situations) |
| Views (normalized) | `default`: Original recording (22.05 kHz stereo) downmixed to mono 16 kHz |
| Reference used as primary RTTM | Linguist transcription, intonation units time-stamped (ms bullets), overlap bracketed. |
| Ground-truth rating | **B-** - Careful human transcription of every participant with overlap marked and IU-level timing, but IU bullets tile the timeline (pauses inside units) and recordings vary widely in quality. |
| Prepared splits (sessions) | all: 60 |
<!-- /auto:meta -->

## Source and access

- OpenSLR [SLR155](https://www.openslr.org/155/): `SBCSAE.tar.gz` (6.2 GB: WAV, MP3, TRN and CHAT transcripts,
  docs). EU mirror `openslr.elda.org` was fastest.
- UCSB page: <https://www.linguistics.ucsb.edu/research/santa-barbara-corpus-spoken-american-english>; TalkBank
  CABank also hosts it (CHAT + media).
- LDC sells the same corpus (LDC2000S85 etc.); the free OpenSLR/UCSB version is complete.

## Annotation methodology

Du Bois et al. transcribed every speaker in discourse-transcription conventions. Intonation units (IUs) carry
millisecond time bullets, overlap is bracketed (⌈ ⌉ / ⌊ ⌋), and laughter, breaths, pauses and vocal noises are
coded. The reference here has one segment per IU that contains at least one lexical word. The environment tier
(`ENV`) and the non-human codes `X`/`MANY` are dropped.

## Known issues and errata

- IU bullets **tile the timeline**: each IU starts where the previous one ended, so leading pauses (`(..)`) are
  inside IUs. Boundaries are loose, especially at collar 0.
- Recording quality varies a lot (1980s-90s field recordings on portable equipment, some very noisy).
- Speaker sets vary from 2 to many; some recordings are lectures or sermons dominated by one speaker.
- CC BY-ND: do not publish modified annotations.

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

**B-.** Expert human transcription of every participant in truly natural talk, with overlap marked. Minus: IU-level
tiling (loose boundaries), variable audio, no-derivatives license.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare sbcsae            # download (resumable) + normalize (idempotent)
python -m diards validate sbcsae --vad     # ground-truth checks
python -m diards stats sbcsae
python -m diards export sbcsae --format nemo      # or pyannote / lhotse
python -m diards evaluate sbcsae --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("sbcsae", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

J. W. Du Bois, W. L. Chafe, C. Meyer, S. A. Thompson, R. Englebretson, N. Martey (2000-2005), Santa Barbara Corpus of Spoken American English, Parts 1-4. Philadelphia: Linguistic Data Consortium.
