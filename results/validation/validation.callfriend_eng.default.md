# Validation: callfriend_eng (view: default)

- sessions: 40, errors: 1, warnings: 4
- sessions whose ORIGINAL labels needed fixing during normalization: 32
- original-label issue totals: same_speaker_overlap=3074, beyond_audio_end=5, seconds_beyond_audio_end=0.344, placeholder_speaker_label=1

| level:code | sessions |
|---|---:|
| error:normalized_placeholder_speaker_label | 1 |
| info:segments_under_50ms | 2 |
| info:silence_over_30s | 1 |
| info:speaker_under_1s | 1 |
| warning:possible_unannotated_speech | 3 |
| warning:segments_over_60s | 1 |

Energy-VAD cross-check (same view audio):
- reference speech: 9.38 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0172 of reference speech
- reference speech where the VAD sees no energy: 0.0497
- sessions with most energy-speech outside the reference: callfriend_eng__eng-n_002 (0.1787), callfriend_eng__eng-s_001 (0.144), callfriend_eng__eng-n_027 (0.0507), callfriend_eng__eng-n_004 (0.0406), callfriend_eng__eng-n_028 (0.0323), callfriend_eng__eng-n_021 (0.0225), callfriend_eng__eng-s_008 (0.0221), callfriend_eng__eng-n_018 (0.0183), callfriend_eng__eng-n_025 (0.0179), callfriend_eng__eng-n_026 (0.0156)

## Sessions with errors/warnings

- **callfriend_eng__eng-n_002**: possible_unannotated_speech (energy VAD finds 170 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 17.9% of reference speech)
- **callfriend_eng__eng-n_013**: normalized_placeholder_speaker_label (1 in normalized RTTM)
- **callfriend_eng__eng-n_016**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **callfriend_eng__eng-n_027**: possible_unannotated_speech (energy VAD finds 15 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 5.1% of reference speech)
- **callfriend_eng__eng-s_001**: possible_unannotated_speech (energy VAD finds 64 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 14.4% of reference speech)
