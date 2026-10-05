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

**TL;DR: best free English test sets with trustworthy labels.**
Two speakers: **HCRC Map Task**. Meetings: **NOTSOFAR-1 eval** and **AMI test (forced-aligned reference)**. Hard
far-field: **CHiME-6 eval** (official alignment RTTM). In-the-wild: **MSDWild (English subset)**, plus
**VoxConverse** if your model was not trained on it. Many speakers: **Earnings-21**. Doctor-patient:
**PriMock57 with this repo's channel-activity reference**, not its TextGrids. Score CallHome/CallFriend (TalkBank)
and AfriSpeech-Dialog only with care: we verified missing turns, and for AfriSpeech, shifted hand-typed times.

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
| # | dataset | domain | hours | recs | spk min/med/max | overlap | reference | GT | licence | access | size | mirrors | known issue |
|---:|---|---|---:|---:|---|---:|---|---|---|---|---|---|---|
| 1 | [maptask](datasets/maptask/README.md) | two-person task dialogue (close-talk) | 14.31 | 128 | 2/2/2 | 5.1% | word-level timed units, per close-talk channel | **A** | CC-BY-NC-SA-2.5 (audio + NXT zip); download page states CC BY 4.0 for annotations v2.1 | Free download, no registration. | ~2 GB | Edinburgh; LDC93S12 (paid) | task dialogue, studio audio; licence ambiguity (use NC) |
| 2 | [notsofar1](datasets/notsofar1/README.md) | meetings (far-field) | 17.07 | 165 | 3/5/7 | 32.1% | utterances + word times (human, close-talk) | **A-** | CC-BY-4.0 | Free download from Hugging Face (no gating) or Azure blob. | ~10 GB (eval+dev: close-talk + 1 far-field device) | HF microsoft/NOTSOFAR; Azure blob | utterances keep short pauses; device differs per room |
| 3 | [ami](datasets/ami/README.md) | meetings | 98.38 | 168 | 3/4/5 | 10.4% | forced-aligned words (MFA) from manual transcripts | **A-** | CC-BY-4.0 | Free download, no registration. | ~30 GB (all meetings, 2 views) | Edinburgh mirror; HF diarizers-community/ami, edinburghcstr/ami | 4 meetings with known timing failures (2 in test) |
| 4 | [chime6](datasets/chime6/README.md) | dinner party (home, far-field) | 9.67 | 4 | 4/4/4 | 25.5% | forced-aligned utterances (official Track 2) | **A-** | CC-BY-SA-4.0 | Free download from OpenSLR (dev 11 GB, eval 12 GB, train 97 GB), no registration. | 23 GB tarballs (dev+eval; only needed channels kept) | OpenSLR SLR150 (+ELDA, CN mirrors); HF argmaxinc/chime-6 | enrolment minute unannotated (UEM fixes); very hard audio |
| 5 | [voxconverse](datasets/voxconverse/README.md) | in-the-wild media (broadcast / YouTube) | 63.83 | 448 | 1/5/21 | 3.3% | human-verified diarization turns | **B+** | CC-BY-4.0 | Free download, no registration (audio CC BY 4.0 for research; copyright remains with video owners). | 7.3 GB (HF mirror) | Oxford VGG; HF diarizers-community/voxconverse | in many models' training data; 37 single-speaker files |
| 6 | [icsi](datasets/icsi/README.md) | meetings | 71.69 | 75 | 3/6/10 | 10.7% | manual transcriber segments (+ word times) | **B** | CC-BY-4.0 | Free download, no registration. | ~15 GB (2 views) | Edinburgh; HF argmaxinc/icsi-meetings | padded segments; 9-13% of words untimed; in Nemotron training data |
| 7 | [dipco](datasets/dipco/README.md) | dinner party (lab, far-field) | 5.33 | 10 | 4/4/4 | 27.7% | manual utterances up to 10-15 s | **B** | CDLA-Permissive-1.0 | Free download from Zenodo (13.4 GB), no registration. | 13.4 GB tarball | Zenodo 8122551; HF huckiyang/DiPCo | pauses inside segments; only 10 sessions |
| 8 | [easycom](datasets/easycom/README.md) | egocentric conversation in noise (AR glasses) | 5.3 | 12 | 4/4/6 | 17.0% | human VAD per utterance (50 ms frames) | **B** | CC-BY-NC-4.0 | Free (GitHub, Git LFS or a 70 GB split release archive). | ~22 GB (glasses audio + labels, per-file LFS) | GitHub LFS + release archive | loudspeaker noise; missing (redacted) minutes |
| 9 | [msdwild_en](datasets/msdwild_en/README.md) | vlogs (in-the-wild media) | 27.91 | 894 | 2/2/9 | 10.1% | human diarization turns | **B** | MSDWild license agreement (research only, no redistribution) | Free download (Google Drive); accept the research-only license agreement. | 8.1 GB (all clips) | Google Drive (+Baidu/Quark) | research-only licence; English by LID; short clips |
| 10 | [ava_avd_en](datasets/ava_avd_en/README.md) | movies (in-the-wild media) | 8.0 | 96 | 2/7/24 | 3.6% | human identity turns | **B** | Research use (AVA annotations CC BY 4.0; movies copyrighted, distributed by CVDF for research) | Free: annotations on GitHub/Google Drive, videos from the CVDF S3 mirror. | ~5 GB (minutes 15-30 of 117 movies via HTTP range) | GitHub + Google Drive + CVDF S3; HF argmaxinc/ava-avd | music/effects-heavy audio, many speakers; English by LID |
| 11 | [earnings21](datasets/earnings21/README.md) | earnings calls (telephone/broadcast) | 39.26 | 44 | 2/10/20 | 0.0% | RTTM from human transcripts (timing method undocumented) | **B-** | CC-BY-SA-4.0 | Free download from GitHub, no registration. | ~1.5 GB | GitHub revdotcom/speech-datasets; HF argmaxinc/earnings21 | almost no overlap/backchannels |
| 12 | [sbcsae](datasets/sbcsae/README.md) | everyday conversation (mixed situations) | 23.31 | 60 | 1/4/16 | 7.1% | intonation units (ms bullets), tiled | **C+** | CC-BY-ND-3.0-US | Free download from OpenSLR (6.2 GB), no registration. | 6.2 GB | OpenSLR SLR155 (+ELDA); UCSB; TalkBank; LDC (paid) | pauses inside units; CC BY-ND (no derived RTTMs shared) |
| 13 | [callhome_eng](datasets/callhome_eng/README.md) | telephone (2+ speakers) | 20.3 | 140 | 2/2/4 | 9.0% | turn bullets (LDC transcripts via TalkBank) | **C** | CC-BY-NC-SA-4.0 | Free, gated on Hugging Face (click-through form asking company + country). | 2.3 GB (HF parquet) | HF talkbank/callhome (gated); TalkBank (login) | loose turns, backchannels incomplete |
| 14 | [scotus](datasets/scotus/README.md) | court (oral arguments) | 20.5 | 12 | 10/11/13 | 0.0% | Oyez turn sync, tiled, no overlap | **C** | Audio: public record; Oyez transcripts/sync: CC-BY-NC-4.0 | Free public API, no registration. | ~0.7 GB (12-case sample) | Oyez API; vcon-dev pack | interruptions never marked as overlap |
| 15 | [callfriend_eng](datasets/callfriend_eng/README.md) | telephone (2+ speakers) | 10.44 | 40 | 2/2/4 | 7.0% | turn bullets (TalkBank) | **C-** | TalkBank ground rules (research, cite); HF card states no license | Free on Hugging Face (not gated). | 1.2 GB (HF parquet) | HF talkbank/callfriend; TalkBank | tiled bullets, 3,074 same-speaker overlaps |
| 16 | [afrispeech_dialog](datasets/afrispeech_dialog/README.md) | medical-like consultations + general conversation | 6.63 | 46 | 2/2/2 | 0.1% | hand-typed turn times (~1 s precision) | **D** | CC-BY-NC-SA-4.0 | Free on Hugging Face (not gated). | ~0.8 GB | HF intronhealth/afrispeech-dialog | coarse times, no overlap, 3/49 untimed |
| 17 | [primock57](datasets/primock57/README.md) | medical consultations (remote, 2 speakers) | 8.64 | 57 | 2/2/2 | 6.3% | padded utterances per channel (+ our channel-activity RTTM) | **D (official) / B (channel-activity RTTM)** | CC-BY-4.0 | Free download from GitHub (audio in Git LFS). | ~1 GB | GitHub (LFS) | 10-14% of labelled time is silence |
| 18 | [libricss](datasets/libricss/README.md) | synthetic meetings (read speech replayed in a room) | 10.1 | 60 | 8/8/8 | 10.3% | exact playback times (synthetic) | **S (synthetic)** | CC-BY-4.0 (LibriSpeech-derived) | Free download (Google Drive, 6.4 GB). | 6.4 GB | Google Drive | read speech replayed; not real conversation |
<!-- /auto:catalog -->

