# Nemotron 3 Diarization on dipco (view: farfield)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 5 (2.6 h); speaker-count accuracy 40.0%, MAE 0.60; RTFx 803.5
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 36.16 | 3.61 | 30.49 | 2.06 | 39.06 | 3.17 |
| primary | 0.25 | 28.07 | 3.48 | 23.20 | 1.38 | 30.93 | 2.07 |
| closetalk_activity | 0.0 | 40.32 | 11.99 | 25.28 | 3.05 | 39.01 | 2.67 |
| closetalk_activity | 0.25 | 18.31 | 4.89 | 11.62 | 1.80 | 21.67 | 1.28 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dipco__S01 | eval | 47.4 | 4 | 5 | 0.176 | 34.52 | 4.71 | 27.96 | 1.86 | 39.72 |
| dipco__S03 | eval | 46.6 | 4 | 4 | 0.347 | 34.45 | 3.24 | 29.13 | 2.08 | 37.53 |
| dipco__S06 | eval | 20.1 | 4 | 5 | 0.283 | 39.51 | 3.06 | 34.23 | 2.22 | 39.68 |
| dipco__S07 | eval | 26.3 | 4 | 4 | 0.331 | 37.07 | 2.60 | 32.35 | 2.12 | 39.28 |
| dipco__S08 | eval | 15.8 | 4 | 5 | 0.223 | 40.60 | 4.81 | 33.57 | 2.23 | 39.07 |
