# Could Silero VAD help this project? A measured answer

Branch `vad-study`. All tables and the exact commands: [results/vad/README.md](../results/vad/README.md); the JSON
files next to it hold per-session numbers; [results/vad/worst_cases.md](../results/vad/worst_cases.md) lists the
worst sessions with their evidence. Progress log: [VAD_PROGRESS.md](../VAD_PROGRESS.md).

## Verdict

**Use Silero VAD as a cheap, independent witness for checking references and UEMs. Do not put it in the
diarization pipeline, and do not run it the stock way.**

| use | verdict | evidence (details below) |
|---|---|---|
| Finding **unannotated speech** in references | **yes**, as the first filter before a Whisper check | 70% of the longest regions Silero flags are intelligible speech and 87% have verbal content (energy VAD 42% / 68%, WebRTC 46% / 68%). Whisper-verified gaps: AMI (utterances whose manual words exist but are missing from the forced-aligned RTTM), ICSI and AMI untranscribed meeting starts/ends, Earnings-21 (12% of one call unlabelled), CallHome, CallFriend, AfriSpeech-Dialog. It flags 5-37x less music and noise than energy/WebRTC on media audio. |
| Checking **whole-file UEMs** | **yes** (new use) | Silero finds speech outside the transcribed span in 36 AMI, 6 ICSI and 5 AfriSpeech-Dialog sessions (all checked regions are real speech). On AfriSpeech-Dialog, cutting those 5 UEMs to the transcribed span lowers Nemotron's DER from 26.7% to 25.1% (false alarm 6.4% -> 4.8%). |
| A **catalog quality metric**: "% of reference speech that Silero calls silence" | **yes**, for close-talk / single-channel views | Across 26 (close-talk tag x reference) pairs it correlates with Nemotron's missed speech against the same reference (Pearson 0.74), and Silero's speech outside the reference with Nemotron's false alarms (0.86), without running a diarizer. It ranks the catalog's ground-truth grades better than energy or WebRTC (Spearman 0.56 vs 0.36 / 0.42). |
| **Boundary precision** of references | **yes**, after calibrating Silero's own bias | On tight references Silero's onsets are unbiased (median 0.00 s) and its offsets ~0.12 s late. Against that, AMI manual segments start ~0.07 s early and end ~0.11 s late, PriMock57 TextGrids start 0.24 s early and end ~0.2 s late, AfriSpeech-Dialog ends ~0.4 s early. The DER gaps between reference variants come from **pauses inside segments**, which Silero measures directly (AMI: 2.1% of the forced-aligned reference is Silero-silent vs 13-15% of the manual-derived ones; Nemotron misses 4.7% vs 24-31%). |
| **Time-shift** detection | yes | Median best lag +0.45 s on AfriSpeech-Dialog (reference early), matching the main benchmark's Nemotron-based finding; no shifted sessions in any other dataset. |
| **Per-channel references** (isolated channels, PriMock57) | **yes** | A Silero reference from each participant's own channel is more speech-specific than the energy-based one (Whisper: 22 of the 30 longest energy-only regions contain nothing but breath/noise); Nemotron DER against it 9.9% / 2.6% (collar 0 / 0.25 s) vs 10.4% / 4.1% (energy) vs 24.2% / 16.0% (TextGrids). |
| Proving that a reference **pads or labels non-speech** (individual long "silent reference" stretches) | **no, not alone** | 47% of the longest such regions are intelligible speech that Silero missed (71% have verbal content). Use the aggregate percentage as a metric, not single regions as proof. |
| **Gating** Nemotron's output with VAD speech | **no** | DER goes up on 25 of 25 evaluated subsets (Silero: +0.0 to +6.7 points on close-talk, telephone and media sets, +0.5 to +27 on far-field). Nemotron's own speech detection is better than every VAD tested; pyannote gating hurts least. |
| **Filling** Nemotron's gaps inside VAD speech | **no** | The same output gets better against padded references and worse against tight ones (AMI close-talk: -3.8 / -5.0 points vs the manual-derived references, +5.7 vs the forced-aligned one; Map Task +8.2): it imitates annotation padding. |
| Feeding Nemotron **VAD-trimmed or VAD-silenced audio** | **no** | DER worse on 22 (trim) and 21 (zero) of 25 subsets, far-field DER up to 2.1x; trimming saves only 1-22% of the audio on close-talk and telephone sets. Re-running Nemotron on unmodified audio reproduces the cached outputs exactly, so the differences are real. |
| **Deriving UEMs** from VAD speech | **no** | Cutting to the VAD speech span changes DER by <= 0.06 points except AVA-AVD (1.0); a speech-only UEM merely hides errors. Official non-trivial UEMs are reproduced within 2 s for only 60 of 126 sessions, and CHiME-6's deliberate exclusion of the enrolment minute cannot be reproduced at all. |
| **Trimming long silences** to save compute | **no** | Nemotron runs at ~1,000x real time; trimming removes speech Silero misses (far-field) and changes outputs. |
| **Far-field** audio in noisy or reverberant rooms (CHiME-6, DiPCo, EasyCom glasses, ICSI SDM) | **no** | Silero calls 45-52% of reference speech silence on CHiME-6, DiPCo and EasyCom far-field (Nemotron misses 20-31%) and 21% on ICSI SDM (Nemotron 4%); fine on NOTSOFAR-1's commercial devices (3%). pyannote segmentation-3.0 is the better witness for far-field. |

