# The normalized format, the loader, and the exports

Every dataset, whatever its original layout, is turned into the same structure by `python -m diards prepare <name>`.
Default root: `$DIARDS_ROOT`, else `D:\diarization-data\normalized` on Windows when that exists, else
`~/diarization-data/normalized`. Raw downloads go to `$DIARDS_RAW` (default `<base>/raw`).

## Layout

```
<root>/<dataset>/
  dataset.json                   license, citation, source version, views, splits, ground-truth rating,
                                 normalization choices, sources (URLs, checksums)
  manifest.jsonl                 one JSON line per session, default view
  manifest.<view>.jsonl          one file per additional view (e.g. far-field vs close-talk mix)
  audio/<view>/<session_id>.wav  16 kHz, mono, 16-bit PCM
  rttm/<session_id>.rttm         primary reference (shared by all views of a session)
  uem/<session_id>.uem           scoring region(s)
  words/<session_id>.jsonl       {"start","end","speaker","word"} per line, where the corpus has word timings
  rttm_alt/<variant>/<session_id>.rttm   alternative references (forced-aligned vs manual, word-based, ...)
  exports/{nemo,pyannote,lhotse}/        created by `diards export`
```

Manifest line (paths are relative to the dataset directory):

```json
{"session_id": "ami__ES2004a", "dataset": "ami", "split": "test", "view": "sdm", "original_id": "ES2004a",
 "audio_filepath": "audio/sdm/ami__ES2004a.wav", "rttm_filepath": "rttm/ami__ES2004a.rttm",
 "uem_filepath": "uem/ami__ES2004a.uem", "words_filepath": "words/ami__ES2004a.jsonl",
 "duration": 1049.3, "scored_duration": 1049.3, "speech_duration": 812.4, "num_speakers": 4,
 "overlap_ratio": 0.152, "license": "CC-BY-4.0",
 "alt_rttm": {"only_words": "rttm_alt/only_words/ami__ES2004a.rttm", "...": "..."},
 "label_issues": {"same_speaker_overlap": 3}, "extra": {"reference": "forced_alignment"}}
```

Conventions:

- **Session ids** are ASCII `<dataset>__<original_id>` (unsafe characters become `_`). RTTM/UEM file ids equal the session id.
- **Speaker ids** are unique within a dataset: the corpus' global ids where they exist (AMI `MEE071`, CHiME `P05`,
  NOTSOFAR aliases, ICSI `me013`, Map Task participant ids, LibriSpeech ids, Oyez identifiers), otherwise
  `<original_id>_<local label>`.
- **Official splits** are kept (`train/dev/test`, `dev/eval`, `few.val`, ...). Corpora without splits use one split
  (`all` / `data`).
- **Views** (microphone or channel choices) never mix within a manifest: e.g. AMI `sdm` vs `ihm-mix`,
  CHiME-6 `farfield` vs `ihm-mix`. Each view is documented in `dataset.json` and the dataset card.
- **References**: same-speaker overlapping or touching segments are merged; segments are clipped to the audio. Every
  problem found in the *original* labels before this (same-speaker overlaps, duplicates, zero or negative durations,
  segments past the end of the audio, placeholder or case-variant speaker labels) is recorded in the manifest as
  `label_issues` and reported by `diards validate`.
- **UEM**: whole file unless the corpus defines a scoring region (CHiME-6: from the first annotated utterance,
  CHiME-7 convention; AVA-AVD: first to last labelled segment, official convention; Oyez: first to last turn).
- **overlap_ratio** = time with >= 2 active speakers / speech time, inside the UEM.

## Commands

```bash
python -m diards list
python -m diards prepare  <dataset> [--split S ...] [--view V ...] [--limit N] [--opt key=value]
python -m diards validate <dataset> [--view V] [--vad] [--out results/validation]
python -m diards stats    <dataset> [--out results/stats]
python -m diards export   <dataset> --format nemo|pyannote|lhotse [--view V] [--out DIR]
python -m diards evaluate <dataset> [--view V] [--split S] [--limit N] [--max-hours H] [--out DIR]
```

`prepare` is resumable (HTTP range resume, size check against the server, md5 where published) and idempotent
(converted audio is reused when it is already valid 16 kHz mono PCM; annotations and manifests are rewritten).

## Python loader

```python
from diards import load_dataset, NormalizedDataset

for s in load_dataset("notsofar1", split="eval", view="sc"):
    s.audio_path          # pathlib.Path to the 16 kHz WAV
    s.segments            # [Segment(start, end, speaker), ...]  primary reference
    s.alt_segments("words_gap0.2")
    s.uem                 # [(start, end), ...]
    s.words               # [{"start", "end", "speaker", "word"}, ...] or None
    s.num_speakers, s.overlap_ratio, s.duration

ds = NormalizedDataset("ami")
ds.views, ds.default_view, ds.meta["license"]
```

## Exports

| format | files | use |
|---|---|---|
| NeMo | `<dataset>.<view>.<split>.json` (JSONL: `audio_filepath, offset, duration, label, text, num_speakers, rttm_filepath, uem_filepath`) | `e2e_diarize_speech.py dataset_manifest=...`, NeMo diarization training/inference |
| pyannote | `database.yml` + per-subset `.lst/.rttm/.uem`; protocol `<dataset>_<view>.SpeakerDiarization.default` (`scope: database`) | `registry.load_database(".../database.yml")`; splits mapped to train/development/test (single-split corpora -> test) |
| Lhotse | `<dataset>_<view>_{recordings,supervisions}_<split>.jsonl.gz` | `CutSet.from_manifests(recordings=..., supervisions=...)` |

The Lhotse export is generic (one converter for every corpus), so no per-corpus Lhotse code is duplicated, and it
uses exactly the references and UEMs scored in this repo. Lhotse also ships native recipes for several of these
corpora. Those parse the original files themselves and differ from the normalized data:

| dataset | native Lhotse recipe | difference from the normalized data |
|---|---|---|
| AMI | `lhotse.recipes.prepare_ami` | uses NXT transcriber segments (loose), not the forced-aligned / BUT diarization references |
| ICSI | `prepare_icsi` | segment-level supervisions incl. non-word segments; same split |
| CHiME-6 | `prepare_chime6` | manual utterance segments, not the Track-2 alignment RTTM; no enrolment-minute UEM |
| DiPCo | `prepare_dipco` | same manual segments |
| VoxConverse | `prepare_voxconverse` | same RTTMs (check the version) |
| Earnings-21 | `prepare_earnings21` | ASR-oriented (no RTTM-based supervisions) |
| LibriCSS | `prepare_libricss` | same meeting_info segments |
| CallHome English | `prepare_callhome_english` | expects the LDC release, not the free TalkBank version |
