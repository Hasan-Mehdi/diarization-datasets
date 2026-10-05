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
_Not evaluated yet._
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
_Not run yet._
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
