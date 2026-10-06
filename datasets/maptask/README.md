# HCRC Map Task Corpus

128 unscripted task-oriented dialogues (~15 h) between pairs of Glasgow university students. One "giver" guides a
"follower" along a route on a map, with or without eye contact. Each speaker was recorded on a separate close-talk
channel in a studio, and every word is time-stamped, with silences and noises explicitly marked. It is the
cleanest free two-speaker reference set: clean channels, word timing, natural (if task-bound) overlap and
backchannels.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-NC-SA-2.5 (audio + NXT zip); download page states CC BY 4.0 for annotations v2.1 ([link](https://groups.inf.ed.ac.uk/maptask/maptasknxt.html)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free download, no registration. |
| Source version used | NXT annotations v2.1 (2011-02-10); signals/dialogues *.mix.wav |
| Domain | two-person task dialogue (close-talk) |
| Views (normalized) | `default`: Official stereo mix of the two close-talk channels, downmixed to mono 16 kHz |
| Reference used as primary RTTM | Word-level timed units per speaker (silence and noise also time-marked). |
| Ground-truth rating | **A** - Each speaker on a separate close-talk channel with word-level timings, silences explicitly marked, overlap naturally represented; verified: 0.6% of reference speech in silence, no time shifts, Nemotron DER 1.9% at collar 0.25 s. Task dialogue, studio audio. |
| Prepared splits (sessions) | all: 128 |
<!-- /auto:meta -->

## Source and access

- <https://groups.inf.ed.ac.uk/maptask/maptasknxt.html>: NXT annotation zip v2.1 (12 MB) and
  `signals/dialogues/<id>.mix.wav` (stereo mix of the two speaker channels, 20 kHz). No registration.
- License: the download page states CC BY 4.0 for the v2.1 annotations; the `00LICENSE.html` inside the zip and
  in the audio folder is CC BY-NC-SA 2.5. Treat the stricter terms (non-commercial, share-alike) as binding.
- LDC also distributes it (LDC93S12).

## Annotation methodology

Orthographic transcription per speaker channel with word-level "timed units" (`<tu start end>`), plus explicitly
timed silences (`<sil>`) and noises (`<noi>`, e.g. breaths). The reference merges a speaker's words across pauses
< 0.2 s (DIHARD convention). Speaker ids are the corpus' global participant ids, so the same person keeps the
same id across their four dialogues.

## Known issues and errata

- Task dialogue: speakers talk about landmarks on a map. It is natural in timing and overlap but narrow in content
  and register (Scottish English).
- The corpus README notes NXT data-model irregularities for tokens/POS layers; they do not affect the timed units.
- 20 kHz studio audio, very clean; easier than real-world phone or meeting audio.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| all | 128 | 14.31 | 9.27 | 0.648 | 0.051 | 0.0 | 2/2/2 | 0.224/0.837/2.935 | 0.0312 | 1.147 | 21.81 |
| ALL | 128 | 14.31 | 9.27 | 0.648 | 0.051 | 0.0 | 2/2/2 | 0.224/0.837/2.935 | 0.0312 | 1.147 | 21.81 |

Computed by `python -m diards stats maptask` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.maptask.md`](../../results/stats/stats.maptask.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 128 sessions, **0 errors**, 12 warnings (normalized files); 1 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: beyond_audio_end = 453, seconds_beyond_audio_end = 442.01
- checks that fired (sessions): `info:segments_under_50ms` 5, `info:silence_over_30s` 2, `warning:possible_unannotated_speech` 11, `warning:words_outside_reference` 1
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 1.8% of reference speech; reference speech without energy = 0.3%. Most-flagged sessions: `maptask__q3nc3` (0.14), `maptask__q3ec5` (0.13), `maptask__q3nc2` (0.13), `maptask__q3nc7` (0.07), `maptask__q3ec3` (0.07)
- full report: [`results/validation/validation.maptask.default.md`](../../results/validation/validation.maptask.default.md)
- **Silero VAD x2 audit** (view `default`, from the [VAD study](../../docs/silero_vad_study.md)): 1.83% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.62% of reference speech; Whisper finds intelligible speech in 3 of the 20 longest such regions.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (all) | 128 | 14.31 | primary | **7.94** | 4.55 | 3.32 | 0.07 | 9.01 | 1.88 | 95% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/maptask.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 128 | 2.78 | 0.56 | 2.22 | 3.82 | 1.51 | 2.31 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 4 of 23 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (5.3 of 30.4 s). Examples: `maptask__q2ec6` 249.3-250.9 s: "Oh, my God."; `maptask__q3ec2` 98.5-99.8 s: "The thing's not even pointing at me."; `maptask__q4nc4` 180.4-181.6 s: "to do it"

**Time-offset check (default):** 0 of 128 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.0 s.
<!-- /auto:diagnosis -->

**Reading the Map Task numbers: the cleanest result in the benchmark.** DER is 7.9% at collar 0 and 1.9% at
0.25 s, with almost no speaker confusion (0.1%) and correct speaker counts on 95% of dialogues (the misses are files
where the model invents a third speaker). The diagnosis shows a tight, complete reference: only 0.56% of reference
speech lies in silence, no dialogue is time-shifted, and most of the 4.5% false alarm is the model's boundaries
extending into silence, which disappears at collar 0.25 s. Only 4 of the 23 long audible false alarms contain
words. Word-level timing on separate close-talk channels gives the best two-speaker ground truth available for
free.


## Quality rating

**A.** Separate close-talk channels plus word-level timing gives diarization-grade references with natural overlap
and backchannels, and every check agrees (no time shifts, almost no labelled silence, 1.9% DER at collar 0.25 s).
Caveats that are not about the labels: narrow task domain, studio audio, licence ambiguity (use non-commercially).

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare maptask            # download (resumable) + normalize (idempotent)
python -m diards validate maptask --vad     # ground-truth checks
python -m diards stats maptask
python -m diards export maptask --format nemo      # or pyannote / lhotse
python -m diards evaluate maptask --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("maptask", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

A. H. Anderson et al., "The HCRC Map Task Corpus", Language and Speech 34(4), 1991.
