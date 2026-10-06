# Nemotron 3 Diarization on afrispeech_dialog (view: default)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 46 (6.63 h); speaker-count accuracy 93.5%, MAE 0.07; RTFx None
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 25.00 | 4.76 | 15.15 | 5.10 | 31.27 | 6.16 |
| primary | 0.25 | 22.75 | 3.50 | 14.87 | 4.38 | 28.46 | 5.91 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog__0adaefab-c0fa-4d55-9564-100d2bd5bd93 | general | 2.1 | 2 | 2 | 0.024 | 28.31 | 6.59 | 16.22 | 5.50 | 42.40 |
| afrispeech_dialog__0f572000-4660-4c37-addc-3443e3448e0c | general | 6.2 | 2 | 2 | 0.000 | 7.75 | 1.75 | 5.57 | 0.43 | 9.11 |
| afrispeech_dialog__136be64d-ca9e-473e-9c0e-fc4b008de0cd | general | 14.4 | 2 | 2 | 0.000 | 24.53 | 9.01 | 11.65 | 3.87 | 25.18 |
| afrispeech_dialog__17745a2c-6705-42df-9949-bbe78aa70307 | general | 7.9 | 2 | 2 | 0.000 | 18.53 | 0.42 | 18.06 | 0.05 | 18.30 |
| afrispeech_dialog__185152d7-0c16-45e5-8f1e-862e5766f39a | general | 14.8 | 2 | 2 | 0.000 | 32.72 | 7.33 | 16.72 | 8.67 | 36.79 |
| afrispeech_dialog__27f9dfd2-193a-46f1-8d2b-f87fb84b6b6a | general | 5.2 | 2 | 2 | 0.000 | 22.62 | 2.78 | 19.67 | 0.16 | 20.96 |
| afrispeech_dialog__304d6402-91d8-4a4f-8a65-143a7c7675d8 | medical | 3.5 | 2 | 1 | 0.000 | 78.67 | 0.00 | 61.36 | 17.31 | 86.72 |
| afrispeech_dialog__30a5b6a2-8370-4dac-bc7f-e4ae7c1d8562 | general | 19.9 | 2 | 2 | 0.000 | 13.00 | 2.39 | 9.22 | 1.38 | 13.73 |
| afrispeech_dialog__363c7601-e830-4db8-ae3b-ae88b9fb29e1 | general | 10.9 | 2 | 2 | 0.000 | 18.06 | 0.89 | 17.08 | 0.09 | 17.72 |
| afrispeech_dialog__392c7093-7347-40b8-ab37-db1dcc90945d | medical | 14.9 | 2 | 2 | 0.015 | 38.95 | 10.71 | 24.22 | 4.03 | 38.59 |
| afrispeech_dialog__3e27c06c-8ba1-4511-88e6-c75b2d9d8839 | general | 6.7 | 2 | 2 | 0.000 | 16.30 | 5.04 | 10.58 | 0.68 | 17.74 |
| afrispeech_dialog__49542e8d-b799-4d91-94e8-fd1571e51741 | general | 6.8 | 2 | 2 | 0.010 | 24.17 | 6.97 | 14.03 | 3.16 | 30.59 |
| afrispeech_dialog__4d398d1f-5058-4e5b-8070-23f42089f14e | general | 10.5 | 2 | 2 | 0.000 | 13.47 | 0.44 | 12.66 | 0.37 | 12.02 |
| afrispeech_dialog__4fc2c19e-de60-4be0-91b5-7870f60f2d99 | medical | 11.4 | 2 | 2 | 0.000 | 25.46 | 4.91 | 20.53 | 0.02 | 24.42 |
| afrispeech_dialog__5b8a8e4c-7463-47c4-858f-5cd8dd278d42 | medical | 3.3 | 2 | 2 | 0.000 | 41.07 | 19.29 | 14.29 | 7.49 | 43.11 |
| afrispeech_dialog__60344b07-b93e-4e14-8b1b-d544d9cd6a16 | general | 10.2 | 2 | 2 | 0.000 | 25.57 | 8.37 | 15.38 | 1.82 | 24.67 |
| afrispeech_dialog__63e6abb7-2d8e-4df3-a52e-8e09aea762c6 | medical | 4.9 | 2 | 2 | 0.000 | 43.45 | 1.08 | 29.74 | 12.62 | 55.34 |
| afrispeech_dialog__656c42a7-6faa-4486-979f-6f64769bd221 | medical | 3.4 | 2 | 2 | 0.000 | 29.59 | 1.03 | 15.52 | 13.04 | 37.37 |
| afrispeech_dialog__68f2adb6-06ab-46a6-9de6-395d89c2e1a3 | medical | 6.8 | 2 | 2 | 0.000 | 19.75 | 0.27 | 14.84 | 4.64 | 25.19 |
| afrispeech_dialog__7e832fef-ddde-4f8b-8687-eefcf95fe1ce | medical | 9.0 | 2 | 2 | 0.000 | 20.08 | 0.20 | 15.48 | 4.40 | 23.71 |
| afrispeech_dialog__818f0aa2-ce0f-4e82-96ee-d66e192a2fca | medical | 5.6 | 2 | 2 | 0.000 | 29.14 | 12.64 | 13.75 | 2.75 | 28.14 |
| afrispeech_dialog__83a0b048-c0e3-4929-9b29-278a873ab7c6 | general | 15.0 | 2 | 2 | 0.000 | 33.25 | 7.79 | 11.91 | 13.54 | 38.74 |
| afrispeech_dialog__94009039-0507-492f-8b26-e53d20642089 | medical | 5.5 | 2 | 2 | 0.000 | 47.61 | 20.01 | 20.87 | 6.72 | 45.42 |
| afrispeech_dialog__95aed576-a1d6-42f3-9651-7103e0717e5e | medical | 3.4 | 2 | 2 | 0.000 | 38.40 | 21.80 | 10.02 | 6.59 | 35.02 |
| afrispeech_dialog__98cc8263-54e8-4101-8942-7ae18f1e082b | general | 13.4 | 2 | 2 | 0.000 | 15.37 | 0.69 | 14.68 | 0.00 | 18.69 |
| afrispeech_dialog__9c267f6c-5a01-4174-bdd3-a53ff045f506 | general | 9.0 | 2 | 1 | 0.000 | 57.23 | 0.95 | 19.10 | 37.18 | 76.34 |
| afrispeech_dialog__9d838ece-8db5-4736-96d8-581071bd5106 | medical | 3.4 | 2 | 2 | 0.000 | 33.51 | 1.72 | 16.62 | 15.17 | 45.23 |
| afrispeech_dialog__ad6848ae-2614-4da8-b129-62b0d86e8926 | general | 8.7 | 2 | 2 | 0.000 | 28.88 | 0.85 | 21.62 | 6.42 | 40.01 |
| afrispeech_dialog__b5079ba2-df1c-448d-89f4-685241747496 | general | 14.8 | 2 | 2 | 0.000 | 26.06 | 3.60 | 15.32 | 7.14 | 43.58 |
| afrispeech_dialog__b945928d-8fd3-4b41-80ce-6c029486c454 | general | 15.4 | 2 | 2 | 0.000 | 17.95 | 6.72 | 8.84 | 2.39 | 18.69 |
| afrispeech_dialog__bb52e43b-e30c-4fb7-87d6-97ee79ce25ea | general | 13.4 | 2 | 2 | 0.000 | 16.64 | 0.93 | 15.71 | 0.00 | 18.87 |
| afrispeech_dialog__c1fd9c2e-cd94-46d4-83c1-7ad12c4720a2 | general | 13.7 | 2 | 2 | 0.000 | 16.84 | 0.12 | 16.39 | 0.32 | 16.83 |
| afrispeech_dialog__c46ac19c-edf5-4bc2-8162-110ff52ef78b | medical | 6.7 | 2 | 2 | 0.000 | 37.84 | 0.39 | 31.34 | 6.12 | 41.84 |
| afrispeech_dialog__c5d612f8-d493-4611-a5da-168ecbd3db35 | general | 15.6 | 2 | 2 | 0.006 | 14.47 | 2.19 | 11.07 | 1.22 | 15.77 |
| afrispeech_dialog__ca43d51b-8431-443a-bcd7-2742819032c8 | general | 7.1 | 2 | 2 | 0.000 | 16.64 | 1.28 | 15.27 | 0.09 | 20.11 |
| afrispeech_dialog__cd255fe0-ebc2-47a0-a990-2ab1ba9ca23d | medical | 3.4 | 2 | 2 | 0.000 | 36.00 | 14.64 | 12.50 | 8.86 | 46.18 |
| afrispeech_dialog__ce541c27-b35d-4b11-ba04-24d3abcb85d3 | general | 6.1 | 2 | 2 | 0.000 | 6.13 | 3.17 | 2.17 | 0.78 | 8.32 |
| afrispeech_dialog__d2f0bed6-f3e1-48a8-9fb2-ceb137670bc4 | medical | 5.8 | 2 | 2 | 0.000 | 24.56 | 9.11 | 14.19 | 1.26 | 23.56 |
| afrispeech_dialog__df50b219-f5aa-4d56-9f33-6865c96fda2b | general | 8.2 | 2 | 2 | 0.000 | 16.71 | 4.39 | 11.31 | 1.00 | 17.47 |
| afrispeech_dialog__e0b202dc-17fe-4936-a3c7-d89c639d9cda | general | 5.9 | 2 | 2 | 0.000 | 17.63 | 1.63 | 15.36 | 0.64 | 16.33 |
| afrispeech_dialog__ebcde1b4-bd3b-49b7-b777-e7d87a7cb7f3 | general | 10.4 | 2 | 2 | 0.000 | 24.79 | 6.45 | 14.90 | 3.43 | 28.31 |
| afrispeech_dialog__eceb9468-7001-4ee0-9475-13486e5352ae | medical | 3.8 | 2 | 2 | 0.000 | 32.66 | 9.71 | 22.13 | 0.82 | 31.09 |
| afrispeech_dialog__f01e751c-11e3-498b-a6ee-5d9bf11ac8cd | general | 8.4 | 2 | 3 | 0.000 | 56.88 | 14.34 | 2.74 | 39.80 | 66.91 |
| afrispeech_dialog__f1345c7a-87ca-4c7c-a22f-04dd30bdea30 | general | 8.8 | 2 | 2 | 0.000 | 19.90 | 0.20 | 17.98 | 1.72 | 29.87 |
| afrispeech_dialog__f533e2de-bac6-4866-8803-b33407813e92 | general | 6.4 | 2 | 2 | 0.009 | 26.41 | 10.70 | 14.47 | 1.24 | 26.32 |
| afrispeech_dialog__fd258274-0797-4cdd-b6ea-426ae9723bf7 | medical | 7.3 | 2 | 2 | 0.000 | 32.62 | 14.02 | 14.62 | 3.98 | 36.99 |
