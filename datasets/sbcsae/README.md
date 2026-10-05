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
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| all | 60 | 23.31 | 21.36 | 0.916 | 0.071 | 0.0031 | 1/4/16 | 0.34/1.512/11.508 | 0.0054 | 1.62 | 13.49 |
| ALL | 60 | 23.31 | 21.36 | 0.916 | 0.071 | 0.0031 | 1/4/16 | 0.34/1.512/11.508 | 0.0054 | 1.62 | 13.49 |

Computed by `python -m diards stats sbcsae` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.sbcsae.md`](../../results/stats/stats.sbcsae.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 60 sessions, **0 errors**, 26 warnings (normalized files); 51 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: same_speaker_overlap = 918, duplicate_segment = 4
- checks that fired (sessions): `info:silence_over_30s` 6, `info:speaker_under_1s` 7, `warning:fewer_than_two_speakers` 1, `warning:possible_unannotated_speech` 4, `warning:segments_over_60s` 21
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 1.4% of reference speech; reference speech without energy = 20.2%. Most-flagged sessions: `sbcsae__SBC024` (0.11), `sbcsae__SBC055` (0.09), `sbcsae__SBC038` (0.07), `sbcsae__SBC045` (0.06), `sbcsae__SBC058` (0.04)
- full report: [`results/validation/validation.sbcsae.default.md`](../../results/validation/validation.sbcsae.default.md)
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
