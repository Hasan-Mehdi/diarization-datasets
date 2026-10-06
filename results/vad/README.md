# Silero VAD study: results

Produced by the code on branch `vad-study`; write-up and verdict: [docs/silero_vad_study.md](../../docs/silero_vad_study.md). Exact commands:

```bash
# env: D:\diarization-data\envs\diar (+ silero-vad 6.2.3 installed with --no-deps); pyannote in envs\vad
WORKERS=8 bash scripts/vad_compute_all.sh                       # Silero / WebRTC / energy VAD cache (CPU)
<envs/vad python> scripts/vad_pyannote.py                       # pyannote segmentation-3.0 baseline (GPU, ~6 min)
for d in <every dataset>; do python -m diards.vad_audit $d; done   # coverage, boundaries, lag, evidence
for d in <every dataset>; do python scripts/vad_whisper_check.py $d; done   # Whisper check of flagged regions
JOBS=6 bash scripts/vad_pipeline_all.sh                         # post-hoc VAD-assisted Nemotron variants (CPU)
for t in <tags>; do python -m diards.vad_assist rerun $t --max-hours 1.0; done   # trim / zero re-inference (GPU)
python scripts/vad_primock57_channels.py --whisper              # PriMock57 per-channel analysis
python scripts/vad_dataprep.py                                  # trimming potential, VAD-derived UEMs
python scripts/vad_report.py                                    # this README + summary.json
```

Conventions: reference speech = union of the RTTM segments inside the UEM; percentages are of reference speech time. *unannotated* = VAD speech >= 0.5 s long and > 0.25 s away from any reference speech; *silent-ref* = reference speech >= 0.5 s long and > 0.25 s away from any VAD speech; FA / miss = frame-level disagreement at collar 0. Boundary offsets: positive = the reference is wider than the VAD (starts earlier / ends later). Silero = `silero-vad` 6.2.3 defaults (threshold 0.5, min speech 250 ms, min silence 100 ms, pad 30 ms) applied to the frame-wise maximum of two runs (stock streaming, and state reset every 30 s): *Silero x2*. *stock* = the plain streaming run.

## 1. Ground-truth audit (primary reference, Silero x2)

| dataset | view | GT | sessions | ref speech h | Silero speech h | FA % | miss % | unannotated % | silent-ref % | onset p50 s | offset p50 s | time-shifted sessions |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog | default | D | 46 | 6.16 | 5.60 | 4.8 | 13.9 | 2.59 | 2.63 | 0.089 | -0.526 | 7 |
| ami | ihm-mix | A- | 170 | 66.42 | 72.20 | 10.8 | 2.1 | 1.29 | 0.36 | 0.002 | -0.120 | 0 |
| ava_avd_en | default | B | 96 | 3.24 | 2.94 | 12.6 | 21.6 | 1.40 | 14.83 | 0.020 | -0.130 | 0 |
| callfriend_eng | default | C- | 40 | 9.38 | 8.47 | 5.8 | 15.5 | 1.65 | 4.00 | 0.157 | -0.222 | 0 |
| callhome_eng | default | C | 140 | 17.53 | 17.27 | 4.0 | 5.4 | 0.46 | 0.71 | 0.000 | -0.096 | 0 |
| chime6 | ihm-mix | A- | 4 | 6.85 | 6.83 | 8.5 | 8.8 | 1.13 | 4.00 | 0.016 | -0.116 | 0 |
| dipco | ihm-mix | B | 10 | 4.87 | 4.22 | 0.9 | 14.3 | 0.28 | 4.69 | 0.236 | 0.052 | 0 |
| earnings21 | default | B- | 44 | 32.82 | 33.12 | 4.0 | 3.1 | 0.43 | 0.30 | 0.047 | -0.110 | 0 |
| easycom | glasses | B | 12 | 4.11 | 2.19 | 0.8 | 47.5 | 0.01 | 35.55 | 0.118 | 0.066 | 0 |
| libricss | clean-mix | S (synthetic) | 60 | 9.43 | 8.82 | 0.2 | 6.7 | 0.00 | 0.18 | 0.046 | -0.030 | 0 |
| maptask | default | A | 128 | 9.27 | 10.36 | 13.6 | 1.8 | 0.62 | 0.16 | -0.009 | -0.120 | 0 |
| msdwild_en | default | B | 894 | 25.78 | 25.94 | 3.4 | 2.8 | 0.32 | 0.46 | 0.011 | -0.107 | 0 |
| notsofar1 | ihm-mix | A- | 165 | 15.93 | 15.68 | 0.8 | 2.4 | 0.02 | 0.04 | 0.082 | -0.026 | 0 |
| primock57 | mix | D (official) / B (channel-activity RTTM) | 57 | 7.92 | 6.78 | 0.2 | 14.6 | 0.01 | 0.69 | 0.236 | 0.092 | 0 |
| sbcsae | default | C+ | 60 | 21.36 | 17.01 | 1.7 | 22.1 | 0.57 | 10.40 | 0.118 | -0.046 | 0 |
| scotus | default | C | 12 | 20.49 | 18.96 | 0.0 | 7.5 | 0.00 | 1.28 | 0.198 | 0.000 | 0 |
| voxconverse | default | B+ | 448 | 57.90 | 57.15 | 2.5 | 3.8 | 0.68 | 0.52 | -0.030 | -0.074 | 0 |

### Unannotated speech (% of reference speech) by detector

| dataset | sessions | Silero x2 | Silero (stock) | Silero (30 s reset) | WebRTC (mode 2) | energy | pyannote seg-3.0 | Nemotron (union) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog | 46 | 2.59 | 2.56 | 2.57 | 3.31 | 2.78 | 2.66 | 2.40 |
| ami | 16 | 0.71 | 0.66 | 0.65 | 5.97 | 5.45 | 3.29 | 0.34 |
| ava_avd_en | 29 | 1.57 | 1.15 | 1.25 | 52.55 | 58.26 | 2.49 | 0.52 |
| callfriend_eng | 40 | 1.65 | 1.65 | 1.64 | 1.85 | 1.72 | 1.73 | 1.65 |
| callhome_eng | 140 | 0.46 | 0.46 | 0.45 | 0.94 | 0.60 | 0.47 | 0.47 |
| chime6 | 2 | 0.85 | 0.79 | 0.75 | 4.80 | 6.88 | 1.40 | 0.80 |
| dipco | 5 | 0.34 | 0.34 | 0.34 | 1.35 | 0.70 | 0.38 | 0.18 |
| earnings21 | 44 | 0.43 | 0.43 | 0.43 | 1.50 | 1.00 | 0.44 | 0.46 |
| easycom | 12 | 0.01 | 0.00 | 0.01 | 0.01 | 0.00 | 1.52 | 0.10 |
| libricss | 54 | 0.00 | 0.00 | 0.00 | 0.01 | 0.18 | 0.00 | 0.00 |
| maptask | 128 | 0.62 | 0.61 | 0.49 | 4.35 | 1.76 | 3.95 | 0.19 |
| msdwild_en | 150 | 0.45 | 0.44 | 0.40 | 1.75 | 0.92 | 0.23 | 0.23 |
| notsofar1 | 129 | 0.03 | 0.03 | 0.03 | 0.37 | 0.04 | 0.02 | 0.02 |
| primock57 | 57 | 0.01 | 0.01 | 0.01 | 0.39 | 0.26 | 0.01 | 0.02 |
| sbcsae | 60 | 0.57 | 0.51 | 0.44 | 1.77 | 1.29 | 0.81 | 0.69 |
| scotus | 12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| voxconverse | 232 | 0.88 | 0.85 | 0.63 | 4.95 | 4.29 | 0.73 | 0.10 |

