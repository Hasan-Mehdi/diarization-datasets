# ICSI Meeting Corpus

75 real (not role-played) research-group meetings recorded at ICSI Berkeley in 2000-2002: ~72 h, 3-10
participants, many of them non-native speakers. Everyone wore a headset and was transcribed. It is older audio,
but natural, long (~1 h) meetings with many speakers; that is rare among free data.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-4.0 ([link](https://creativecommons.org/licenses/by/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free download, no registration. |
| Source version used | ICSI core NXT annotations v1.0 (2016-07-22) |
| Domain | meetings |
| Views (normalized) | `ihm-mix`: Headset mix (<meeting>.interaction.wav); `sdm`: Table-top microphone channel 6 (chan6.sph) |
| Reference used as primary RTTM | Manual transcriber segments (MRT) per participant; forced-aligned word times as alternative. |
| Ground-truth rating | **B** - All participants on headsets and fully transcribed (overlap and backchannels included); segment boundaries are hand-placed but transcription-oriented (padding, merged pauses). |
| Prepared splits (sessions) | dev: 2, test: 3, train: 70 |
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
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| dev | 2 | 2.28 | 1.86 | 0.818 | 0.082 | 0.0053 | 6/6.5/7 | 0.25/1.749/6.43 | 0.0271 | 0.704 | 8.95 |
| test | 3 | 2.77 | 2.25 | 0.815 | 0.109 | 0.0125 | 7/7/7 | 0.23/1.57/6.65 | 0.031 | 0.973 | 13.85 |
| train | 70 | 66.64 | 54.69 | 0.821 | 0.108 | 0.0134 | 3/6/10 | 0.23/1.523/7.0 | 0.0319 | 1.09 | 13.91 |
| ALL | 75 | 71.69 | 58.8 | 0.82 | 0.107 | 0.0131 | 3/6/10 | 0.23/1.533/6.963 | 0.0317 | 1.069 | 13.75 |

Computed by `python -m diards stats icsi` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.icsi.md`](../../results/stats/stats.icsi.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `ihm-mix`: 75 sessions, **0 errors**, 16 warnings (normalized files); 74 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: same_speaker_overlap = 986, beyond_audio_end = 1, seconds_beyond_audio_end = 2122.62
- checks that fired (sessions): `info:segments_under_50ms` 10, `info:silence_over_30s` 19, `info:speaker_under_1s` 1, `warning:possible_unannotated_speech` 10, `warning:segments_over_60s` 6
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 2.4% of reference speech; reference speech without energy = 4.7%. Most-flagged sessions: `icsi__Bed008` (0.18), `icsi__Bed016` (0.14), `icsi__Bed012` (0.11), `icsi__Bed010` (0.11), `icsi__Bed003` (0.09)
- full report: [`results/validation/validation.icsi.ihm-mix.md`](../../results/validation/validation.icsi.ihm-mix.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| ihm-mix (test) | 3 | 2.77 | primary | **15.86** | 12.22 | 2.89 | 0.76 | 16.36 | 5.31 | 100% |
| ihm-mix (test) | 3 | 2.77 | words | **44.46** | 43.40 | 0.62 | 0.44 | 35.46 | 28.20 | 100% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/icsi.*/results.md`.

> **Training-data overlap:** ICSI (full corpus) is in the model's training data: these scores are NOT held-out.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
_Not run yet._
<!-- /auto:diagnosis -->

## Quality rating

**B.** Natural meetings, complete headset transcription with overlap and backchannels, hand-placed boundaries.
Points off for transcription-oriented (padded) segments, incomplete word timings, and old audio.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare icsi            # download (resumable) + normalize (idempotent)
python -m diards validate icsi --vad     # ground-truth checks
python -m diards stats icsi
python -m diards export icsi --format nemo      # or pyannote / lhotse
python -m diards evaluate icsi --view ihm-mix  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("icsi", view="ihm-mix"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

A. Janin et al., "The ICSI Meeting Corpus", ICASSP 2003.
