# Nemotron 3 Diarization on primock57 (view: mix)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 57 (8.64 h); speaker-count accuracy 84.2%, MAE 0.16; RTFx None
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 24.15 | 0.10 | 24.00 | 0.05 | 24.92 | 8.41 |
| primary | 0.25 | 15.99 | 0.07 | 15.88 | 0.04 | 15.97 | 7.01 |
| channel_activity | 0.0 | 10.38 | 1.12 | 9.15 | 0.11 | 10.55 | 6.96 |
| channel_activity | 0.25 | 4.08 | 0.04 | 4.01 | 0.03 | 3.78 | 4.68 |
| silero_channel | 0.0 | 9.85 | 1.74 | 7.99 | 0.12 | 10.08 | 6.83 |
| silero_channel | 0.25 | 2.55 | 0.60 | 1.92 | 0.03 | 2.53 | 4.91 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| primock57__day1_consultation01 | all | 7.6 | 2 | 2 | 0.143 | 26.99 | 0.04 | 26.93 | 0.02 | 27.22 |
| primock57__day1_consultation02 | all | 9.3 | 2 | 2 | 0.067 | 21.70 | 0.05 | 21.65 | 0.00 | 21.88 |
| primock57__day1_consultation03 | all | 9.1 | 2 | 2 | 0.044 | 19.65 | 0.07 | 19.58 | 0.00 | 19.81 |
| primock57__day1_consultation04 | all | 10.3 | 2 | 2 | 0.069 | 24.49 | 0.03 | 24.42 | 0.04 | 24.68 |
| primock57__day1_consultation05 | all | 9.6 | 2 | 2 | 0.044 | 19.99 | 0.03 | 19.96 | 0.00 | 20.10 |
| primock57__day1_consultation06 | all | 11.0 | 2 | 2 | 0.049 | 24.28 | 0.07 | 24.21 | 0.00 | 25.30 |
| primock57__day1_consultation07 | all | 14.3 | 2 | 2 | 0.136 | 25.95 | 0.03 | 25.92 | 0.00 | 25.88 |
| primock57__day1_consultation08 | all | 7.8 | 2 | 2 | 0.045 | 26.97 | 0.35 | 26.60 | 0.02 | 28.99 |
| primock57__day1_consultation09 | all | 8.9 | 2 | 2 | 0.091 | 26.29 | 0.76 | 25.49 | 0.05 | 26.81 |
| primock57__day1_consultation10 | all | 10.3 | 2 | 3 | 0.142 | 27.79 | 0.03 | 27.70 | 0.05 | 27.69 |
| primock57__day1_consultation11 | all | 13.4 | 2 | 2 | 0.077 | 24.37 | 0.00 | 24.37 | 0.00 | 24.50 |
| primock57__day1_consultation12 | all | 7.9 | 2 | 2 | 0.045 | 22.26 | 0.02 | 22.25 | 0.00 | 22.26 |
| primock57__day1_consultation13 | all | 10.4 | 2 | 2 | 0.071 | 23.63 | 0.11 | 23.53 | 0.00 | 23.76 |
| primock57__day1_consultation14 | all | 10.1 | 2 | 2 | 0.090 | 22.62 | 0.06 | 22.47 | 0.10 | 22.61 |
| primock57__day1_consultation15 | all | 8.2 | 2 | 2 | 0.071 | 29.74 | 0.12 | 29.60 | 0.01 | 31.13 |
| primock57__day2_consultation01 | all | 5.5 | 2 | 2 | 0.042 | 20.47 | 0.01 | 20.46 | 0.00 | 22.83 |
| primock57__day2_consultation02 | all | 9.0 | 2 | 2 | 0.096 | 28.45 | 0.12 | 28.30 | 0.03 | 30.91 |
| primock57__day2_consultation03 | all | 7.5 | 2 | 2 | 0.106 | 28.85 | 0.08 | 28.70 | 0.08 | 29.30 |
| primock57__day2_consultation04 | all | 9.6 | 2 | 2 | 0.054 | 24.64 | 0.06 | 24.58 | 0.00 | 28.08 |
| primock57__day2_consultation05 | all | 10.6 | 2 | 2 | 0.020 | 21.51 | 0.11 | 21.40 | 0.00 | 22.63 |
| primock57__day2_consultation06 | all | 10.0 | 2 | 3 | 0.058 | 20.56 | 0.00 | 20.54 | 0.02 | 21.79 |
| primock57__day2_consultation07 | all | 7.6 | 2 | 3 | 0.082 | 21.78 | 0.11 | 21.52 | 0.16 | 21.60 |
| primock57__day2_consultation08 | all | 10.6 | 2 | 2 | 0.037 | 21.20 | 0.04 | 21.12 | 0.03 | 21.21 |
| primock57__day2_consultation09 | all | 7.2 | 2 | 2 | 0.032 | 25.35 | 0.00 | 25.35 | 0.00 | 25.55 |
| primock57__day2_consultation10 | all | 9.7 | 2 | 2 | 0.035 | 23.06 | 0.13 | 22.87 | 0.06 | 23.34 |
| primock57__day3_consultation01 | all | 8.5 | 2 | 2 | 0.072 | 23.22 | 0.02 | 23.17 | 0.04 | 23.23 |
| primock57__day3_consultation02 | all | 7.4 | 2 | 2 | 0.060 | 24.31 | 0.01 | 24.30 | 0.00 | 24.96 |
| primock57__day3_consultation03 | all | 11.6 | 2 | 2 | 0.088 | 24.67 | 0.04 | 24.61 | 0.02 | 25.04 |
| primock57__day3_consultation04 | all | 7.2 | 2 | 2 | 0.052 | 21.90 | 0.00 | 21.90 | 0.00 | 23.46 |
| primock57__day3_consultation05 | all | 6.9 | 2 | 3 | 0.051 | 23.20 | 0.09 | 22.36 | 0.75 | 25.73 |
| primock57__day3_consultation06 | all | 3.8 | 2 | 2 | 0.043 | 19.18 | 0.12 | 19.05 | 0.02 | 20.05 |
| primock57__day3_consultation07 | all | 7.6 | 2 | 2 | 0.086 | 24.07 | 0.05 | 24.00 | 0.03 | 26.51 |
| primock57__day3_consultation08 | all | 5.7 | 2 | 2 | 0.069 | 22.22 | 0.06 | 22.08 | 0.07 | 22.74 |
| primock57__day3_consultation09 | all | 11.9 | 2 | 2 | 0.073 | 19.66 | 0.04 | 19.61 | 0.01 | 19.75 |
| primock57__day3_consultation10 | all | 9.3 | 2 | 2 | 0.045 | 24.30 | 0.06 | 24.24 | 0.00 | 28.10 |
| primock57__day4_consultation01 | all | 8.6 | 2 | 2 | 0.048 | 21.62 | 0.27 | 21.35 | 0.00 | 21.85 |
| primock57__day4_consultation02 | all | 8.4 | 2 | 2 | 0.050 | 28.52 | 0.00 | 28.52 | 0.00 | 29.35 |
| primock57__day4_consultation03 | all | 6.4 | 2 | 2 | 0.055 | 25.09 | 0.05 | 25.04 | 0.01 | 26.59 |
| primock57__day4_consultation04 | all | 6.6 | 2 | 2 | 0.043 | 21.59 | 0.09 | 21.44 | 0.06 | 21.68 |
| primock57__day4_consultation05 | all | 9.7 | 2 | 2 | 0.097 | 31.36 | 0.05 | 31.30 | 0.01 | 31.41 |
| primock57__day4_consultation06 | all | 10.1 | 2 | 3 | 0.045 | 18.03 | 0.12 | 17.79 | 0.12 | 18.17 |
| primock57__day4_consultation07 | all | 10.4 | 2 | 2 | 0.025 | 19.21 | 0.13 | 19.05 | 0.02 | 19.91 |
| primock57__day4_consultation08 | all | 12.0 | 2 | 3 | 0.045 | 25.96 | 0.11 | 25.78 | 0.07 | 27.26 |
| primock57__day4_consultation09 | all | 10.5 | 2 | 2 | 0.046 | 24.16 | 0.01 | 24.15 | 0.00 | 24.75 |
| primock57__day4_consultation10 | all | 12.4 | 2 | 2 | 0.036 | 23.51 | 0.22 | 23.29 | 0.00 | 23.98 |
| primock57__day5_consultation01 | all | 7.6 | 2 | 2 | 0.051 | 25.99 | 0.00 | 25.99 | 0.00 | 26.28 |
| primock57__day5_consultation02 | all | 7.4 | 2 | 2 | 0.049 | 27.27 | 0.00 | 27.27 | 0.00 | 30.87 |
| primock57__day5_consultation03 | all | 12.9 | 2 | 2 | 0.041 | 23.61 | 0.08 | 23.51 | 0.03 | 23.36 |
| primock57__day5_consultation04 | all | 9.1 | 2 | 2 | 0.072 | 30.97 | 0.96 | 29.75 | 0.26 | 31.27 |
| primock57__day5_consultation05 | all | 6.8 | 2 | 2 | 0.067 | 25.72 | 0.21 | 25.52 | 0.00 | 25.52 |
| primock57__day5_consultation06 | all | 10.2 | 2 | 2 | 0.056 | 23.68 | 0.12 | 23.54 | 0.02 | 23.76 |
| primock57__day5_consultation07 | all | 8.2 | 2 | 2 | 0.048 | 23.91 | 0.00 | 23.91 | 0.00 | 24.65 |
| primock57__day5_consultation08 | all | 9.4 | 2 | 2 | 0.036 | 25.11 | 0.11 | 24.93 | 0.07 | 26.11 |
| primock57__day5_consultation09 | all | 9.7 | 2 | 3 | 0.052 | 29.20 | 0.09 | 28.90 | 0.21 | 29.02 |
| primock57__day5_consultation10 | all | 9.8 | 2 | 3 | 0.044 | 24.74 | 0.01 | 24.47 | 0.27 | 24.86 |
| primock57__day5_consultation11 | all | 11.1 | 2 | 3 | 0.057 | 19.91 | 0.02 | 19.62 | 0.27 | 20.29 |
| primock57__day5_consultation12 | all | 5.4 | 2 | 2 | 0.056 | 28.57 | 0.00 | 28.56 | 0.01 | 30.19 |