### Silent reference speech (% of reference speech) by detector

| dataset | sessions | Silero x2 | Silero (stock) | Silero (30 s reset) | WebRTC (mode 2) | energy | pyannote seg-3.0 | Nemotron (union) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog | 46 | 2.63 | 2.70 | 2.70 | 1.34 | 3.03 | 2.83 | 3.32 |
| ami | 16 | 0.28 | 0.35 | 0.38 | 0.04 | 0.12 | 0.13 | 0.23 |
| ava_avd_en | 29 | 20.83 | 24.80 | 21.44 | 3.79 | 2.37 | 9.53 | 12.26 |
| callfriend_eng | 40 | 4.00 | 4.05 | 4.63 | 2.00 | 3.32 | 4.27 | 3.84 |
| callhome_eng | 140 | 0.71 | 2.15 | 1.48 | 0.12 | 0.33 | 0.66 | 0.40 |
| chime6 | 2 | 3.19 | 3.80 | 4.95 | 2.12 | 2.69 | 1.14 | 1.06 |
| dipco | 5 | 1.18 | 1.32 | 1.43 | 0.42 | 1.11 | 1.08 | 1.74 |
| earnings21 | 44 | 0.30 | 0.31 | 0.34 | 0.01 | 1.22 | 0.31 | 1.38 |
| easycom | 12 | 35.55 | 42.18 | 37.92 | 65.59 | 50.42 | 3.21 | 4.69 |
| libricss | 54 | 0.19 | 0.19 | 0.19 | 0.13 | 0.39 | 0.21 | 0.30 |
| maptask | 128 | 0.16 | 0.19 | 0.22 | 0.08 | 0.12 | 0.06 | 0.06 |
| msdwild_en | 150 | 2.23 | 3.09 | 2.51 | 0.03 | 9.29 | 0.27 | 0.63 |
| notsofar1 | 129 | 0.04 | 0.04 | 0.04 | 0.00 | 0.05 | 0.07 | 0.42 |
| primock57 | 57 | 0.69 | 0.70 | 0.77 | 0.14 | 0.29 | 0.96 | 0.71 |
| sbcsae | 60 | 10.40 | 11.44 | 12.23 | 9.10 | 17.71 | 8.66 | 9.01 |
| scotus | 12 | 1.28 | 1.32 | 1.31 | 1.17 | 1.75 | 1.47 | 4.40 |
| voxconverse | 232 | 0.67 | 0.73 | 0.85 | 0.03 | 0.33 | 0.30 | 0.82 |

### Whisper check of the longest flagged regions

Cells: regions whose Whisper transcript is intelligible speech (>= 3 words, not a hallucination) / regions with any verbal content (also 1-2 words or fillers such as "yeah", "um") / regions checked. Unannotated + speech = the reference is missing speech; silent-ref + speech = the detector missed speech.

| dataset | unannotated: Silero | unannotated: energy | unannotated: WebRTC | silent-ref: Silero | silent-ref: energy | silent-ref: WebRTC | control (both silent) |
|---|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog | 19 / 20 / 20 | 19 / 20 / 20 | 18 / 20 / 20 | 3 / 8 / 20 | 7 / 7 / 20 | 2 / 3 / 20 | 0 / 1 / 20 |
| ami | 20 / 20 / 20 | 10 / 17 / 20 | 17 / 18 / 20 | 12 / 16 / 20 | 16 / 19 / 20 | 11 / 12 / 13 | 1 / 5 / 20 |
| ava_avd_en | 7 / 18 / 20 (2 laugh) | 5 / 15 / 20 | 4 / 14 / 20 (1 laugh) | 13 / 20 / 20 | 12 / 14 / 20 | 9 / 15 / 20 | 6 / 10 / 20 |
| callfriend_eng | 20 / 20 / 20 | 20 / 20 / 20 | 20 / 20 / 20 | 6 / 8 / 20 | 4 / 5 / 20 | 2 / 4 / 20 | 0 / 1 / 20 |
| callhome_eng | 20 / 20 / 20 | 20 / 20 / 20 | 19 / 20 / 20 | 10 / 14 / 20 | 12 / 14 / 20 | 0 / 1 / 13 | 2 / 2 / 20 |
| chime6 | 16 / 20 / 20 | 6 / 17 / 20 | 9 / 15 / 20 | 16 / 18 / 19 | 20 / 20 / 20 | 18 / 20 / 20 | 0 / 2 / 20 |
| dipco | 9 / 14 / 18 (2 laugh) | 5 / 14 / 20 | 6 / 12 / 20 | 13 / 18 / 20 | 10 / 16 / 20 | 8 / 13 / 17 | 1 / 6 / 20 |
| earnings21 | 20 / 20 / 20 | 10 / 12 / 20 | 10 / 10 / 20 | 7 / 9 / 17 | 6 / 6 / 7 | 0 / 0 / 2 | 1 / 1 / 20 |
| easycom | - | - | - | 15 / 19 / 20 | 17 / 19 / 20 | 15 / 20 / 20 | 0 / 3 / 20 |
| libricss | - | 0 / 0 / 20 | 0 / 0 / 3 | 0 / 1 / 15 | 0 / 4 / 20 | 0 / 0 / 8 | 0 / 0 / 20 |
| maptask | 3 / 11 / 20 (8 laugh) | 3 / 14 / 20 (1 laugh) | 8 / 14 / 20 (3 laugh) | 8 / 13 / 13 | 6 / 8 / 8 | 4 / 5 / 5 | 1 / 3 / 20 |
| msdwild_en | 8 / 16 / 20 (3 laugh) | 8 / 13 / 20 (1 laugh) | 6 / 11 / 20 | 17 / 20 / 20 | 19 / 20 / 20 | 2 / 4 / 4 | 0 / 5 / 20 (1 laugh) |
| notsofar1 | 5 / 5 / 5 | 5 / 5 / 6 | 4 / 5 / 20 | 1 / 7 / 8 (1 laugh) | 7 / 7 / 8 | - | 0 / 1 / 20 |
| primock57 | 0 / 0 / 1 | 2 / 8 / 20 | 3 / 9 / 20 | 4 / 14 / 20 | 1 / 1 / 9 | 0 / 2 / 6 | 0 / 0 / 20 |
| sbcsae | 10 / 11 / 20 (6 laugh) | 5 / 11 / 20 (2 laugh) | 1 / 13 / 20 | 10 / 16 / 20 | 15 / 18 / 20 | 5 / 14 / 20 | 0 / 4 / 20 |
| scotus | - | - | - | 0 / 5 / 20 | 1 / 5 / 20 | 0 / 4 / 20 | - |
| voxconverse | 9 / 14 / 20 (3 laugh) | 1 / 9 / 20 (1 laugh) | 4 / 11 / 20 (1 laugh) | 11 / 16 / 20 (1 laugh) | 16 / 17 / 20 | 9 / 12 / 14 | 2 / 8 / 20 |
| **all** | **166 / 209 / 244** (68% / 86%) | **119 / 195 / 286** (42% / 68%) | **129 / 192 / 283** (46% / 68%) | **146 / 222 / 312** (47% / 71%) | **169 / 200 / 292** (58% / 68%) | **85 / 129 / 222** (38% / 58%) | **14 / 52 / 320** (4% / 16%) |

