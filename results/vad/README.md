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
| callfriend_eng | default | C- | 40 | 9.38 | 8.47 | 5.8 | 15.5 | 1.65 | 4.00 | 0.157 | -0.222 | 0 |
| callhome_eng | default | C | 140 | 17.53 | 17.27 | 4.0 | 5.4 | 0.46 | 0.71 | 0.000 | -0.096 | 0 |
| chime6 | ihm-mix | A- | 4 | 6.85 | 6.83 | 8.5 | 8.8 | 1.13 | 4.00 | 0.016 | -0.116 | 0 |
| maptask | default | A | 128 | 9.27 | 10.36 | 13.6 | 1.8 | 0.62 | 0.16 | -0.009 | -0.120 | 0 |
| msdwild_en | default | B | 894 | 25.78 | 25.94 | 3.4 | 2.8 | 0.32 | 0.46 | 0.011 | -0.107 | 0 |
| primock57 | mix | D (official) / B (channel-activity RTTM) | 57 | 7.92 | 6.78 | 0.2 | 14.6 | 0.01 | 0.69 | 0.236 | 0.092 | 0 |
| voxconverse | default | B+ | 448 | 57.90 | 57.15 | 2.5 | 3.8 | 0.68 | 0.52 | -0.030 | -0.074 | 0 |

### Unannotated speech (% of reference speech) by detector

| dataset | sessions | Silero x2 | Silero (stock) | Silero (30 s reset) | WebRTC (mode 2) | energy | pyannote seg-3.0 | Nemotron (union) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog | 46 | 2.59 | 2.56 | 2.57 | 3.31 | 2.78 | 2.66 | 2.40 |
| ami | 16 | 0.71 | 0.66 | 0.65 | 5.97 | 5.45 | 3.29 | 0.34 |
| callfriend_eng | 40 | 1.65 | 1.65 | 1.64 | 1.85 | 1.72 | 1.73 | 1.65 |
| callhome_eng | 140 | 0.46 | 0.46 | 0.45 | 0.94 | 0.60 | 0.47 | 0.47 |
| chime6 | 2 | 0.85 | 0.79 | 0.75 | 4.80 | 6.88 | 1.40 | 0.80 |
| maptask | 128 | 0.62 | 0.61 | 0.49 | 4.35 | 1.76 | 3.95 | 0.19 |
| msdwild_en | 150 | 0.45 | 0.44 | 0.40 | 1.75 | 0.92 | 0.23 | 0.23 |
| primock57 | 57 | 0.01 | 0.01 | 0.01 | 0.39 | 0.26 | 0.01 | 0.02 |
| voxconverse | 232 | 0.88 | 0.85 | 0.63 | 4.95 | 4.29 | 0.73 | 0.10 |

### Silent reference speech (% of reference speech) by detector

| dataset | sessions | Silero x2 | Silero (stock) | Silero (30 s reset) | WebRTC (mode 2) | energy | pyannote seg-3.0 | Nemotron (union) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog | 46 | 2.63 | 2.70 | 2.70 | 1.34 | 3.03 | 2.83 | 3.32 |
| ami | 16 | 0.28 | 0.35 | 0.38 | 0.04 | 0.12 | 0.13 | 0.23 |
| callfriend_eng | 40 | 4.00 | 4.05 | 4.63 | 2.00 | 3.32 | 4.27 | 3.84 |
| callhome_eng | 140 | 0.71 | 2.15 | 1.48 | 0.12 | 0.33 | 0.66 | 0.40 |
| chime6 | 2 | 3.19 | 3.80 | 4.95 | 2.12 | 2.69 | 1.14 | 1.06 |
| maptask | 128 | 0.16 | 0.19 | 0.22 | 0.08 | 0.12 | 0.06 | 0.06 |
| msdwild_en | 150 | 2.23 | 3.09 | 2.51 | 0.03 | 9.29 | 0.27 | 0.63 |
| primock57 | 57 | 0.69 | 0.70 | 0.77 | 0.14 | 0.29 | 0.96 | 0.71 |
| voxconverse | 232 | 0.67 | 0.73 | 0.85 | 0.03 | 0.33 | 0.30 | 0.82 |

### Whisper check of the longest flagged regions (regions with intelligible speech / regions checked)

