# AfriSpeech-Dialog v1

Intron Health's African-accented English conversations (Nigeria, Kenya, South Africa; 11 accents): 20 simulated
doctor-patient consultations and 29 general-topic conversations (~7 h), recorded remotely. It is one of very few
free *medical-like* two-party English datasets with speaker turns. **The timestamps are weak**: hand-typed, about
1 s effective precision, and missing in a few files.

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- Hugging Face (not gated): [`intronhealth/afrispeech-dialog`](https://huggingface.co/datasets/intronhealth/afrispeech-dialog),
  CC BY-NC-SA 4.0: `data/*.wav` + `metadata.csv` (transcript with embedded times, domain, accent, country).
- Paper: Sanni et al., NAACL 2025 (arXiv:2502.03945). Diarization study: arXiv:2509.21554.

## Annotation methodology

Professional annotators transcribed each conversation and typed a start and end time around every speaker turn,
as `MM:SS:cc` lines before and after `[Speaker N]: text`.

## Known issues and errata

- **Coarse, hand-typed times.** The hundredths field is almost always 96-100 or 00-04 (e.g. `00:06:100`), so the
  times are effectively whole seconds with jitter. A negative value (`00:00:-1`) also occurs.
- **3 of 49 conversations have no timestamps** (46 usable; the card claims 30 timestamped files, 9 medical + 21
  general, but 46 parse in the current release).
- Some general conversations have very few, very long turns (e.g. 5 turns in 6 minutes), so the other speaker's
  backchannels are not separately labelled.
- Overlap is essentially not annotated (0.1% of speech).
- Remote recordings, varying quality.

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

**D+.** Valuable domain (medical consultations, African accents), but timestamps at ~1 s precision, missing
overlap/backchannels, and long merged turns make it unsuitable for precise DER. Use it for speaker-attributed ASR or
coarse turn-level checks, or re-time it (e.g. forced alignment of the transcripts) before scoring diarization.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

M. Sanni et al., "Afrispeech-Dialog: A Benchmark Dataset for Spontaneous English Conversations in Healthcare and Beyond", NAACL 2025.