## 2. Boundary precision per reference variant (vs Silero) and Nemotron error against the same reference

| dataset | reference | ref speech h | onset p25 / p50 / p75 s | offset p25 / p50 / p75 s | ref speech Silero calls silence % | Nemotron miss % | Nemotron FA % | Nemotron DER % (c=0) |
|---|---|---:|---|---|---:|---:|---:|---:|
| afrispeech_dialog | primary | 6.16 | -0.15 / 0.09 / 0.34 | -0.77 / -0.53 / -0.26 | 13.9 | 15.2 | 6.4 | 26.7 |
| ami | primary | 66.42 | -0.01 / 0.00 / 0.02 | -0.18 / -0.12 / -0.09 | 2.1 | 4.7 | 3.7 | 9.2 |
| ami | only_words | 80.91 | -0.01 / 0.01 / 0.03 | -0.15 / -0.10 / -0.05 | 13.0 | 24.1 | 1.2 | 26.0 |
| ami | segments | 83.99 | 0.03 / 0.07 / 0.18 | -0.08 / -0.01 / 0.12 | 15.0 | 30.5 | 0.2 | 31.1 |
| ami | word_and_vocalsounds | 81.63 | -0.01 / 0.01 / 0.03 | -0.14 / -0.10 / -0.03 | 13.5 | 26.1 | 1.0 | 27.7 |
| ava_avd_en | primary | 3.24 | -0.02 / 0.02 / 0.09 | -0.21 / -0.13 / -0.06 | 21.6 | 23.3 | 11.8 | 49.8 |
| callfriend_eng | primary | 9.38 | 0.13 / 0.16 / 0.21 | -0.26 / -0.22 / -0.18 | 15.5 | 18.6 | 7.9 | 30.8 |
| callhome_eng | primary | 17.53 | -0.02 / 0.00 / 0.03 | -0.13 / -0.10 / -0.06 | 5.4 | 7.3 | 3.9 | 11.7 |
| chime6 | primary | 6.85 | -0.01 / 0.02 / 0.05 | -0.19 / -0.12 / -0.04 | 8.8 | 16.6 | 10.1 | 32.8 |
| chime6 | annotation | 7.97 | 0.00 / 0.09 / 0.21 | -0.03 / 0.07 / 0.20 | 15.6 | 31.6 | 1.9 | 37.8 |
| dipco | primary | 4.87 | 0.19 / 0.24 / 0.31 | -0.02 / 0.05 / 0.12 | 14.3 | 25.1 | 1.5 | 27.3 |
| dipco | closetalk_activity | 4.04 | -0.02 / -0.01 / 0.01 | -0.21 / -0.16 / -0.13 | 5.7 | 20.0 | 10.5 | 31.5 |
| earnings21 | primary | 32.82 | 0.03 / 0.05 / 0.06 | -0.15 / -0.11 / -0.08 | 3.1 | 4.0 | 3.6 | 19.5 |
| easycom | primary | 4.11 | 0.02 / 0.12 / 0.37 | -0.03 / 0.07 / 0.43 | 47.5 | 19.6 | 4.1 | 30.4 |
| libricss | primary | 9.43 | 0.03 / 0.05 / 0.06 | -0.05 / -0.03 / -0.00 | 6.7 | 4.5 | 0.1 | 5.1 |
| maptask | primary | 9.27 | -0.02 / -0.01 / 0.01 | -0.16 / -0.12 / -0.09 | 1.8 | 3.3 | 4.5 | 7.9 |
| msdwild_en | primary | 25.78 | -0.04 / 0.01 / 0.07 | -0.19 / -0.11 / -0.02 | 2.8 | 9.6 | 3.9 | 17.8 |
| notsofar1 | primary | 15.93 | 0.07 / 0.08 / 0.10 | -0.06 / -0.03 / 0.00 | 2.4 | 12.6 | 0.7 | 14.5 |
| notsofar1 | fastmss_mfa | 10.64 | -0.02 / -0.01 / 0.02 | -0.18 / -0.13 / -0.09 | 0.6 | 3.7 | 4.4 | 9.6 |
| notsofar1 | words_gap0.2 | 15.68 | 0.02 / 0.04 / 0.06 | -0.10 / -0.05 / -0.02 | 1.6 | 8.4 | 1.4 | 11.2 |
| primock57 | primary | 7.92 | 0.18 / 0.24 / 0.29 | 0.03 / 0.09 / 0.15 | 14.6 | 24.0 | 0.1 | 24.1 |
| primock57 | channel_activity | 6.71 | -0.01 / 0.00 / 0.02 | -0.12 / -0.10 / -0.07 | 3.6 | 9.2 | 1.1 | 10.4 |
| sbcsae | primary | 21.36 | 0.03 / 0.12 / 0.39 | -0.14 / -0.05 / 0.05 | 22.1 | 22.5 | 2.6 | 27.4 |
| scotus | primary | 20.49 | 0.14 / 0.20 / 0.28 | 0.00 / 0.00 / 0.00 | 7.5 | 11.2 | 1.1 | 31.7 |
| voxconverse | primary | 57.90 | -0.09 / -0.03 / 0.02 | -0.19 / -0.07 / 0.01 | 3.8 | 3.2 | 1.9 | 8.4 |

### VAD accuracy against the tightest references

Cells: FA / miss % at collar 0; FA / miss % outside +/- 0.25 s of reference boundaries (sessions where every detector is available).

