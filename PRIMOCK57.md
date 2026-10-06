# PriMock57: how good is its ground truth for diarization?

**Short answer:** the speaker *attribution* in PriMock57 is reliable and almost all speech is transcribed, but
the *timing* is utterance-level and loose. About 10-14% of the time labelled as speech is silence, many
"utterances" contain several sentences with long pauses (607 are longer than 10 s), and the padding produces
twice as much "overlap" as there really is. Scored against the official TextGrids, NVIDIA Nemotron 3 Diarization
gets **24.2% DER** (collar 0), almost all of it "missed speech". Scored against speech activity measured on each
speaker's own isolated channel, the same output gets **10.4%** (collar 0) and **4.1%** (collar 0.25 s). Most of the
apparent error is in the reference, not the model.

The claim that PriMock57 is weak for diarization holds, with one correction: the problem is coarse, padded
timing, not missing or wrong speakers. Because the two channels are recorded separately, it can be fixed. This
repo ships tighter per-channel activity RTTMs for all 57 consultations
([`results/primock57/channel_activity_rttm/`](results/primock57/channel_activity_rttm/)).

## What PriMock57 is

57 mock GP consultations held as remote video calls (7 Babylon clinicians, 57 staff acting as patients from case
cards), about 8.6 h. The doctor and the patient were recorded on **separate channels** (16 kHz WAV from the call's
Opus streams). Transcripts are Praat TextGrids, one per channel. Per the repo README: *"The transcription is done on
an utterance level; the transcriber first identified utterances in the audio, then provided timings for the
utterance along with a transcription."* The annotation was made for ASR evaluation, not diarization.

## Method

Script: [`scripts/analyze_primock57.py`](scripts/analyze_primock57.py). Inputs: the official audio and TextGrids,
plus the Nemotron hypotheses from `python -m diards evaluate primock57`.

1. **Channel isolation.** Median frame energy (30 ms frames, 10 ms hop) on each channel while only the *other*
   speaker is labelled.
2. **Own-channel activity.** For each channel, a frame is active when its energy exceeds a threshold halfway (in
   dB) between the channel's median level inside and outside its labelled utterances. The labels set the levels
   only, never the boundaries. Then 5-frame smoothing, gaps < 0.2 s bridged, bursts < 0.1 s dropped. Because the
   channels are isolated, this is a tight measure of when each person was making sound. It also counts breaths,
   coughs and laughter, so it slightly over-counts speech.
3. TextGrid labels are compared against that activity.

## Findings (all 57 consultations)

| measurement | doctor | patient |
|---|---:|---:|
| median level of own speech | -26.5 dB | -33.3 dB |
| median level on this channel while only the *other* person speaks | -76.1 dB | -87.4 dB |
| labelled speech (TextGrid) | 4.82 h | 3.59 h |
| own-channel activity | 4.11 h | 2.85 h |
| **labelled time that is silence (>= 0.3 s stretches) on the speaker's own channel** | **9.5%** | **13.7%** |
| own-channel activity (>= 0.5 s) with no utterance within 0.25 s | 1.4 min (107 bursts) | 1.0 min (88 bursts) |
| median offset: label start before first activity | 0.17 s | 0.20 s |
| median offset: label end after last activity | 0.15 s | 0.18 s |
| utterances / utterances longer than 10 s | 3674 / 336 | 3434 / 271 |

| whole recordings | TextGrid | own-channel activity |
|---|---:|---:|
| speech (union of both speakers) | 7.92 h | 6.71 h |
| overlap (>= 2 speakers) as a fraction of speech | 6.3% | 3.7% |

What this means:

* **Channels are clean.** The other speaker is 50-55 dB down on each channel, so each channel is effectively a
  close-talk recording of one person. That is why the analysis above is possible.
