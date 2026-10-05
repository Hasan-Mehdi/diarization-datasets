# Validation: icsi (view: ihm-mix)

- sessions: 75, errors: 0, warnings: 16
- sessions whose ORIGINAL labels needed fixing during normalization: 74
- original-label issue totals: same_speaker_overlap=986, beyond_audio_end=1, seconds_beyond_audio_end=2122.616

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 10 |
| info:silence_over_30s | 19 |
| info:speaker_under_1s | 1 |
| warning:possible_unannotated_speech | 10 |
| warning:segments_over_60s | 6 |

Energy-VAD cross-check (same view audio):
- reference speech: 58.8 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0238 of reference speech
- reference speech where the VAD sees no energy: 0.0466
- sessions with most energy-speech outside the reference: icsi__Bed008 (0.1824), icsi__Bed016 (0.1351), icsi__Bed012 (0.1121), icsi__Bed010 (0.1097), icsi__Bed003 (0.0942), icsi__Bed009 (0.0618), icsi__Bed014 (0.0567), icsi__Bro007 (0.0557), icsi__Bro026 (0.0541), icsi__Bmr013 (0.0513)

## Sessions with errors/warnings

- **icsi__Bns001**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **icsi__Bmr013**: possible_unannotated_speech (energy VAD finds 117 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.1% of reference speech)
- **icsi__Bed002**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **icsi__Bed003**: possible_unannotated_speech (energy VAD finds 257 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 9.4% of reference speech)
- **icsi__Bed008**: possible_unannotated_speech (energy VAD finds 549 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 18.2% of reference speech)
- **icsi__Bed009**: possible_unannotated_speech (energy VAD finds 149 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.2% of reference speech)
- **icsi__Bed010**: possible_unannotated_speech (energy VAD finds 263 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 11.0% of reference speech)
- **icsi__Bed012**: possible_unannotated_speech (energy VAD finds 183 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 11.2% of reference speech)
- **icsi__Bed014**: possible_unannotated_speech (energy VAD finds 148 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.7% of reference speech)
- **icsi__Bed016**: possible_unannotated_speech (energy VAD finds 261 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 13.5% of reference speech)
- **icsi__Bro004**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **icsi__Bro007**: possible_unannotated_speech (energy VAD finds 79 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.6% of reference speech)
- **icsi__Bro008**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **icsi__Bro012**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **icsi__Bro026**: possible_unannotated_speech (energy VAD finds 144 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.4% of reference speech)
- **icsi__Bsr001**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
