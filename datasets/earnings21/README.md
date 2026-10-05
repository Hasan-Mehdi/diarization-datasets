# Earnings-21

44 public earnings calls from 2020 (39 h, nine sectors), released by Rev.com for ASR benchmarking. Speakers are
an operator, company executives and sell-side analysts on the phone. Rev added RTTMs in 2023, so it can serve as
a long-form, many-speaker "business call" diarization test with almost no overlap.

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- <https://github.com/revdotcom/speech-datasets/tree/main/earnings21> (CC BY-SA 4.0): `media/*.mp3`,
  `transcripts/nlp_references/*.nlp` (token + speaker), `rttms/*.rttm`, `eval10-file-metadata.csv`.
- HF mirror: [`argmaxinc/earnings21`](https://huggingface.co/datasets/argmaxinc/earnings21). Lhotse recipe: `lhotse.recipes.prepare_earnings21`.
- Earnings-22 (125 calls, 119 h, global accents) has no RTTMs and no token timings, so it is not usable for
  diarization scoring without your own alignment.

## Annotation methodology

Professional Rev transcriptionists transcribed each call and senior transcriptionists reviewed it. The `.nlp` files
carry a speaker index per token but **no timestamps**. The 2023 RTTMs give segment timings; Rev does not document how
they were produced (most likely forced alignment of the human transcripts). Release 202408 fixed an off-by-one
speaker-labelling issue in file 4341191.

## Known issues and errata

- Timing method undocumented (see above).
- Calls contain long hold music or operator instructions, and Q&A over phone lines of varying quality.
- Nearly no overlap is labelled; backchannels and crosstalk tend to be absent.
- Split: Rev's `eval10` subset (10 files) plus the remaining 34 (`other`). There is no train/test split.

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

**B-.** Careful human transcripts and speaker labels on long real calls with many speakers (up to ~14). The
segment timing is of unknown provenance and overlap/backchannels are essentially absent, so it tests speaker
counting and long-form tracking more than overlap handling.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

M. Del Rio et al., "Earnings-21: A Practical Benchmark for ASR in the Wild", Interspeech 2021.
