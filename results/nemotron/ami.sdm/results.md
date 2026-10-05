# Nemotron 3 Diarization on ami (view: sdm)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 16 (9.06 h); speaker-count accuracy 87.5%, MAE 0.12; RTFx 943.5
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 11.35 | 4.12 | 5.86 | 1.38 | 15.03 | 6.65 |
| primary | 0.25 | 4.73 | 1.82 | 2.18 | 0.73 | 8.25 | 3.79 |
| only_words | 0.0 | 27.45 | 1.47 | 24.91 | 1.07 | 29.52 | 8.53 |
| only_words | 0.25 | 25.13 | 0.78 | 23.73 | 0.61 | 27.14 | 6.56 |
| segments | 0.0 | 32.52 | 0.50 | 31.25 | 0.77 | 35.38 | 9.43 |
| segments | 0.25 | 26.98 | 0.46 | 25.95 | 0.56 | 29.77 | 6.90 |
| word_and_vocalsounds | 0.0 | 29.22 | 1.28 | 26.89 | 1.04 | 32.03 | 8.78 |
| word_and_vocalsounds | 0.25 | 25.92 | 0.65 | 24.69 | 0.58 | 28.53 | 6.57 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ami__EN2002a | test | 35.7 | 4 | 4 | 0.185 | 16.08 | 5.36 | 9.16 | 1.56 | 17.43 |
| ami__EN2002b | test | 29.8 | 4 | 4 | 0.166 | 15.10 | 6.52 | 7.19 | 1.39 | 16.15 |
| ami__EN2002c | test | 49.5 | 3 | 4 | 0.136 | 12.40 | 4.77 | 6.21 | 1.42 | 12.19 |
| ami__EN2002d | test | 36.8 | 4 | 4 | 0.186 | 16.52 | 4.96 | 9.66 | 1.90 | 19.14 |
| ami__ES2004a | test | 17.5 | 4 | 4 | 0.099 | 17.70 | 5.11 | 10.93 | 1.65 | 25.34 |
| ami__ES2004b | test | 39.1 | 4 | 5 | 0.070 | 9.09 | 3.43 | 4.56 | 1.10 | 10.08 |
| ami__ES2004c | test | 38.9 | 4 | 4 | 0.078 | 6.57 | 3.06 | 3.08 | 0.43 | 7.14 |
| ami__ES2004d | test | 37.0 | 4 | 4 | 0.110 | 9.65 | 4.26 | 4.16 | 1.23 | 12.41 |
| ami__IS1009a | test | 14.0 | 4 | 4 | 0.139 | 13.02 | 5.04 | 6.21 | 1.76 | 19.06 |
| ami__IS1009b | test | 34.2 | 4 | 4 | 0.091 | 7.39 | 3.09 | 3.21 | 1.09 | 8.20 |
| ami__IS1009c | test | 30.3 | 4 | 4 | 0.045 | 7.85 | 3.88 | 3.00 | 0.97 | 8.42 |
| ami__IS1009d | test | 32.4 | 4 | 4 | 0.100 | 15.99 | 3.79 | 6.92 | 5.28 | 29.21 |
| ami__TS3003a | test | 25.1 | 4 | 4 | 0.030 | 12.40 | 3.36 | 8.07 | 0.96 | 29.50 |
| ami__TS3003b | test | 36.8 | 4 | 4 | 0.033 | 7.09 | 3.14 | 3.53 | 0.42 | 7.49 |
| ami__TS3003c | test | 42.8 | 4 | 4 | 0.034 | 7.20 | 3.13 | 3.78 | 0.29 | 6.86 |
| ami__TS3003d | test | 43.6 | 4 | 4 | 0.080 | 10.46 | 3.05 | 6.78 | 0.63 | 11.11 |
