# Validation: sbcsae (view: default)

- sessions: 60, errors: 0, warnings: 26
- sessions whose ORIGINAL labels needed fixing during normalization: 51
- original-label issue totals: same_speaker_overlap=918, duplicate_segment=4

| level:code | sessions |
|---|---:|
| info:silence_over_30s | 6 |
| info:speaker_under_1s | 7 |
| warning:fewer_than_two_speakers | 1 |
| warning:possible_unannotated_speech | 4 |
| warning:segments_over_60s | 21 |

Energy-VAD cross-check (same view audio):
- reference speech: 21.36 h
- energy speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0141 of reference speech
- reference speech where the VAD sees no energy: 0.2015
- sessions with most energy-speech outside the reference: sbcsae__SBC024 (0.1112), sbcsae__SBC055 (0.0944), sbcsae__SBC038 (0.0657), sbcsae__SBC045 (0.0624), sbcsae__SBC058 (0.043), sbcsae__SBC018 (0.0342), sbcsae__SBC037 (0.0337), sbcsae__SBC054 (0.0328), sbcsae__SBC022 (0.0284), sbcsae__SBC050 (0.0274)

## Sessions with errors/warnings

- **sbcsae__SBC001**: segments_over_60s (6 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC005**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC006**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC012**: segments_over_60s (4 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC014**: segments_over_60s (4 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC017**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC020**: segments_over_60s (5 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC024**: possible_unannotated_speech (energy VAD finds 76 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 11.1% of reference speech)
- **sbcsae__SBC025**: fewer_than_two_speakers (1 speaker(s)); segments_over_60s (7 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC034**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC038**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?)); possible_unannotated_speech (energy VAD finds 71 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.6% of reference speech)
- **sbcsae__SBC039**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC040**: segments_over_60s (5 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC043**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC044**: segments_over_60s (4 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC045**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?)); possible_unannotated_speech (energy VAD finds 89 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.2% of reference speech)
- **sbcsae__SBC046**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC047**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC054**: segments_over_60s (5 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC055**: segments_over_60s (8 segment(s) longer than 60 s (merged turns?)); possible_unannotated_speech (energy VAD finds 138 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 9.4% of reference speech)
- **sbcsae__SBC057**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **sbcsae__SBC060**: segments_over_60s (6 segment(s) longer than 60 s (merged turns?))
