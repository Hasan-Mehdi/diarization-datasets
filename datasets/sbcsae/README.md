# Santa Barbara Corpus of Spoken American English (SBCSAE)

60 recordings (~23 min each, 23.3 h) of naturally occurring American English from across the US: face-to-face
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
| Ground-truth rating | **C+** - Careful human transcription of every participant with overlap marked, but IU bullets tile the timeline: pauses are labelled as speech (13.7% of reference speech is silent per our check), plus untranscribed edges and background media. |
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
| all | 60 | 23.31 | 21.36 | 0.919 | 0.071 | 0.0031 | 1/4/16 | 0.34/1.512/11.508 | 0.0054 | 1.62 | 13.54 |
| ALL | 60 | 23.31 | 21.36 | 0.919 | 0.071 | 0.0031 | 1/4/16 | 0.34/1.512/11.508 | 0.0054 | 1.62 | 13.54 |

Computed by `python -m diards stats sbcsae` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.sbcsae.md`](../../results/stats/stats.sbcsae.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 60 sessions, **0 errors**, 26 warnings (normalized files); 51 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: same_speaker_overlap = 918, duplicate_segment = 4
- checks that fired (sessions): `info:silence_over_30s` 6, `info:speaker_under_1s` 7, `warning:fewer_than_two_speakers` 1, `warning:possible_unannotated_speech` 4, `warning:segments_over_60s` 21
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 1.3% of reference speech; reference speech without energy = 20.2%. Most-flagged sessions: `sbcsae__SBC024` (0.11), `sbcsae__SBC055` (0.08), `sbcsae__SBC038` (0.07), `sbcsae__SBC045` (0.06), `sbcsae__SBC058` (0.04)
- full report: [`results/validation/validation.sbcsae.default.md`](../../results/validation/validation.sbcsae.default.md)
- **Silero VAD x2 audit** (view `default`, from the [VAD study](../../docs/silero_vad_study.md)): 22.13% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.57% of reference speech; Whisper finds intelligible speech in 10 of the 20 longest such regions.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (all) | 60 | 23.31 | primary | **27.38** | 2.56 | 22.52 | 2.30 | 48.68 | 24.23 | 43% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/sbcsae.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 60 | 21.2 | 13.67 | 7.53 | 1.57 | 0.82 | 0.74 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 18 of 40 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (47.2 of 88.2 s). Examples: `sbcsae__SBC021` 2.0-7.7 s: "The Great I Am!"; `sbcsae__SBC015` 1545.9-1550.8 s: "I thought it wasn't going to eat it. And I was really worried. You know, they di"; `sbcsae__SBC045` 904.7-907.9 s: "one person that I've known for a long time."

**Time-offset check (default):** 0 of 60 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.05 s.
<!-- /auto:diagnosis -->

**Reading the SBCSAE numbers: mostly reference convention.** DER is 27.4% at collar 0 and still 24.2% at 0.25 s,
almost all *missed speech* (22.5%). 13.7 points of it fall where the audio is silent: the intonation-unit bullets
tile the timeline, so pauses, including long ones marked `(...)` in the transcript, are labelled as speech. The
reference is not shifted (offset check: 0 of 60). Some genuinely unlabelled speech exists too: 18 of the 40 longest
audible false alarms contain words. These are untranscribed edges of recordings (276 s in total across 60
recordings, e.g. the last 28 s of SBC015; now excluded by the UEM) and background media in SBC045 ("When we return
for final..."). JER is high (49%) because many recordings have several minor speakers (up to 16) who say little. For
a diarization benchmark, re-time SBCSAE (forced alignment of the IU text) or use a generous collar.


## Quality rating

**C+.** Expert human transcription of every participant in truly natural talk, with overlap marked. But as a
diarization reference the IU tiling labels pauses as speech (DER stays at 24% even at collar 0.25 s), plus
untranscribed edges, variable audio and a no-derivatives licence.

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
