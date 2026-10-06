# Validation: icsi (view: ihm-mix)

- sessions: 75, errors: 0, warnings: 15
- sessions whose ORIGINAL labels needed fixing during normalization: 74
- original-label issue totals: same_speaker_overlap=986, beyond_audio_end=1, seconds_beyond_audio_end=2122.616

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 10 |
| info:silence_over_30s | 4 |
| info:speaker_under_1s | 1 |
| warning:possible_unannotated_speech | 9 |
| warning:segments_over_60s | 6 |

VAD cross-check (energy VAD, same view audio):
- reference speech: 58.8 h
- VAD speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0221 of reference speech
- reference speech where the VAD sees no energy: 0.0466
- sessions with most VAD speech outside the reference: icsi__Bed008 (0.1695), icsi__Bed016 (0.1337), icsi__Bed010 (0.1092), icsi__Bed012 (0.086), icsi__Bed009 (0.0573), icsi__Bed014 (0.0554), icsi__Bro026 (0.0537), icsi__Bro007 (0.0535), icsi__Bed003 (0.051), icsi__Bed013 (0.0464)

## Sessions with errors/warnings

- **icsi__Bns001**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **icsi__Bed002**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **icsi__Bed003**: possible_unannotated_speech (energy VAD finds 139 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.1% of reference speech)
- **icsi__Bed008**: possible_unannotated_speech (energy VAD finds 511 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 17.0% of reference speech)
- **icsi__Bed009**: possible_unannotated_speech (energy VAD finds 138 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.7% of reference speech)
- **icsi__Bed010**: possible_unannotated_speech (energy VAD finds 262 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 10.9% of reference speech)
- **icsi__Bed012**: possible_unannotated_speech (energy VAD finds 141 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 8.6% of reference speech)
- **icsi__Bed014**: possible_unannotated_speech (energy VAD finds 144 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.5% of reference speech)
- **icsi__Bed016**: possible_unannotated_speech (energy VAD finds 258 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 13.4% of reference speech)
- **icsi__Bro004**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **icsi__Bro007**: possible_unannotated_speech (energy VAD finds 76 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.4% of reference speech)
- **icsi__Bro008**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **icsi__Bro012**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **icsi__Bro026**: possible_unannotated_speech (energy VAD finds 143 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.4% of reference speech)
- **icsi__Bsr001**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
