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