| dataset | reference | Silero x2 | Silero (30 s reset) | WebRTC (mode 2) | energy | pyannote seg-3.0 | Nemotron (union) | Silero x2 onset / offset p50 s |
|---|---|---|---|---|---|---|---|---|
| maptask (default) | primary: word-level | 13.6 / 1.8; 2.3 / 0.6 | 13.1 / 2.1; 1.9 / 0.7 | 28.3 / 0.5; 12.5 / 0.3 | 13.5 / 2.4; 4.9 / 0.6 | 30.0 / 0.7; 11.8 / 0.1 | 3.8 / 2.8; 0.5 / 1.1 | -0.009 / -0.120 |
| libricss (clean-mix) | primary: exact playback times (synthetic) | 0.2 / 6.7; 0.0 / 6.6 | 0.2 / 6.8; 0.0 / 6.6 | 0.9 / 3.4; 0.0 / 3.4 | 0.5 / 9.8; 0.2 / 9.4 | 0.3 / 3.6; 0.0 / 3.2 | 0.1 / 4.0; 0.0 / 3.7 | 0.046 / -0.031 |
| ami (ihm-mix) | primary: forced-aligned (MFA) | 9.8 / 2.1; 1.8 / 0.7 | 9.6 / 2.4; 1.7 / 0.8 | 20.5 / 1.0; 11.6 / 0.6 | 16.1 / 2.1; 9.9 / 0.7 | 22.5 / 0.8; 8.2 / 0.2 | 2.6 / 2.5; 0.8 / 1.3 | 0.004 / -0.116 |
| notsofar1 (ihm-mix) | fastmss_mfa: forced-aligned (MFA) | 4.8 / 0.5; 0.2 / 0.2 | 4.8 / 0.6; 0.2 / 0.2 | 7.1 / 0.4; 1.2 / 0.2 | 2.8 / 1.9; 0.2 / 0.6 | 2.5 / 1.3; 0.1 / 0.5 | 2.0 / 1.5; 0.1 / 0.9 | -0.008 / -0.130 |
| primock57 (mix) | channel_activity: per-channel energy (diagnostic) | 4.6 / 3.6; 0.0 / 1.8 | 4.5 / 3.8; 0.0 / 1.9 | 12.2 / 0.2; 1.4 / 0.1 | 6.9 / 0.2; 0.4 / 0.0 | 2.3 / 6.4; 0.0 / 3.6 | 1.1 / 6.7; 0.0 / 4.3 | 0.004 / -0.096 |

### Does Silero-vs-reference disagreement predict Nemotron's error? (every evaluated tag x reference)

| subset | detector | n | miss vs Nemotron miss: Pearson / Spearman | FA vs Nemotron FA: Pearson / Spearman |
|---|---|---:|---|---|
| all | Silero x2 | 43 | 0.65 / 0.67 | 0.83 / 0.83 |
| all | Silero (stock) | 43 | 0.61 / 0.65 | 0.81 / 0.81 |
| all | pyannote seg-3.0 | 43 | 0.61 / 0.69 | 0.79 / 0.86 |
| all | WebRTC (mode 2) | 43 | 0.42 / 0.52 | 0.41 / 0.58 |
| all | energy | 43 | 0.25 / 0.46 | 0.35 / 0.56 |
| close_talk_and_single_channel | Silero x2 | 26 | 0.74 / 0.71 | 0.86 / 0.89 |
| close_talk_and_single_channel | Silero (stock) | 26 | 0.72 / 0.73 | 0.87 / 0.90 |
| close_talk_and_single_channel | pyannote seg-3.0 | 26 | 0.61 / 0.67 | 0.73 / 0.83 |
| close_talk_and_single_channel | WebRTC (mode 2) | 26 | 0.74 / 0.70 | 0.54 / 0.72 |
| close_talk_and_single_channel | energy | 26 | 0.51 / 0.59 | 0.46 / 0.66 |
| far_field | Silero x2 | 17 | 0.63 / 0.73 | 0.89 / 0.73 |
| far_field | Silero (stock) | 17 | 0.59 / 0.68 | 0.88 / 0.69 |
| far_field | pyannote seg-3.0 | 17 | 0.70 / 0.78 | 0.87 / 0.91 |
| far_field | WebRTC (mode 2) | 17 | 0.29 / 0.27 | 0.45 / 0.52 |
| far_field | energy | 17 | -0.01 / 0.18 | 0.24 / 0.47 |

| tag | reference | Silero x2 miss % | pyannote miss % | Nemotron miss % | Silero x2 FA % | Nemotron FA % | Nemotron DER % |
|---|---|---:|---:|---:|---:|---:|---:|
| ava_avd_en.default | primary | 28.9 | 16.9 | 23.3 | 13.1 | 11.8 | 49.8 |
| sbcsae.default | primary | 22.1 | 17.2 | 22.5 | 1.7 | 2.6 | 27.4 |
| chime6.ihm-mix | annotation | 16.1 | 11.1 | 31.6 | 1.4 | 1.9 | 37.8 |
| callfriend_eng.default | primary | 15.5 | 17.2 | 18.6 | 5.8 | 7.9 | 30.8 |
| ami.ihm-mix | segments | 15.4 | 5.4 | 30.5 | 0.6 | 0.2 | 31.1 |
| primock57.mix | primary | 14.6 | 18.7 | 24.0 | 0.2 | 0.1 | 24.1 |
| afrispeech_dialog.default | primary | 13.9 | 11.2 | 15.2 | 4.8 | 6.4 | 26.7 |
| ami.ihm-mix | word_and_vocalsounds | 13.8 | 3.7 | 26.1 | 1.5 | 1.0 | 27.7 |
| ami.ihm-mix | only_words | 13.5 | 3.3 | 24.1 | 1.7 | 1.2 | 26.0 |
| dipco.ihm-mix | primary | 10.0 | 12.9 | 25.1 | 1.1 | 1.5 | 27.3 |
| chime6.ihm-mix | primary | 8.4 | 4.2 | 16.6 | 9.4 | 10.1 | 32.8 |
| scotus.default | primary | 7.5 | 6.9 | 11.2 | 0.0 | 1.1 | 31.7 |
| libricss.clean-mix | primary | 6.7 | 3.6 | 4.5 | 0.2 | 0.1 | 5.1 |
| icsi.ihm-mix | primary | 5.8 | 2.0 | 2.9 | 6.8 | 12.2 | 15.9 |
| msdwild_en.default | primary | 5.5 | 2.5 | 9.6 | 3.8 | 3.9 | 17.8 |
| callhome_eng.default | primary | 5.4 | 6.8 | 7.3 | 4.0 | 3.9 | 11.7 |
| voxconverse.default | primary | 4.1 | 2.2 | 3.2 | 3.0 | 1.9 | 8.4 |
| primock57.mix | channel_activity | 3.6 | 6.4 | 9.2 | 4.6 | 1.1 | 10.4 |
| earnings21.default | primary | 3.1 | 2.5 | 4.0 | 4.0 | 3.6 | 19.5 |
| notsofar1.ihm-mix | primary | 2.3 | 5.0 | 12.6 | 0.8 | 0.7 | 14.5 |
| ami.ihm-mix | primary | 2.1 | 0.8 | 4.7 | 9.8 | 3.7 | 9.2 |
| maptask.default | primary | 1.8 | 0.7 | 3.3 | 13.6 | 4.5 | 7.9 |
| icsi.ihm-mix | words_gap0.2 | 1.6 | 0.6 | 0.6 | 22.7 | 38.4 | 39.4 |
| notsofar1.ihm-mix | words_gap0.2 | 1.5 | 3.8 | 8.4 | 1.6 | 1.4 | 11.2 |
| dipco.ihm-mix | closetalk_activity | 1.2 | 2.0 | 20.0 | 11.0 | 10.6 | 31.5 |
| notsofar1.ihm-mix | fastmss_mfa | 0.5 | 1.3 | 3.7 | 4.8 | 4.4 | 9.6 |
| dipco.farfield | primary | 52.1 | 7.6 | 30.5 | 0.5 | 3.6 | 36.2 |
| chime6.farfield | annotation | 50.1 | 19.9 | 36.1 | 1.0 | 1.5 | 43.6 |
| easycom.glasses | primary | 47.5 | 7.8 | 19.6 | 0.8 | 4.1 | 30.4 |
| dipco.farfield | closetalk_activity | 47.3 | 4.0 | 25.3 | 5.7 | 12.0 | 40.3 |
| chime6.farfield | primary | 44.7 | 12.9 | 21.3 | 4.9 | 8.3 | 37.6 |
| chime6.farfield.dev | annotation | 27.7 | 10.7 | 38.1 | 0.9 | 1.1 | 41.6 |
| ami.sdm | segments | 23.0 | 6.6 | 31.2 | 0.6 | 0.5 | 32.5 |
| chime6.farfield.dev | primary | 22.6 | 5.4 | 18.7 | 6.3 | 8.5 | 31.7 |
| ami.sdm | word_and_vocalsounds | 21.3 | 5.0 | 26.9 | 1.1 | 1.3 | 29.2 |
| ami.sdm | only_words | 20.9 | 4.5 | 24.9 | 1.3 | 1.5 | 27.4 |
| icsi.sdm | primary | 20.6 | 3.1 | 3.8 | 3.5 | 11.1 | 15.8 |
| icsi.sdm | words_gap0.2 | 15.1 | 1.0 | 1.1 | 14.4 | 36.4 | 38.2 |
| libricss.sdm | primary | 13.5 | 5.7 | 8.2 | 0.1 | 0.6 | 14.3 |
| ami.sdm | primary | 9.1 | 1.4 | 5.9 | 7.3 | 4.1 | 11.3 |
| notsofar1.sc | primary | 3.1 | 4.3 | 15.9 | 1.1 | 0.6 | 18.4 |
| notsofar1.sc | words_gap0.2 | 2.3 | 3.2 | 11.8 | 1.8 | 1.1 | 15.0 |
| notsofar1.sc | fastmss_mfa | 1.1 | 1.6 | 6.1 | 4.8 | 2.6 | 11.3 |

