# Nemotron 3 Diarization on easycom (view: glasses)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 12 (5.3 h); speaker-count accuracy 25.0%, MAE 0.83; RTFx 1126.4
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 30.38 | 4.10 | 19.61 | 6.67 | 33.75 | 4.90 |
| primary | 0.25 | 21.68 | 0.57 | 14.59 | 6.52 | 26.07 | 3.28 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| easycom__Session_1 | all | 23.1 | 4 | 5 | 0.158 | 24.79 | 4.94 | 16.40 | 3.45 | 29.39 |
| easycom__Session_10 | all | 24.0 | 4 | 5 | 0.153 | 24.06 | 4.29 | 15.29 | 4.49 | 28.37 |
| easycom__Session_11 | all | 22.8 | 5 | 6 | 0.216 | 35.24 | 4.77 | 26.77 | 3.69 | 35.30 |
| easycom__Session_12 | all | 29.6 | 4 | 6 | 0.304 | 27.92 | 2.82 | 22.17 | 2.93 | 29.91 |
| easycom__Session_2 | all | 25.7 | 5 | 5 | 0.185 | 26.81 | 3.18 | 22.55 | 1.08 | 26.13 |
| easycom__Session_3 | all | 28.0 | 4 | 5 | 0.168 | 33.08 | 3.98 | 15.84 | 13.26 | 28.91 |
| easycom__Session_4 | all | 28.9 | 6 | 6 | 0.212 | 35.24 | 4.28 | 23.48 | 7.48 | 40.15 |
| easycom__Session_5 | all | 28.5 | 4 | 5 | 0.118 | 28.51 | 2.99 | 19.37 | 6.15 | 37.65 |
| easycom__Session_6 | all | 29.4 | 4 | 5 | 0.168 | 34.95 | 5.03 | 12.37 | 17.55 | 48.67 |
| easycom__Session_7 | all | 24.2 | 4 | 4 | 0.105 | 26.64 | 6.37 | 14.84 | 5.43 | 31.72 |
| easycom__Session_8 | all | 25.5 | 4 | 5 | 0.126 | 25.20 | 3.56 | 19.72 | 1.91 | 24.22 |
| easycom__Session_9 | all | 28.4 | 4 | 5 | 0.084 | 40.62 | 3.66 | 26.24 | 10.72 | 42.95 |
