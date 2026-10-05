# AMI Meeting Corpus

About 100 h of English meetings (mostly role-played design meetings, plus some natural ones) with 3-5
participants, recorded in three instrumented rooms with headsets and far-field arrays. Every participant is
transcribed at word level, so all speech is covered, overlap and backchannels included. It is the standard
free meeting benchmark. The thing to watch is **which reference you score against**: the choice moves DER by
about a factor of two (see below).

<!-- auto:meta -->
<!-- /auto:meta -->

## Source and access

- Audio: <https://groups.inf.ed.ac.uk/ami/corpus/> (per-meeting WAV files on the Edinburgh mirror, no registration).
  This repo uses `Array1-01.wav` (single distant mic) and `Mix-Headset.wav` (official close-talk mix).
- Manual annotations v1.6.2: `ami_public_manual_1.6.2.zip` (NXT XML: words with timings, transcriber segments).
- Diarization references (all free, all derived from the same manual transcripts):
  - **Forced alignment (MFA v3)**: <https://github.com/nttcslab-sp/diar-forced-alignment> (Horiguchi et al., ASRU 2025).
    Also used by NVIDIA for the Nemotron 3 Diarization model card. **Primary reference here.**
  - **BUT `only_words` / `word_and_vocalsounds`**: <https://github.com/BUTSpeechFIT/AMI-diarization-setup>
    (pyannote fork: <https://github.com/pyannote/AMI-diarization-setup>). Built from the word timings in the manual
    annotation, Full-corpus-ASR partition. The standard reference in most papers since 2021.
  - Transcriber `segments` from the NXT annotation: loose, ASR-oriented boundaries (kept as `rttm_alt/segments`).
- Hugging Face mirrors: `diarizers-community/ami` (audio + segments), `edinburghcstr/ami` (ASR version).
- Lhotse recipe: `lhotse.recipes.prepare_ami` (uses the NXT segments, not the diarization setups above).

## Annotation methodology

Transcribers segmented and transcribed each headset channel. Word timings in the public release come from
**automatic forced alignment** of those transcripts (the release README says so and lists failures). The BUT setup
turns words into speech turns: adjacent words of a speaker are merged, pauses are never bridged, vocal sounds are
excluded in `only_words` because their marking is inconsistent. The NTT setup re-aligns the same transcripts with
the Montreal Forced Aligner v3 (English MFA acoustic model and dictionary v3.1.0, G2P for OOVs), giving tighter
word boundaries and excluding inter-word silences.

## Known issues and errata

- The AMI release notes say timings are **incomplete or incorrect for EN2002a, EN2002c, EN2003a and TS3009c
  (channel 3)**. EN2002a and EN2002c are in the **test** split.
- Original word timings can absorb pauses. For example, the word "meetings" in EN2002a speaker A runs from
  3.16 s to 6.65 s.
- A few meetings lack some streams on the mirror (e.g. IS1003b, IS1007d have no `Array1-01.wav`). Those sessions
  are skipped for the `sdm` view and kept for `ihm-mix`.
- Two "official" partitions exist (Full-corpus-ASR, used here, and the older diarization partition). Results from
  different partitions are not comparable.
- References: Horiguchi et al. (ASRU 2025) measured a **21-25% DER gap** between AMI's original segment-level
  labels and forced-aligned labels, mostly from pauses labelled as speech.

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

**A-.** Close-talk transcription of every participant gives complete coverage with overlap and backchannels. The
MFA reference makes the timing diarization-grade. Points off for the forced-alignment origin of all timings (no
human-placed boundaries), the four meetings with known timing failures, and role-played meetings that are more
orderly than real ones.

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

Alternative references are in `rttm_alt/{only_words,word_and_vocalsounds,segments}/` and are scored
automatically by `diards evaluate`.

## Citation

- J. Carletta et al., "The AMI Meeting Corpus: A Pre-announcement", MLMI 2005.
- S. Horiguchi et al., "Can We Really Repurpose Multi-Speaker ASR Corpus for Speaker Diarization?", ASRU 2025.
- F. Landini et al., "Bayesian HMM clustering of x-vector sequences (VBx) in speaker diarization", CSL 2022 (BUT setup).
