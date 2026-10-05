# Free English speaker-diarization datasets, verified

This repo is a catalog of **free** English datasets for speaker diarization (2+ speakers per recording), with the
quality of each one's ground truth **measured, not just cited**. It includes:

* **18 datasets** downloaded, normalized into one layout, and checked with our own scripts: speaker counts,
  overlap, segment and pause statistics, label sanity, and an energy-VAD check for unlabelled speech.
* **A benchmark of NVIDIA's [Nemotron 3 Diarization](https://huggingface.co/nvidia/Nemotron-3-Diarization)**
  (released 2026-09-23) on every dataset, scored against each available reference variant. The point is to show
  how much "model error" is actually reference error.
* **One command per dataset** that downloads (resumable) and normalizes (idempotent) the data, plus `validate`,
  `stats`, `export` (NeMo / pyannote / Lhotse) and `evaluate` commands and a small Python loader.
* **[PRIMOCK57.md](PRIMOCK57.md)**: evidence on why PriMock57's labels are weak for diarization, and a tighter
  reference derived from its separate channels.
* An appendix of everything considered and excluded (paid/LDC, sign-up only, weak or automatic labels, non-English,
  synthetic): [docs/OTHER_DATASETS.md](docs/OTHER_DATASETS.md).

Progress log: [PROGRESS.md](PROGRESS.md).

## Quick start

```bash
# 1. environment (Python >= 3.10; GPU optional, needed for evaluation at speed)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128   # pick your CUDA
pip install -r requirements.txt          # needs a Transformers build with Nemotron 3 Diarization (see file)
# ffmpeg on PATH is recommended (mp3/mp4/sph inputs)

# 2. where data goes (defaults: D:\diarization-data on Windows if present, else ~/diarization-data)
export DIARDS_BASE=/data/diarization        # normalized/, raw/, work/ are created below it

# 3. one dataset end to end
python -m diards list
python -m diards prepare notsofar1 --split eval          # download + normalize
python -m diards validate notsofar1 --view ihm-mix --vad # ground-truth checks
python -m diards stats notsofar1
python -m diards export notsofar1 --format pyannote      # or nemo / lhotse
python -m diards evaluate notsofar1 --view sc --split eval
```

```python
from diards import load_dataset
for s in load_dataset("ami", split="test", view="sdm"):
    print(s.session_id, s.audio_path, len(s.segments), s.num_speakers, s.overlap_ratio)
```

Format details, conventions and exports: [docs/FORMAT.md](docs/FORMAT.md). Tests: `python -m pytest tests`.

## Ground-truth rating

| grade | meaning |
|---|---|
| **A** | every speaker on a close-talk channel, human transcription, tight (word-level or forced-aligned) timing, overlap and backchannels present, documented method |
| **B** | human labels with full speaker coverage and overlap, but utterance-level / padded boundaries or minor gaps |
| **C** | human turn-level timing that tiles the timeline or misses backchannels/overlap; fine at collar 0.25 s, not at collar 0 |
| **D** | timing too coarse or incomplete for DER without re-alignment |
| **S** | synthetic or simulated: exact by construction, not natural conversation |

## Catalog (ranked)

Numbers (hours, recordings, speakers, overlap) are **measured** on the normalized data by `diards stats`
(primary reference, inside the UEM; overlap = time with >= 2 speakers / speech time). Click a dataset for its card:
source, licence, access steps, annotation method, known issues and errata, validation report and Nemotron results.

<!-- auto:catalog -->
<!-- /auto:catalog -->

## Recommendations by use case

RECOMMENDATIONS_PLACEHOLDER

## Nemotron 3 Diarization on every dataset

`nvidia/Nemotron-3-Diarization` (revision `f667ed73`), Hugging Face Transformers port in offline mode. It chunks
exactly like the model card's 30.4 s NeMo configuration (chunk 340, right context 40, FIFO 40, update period 300,
speaker cache 264). Threshold 0.5, no other post-processing. RTX 5080, fp32, ~800-1,100x real time. Scoring:
pyannote.metrics DER/JER, overlap included, UEM applied, collar = half-width (0 and 0.25 s). Exact commands:
[results/README.md](results/README.md).

<!-- auto:nemotron_summary -->
<!-- /auto:nemotron_summary -->

NEMOTRON_FINDINGS_PLACEHOLDER

## Paid or restricted (appendix)

Not in the catalog, listed for completeness. Details and free substitutes are in
[docs/OTHER_DATASETS.md](docs/OTHER_DATASETS.md#b-paid-or-restricted-ldc--elra--broadcaster-listed-for-completeness).

| dataset | where | note |
|---|---|---|
| CALLHOME (NIST SRE 2000), the 2-speaker phone benchmark | LDC2001S97 | free substitute: `callhome_eng` (TalkBank) |
| CallHome American English (full calls) | LDC97S42 / LDC97T14 | free TalkBank excerpts: `callhome_eng` |
| Fisher English | LDC2004S13 / LDC2005S13 | 2,000 h of 2-speaker calls |
| Switchboard-1 R2 (+ NXT) | LDC97S62 / LDC2009T26 | classic phone corpus |
| DIHARD III | LDC2022S14 / LDC2022S15 | multi-domain benchmark |
| Mixer 6 | LDC2013S03 | CHiME-7 interviews |
| NIST RT meetings, ISL meetings, CHIL | LDC / ELRA | historic meeting sets |
| MGB (BBC) | BBC R&D agreement | broadcast |

Free but needing a manual sign-up (not verified here): Ego4D AVD, MMCSG, CHiME-9 ECHI, Fearless Steps, MLC-SLM
English, MCoRec, This American Life (Kaggle). See [docs/OTHER_DATASETS.md](docs/OTHER_DATASETS.md#a-free-but-needs-a-manual-sign-up-that-could-not-be-completed-unattended).

## Repository layout

```
diards/              python package: core layout + loader, recipes (diards/datasets/*), validate, stats, score,
                     evaluate (Nemotron), export (NeMo / pyannote / Lhotse), energy VAD, Whisper LID
datasets/<name>/     one card per dataset
results/             stats/, validation/, nemotron/, primock57/ (+ SUMMARY.md, README.md with commands)
metadata/            derived language-ID results for the English subsets of MSDWild and AVA-AVD
scripts/             validate_all.sh, run_nemotron_all.sh, make_cards.py, analyze_primock57.py
docs/                FORMAT.md, OTHER_DATASETS.md, research_notes.md
tests/               pytest suite with small fixtures
```

Code: MIT. Every dataset keeps its own licence (see its card). This repo redistributes only annotation-derived
files whose licence allows it (e.g. the PriMock57 channel-activity RTTMs, CC BY 4.0) and language-ID metadata.
