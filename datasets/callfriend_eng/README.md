# CallFriend English (TalkBank version)

Telephone calls between friends and family within North America (LDC CallFriend American English, North and
Southern dialects), as transcribed and time-bulleted in TalkBank's CABank: 40 calls, ~10 h, 2-4 labelled speakers.
Same family and format as CallHome English, but **not gated** on Hugging Face.

<!-- auto:meta -->
| | |
|---|---|
| License | TalkBank ground rules (research, cite); HF card states no license ([link](https://talkbank.org/share/rules.html)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free on Hugging Face (not gated). |
| Source version used | huggingface.co/datasets/talkbank/callfriend (configs eng-n, eng-s) |
| Domain | telephone (2+ speakers) |
| Views (normalized) | `default`: Telephone audio (channels summed), 16 kHz |
| Reference used as primary RTTM | TalkBank CHAT transcripts with per-turn time bullets. |
| Ground-truth rating | **C** - Human transcription with turn-level bullets; see dataset card for measured boundary quality. |
| Prepared splits (sessions) | data: 40 |
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
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| data | 40 | 10.44 | 9.38 | 0.899 | 0.07 | 0.0 | 2/2/4 | 0.312/1.312/6.144 | 0.0098 | 0.974 | 20.17 |
| ALL | 40 | 10.44 | 9.38 | 0.899 | 0.07 | 0.0 | 2/2/4 | 0.312/1.312/6.144 | 0.0098 | 0.974 | 20.17 |

Computed by `python -m diards stats callfriend_eng` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.callfriend_eng.md`](../../results/stats/stats.callfriend_eng.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `default`: 40 sessions, **1 errors**, 4 warnings (normalized files); 32 sessions had problems in the ORIGINAL labels that normalization fixed.
- original-label issues: same_speaker_overlap = 3074, beyond_audio_end = 5, seconds_beyond_audio_end = 0.34, placeholder_speaker_label = 1
- checks that fired (sessions): `error:normalized_placeholder_speaker_label` 1, `info:segments_under_50ms` 2, `info:silence_over_30s` 1, `info:speaker_under_1s` 1, `warning:possible_unannotated_speech` 3, `warning:segments_over_60s` 1
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 1.7% of reference speech; reference speech without energy = 5.0%. Most-flagged sessions: `callfriend_eng__eng-n_002` (0.18), `callfriend_eng__eng-s_001` (0.14), `callfriend_eng__eng-n_027` (0.05), `callfriend_eng__eng-n_004` (0.04), `callfriend_eng__eng-n_028` (0.03)
- full report: [`results/validation/validation.callfriend_eng.default.md`](../../results/validation/validation.callfriend_eng.default.md)
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| default (data) | 40 | 10.44 | primary | **30.80** | 7.90 | 18.58 | 4.32 | 38.29 | 23.24 | 75% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/callfriend_eng.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default | default | 40 | 16.0 | 11.65 | 4.36 | 5.04 | 3.36 | 1.67 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (default):** 39 of 40 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (91.8 of 93.7 s). Examples: `callfriend_eng__eng-n_026` 264.6-268.8 s: "You know when Reagan says something stupid, people turn it to disapprove, and wh"; `callfriend_eng__eng-s_001` 45.1-48.4 s: "He's a very talented accomplice."; `callfriend_eng__eng-s_001` 19.4-22.6 s: "I mean, you know, for just a casual outing with your children."

**Time-offset check (default):** 1 of 40 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.175 s; shifted: `callfriend_eng__eng-n_000` (+4.30 s).
<!-- /auto:diagnosis -->

**Why the DER is so high (30.8% at collar 0, 23.2% at 0.25 s).** Mostly the reference: 16% of reference speech is
missed by the model, and 11.7 points of that lie where the audio is *silent*. The tiled TalkBank bullets label
pauses and gaps as speech. Two more problems:
- `eng-n_000` is only 6 s long in the HF conversion (a truncated item).
- `eng-s_007` (two male speakers, 30 min) has 34% speaker confusion. In every 5-minute window both reference
  speakers map to both model speakers in similar proportions. Either the two voices are too similar on the phone
  line for the model, or the reference speaker codes are inconsistent; this was not resolved by listening.
- **Missing turns:** 39 of the 40 longest audible "false alarms" contain intelligible speech per Whisper, and the
  time-offset check rules out a shifted reference (median best lag 0.18 s; only the truncated `eng-n_000` is
  shifted). So, like CallHome, some turns were simply not transcribed or lost in the conversion.
Use CallFriend at collar >= 0.25 s, check the flagged files, and prefer Map Task (or CallHome with the flagged calls
removed) for two-speaker evaluation.


## Quality rating

**C.** Human turn-level transcription of natural phone calls, but tiled bullets and many same-speaker overlaps
make boundaries loose. Useful as an ungated, free stand-in for CallHome at collar 0.25 s.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare callfriend_eng            # download (resumable) + normalize (idempotent)
python -m diards validate callfriend_eng --vad     # ground-truth checks
python -m diards stats callfriend_eng
python -m diards export callfriend_eng --format nemo      # or pyannote / lhotse
python -m diards evaluate callfriend_eng --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("callfriend_eng", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

A. Canavan, G. Zipperlen, CALLFRIEND American English (North / South) LDC96S46/LDC96S47; TalkBank CABank CallFriend corpus.
