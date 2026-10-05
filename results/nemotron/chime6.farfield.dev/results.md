# Nemotron 3 Diarization on chime6 (view: farfield)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 2 (4.46 h); speaker-count accuracy 0.0%, MAE 1.50; RTFx 939.3
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 31.70 | 8.52 | 18.71 | 4.48 | 32.60 | 4.55 |
| primary | 0.25 | 19.06 | 5.36 | 10.57 | 3.13 | 20.92 | 2.07 |
| annotation | 0.0 | 41.65 | 1.13 | 38.13 | 2.38 | 42.53 | 6.49 |
| annotation | 0.25 | 35.09 | 1.26 | 31.69 | 2.15 | 35.67 | 3.91 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| chime6__S02 | dev | 148.4 | 4 | 6 | 0.300 | 29.80 | 7.90 | 18.74 | 3.16 | 30.12 |
| chime6__S09 | dev | 119.4 | 4 | 5 | 0.265 | 34.65 | 9.48 | 18.66 | 6.51 | 35.08 |
