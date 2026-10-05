# DiPCo (Dinner Party Corpus)

Amazon's dinner-party corpus: 10 sessions of four volunteers eating and talking around a table in a lab dining
room (5.3 h), with headsets and five 7-microphone devices. Background music is played from a fixed point in each
session. It is small, permissively licensed (CDLA-Permissive), and a cleaner, shorter companion to CHiME-6.

<!-- auto:meta -->
| | |
|---|---|
| License | CDLA-Permissive-1.0 ([link](https://cdla.dev/permissive-1-0/)) |
| Annotations redistributable here | yes |
| Access | Free download from Zenodo (13.4 GB), no registration. |
| Source version used | Zenodo 8122551 DipCo.tgz (md5 2297eb93...) |
| Domain | dinner party (lab, far-field) |
| Views (normalized) | `farfield`: Device U01, channel 1 (far-field); `ihm-mix`: Sum of the 4 close-talk headsets |
| Reference used as primary RTTM | Human transcription of each headset, utterance segments of up to 10-15 s. |
| Ground-truth rating | **B** - Every participant on a headset and transcribed, overlap fully covered, but segments are ASR-oriented (split only at 'logical' points, up to 10-15 s), so pauses are labelled as speech. |
| Prepared splits (sessions) | dev: 5, eval: 5 |
<!-- /auto:meta -->

## Source and access

- Zenodo record [8122551](https://zenodo.org/records/8122551): `DipCo.tgz`, 13.4 GB, md5 `2297eb9334f3b90e02b54b708e501b24`
  (Zenodo delivered ~1 MB/s when tested; the recipe resumes interrupted downloads).
- Also part of CHiME-7 DASR (sessions renamed with an offset of 24 there). HF mirror: `huckiyang/DiPCo`.
  Lhotse recipe: `lhotse.recipes.prepare_dipco`.

## Annotation methodology

Each headset was transcribed manually with utterance boundaries. Per the README, transcribers split long stretches
of speech at "logical" points such as sentence starts, into segments of up to 10 s (15 s if necessary). So the
segments are **ASR-oriented**: pauses inside a segment are labelled as speech. Times are given per device and are
identical across devices (synchronised).

The recipe also writes a diagnostic `rttm_alt/closetalk_activity`: per-headset activity (level threshold calibrated
on each headset), restricted to within 0.5 s of that speaker's labelled utterances so crosstalk is not counted.
This shows how much of the labelled time is silent.

## Known issues and errata

- Loose, sentence-level segment boundaries (see above). Horiguchi et al. (ASRU 2025) list DiPCo among the
  "ASR-oriented" corpora.
- Each session begins with participants reading "speaker one", "speaker two"... (enrolment), which *is* labelled.
- Music playback in the second part of every session affects far-field audio only.
- Small: 5 eval sessions. The DiPCo dev sessions are in Nemotron 3 Diarization's training data, the eval sessions are not.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| dev | 5 | 2.73 | 2.52 | 0.921 | 0.279 | 0.0431 | 4/4/4 | 0.69/1.73/11.358 | 0.0 | 2.895 | 18.0 |
| eval | 5 | 2.6 | 2.36 | 0.906 | 0.275 | 0.0612 | 4/4/4 | 0.65/1.48/12.992 | 0.0006 | 3.56 | 17.41 |
| ALL | 10 | 5.33 | 4.87 | 0.914 | 0.277 | 0.0518 | 4/4/4 | 0.67/1.61/12.156 | 0.0003 | 3.18 | 17.71 |

Computed by `python -m diards stats dipco` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.dipco.md`](../../results/stats/stats.dipco.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `ihm-mix`: 10 sessions, **0 errors**, 4 warnings (normalized files); 10 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: same_speaker_overlap = 165
- checks that fired (sessions): `info:segments_under_50ms` 1, `info:silence_over_30s` 1, `warning:segments_over_60s` 4
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 1.2% of reference speech; reference speech without energy = 3.7%. Most-flagged sessions: `dipco__S04` (0.03), `dipco__S05` (0.02), `dipco__S02` (0.01), `dipco__S08` (0.01), `dipco__S01` (0.01)
- full report: [`results/validation/validation.dipco.ihm-mix.md`](../../results/validation/validation.dipco.ihm-mix.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| farfield (eval) | 5 | 2.6 | primary | **36.16** | 3.61 | 30.49 | 2.06 | 39.06 | 28.07 | 40% |
| farfield (eval) | 5 | 2.6 | closetalk_activity | **40.32** | 11.99 | 25.28 | 3.05 | 39.01 | 18.31 | 40% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/dipco.*/results.md`.

> **Training-data overlap:** DiPCo dev was used for training; the eval split scored here is held out.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| farfield | ihm-mix | 5 | 17.89 | 5.55 | 12.34 | 0.93 | 0.51 | 0.42 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (farfield):** 3 of 10 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (6.4 of 16.1 s). Examples: `dipco__S01` 1349.8-1352.3 s: "It's actually quite different."; `dipco__S03` 718.7-721.2 s: "It's also good to know that that's not what you will be"; `dipco__S03` 715.7-717.0 s: "Definitely good to go out on a hike."

**Time-offset check (farfield):** 0 of 5 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.25 s.
<!-- /auto:diagnosis -->

## Quality rating

**B.** Complete close-talk transcription with overlap, permissive license. The 10-15 s segments overstate speech
time; prefer collar 0.25 s or the close-talk activity reference when you need tight boundaries.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare dipco            # download (resumable) + normalize (idempotent)
python -m diards validate dipco --vad     # ground-truth checks
python -m diards stats dipco
python -m diards export dipco --format nemo      # or pyannote / lhotse
python -m diards evaluate dipco --view farfield  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("dipco", view="farfield"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

M. Van Segbroeck et al., "DiPCo - Dinner Party Corpus", Interspeech 2020.
