# Research notes (raw, chronological)

Working notes gathered while surveying candidates. The curated results live in the
dataset cards and README; this file keeps sources and first impressions.

## Model under test

- "Nemotron 3 Diarization" = `nvidia/Nemotron-3-Diarization` on Hugging Face, released 2026-09-23.
  Streaming Sortformer successor, up to 8 speakers, 100M params, 16 kHz mono input, license OpenMDW-1.1.
  Runs in NeMo (`SortformerEncLabelModel`, NeMo Speech v3.0, Python >= 3.12) and natively in HF Transformers
  (`AutoModelForAudioFrameClassification`, install transformers from source).
  Baseline/predecessor: `nvidia/diar_streaming_sortformer_4spk-v2.1`.
- Official eval protocol: NeMo `e2e_diarize_speech.py`, collar 0 (0.25 for CALLHOME), overlap included.
- TRAINING DATA OVERLAP (contamination risk for our benchmark): Fisher Eng, AMI train+dev (forced-aligned),
  ICSI (full!), VoxConverse v0.3 dev AND test, DIHARD III dev, CALLHOME (NIST SRE2000) part 1, DiPCo dev,
  NOTSOFAR1 train+dev, DISPLACE 2024 dev+eval, AliMeeting train, AISHELL-4 train, YODAS pseudo-labels,
  LibriSpeech-based simulation. => only AMI test, NOTSOFAR eval, DiPCo eval, CHiME-6, etc. are clean.
- Model card AMI/AliMeeting/NOTSOFAR evals use forced-alignment references:
  nttcslab-sp/diar-forced-alignment (AMI, AliMeeting), popcornell/FastMSS resources (NOTSOFAR1 MFA RTTMs).

## Annotation-quality literature

- arXiv 2507.09226 (ASRU 2025) "Can We Really Repurpose Multi-Speaker ASR Corpus for Speaker Diarization?":
  ASR-oriented corpora (AMI, AliMeeting, AISHELL-4, DiPCo, NOTSOFAR-1) use loose segment boundaries;
  replacing AMI original labels with forced-aligned labels gives ~21-25% DER gap (mostly missed/FA speech
  from merged pauses). Diarization-oriented corpora: DIHARD III (split at >200 ms pauses), VoxConverse,
  MSDWild (>250 ms), CHiME-6 (forced alignment + 300 ms).

## Candidates (first pass)

- CallHome English via TalkBank: HF `talkbank/callhome` (config `eng`, 140 calls, gated auto-approve,
  CC BY-NC-SA 4.0). Only the transcribed parts kept (diarizers preprocessing). Telephone, 2+ speakers.
  Also `talkbank/callfriend` (eng-n 31, eng-s 9). Hasan's HF account already has access.
- SBCSAE: OpenSLR SLR155 (6.1 GB tar.gz, 60 recordings ~20 min, 22.05 kHz stereo),
  CC BY-ND 3.0 US (ND: do not redistribute derived RTTMs; ship scripts). Intonation-unit timestamps.
- CANDOR: 1656 Zoom conversations, 850 h, CC BY-NC; transcripts are AWS Transcribe ASR (weak GT);
  access needs BetterUp approval + TalkBank email. -> weak, not main catalog.
- CHiME-6: OpenSLR SLR150, CC BY-SA 4.0. train 97 GB, dev 11 GB, eval 12 GB, transcriptions 2.4 MB.
  CHiME-5 re-licensed CC BY-SA 4.0 since 2024-01-01.
- DiPCo: Zenodo 8122551, 13.4 GB, CDLA-Permissive-1.0, 10 sessions x 4 speakers, manual transcripts,
  segments up to 10-15 s (loose boundaries).
- NOTSOFAR-1: CC BY 4.0, Azure blob / HF `microsoft/NOTSOFAR`, 315 meetings ~6 min, 4-8 attendees,
  word-level alignment in JSON GT.
- Argmax OpenBench uses HF mirrors: argmaxinc/icsi-meetings, chime-6, ava-avd, earnings21, ali-meetings,
  aishell-4. diarizers-community/ami, voxconverse, simsamu.
- AMI variants: (1) original NXT manual annotations v1.6.2 (words + segments); (2) BUTSpeechFIT/pyannote
  AMI-diarization-setup: RTTMs derived from manual word timings ("only_words" preferred,
  "word_and_vocalsounds" inconsistent), Full-corpus-ASR partition; (3) nttcslab-sp/diar-forced-alignment
  (MFA v3 forced alignment, used by NVIDIA model card).
- ICSI: CC BY 4.0, 75 meetings ~72 h; HF mirror argmaxinc/icsi-meetings. Nemotron trained on ICSI (full) -> contaminated.
- MSDWild: 3143 clips, 80 h, multilingual vlogs, no language labels; wav 7.56 GB on Google Drive;
  research-only license agreement (MSDWILD_license_agreement.pdf). English subset must be derived via LID
  (SDBench used Whisper large-v3 LID for the same purpose). Disregard ~90 files with negative names.
- AVA-AVD: 117 movies x 3 5-min clips = 351 clips (243/54/54 train/val/test), multilingual movies,
  RTTMs in zcxu-eric/AVA-AVD repo, videos from CVDF AVA mirror. HF mirror argmaxinc/ava-avd.
