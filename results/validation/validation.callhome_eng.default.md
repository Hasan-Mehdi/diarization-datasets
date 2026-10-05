# Validation: callhome_eng (view: default)

- sessions: 140, errors: 0, warnings: 3
- sessions whose ORIGINAL labels needed fixing during normalization: 23
- original-label issue totals: same_speaker_overlap=30

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 17 |
| info:silence_over_30s | 2 |
| info:speaker_under_1s | 4 |
| warning:possible_unannotated_speech | 3 |

Energy-VAD cross-check (same view audio):
- reference speech: 17.53 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.006 of reference speech
- reference speech where the VAD sees no energy: 0.0082
- sessions with most energy-speech outside the reference: callhome_eng__eng_037 (0.321), callhome_eng__eng_011 (0.0772), callhome_eng__eng_099 (0.0606), callhome_eng__eng_013 (0.0304), callhome_eng__eng_072 (0.0297), callhome_eng__eng_012 (0.0275), callhome_eng__eng_073 (0.0273), callhome_eng__eng_109 (0.0236), callhome_eng__eng_057 (0.0141), callhome_eng__eng_100 (0.0139)

## Sessions with errors/warnings

- **callhome_eng__eng_011**: possible_unannotated_speech (energy VAD finds 37 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 7.7% of reference speech)
- **callhome_eng__eng_037**: possible_unannotated_speech (energy VAD finds 148 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 32.1% of reference speech)
- **callhome_eng__eng_099**: possible_unannotated_speech (energy VAD finds 13 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.1% of reference speech)