## Silero drop-outs (stock vs state reset vs max of both)

A 10 s window is clear speech when Nemotron covers >= 50% of it and WebRTC (mode 3) fires on >= 50% of its frames; Silero drops out when its maximum probability in the window is < 0.2 (`scripts/vad_reset_check.py`).

| tag | hours | clear-speech 10 s windows | stock Silero drop-outs | 30 s reset | Silero x2 (max of both) |
|---|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 6.63 | 2288 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| ami.ihm-mix | 9.06 | 2472 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| ami.sdm | 9.06 | 536 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| ava_avd_en.default | 2.42 | 220 | 20 (9.09%) | 10 (4.55%) | 9 (4.09%) |
| callfriend_eng.default | 10.44 | 3457 | 0 (0.0%) | 2 (0.06%) | 0 (0.0%) |
| callhome_eng.default | 20.3 | 7067 | 74 (1.05%) | 8 (0.11%) | 1 (0.01%) |
| chime6.farfield | 5.21 | 551 | 140 (25.41%) | 44 (7.99%) | 24 (4.36%) |
| chime6.farfield.dev | 4.46 | 505 | 8 (1.58%) | 8 (1.58%) | 4 (0.79%) |
| chime6.ihm-mix | 5.21 | 655 | 0 (0.0%) | 2 (0.31%) | 0 (0.0%) |
| dipco.farfield | 2.6 | 5 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| dipco.ihm-mix | 2.6 | 825 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| earnings21.default | 39.26 | 13107 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| easycom.glasses | 5.3 | 70 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| icsi.ihm-mix | 2.77 | 824 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| icsi.sdm | 2.77 | 11 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| libricss.clean-mix | 9.08 | 3146 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| libricss.sdm | 9.09 | 496 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| maptask.default | 14.31 | 4234 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| msdwild_en.default | 4.16 | 1346 | 25 (1.86%) | 0 (0.0%) | 0 (0.0%) |
| notsofar1.ihm-mix | 13.34 | 4561 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| notsofar1.sc | 13.34 | 4577 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| primock57.mix | 8.64 | 2948 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| sbcsae.default | 23.31 | 5278 | 15 (0.28%) | 20 (0.38%) | 4 (0.08%) |
| scotus.default | 20.5 | 5938 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| voxconverse.default | 43.54 | 14537 | 11 (0.08%) | 10 (0.07%) | 10 (0.07%) |
| **all** | | **79654** | **293 (0.368%)** | **104 (0.131%)** | **52 (0.065%)** |

## 3. VAD-assisted Nemotron (post-hoc on cached outputs): change in DER (points)

Primary reference, collar 0:

