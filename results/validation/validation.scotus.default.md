# Validation: scotus (view: default)

- sessions: 12, errors: 0, warnings: 12
- sessions whose ORIGINAL labels needed fixing during normalization: 0

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 6 |
| info:speaker_under_1s | 1 |
| warning:segments_over_60s | 12 |

Energy-VAD cross-check (same view audio):
- reference speech: 20.49 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0 of reference speech
- reference speech where the VAD sees no energy: 0.0294
- sessions with most energy-speech outside the reference: scotus__2022_20-1199_25450 (0.0), scotus__2022_21-1168_25458 (0.0), scotus__2022_21-376_25455 (0.0), scotus__2022_21-432_25444 (0.0), scotus__2022_21-442_25445 (0.0), scotus__2022_21-454_25446 (0.0), scotus__2022_21-468_25447 (0.0), scotus__2022_21-476_25462 (0.0), scotus__2022_21-846_25453 (0.0), scotus__2022_21-869_25448 (0.0)

## Sessions with errors/warnings

- **scotus__2022_20-1199_25450**: segments_over_60s (21 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-1168_25458**: segments_over_60s (19 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-376_25455**: segments_over_60s (40 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-432_25444**: segments_over_60s (16 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-442_25445**: segments_over_60s (11 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-454_25446**: segments_over_60s (12 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-468_25447**: segments_over_60s (17 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-476_25462**: segments_over_60s (19 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-846_25453**: segments_over_60s (12 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-869_25448**: segments_over_60s (16 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_21-86_25451**: segments_over_60s (26 segment(s) longer than 60 s (merged turns?))
- **scotus__2022_22O145_25368**: segments_over_60s (19 segment(s) longer than 60 s (merged turns?))
