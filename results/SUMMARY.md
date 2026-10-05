# Summary tables (auto-generated)

Regenerate with `python scripts/make_cards.py`. Per-dataset details are in the dataset cards.

## Catalog with measured statistics

<!-- auto:catalog -->
| # | dataset | domain | hours | recs | spk min/med/max | overlap | reference | GT | licence | access | size | known issue |
|---:|---|---|---:|---:|---|---:|---|---|---|---|---|---|
| 1 | [notsofar1](datasets/notsofar1/README.md) | meetings (far-field) | 17.07 | 165 | 3/5/7 | 32.1% | utterances + word times (human, close-talk) | **A-** | CC-BY-4.0 | Free download from Hugging Face (no gating) or Azure blob. | ~10 GB (eval+dev: close-talk + 1 far-field device) | utterances keep short pauses; device differs per room |
| 2 | [ami](datasets/ami/README.md) | meetings | 98.38 | 168 | 3/4/5 | 10.4% | forced-aligned words (MFA) from manual transcripts | **A-** | CC-BY-4.0 | Free download, no registration. | ~30 GB (all meetings, 2 views) | 4 meetings with known timing failures (2 in test) |
| 3 | [chime6](datasets/chime6/README.md) | dinner party (home, far-field) | - | - | - | - | forced-aligned utterances (official Track 2) | **A-** | CC-BY-SA-4.0 | Free download from OpenSLR (dev 11 GB, eval 12 GB, train 97 GB), no registration. | 23 GB tarballs (dev+eval; only needed channels kept) | enrolment minute unannotated (UEM fixes); very hard audio |
| 4 | [maptask](datasets/maptask/README.md) | two-person task dialogue (close-talk) | - | - | - | - | word-level timed units, per close-talk channel | **A-** | CC-BY-NC-SA-2.5 (audio + NXT zip); download page states CC BY 4.0 for annotations v2.1 | Free download, no registration. | ~2 GB | task dialogue, studio audio; licence ambiguity (use NC) |
| 5 | [voxconverse](datasets/voxconverse/README.md) | in-the-wild media (broadcast / YouTube) | 63.83 | 448 | 1/5/21 | 3.3% | human-verified diarization turns | **B+** | CC-BY-4.0 | Free download, no registration (audio CC BY 4.0 for research; copyright remains with video owners). | 7.3 GB (HF mirror) | in many models' training data; 37 single-speaker files |
| 6 | [icsi](datasets/icsi/README.md) | meetings | 71.69 | 75 | 3/6/10 | 10.7% | manual transcriber segments (+ word times) | **B** | CC-BY-4.0 | Free download, no registration. | ~15 GB (2 views) | padded segments; 9-13% of words untimed; in Nemotron training data |
| 7 | [dipco](datasets/dipco/README.md) | dinner party (lab, far-field) | - | - | - | - | manual utterances up to 10-15 s | **B** | CDLA-Permissive-1.0 | Free download from Zenodo (13.4 GB), no registration. | 13.4 GB tarball | pauses inside segments; only 10 sessions |
| 8 | [easycom](datasets/easycom/README.md) | egocentric conversation in noise (AR glasses) | - | - | - | - | human VAD per utterance (50 ms frames) | **B** | CC-BY-NC-4.0 | Free (GitHub, Git LFS or a 70 GB split release archive). | ~22 GB (glasses audio + labels, per-file LFS) | loudspeaker noise; missing (redacted) minutes |
| 9 | [msdwild_en](datasets/msdwild_en/README.md) | vlogs (in-the-wild media) | - | - | - | - | human diarization turns | **B** | MSDWild license agreement (research only, no redistribution) | Free download (Google Drive); accept the research-only license agreement. | 8.1 GB (all clips) | research-only licence; English by LID; short clips |
| 10 | [earnings21](datasets/earnings21/README.md) | earnings calls (telephone/broadcast) | 39.26 | 44 | 2/10/20 | 0.0% | RTTM from human transcripts (timing method undocumented) | **B-** | CC-BY-SA-4.0 | Free download from GitHub, no registration. | ~1.5 GB | almost no overlap/backchannels |
| 11 | [ava_avd_en](datasets/ava_avd_en/README.md) | movies (in-the-wild media) | 8.0 | 96 | 2/7/24 | 3.6% | human identity turns | **B-** | Research use (AVA annotations CC BY 4.0; movies copyrighted, distributed by CVDF for research) | Free: annotations on GitHub/Google Drive, videos from the CVDF S3 mirror. | ~5 GB (minutes 15-30 of 117 movies via HTTP range) | speech in .lab files without speaker label; English by LID |
| 12 | [sbcsae](datasets/sbcsae/README.md) | everyday conversation (mixed situations) | - | - | - | - | intonation units (ms bullets), tiled | **B-** | CC-BY-ND-3.0-US | Free download from OpenSLR (6.2 GB), no registration. | 6.2 GB | pauses inside units; CC BY-ND (no derived RTTMs shared) |
| 13 | [callhome_eng](datasets/callhome_eng/README.md) | telephone (2+ speakers) | 20.3 | 140 | 2/2/4 | 9.0% | turn bullets (LDC transcripts via TalkBank) | **C+** | CC-BY-NC-SA-4.0 | Free, gated on Hugging Face (click-through form asking company + country). | 2.3 GB (HF parquet) | loose turns, backchannels incomplete |
| 14 | [callfriend_eng](datasets/callfriend_eng/README.md) | telephone (2+ speakers) | 10.44 | 40 | 2/2/4 | 7.0% | turn bullets (TalkBank) | **C** | TalkBank ground rules (research, cite); HF card states no license | Free on Hugging Face (not gated). | 1.2 GB (HF parquet) | tiled bullets, 3,074 same-speaker overlaps |
| 15 | [scotus](datasets/scotus/README.md) | court (oral arguments) | - | - | - | - | Oyez turn sync, tiled, no overlap | **C** | Audio: public record; Oyez transcripts/sync: CC-BY-NC-4.0 | Free public API, no registration. | ~0.7 GB (12-case sample) | interruptions never marked as overlap |
| 16 | [afrispeech_dialog](datasets/afrispeech_dialog/README.md) | medical-like consultations + general conversation | 6.63 | 46 | 2/2/2 | 0.1% | hand-typed turn times (~1 s precision) | **D+** | CC-BY-NC-SA-4.0 | Free on Hugging Face (not gated). | ~0.8 GB | coarse times, no overlap, 3/49 untimed |
| 17 | [primock57](datasets/primock57/README.md) | medical consultations (remote, 2 speakers) | 8.64 | 57 | 2/2/2 | 6.3% | padded utterances per channel (+ our channel-activity RTTM) | **D** | CC-BY-4.0 | Free download from GitHub (audio in Git LFS). | ~1 GB | 10-14% of labelled time is silence |
| 18 | [libricss](datasets/libricss/README.md) | synthetic meetings (read speech replayed in a room) | - | - | - | - | exact playback times (synthetic) | **S (synthetic)** | CC-BY-4.0 (LibriSpeech-derived) | Free download (Google Drive, 6.4 GB). | 6.4 GB | read speech replayed; not real conversation |
<!-- /auto:catalog -->

