# Nemotron 3 Diarization on dipco (view: ihm-mix)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 5 (2.6 h); speaker-count accuracy 100.0%, MAE 0.00; RTFx 970.6
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 27.31 | 1.47 | 25.08 | 0.76 | 29.70 | 3.17 |
| primary | 0.25 | 19.43 | 1.40 | 17.51 | 0.51 | 21.91 | 2.07 |
| closetalk_activity | 0.0 | 31.50 | 10.55 | 19.97 | 0.98 | 31.41 | 2.67 |
| closetalk_activity | 0.25 | 17.23 | 1.92 | 14.91 | 0.40 | 19.96 | 1.28 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dipco__S01 | eval | 47.4 | 4 | 4 | 0.176 | 22.93 | 2.15 | 20.15 | 0.63 | 26.07 |
| dipco__S03 | eval | 46.6 | 4 | 4 | 0.347 | 27.27 | 1.72 | 24.60 | 0.95 | 30.38 |
| dipco__S06 | eval | 20.1 | 4 | 4 | 0.283 | 28.42 | 0.79 | 26.91 | 0.72 | 29.64 |
| dipco__S07 | eval | 26.2 | 4 | 4 | 0.331 | 31.44 | 0.72 | 29.98 | 0.75 | 33.52 |
| dipco__S08 | eval | 15.8 | 4 | 4 | 0.223 | 29.88 | 1.12 | 28.23 | 0.52 | 28.92 |
