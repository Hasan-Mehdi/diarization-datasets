# Validation: chime6 (view: ihm-mix)

- sessions: 4, errors: 0, warnings: 2
- sessions whose ORIGINAL labels needed fixing during normalization: 0

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 4 |
| info:silence_over_30s | 2 |
| warning:possible_unannotated_speech | 2 |

Energy-VAD cross-check (same view audio):
- reference speech: 6.85 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0425 of reference speech
- reference speech where the VAD sees no energy: 0.0866
- sessions with most energy-speech outside the reference: chime6__S21 (0.0802), chime6__S01 (0.0582), chime6__S02 (0.0161), chime6__S09 (0.0147)

## Sessions with errors/warnings

- **chime6__S01**: possible_unannotated_speech (energy VAD finds 372 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.8% of reference speech)
- **chime6__S21**: possible_unannotated_speech (energy VAD finds 487 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 8.0% of reference speech)
