# AMI Meeting Corpus

About 100 h of English meetings (mostly role-played design meetings, plus some natural ones) with 3-5
participants, recorded in three instrumented rooms with headsets and far-field arrays. Every participant is
transcribed at word level, so all speech is covered, overlap and backchannels included. It is the standard
free meeting benchmark. The thing to watch is **which reference you score against**: the choice moves DER by
about a factor of two (see below).

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-4.0 ([link](https://creativecommons.org/licenses/by/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free download, no registration. |
| Source version used | AMI manual annotations 1.6.2; BUT AMI-diarization-setup (git HEAD); nttcslab diar-forced-alignment (git HEAD) |
| Domain | meetings |
| Views (normalized) | `sdm`: Single distant microphone (Array1-01, 16 kHz); `ihm-mix`: Official Mix-Headset (sum of individual headset microphones) |
| Reference used as primary RTTM | Forced alignment (MFA v3) of the manual transcripts (primary); manual-annotation-derived alternatives in rttm_alt/. |
| Ground-truth rating | **A-** - Manual word-level transcripts of every participant (close-talk), so all speech including overlap and backchannels is covered; boundaries come from forced alignment (tight with MFA, looser in the original release). Known timing problems in EN2002a, EN2002c, EN2003a, TS3009c. |
| Prepared splits (sessions) | dev: 18, test: 16, train: 134 |
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
- **The MFA reference drops some utterances.** Measured here: across all meetings only 1.0% of the `only_words`
  speech lies in stretches of >= 2 s with no MFA speech of the same speaker nearby, so MFA mostly *tightens*
  boundaries (it labels 20-35% less speech time than `only_words` in many meetings). But in the EN2002 test meetings
  whole utterances are missing: EN2002d 5.3%, EN2002b 4.7%, EN2002a 2.7%, EN2002c 1.6% of `only_words` speech
  (e.g. EN2002b, MEE073, 48.3-62.3 s). These are the meetings the AMI release already flags for bad timings.
- The words JSONL comes from the original v1.6.2 alignment, which is looser than MFA: 15-29% of word time lies
  outside the MFA segments of the same speaker (the validator's `words_outside_reference` warning). This is
  expected and is why both references are shipped.
- References: Horiguchi et al. (ASRU 2025) measured a **21-25% DER gap** between AMI's original segment-level
  labels and forced-aligned labels, mostly from pauses labelled as speech.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| dev | 18 | 9.67 | 6.45 | 0.668 | 0.119 | 0.012 | 4/4/4 | 0.2/1.05/4.53 | 0.0495 | 1.078 | 17.07 |
| test | 16 | 9.06 | 5.97 | 0.659 | 0.102 | 0.0112 | 3/4/4 | 0.19/0.89/4.19 | 0.0553 | 0.97 | 17.52 |
| train | 134 | 79.65 | 53.33 | 0.669 | 0.103 | 0.0086 | 3/4/5 | 0.2/0.97/4.08 | 0.0479 | 0.94 | 17.11 |
| ALL | 168 | 98.38 | 65.75 | 0.668 | 0.104 | 0.0092 | 3/4/5 | 0.2/0.97/4.13 | 0.0488 | 0.96 | 17.14 |

Computed by `python -m diards stats ami` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.ami.md`](../../results/stats/stats.ami.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `ihm-mix`: 170 sessions, **0 errors**, 263 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- checks that fired (sessions): `info:segments_under_50ms` 157, `info:silence_over_30s` 113, `warning:possible_unannotated_speech` 93, `warning:words_outside_reference` 170
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 5.7% of reference speech; reference speech without energy = 0.2%. Most-flagged sessions: `ami__ES2005a` (0.50), `ami__IS1003a` (0.35), `ami__TS3010a` (0.32), `ami__ES2013a` (0.24), `ami__ES2005d` (0.24)
- full report: [`results/validation/validation.ami.ihm-mix.md`](../../results/validation/validation.ami.ihm-mix.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| ihm-mix (test) | 16 | 9.06 | primary | **9.22** | 3.66 | 4.68 | 0.88 | 12.89 | 3.56 | 88% |
| ihm-mix (test) | 16 | 9.06 | only_words | **25.96** | 1.17 | 24.05 | 0.74 | 28.24 | 24.07 | 88% |
| ihm-mix (test) | 16 | 9.06 | segments | **31.13** | 0.25 | 30.49 | 0.39 | 34.16 | 25.74 | 88% |
| ihm-mix (test) | 16 | 9.06 | word_and_vocalsounds | **27.74** | 1.01 | 26.07 | 0.67 | 30.70 | 24.82 | 88% |
| sdm (test) | 16 | 9.06 | primary | **11.35** | 4.12 | 5.86 | 1.38 | 15.03 | 4.73 | 88% |
| sdm (test) | 16 | 9.06 | only_words | **27.45** | 1.47 | 24.91 | 1.07 | 29.52 | 25.13 | 88% |
| sdm (test) | 16 | 9.06 | segments | **32.52** | 0.50 | 31.25 | 0.77 | 35.38 | 26.98 | 88% |
| sdm (test) | 16 | 9.06 | word_and_vocalsounds | **29.22** | 1.28 | 26.89 | 1.04 | 32.03 | 25.92 | 88% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/ami.*/results.md`.

> **Training-data overlap:** AMI train+dev were used for training; the test split scored here is held out.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ihm-mix | ihm-mix | 16 | 2.49 | 0.3 | 2.19 | 2.59 | 1.46 | 1.12 |
| sdm | ihm-mix | 16 | 3.41 | 0.37 | 3.04 | 2.99 | 1.5 | 1.49 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (sdm):** 14 of 16 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (21.2 of 24.2 s). Examples: `ami__EN2002b` 279.8-282.6 s: "When I go to bed at like 1, you're still online."; `ami__IS1009c` 225.9-228.0 s: "interesting feature that it would have maybe"; `ami__EN2002b` 49.3-51.1 s: "which I guess first thing just sort of did it."

**Time-offset check (sdm):** 0 of 16 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.0 s.
<!-- /auto:diagnosis -->

**Reading the AMI numbers.** On the SDM test set Nemotron scores 11.3% DER against the MFA reference, close to
published numbers for this model and protocol. Against BUT `only_words` it scores 27.5%, and against the
transcriber segments 32.5%. Almost all of the difference is *missed speech* that persists at collar 0.25 s (about
24%): the looser references label ~28% more speaker time (8.5 h vs 6.7 h), mostly pauses absorbed into words and
turns. This is a **reference-convention effect, not model error**, and it matches the 21-25% gap Horiguchi et al.
report. Note that Nemotron was trained on forced-aligned AMI labels, so it has learned the tight convention: a
model trained on `only_words`-style labels would show the opposite pattern. Always state which AMI reference you
score against.

**Independent confirmation of the dropped MFA utterances.** Whisper finds intelligible speech in 14 of the 16
longest audible "false alarms" on the SDM test set. Six of them are in EN2002a/b, e.g. EN2002b 49.3-51.1 s
(*"which I guess first thing just sort of did it"*), which lies inside the 48.3-62.3 s stretch that the MFA reference
lost. The total is small (about 21 s in 9 h), so the MFA reference is still the right primary reference, but these
are reference errors, not model false alarms.


## Quality rating

**A-.** Close-talk transcription of every participant gives complete coverage with overlap and backchannels. The
MFA reference makes the timing diarization-grade. Points off for the forced-alignment origin of all timings (no
human-placed boundaries), the four meetings with known timing failures, and role-played meetings that are more
orderly than real ones.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare ami            # download (resumable) + normalize (idempotent)
python -m diards validate ami --vad     # ground-truth checks
python -m diards stats ami
python -m diards export ami --format nemo      # or pyannote / lhotse
python -m diards evaluate ami --view sdm  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("ami", view="sdm"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

Alternative references are in `rttm_alt/{only_words,word_and_vocalsounds,segments}/` and are scored
automatically by `diards evaluate`.

## Citation

- J. Carletta et al., "The AMI Meeting Corpus: A Pre-announcement", MLMI 2005.
- S. Horiguchi et al., "Can We Really Repurpose Multi-Speaker ASR Corpus for Speaker Diarization?", ASRU 2025.
- F. Landini et al., "Bayesian HMM clustering of x-vector sequences (VBx) in speaker diarization", CSL 2022 (BUT setup).