| dataset | unannotated: Silero | unannotated: energy | unannotated: WebRTC | silent-ref: Silero | silent-ref: energy | silent-ref: WebRTC | control (both silent) |
|---|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog | 19/20 | 19/20 | 18/20 | 3/20 | 7/20 | 3/20 | 0/20 |
| callfriend_eng | 20/20 | 20/20 | 20/20 | 6/20 | 4/20 | 2/20 | 0/20 |
| callhome_eng | 20/20 | 20/20 | 19/20 | 10/20 | 12/20 | 0/13 | 2/20 |
| maptask | 3/20 | 5/20 | 8/20 | 8/13 | 6/8 | 4/5 | 2/20 |
| msdwild_en | 8/20 | 8/20 | 8/20 | 17/20 | 19/20 | 2/4 | 0/20 |
| primock57 | 0/1 | 2/20 | 3/20 | 4/20 | 1/9 | 0/6 | 0/20 |
| voxconverse | 10/20 | 1/20 | 4/20 | 11/20 | 19/20 | 9/14 | 2/20 |
| **all** | **80/121 (66%)** | **75/140 (54%)** | **80/140 (57%)** | **59/133 (44%)** | **68/117 (58%)** | **20/82 (24%)** | **6/140 (4%)** |

## 2. Boundary precision per reference variant (vs Silero) and Nemotron error against the same reference

| dataset | reference | ref speech h | onset p25 / p50 / p75 s | offset p25 / p50 / p75 s | ref speech Silero calls silence % | Nemotron miss % | Nemotron FA % | Nemotron DER % (c=0) |
|---|---|---:|---|---|---:|---:|---:|---:|
| afrispeech_dialog | primary | 6.16 | -0.15 / 0.09 / 0.34 | -0.77 / -0.53 / -0.26 | 13.9 | 15.2 | 6.4 | 26.7 |
| ami | primary | 66.42 | -0.01 / 0.00 / 0.02 | -0.18 / -0.12 / -0.09 | 2.1 | 4.7 | 3.7 | 9.2 |
| ami | only_words | 80.91 | -0.01 / 0.01 / 0.03 | -0.15 / -0.10 / -0.05 | 13.0 | 24.1 | 1.2 | 26.0 |
| ami | segments | 83.99 | 0.03 / 0.07 / 0.18 | -0.08 / -0.01 / 0.12 | 15.0 | 30.5 | 0.2 | 31.1 |
| ami | word_and_vocalsounds | 81.63 | -0.01 / 0.01 / 0.03 | -0.14 / -0.10 / -0.03 | 13.5 | 26.1 | 1.0 | 27.7 |
| callfriend_eng | primary | 9.38 | 0.13 / 0.16 / 0.21 | -0.26 / -0.22 / -0.18 | 15.5 | 18.6 | 7.9 | 30.8 |
| callhome_eng | primary | 17.53 | -0.02 / 0.00 / 0.03 | -0.13 / -0.10 / -0.06 | 5.4 | 7.3 | 3.9 | 11.7 |
| chime6 | primary | 6.85 | -0.01 / 0.02 / 0.05 | -0.19 / -0.12 / -0.04 | 8.8 | 16.6 | 10.1 | 32.8 |
| chime6 | annotation | 7.97 | 0.00 / 0.09 / 0.21 | -0.03 / 0.07 / 0.20 | 15.6 | 31.6 | 1.9 | 37.8 |
| maptask | primary | 9.27 | -0.02 / -0.01 / 0.01 | -0.16 / -0.12 / -0.09 | 1.8 | 3.3 | 4.5 | 7.9 |
| msdwild_en | primary | 25.78 | -0.04 / 0.01 / 0.07 | -0.19 / -0.11 / -0.02 | 2.8 | 9.6 | 3.9 | 17.8 |
| primock57 | primary | 7.92 | 0.18 / 0.24 / 0.29 | 0.03 / 0.09 / 0.15 | 14.6 | 24.0 | 0.1 | 24.1 |
| primock57 | channel_activity | 6.71 | -0.01 / 0.00 / 0.02 | -0.12 / -0.10 / -0.07 | 3.6 | 9.2 | 1.1 | 10.4 |
| voxconverse | primary | 57.90 | -0.09 / -0.03 / 0.02 | -0.19 / -0.07 / 0.01 | 3.8 | 3.2 | 1.9 | 8.4 |

### VAD accuracy against the tightest references (frame level, collar 0)

| dataset | reference | Silero x2 FA / miss % | Silero (30 s reset) FA / miss % | WebRTC (mode 2) FA / miss % | energy FA / miss % | pyannote seg-3.0 FA / miss % | Nemotron (union) FA / miss % | Silero onset / offset p50 s |
|---|---|---|---|---|---|---|---|---|
| maptask (default) | primary: word-level | 13.6 / 1.8 | 13.1 / 2.1 | 28.3 / 0.5 | 13.5 / 2.4 | 30.0 / 0.7 | 3.8 / 2.8 | -0.009 / -0.120 |
| ami (ihm-mix) | primary: forced-aligned (MFA) | 10.8 / 2.1 | 10.5 / 2.4 | 21.2 / 1.0 | 16.5 / 2.2 | 22.5 / 0.8 | 2.6 / 2.5 | 0.002 / -0.120 |
| primock57 (mix) | channel_activity: per-channel energy (diagnostic) | 4.6 / 3.6 | 4.5 / 3.8 | 12.2 / 0.2 | 6.9 / 0.2 | 2.3 / 6.4 | 1.1 / 6.7 | 0.004 / -0.096 |

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

