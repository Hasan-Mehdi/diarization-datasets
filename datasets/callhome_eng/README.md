# CallHome American English (TalkBank version)

Unscripted telephone calls between family members and friends, mostly from the US to relatives abroad, collected
by the LDC in 1996-97 (LDC97S42 / LDC97T14). TalkBank's CABank distributes the transcribed excerpts (5-10 min of
each call) with CHAT time bullets, and TalkBank published them on Hugging Face. This is the only *free* route to
CallHome English. The LDC packages cost money.

Not to be confused with the "CALLHOME" diarization benchmark (NIST SRE 2000 Disk 8, multilingual, LDC-only).

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- Hugging Face: [`talkbank/callhome`](https://huggingface.co/datasets/talkbank/callhome), config `eng` (140 rows,
  2.3 GB parquet). Gated with automatic approval: log in, open the page, accept (the form asks for company and
  country). CC BY-NC-SA 4.0 per the card.
- TalkBank page: <https://ca.talkbank.org/access/CallHome/eng.html> (transcripts and media need a TalkBank login).
- The HF conversion (made with the `diarizers` scripts) keeps only the transcribed part of each call, as 16 kHz
  audio with per-turn `timestamps_start/end` and speaker codes. Original file names are not preserved, so sessions
  are named `eng_<row>`.

## Annotation methodology

LDC transcribers produced turn-level transcripts of a contiguous 5- or 10-minute excerpt of each call. TalkBank
converted them to CHAT, with one time bullet per utterance. Speakers are the callers on either end; sometimes
several people share a handset, so a "two-party" call can have 3-4 labelled speakers. Overlap appears where
bullets of different speakers overlap. Bullets come from the original turn-level timestamps, not from forced
alignment.

## Known issues and errata

- Turn-level (not word-level) timing. Short backchannels are often folded into the other speaker's turn or left
  unlabelled. See the validation section for measured coverage.
- Telephone band (8 kHz source), both channels summed in the HF version.
- **Possible training-data overlap** with diarizers trained on NIST SRE 2000 CALLHOME (Nemotron 3 Diarization uses
  CALLHOME part 1); the SRE set draws on CallHome calls in several languages.
- The excerpt boundaries are the transcription boundaries. Audio outside them is cut in the HF version, so
  nothing unlabelled is left at the edges.

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

**C+.** Human transcripts of natural telephone conversation (a classic benchmark domain), but turn-level bullets
with loose boundaries and spotty backchannel coverage. Fine at collar 0.25 s, weak at collar 0.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

- A. Canavan, D. Graff, G. Zipperlen, CALLHOME American English Speech, LDC97S42, 1997.
- Linguistic Data Consortium (2008), CABank English CallHome Corpus, TalkBank, doi:10.21415/T5KP54.