## Recommendations by use case

Pick by what you need to measure. The **reference** to score against is part of the recommendation, because on
several corpora it changes DER by a factor of two (see the Nemotron section).

**Meetings, close-talk or near-field**
1. **NOTSOFAR-1 eval, `ihm-mix` view**, scored against `words_gap0.2` (or the FastMSS MFA subset): recent, real
   office meetings, 3-8 speakers, held out from Nemotron's training data, CC BY 4.0.
2. **AMI test, `ihm-mix`**, scored against the **forced-aligned (MFA) reference**, and say so. Our run reproduces
   the model card (9.22% vs 9.25% DER). The EN2002 meetings have known timing problems.
3. ICSI for long (~1 h) natural meetings with up to 10 speakers. It is in Nemotron's training data, so it is not
   held-out for that model.

**Meetings, far-field**
1. **NOTSOFAR-1 eval, `sc` view**: commercial single-channel devices in 30 rooms, the realistic product setting.
2. **AMI test, `sdm`**: the classic far-field benchmark (MFA reference).
3. **CHiME-6 eval, `farfield`**: real dinner parties in homes, ~25% overlap, ~32 speaker changes per minute. The
   hardest free English test. Official forced-aligned reference plus the CHiME-7 UEM.
4. DiPCo eval: small and permissive, but its 10-15 s segments overstate speech (use collar 0.25 s).

