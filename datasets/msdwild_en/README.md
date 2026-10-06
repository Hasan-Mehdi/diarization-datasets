# MSDWild (English subset)

MSDWild ("Multi-modal Speaker Diarization dataset in the Wild") has 3,143 vlog-style video clips (~80 h) of daily
conversation with frequent overlap, labelled for audio-visual diarization. The corpus is multilingual and has no
language tags, so this repo derives a reproducible **English subset with Whisper large-v3 language ID** and
publishes the per-clip language probabilities ([`metadata/msdwild_lid.json`](../../metadata/msdwild_lid.json)).

<!-- auto:meta -->
| | |
|---|---|
| License | MSDWild license agreement (research only, no redistribution) ([link](https://github.com/X-LANCE/MSDWILD/blob/master/MSDWILD_license_agreement.pdf)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free download (Google Drive); accept the research-only license agreement. |
| Source version used | X-LANCE/MSDWILD (git HEAD rttms) + wav archive (Google Drive, md5 0057f82d...) |
| Domain | vlogs (in-the-wild media) |
| Views (normalized) | `default`: Clip audio, mono 16 kHz |
| Reference used as primary RTTM | Manual audio-visual annotation (pauses > 0.25 s split), later corrections credited in the repo. |
| Ground-truth rating | **B** - Human, diarization-oriented labels with overlap, but short clips, no language tags, and the maintainers withdrew ~90 files; label quality checked below. |
| Prepared splits (sessions) | few.train: 744, few.val: 114, many.val: 36 |
<!-- /auto:meta -->

## Source and access

- Annotations: <https://github.com/X-LANCE/MSDWILD> (`rttms/all.rttm`, `few.train.rttm`, `few.val.rttm`, `many.val.rttm`).
- Audio: Google Drive archive linked from the repo (7.56 GB on the page; 8.12 GB downloaded, md5
  `0057f82daaddf2ce993d1bf0679929c4`). Videos and face tracks are also available.
- License: `MSDWILD_license_agreement.pdf`: research use only, no redistribution, cite. Read and accept it before
  use. The repo publishes only clip ids and language probabilities, no audio or labels.

## Annotation methodology

Liu et al. (Interspeech 2022): human annotators labelled speaker turns on the video clips (audio-visual, so
off-screen speakers are labelled by voice). Diarization-oriented conventions (pauses > ~0.25 s split), overlap
labelled. The maintainers later fixed annotation issues reported by users and asked users to ignore ~90 files with
negative names, which were withdrawn.

## English subset (our derivation)

Whisper large-v3 language detection on up to three 30-second windows centred on reference speech; window
probabilities are averaged and a clip is kept when P(en) >= 0.7. Result: **894 of 3,143 clips**. Mixed-language
and code-switched clips are excluded on purpose. Note that `few.train` is a training split and the validation
splits are the usual test material.

## Known issues and errata

- No language labels in the original. Our subset depends on LID; clips near the threshold may be mixed-language.
- Short clips (tens of seconds to a few minutes), so per-file speaker counts are low and DER is noisy per file.
- Withdrawn files (negative ids) are skipped.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| few.train | 744 | 23.75 | 22.03 | 0.928 | 0.1 | 0.0027 | 2/2/4 | 0.411/1.574/11.333 | 0.0002 | 1.248 | 11.85 |
| few.val | 114 | 3.02 | 2.75 | 0.912 | 0.109 | 0.0046 | 2/2/4 | 0.408/1.418/9.824 | 0.0 | 1.334 | 14.37 |
| many.val | 36 | 1.14 | 0.99 | 0.873 | 0.111 | 0.0135 | 3/5/9 | 0.375/1.176/12.373 | 0.0 | 2.111 | 17.02 |
| ALL | 894 | 27.91 | 25.78 | 0.924 | 0.101 | 0.0033 | 2/2/9 | 0.408/1.524/11.142 | 0.0002 | 1.293 | 12.34 |

Computed by `python -m diards stats msdwild_en` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.msdwild_en.md`](../../results/stats/stats.msdwild_en.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 894 sessions, **0 errors**, 48 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- checks that fired (sessions): `info:speaker_under_1s` 39, `warning:possible_unannotated_speech` 45, `warning:segments_over_60s` 3
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 0.5% of reference speech; reference speech without energy = 4.7%. Most-flagged sessions: `msdwild_en__00740` (0.39), `msdwild_en__01631` (0.34), `msdwild_en__02080` (0.31), `msdwild_en__00880` (0.30), `msdwild_en__02311` (0.29)
- full report: [`results/validation/validation.msdwild_en.default.md`](../../results/validation/validation.msdwild_en.default.md)
- **Silero VAD x2 audit** (view `default`, from the [VAD study](../../docs/silero_vad_study.md)): 2.79% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.32% of reference speech; Whisper finds intelligible speech in 8 of the 20 longest such regions.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (few.val, many.val) | 150 | 4.16 | primary | **17.79** | 3.87 | 9.55 | 4.37 | 32.71 | 10.67 | 76% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/msdwild_en.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 150 | 5.52 | 2.21 | 3.31 | 2.69 | 1.18 | 1.51 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 2 of 10 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (3.1 of 17.1 s). Examples: `msdwild_en__02646` 63.3-64.9 s: "Oh my god."; `msdwild_en__02241` 61.8-63.3 s: "I love cashews."

**Time-offset check (default):** 5 of 150 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.05 s; shifted: `msdwild_en__00239` (-3.75 s), `msdwild_en__01240` (-3.00 s), `msdwild_en__00785` (+2.20 s).
<!-- /auto:diagnosis -->

**Reading the MSDWild numbers.** DER is 17.8% at collar 0 on the 150 English validation clips (few.val + many.val).
Speech detection on its own is good (speaker-agnostic miss 5.5%, FA 2.7%). The rest comes from overlapped speech
(10% of speech) and speaker confusion (4.4%) in short, lively clips with up to 9 speakers, which is real model
difficulty. The labels look sound: only 2 of the 10 long audible false alarms contain words. The offset check
flags 5 of 150 clips, but with tiny gains (2-3 points) at multi-second lags; with clips of a few tens of seconds
these are most likely chance alignments of turn patterns, not real shifts.


## Quality rating

**B.** Human, diarization-oriented labels with natural overlap in casual, noisy, real-life conversation. Minus:
research-only license, LID-derived English subset, short clips.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare msdwild_en            # download (resumable) + normalize (idempotent)
python -m diards validate msdwild_en --vad     # ground-truth checks
python -m diards stats msdwild_en
python -m diards export msdwild_en --format nemo      # or pyannote / lhotse
python -m diards evaluate msdwild_en --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("msdwild_en", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

T. Liu et al., "MSDWild: Multi-modal Speaker Diarization Dataset in the Wild", Interspeech 2022.
