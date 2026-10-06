# Nemotron 3 Diarization on icsi (view: ihm-mix)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 3 (2.77 h); speaker-count accuracy 100.0%, MAE 0.00; RTFx None
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 15.84 | 12.20 | 2.89 | 0.76 | 16.36 | 2.55 |
| primary | 0.25 | 5.29 | 3.69 | 1.41 | 0.19 | 7.26 | 1.75 |
| words_gap0.2 | 0.0 | 39.42 | 38.37 | 0.64 | 0.41 | 33.14 | 2.02 |
| words_gap0.2 | 0.25 | 22.92 | 22.81 | 0.06 | 0.05 | 26.10 | 1.22 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| icsi__Bmr013 | test | 48.5 | 7 | 7 | 0.079 | 13.29 | 10.48 | 2.32 | 0.49 | 12.49 |
| icsi__Bmr018 | test | 57.0 | 7 | 7 | 0.168 | 19.49 | 15.74 | 2.60 | 1.15 | 23.92 |
| icsi__Bro021 | test | 60.5 | 7 | 7 | 0.071 | 13.62 | 9.43 | 3.68 | 0.51 | 12.66 |