**Phone / two-speaker**
1. **HCRC Map Task**: separate close-talk channels and word-level timing, the cleanest free two-speaker reference.
   Studio audio and task dialogue, so it is easier than real calls.
2. **CallHome English (TalkBank)**: the classic phone domain. Usable at collar 0.25 s, but some calls have
   unlabelled turns (verified with Whisper), so check `results/diagnosis` and drop the flagged calls.
3. CallFriend English: ungated, but loose tiled bullets (high DER that is mostly reference error).
4. With a sign-up: MLC-SLM English (~500 h of natural two-speaker mobile conversations).

**Far-field / egocentric / hearing-aid style**
EasyCom (AR glasses in restaurant noise, human per-speaker VAD), CHiME-6. With a sign-up: CHiME-9 ECHI, MMCSG,
Ego4D AVD.

**In-the-wild media**
1. **VoxConverse v0.3** is still the standard, but it is in Nemotron's (and others') training data.
2. **MSDWild (English subset)**: casual vlogs with lots of overlap; research-only licence.
3. **AVA-AVD (English subset)**: movies, many speakers, off-screen speech.
4. **Earnings-21**: long business calls with up to 20 speakers and almost no overlap (tests speaker counting and
   long-form tracking).
5. SCOTUS (Oyez) for the court domain: coarse turn timing, use a generous collar.

