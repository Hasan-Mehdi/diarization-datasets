# Nemotron 3 Diarization on icsi (view: sdm)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 3 (2.77 h); speaker-count accuracy 100.0%, MAE 0.00; RTFx None
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 15.84 | 11.06 | 3.77 | 1.00 | 16.10 | 2.55 |
| primary | 0.25 | 5.36 | 3.15 | 1.81 | 0.40 | 6.59 | 1.75 |
| words_gap0.2 | 0.0 | 38.20 | 36.33 | 1.14 | 0.74 | 33.67 | 2.02 |
| words_gap0.2 | 0.25 | 22.37 | 21.94 | 0.19 | 0.24 | 26.54 | 1.22 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| icsi__Bmr013 | test | 48.5 | 7 | 7 | 0.079 | 14.29 | 10.44 | 3.13 | 0.72 | 13.54 |
| icsi__Bmr018 | test | 57.0 | 7 | 7 | 0.168 | 17.99 | 13.64 | 3.04 | 1.31 | 21.06 |
| icsi__Bro021 | test | 60.5 | 7 | 7 | 0.071 | 14.55 | 8.54 | 5.14 | 0.87 | 13.68 |