- Earnings-21: revdotcom/speech-datasets, CC BY-SA 4.0, 44 calls / 39 h, RTTMs added 2023-12 (method
  undocumented; probably alignment of human transcripts). 2024-08 fix for 4341191 off-by-one labels.
  Earnings-22: 125 calls / 119 h, no RTTMs.
- American-Life-Podcast (Mao et al. 2020, arXiv 2005.08072): This American Life transcripts aligned to audio;
  used in SDBench; median 19 speakers; audio copyrighted.
- Seamless Interaction (Meta 2025, facebook/seamless-interaction): 4000+ h dyadic, CC BY-NC 4.0,
  time-aligned transcripts + VAD (likely automatic) -> check.
- CHiME-9 ECHI: 48 sessions / 29 h, 4 people at a table (cafe noise), Aria + hearing aids + close-talk,
  HF gated with DUA (academic only), dev 23.6 GB.
- MMCSG (CHiME-8 T3): 2-party conversations, Aria glasses, train 8.5 h / dev 8.4 h / test 9.4 h, manual annotations.
- AfriSpeech-Dialog: HF intronhealth/afrispeech-dialog, CC BY-NC-SA 4.0, 50 convs (20 medical, 30 general),
  ~6-7 h, manual turns + timestamps; African-accented English. Paper arXiv 2502.03945; diarization study 2509.21554.
- Fareez et al. 2022 (Sci Data) OSCE simulated interviews: 272 mp3 + text transcripts on figshare
  (likely no timestamps -> unusable for diarization scoring without alignment).
- HCRC Map Task: annotations CC BY 4.0 (NXT v2.1, 12 MB), audio free from groups.inf.ed.ac.uk/maptask
  (stereo mixes of 2 mono close-talk channels, 20 kHz). 128 dialogues, 2 speakers. Timing method to check.
- SCOTUS (Oyez): ~8.5k arguments, public-domain audio, Oyez turn timestamps (alignment quality unknown,
  no overlap). vcon-dev/vcon-supreme-court-arguments packs it. Candidate for court domain.
- DISPLACE 2024: Zenodo 14097187, CC BY 4.0, Indian languages + Indian English code-mixed -> not English-only.
  Nemotron trained on DISPLACE 2024 dev+eval.

## Second pass (2026-10-05 afternoon)

- CHiME-6: two references, "annotation RTTM" (human utterances) and "alignment RTTM" (GMM-HMM forced alignment,
  official Track 2; github.com/nateanl/chime6_rttm). CHiME-7/8 UEMs start at the first annotated utterance because the
  enrolment minute is unannotated but was scored in CHiME-6. CHiME6_falign repo adds FA for train.
  Tar member prefix is `CHiME6_<split>/CHiME6/audio/<split>/`. ELDA mirror (openslr.elda.org) ~6 MB/s vs ~1 MB/s main.
- DiPCo: CHiME-style JSON, per-device times identical; segments up to 10-15 s (README). Zenodo ~1 MB/s.
- NOTSOFAR-1 on HF microsoft/NOTSOFAR (ungated): per meeting close_talk/CT_*.wav, sc_*/ch0.wav, mc_*/ch*.wav,
  gt_transcription.json (utterances + word_timing), devices.json, gt_meeting_metadata.json.
  FastMSS sessions MFA RTTMs cover dev + 80-meeting eval_small (MTG ids).
- ICSI NXT: Segments/*.segs.xml with participant ids; 9-13% of words lack timings; many segments are noise-only.
- Earnings-21 RTTMs added 2023-12 ("Adding RTTM files for DER evaluation"), method undocumented.
- AfriSpeech-Dialog: transcript times "MM:SS:cc" hand-typed, cc clusters at 96-100/00-04 (=> ~1 s precision);
  46/49 files have times (card claims 30).
- PriMock57: channels isolated by ~50 dB -> per-channel activity is a reliable reference (see PRIMOCK57.md).
- EasyCom: files in Git LFS, fetchable individually; VAD in 20 fps frames; 1-minute files; some JSON in cp1252.
- MMCSG (CHiME-8 T3): registration needed; official note says RTTM segments "might often overestimate the actual
  speaking time"; word TSVs are forced-aligned.
- CHiME-9 ECHI: HF gated (manual DUA) -> 403. CHiME-10 Task 1 = ECHI-2.
- CHiME-9 MCoRec: HF gated DUA, ~15 h total, up to 4 simultaneous conversations; language not stated.
- Fearless Steps: CC BY 4.0, NIST OpenSAT registration, 80 h GT (FSC P3), 8 kHz mission audio.
- MLC-SLM: ~500 h English 2-speaker (Nexdata registration); eval GT on HF bsmu/MLC-SLM-Eval (CC BY-SA 4.0, text only).
- M3SD (Igor97/MISP-M3SD): 770 h, 16 languages, automatic audio-visual pseudo-labels -> excluded.
- Seamless Interaction (facebook/seamless-interaction): ungated CC BY-NC, 27 TB, per-participant denoised audio,
  automatic VAD (100 Hz) + transcripts; human annotations are behavioural only.
- This American Life (Mao et al. 2020): Kaggle transcripts+alignments, audio links (many dead), 637 h.
- SCOTUS/Oyez: API api.oyez.org; turns tile the timeline, no overlap; Oyez content CC BY-NC 4.0.
- Nemotron 3 Diarization Transformers port: offline mode == 30.4 s NeMo config (chunk 340/rc 40/fifo 40/upd 300).