**Medical-like conversations**
1. **PriMock57 with this repo's channel-activity reference** (`rttm_alt/channel_activity`): the best free English
   doctor-patient audio. The official TextGrids are not diarization-grade ([PRIMOCK57.md](PRIMOCK57.md)).
2. AfriSpeech-Dialog (African-accented consultations): hand-typed ~1 s timestamps, so only for coarse checks or
   after re-alignment.
3. Map Task as a clean two-party proxy for consultation-style turn-taking.

**Training rather than benchmarking**: AMI/ICSI/NOTSOFAR/CHiME-6 train splits; Seamless Interaction (4,000 h of
dyadic conversation with automatic per-channel VAD); synthetic LibriCSS / LibriMix for controlled overlap.

## Nemotron 3 Diarization on every dataset

`nvidia/Nemotron-3-Diarization` (revision `f667ed73`), Hugging Face Transformers port in offline mode. It chunks
exactly like the model card's 30.4 s NeMo configuration (chunk 340, right context 40, FIFO 40, update period 300,
speaker cache 264). Threshold 0.5, no other post-processing. RTX 5080, fp32, ~800-1,100x real time. Scoring:
pyannote.metrics DER/JER, overlap included, UEM applied, collar = half-width (0 and 0.25 s). Exact commands:
[results/README.md](results/README.md).

<!-- auto:nemotron_summary -->
| dataset | view (subset) | sessions | hours | DER % c=0 (primary ref) | DER % c=0.25 | other references (DER % c=0) | spk-count acc | held-out? |
|---|---|---:|---:|---:|---:|---|---:|---|
| [maptask](datasets/maptask/README.md) | default (all) | 128 | 14.31 | 7.94 | 1.88 |  | 95% | yes |
| [notsofar1](datasets/notsofar1/README.md) | ihm-mix (eval) | 129 | 13.34 | 14.52 | 5.51 | fastmss_mfa 9.6; words_gap0.2 11.2 | 95% | yes |
| [notsofar1](datasets/notsofar1/README.md) | sc (eval) | 129 | 13.34 | 18.41 | 6.92 | fastmss_mfa 11.3; words_gap0.2 15.0 | 77% | yes |
| [ami](datasets/ami/README.md) | ihm-mix (test) | 16 | 9.06 | 9.22 | 3.56 | only_words 26.0; word_and_vocalsounds 27.7; segments 31.1 | 88% | yes |
| [ami](datasets/ami/README.md) | sdm (test) | 16 | 9.06 | 11.35 | 4.73 | only_words 27.5; word_and_vocalsounds 29.2; segments 32.5 | 88% | yes |
| [chime6](datasets/chime6/README.md) | farfield (eval) | 2 | 5.21 | 37.63 | 25.61 | annotation 43.6 | 0% | yes |
| [chime6](datasets/chime6/README.md) | farfield.dev (dev) | 2 | 4.46 | 31.70 | 19.06 | annotation 41.6 | 0% | yes |
| [chime6](datasets/chime6/README.md) | ihm-mix (eval) | 2 | 5.21 | 32.76 | 22.49 | annotation 37.8 | 50% | yes |
| [voxconverse](datasets/voxconverse/README.md) | default (test) | 232 | 43.54 | 8.39 | 5.74 |  | 53% | NO (in training data) |
| [icsi](datasets/icsi/README.md) | ihm-mix (test) | 3 | 2.77 | 15.86 | 5.31 | words_gap0.2 39.4 | 100% | NO (in training data) |
| [icsi](datasets/icsi/README.md) | sdm (test) | 3 | 2.77 | 15.85 | 5.39 | words_gap0.2 38.2 | 100% | NO (in training data) |
| [dipco](datasets/dipco/README.md) | farfield (eval) | 5 | 2.6 | 36.16 | 28.07 | closetalk_activity 40.3 | 40% | yes |
| [msdwild_en](datasets/msdwild_en/README.md) | default (few.val,many.val) | 150 | 4.16 | 17.79 | 10.67 |  | 76% | yes |
| [ava_avd_en](datasets/ava_avd_en/README.md) | default (test,val) | 29 | 2.42 | 49.79 | 33.98 |  | 21% | yes |
| [earnings21](datasets/earnings21/README.md) | default (eval10,other) | 44 | 39.26 | 19.54 | 15.90 |  | 20% | yes |
| [sbcsae](datasets/sbcsae/README.md) | default (all) | 60 | 23.31 | 27.38 | 24.23 |  | 43% | yes |
| [callhome_eng](datasets/callhome_eng/README.md) | default (data) | 140 | 20.3 | 11.68 | 7.23 |  | 93% | unclear |
| [scotus](datasets/scotus/README.md) | default (term2022) | 12 | 20.5 | 31.66 | 30.25 |  | 0% | yes |
| [callfriend_eng](datasets/callfriend_eng/README.md) | default (data) | 40 | 10.44 | 30.80 | 23.24 |  | 75% | yes |
| [afrispeech_dialog](datasets/afrispeech_dialog/README.md) | default (general,medical) | 46 | 6.63 | 26.69 | 24.51 |  | 93% | yes |
| [primock57](datasets/primock57/README.md) | mix (all) | 57 | 8.64 | 24.15 | 15.99 | channel_activity 10.4 | 84% | yes |
<!-- /auto:nemotron_summary -->