**Must-know if anyone uses Silero:** the stock streaming loop (`get_speech_timestamps`, which never resets the
model state) silently drops out on some recordings: the model outputs ~0 for minutes over clear speech (25% of
clear-speech windows on CHiME-6 far-field eval, 9% AVA-AVD, 1.9% MSDWild, 1.0% CallHome). Run it twice (stock and
with the state reset every 30 s) and take the frame-wise maximum ("Silero x2"): drop-outs fall from 0.37% to
0.065% of clear-speech windows. Recommended settings are at the end.

## The question

Hasan asked whether [Silero VAD](https://github.com/snakers4/silero-vad) is useful for this catalog of
diarization datasets, and wanted the answer from experiments. Five possible uses were tested, each against
alternatives (a simple energy VAD, WebRTC VAD, pyannote segmentation-3.0, and Nemotron's own speech activity):

1. **Ground-truth auditing**: does VAD speech missing from a reference reveal unannotated speech, and does
   reference speech with no VAD speech reveal padding or mislabelled non-speech?
2. **Boundary precision**: how tight are reference boundaries, and does that explain the DER gaps between
   reference variants of the same recordings?
3. **Diarization pipeline**: does Silero, combined with Nemotron 3 Diarization (gating its output, filling its
   gaps, feeding it trimmed or silenced audio, or deriving UEMs), lower DER/JER?
4. **Data preparation**: UEMs where datasets lack them, trimming long silences, a catalog quality metric.
5. **Baselines**: is Silero better at any of this than the cheaper or stronger alternatives?

Uses found along the way and tested too: checking whole-file UEMs, time-shift detection, per-channel references
for datasets with isolated channels, and Silero's own failure mode.

## Method

### Data

All 18 normalized datasets, every session: about 470 h on the audit views and ~1,050 h of VAD in total (including
far-field views and PriMock57's separate channels). For datasets with a close-talk view (AMI, ICSI, NOTSOFAR-1,
CHiME-6, DiPCo: `ihm-mix`; LibriCSS: `clean-mix`) the audit uses that view, because the annotations were made from
close-talk audio; the pipeline experiments use the view Nemotron was scored on. Comparisons involving pyannote or
Nemotron are restricted to the sessions the main benchmark evaluated (where those outputs exist).

### Detectors

| detector | version / settings | where it runs |
|---|---|---|
| **Silero VAD** | `silero-vad` 6.2.3 (latest on PyPI on 2026-10-05), JIT model, 16 kHz, 512-sample (32 ms) frames, package defaults, which are its documented recommendation: threshold 0.5 (exit threshold 0.35), min speech 250 ms, min silence 100 ms, 30 ms padding | CPU, 1 thread per process, 115-170x real time per process |
| **Silero x2** (main variant) | frame-wise max of the stock run and a run with the state reset every 30 s (2 s warm-up), then the same post-processing | CPU, ~60x real time per process |
| WebRTC VAD | `webrtcvad` 2.0.14, 30 ms frames, aggressiveness 2, then the same min-silence / min-speech / padding rules | CPU |
| energy VAD | this repo's `diards.vad.energy_vad` (threshold relative to the recording's noise floor), as used by `diards validate --vad` | CPU |
| pyannote | `pyannote/segmentation-3.0` VAD pipeline (pyannote.audio 4.0.7, min_duration_on/off 0 as on the model card), separate venv | GPU, ~800x real time |
| Nemotron | speaker-agnostic union of the cached Nemotron 3 Diarization output (the main benchmark) | cached |

### Audit metrics (`python -m diards.vad_audit`)

Reference speech = union of the RTTM segments inside the UEM; VAD speech likewise. Per session and dataset:

* **FA / miss**: VAD speech outside the reference, and reference speech outside VAD speech ("% of reference
  speech the VAD calls silence"), as % of reference speech, at collar 0 and outside +/- 0.25 s of reference
  boundaries.
* **unannotated**: VAD speech chunks >= 0.5 s that are more than 0.25 s from any reference speech.
* **silent reference**: reference speech chunks >= 0.5 s more than 0.25 s from any VAD speech.
* **boundary offsets**: for each reference "island" (speech separated by >= 0.3 s of silence), onset = VAD start -
  reference start, offset = reference end - VAD end; positive = the reference is wider than the VAD.
* **time shift**: lag (+/- 5 s, 50 ms raster) that maximises reference/VAD agreement (sessions >= 120 s).
* For the five longest flagged regions of each session: coverage by every other detector, by word timings and by
  Nemotron, and the level above the noise floor.

### Verification (`scripts/vad_whisper_check.py`)

For each dataset and detector, the 20 longest "unannotated" and 20 longest "silent reference" regions were
transcribed with Whisper large-v3 (GPU, ~2 min per dataset). A transcript is *speech* with the main benchmark's
criterion (>= 3 words, not a known hallucination, not repetitive), *verbal* if it also has 1-2 real words or a
filler ("yeah", "um"), *laughter*, or *none*. Words in an "unannotated" region mean the reference is missing
speech; words in a "silent reference" region mean the detector missed speech. 20 random stretches per dataset where
both the reference and Silero say non-speech are the control: 5% *speech*, 17% *verbal* (mostly Whisper
hallucinations such as "Okay."), so *speech* is a reliable signal and *verbal* a lenient one.

### Pipeline experiments (`python -m diards.vad_assist`)

Scored with the repo's `diards.score.Scorer` exactly as `diards evaluate` does (pyannote.metrics, overlap scored,
per-session UEM, collars 0 and 0.25 s half-width, primary and alternative references) on exactly the sessions of
each `results/nemotron/<tag>`. Re-scoring the cached hypotheses with this code reproduces every number in
`results/nemotron` exactly (checked on all 25 tags).

* post-hoc, all evaluated sessions: `gate` (keep hypothesis speech only inside VAD speech), `gate+0.25` (VAD
  speech dilated by 0.25 s), `fill` (inside Silero speech, frames where no speaker passes 0.5 get Nemotron's most
  probable speaker from its cached probabilities), `vad_decides` (gate + fill);
* re-inference on a deterministic ~1 h sample per tag (GPU, a few minutes in total): `trim` (Silero non-speech
  longer than 1 s shortened to 0.5 s, output mapped back to original time) and `zero` (audio outside Silero speech
  +/- 0.25 s set to digital silence). Re-running Nemotron on the unmodified audio reproduces the cached hypotheses
  exactly on all 25 tags;
* protocol variants (they change what is scored, so they are not improvements): UEM cut to the Silero speech
  span +/- 1 s (`uem_span`), or to Silero speech +/- 0.5 s (`uem_speech`).

## A Silero failure mode found on the way: drop-outs from its recurrent state

The first Whisper check on CallHome English showed that 17 of the 20 longest "reference speech that Silero calls
silence" regions were fluent, loud speech that Nemotron, WebRTC, the energy VAD and pyannote all detected. The
cause is Silero's recurrent state. `get_speech_timestamps` runs the model frame by frame and never resets the
state; on some audio the model is **bistable**: the same stretch of clear speech gets probabilities near 1 or near
0 depending on where the stream started, and the bad state can last for minutes. Per-minute speech fraction (%) on
CallHome `eng_125` (12.4 min):

| detector | min 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Silero, stock streaming | 44 | 0 | 0 | 1 | 0 | 4 | 35 | 8 | 0 | 0 | 3 | 0 | 0 |
| Silero, state reset every 30 s | 72 | 79 | 72 | 77 | 81 | 69 | 76 | 74 | 75 | 75 | 79 | 49 | 79 |
| Nemotron 3 Diarization | 80 | 81 | 72 | 77 | 80 | 69 | 78 | 74 | 77 | 75 | 77 | 81 | 77 |
| WebRTC (mode 2) | 84 | 87 | 78 | 86 | 86 | 76 | 83 | 80 | 82 | 82 | 85 | 87 | 85 |
| reference | 89 | 90 | 82 | 84 | 88 | 70 | 81 | 88 | 88 | 92 | 90 | 94 | 95 |

It is not the level, the telephone band or decoding: a fresh model state started 1-10 s apart on the same audio
gives either ~80% or ~0% speech for the same 20 s (CallHome `eng_110`, `eng_121`), and resetting every 30 s creates
new drop-outs elsewhere. On CallHome, feeding the model 8 kHz audio (its other supported rate; CallHome is
telephone audio) is also stable (1 bad window vs 77 stock), but that does not help wide-band far-field audio.

Measured on every evaluated subset (`scripts/vad_reset_check.py`): a 10 s window counts as *clear speech* when
Nemotron covers >= 50% of it and WebRTC in its strictest mode fires on >= 50% of its frames; Silero *drops out*
when its maximum probability in such a window is below 0.2.

| subset | clear-speech windows | stock | 30 s reset | **x2** (max of both) |
|---|---:|---:|---:|---:|
| CHiME-6 far-field eval | 551 | 140 (25.4%) | 44 (8.0%) | 24 (4.4%) |
| AVA-AVD (en) test+val | 220 | 20 (9.1%) | 10 (4.5%) | 9 (4.1%) |
| MSDWild (en) val | 1,346 | 25 (1.9%) | 0 | 0 |
| CHiME-6 far-field dev | 505 | 8 (1.6%) | 8 (1.6%) | 4 (0.8%) |
| CallHome English | 7,067 | 74 (1.05%) | 8 (0.11%) | 1 (0.01%) |
| SBCSAE | 5,278 | 15 (0.28%) | 20 (0.38%) | 4 (0.08%) |
| VoxConverse test | 14,537 | 11 (0.08%) | 10 (0.07%) | 10 (0.07%) |
| 18 other subsets | 50,150 | 0 | 4 | 0 |
| **all 25 subsets** | **79,654** | **0.37%** | **0.13%** | **0.065%** |

The drop-outs are concentrated in a few recordings (CHiME-6 `S01` far-field: 137 of the 140; CallHome `eng_125`,
`eng_123`; MSDWild `02508`; VoxConverse `vylyk`), but they are silent and long, so one affected session can
dominate an audit. Everything below uses Silero x2 unless marked *stock*.

## 1. Ground-truth auditing

Per dataset, primary reference, Silero x2 (tables per detector and per reference: results/vad/README.md):

| dataset | view | GT grade | ref speech h | Silero-silent reference % (c=0 / c=0.25) | unannotated % | Whisper: unannotated regions with speech | Whisper: silent-ref regions with speech |
|---|---|---|---:|---|---:|---|---|
| maptask | default | A | 9.27 | 1.8 / 0.6 | 0.62 | 3/20 (11 verbal, 8 laughter) | 8/13 |
| notsofar1 | ihm-mix | A- | 15.93 | 2.4 / 1.0 | 0.02 | 5/5 | 1/8 |
| ami | ihm-mix | A- | 66.42 | 2.1 / 0.9 | 1.29 | 20/20 | 12/20 |
| chime6 | ihm-mix | A- | 6.85 | 8.8 / 6.6 | 1.13 | 16/20 | 16/19 |
| voxconverse | default | B+ | 57.90 | 3.8 / 3.4 | 0.68 | 9/20 (singing, laughter) | 11/20 |
| icsi | ihm-mix | B | 58.80 | 8.3 / 7.2 | 0.91 | 20/20 | 11/20 |
| dipco | ihm-mix | B | 4.87 | 14.3 / 12.5 | 0.28 | 9/18 | 13/20 |
| easycom | glasses | B | 4.11 | 47.5 / 45.1 | 0.01 | - | 15/20 |
| msdwild_en | default | B | 25.78 | 2.8 / 2.1 | 0.32 | 8/20 | 17/20 |
| ava_avd_en | default | B | 3.24 | 21.6 / 18.7 | 1.40 | 7/20 | 13/20 |
| earnings21 | default | B- | 32.82 | 3.1 / 2.0 | 0.43 | 20/20 | 7/17 |
| sbcsae | default | C+ | 21.36 | 22.1 / 21.7 | 0.57 | 10/20 (6 laughter) | 10/20 |
| callhome_eng | default | C | 17.53 | 5.4 / 4.8 | 0.46 | 20/20 | 10/20 |
| scotus | default | C | 20.49 | 7.5 / 7.4 | 0.00 | - | 0/20 |
| callfriend_eng | default | C- | 9.38 | 15.5 / 14.7 | 1.65 | 20/20 | 6/20 |
| afrispeech_dialog | default | D | 6.16 | 13.9 / 13.7 | 2.59 | 19/20 | 3/20 |
| primock57 | mix | D (official) | 7.92 | 14.6 / 11.2 | 0.01 | 0/1 | 4/20 |
| libricss | clean-mix | S | 9.43 | 6.7 / 6.6 | 0.00 | - | 0/15 |

**Unannotated speech (VAD speech the reference lacks): real annotation problems, found reliably.** Over all
datasets, of the 20 longest regions per dataset each detector flags, Whisper hears intelligible speech in 70% for
Silero, 42% for the energy VAD and 46% for WebRTC (verbal content: 87% / 68% / 68%). Silero also flags far less in
total where the audio has music or noise (AVA-AVD 1.6% of reference speech vs 53-58% for energy/WebRTC;
VoxConverse 0.9% vs 4.3-5.0%; AMI 0.7% vs 5.5-6.0%). What the verified regions are:

* **AMI** (20/20 speech): utterances whose manual word timings exist but that are missing from the forced-aligned
  (MFA) RTTM, e.g. `IB4002` 193.7-198.7 s ("Because also we're going to put people together by projects...",
  word coverage 1.0, reference coverage 0), `IS1003a` 154.5 s; plus untranscribed talk before and after meetings
  (`ES2005a` 418-442 s, `TS3007d` "Welcome to the fourth meeting..." before the first reference segment at 100 s).
  The main benchmark had found MFA drop-outs in the EN2002 test meetings; Silero flags those too (EN2002b/d/a are
  among the top four of the 16 test meetings, 0.8-2.1% of their reference speech), and the largest cases are in
  train and dev meetings (up to 12.9%).
* **ICSI** (20/20): untranscribed meeting tails and heads, e.g. `Bed003`: the transcript ends at 3,499 s, the
  recording at 4,449 s, with 426 s of conversation in between ("Mushroom is not a vegetable..."); test meeting
  `Bmr013` has 67 s of pre-meeting talk ("Oh, so it's recording...") before its first segment at 92.5 s.
* **Earnings-21** (20/20): call `4384964` has unlabelled fluent speech worth 12.4% of its reference speech, also
  detected by Nemotron (e.g. 3089.7-3096.7 s, "...there's nothing planned on our end...").
* **CallHome, CallFriend** (20/20 each) and **AfriSpeech-Dialog** (19/20): missing turns, confirming the main
  benchmark's Whisper audit of Nemotron's false alarms. Energy and WebRTC find these equally well: on telephone
  audio any VAD works.
* **Not annotation errors**: laughter (Map Task, SBCSAE, VoxConverse `qlrry`), singing (VoxConverse `qvtia`, "You
  are my sunshine..."), one-word backchannels in Map Task. These follow the corpora's conventions (Map Task marks
  noises and laughter separately).
* PriMock57, NOTSOFAR-1 and LibriCSS have essentially no unannotated speech (0.00-0.03%), as expected from their
  channel- or playback-based references.

**Silent reference speech (reference speech the VAD calls silence): a good metric, a poor witness.** The
individual long regions are not proof of padding: 47% of Silero's longest "silent reference" regions are
intelligible speech that Silero missed (71% verbal), worst on noisy or far-field audio (MSDWild 17/20, CHiME-6
16/19, EasyCom 15/20). Aggregated, though, the collar-0 percentage tracks reference looseness: 1.8-2.4% on the
tightest references (Map Task, AMI MFA, NOTSOFAR-1) and 14-22% on padded or tiled ones (PriMock57 TextGrids,
AfriSpeech, CallFriend, SBCSAE); its rank correlation with the catalog's ground-truth grades is 0.56 (energy 0.36,
WebRTC 0.42). Two outliers are detector problems, not reference problems: EasyCom's glasses audio (47.5%) and
AVA-AVD's film soundtracks (21.6%), where Silero misses distant or music-covered speech.

