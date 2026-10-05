# Validation: earnings21 (view: default)

- sessions: 44, errors: 0, warnings: 8
- sessions whose ORIGINAL labels needed fixing during normalization: 0

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 36 |
| info:silence_over_30s | 4 |
| info:speaker_under_1s | 2 |
| warning:possible_unannotated_speech | 2 |
| warning:segments_over_60s | 6 |

Energy-VAD cross-check (same view audio):
- reference speech: 32.82 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.01 of reference speech
- reference speech where the VAD sees no energy: 0.0133
- sessions with most energy-speech outside the reference: earnings21__4387383 (0.2725), earnings21__4384964 (0.1221), earnings21__4384198 (0.0352), earnings21__4394084 (0.0169), earnings21__4384683 (0.0152), earnings21__4346923 (0.0147), earnings21__4389907 (0.0124), earnings21__4375653 (0.0108), earnings21__4368670 (0.0107), earnings21__4344866 (0.0086)

## Sessions with errors/warnings

- **earnings21__4367535**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **earnings21__4384964**: possible_unannotated_speech (energy VAD finds 356 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 12.2% of reference speech)
- **earnings21__4361631**: segments_over_60s (3 segment(s) longer than 60 s (merged turns?))
- **earnings21__4375653**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **earnings21__4382825**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **earnings21__4387383**: possible_unannotated_speech (energy VAD finds 387 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 27.2% of reference speech)
- **earnings21__4397800**: segments_over_60s (10 segment(s) longer than 60 s (merged turns?))
- **earnings21__4397829**: segments_over_60s (7 segment(s) longer than 60 s (merged turns?))
