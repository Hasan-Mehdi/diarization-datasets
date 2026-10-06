# U.S. Supreme Court oral arguments (Oyez), court-domain sample

Oral arguments before the U.S. Supreme Court: about an hour each, nine justices plus two or three advocates,
formal turn-taking with frequent interruptions. Oyez provides speaker-attributed transcripts synchronised to the
public-record audio for ~8,500 arguments (1955-2025). This repo prepares a **sample** (12 cases of the October 2022
term by default) to measure how usable Oyez timing is as a court-domain diarization reference.

<!-- auto:meta -->
| | |
|---|---|
| License | Audio: public record; Oyez transcripts/sync: CC-BY-NC-4.0 ([link](https://www.oyez.org/license)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free public API, no registration. |
| Source version used | api.oyez.org (fetched at prepare time) |
| Domain | court (oral arguments) |
| Views (normalized) | `default`: Oyez MP3 (court recording) to mono 16 kHz |
| Reference used as primary RTTM | Oyez speaker-attributed transcript turns synchronised to the audio (no overlap). |
| Ground-truth rating | **C** - Human-transcribed and speaker-attributed with stable global ids, but turn-level sync that tiles the timeline and never marks the frequent interruptions/overlaps. |
| Prepared splits (sessions) | term2022: 12 |
<!-- /auto:meta -->

## Source and access

- Oyez API: `https://api.oyez.org/cases?filter=term:<year>`, then `oral_argument_audio` -> `media_file` (MP3) and
  `transcript.sections[].turns[]` (start, stop, speaker, text blocks). No registration. Oyez content is
  CC BY-NC 4.0; the recordings are public records of the Court.
- Bulk packs: <https://github.com/vcon-dev/vcon-supreme-court-arguments> (all arguments as vCon JSON, MIT container;
  196 recordings without Oyez transcripts were transcribed with Whisper there, so avoid those for ground truth).

## Annotation methodology

Oyez volunteers and staff transcribed the arguments, with speaker attribution from the Court's transcripts, and
synchronised them to the audio at turn and text-block level. The sync method is not documented in detail. Turns
are contiguous: each turn ends where the next begins, so pauses belong to the turn, and simultaneous speech
(interruptions) is never represented as overlap.

## Known issues and errata

- No overlap at all in the reference, although justices interrupt constantly. Interruptions become boundary errors.
- Turn tiling means silence is labelled as speech.
- Older recordings (pre-2000s) have tape noise and different sync quality. The sample here is recent (OT2022).
- Advocates appear in few cases. Justices recur across all cases (useful for speaker-ID experiments).

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| term2022 | 12 | 20.5 | 20.49 | 1.0 | 0.0 | 0.0 | 10/11/13 | 0.287/6.135/58.521 | 0.0324 | 8.91 | 3.89 |
| ALL | 12 | 20.5 | 20.49 | 1.0 | 0.0 | 0.0 | 10/11/13 | 0.287/6.135/58.521 | 0.0324 | 8.91 | 3.89 |

Computed by `python -m diards stats scotus` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.scotus.md`](../../results/stats/stats.scotus.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 12 sessions, **0 errors**, 12 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- checks that fired (sessions): `info:segments_under_50ms` 6, `info:speaker_under_1s` 1, `warning:segments_over_60s` 12
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 0.0% of reference speech; reference speech without energy = 2.9%. Most-flagged sessions: `scotus__2022_20-1199_25450` (0.00), `scotus__2022_21-1168_25458` (0.00), `scotus__2022_21-376_25455` (0.00), `scotus__2022_21-432_25444` (0.00), `scotus__2022_21-442_25445` (0.00)
- full report: [`results/validation/validation.scotus.default.md`](../../results/validation/validation.scotus.default.md)
- **Silero VAD x2 audit** (view `default`, from the [VAD study](../../docs/silero_vad_study.md)): 7.51% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.0% of reference speech.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (term2022) | 12 | 20.5 | primary | **31.66** | 1.10 | 11.16 | 19.40 | 47.68 | 30.25 | 0% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/scotus.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 12 | 11.16 | 5.83 | 5.33 | 0.0 | 0.0 | 0.0 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 0 of 0 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (0 of 0 s).

**Time-offset check (default):** 0 of 12 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 1.05 s.
<!-- /auto:diagnosis -->

**Reading the SCOTUS numbers.** DER is 31.7% at collar 0 and barely lower at 0.25 s (30.3%), because the errors are
not boundary effects:
- **Speaker confusion 19.4%** comes from the model limit: each argument has 11-13 speakers (nine justices plus
  advocates) and Nemotron outputs at most 8, so several justices are merged on every recording (speaker-count
  accuracy 0%).
- **Missed speech 11.2%**: about half (5.8 points) falls in silence, where Oyez's tiled turns label pauses as speech
  (reference convention). The other half is audible speech the model drops.
- **No false alarm at all** (0.0%): the tiled reference labels everything as speech, so the model cannot be
  "wrong" there. Interruptions and cross-talk are not represented as overlap, so this reference cannot test
  overlap handling either.
Use it for long-form, many-speaker speaker tracking with a generous collar, not as an overlap-aware benchmark.


## Quality rating

**C.** Human transcripts with reliable global speaker ids in a valuable domain, but coarse, tiled turn timing and no
overlap. Use collar 0.25 s or more and expect inflated miss/FA numbers that are not model errors.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare scotus            # download (resumable) + normalize (idempotent)
python -m diards validate scotus --vad     # ground-truth checks
python -m diards stats scotus
python -m diards export scotus --format nemo      # or pyannote / lhotse
python -m diards evaluate scotus --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("scotus", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

Options: `--opt term=2019 --opt n_cases=30` to sample a different term or more cases.

## Citation

Oyez (Justia and the Legal Information Institute, Cornell Law School), <https://www.oyez.org>.
