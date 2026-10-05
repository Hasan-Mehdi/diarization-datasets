# Nemotron 3 Diarization on ami (view: ihm-mix)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 16 (9.06 h); speaker-count accuracy 87.5%, MAE 0.12; RTFx 1012.9
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 9.22 | 3.66 | 4.68 | 0.88 | 12.89 | 6.65 |
| primary | 0.25 | 3.56 | 1.35 | 1.73 | 0.48 | 7.20 | 3.79 |
| only_words | 0.0 | 25.96 | 1.17 | 24.05 | 0.74 | 28.24 | 8.53 |
| only_words | 0.25 | 24.07 | 0.50 | 23.16 | 0.41 | 26.53 | 6.56 |
| segments | 0.0 | 31.13 | 0.25 | 30.49 | 0.39 | 34.16 | 9.43 |
| segments | 0.25 | 25.74 | 0.19 | 25.25 | 0.29 | 28.89 | 6.90 |
| word_and_vocalsounds | 0.0 | 27.74 | 1.01 | 26.07 | 0.67 | 30.70 | 8.78 |
| word_and_vocalsounds | 0.25 | 24.82 | 0.37 | 24.12 | 0.33 | 27.82 | 6.57 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ami__EN2002a | test | 35.7 | 4 | 4 | 0.185 | 14.25 | 5.09 | 7.68 | 1.47 | 15.56 |
| ami__EN2002b | test | 29.8 | 4 | 4 | 0.166 | 12.49 | 5.32 | 6.03 | 1.14 | 13.47 |
| ami__EN2002c | test | 49.5 | 3 | 4 | 0.136 | 8.81 | 3.55 | 4.83 | 0.43 | 8.99 |
| ami__EN2002d | test | 36.8 | 4 | 4 | 0.186 | 14.83 | 4.66 | 8.37 | 1.79 | 17.02 |
| ami__ES2004a | test | 17.5 | 4 | 4 | 0.099 | 9.46 | 3.54 | 5.64 | 0.29 | 11.22 |
| ami__ES2004b | test | 39.1 | 4 | 5 | 0.070 | 6.47 | 2.88 | 3.22 | 0.37 | 6.74 |
| ami__ES2004c | test | 38.9 | 4 | 4 | 0.078 | 5.60 | 2.74 | 2.55 | 0.31 | 6.09 |
| ami__ES2004d | test | 37.0 | 4 | 4 | 0.110 | 7.93 | 4.02 | 3.42 | 0.49 | 9.43 |
| ami__IS1009a | test | 14.0 | 4 | 4 | 0.139 | 19.10 | 4.12 | 7.03 | 7.96 | 41.21 |
| ami__IS1009b | test | 34.2 | 4 | 4 | 0.091 | 6.53 | 2.69 | 3.00 | 0.83 | 7.23 |
| ami__IS1009c | test | 30.3 | 4 | 4 | 0.045 | 7.05 | 3.69 | 2.85 | 0.51 | 7.45 |
| ami__IS1009d | test | 32.4 | 4 | 4 | 0.100 | 10.50 | 3.48 | 6.05 | 0.97 | 15.04 |
| ami__TS3003a | test | 25.1 | 4 | 4 | 0.030 | 8.98 | 2.85 | 5.55 | 0.58 | 25.69 |
| ami__TS3003b | test | 36.8 | 4 | 4 | 0.033 | 5.64 | 3.18 | 2.38 | 0.08 | 5.43 |
| ami__TS3003c | test | 42.8 | 4 | 4 | 0.034 | 5.83 | 3.19 | 2.57 | 0.07 | 5.44 |
| ami__TS3003d | test | 43.6 | 4 | 4 | 0.080 | 8.42 | 3.19 | 4.76 | 0.47 | 9.26 |