## Nemotron 3 Diarization

<!-- auto:nemotron_summary -->
| dataset | view (subset) | sessions | hours | DER % c=0 (primary ref) | DER % c=0.25 | best alternative ref (DER % c=0) | spk-count acc | held-out? |
|---|---|---:|---:|---:|---:|---|---:|---|
| [notsofar1](datasets/notsofar1/README.md) | ihm-mix (eval) | 129 | 13.34 | 14.52 | 5.51 | fastmss_mfa: 9.63 | 95% | yes |
| [notsofar1](datasets/notsofar1/README.md) | sc (eval) | 129 | 13.34 | 18.41 | 6.92 | fastmss_mfa: 11.32 | 77% | yes |
| [ami](datasets/ami/README.md) | sdm (test) | 16 | 9.06 | 11.35 | 4.73 | only_words: 27.45 | 88% | yes |
| [voxconverse](datasets/voxconverse/README.md) | default (test) | 232 | 43.54 | 8.39 | 5.74 |  | 53% | NO (in training data) |
| [icsi](datasets/icsi/README.md) | ihm-mix (test) | 3 | 2.77 | 15.86 | 5.31 | words: 44.46 | 100% | NO (in training data) |
| [callhome_eng](datasets/callhome_eng/README.md) | default (data) | 140 | 20.3 | 11.68 | 7.23 |  | 93% | unclear |
| [callfriend_eng](datasets/callfriend_eng/README.md) | default (data) | 40 | 10.44 | 30.80 | 23.24 |  | 75% | yes |
| [primock57](datasets/primock57/README.md) | mix (all) | 57 | 8.64 | 24.15 | 15.99 | channel_activity: 10.38 | 84% | yes |
<!-- /auto:nemotron_summary -->