### What the benchmark shows

1. **The reference is half the result.** Same model output, different reference, very different DER:
   AMI SDM test 11.3% (forced-aligned MFA) vs 27.5% (BUT `only_words`) vs 32.5% (transcriber segments);
   NOTSOFAR-1 far-field 18.4% (official utterances) vs 15.0% (word-based) vs 11.3% (MFA);
   PriMock57 24.2% (official TextGrids) vs 10.4% (per-channel activity); CHiME-6 far-field 37.6% (official alignment
   RTTM) vs 43.6% (human utterance RTTM). The gap is almost entirely missed speech in pauses that loose references
   label as speech, and it survives a 0.25 s collar. Always report which reference you used.
2. **Reference errors verified, not just suspected.** The checks combine an energy split of errors, a Whisper
   transcription of the longest audible "false alarms", and a time-offset search. They found:
   - missing turns in CallHome English (38 of the 40 longest audible false alarms are real speech) and CallFriend
     (39/40), both TalkBank conversions;
   - hand-typed AfriSpeech-Dialog times that are about 0.45 s early (median best lag), plus untimed speech (35/40);
   - utterances dropped by the MFA reference in AMI's EN2002 test meetings (up to 5% of a meeting's speech;
     confirmed by the model's false alarms);
   - pauses labelled as speech in tiled or padded references: SBCSAE, SCOTUS, PriMock57, CallFriend, DiPCo,
     AfriSpeech;
   - a corrupted ICSI segment that ends 35 minutes after the recording (Bro025), and a 6-second truncated CallFriend
     item.
3. **Real model limits.** Nemotron 3 Diarization outputs at most 8 speakers. On Earnings-21 (31 of 44 calls have
   more than 8), SCOTUS (11-13 speakers) and AVA-AVD most error is speaker confusion and wrong speaker counts.
   Heavy overlap in far-field homes (CHiME-6) and movie soundtracks (AVA-AVD) remain hard. Speech detection itself
   is strong almost everywhere.
4. **Training-data overlap.** The model was trained on ICSI, VoxConverse (dev and test), AMI/NOTSOFAR train+dev,
   DiPCo dev and CALLHOME part 1. Treat ICSI and VoxConverse scores as non-held-out.
5. **The harness is faithful.** It reproduces the model card on AMI test close-talk (9.22% vs 9.25% DER), and the
   official NeMo 3.1 implementation agrees with our Transformers path to within about 1% DER
   ([results/nemo_crosscheck](results/nemo_crosscheck/README.md)).

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
