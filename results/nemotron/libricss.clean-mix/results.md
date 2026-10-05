# Nemotron 3 Diarization on libricss (view: clean-mix)

- model: `nvidia/Nemotron-3-Diarization` (revision f667ed73aee57d40cc39428eb768b4fd87a0a29e); transformers (offline mode), chunk 340 / right ctx 40 / fifo 40 / update 300 / spk cache 264, threshold 0.5
- sessions: 54 (9.08 h); speaker-count accuracy 100.0%, MAE 0.00; RTFx 1136.0
- scoring: pyannote.metrics, overlap included, UEM applied; collar = half-width in seconds

| reference | collar | DER % | FA % | Miss % | Conf % | JER % | scored ref speaker-time h |
|---|---:|---:|---:|---:|---:|---:|---:|
| primary | 0.0 | 5.09 | 0.14 | 4.51 | 0.44 | 5.83 | 9.37 |
| primary | 0.25 | 4.44 | 0.00 | 4.03 | 0.41 | 5.10 | 8.23 |

Per session (primary reference, collar 0):

| session | split | dur (min) | ref spk | hyp spk | overlap | DER % | FA % | Miss % | Conf % | JER % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| libricss__0L_session1 | eval | 10.0 | 8 | 8 | 0.000 | 6.89 | 0.02 | 3.53 | 3.34 | 13.00 |
| libricss__0L_session2 | eval | 10.1 | 8 | 8 | 0.000 | 6.34 | 0.01 | 6.33 | 0.00 | 6.38 |
| libricss__0L_session3 | eval | 10.1 | 8 | 8 | 0.000 | 3.14 | 0.03 | 3.11 | 0.00 | 3.18 |
| libricss__0L_session4 | eval | 10.3 | 8 | 8 | 0.000 | 9.85 | 0.02 | 3.66 | 6.18 | 14.59 |
| libricss__0L_session5 | eval | 10.2 | 8 | 8 | 0.000 | 4.90 | 0.02 | 4.58 | 0.30 | 5.42 |
| libricss__0L_session6 | eval | 10.1 | 8 | 8 | 0.000 | 5.06 | 0.04 | 4.77 | 0.25 | 5.17 |
| libricss__0L_session7 | eval | 10.0 | 8 | 8 | 0.000 | 2.67 | 0.03 | 2.57 | 0.07 | 3.05 |
| libricss__0L_session8 | eval | 10.0 | 8 | 8 | 0.000 | 6.25 | 0.03 | 2.40 | 3.82 | 8.86 |
| libricss__0L_session9 | eval | 10.1 | 8 | 8 | 0.000 | 4.79 | 0.01 | 4.78 | 0.00 | 4.44 |
| libricss__0S_session1 | eval | 10.1 | 8 | 8 | 0.000 | 3.82 | 0.09 | 3.73 | 0.01 | 3.97 |
| libricss__0S_session2 | eval | 10.1 | 8 | 8 | 0.000 | 2.99 | 0.11 | 2.88 | 0.00 | 2.90 |
| libricss__0S_session3 | eval | 10.1 | 8 | 8 | 0.000 | 3.46 | 0.13 | 3.00 | 0.33 | 3.63 |
| libricss__0S_session4 | eval | 10.0 | 8 | 8 | 0.000 | 5.34 | 0.14 | 5.20 | 0.00 | 5.22 |
| libricss__0S_session5 | eval | 10.1 | 8 | 8 | 0.000 | 4.77 | 0.08 | 4.68 | 0.00 | 4.99 |
| libricss__0S_session6 | eval | 10.1 | 8 | 8 | 0.000 | 3.08 | 0.23 | 2.85 | 0.00 | 2.94 |
| libricss__0S_session7 | eval | 10.0 | 8 | 8 | 0.000 | 4.10 | 0.12 | 3.97 | 0.01 | 5.35 |
| libricss__0S_session8 | eval | 10.0 | 8 | 8 | 0.000 | 5.67 | 0.18 | 5.49 | 0.00 | 4.66 |
| libricss__0S_session9 | eval | 10.0 | 8 | 8 | 0.000 | 3.05 | 0.23 | 2.82 | 0.00 | 2.96 |
| libricss__OV10_session1 | eval | 10.0 | 8 | 8 | 0.054 | 4.97 | 0.11 | 4.86 | 0.00 | 4.32 |
| libricss__OV10_session2 | eval | 10.1 | 8 | 8 | 0.053 | 4.73 | 0.16 | 4.57 | 0.00 | 4.40 |
| libricss__OV10_session3 | eval | 10.0 | 8 | 8 | 0.053 | 3.99 | 0.08 | 3.91 | 0.00 | 3.61 |
| libricss__OV10_session4 | eval | 10.2 | 8 | 8 | 0.052 | 7.87 | 0.24 | 7.63 | 0.01 | 7.29 |
| libricss__OV10_session5 | eval | 10.2 | 8 | 8 | 0.052 | 3.96 | 0.17 | 3.78 | 0.00 | 4.28 |
| libricss__OV10_session6 | eval | 10.2 | 8 | 8 | 0.052 | 7.29 | 0.10 | 5.83 | 1.35 | 10.09 |
| libricss__OV10_session7 | eval | 10.1 | 8 | 8 | 0.053 | 3.59 | 0.13 | 3.46 | 0.00 | 4.18 |
| libricss__OV10_session8 | eval | 10.0 | 8 | 8 | 0.053 | 4.22 | 0.13 | 4.08 | 0.00 | 4.42 |
| libricss__OV10_session9 | eval | 10.1 | 8 | 8 | 0.053 | 4.99 | 0.09 | 4.60 | 0.29 | 5.03 |
| libricss__OV20_session1 | eval | 10.0 | 8 | 8 | 0.114 | 5.61 | 0.14 | 4.54 | 0.93 | 7.96 |
| libricss__OV20_session2 | eval | 10.0 | 8 | 8 | 0.118 | 3.97 | 0.13 | 3.85 | 0.00 | 4.35 |
| libricss__OV20_session3 | eval | 10.0 | 8 | 8 | 0.111 | 3.67 | 0.12 | 2.94 | 0.61 | 4.40 |
| libricss__OV20_session4 | eval | 10.1 | 8 | 8 | 0.111 | 3.14 | 0.12 | 3.02 | 0.00 | 3.07 |
| libricss__OV20_session5 | eval | 10.0 | 8 | 8 | 0.109 | 3.48 | 0.14 | 3.34 | 0.00 | 3.05 |
| libricss__OV20_session6 | eval | 10.0 | 8 | 8 | 0.111 | 5.83 | 0.24 | 4.45 | 1.14 | 9.29 |
| libricss__OV20_session7 | eval | 10.1 | 8 | 8 | 0.112 | 4.88 | 0.12 | 4.57 | 0.19 | 5.00 |
| libricss__OV20_session8 | eval | 10.2 | 8 | 8 | 0.110 | 5.73 | 0.11 | 5.62 | 0.00 | 5.75 |
| libricss__OV20_session9 | eval | 10.2 | 8 | 8 | 0.116 | 3.41 | 0.13 | 3.12 | 0.15 | 3.91 |
| libricss__OV30_session1 | eval | 10.0 | 8 | 8 | 0.178 | 4.80 | 0.20 | 4.14 | 0.46 | 5.89 |
| libricss__OV30_session2 | eval | 10.3 | 8 | 8 | 0.171 | 4.89 | 0.20 | 4.36 | 0.33 | 5.24 |
| libricss__OV30_session3 | eval | 10.0 | 8 | 8 | 0.177 | 5.64 | 0.14 | 5.35 | 0.15 | 7.10 |
| libricss__OV30_session4 | eval | 10.1 | 8 | 8 | 0.174 | 6.71 | 0.23 | 4.96 | 1.52 | 8.39 |
| libricss__OV30_session5 | eval | 10.1 | 8 | 8 | 0.173 | 6.96 | 0.08 | 6.52 | 0.37 | 8.44 |
| libricss__OV30_session6 | eval | 10.1 | 8 | 8 | 0.176 | 4.38 | 0.17 | 4.20 | 0.00 | 4.18 |
| libricss__OV30_session7 | eval | 10.0 | 8 | 8 | 0.178 | 10.64 | 0.10 | 6.92 | 3.62 | 20.82 |
| libricss__OV30_session8 | eval | 10.3 | 8 | 8 | 0.174 | 4.57 | 0.17 | 4.40 | 0.01 | 4.35 |
| libricss__OV30_session9 | eval | 10.0 | 8 | 8 | 0.175 | 5.11 | 0.23 | 4.70 | 0.19 | 4.83 |
| libricss__OV40_session1 | eval | 10.1 | 8 | 8 | 0.246 | 5.56 | 0.24 | 5.32 | 0.00 | 5.40 |
| libricss__OV40_session2 | eval | 10.1 | 8 | 8 | 0.258 | 5.80 | 0.09 | 5.71 | 0.00 | 4.92 |
| libricss__OV40_session3 | eval | 10.0 | 8 | 8 | 0.248 | 5.71 | 0.17 | 5.53 | 0.00 | 5.38 |
| libricss__OV40_session4 | eval | 10.0 | 8 | 8 | 0.240 | 6.58 | 0.13 | 6.45 | 0.00 | 6.29 |
| libricss__OV40_session5 | eval | 10.1 | 8 | 8 | 0.263 | 6.08 | 0.13 | 4.90 | 1.05 | 7.93 |
| libricss__OV40_session6 | eval | 10.1 | 8 | 8 | 0.245 | 7.52 | 0.17 | 7.01 | 0.35 | 7.50 |
| libricss__OV40_session7 | eval | 10.0 | 8 | 8 | 0.253 | 4.65 | 0.19 | 4.28 | 0.18 | 6.17 |
| libricss__OV40_session8 | eval | 10.1 | 8 | 8 | 0.253 | 3.89 | 0.13 | 3.75 | 0.01 | 3.98 |
| libricss__OV40_session9 | eval | 10.0 | 8 | 8 | 0.246 | 3.52 | 0.14 | 3.38 | 0.00 | 3.08 |