| tag | sessions | baseline DER % | gate:silero_x2 | gate+0.25:silero_x2 | gate:silero | gate:silero_r30 | gate:webrtc | gate:energy | gate:pyannote | gate+0.25:pyannote | fill:silero_x2 | vad_decides:silero_x2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 46 | 26.69 | +1.93 | +0.03 | +2.10 | +1.99 | +1.60 | +3.69 | +1.03 | +0.03 | -2.58 | -0.62 |
| ava_avd_en.default | 29 | 49.79 | +6.72 | +7.51 | +7.98 | +7.00 | +0.62 | -0.07 | -0.45 | +1.67 | +3.32 | +10.00 |
| callfriend_eng.default | 40 | 30.80 | +1.92 | +0.37 | +1.99 | +2.54 | +0.64 | +1.38 | +1.76 | +0.40 | -1.04 | +0.97 |
| callhome_eng.default | 140 | 11.68 | +1.17 | +0.34 | +2.38 | +2.19 | +0.23 | +0.87 | +1.61 | +0.30 | +0.56 | +1.77 |
| chime6.farfield.dev | 2 | 31.70 | +11.50 | +10.30 | +13.42 | +15.71 | +20.20 | +14.55 | +1.68 | +1.17 | +0.24 | +11.77 |
| chime6.farfield | 2 | 37.63 | +23.83 | +21.64 | +30.44 | +27.26 | +14.98 | +9.47 | +4.20 | +3.16 | +0.44 | +24.29 |
| chime6.ihm-mix | 2 | 32.76 | +2.59 | +1.57 | +3.14 | +3.89 | +3.66 | +4.92 | +0.66 | +0.37 | +1.00 | +3.63 |
| dipco.farfield | 5 | 36.16 | +26.93 | +20.70 | +36.09 | +27.50 | +28.51 | +26.38 | +0.49 | +0.23 | -0.98 | +26.00 |
| dipco.ihm-mix | 5 | 27.31 | +1.56 | +0.21 | +1.73 | +1.69 | +1.48 | +3.31 | +3.21 | +0.07 | -2.41 | -0.82 |
| earnings21.default | 44 | 19.54 | +0.01 | -0.03 | +0.04 | +0.09 | -0.08 | +0.97 | -0.87 | -0.09 | +1.20 | +1.30 |
| easycom.glasses | 12 | 30.38 | +25.03 | +20.18 | +29.61 | +26.47 | +49.55 | +40.84 | +1.11 | +0.58 | -0.35 | +24.70 |
| icsi.ihm-mix | 3 | 15.86 | +1.09 | +0.26 | +1.27 | +1.37 | +0.43 | +5.09 | -0.14 | +0.10 | +2.26 | +3.39 |
| icsi.sdm | 3 | 15.85 | +11.71 | +6.98 | +15.71 | +12.25 | +37.54 | +54.08 | +0.30 | +0.20 | +1.15 | +12.90 |
| libricss.clean-mix | 54 | 5.09 | +3.34 | +0.15 | +3.46 | +3.35 | +1.35 | +5.73 | +1.50 | +0.14 | -0.60 | +2.78 |
| libricss.sdm | 54 | 14.30 | +6.97 | +2.95 | +7.99 | +7.11 | +8.32 | +10.16 | +1.14 | +0.15 | -1.04 | +5.95 |
| maptask.default | 128 | 7.94 | +0.37 | +0.25 | +0.45 | +0.52 | +0.18 | +0.46 | +0.05 | +0.01 | +8.24 | +8.62 |
| msdwild_en.default | 150 | 17.79 | +2.26 | +1.59 | +2.89 | +2.46 | +0.48 | +13.56 | +0.05 | -0.12 | -0.44 | +1.85 |
| notsofar1.ihm-mix | 129 | 14.52 | +0.20 | +0.02 | +0.22 | +0.22 | +0.20 | +1.28 | +0.92 | +0.03 | -1.66 | -1.43 |
| notsofar1.sc | 129 | 18.41 | +0.50 | +0.00 | +0.54 | +0.53 | +0.12 | +1.37 | +0.77 | +0.10 | -1.83 | -1.30 |
| primock57.mix | 57 | 24.15 | +0.87 | +0.15 | +0.90 | +0.96 | +0.11 | +0.19 | +1.70 | +0.15 | -5.87 | -4.92 |
| sbcsae.default | 60 | 27.38 | +3.53 | +1.24 | +4.31 | +4.81 | +6.37 | +14.02 | +1.41 | +0.43 | -1.93 | +1.65 |
| scotus.default | 12 | 31.66 | +1.80 | +0.05 | +2.02 | +1.83 | +2.68 | +4.41 | +1.43 | +0.08 | -1.89 | -0.09 |
| voxconverse.default | 232 | 8.39 | +2.86 | +0.54 | +3.11 | +3.14 | +2.28 | +6.80 | +1.22 | +0.23 | +1.32 | +4.18 |

Primary reference, collar 0.25 s:

| tag | sessions | baseline DER % | gate:silero_x2 | gate+0.25:silero_x2 | gate:silero | gate:silero_r30 | gate:webrtc | gate:energy | gate:pyannote | gate+0.25:pyannote | fill:silero_x2 | vad_decides:silero_x2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 46 | 24.51 | +1.99 | +0.02 | +2.16 | +2.04 | +1.64 | +3.81 | +1.08 | +0.02 | -2.74 | -0.72 |
| ava_avd_en.default | 29 | 33.98 | +11.68 | +11.09 | +13.49 | +11.92 | +3.01 | +1.89 | +2.59 | +2.44 | +2.51 | +14.07 |
| callfriend_eng.default | 40 | 23.24 | +1.84 | +0.36 | +1.92 | +2.47 | +0.66 | +1.66 | +1.90 | +0.39 | -1.70 | +0.21 |
| callhome_eng.default | 140 | 7.23 | +1.38 | +0.24 | +2.75 | +2.25 | +0.44 | +1.12 | +1.67 | +0.21 | -0.98 | +0.42 |
| chime6.farfield.dev | 2 | 19.06 | +14.23 | +12.90 | +16.46 | +18.82 | +26.56 | +18.01 | +1.78 | +1.25 | -0.52 | +13.71 |
| chime6.farfield | 2 | 25.61 | +27.21 | +24.95 | +34.42 | +31.07 | +19.24 | +11.60 | +4.79 | +3.84 | -0.34 | +26.88 |
| chime6.ihm-mix | 2 | 22.49 | +2.62 | +1.41 | +3.23 | +3.86 | +5.03 | +5.84 | +0.53 | +0.23 | -0.64 | +1.99 |
| dipco.farfield | 5 | 28.07 | +30.87 | +23.72 | +41.08 | +31.44 | +33.12 | +31.03 | +0.49 | +0.23 | -1.05 | +29.88 |
| dipco.ihm-mix | 5 | 19.43 | +1.46 | +0.18 | +1.61 | +1.56 | +1.53 | +3.09 | +2.60 | +0.03 | -2.39 | -0.88 |
| earnings21.default | 44 | 15.90 | +0.68 | -0.03 | +0.76 | +0.75 | +0.32 | +1.67 | +0.43 | -0.08 | -0.52 | +0.17 |
| easycom.glasses | 12 | 21.68 | +29.30 | +23.92 | +34.36 | +30.96 | +56.44 | +46.48 | +1.39 | +0.63 | -0.36 | +28.94 |
| icsi.ihm-mix | 3 | 5.31 | +2.95 | +0.19 | +3.26 | +3.21 | +1.75 | +7.84 | +0.22 | -0.04 | +1.69 | +4.63 |
| icsi.sdm | 3 | 5.39 | +14.93 | +7.75 | +19.61 | +15.49 | +45.77 | +63.82 | +0.88 | +0.14 | +1.31 | +16.22 |
| libricss.clean-mix | 54 | 4.44 | +3.55 | +0.16 | +3.68 | +3.56 | +1.49 | +5.87 | +1.44 | +0.16 | -0.62 | +2.96 |
| libricss.sdm | 54 | 13.02 | +7.28 | +3.11 | +8.33 | +7.42 | +8.77 | +10.42 | +1.12 | +0.16 | -0.98 | +6.33 |
| maptask.default | 128 | 1.88 | +0.18 | -0.03 | +0.23 | +0.23 | +0.16 | +0.25 | -0.09 | -0.09 | +1.44 | +1.62 |
| msdwild_en.default | 150 | 10.67 | +2.43 | +1.42 | +3.06 | +2.61 | +0.76 | +14.45 | +0.09 | -0.20 | -1.06 | +1.38 |
| notsofar1.ihm-mix | 129 | 5.51 | +0.14 | +0.01 | +0.16 | +0.16 | +0.19 | +0.83 | +0.54 | +0.02 | -1.51 | -1.35 |
| notsofar1.sc | 129 | 6.92 | +0.30 | -0.04 | +0.34 | +0.33 | +0.02 | +0.95 | +0.47 | +0.05 | -1.47 | -1.14 |
| primock57.mix | 57 | 15.99 | +0.83 | +0.12 | +0.86 | +0.93 | +0.11 | +0.16 | +1.47 | +0.14 | -4.58 | -3.69 |
| sbcsae.default | 60 | 24.23 | +3.94 | +1.27 | +4.74 | +5.21 | +6.90 | +14.77 | +1.53 | +0.42 | -1.86 | +2.11 |
| scotus.default | 12 | 30.25 | +1.82 | +0.04 | +2.05 | +1.85 | +2.70 | +4.47 | +1.42 | +0.07 | -1.81 | +0.01 |
| voxconverse.default | 232 | 5.74 | +3.16 | +0.50 | +3.42 | +3.41 | +2.59 | +7.27 | +1.32 | +0.23 | +0.73 | +3.89 |

