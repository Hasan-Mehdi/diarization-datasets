# NOTSOFAR-1 (recorded meetings)

Microsoft's "Natural Office Talkers in Settings of Far-field Audio Recordings": ~6-minute real office meetings
in 30 rooms, 3-8 participants (35 unique speakers), each wearing a close-talk mic, recorded by many commercial
far-field devices. Released for CHiME-8 Task 2 under CC BY 4.0. It is the best free, recent, real far-field
meeting set with full ground truth, and its eval set is held out from Nemotron 3 Diarization's training data.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-4.0 ([link](https://creativecommons.org/licenses/by/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free download from Hugging Face (no gating) or Azure blob. |
| Source version used | microsoft/NOTSOFAR on Hugging Face: 240825.1_eval_full_with_GT, 240825.1_dev1, 240825.1_train |
| Domain | meetings (far-field) |
| Views (normalized) | `sc`: First single-channel far-field device in devices.json (commercial conference device); `ihm-mix`: Sum of the participants' close-talk microphones |
| Reference used as primary RTTM | Human transcription from close-talk mics with word-level timings (multi-stage annotation). |
| Ground-truth rating | **A-** - Every participant wore a close-talk mic and was transcribed; utterance boundaries are tight and word timings are provided; overlap is fully represented. Utterances can include short internal pauses; <ST/> (unintelligible) stretches have no word timings. |
| Prepared splits (sessions) | dev: 36, eval: 129 |
<!-- /auto:meta -->

## Source and access

