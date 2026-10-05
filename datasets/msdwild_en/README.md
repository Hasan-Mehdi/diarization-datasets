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
_Statistics not computed yet._
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
_Validation not run yet._
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