Error components, gate with Silero (collar 0):

| tag | baseline FA / miss / conf % | gate:silero_x2 FA / miss / conf % |
|---|---|---|
| afrispeech_dialog.default | 6.44 / 15.15 / 5.10 | 6.29 / 17.37 / 4.97 |
| ava_avd_en.default | 11.78 / 23.30 / 14.70 | 7.38 / 37.85 / 11.28 |
| callfriend_eng.default | 7.90 / 18.58 / 4.32 | 7.63 / 20.93 / 4.16 |
| callhome_eng.default | 3.92 / 7.35 / 0.41 | 3.25 / 9.23 / 0.37 |
| chime6.farfield.dev | 8.52 / 18.71 / 4.48 | 6.56 / 34.04 / 2.60 |
| chime6.farfield | 8.27 / 21.29 / 8.07 | 4.66 / 52.54 / 4.25 |
| chime6.ihm-mix | 10.12 / 16.60 / 6.05 | 8.54 / 21.21 / 5.60 |
| dipco.farfield | 3.61 / 30.49 / 2.06 | 2.33 / 59.61 / 1.15 |
| dipco.ihm-mix | 1.47 / 25.08 / 0.76 | 1.34 / 26.81 / 0.72 |
| earnings21.default | 3.56 / 3.99 / 11.99 | 2.32 / 5.39 / 11.83 |
| easycom.glasses | 4.10 / 19.61 / 6.67 | 1.33 / 51.65 / 2.43 |
| icsi.ihm-mix | 12.22 / 2.89 / 0.76 | 8.99 / 7.32 / 0.65 |
| icsi.sdm | 11.08 / 3.77 / 1.00 | 6.04 / 20.92 / 0.59 |
| libricss.clean-mix | 0.14 / 4.51 / 0.44 | 0.08 / 7.91 / 0.43 |
| libricss.sdm | 0.58 / 8.21 / 5.52 | 0.32 / 15.81 / 5.14 |
| maptask.default | 4.55 / 3.32 / 0.07 | 3.95 / 4.30 / 0.07 |
| msdwild_en.default | 3.87 / 9.55 / 4.37 | 3.23 / 12.61 / 4.22 |
| notsofar1.ihm-mix | 0.68 / 12.57 / 1.27 | 0.64 / 12.82 / 1.27 |
| notsofar1.sc | 0.60 / 15.91 / 1.90 | 0.53 / 16.49 / 1.89 |
| primock57.mix | 0.10 / 24.00 / 0.05 | 0.06 / 24.92 / 0.04 |
| sbcsae.default | 2.56 / 22.52 / 2.30 | 1.96 / 27.05 / 1.90 |
| scotus.default | 1.10 / 11.16 / 19.40 | 1.09 / 13.35 / 19.01 |
| voxconverse.default | 1.87 / 3.24 / 3.27 | 1.47 / 6.65 / 3.13 |

Protocol variants (scoring region changed; not comparable to official numbers):

| tag | official UEM h | uem_span h | uem_speech h | baseline DER % c=0 | uem_span | uem_speech |
|---|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 6.632 | 6.63 | 6.487 | 26.69 | 26.69 | 25.60 |
| ava_avd_en.default | 2.318 | 2.216 | 1.13 | 49.79 | 48.74 | 44.75 |
| callfriend_eng.default | 10.438 | 10.432 | 10.053 | 30.80 | 30.77 | 29.18 |
| callhome_eng.default | 20.296 | 20.294 | 19.912 | 11.68 | 11.68 | 11.44 |
| chime6.farfield.dev | 4.433 | 4.394 | 3.237 | 31.70 | 31.64 | 29.13 |
| chime6.farfield | 5.191 | 5.191 | 2.629 | 37.63 | 37.63 | 32.55 |
| chime6.ihm-mix | 5.191 | 5.191 | 4.289 | 32.76 | 32.76 | 31.61 |
| dipco.farfield | 2.602 | 2.596 | 1.629 | 36.16 | 36.17 | 33.37 |
| dipco.ihm-mix | 2.602 | 2.599 | 2.435 | 27.31 | 27.31 | 26.99 |
| earnings21.default | 39.263 | 39.185 | 37.748 | 19.54 | 19.53 | 19.30 |
| easycom.glasses | 5.303 | 5.285 | 3.076 | 30.38 | 30.37 | 25.82 |
| icsi.ihm-mix | 2.766 | 2.758 | 2.644 | 15.86 | 15.83 | 15.63 |
| icsi.sdm | 2.766 | 2.757 | 2.407 | 15.85 | 15.84 | 14.97 |
| libricss.clean-mix | 9.076 | 9.044 | 8.741 | 5.09 | 5.09 | 5.04 |
| libricss.sdm | 9.076 | 9.026 | 8.456 | 14.30 | 14.32 | 14.22 |
| maptask.default | 14.31 | 14.294 | 13.334 | 7.94 | 7.94 | 7.79 |
| msdwild_en.default | 4.16 | 4.149 | 3.986 | 17.79 | 17.74 | 17.49 |
| notsofar1.ihm-mix | 13.337 | 13.039 | 12.978 | 14.52 | 14.52 | 14.50 |
| notsofar1.sc | 13.337 | 13.038 | 12.97 | 18.41 | 18.37 | 18.35 |
| primock57.mix | 8.635 | 8.611 | 8.349 | 24.15 | 24.14 | 23.93 |
| sbcsae.default | 23.238 | 23.205 | 20.525 | 27.38 | 27.31 | 22.40 |
| scotus.default | 20.494 | 20.494 | 20.335 | 31.66 | 31.66 | 31.13 |
| voxconverse.default | 43.536 | 43.164 | 41.543 | 8.39 | 8.37 | 8.25 |