- Hugging Face (not gated): [`microsoft/NOTSOFAR`](https://huggingface.co/datasets/microsoft/NOTSOFAR), folders
  `benchmark-datasets/{train,dev,eval}_set/<version>/MTG/<meeting>/`. Also on Azure blob storage
  (see <https://github.com/microsoft/NOTSOFAR1-Challenge>).
- Versions used: `240825.1_eval_full_with_GT` (129 meetings), `240825.1_dev1`, `240825.1_train`.
- Forced-alignment RTTMs (MFA) published with FastMSS (used by the Nemotron model card):
  <https://github.com/popcornell/FastMSS/tree/master/resources> (`notsofar1-sessions_mfa_rttms.tar.gz`, which covers
  dev and the 80-meeting eval_small subset).

## Annotation methodology

Participants wore close-talk mics. Transcription went through a multi-stage process designed to remove machine
bias (Vinnikov et al., Interspeech 2024). `gt_transcription.json` gives utterances with start/end times plus
**word-level timings**. Speaker aliases (e.g. "Ron") are consistent across meetings. Utterance boundaries are tight
around the words but include within-utterance pauses. `<ST/>` marks unintelligible stretches, which have no word
timing.

## Known issues and errata

- Several eval versions exist (`240629.1_eval_small_with_GT` = 80 meetings / 2 devices; `240825.1_eval_full_with_GT`
  = 129 meetings / all devices). Say which one you score.
- The `mc_rockfall_1` device is excluded from the eval sets because of suspected audio problems. Three training
  meetings had faulty white-noise recordings removed in `240825.1_train`.
- Device sets differ per room, so the `sc` view (first single-channel device listed in `devices.json`) is not the
  same physical device in every meeting.
- Horiguchi et al. (ASRU 2025) classify NOTSOFAR-1 as "ASR-oriented" (utterances include pauses). The alternative
  references `words_gap0.2` (words merged across pauses < 0.2 s) and `fastmss_mfa` let you measure the effect.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| dev | 36 | 3.73 | 3.47 | 0.93 | 0.394 | 0.1311 | 5/5/7 | 0.43/1.19/5.64 | 0.0 | 1.51 | 39.63 |
| eval | 129 | 13.34 | 12.46 | 0.934 | 0.301 | 0.0638 | 3/4/7 | 0.4/1.35/6.03 | 0.0002 | 1.06 | 28.51 |
| ALL | 165 | 17.07 | 15.93 | 0.933 | 0.321 | 0.0785 | 3/5/7 | 0.409/1.3/5.95 | 0.0001 | 1.19 | 30.94 |

Computed by `python -m diards stats notsofar1` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.notsofar1.md`](../../results/stats/stats.notsofar1.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `ihm-mix`: 165 sessions, **0 errors**, 0 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 0.0% of reference speech; reference speech without energy = 0.4%. Most-flagged sessions: `notsofar1__MTG_32091` (0.01), `notsofar1__MTG_32049` (0.01), `notsofar1__MTG_32082` (0.01), `notsofar1__MTG_30893` (0.01), `notsofar1__MTG_32051` (0.01)
- full report: [`results/validation/validation.notsofar1.ihm-mix.md`](../../results/validation/validation.notsofar1.ihm-mix.md)
- **Silero VAD x2 audit** (view `ihm-mix`, from the [VAD study](../../docs/silero_vad_study.md)): 2.37% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.02% of reference speech; Whisper finds intelligible speech in 5 of the 5 longest such regions.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| ihm-mix (eval) | 129 | 13.34 | primary | **14.52** | 0.68 | 12.57 | 1.27 | 17.21 | 5.51 | 95% |
| ihm-mix (eval) | 80 | 8.33 | fastmss_mfa | **9.63** | 4.37 | 3.68 | 1.58 | 12.58 | 2.56 | 95% |
| ihm-mix (eval) | 129 | 13.34 | words_gap0.2 | **11.16** | 1.37 | 8.40 | 1.39 | 14.01 | 4.65 | 95% |
| sc (eval) | 129 | 13.34 | primary | **18.41** | 0.60 | 15.91 | 1.90 | 20.74 | 6.92 | 77% |
| sc (eval) | 80 | 8.33 | fastmss_mfa | **11.32** | 2.62 | 6.07 | 2.63 | 14.30 | 3.64 | 77% |
| sc (eval) | 129 | 13.34 | words_gap0.2 | **14.98** | 1.14 | 11.77 | 2.07 | 17.55 | 6.01 | 77% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/notsofar1.*/results.md`.

> **Training-data overlap:** NOTSOFAR-1 train+dev were used for training; the eval set scored here is held out.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ihm-mix | ihm-mix | 129 | 5.44 | 1.66 | 3.78 | 0.29 | 0.08 | 0.21 |
| sc | ihm-mix | 129 | 6.19 | 1.82 | 4.37 | 0.29 | 0.07 | 0.22 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (ihm-mix):** 5 of 5 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (7.6 of 7.6 s). Examples: `notsofar1__MTG_32051` 203.2-205.4 s: "with a canapé tray."; `notsofar1__MTG_32091` 12.6-14.1 s: "We've had company stores."; `notsofar1__MTG_32049` 89.4-90.8 s: "but is there anything that is like,"

**Time-offset check (ihm-mix):** 0 of 129 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.0 s.

**Whisper audit of the longest audible false alarms (sc):** 4 of 5 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (6.3 of 7.6 s). Examples: `notsofar1__MTG_32051` 203.2-205.4 s: "with a canapé tray"; `notsofar1__MTG_32091` 12.6-14.1 s: "We've had company stores."; `notsofar1__MTG_32049` 89.4-90.8 s: "but is there anything that is like,"
<!-- /auto:diagnosis -->

**Reading the NOTSOFAR-1 numbers.** Against the official utterance segments, Nemotron's error is dominated by missed
speech (15.9% on the far-field `sc` view, 12.6% on the close-talk mix). Against word-based segments
(`words_gap0.2`) DER drops by 3-4 points, and against the MFA reference (80-meeting subset) to 11.3% (`sc`) and 9.6%
(`ihm-mix`). So a sizeable part of the "miss" is pause time inside utterances: a reference convention, not model
error. The validator found the labels otherwise very clean: no label errors, and only 0.04% of energy-speech on the
close-talk mix falls outside the reference. The far-field view adds ~4 points over the close-talk mix and lowers
speaker-count accuracy (77% vs 95%): a real acoustic difficulty, i.e. model error.


## Quality rating

**A-.** Real meetings, everyone close-talk transcribed with a documented multi-stage process, word timings and
full overlap. Only the utterance-level boundaries (pauses inside) keep it from an A. Use `words_gap0.2` when you
need tight boundaries.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare notsofar1            # download (resumable) + normalize (idempotent)
python -m diards validate notsofar1 --vad     # ground-truth checks
python -m diards stats notsofar1
python -m diards export notsofar1 --format nemo      # or pyannote / lhotse
python -m diards evaluate notsofar1 --view sc  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("notsofar1", view="sc"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

A. Vinnikov et al., "NOTSOFAR-1 Challenge: New Datasets, Baseline, and Tasks for Distant Meeting Transcription", Interspeech 2024.
