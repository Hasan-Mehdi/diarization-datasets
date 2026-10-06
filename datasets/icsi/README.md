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

- **Corrupted end time:** in Bro025 one segment of speaker me013 runs from 2122.08 s to 4245.17 s, i.e. about 35
  minutes past the end of the 2122.6 s recording (the end time is roughly double the start). The validator flags it
  (`beyond_audio_end`) and normalization clips it.
- 986 pairs of overlapping segments of the same speaker in the original segments (merged during normalization).
- **Untranscribed speech outside the transcript** (found by the Silero VAD study): six meetings have talk before
  the first or after the last transcribed segment, e.g. Bed003 (transcript ends at 3,499 s, audio at 4,449 s,
  426 s of talk) and test meeting Bmr013 (67 s of pre-meeting talk before 92.5 s). The UEM is therefore the
  transcribed span +/- 1 s. (Nemotron output nothing in Bmr013's head, so its ICSI scores barely change; other
  diarizers' would.)

- **Training-data contamination:** ICSI (full corpus) is in Nemotron 3 Diarization's training data, so scores here
  are not held-out results.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| dev | 2 | 2.28 | 1.86 | 0.819 | 0.082 | 0.0053 | 6/6.5/7 | 0.25/1.749/6.43 | 0.0271 | 0.704 | 8.96 |
| test | 3 | 2.77 | 2.25 | 0.823 | 0.109 | 0.0125 | 7/7/7 | 0.23/1.57/6.65 | 0.031 | 0.973 | 13.99 |
| train | 70 | 66.64 | 54.69 | 0.831 | 0.108 | 0.0134 | 3/6/10 | 0.23/1.523/7.0 | 0.0319 | 1.09 | 14.08 |
| ALL | 75 | 71.69 | 58.8 | 0.83 | 0.107 | 0.0131 | 3/6/10 | 0.23/1.533/6.963 | 0.0317 | 1.069 | 13.91 |

Computed by `python -m diards stats icsi` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.icsi.md`](../../results/stats/stats.icsi.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `ihm-mix`: 75 sessions, **0 errors**, 15 warnings (normalized files); 74 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: same_speaker_overlap = 986, beyond_audio_end = 1, seconds_beyond_audio_end = 2122.62
- checks that fired (sessions): `info:segments_under_50ms` 10, `info:silence_over_30s` 4, `info:speaker_under_1s` 1, `warning:possible_unannotated_speech` 9, `warning:segments_over_60s` 6
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 2.2% of reference speech; reference speech without energy = 4.7%. Most-flagged sessions: `icsi__Bed008` (0.17), `icsi__Bed016` (0.13), `icsi__Bed010` (0.11), `icsi__Bed012` (0.09), `icsi__Bed009` (0.06)
- full report: [`results/validation/validation.icsi.ihm-mix.md`](../../results/validation/validation.icsi.ihm-mix.md)
- **Silero VAD x2 audit** (view `ihm-mix`, from the [VAD study](../../docs/silero_vad_study.md)): 8.28% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.91% of reference speech; Whisper finds intelligible speech in 20 of the 20 longest such regions.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| ihm-mix (test) | 3 | 2.77 | primary | **15.84** | 12.20 | 2.89 | 0.76 | 16.36 | 5.29 | 100% |
| ihm-mix (test) | 3 | 2.77 | words_gap0.2 | **39.42** | 38.37 | 0.64 | 0.41 | 33.14 | 22.92 | 100% |
| sdm (test) | 3 | 2.77 | primary | **15.84** | 11.06 | 3.77 | 1.00 | 16.10 | 5.36 | 100% |
| sdm (test) | 3 | 2.77 | words_gap0.2 | **38.20** | 36.33 | 1.14 | 0.74 | 33.67 | 22.37 | 100% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/icsi.*/results.md`.

> **Training-data overlap:** ICSI (full corpus) is in the model's training data: these scores are NOT held-out.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ihm-mix | ihm-mix | 3 | 1.16 | 0.59 | 0.57 | 7.36 | 2.4 | 4.96 |
| sdm | ihm-mix | 3 | 1.86 | 0.79 | 1.07 | 6.89 | 2.19 | 4.7 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (ihm-mix):** 0 of 5 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (0 of 7.7 s).

**Time-offset check (ihm-mix):** 0 of 3 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.0 s.

**Whisper audit of the longest audible false alarms (sdm):** 0 of 5 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (0 of 7.6 s).

**Time-offset check (sdm):** 0 of 3 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.0 s.
<!-- /auto:diagnosis -->

**Reading the ICSI numbers.** Against the transcriber segments, Nemotron's errors are mostly *false alarm* (~12% at
collar 0, ~4% at 0.25 s): it marks speech just outside the segments. The false alarms are short. Only 5 audible
false-alarm regions are longer than 1 s, and Whisper finds no intelligible words in any of them, so they are segment
edges and vocal sounds (laughter, breaths), not missing speakers. The word-timing reference (`words_gap0.2`) is
**not usable**: with 9-13% of words untimed it covers 21% less speech and turns into 38% false alarm. ICSI is in
the model's training data, so treat these scores as a sanity check, not a benchmark.


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