### Re-inference on VAD-modified audio (sample of sessions per tag)

| tag | sessions | hours | cached DER % c=0 | re-run, same audio | trim (audio kept %) | zero | cached DER % c=0.25 | re-run | trim | zero |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 8 | 1.11 | 17.19 | 17.19 | 17.20 (98%) | 16.98 | 15.36 | 15.36 | 15.36 | 15.14 |
| ami.ihm-mix | 2 | 1.21 | 9.26 | 9.26 | 9.57 (78%) | 11.14 | 4.12 | 4.12 | 4.21 | 5.07 |
| ami.sdm | 2 | 1.21 | 11.27 | 11.27 | 14.50 (72%) | 16.65 | 5.02 | 5.02 | 6.93 | 8.35 |
| ava_avd_en.default | 12 | 1.00 | 50.06 | 50.06 | 58.33 (44%) | 59.05 | 34.13 | 34.13 | 45.76 | 47.84 |
| callfriend_eng.default | 5 | 1.15 | 37.37 | 37.37 | 37.83 (88%) | 38.33 | 32.93 | 32.93 | 33.50 | 34.40 |
| callhome_eng.default | 9 | 1.09 | 10.97 | 10.97 | 11.34 (95%) | 11.78 | 6.57 | 6.57 | 6.89 | 7.31 |
| chime6.farfield | 1 | 2.56 | 33.03 | 33.03 | 70.09 (28%) | 71.05 | 21.22 | 21.22 | 63.34 | 64.16 |
| chime6.ihm-mix | 1 | 2.56 | 31.89 | 31.89 | 23.94 (80%) | 23.35 | 22.25 | 22.25 | 12.69 | 12.50 |
| dipco.farfield | 2 | 1.11 | 35.90 | 35.90 | 50.08 (69%) | 50.32 | 27.73 | 27.73 | 43.62 | 43.97 |
| dipco.ihm-mix | 2 | 1.11 | 27.60 | 27.60 | 27.63 (94%) | 29.79 | 18.84 | 18.84 | 18.93 | 20.32 |
| earnings21.default | 2 | 1.44 | 12.61 | 12.61 | 11.99 (96%) | 12.10 | 4.61 | 4.61 | 4.14 | 5.32 |
| easycom.glasses | 3 | 1.25 | 32.20 | 32.20 | 58.57 (47%) | 62.18 | 21.77 | 21.77 | 53.36 | 57.14 |
| icsi.ihm-mix | 1 | 1.01 | 13.62 | 13.62 | 14.72 (88%) | 18.55 | 4.47 | 4.47 | 5.57 | 12.18 |
| icsi.sdm | 1 | 1.01 | 14.55 | 14.55 | 27.69 (72%) | 32.76 | 5.23 | 5.23 | 18.73 | 26.41 |
| libricss.clean-mix | 6 | 1.01 | 5.14 | 5.14 | 6.47 (95%) | 5.69 | 4.41 | 4.41 | 5.78 | 5.07 |
| libricss.sdm | 6 | 1.01 | 13.50 | 13.50 | 15.25 (94%) | 12.92 | 12.26 | 12.26 | 14.03 | 11.54 |
| maptask.default | 10 | 1.27 | 7.35 | 7.35 | 7.50 (92%) | 9.71 | 1.25 | 1.25 | 1.33 | 2.91 |
| msdwild_en.default | 28 | 1.02 | 23.43 | 23.43 | 25.27 (86%) | 27.11 | 18.01 | 18.01 | 17.83 | 19.76 |
| notsofar1.ihm-mix | 10 | 1.03 | 12.60 | 12.60 | 12.15 (97%) | 13.86 | 4.94 | 4.94 | 4.54 | 5.84 |
| notsofar1.sc | 10 | 1.03 | 15.52 | 15.52 | 15.57 (97%) | 15.80 | 5.66 | 5.66 | 5.55 | 6.09 |
| primock57.mix | 7 | 1.07 | 23.25 | 23.25 | 23.76 (95%) | 23.90 | 15.56 | 15.56 | 16.07 | 16.21 |
| sbcsae.default | 3 | 1.18 | 22.28 | 22.28 | 23.33 (87%) | 22.61 | 16.36 | 16.36 | 17.38 | 16.87 |
| scotus.default | 1 | 1.71 | 22.44 | 22.44 | 29.59 (99%) | 30.51 | 20.89 | 20.89 | 28.22 | 29.21 |
| voxconverse.default | 6 | 1.13 | 9.52 | 9.52 | 9.73 (98%) | 9.79 | 6.24 | 6.24 | 6.47 | 6.59 |

## PriMock57 per channel

```json
{
 "per_speaker_role": {
  "doctor": {
   "labelled_h": 4.817,
   "energy_activity_h": 4.106,
   "silero_h": 4.02,
   "silero_nopad_h": 3.903,
   "labelled_silero_silent_pct": 16.78,
   "labelled_silero_silent_ge0.3s_pct": 10.29,
   "labelled_energy_silent_ge0.3s_pct": 9.53,
   "silero_unlabelled_min": 0.05,
   "energy_unlabelled_min": 1.37,
   "energy_not_silero_ge0.3s_min": 6.73,
   "silero_not_energy_ge0.3s_min": 0.08
  },
  "patient": {
   "labelled_h": 3.593,
   "energy_activity_h": 2.852,
   "silero_h": 2.806,
   "silero_nopad_h": 2.698,
   "labelled_silero_silent_pct": 22.15,
   "labelled_silero_silent_ge0.3s_pct": 14.21,
   "labelled_energy_silent_ge0.3s_pct": 13.73,
   "silero_unlabelled_min": 0.1,
   "energy_unlabelled_min": 1.03,
   "energy_not_silero_ge0.3s_min": 4.63,
   "silero_not_energy_ge0.3s_min": 0.02
  }
 },
 "overlap_pct_of_speech": {
  "textgrid": 6.26,
  "energy": 3.69,
  "silero_channel": 1.45
 }
}
```

Nemotron 3 Diarization (cached, mix) against each reference:

| reference | DER % c=0 | FA | miss | DER % c=0.25 |
|---|---:|---:|---:|---:|
| primary | 24.15 | 0.10 | 24.00 | 15.99 |
| channel_activity | 10.38 | 1.12 | 9.15 | 4.08 |
| silero_channel | 9.85 | 1.74 | 7.99 | 2.55 |
| silero_channel_nopad | 9.74 | 3.28 | 6.33 | 2.56 |

Energy-vs-Silero disagreements on the isolated channels (30 longest of each kind), Whisper transcript classes:

| kind | regions | seconds | speech | short | laughter | none |
|---|---:|---:|---:|---:|---:|---:|
| energy_not_silero | 30 | 46.44 | 2 | 6 | 0 | 22 |
| silero_not_energy | 17 | 5.78 | 1 | 11 | 0 | 5 |

