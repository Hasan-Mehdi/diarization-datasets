# NOTSOFAR-1 (recorded meetings)

Microsoft's "Natural Office Talkers in Settings of Far-field Audio Recordings": ~6-minute real office meetings
in 30 rooms, 3-8 participants (35 unique speakers), each wearing a close-talk mic, recorded by many commercial
far-field devices. Released for CHiME-8 Task 2 under CC BY 4.0. It is the best free, recent, real far-field
meeting set with full ground truth, and its eval set is held out from Nemotron 3 Diarization's training data.

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- Hugging Face (not gated): [`microsoft/NOTSOFAR`](https://huggingface.co/datasets/microsoft/NOTSOFAR), folders
  `benchmark-datasets/{train,dev,eval}_set/<version>/MTG/<meeting>/`. Also on Azure blob storage
  (see <https://github.com/microsoft/NOTSOFAR1-Challenge>).
- Versions used: `240825.1_eval_full_with_GT` (129 meetings), `240825.1_dev1`, `240825.1_train`.
- Forced-alignment RTTMs (MFA) published with FastMSS (used by the Nemotron model card):
  <https://github.com/popcornell/FastMSS/tree/master/resources> (`notsofar1-sessions_mfa_rttms.tar.gz`, which covers
  dev and the 80-meeting eval_small subset).

## Annotation methodology

Participants wore close-talk mics. Transcription went through a multi-stage process designed to remove machine
bias (Vinnikov et al., Interspeech 2024). `gt_transcription.json` gives utterances with start/end times plus
**word-level timings**. Speaker aliases (e.g. "Ron") are consistent across meetings. Utterance boundaries are tight
around the words but include within-utterance pauses. `<ST/>` marks unintelligible stretches, which have no word
timing.

## Known issues and errata

- Several eval versions exist (`240629.1_eval_small_with_GT` = 80 meetings / 2 devices; `240825.1_eval_full_with_GT`
  = 129 meetings / all devices). Say which one you score.
- The `mc_rockfall_1` device is excluded from the eval sets because of suspected audio problems. Three training
  meetings had faulty white-noise recordings removed in `240825.1_train`.
- Device sets differ per room, so the `sc` view (first single-channel device listed in `devices.json`) is not the
  same physical device in every meeting.
- Horiguchi et al. (ASRU 2025) classify NOTSOFAR-1 as "ASR-oriented" (utterances include pauses). The alternative
  references `words_gap0.2` (words merged across pauses < 0.2 s) and `fastmss_mfa` let you measure the effect.

## Verified statistics

<!-- auto:stats -->
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
<!-- /auto:nemotron -->

## Quality rating

**A-.** Real meetings, everyone close-talk transcribed with a documented multi-stage process, word timings and
full overlap. Only the utterance-level boundaries (pauses inside) keep it from an A. Use `words_gap0.2` when you
need tight boundaries.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

A. Vinnikov et al., "NOTSOFAR-1 Challenge: New Datasets, Baseline, and Tasks for Distant Meeting Transcription", Interspeech 2024.
