# Validation: maptask (view: default)

- sessions: 128, errors: 0, warnings: 12
- sessions whose ORIGINAL labels needed fixing during normalization: 1
- original-label issue totals: beyond_audio_end=453, seconds_beyond_audio_end=442.009

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 5 |
| info:silence_over_30s | 2 |
| warning:possible_unannotated_speech | 11 |
| warning:words_outside_reference | 1 |

Energy-VAD cross-check (same view audio):
- reference speech: 9.27 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0176 of reference speech
- reference speech where the VAD sees no energy: 0.003
- sessions with most energy-speech outside the reference: maptask__q3nc3 (0.1375), maptask__q3ec5 (0.1278), maptask__q3nc2 (0.1264), maptask__q3nc7 (0.0733), maptask__q3ec3 (0.0688), maptask__q3ec2 (0.0666), maptask__q1ec4 (0.0663), maptask__q1ec2 (0.0621), maptask__q1ec6 (0.0584), maptask__q7ec5 (0.0561)

## Sessions with errors/warnings

- **maptask__q1ec2**: possible_unannotated_speech (energy VAD finds 11 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.2% of reference speech)
- **maptask__q1ec4**: possible_unannotated_speech (energy VAD finds 7 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.6% of reference speech)
- **maptask__q1ec6**: possible_unannotated_speech (energy VAD finds 5 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.8% of reference speech)
- **maptask__q3ec2**: possible_unannotated_speech (energy VAD finds 8 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.7% of reference speech)
- **maptask__q3ec3**: possible_unannotated_speech (energy VAD finds 17 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.9% of reference speech)
- **maptask__q3ec5**: possible_unannotated_speech (energy VAD finds 20 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 12.8% of reference speech)
- **maptask__q3nc2**: possible_unannotated_speech (energy VAD finds 37 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 12.6% of reference speech)
- **maptask__q3nc3**: possible_unannotated_speech (energy VAD finds 23 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 13.8% of reference speech)
- **maptask__q3nc7**: possible_unannotated_speech (energy VAD finds 9 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 7.3% of reference speech)
- **maptask__q5ec5**: possible_unannotated_speech (energy VAD finds 9 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.1% of reference speech)
- **maptask__q6ec2**: words_outside_reference (88.5% of word time is outside same-speaker reference segments)
- **maptask__q7ec5**: possible_unannotated_speech (energy VAD finds 10 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.6% of reference speech)