**Time shifts.** Silero's best-lag search confirms AfriSpeech-Dialog's reference is early (median lag +0.45 s;
7 of 46 sessions shifted by >= 0.3 s with a clear gain) and finds no shifted sessions anywhere else. MSDWild clips
under 2 minutes produced spurious 3-5 s "shifts", so the check ignores sessions shorter than 120 s.

## 2. Boundary precision

Silero's own bias on the tightest references: onset median -0.01 s (Map Task word timings), 0.00 s (AMI forced
alignment), 0.00 s (PriMock57 channel activity); offset median -0.12 / -0.12 / -0.10 s (Silero ends ~0.1 s after
the speech: its 30 ms pad plus the model's hangover). Against that calibration:

| dataset | reference | onset p50 (p25 / p75) s | offset p50 (p25 / p75) s | ref speech Silero calls silence % | Nemotron miss % | Nemotron DER % |
|---|---|---|---|---:|---:|---:|
| ami | MFA (primary) | 0.00 (-0.01 / 0.02) | -0.12 (-0.18 / -0.09) | 2.1 | 4.7 | 9.2 |
| ami | only_words | 0.01 (-0.01 / 0.03) | -0.10 (-0.15 / -0.05) | 13.0 | 24.1 | 26.0 |
| ami | word_and_vocalsounds | 0.01 (-0.01 / 0.03) | -0.10 (-0.14 / -0.03) | 13.5 | 26.1 | 27.7 |
| ami | segments | 0.07 (0.03 / 0.18) | -0.01 (-0.08 / 0.12) | 15.0 | 30.5 | 31.1 |
| icsi | transcriber segments (primary) | 0.00 (-0.04 / 0.04) | -0.12 (-0.20 / -0.05) | 8.3 | 2.9 | 15.9 |
| icsi | words, gaps < 0.2 s merged | -0.01 (-0.05 / 0.02) | -0.15 (-0.24 / -0.10) | 2.8 | 0.6 | 39.4 |
| chime6 | forced-aligned (primary) | 0.02 | -0.12 | 8.8 | 16.6 | 32.8 |
| chime6 | human utterances | 0.09 | 0.07 | 15.6 | 31.6 | 37.8 |
| primock57 | TextGrids | 0.24 (0.18 / 0.29) | 0.09 (0.03 / 0.15) | 14.6 | 24.0 | 24.1 |
| primock57 | channel activity | 0.00 | -0.10 | 3.6 | 9.2 | 10.4 |
| callfriend_eng | turn bullets | 0.16 | -0.22 | 15.5 | 18.6 | 30.8 |
| afrispeech_dialog | hand-typed times | 0.09 (-0.15 / 0.34) | -0.53 (-0.77 / -0.26) | 13.9 | 15.2 | 26.7 |

* AMI's three manual-derived references have the **same** island-edge offsets as the MFA reference (within
  0.02 s at the median); only the segment-level one starts ~0.07 s earlier and ends ~0.11 s later. What separates
  them is speech-free time *inside* the reference: Silero calls 13-15% of the manual-derived references silence vs
  2.1% of MFA, matching Nemotron's 24-31% vs 4.7% missed speech. The DER gap between AMI references is pauses
  inside segments, not boundary placement.
