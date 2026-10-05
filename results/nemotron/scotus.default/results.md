# Nemotron 3 Diarization on scotus (view: default)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 12 (20.5 h); speaker-count accuracy 0.0%, MAE 3.50; RTFx 818.5
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 31.66 | 1.10 | 11.16 | 19.40 | 47.68 | 20.49 |
| primary | 0.25 | 30.25 | 0.50 | 10.39 | 19.35 | 46.17 | 19.86 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| scotus__2022_20-1199_25450 | term2022 | 115.3 | 11 | 8 | 0.000 | 32.66 | 1.38 | 11.74 | 19.54 | 46.55 |
| scotus__2022_21-1168_25458 | term2022 | 108.2 | 12 | 8 | 0.000 | 34.41 | 1.26 | 17.11 | 16.04 | 52.12 |
| scotus__2022_21-376_25455 | term2022 | 192.3 | 13 | 8 | 0.000 | 50.90 | 1.38 | 13.00 | 36.52 | 60.58 |
| scotus__2022_21-432_25444 | term2022 | 47.5 | 10 | 8 | 0.000 | 10.44 | 0.46 | 7.75 | 2.23 | 32.11 |
| scotus__2022_21-442_25445 | term2022 | 59.9 | 11 | 8 | 0.000 | 31.78 | 0.94 | 14.06 | 16.77 | 50.44 |
| scotus__2022_21-454_25446 | term2022 | 108.1 | 11 | 8 | 0.000 | 22.58 | 0.60 | 11.66 | 10.32 | 41.32 |
| scotus__2022_21-468_25447 | term2022 | 132.1 | 13 | 8 | 0.000 | 39.11 | 1.58 | 8.43 | 29.11 | 52.48 |
| scotus__2022_21-476_25462 | term2022 | 142.0 | 12 | 8 | 0.000 | 37.99 | 1.37 | 9.18 | 27.44 | 54.28 |
| scotus__2022_21-846_25453 | term2022 | 62.0 | 11 | 8 | 0.000 | 30.28 | 0.87 | 20.26 | 9.16 | 48.34 |
| scotus__2022_21-869_25448 | term2022 | 102.5 | 12 | 8 | 0.000 | 22.44 | 1.09 | 8.11 | 13.24 | 49.48 |
| scotus__2022_21-86_25451 | term2022 | 91.6 | 11 | 8 | 0.000 | 17.31 | 0.45 | 8.48 | 8.38 | 41.29 |
| scotus__2022_22O145_25368 | term2022 | 68.7 | 11 | 8 | 0.000 | 7.42 | 0.46 | 4.06 | 2.89 | 37.39 |
