# Santa Barbara Corpus of Spoken American English (SBCSAE)

60 recordings (~20 min each, ~20 h) of naturally occurring American English from across the US: face-to-face
conversation, phone calls, classroom lectures, sermons, story-telling, business meetings. Carefully transcribed by
linguists, with every intonation unit time-stamped and overlap marked. Free, but licensed **CC BY-ND 3.0**, so
derived RTTMs may not be redistributed. This repo ships only the scripts and statistics.

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- OpenSLR [SLR155](https://www.openslr.org/155/): `SBCSAE.tar.gz` (6.2 GB: WAV, MP3, TRN and CHAT transcripts,
  docs). EU mirror `openslr.elda.org` was fastest.
- UCSB page: <https://www.linguistics.ucsb.edu/research/santa-barbara-corpus-spoken-american-english>; TalkBank
  CABank also hosts it (CHAT + media).
- LDC sells the same corpus (LDC2000S85 etc.); the free OpenSLR/UCSB version is complete.

## Annotation methodology

Du Bois et al. transcribed every speaker in discourse-transcription conventions. Intonation units (IUs) carry
millisecond time bullets, overlap is bracketed (⌈ ⌉ / ⌊ ⌋), and laughter, breaths, pauses and vocal noises are
coded. The reference here has one segment per IU that contains at least one lexical word. The environment tier
(`ENV`) and the non-human codes `X`/`MANY` are dropped.

## Known issues and errata

- IU bullets **tile the timeline**: each IU starts where the previous one ended, so leading pauses (`(..)`) are
  inside IUs. Boundaries are loose, especially at collar 0.
- Recording quality varies a lot (1980s-90s field recordings on portable equipment, some very noisy).
- Speaker sets vary from 2 to many; some recordings are lectures or sermons dominated by one speaker.
- CC BY-ND: do not publish modified annotations.

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

**B-.** Expert human transcription of every participant in truly natural talk, with overlap marked. Minus: IU-level
tiling (loose boundaries), variable audio, no-derivatives license.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

J. W. Du Bois, W. L. Chafe, C. Meyer, S. A. Thompson, R. Englebretson, N. Martey (2000-2005), Santa Barbara Corpus of Spoken American English, Parts 1-4. Philadelphia: Linguistic Data Consortium.