## 3. VAD-assisted Nemotron (post-hoc on cached outputs): change in DER (points)

Primary reference, collar 0:

| tag | sessions | baseline DER % | gate:silero_x2 | gate+0.25:silero_x2 | gate:silero | gate:silero_r30 | gate:webrtc | gate:energy | gate:pyannote | gate+0.25:pyannote | fill:silero_x2 | vad_decides:silero_x2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 46 | 26.69 | +1.93 | +0.03 | +2.10 | +1.99 | +1.60 | +3.69 | +1.03 | +0.03 | -2.58 | -0.62 |
| callfriend_eng.default | 40 | 30.80 | +1.92 | +0.37 | +1.99 | +2.54 | +0.64 | +1.38 | +1.76 | +0.40 | -1.04 | +0.97 |
| callhome_eng.default | 140 | 11.68 | +1.17 | +0.34 | +2.38 | +2.19 | +0.23 | +0.87 | +1.61 | +0.30 | +0.56 | +1.77 |
| maptask.default | 128 | 7.94 | +0.37 | +0.25 | +0.45 | +0.52 | +0.18 | +0.46 | +0.05 | +0.01 | +8.24 | +8.62 |
| msdwild_en.default | 150 | 17.79 | +2.26 | +1.59 | +2.89 | +2.46 | +0.48 | +13.56 | +0.05 | -0.12 | -0.44 | +1.85 |
| primock57.mix | 57 | 24.15 | +0.87 | +0.15 | +0.90 | +0.96 | +0.11 | +0.19 | +1.70 | +0.15 | -5.87 | -4.92 |
| voxconverse.default | 232 | 8.39 | +2.86 | +0.54 | +3.11 | +3.14 | +2.28 | +6.80 | +1.22 | +0.23 | +1.32 | +4.18 |

Primary reference, collar 0.25 s:

| tag | sessions | baseline DER % | gate:silero_x2 | gate+0.25:silero_x2 | gate:silero | gate:silero_r30 | gate:webrtc | gate:energy | gate:pyannote | gate+0.25:pyannote | fill:silero_x2 | vad_decides:silero_x2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 46 | 24.51 | +1.99 | +0.02 | +2.16 | +2.04 | +1.64 | +3.81 | +1.08 | +0.02 | -2.74 | -0.72 |
| callfriend_eng.default | 40 | 23.24 | +1.84 | +0.36 | +1.92 | +2.47 | +0.66 | +1.66 | +1.90 | +0.39 | -1.70 | +0.21 |
| callhome_eng.default | 140 | 7.23 | +1.38 | +0.24 | +2.75 | +2.25 | +0.44 | +1.12 | +1.67 | +0.21 | -0.98 | +0.42 |
| maptask.default | 128 | 1.88 | +0.18 | -0.03 | +0.23 | +0.23 | +0.16 | +0.25 | -0.09 | -0.09 | +1.44 | +1.62 |
| msdwild_en.default | 150 | 10.67 | +2.43 | +1.42 | +3.06 | +2.61 | +0.76 | +14.45 | +0.09 | -0.20 | -1.06 | +1.38 |
| primock57.mix | 57 | 15.99 | +0.83 | +0.12 | +0.86 | +0.93 | +0.11 | +0.16 | +1.47 | +0.14 | -4.58 | -3.69 |
| voxconverse.default | 232 | 5.74 | +3.16 | +0.50 | +3.42 | +3.41 | +2.59 | +7.27 | +1.32 | +0.23 | +0.73 | +3.89 |

Error components, gate with Silero (collar 0):

| tag | baseline FA / miss / conf % | gate:silero_x2 FA / miss / conf % |
|---|---|---|
| afrispeech_dialog.default | 6.44 / 15.15 / 5.10 | 6.29 / 17.37 / 4.97 |
| callfriend_eng.default | 7.90 / 18.58 / 4.32 | 7.63 / 20.93 / 4.16 |
| callhome_eng.default | 3.92 / 7.35 / 0.41 | 3.25 / 9.23 / 0.37 |
| maptask.default | 4.55 / 3.32 / 0.07 | 3.95 / 4.30 / 0.07 |
| msdwild_en.default | 3.87 / 9.55 / 4.37 | 3.23 / 12.61 / 4.22 |
| primock57.mix | 0.10 / 24.00 / 0.05 | 0.06 / 24.92 / 0.04 |
| voxconverse.default | 1.87 / 3.24 / 3.27 | 1.47 / 6.65 / 3.13 |

