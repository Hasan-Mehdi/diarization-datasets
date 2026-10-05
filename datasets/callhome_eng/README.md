# CallHome American English (TalkBank version)

Unscripted telephone calls between family members and friends, mostly from the US to relatives abroad, collected
by the LDC in 1996-97 (LDC97S42 / LDC97T14). TalkBank's CABank distributes the transcribed excerpts (5-10 min of
each call) with CHAT time bullets, and TalkBank published them on Hugging Face. This is the only *free* route to
CallHome English. The LDC packages cost money.

Not to be confused with the "CALLHOME" diarization benchmark (NIST SRE 2000 Disk 8, multilingual, LDC-only).

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-NC-SA-4.0 ([link](https://creativecommons.org/licenses/by-nc-sa/4.0/)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free, gated on Hugging Face (click-through form asking company + country). |
| Source version used | huggingface.co/datasets/talkbank/callhome (config eng) |
| Domain | telephone (2+ speakers) |
| Views (normalized) | `default`: Telephone audio (both channels summed), 8 kHz source upsampled to 16 kHz |
| Reference used as primary RTTM | LDC transcripts re-formatted by TalkBank (CHAT), per-turn time bullets. |
| Ground-truth rating | **C+** - Human transcription with turn-level bullets; see dataset card for measured boundary quality. |
| Prepared splits (sessions) | data: 140 |
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
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| data | 140 | 20.3 | 17.53 | 0.863 | 0.09 | 0.0001 | 2/2/4 | 0.29/1.42/5.93 | 0.017 | 1.08 | 19.56 |
| ALL | 140 | 20.3 | 17.53 | 0.863 | 0.09 | 0.0001 | 2/2/4 | 0.29/1.42/5.93 | 0.017 | 1.08 | 19.56 |

Computed by `python -m diards stats callhome_eng` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.callhome_eng.md`](../../results/stats/stats.callhome_eng.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 140 sessions, **0 errors**, 3 warnings (normalized files); 23 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: same_speaker_overlap = 30
- checks that fired (sessions): `info:segments_under_50ms` 17, `info:silence_over_30s` 2, `info:speaker_under_1s` 4, `warning:possible_unannotated_speech` 3
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 0.6% of reference speech; reference speech without energy = 0.8%. Most-flagged sessions: `callhome_eng__eng_037` (0.32), `callhome_eng__eng_011` (0.08), `callhome_eng__eng_099` (0.06), `callhome_eng__eng_013` (0.03), `callhome_eng__eng_072` (0.03)
- full report: [`results/validation/validation.callhome_eng.default.md`](../../results/validation/validation.callhome_eng.default.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (data) | 140 | 20.3 | primary | **11.68** | 3.92 | 7.35 | 0.41 | 15.29 | 7.23 | 93% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/callhome_eng.*/results.md`.

> **Training-data overlap:** The model was trained on NIST SRE 2000 CALLHOME part 1, which contains CallHome calls in several languages; overlap with these CallHome English calls cannot be ruled out.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 140 | 5.17 | 2.42 | 2.75 | 2.53 | 0.98 | 1.56 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 38 of 40 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (92.2 of 94.7 s). Examples: `callhome_eng__eng_013` 44.9-50.3 s: "They said he doesn't want to start working because you didn't tell him exactly e"; `callhome_eng__eng_073` 603.6-607.2 s: "See, I should have planned to arrive on the same day that you arrived."; `callhome_eng__eng_047` 202.2-205.7 s: "and the barges go so slowly that like you can get off at a bridge"

**Time-offset check (default):** 0 of 140 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.0 s.
<!-- /auto:diagnosis -->

**Missing turns in the TalkBank / HF version (annotation error, verified).** The model's longest audible "false
alarms" were transcribed with Whisper: **38 of the 40 longest regions contain clear speech** that has no label at
all in the reference, for example `eng_037` 380.4-383.7 s *"It's really interesting. It's University of
Pennsylvania."* and `eng_076` 452.0-454.9 s *"How much does a hamburger cost at Burger King, do you know?"*. In
`eng_037` about 121 s of audible speech is unlabelled (32% of its reference speech; the energy-VAD check flags the
same file). At least 12 calls are affected. So part of the 3.9% false alarm is reference error. The overall DER
(11.7% at collar 0, 7.2% at 0.25 s) is in line with the model card's CALLHOME results (9.1% at 0.25 s), so the bulk
of the data is usable. Drop or re-check the flagged calls (see `results/diagnosis/fa_audit.callhome_eng.default.json`).


## Quality rating

**C+.** Human transcripts of natural telephone conversation (a classic benchmark domain), but turn-level bullets
with loose boundaries and spotty backchannel coverage. Fine at collar 0.25 s, weak at collar 0.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare callhome_eng            # download (resumable) + normalize (idempotent)
python -m diards validate callhome_eng --vad     # ground-truth checks
python -m diards stats callhome_eng
python -m diards export callhome_eng --format nemo      # or pyannote / lhotse
python -m diards evaluate callhome_eng --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("callhome_eng", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

- A. Canavan, D. Graff, G. Zipperlen, CALLHOME American English Speech, LDC97S42, 1997.
- Linguistic Data Consortium (2008), CABank English CallHome Corpus, TalkBank, doi:10.21415/T5KP54.
