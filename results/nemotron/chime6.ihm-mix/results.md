# Nemotron 3 Diarization on chime6 (view: ihm-mix)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 2 (5.21 h); speaker-count accuracy 50.0%, MAE 0.50; RTFx 835.1
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 32.76 | 10.12 | 16.60 | 6.05 | 33.78 | 4.43 |
| primary | 0.25 | 22.49 | 5.41 | 11.36 | 5.72 | 25.87 | 2.10 |
| annotation | 0.0 | 37.81 | 1.90 | 31.65 | 4.25 | 40.11 | 5.89 |
| annotation | 0.25 | 29.04 | 1.10 | 23.39 | 4.54 | 32.11 | 3.19 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| chime6__S01 | eval | 159.1 | 4 | 4 | 0.254 | 33.52 | 11.52 | 18.70 | 3.29 | 33.40 |
| chime6__S21 | eval | 153.3 | 4 | 5 | 0.196 | 31.89 | 8.50 | 14.15 | 9.24 | 34.16 |
