# PriMock57

57 mock primary-care consultations held as remote video calls (7 Babylon clinicians, 57 staff acting as patients
from case cards), ~8.6 h, with doctor and patient on **separate channels**. Released for ASR and note-generation
research. **Full ground-truth audit: [PRIMOCK57.md](../../PRIMOCK57.md).** In short, the official utterance
timings are padded and ASR-oriented, but the clean separate channels let us derive a much tighter reference.

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- <https://github.com/babylonhealth/primock57> (CC BY 4.0). Audio in Git LFS (`audio/<consultation>_{doctor,patient}.wav`,
  16 kHz); also downloadable per file from `media.githubusercontent.com`. Transcripts: `transcripts/*.TextGrid`.

## Annotation methodology

Per the repo: "The transcription is done on an utterance level; the transcriber first identified utterances in the
audio, then provided timings for the utterance along with a transcription." There is one Praat tier per channel.
Tags: `<UNSURE>`, `<UNIN/>`.

This repo adds `rttm_alt/channel_activity`: when each person is actually making sound, measured on their own
channel (the channels are isolated by ~50 dB). The same RTTMs are published under
[`results/primock57/channel_activity_rttm/`](../../results/primock57/channel_activity_rttm/) (CC BY 4.0 allows it).

## Known issues and errata (measured, see PRIMOCK57.md)

- 9.5% (doctor) / 13.7% (patient) of labelled time is silence of >= 0.3 s on the speaker's own channel.
- 607 utterances are longer than 10 s, up to 27 s, often several sentences with long pauses.
- Overlap is inflated: 6.3% of speech per the TextGrids vs 3.7% measured on the channels.
- Coverage and speaker attribution are good: only ~2.4 min of unlabelled own-channel activity in 8.6 h.

## Verified statistics

<!-- auto:stats -->
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
<!-- /auto:diagnosis -->

Against the official TextGrids almost all error is "missed speech", and 80% of it falls where the labelled
speaker's own microphone is silent. Against the channel-activity reference the DER drops from 24.2% to 10.4%
(collar 0). The model is fine here; the reference is the problem.

## Quality rating

**D** for the official TextGrids as a diarization reference (padded utterances, inflated overlap). **B** with the
channel-activity reference from this repo (automatic, but measured on isolated close-talk channels; counts breaths
and coughs too).

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

A. Papadopoulos Korfiatis, F. Moramarco, R. Sarac, A. Savkov, "PriMock57: A Dataset Of Primary Care Mock Consultations", ACL 2022.
