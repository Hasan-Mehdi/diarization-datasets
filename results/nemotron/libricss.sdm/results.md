# Nemotron 3 Diarization on libricss (view: sdm)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 54 (9.09 h); speaker-count accuracy 68.5%, MAE 0.37; RTFx 1131.8
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 14.30 | 0.58 | 8.21 | 5.52 | 20.33 | 9.37 |
| primary | 0.25 | 13.02 | 0.05 | 7.51 | 5.46 | 19.09 | 8.23 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| libricss__0L_session1 | eval | 10.0 | 8 | 6 | 0.000 | 22.63 | 0.41 | 8.11 | 14.11 | 42.85 |
| libricss__0L_session2 | eval | 10.1 | 8 | 8 | 0.000 | 10.75 | 0.27 | 9.14 | 1.35 | 13.16 |
| libricss__0L_session3 | eval | 10.1 | 8 | 6 | 0.000 | 24.18 | 0.81 | 4.52 | 18.86 | 36.60 |
| libricss__0L_session4 | eval | 10.3 | 8 | 7 | 0.000 | 26.25 | 0.58 | 6.95 | 18.72 | 33.00 |
| libricss__0L_session5 | eval | 10.2 | 8 | 7 | 0.000 | 20.80 | 0.58 | 8.45 | 11.77 | 28.67 |
| libricss__0L_session6 | eval | 10.1 | 8 | 8 | 0.000 | 11.61 | 0.49 | 5.92 | 5.21 | 14.57 |
| libricss__0L_session7 | eval | 10.0 | 8 | 7 | 0.000 | 17.56 | 0.59 | 6.41 | 10.56 | 28.32 |
| libricss__0L_session8 | eval | 10.1 | 8 | 8 | 0.000 | 24.32 | 0.60 | 11.08 | 12.64 | 33.23 |
| libricss__0L_session9 | eval | 10.1 | 8 | 6 | 0.000 | 28.53 | 0.43 | 8.64 | 19.46 | 42.69 |
| libricss__0S_session1 | eval | 10.2 | 8 | 8 | 0.000 | 10.68 | 0.55 | 8.75 | 1.38 | 13.21 |
| libricss__0S_session2 | eval | 10.1 | 8 | 8 | 0.000 | 8.20 | 0.44 | 7.52 | 0.25 | 9.37 |
| libricss__0S_session3 | eval | 10.1 | 8 | 7 | 0.000 | 25.64 | 0.63 | 10.33 | 14.69 | 33.15 |
| libricss__0S_session4 | eval | 10.0 | 8 | 7 | 0.000 | 15.95 | 0.74 | 11.91 | 3.30 | 24.70 |
| libricss__0S_session5 | eval | 10.1 | 8 | 8 | 0.000 | 13.54 | 0.46 | 8.22 | 4.86 | 17.29 |
| libricss__0S_session6 | eval | 10.1 | 8 | 8 | 0.000 | 20.20 | 0.66 | 8.69 | 10.85 | 24.76 |
| libricss__0S_session7 | eval | 10.1 | 8 | 7 | 0.000 | 15.71 | 0.57 | 6.89 | 8.25 | 23.16 |
| libricss__0S_session8 | eval | 10.1 | 8 | 8 | 0.000 | 10.54 | 0.60 | 9.81 | 0.13 | 11.72 |
| libricss__0S_session9 | eval | 10.0 | 8 | 7 | 0.000 | 22.16 | 0.75 | 6.74 | 14.67 | 33.89 |
| libricss__OV10_session1 | eval | 10.0 | 8 | 8 | 0.054 | 9.35 | 0.50 | 8.31 | 0.54 | 9.65 |
| libricss__OV10_session2 | eval | 10.1 | 8 | 8 | 0.053 | 7.32 | 0.50 | 6.81 | 0.02 | 7.05 |
| libricss__OV10_session3 | eval | 10.0 | 8 | 8 | 0.053 | 7.67 | 0.64 | 6.50 | 0.53 | 8.50 |
| libricss__OV10_session4 | eval | 10.2 | 8 | 7 | 0.052 | 22.94 | 0.62 | 9.24 | 13.08 | 40.36 |
| libricss__OV10_session5 | eval | 10.2 | 8 | 8 | 0.052 | 10.29 | 0.67 | 9.01 | 0.60 | 10.76 |
| libricss__OV10_session6 | eval | 10.2 | 8 | 8 | 0.052 | 9.03 | 0.46 | 7.83 | 0.74 | 9.40 |
| libricss__OV10_session7 | eval | 10.1 | 8 | 8 | 0.053 | 7.42 | 0.67 | 5.10 | 1.65 | 10.14 |
| libricss__OV10_session8 | eval | 10.0 | 8 | 8 | 0.053 | 12.24 | 1.28 | 6.47 | 4.49 | 14.66 |
| libricss__OV10_session9 | eval | 10.1 | 8 | 8 | 0.053 | 7.01 | 0.40 | 5.45 | 1.16 | 8.25 |
| libricss__OV20_session1 | eval | 10.0 | 8 | 8 | 0.114 | 11.38 | 0.57 | 8.53 | 2.28 | 14.63 |
| libricss__OV20_session2 | eval | 10.0 | 8 | 8 | 0.118 | 7.48 | 0.48 | 6.63 | 0.37 | 8.89 |
| libricss__OV20_session3 | eval | 10.0 | 8 | 7 | 0.111 | 16.59 | 0.77 | 7.61 | 8.21 | 26.39 |
| libricss__OV20_session4 | eval | 10.1 | 8 | 8 | 0.111 | 18.37 | 0.46 | 8.94 | 8.97 | 26.90 |
| libricss__OV20_session5 | eval | 10.0 | 8 | 7 | 0.109 | 17.34 | 0.50 | 7.67 | 9.17 | 29.60 |
| libricss__OV20_session6 | eval | 10.0 | 8 | 7 | 0.111 | 12.05 | 0.70 | 8.24 | 3.11 | 22.30 |
| libricss__OV20_session7 | eval | 10.1 | 8 | 8 | 0.112 | 17.36 | 0.53 | 12.52 | 4.30 | 21.65 |
| libricss__OV20_session8 | eval | 10.2 | 8 | 8 | 0.110 | 8.84 | 0.39 | 8.42 | 0.02 | 9.61 |
| libricss__OV20_session9 | eval | 10.2 | 8 | 8 | 0.116 | 11.60 | 0.45 | 8.61 | 2.53 | 20.38 |
| libricss__OV30_session1 | eval | 10.1 | 8 | 7 | 0.178 | 15.61 | 0.62 | 6.90 | 8.09 | 27.88 |
| libricss__OV30_session2 | eval | 10.3 | 8 | 8 | 0.171 | 17.26 | 0.56 | 8.34 | 8.36 | 23.07 |
| libricss__OV30_session3 | eval | 10.1 | 8 | 8 | 0.177 | 8.72 | 0.69 | 5.81 | 2.22 | 11.77 |
| libricss__OV30_session4 | eval | 10.1 | 8 | 8 | 0.174 | 10.50 | 0.74 | 6.53 | 3.24 | 14.45 |
| libricss__OV30_session5 | eval | 10.1 | 8 | 8 | 0.173 | 11.67 | 0.39 | 9.45 | 1.84 | 13.01 |
| libricss__OV30_session6 | eval | 10.1 | 8 | 7 | 0.176 | 31.13 | 0.69 | 12.36 | 18.07 | 40.76 |
| libricss__OV30_session7 | eval | 10.0 | 8 | 8 | 0.178 | 13.49 | 0.61 | 9.01 | 3.87 | 17.02 |
| libricss__OV30_session8 | eval | 10.3 | 8 | 8 | 0.174 | 8.01 | 0.63 | 7.33 | 0.05 | 7.60 |
| libricss__OV30_session9 | eval | 10.0 | 8 | 8 | 0.175 | 18.52 | 0.48 | 7.45 | 10.59 | 24.61 |
| libricss__OV40_session1 | eval | 10.1 | 8 | 8 | 0.246 | 14.59 | 0.58 | 8.76 | 5.25 | 22.67 |
| libricss__OV40_session2 | eval | 10.1 | 8 | 7 | 0.258 | 20.49 | 0.52 | 10.08 | 9.89 | 31.70 |
| libricss__OV40_session3 | eval | 10.1 | 8 | 8 | 0.248 | 11.15 | 0.44 | 9.33 | 1.38 | 12.78 |
| libricss__OV40_session4 | eval | 10.1 | 8 | 8 | 0.240 | 12.89 | 0.49 | 10.11 | 2.28 | 14.57 |
| libricss__OV40_session5 | eval | 10.1 | 8 | 8 | 0.263 | 15.13 | 0.59 | 11.18 | 3.36 | 22.24 |
| libricss__OV40_session6 | eval | 10.1 | 8 | 8 | 0.245 | 12.12 | 0.40 | 9.20 | 2.52 | 14.84 |
| libricss__OV40_session7 | eval | 10.0 | 8 | 8 | 0.253 | 6.80 | 0.72 | 6.04 | 0.04 | 7.85 |
| libricss__OV40_session8 | eval | 10.1 | 8 | 8 | 0.253 | 7.99 | 0.51 | 6.82 | 0.66 | 8.26 |
| libricss__OV40_session9 | eval | 10.1 | 8 | 8 | 0.246 | 13.93 | 0.77 | 6.47 | 6.68 | 19.12 |