* ICSI's word-based reference is the opposite case: tight (2.8% Silero-silent) but it drops untimed words, so
  Nemotron's error moves to false alarm (38%; Silero's speech outside it: 22.7%).
* CHiME-6's human utterances start ~0.07 s earlier and end ~0.19 s later than the forced alignment.
* PriMock57 TextGrids start 0.24 s before the speech and end ~0.2 s after it (0.09 s + Silero's 0.10 s bias).
* AfriSpeech-Dialog's ends are ~0.4 s early, with widely spread starts: the signature of its time shift.
* CallFriend's turn bullets start ~0.16 s early and end ~0.1 s early.

Across every evaluated (tag, reference) pair, how well each detector's disagreement with a reference predicts
Nemotron's error against the same reference (Pearson / Spearman; all pairs: results/vad/README.md):

| subset | Silero x2 | Silero stock | pyannote | WebRTC | energy |
|---|---|---|---|---|---|
| close-talk / single-channel (26 pairs): "calls silence" vs Nemotron miss | **0.74 / 0.71** | 0.72 / 0.73 | 0.61 / 0.67 | 0.74 / 0.70 | 0.51 / 0.59 |
| close-talk / single-channel: speech outside reference vs Nemotron FA | **0.86 / 0.89** | 0.87 / 0.90 | 0.73 / 0.83 | 0.54 / 0.72 | 0.46 / 0.66 |
| far-field (17 pairs): "calls silence" vs Nemotron miss | 0.63 / 0.73 | 0.59 / 0.68 | **0.70 / 0.78** | 0.29 / 0.27 | -0.01 / 0.18 |

So on close-talk and single-channel audio a CPU pass of Silero predicts most of how much of a diarizer's "error"
against a reference is the reference's own looseness, as well as or better than the alternatives. On far-field
audio pyannote is the better witness.

## 3. Silero in the diarization pipeline

Change in DER (points, primary reference, collar 0) relative to Nemotron alone, all evaluated sessions (all 25
tags, collar 0.25 s and alternative references: results/vad/README.md, section 3):

| tag | baseline DER % | gate Silero | gate Silero +0.25 s | gate WebRTC | gate pyannote | fill Silero | VAD decides |
|---|---:|---:|---:|---:|---:|---:|---:|
| ami.ihm-mix | 9.22 | +0.77 | +0.24 | +0.50 | +0.09 | +5.69 | +6.53 |
| ami.sdm | 11.35 | +5.58 | +3.28 | +22.41 | +0.33 | +3.74 | +9.41 |
| maptask | 7.94 | +0.37 | +0.25 | +0.18 | +0.05 | +8.24 | +8.62 |
| notsofar1.ihm-mix | 14.52 | +0.20 | +0.02 | +0.20 | +0.92 | -1.66 | -1.43 |
| notsofar1.sc | 18.41 | +0.50 | 0.00 | +0.12 | +0.77 | -1.83 | -1.30 |
| voxconverse | 8.39 | +2.86 | +0.54 | +2.28 | +1.22 | +1.32 | +4.18 |
| callhome_eng | 11.68 | +1.17 | +0.34 | +0.23 | +1.61 | +0.56 | +1.77 |
| earnings21 | 19.54 | +0.01 | -0.03 | -0.08 | -0.87 | +1.20 | +1.30 |
| icsi.ihm-mix | 15.86 | +1.09 | +0.26 | +0.43 | -0.14 | +2.26 | +3.39 |
| primock57 (TextGrids) | 24.15 | +0.87 | +0.15 | +0.11 | +1.70 | -5.87 | -4.92 |
| primock57 (channel activity) | 10.38 | +0.51 | +0.17 | +0.01 | +1.16 | +0.34 | +0.91 |
| libricss.clean-mix | 5.09 | +3.34 | +0.15 | +1.35 | +1.50 | -0.60 | +2.78 |
| ava_avd_en | 49.79 | +6.72 | +7.51 | +0.62 | -0.45 | +3.32 | +10.00 |
| chime6.farfield | 37.63 | +23.83 | +21.64 | +14.98 | +4.20 | +0.44 | +24.29 |
| dipco.farfield | 36.16 | +26.93 | +20.70 | +28.51 | +0.49 | -0.98 | +26.00 |
| easycom.glasses | 30.38 | +25.03 | +20.18 | +49.55 | +1.11 | -0.35 | +24.70 |

* **Gating never helps.** Silero gating raises DER on all 25 tags. Nemotron's false alarms are mostly unannotated
  speech and boundary overhang that every VAD also hears, so gating removes little false alarm (CallHome 3.9% ->
  3.3%) and adds more missed speech (7.4% -> 9.2%). Silero gating is worse than WebRTC or pyannote gating on most
  sets because Silero misses more speech; on far-field audio it is catastrophic. Even the gentlest version
  (+0.25 s) is at best neutral; pyannote gating is the least harmful and still not useful.
* **Filling only imitates padding.** On AMI close-talk the same filled output is 5.7 points worse against the
  forced-aligned reference and 3.8 / 5.0 points better against the manual-derived `only_words` / `segments`
  references; it helps against the PriMock57 TextGrids (-5.9) and hurts on Map Task (+8.2). It moves the output
  towards annotation habits, not towards the truth.
* **Re-inference** (sample of ~1 h per tag): trimming non-speech longer than 1 s kept 78-99% of the audio on
  close-talk and telephone sets (28-72% on CHiME-6, DiPCo, EasyCom, AMI/ICSI SDM and AVA-AVD) and raised DER on 22 of 25 tags (e.g. AMI SDM
  11.3 -> 14.5, ICSI SDM 14.6 -> 27.7, CHiME-6 far-field 33.0 -> 70.1, EasyCom 32.2 -> 58.6); zeroing non-speech
  raised it on 21 of 25. The gains were CHiME-6 close-talk (one 2.6 h session, 31.9 -> 23.9), Earnings-21 (-0.6)
  and NOTSOFAR-1 close-talk (-0.45). A single session is not evidence of a general effect, and SCOTUS shows the
  opposite instability (99% of the audio kept, DER 22.4 -> 29.6) because any change to the input moves
  Nemotron's chunk boundaries and speaker-cache decisions.
* **VAD-derived UEMs** change nothing when they only trim leading/trailing non-speech (`uem_span`: <= 0.06 points
  except AVA-AVD, 1.0), and a speech-only UEM (`uem_speech`) just stops scoring part of the errors (e.g. SBCSAE
  27.4 -> 22.4); that is a different metric, not an improvement.

## 4. Data preparation

* **Checking UEMs (useful).** A whole-file UEM is only right if the transcription covers the whole file. Silero
  speech more than 1 s outside the transcribed span (`scripts/vad_uem_check.py`): AMI 36 sessions (1,286 s;
  33 train, 3 dev), ICSI 6 (627 s; 5 train and test meeting `Bmr013`), AfriSpeech-Dialog 5 (369 s), MSDWild 1
  (15 s), none elsewhere. Every region spot-checked with Whisper is real conversation. In the benchmark this
  matters for AfriSpeech-Dialog: cutting those 5 UEMs to the transcribed span +/- 1 s lowers Nemotron's DER from
  26.69% to 25.09% (collar 0; false alarm 6.44% -> 4.84%). Nemotron happened to output nothing in `Bmr013`'s
  untranscribed head, so ICSI's numbers do not change, but another diarizer's would.
* **Writing UEMs (not useful).** No dataset needs a VAD-made UEM: where official UEMs are not the whole file they
  are either the annotated span (SBCSAE, SCOTUS, AVA-AVD: a Silero span reproduces them within 2 s at both ends
  for 20/40, 9/12 and 31/71 sessions, and on AVA-AVD would cut 208 s of annotated speech) or a deliberate
  exclusion (CHiME-6 drops the enrolment minute: 26-46 s of speech per session that no VAD can know to skip).
* **Trimming silence (not useful).** Silero non-speech in stretches longer than 1 s is 2-22% of the audio on
  close-talk, telephone and media sets (more only on AVA-AVD and EasyCom, 52-57%), and trimming it hurts
  diarization (section 3).
* **Catalog quality metrics (useful).** "% of reference speech that Silero calls silence" (collar 0, close-talk or
  single-channel view) predicts reference-induced missed speech (section 2); "unannotated Silero speech as % of
  reference speech", with a Whisper check of its longest regions, finds real missing speech (section 1); "Silero
  speech outside the transcribed span" finds bad whole-file UEMs. All three are in
  `results/vad/audit/audit.<dataset>.<view>.json` (`summary.primary.silero_x2.miss_pct`, `.unref_pct`) and
  `results/vad/uem_check.json`.

## 5. Baselines

| task | best | Silero x2 | others |
|---|---|---|---|
| precision of unannotated-speech flags (Whisper) | **Silero** | 70% speech / 87% verbal | energy 42% / 68%, WebRTC 46% / 68% (pyannote's flags were not Whisper-checked; its flagged totals are close to Silero's) |
| fewest false flags on music / noise | **Silero**, pyannote | AVA-AVD 1.6% of reference speech | pyannote 2.5%, energy 58%, WebRTC 53% |
| predicting Nemotron's reference-induced error, close-talk | **Silero** | 0.74 (miss) / 0.86 (FA) | WebRTC 0.74 / 0.54, pyannote 0.61 / 0.73, energy 0.51 / 0.46 |
| same, far-field | **pyannote** | 0.63 / 0.89 | pyannote 0.70 / 0.87; WebRTC and energy useless |
| frame accuracy vs tight references, outside +/- 0.25 s (FA / miss %) | Nemotron | AMI MFA 1.8 / 0.7, Map Task 2.3 / 0.6 | pyannote 8.2 / 0.2 and 11.8 / 0.1; WebRTC 11.6 / 0.6 and 12.5 / 0.3 |
| far-field speech detection | **pyannote**, Nemotron | calls 3-52% of reference speech silence (NOTSOFAR-1 3%, CHiME-6 / DiPCo / EasyCom 45-52%) | |
| gating Nemotron | none: all hurt | | pyannote hurts least |
| robustness | pyannote, WebRTC, energy | only with x2 | stock Silero drops out silently |
| cost | energy, WebRTC (~1,500x real time together) | ~60x real time per CPU thread (x2) | pyannote needs pyannote.audio and a GPU for speed |

## PriMock57

Silero on each participant's isolated channel (`scripts/vad_primock57_channels.py`, results/vad/primock57/):

* 10.3% (doctor) / 14.2% (patient) of TextGrid-labelled time is Silero silence in stretches >= 0.3 s; the
  energy method gave 9.5% / 13.7%. Two independent detectors agree on the padding PRIMOCK57.md describes.
* Silero finds 0.05 / 0.10 min of speech with no label nearby; the energy method 1.4 / 1.0 min. Of the 30 longest
  "energy says sound, Silero says no" regions, Whisper finds nothing in 22 (it outputs "Thank you.", its usual
  hallucination on breath and clicks), 1-2 words in 6 and speech in 2. Silero's channel reference is the more
  speech-specific one.
* Overlap (>= 2 speakers, % of speech): 6.3% TextGrids, 3.7% energy channel activity, 1.4% Silero channels.
* Nemotron 3 Diarization (cached, mix) against each reference: TextGrids 24.2% / 16.0% DER (collar 0 / 0.25 s),
  energy channel activity 10.4% / 4.1%, **Silero channel activity 9.9% / 2.6%**.

The Silero channel RTTMs (CC BY 4.0, like the dataset) are in `results/vad/primock57/silero_channel_rttm/`.

## Recommended settings

```python
import numpy as np
from diards.vads import silero_intervals, silero_probs

# x: 16 kHz mono float32 numpy array
p = np.maximum(silero_probs(x), silero_probs(x, reset_every=30.0))   # "Silero x2"
speech = silero_intervals(p, len(x))   # silero-vad 6.2.3 defaults: threshold 0.5 (exit 0.35), min speech 250 ms,
                                       # min silence 100 ms, pad 30 ms
```

* Install: `pip install --no-deps silero-vad` (needs only torch and packaging; the JIT model runs on CPU, one
  thread per process; the two passes run at ~60x real time per process).
* 16 kHz input; for 8 kHz telephone sources the 8 kHz path was also stable on CallHome.
* Expect offsets ~0.1 s late and onsets unbiased: compare with a 0.25 s collar or correct for it.
* Use the close-talk view; for far-field audio use pyannote segmentation-3.0 instead.
* Treat flagged regions as candidates and confirm them (Whisper, a second detector, or listening).

## Reproduce

Exact commands: [results/vad/README.md](../results/vad/README.md). Library code: `diards/vads.py` (detectors and
cache), `diards/vad_audit.py` (audit), `diards/vad_assist.py` (VAD-assisted scoring); scripts: `scripts/vad_*.py`;
tests: `tests/test_vad_study.py`.
