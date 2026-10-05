# Validation: dipco (view: ihm-mix)

- sessions: 10, errors: 0, warnings: 4
- sessions whose ORIGINAL labels needed fixing during normalization: 10
- original-label issue totals: same_speaker_overlap=165

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 1 |
| info:silence_over_30s | 1 |
| warning:segments_over_60s | 4 |

Energy-VAD cross-check (same view audio):
- reference speech: 4.87 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0116 of reference speech
- reference speech where the VAD sees no energy: 0.0367
- sessions with most energy-speech outside the reference: dipco__S04 (0.0314), dipco__S05 (0.0167), dipco__S02 (0.012), dipco__S08 (0.0112), dipco__S01 (0.0104), dipco__S03 (0.0093), dipco__S09 (0.003), dipco__S07 (0.0008), dipco__S06 (0.0005), dipco__S10 (0.0)

## Sessions with errors/warnings

- **dipco__S02**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **dipco__S01**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **dipco__S03**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **dipco__S07**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
