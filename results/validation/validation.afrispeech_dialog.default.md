# Validation: afrispeech_dialog (view: default)

- sessions: 46, errors: 0, warnings: 30
- sessions whose ORIGINAL labels needed fixing during normalization: 21
- original-label issue totals: zero_duration=63, same_speaker_overlap=5, negative_duration=16, negative_start=1

| level:code | sessions |
|---|---:|
| info:segments_under_50ms | 20 |
| warning:possible_unannotated_speech | 2 |
| warning:segments_over_60s | 28 |

VAD cross-check (energy VAD, same view audio):
- reference speech: 6.16 h
- VAD speech outside reference (+/-0.25 s, chunks >= 0.5 s): 0.0115 of reference speech
- reference speech where the VAD sees no energy: 0.0473
- sessions with most VAD speech outside the reference: afrispeech_dialog__392c7093-7347-40b8-ab37-db1dcc90945d (0.1015), afrispeech_dialog__f533e2de-bac6-4866-8803-b33407813e92 (0.06), afrispeech_dialog__eceb9468-7001-4ee0-9475-13486e5352ae (0.041), afrispeech_dialog__60344b07-b93e-4e14-8b1b-d544d9cd6a16 (0.0403), afrispeech_dialog__4fc2c19e-de60-4be0-91b5-7870f60f2d99 (0.0336), afrispeech_dialog__fd258274-0797-4cdd-b6ea-426ae9723bf7 (0.0289), afrispeech_dialog__818f0aa2-ce0f-4e82-96ee-d66e192a2fca (0.0262), afrispeech_dialog__3e27c06c-8ba1-4511-88e6-c75b2d9d8839 (0.0257), afrispeech_dialog__d2f0bed6-f3e1-48a8-9fb2-ceb137670bc4 (0.0223), afrispeech_dialog__cd255fe0-ebc2-47a0-a990-2ab1ba9ca23d (0.0215)

## Sessions with errors/warnings

- **afrispeech_dialog__0adaefab-c0fa-4d55-9564-100d2bd5bd93**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__0f572000-4660-4c37-addc-3443e3448e0c**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__136be64d-ca9e-473e-9c0e-fc4b008de0cd**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__17745a2c-6705-42df-9949-bbe78aa70307**: segments_over_60s (4 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__185152d7-0c16-45e5-8f1e-862e5766f39a**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__27f9dfd2-193a-46f1-8d2b-f87fb84b6b6a**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__30a5b6a2-8370-4dac-bc7f-e4ae7c1d8562**: segments_over_60s (8 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__363c7601-e830-4db8-ae3b-ae88b9fb29e1**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__3e27c06c-8ba1-4511-88e6-c75b2d9d8839**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__4d398d1f-5058-4e5b-8070-23f42089f14e**: segments_over_60s (5 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__83a0b048-c0e3-4929-9b29-278a873ab7c6**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__98cc8263-54e8-4101-8942-7ae18f1e082b**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__9c267f6c-5a01-4174-bdd3-a53ff045f506**: segments_over_60s (4 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__ad6848ae-2614-4da8-b129-62b0d86e8926**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__b5079ba2-df1c-448d-89f4-685241747496**: segments_over_60s (4 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__b945928d-8fd3-4b41-80ce-6c029486c454**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__bb52e43b-e30c-4fb7-87d6-97ee79ce25ea**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__c1fd9c2e-cd94-46d4-83c1-7ad12c4720a2**: segments_over_60s (3 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__c5d612f8-d493-4611-a5da-168ecbd3db35**: segments_over_60s (5 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__ca43d51b-8431-443a-bcd7-2742819032c8**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__ce541c27-b35d-4b11-ba04-24d3abcb85d3**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__df50b219-f5aa-4d56-9f33-6865c96fda2b**: segments_over_60s (3 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__e0b202dc-17fe-4936-a3c7-d89c639d9cda**: segments_over_60s (2 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__ebcde1b4-bd3b-49b7-b777-e7d87a7cb7f3**: segments_over_60s (3 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__f01e751c-11e3-498b-a6ee-5d9bf11ac8cd**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__f1345c7a-87ca-4c7c-a22f-04dd30bdea30**: segments_over_60s (3 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__f533e2de-bac6-4866-8803-b33407813e92**: possible_unannotated_speech (energy VAD finds 20 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 6.0% of reference speech)
- **afrispeech_dialog__392c7093-7347-40b8-ab37-db1dcc90945d**: possible_unannotated_speech (energy VAD finds 66 s of energy-speech (>= 0.5 s chunks) outside reference speech (+/-0.25 s): 10.1% of reference speech)
- **afrispeech_dialog__7e832fef-ddde-4f8b-8687-eefcf95fe1ce**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
- **afrispeech_dialog__d2f0bed6-f3e1-48a8-9fb2-ceb137670bc4**: segments_over_60s (1 segment(s) longer than 60 s (merged turns?))
