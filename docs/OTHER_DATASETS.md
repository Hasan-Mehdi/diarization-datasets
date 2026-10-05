# Other datasets: needs sign-up, paid / restricted, weak labels, non-English, synthetic

Everything below was checked (October 2026) and is **not** in the main catalog. Each entry says why. Sources are
in [`research_notes.md`](research_notes.md).

## A. Free, but needs a manual sign-up that could not be completed unattended

These look good and are free. Each needs a person to accept a license that involves manual approval or an emailed
key, so they were not downloaded or verified here.

| Dataset | What | Ground truth | Access | Notes |
|---|---|---|---|---|
| **Ego4D Audio-Visual Diarization** | ~50 h annotated egocentric video (572 clips) from 3,000+ h of Ego4D; multilingual, much English | Human AV speaker tracks + voice activity + transcripts | Sign the Ego4D license at <https://ego4d-data.org/>; AWS keys emailed after ~48 h | Benchmark code MIT. Clips are 5 min. Needs LID or metadata for English. |
| **MMCSG** (CHiME-8 Task 3) | 530 two-party conversations recorded with Aria glasses (26 h: train/dev/eval) | Human segments + forced-aligned word times | Registration on Meta's dataset page linked from <https://www.chimechallenge.org/challenges/chime8/task3/data>; no redistribution; CC BY-NC | Official note: the RTTM segments "might often overestimate the actual speaking time"; use the word-level TSVs for tight references. |
| **CHiME-9 ECHI** | 48 sessions / 29 h, 4 people at a table in cafe noise, Aria glasses + hearing aids + close-talk mics | Segmentation of each participant's speech | HF [`CHiME9-ECHI/CHiME9-ECHI`](https://huggingface.co/datasets/CHiME9-ECHI/CHiME9-ECHI), manual DUA approval (academic only); our token got 403 | Dev 23.6 GB. Strong candidate for far-field / hearing-aid diarization once approved. A follow-up "ECHI-2" is CHiME-10 Task 1. |
| **Fearless Steps (Apollo-11/13)** | NASA mission-control loops, 8 kHz, ~80 h of ground truth in FSC Phase 3 (19,000 h raw) | Human speaker segments (challenge GT) | Register on NIST OpenSAT (<https://sat.nist.gov/fsc3>) or the UT Dallas form; CC BY 4.0 + NASA media guidelines | Unique domain (radio comms, many speakers, low SNR). |
| **MLC-SLM English** | ~500 h of natural two-speaker English conversations (American, British, Australian, Filipino, Indian) on mobile phones; eval sets 69 conversations | Oracle segments + speaker labels + transcripts (human) | Audio via Nexdata registration (<https://www.nexdata.ai/competition/mlc-slm>); eval ground truth is public on HF [`bsmu/MLC-SLM-Eval`](https://huggingface.co/datasets/bsmu/MLC-SLM-Eval) (CC BY-SA 4.0) | Probably the largest human-labelled 2-speaker English set if you register. |
| **CHiME-9 MCoRec** | 150 recordings of up to 4 simultaneous conversations in one room (360-degree camera + mic) | Per-speaker WebVTT transcripts with times | HF gated DUA | Language not stated on the data page; CC BY-NC. |
| **This American Life** (Mao et al. 2020) | 663 radio episodes, 637 h, ~18 speakers per episode | Professional transcripts with speaker names, aligned to audio | Alignments on Kaggle (free account): `shuyangli94/this-american-life-podcast-transcriptsalignments`; audio must be fetched from the show's site (many links dead; see github.com/jovistos/TALAD) | Audio copyrighted. Alignment is automatic. Used as "American-Life-Podcast" in SDBench. |

## B. Paid or restricted (LDC / ELRA / broadcaster), listed for completeness

| Dataset | Distributor / catalog | Why it matters | Free alternative here |
|---|---|---|---|
| CALLHOME (NIST SRE 2000 Disk 8, the "CALLHOME" diarization benchmark) | LDC2001S97 | Most-cited 2-speaker phone benchmark (multilingual) | `callhome_eng` (TalkBank version of the English calls) |
| CallHome American English speech + transcripts | LDC97S42 / LDC97T14 | Full 30-min calls, LDC transcripts | `callhome_eng` (transcribed excerpts, free on HF) |
| Fisher English Part 1/2 | LDC2004S13, LDC2005S13 (+T19/T19 transcripts) | 2,000 h of 2-speaker phone calls, separate channels | Map Task, CallFriend, MLC-SLM (sign-up) |
| Switchboard-1 Release 2 (+ NXT) | LDC97S62, LDC2009T26 | Classic 2-speaker phone, word-level MS-State alignments | Map Task, CallFriend |
| DIHARD III (dev / eval) | LDC2022S14 / LDC2022S15 | The multi-domain diarization benchmark (some free during the challenge only) | Use the domain-matched free sets in this catalog |
| Mixer 6 Speech | LDC2013S03 (free to CHiME-7 participants only) | Interviews, 2 speakers, far-field, CHiME-7 DASR | NOTSOFAR-1, CHiME-6 |
| NIST Rich Transcription meeting sets (RT-02..RT-09) | LDC (e.g. LDC2007S11) | Historic meeting diarization benchmarks | AMI, ICSI, NOTSOFAR-1 |
| ISL Meeting Corpus | LDC2004S05 | Meetings | AMI, ICSI |
| CHIL seminars/meetings | ELRA | Lecture/meeting diarization | AMI, ICSI |
| MGB Challenge (BBC TV) | BBC R&D research agreement | Broadcast diarization at scale | VoxConverse, Earnings-21 |
| Spotify Podcasts Dataset | Withdrawn (2023) | Podcasts | (none) |
| Santa Barbara Corpus (LDC edition) | LDC2000S85 etc. | Same corpus | `sbcsae` (free OpenSLR / UCSB version) |
| HCRC Map Task (LDC edition) | LDC93S12 | Same corpus | `maptask` (free Edinburgh version) |

## C. Free, but ground truth too weak (or wrong kind) for a diarization reference

| Dataset | Problem | Possible use |
|---|---|---|
| **CANDOR** (BetterUp/UPenn, 1,656 video calls, 850 h) | Transcripts and turns are AWS Transcribe output (TalkBank's CHAT version is also ASR "needing further checking"); access needs BetterUp approval plus a TalkBank email | Training data with pseudo-labels |
| **Seamless Interaction** (Meta, 4,000 h dyadic, CC BY-NC, HF ungated) | Per-participant channels with *automatic* VAD and WhisperX-style word times; the human annotations are behavioural. 27 TB total; known duplicate/mismatched participant ids. **Sample check (12 participants of `naturalistic/dev/0000/0000.tar`):** 5-11% of VAD time is silent on the participant's own denoised channel (about as tight as PriMock57's human labels), little audible activity outside the VAD, but one participant has no VAD speech at all in 198 s, ASR word times fall outside the VAD by up to 14 s per file, and partners are stored in different shards (pairing needs `interactions.csv`) | Large-scale 2-speaker training data with decent automatic labels; not a benchmark |
| **M3SD / MISP-M3SD** (770 h, 16 languages) | Labels are automatic audio-visual pseudo-labels | Pre-training |
| **Buckeye Corpus** (Ohio State, free registration) | Sociolinguistic interviews where only the interviewee is transcribed: interviewer speech is unlabelled | Single-speaker word alignment |
| **Fareez et al. 2022 OSCE interviews** (272 simulated respiratory consultations, figshare) | Transcripts carry speaker labels but no timestamps | Medical ASR / NLP; would need forced alignment |
| **Earnings-22** (125 calls, CC BY-SA) | Speaker labels in `.nlp` but no token or segment timings, no RTTMs | Speaker-attributed ASR; align yourself |
| **SCOTUS oral arguments** (Oyez; public-domain audio, ~8,500 arguments) | Turn timestamps come from Oyez's transcript-to-audio sync (no overlap, coarse; some recordings re-transcribed with Whisper in community packs) | Court-domain long-form tests at a generous collar |
| **YODAS / Emilia / podcast scrapes** | Automatic segmentation only | Pre-training |

## D. Not English (or no separable English subset)

AliMeeting, AISHELL-4, MISP 2021-2025, RAMC (Mandarin); DISPLACE 2023/2024 (code-mixed Indian languages and Indian
English, CC BY 4.0 on Zenodo, not separable by recording); Indic DiarBench (22 Indian languages, 2026);
REPERE / ESTER / ETAPE (French); Albayzin (Spanish). AVA-AVD and MSDWild are multilingual but have a clearly
separable English subset (derived here with Whisper LID), so they are in the main catalog.

## E. Synthetic / simulated (marked as such)

- **LibriCSS**: in the main catalog, marked SYNTHETIC (real room re-recording of simulated meetings).
- **LibriMix / SparseLibriMix** (<https://github.com/JorisCos/LibriMix>): fully synthetic mixtures with exact labels
  from scripts; SparseLibriMix has controlled sparse overlap. Generate locally (CC BY 4.0 sources).
- **LibriheavyMix** (2024, 20,000 h), **FastMSS** / **NeMo multispeaker simulator**: simulated conversations from
  single-speaker corpora with exact labels. Training only; they say nothing about real-conversation ground truth.
- Many "synthetic-speaker-diarization-dataset-*" repos on the HF Hub (TTS or concatenation): training only.