Protocol variants (scoring region changed; not comparable to official numbers):

| tag | official UEM h | uem_span h | uem_speech h | baseline DER % c=0 | uem_span | uem_speech |
|---|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 6.632 | 6.63 | 6.487 | 26.69 | 26.69 | 25.60 |
| callfriend_eng.default | 10.438 | 10.432 | 10.053 | 30.80 | 30.77 | 29.18 |
| callhome_eng.default | 20.296 | 20.294 | 19.912 | 11.68 | 11.68 | 11.44 |
| maptask.default | 14.31 | 14.294 | 13.334 | 7.94 | 7.94 | 7.79 |
| msdwild_en.default | 4.16 | 4.149 | 3.986 | 17.79 | 17.74 | 17.49 |
| primock57.mix | 8.635 | 8.611 | 8.349 | 24.15 | 24.14 | 23.93 |
| voxconverse.default | 43.536 | 43.164 | 41.543 | 8.39 | 8.37 | 8.25 |

### Re-inference on VAD-modified audio (sample of sessions per tag)

| tag | sessions | hours | cached DER % c=0 | re-run, same audio | trim (audio kept %) | zero | cached DER % c=0.25 | re-run | trim | zero |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| afrispeech_dialog.default | 8 | 1.11 | 17.19 | 17.19 | 17.20 (98%) | 16.98 | 15.36 | 15.36 | 15.36 | 15.14 |
| callfriend_eng.default | 5 | 1.15 | 37.37 | 37.37 | 37.83 (88%) | 38.33 | 32.93 | 32.93 | 33.50 | 34.40 |
| callhome_eng.default | 9 | 1.09 | 10.97 | 10.97 | 11.34 (95%) | 11.78 | 6.57 | 6.57 | 6.89 | 7.31 |
| chime6.farfield | 1 | 2.56 | 33.03 | 33.03 | 70.09 (28%) | 71.05 | 21.22 | 21.22 | 63.34 | 64.16 |
| maptask.default | 10 | 1.27 | 7.35 | 7.35 | 7.50 (92%) | 9.71 | 1.25 | 1.25 | 1.33 | 2.91 |
| msdwild_en.default | 28 | 1.02 | 23.43 | 23.43 | 25.27 (86%) | 27.11 | 18.01 | 18.01 | 17.83 | 19.76 |
| primock57.mix | 7 | 1.07 | 23.25 | 23.25 | 23.76 (95%) | 23.90 | 15.56 | 15.56 | 16.07 | 16.21 |
| voxconverse.default | 6 | 1.13 | 9.52 | 9.52 | 9.73 (98%) | 9.79 | 6.24 | 6.24 | 6.47 | 6.59 |

## PriMock57 per channel

```json
{
 "per_speaker_role": {
  "doctor": {
   "labelled_h": 4.817,
   "energy_activity_h": 4.106,
   "silero_h": 4.002,
   "silero_nopad_h": 3.885,
   "labelled_silero_silent_pct": 17.15,
   "labelled_silero_silent_ge0.3s_pct": 10.73,
   "labelled_energy_silent_ge0.3s_pct": 9.53,
   "silero_unlabelled_min": 0.04,
   "energy_unlabelled_min": 1.37,
   "energy_not_silero_ge0.3s_min": 7.33,
   "silero_not_energy_ge0.3s_min": 0.08
  },
  "patient": {
   "labelled_h": 3.593,
   "energy_activity_h": 2.852,
   "silero_h": 2.783,
   "silero_nopad_h": 2.676,
   "labelled_silero_silent_pct": 22.76,
   "labelled_silero_silent_ge0.3s_pct": 14.96,
   "labelled_energy_silent_ge0.3s_pct": 13.73,
   "silero_unlabelled_min": 0.1,
   "energy_unlabelled_min": 1.03,
   "energy_not_silero_ge0.3s_min": 5.37,
   "silero_not_energy_ge0.3s_min": 0.02
  }
 },
 "overlap_pct_of_speech": {
  "textgrid": 6.26,
  "energy": 3.69,
  "silero_channel": 1.34
 }
}
```

Nemotron 3 Diarization (cached, mix) against each reference:

| reference | DER % c=0 | FA | miss | DER % c=0.25 |
|---|---:|---:|---:|---:|
| primary | 24.15 | 0.10 | 24.00 | 15.99 |
| channel_activity | 10.38 | 1.12 | 9.15 | 4.08 |
| silero_channel | 10.02 | 2.11 | 7.79 | 2.74 |
| silero_channel_nopad | 9.97 | 3.69 | 6.14 | 2.78 |

