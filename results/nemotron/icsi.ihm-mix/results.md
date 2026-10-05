# Nemotron 3 Diarization on icsi (view: ihm-mix)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 3 (2.77 h); speaker-count accuracy 100.0%, MAE 0.00; RTFx 833.6
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | ref speech h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 15.86 | 12.22 | 2.89 | 0.76 | 16.36 | 2.55 |
| primary | 0.25 | 5.31 | 3.72 | 1.41 | 0.19 | 7.28 | 1.75 |
| words | 0.0 | 44.46 | 43.40 | 0.62 | 0.44 | 35.46 | 1.95 |
| words | 0.25 | 28.20 | 28.09 | 0.05 | 0.06 | 29.62 | 0.95 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| icsi__Bmr013 | test | 48.5 | 7 | 7 | 0.079 | 13.29 | 10.48 | 2.32 | 0.49 | 12.49 |
| icsi__Bmr018 | test | 57.0 | 7 | 7 | 0.168 | 19.53 | 15.78 | 2.60 | 1.15 | 23.95 |
| icsi__Bro021 | test | 60.5 | 7 | 7 | 0.071 | 13.62 | 9.43 | 3.68 | 0.51 | 12.66 |
