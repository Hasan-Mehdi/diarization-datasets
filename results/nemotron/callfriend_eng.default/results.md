# Nemotron 3 Diarization on callfriend_eng (view: default)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 40 (10.44 h); speaker-count accuracy 75.0%, MAE 0.28; RTFx 1080.2
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 30.80 | 7.90 | 18.58 | 4.32 | 38.29 | 10.04 |
| primary | 0.25 | 23.24 | 3.84 | 16.19 | 3.21 | 31.00 | 7.02 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| callfriend_eng__eng-n_000 | data | 0.1 | 2 | 2 | 0.012 | 37.83 | 8.04 | 28.95 | 0.84 | 35.37 |
| callfriend_eng__eng-n_001 | data | 5.1 | 2 | 2 | 0.056 | 33.45 | 2.67 | 29.07 | 1.71 | 33.56 |
| callfriend_eng__eng-n_002 | data | 20.0 | 2 | 2 | 0.048 | 45.19 | 28.64 | 14.90 | 1.66 | 35.91 |
| callfriend_eng__eng-n_003 | data | 8.2 | 2 | 2 | 0.000 | 34.69 | 2.47 | 29.31 | 2.92 | 35.55 |
| callfriend_eng__eng-n_004 | data | 30.0 | 2 | 3 | 0.048 | 28.45 | 10.92 | 15.85 | 1.68 | 27.18 |
| callfriend_eng__eng-n_005 | data | 30.0 | 2 | 2 | 0.085 | 24.60 | 8.80 | 12.67 | 3.13 | 24.78 |
| callfriend_eng__eng-n_006 | data | 30.0 | 2 | 2 | 0.138 | 25.83 | 9.55 | 14.72 | 1.56 | 24.55 |
| callfriend_eng__eng-n_007 | data | 5.0 | 2 | 2 | 0.002 | 26.60 | 8.33 | 10.65 | 7.63 | 29.51 |
| callfriend_eng__eng-n_008 | data | 2.7 | 2 | 2 | 0.083 | 27.59 | 8.65 | 17.12 | 1.82 | 26.63 |
| callfriend_eng__eng-n_009 | data | 8.7 | 2 | 2 | 0.089 | 23.14 | 7.58 | 13.01 | 2.56 | 23.56 |
| callfriend_eng__eng-n_010 | data | 25.3 | 3 | 3 | 0.123 | 22.77 | 10.96 | 8.94 | 2.86 | 41.38 |
| callfriend_eng__eng-n_011 | data | 4.8 | 3 | 2 | 0.037 | 44.52 | 12.81 | 10.79 | 20.93 | 61.64 |
| callfriend_eng__eng-n_012 | data | 29.9 | 2 | 2 | 0.034 | 25.43 | 7.98 | 16.03 | 1.42 | 25.61 |
| callfriend_eng__eng-n_013 | data | 5.2 | 3 | 2 | 0.000 | 34.34 | 2.97 | 28.83 | 2.54 | 57.31 |
| callfriend_eng__eng-n_014 | data | 18.0 | 2 | 2 | 0.104 | 29.72 | 9.56 | 18.08 | 2.08 | 28.95 |
| callfriend_eng__eng-n_015 | data | 3.2 | 2 | 2 | 0.000 | 27.42 | 13.06 | 8.74 | 5.62 | 27.90 |
| callfriend_eng__eng-n_016 | data | 7.8 | 3 | 4 | 0.050 | 34.59 | 4.06 | 27.92 | 2.62 | 34.84 |
| callfriend_eng__eng-n_017 | data | 5.0 | 2 | 2 | 0.038 | 23.58 | 3.03 | 18.61 | 1.94 | 29.97 |
| callfriend_eng__eng-n_018 | data | 5.1 | 2 | 2 | 0.002 | 44.21 | 5.36 | 35.76 | 3.09 | 44.66 |
| callfriend_eng__eng-n_019 | data | 30.0 | 2 | 2 | 0.044 | 29.09 | 5.11 | 21.52 | 2.46 | 29.55 |
| callfriend_eng__eng-n_020 | data | 30.0 | 2 | 2 | 0.142 | 25.05 | 4.71 | 18.23 | 2.12 | 26.61 |
| callfriend_eng__eng-n_021 | data | 5.0 | 2 | 2 | 0.001 | 29.63 | 5.91 | 19.34 | 4.39 | 31.89 |
| callfriend_eng__eng-n_022 | data | 10.1 | 2 | 2 | 0.083 | 32.60 | 8.56 | 22.67 | 1.37 | 32.64 |
| callfriend_eng__eng-n_023 | data | 30.0 | 2 | 2 | 0.100 | 21.99 | 5.86 | 14.49 | 1.64 | 22.03 |
| callfriend_eng__eng-n_024 | data | 30.0 | 2 | 3 | 0.047 | 27.48 | 8.27 | 16.48 | 2.72 | 27.23 |
| callfriend_eng__eng-n_025 | data | 5.5 | 2 | 2 | 0.000 | 39.03 | 14.81 | 15.83 | 8.38 | 38.39 |
| callfriend_eng__eng-n_026 | data | 29.9 | 4 | 4 | 0.069 | 23.60 | 9.57 | 11.57 | 2.45 | 25.88 |
| callfriend_eng__eng-n_027 | data | 5.5 | 2 | 2 | 0.013 | 29.28 | 9.65 | 15.35 | 4.28 | 39.24 |
| callfriend_eng__eng-n_028 | data | 3.9 | 2 | 2 | 0.059 | 24.02 | 12.53 | 9.39 | 2.10 | 23.43 |
| callfriend_eng__eng-n_029 | data | 2.8 | 2 | 2 | 0.014 | 32.30 | 2.79 | 27.94 | 1.57 | 33.40 |
| callfriend_eng__eng-n_030 | data | 30.0 | 4 | 3 | 0.123 | 22.68 | 6.26 | 14.99 | 1.43 | 46.49 |
| callfriend_eng__eng-s_000 | data | 5.6 | 3 | 3 | 0.000 | 34.26 | 3.36 | 28.08 | 2.83 | 37.54 |
| callfriend_eng__eng-s_001 | data | 9.8 | 2 | 2 | 0.048 | 37.55 | 25.75 | 10.17 | 1.62 | 30.69 |
| callfriend_eng__eng-s_002 | data | 27.1 | 3 | 2 | 0.105 | 24.05 | 8.60 | 12.86 | 2.59 | 50.14 |
| callfriend_eng__eng-s_003 | data | 16.9 | 4 | 2 | 0.040 | 49.27 | 2.48 | 39.95 | 6.84 | 74.33 |
| callfriend_eng__eng-s_004 | data | 30.0 | 2 | 3 | 0.033 | 36.87 | 2.69 | 32.05 | 2.13 | 36.76 |
| callfriend_eng__eng-s_005 | data | 15.3 | 3 | 2 | 0.045 | 37.75 | 2.68 | 31.56 | 3.51 | 59.07 |
| callfriend_eng__eng-s_006 | data | 30.0 | 2 | 2 | 0.055 | 27.11 | 4.22 | 19.78 | 3.11 | 28.16 |
| callfriend_eng__eng-s_007 | data | 30.0 | 2 | 2 | 0.075 | 61.38 | 9.25 | 18.07 | 34.05 | 68.07 |
| callfriend_eng__eng-s_008 | data | 5.0 | 2 | 2 | 0.082 | 49.64 | 2.71 | 44.74 | 2.18 | 52.51 |
