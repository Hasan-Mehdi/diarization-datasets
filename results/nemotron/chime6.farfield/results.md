# Nemotron 3 Diarization on chime6 (view: farfield)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 2 (5.21 h); speaker-count accuracy 0.0%, MAE 1.00; RTFx 515.0
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 37.63 | 8.27 | 21.29 | 8.07 | 39.40 | 4.43 |
| primary | 0.25 | 25.61 | 4.37 | 14.49 | 6.74 | 29.83 | 2.10 |
| annotation | 0.0 | 43.62 | 1.49 | 36.15 | 5.98 | 46.85 | 5.89 |
| annotation | 0.25 | 34.28 | 0.86 | 27.55 | 5.86 | 38.53 | 3.19 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| chime6__S01 | eval | 159.1 | 4 | 5 | 0.254 | 41.60 | 9.61 | 22.67 | 9.32 | 41.09 |
| chime6__S21 | eval | 153.3 | 4 | 5 | 0.196 | 33.03 | 6.71 | 19.69 | 6.63 | 37.71 |