* **Labels are padded and span pauses.** One label covers a whole multi-sentence utterance, including hesitation
  pauses. 9.5-13.7% of labelled time is silence on the speaker's own microphone. Worst cases (times in seconds):
  * `day5_consultation09` patient, 204.0-222.6 (18.6 s, *"Um, probably, uh, around the end of February..."*): 6.1 s of it is silent.
  * `day3_consultation10` patient, 49.2-64.7 (15.5 s): 5.5 s silent.
  * `day4_consultation05` patient, 500.1-518.9 (18.8 s): 5.4 s silent.
* **Overlap is inflated.** Padded utterance edges run into the other person's turn. The TextGrids imply 6.3%
  overlapped speech, while the channels show 3.7%. A diarizer is penalised for not reproducing overlap that did
  not happen.
* **Coverage is good.** Only about 2.4 minutes of own-channel activity in 8.6 h has no nearby label, and some of it
  is probably breathing or coughing. Speakers are never confused, because each TextGrid belongs to one channel.
* **No global misalignment.** Label boundaries sit within ~0.2 s (median) of the measured activity, so the
  TextGrids and audio are in sync. The error is granularity, not a time shift.

## Effect on a diarization benchmark

`nvidia/Nemotron-3-Diarization` (Transformers, offline 30.4 s chunking, threshold 0.5) on the doctor+patient mix,
all 57 consultations (8.64 h), overlap included, UEM = whole file
([`results/nemotron/primock57.mix/results.md`](results/nemotron/primock57.mix/results.md)):

| reference | collar | DER | FA | Miss | Confusion | JER |
|---|---:|---:|---:|---:|---:|---:|
| official TextGrid utterances | 0 | **24.15%** | 0.10% | 24.00% | 0.05% | 24.92% |
| official TextGrid utterances | 0.25 s | 15.99% | 0.07% | 15.88% | 0.04% | 15.97% |
| own-channel activity (this repo) | 0 | **10.38%** | 1.12% | 9.15% | 0.11% | 10.55% |
| own-channel activity (this repo) | 0.25 s | 4.08% | 0.04% | 4.01% | 0.03% | 3.78% |
| Silero VAD on each own channel (VAD study) | 0 | **9.85%** | 1.74% | 7.99% | 0.12% | 10.08% |
| Silero VAD on each own channel (VAD study) | 0.25 s | 2.55% | 0.60% | 1.92% | 0.03% | 2.53% |

* Against the TextGrids, almost all error is "missed speech". **79.6% of that missed time is in stretches
  where the labelled speaker's own microphone is silent for >= 0.3 s**, i.e. annotation padding and pauses.
* Speaker confusion is ~0.1% either way, and the model found 2 speakers in 48/57 calls (84%). The model has no
  real trouble with this data; the reference does.
* Against the channel activity, the remaining 9% miss is partly short sounds (5 min inside bursts under 0.5 s,
  often breaths or backchannels) and partly edges of longer bursts (23 min). Some of that is a real model
  limitation, some is the activity measure counting non-speech sounds.

## Recommendations

* Do not use the PriMock57 TextGrids at collar 0 to judge a diarizer. Even at collar 0.25 s they add roughly 12
  points of DER that are not model error.
* If you need PriMock57 (it is still the best free English doctor-patient audio), use the doctor+patient mix with
  a **channel-based reference** from this repo: preferably the Silero per-channel RTTMs from the follow-up VAD study
  (`rttm_alt/silero_channel`; [results/vad/primock57/silero_channel_rttm/](results/vad/primock57/silero_channel_rttm/)),
  which ignore breaths and noise that the energy-based `channel_activity` counts (Whisper: 22 of the 30 longest
  energy-only regions are breath/noise). Keep the TextGrids for ASR and word-level work.
* For truly human-annotated, diarization-grade references in a two-party setting, see the catalog in the
  [README](README.md) (Map Task, CallHome/CallFriend, AMI/NOTSOFAR close-talk-derived references).

Reproduce:

```bash
python -m diards prepare primock57
python -m diards evaluate primock57 --out results/nemotron/primock57.mix
python scripts/analyze_primock57.py --hyp-dir <work>/nemotron/primock57.mix/hyp
```
