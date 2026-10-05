# CallFriend English (TalkBank version)

Telephone calls between friends and family within North America (LDC CallFriend American English, North and
Southern dialects), as transcribed and time-bulleted in TalkBank's CABank: 40 calls, ~10 h, 2-4 labelled speakers.
Same family and format as CallHome English, but **not gated** on Hugging Face.

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- Hugging Face: [`talkbank/callfriend`](https://huggingface.co/datasets/talkbank/callfriend), configs `eng-n`
  (31 calls) and `eng-s` (9 calls). Not gated. The card states no license; TalkBank's ground rules apply (research
  use, cite the corpus).
- TalkBank: <https://ca.talkbank.org/access/CallFriend/>.

## Annotation methodology

TalkBank CHAT transcripts with one time bullet per utterance (turn), produced by TalkBank/LDC transcribers; the HF
conversion keeps the bulleted turns. Bullets are typically contiguous: one turn ends where the next begins, so
silences are absorbed into turns.

## Known issues and errata

- **3,074 same-speaker overlapping bullets** in the original labels (our validator counts them before
  normalization merges them). Consecutive bullets of one speaker often overlap slightly.
- Contiguous bullets (tiling) mean short pauses and gaps are labelled as speech.
- One recording has a placeholder-like speaker code (flagged by the validator).
- Speaker codes such as `S1/S2/S3` or initials are per call. Global speaker identities are not given.

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

## Quality rating

**C.** Human turn-level transcription of natural phone calls, but tiled bullets and many same-speaker overlaps
make boundaries loose. Useful as an ungated, free stand-in for CallHome at collar 0.25 s.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

A. Canavan, G. Zipperlen, CALLFRIEND American English (North / South) LDC96S46/LDC96S47; TalkBank CABank CallFriend corpus.
