# Nemotron 3 Diarization on ava_avd_en (view: default)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 29 (2.42 h); speaker-count accuracy 20.7%, MAE 2.69; RTFx 895.5
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 49.79 | 11.78 | 23.30 | 14.70 | 67.44 | 0.99 |
| primary | 0.25 | 33.98 | 2.58 | 17.57 | 13.84 | 59.88 | 0.57 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ava_avd_en__2XeFK-DTSZk_c_01 | val | 5.0 | 6 | 6 | 0.055 | 51.42 | 20.80 | 26.56 | 4.06 | 49.09 |
| ava_avd_en__2XeFK-DTSZk_c_02 | val | 5.0 | 3 | 3 | 0.000 | 65.57 | 19.62 | 26.04 | 19.91 | 60.35 |
| ava_avd_en__2XeFK-DTSZk_c_03 | val | 5.0 | 3 | 3 | 0.001 | 68.86 | 15.25 | 27.41 | 26.20 | 61.22 |
| ava_avd_en__55Ihr6uVIDA_c_01 | val | 5.0 | 9 | 3 | 0.085 | 67.73 | 13.55 | 20.27 | 33.91 | 82.84 |
| ava_avd_en__55Ihr6uVIDA_c_02 | val | 5.0 | 4 | 2 | 0.000 | 64.69 | 16.15 | 3.63 | 44.90 | 76.93 |
| ava_avd_en__55Ihr6uVIDA_c_03 | val | 5.0 | 8 | 4 | 0.003 | 78.99 | 12.25 | 40.28 | 26.46 | 80.95 |
| ava_avd_en__914yZXz-iRs_c_01 | val | 5.0 | 11 | 7 | 0.030 | 49.34 | 7.15 | 21.55 | 20.64 | 68.24 |
| ava_avd_en__914yZXz-iRs_c_02 | val | 5.0 | 14 | 6 | 0.024 | 76.36 | 16.18 | 27.05 | 33.12 | 74.19 |
| ava_avd_en__914yZXz-iRs_c_03 | val | 5.0 | 8 | 5 | 0.066 | 63.48 | 7.09 | 41.28 | 15.11 | 63.28 |
| ava_avd_en__BCiuXAuCKAU_c_01 | test | 5.0 | 8 | 4 | 0.133 | 48.38 | 3.44 | 36.18 | 8.76 | 72.43 |
| ava_avd_en__BCiuXAuCKAU_c_02 | test | 5.0 | 10 | 4 | 0.027 | 55.56 | 20.25 | 15.64 | 19.67 | 81.47 |
| ava_avd_en__BCiuXAuCKAU_c_03 | test | 5.0 | 8 | 4 | 0.215 | 50.88 | 2.23 | 38.63 | 10.02 | 70.00 |
| ava_avd_en__HKjR70GCRPE_c_01 | test | 5.0 | 5 | 3 | 0.009 | 29.41 | 15.71 | 12.25 | 1.45 | 61.82 |
| ava_avd_en__HKjR70GCRPE_c_02 | test | 5.0 | 7 | 6 | 0.001 | 47.89 | 16.27 | 15.94 | 15.68 | 66.69 |
| ava_avd_en__HKjR70GCRPE_c_03 | test | 5.0 | 7 | 6 | 0.012 | 36.70 | 15.03 | 9.68 | 11.99 | 48.01 |
| ava_avd_en__fD6VkIRlIRI_c_01 | val | 5.0 | 7 | 4 | 0.019 | 42.33 | 2.53 | 20.85 | 18.95 | 62.94 |
| ava_avd_en__fD6VkIRlIRI_c_02 | val | 5.0 | 6 | 4 | 0.014 | 48.92 | 7.41 | 38.42 | 3.09 | 61.30 |
| ava_avd_en__fD6VkIRlIRI_c_03 | val | 5.0 | 9 | 5 | 0.004 | 51.14 | 14.03 | 16.43 | 20.67 | 72.31 |
| ava_avd_en__kMy-6RtoOVU_c_01 | test | 5.0 | 7 | 4 | 0.026 | 31.61 | 8.14 | 18.95 | 4.53 | 64.60 |
| ava_avd_en__kMy-6RtoOVU_c_02 | test | 5.0 | 5 | 4 | 0.009 | 52.16 | 23.00 | 19.28 | 9.88 | 50.69 |
| ava_avd_en__kMy-6RtoOVU_c_03 | test | 5.0 | 6 | 6 | 0.000 | 57.21 | 16.94 | 15.23 | 25.04 | 46.56 |
| ava_avd_en__o4xQ-BEa3Ss_c_02 | val | 5.0 | 8 | 5 | 0.026 | 36.09 | 15.61 | 8.36 | 12.12 | 60.29 |
| ava_avd_en__o4xQ-BEa3Ss_c_03 | val | 5.0 | 4 | 2 | 0.001 | 30.78 | 17.37 | 8.23 | 5.18 | 63.30 |
| ava_avd_en__oD_wxyTHJ2I_c_01 | val | 5.0 | 15 | 6 | 0.049 | 66.19 | 7.54 | 32.67 | 25.97 | 83.27 |
| ava_avd_en__oD_wxyTHJ2I_c_02 | val | 5.0 | 5 | 5 | 0.018 | 17.86 | 4.61 | 11.93 | 1.32 | 42.34 |
| ava_avd_en__oD_wxyTHJ2I_c_03 | val | 5.0 | 6 | 5 | 0.043 | 46.10 | 4.45 | 33.00 | 8.65 | 70.17 |
| ava_avd_en__yMtGmGa8KZ0_c_01 | val | 5.0 | 4 | 2 | 0.000 | 34.86 | 11.16 | 22.37 | 1.33 | 63.05 |
| ava_avd_en__yMtGmGa8KZ0_c_02 | val | 5.0 | 3 | 3 | 0.000 | 19.45 | 8.64 | 9.26 | 1.55 | 22.83 |
| ava_avd_en__yMtGmGa8KZ0_c_03 | val | 5.0 | 6 | 3 | 0.233 | 71.72 | 9.68 | 41.81 | 20.23 | 86.46 |
