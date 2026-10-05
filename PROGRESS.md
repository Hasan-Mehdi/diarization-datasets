# PROGRESS

Running log for the unattended build of this repo. Work is tracked here, not in GitHub issues (by design).

## Current status

_Last updated: 2026-10-05 13:28 EDT (from `date`)_

- **Now doing:** writing per-dataset recipes in the `diards` package and running them in the background
  (AMI, VoxConverse, CallFriend done/near-done; NOTSOFAR-1, Earnings-21, ICSI running; CHiME-6, DiPCo, SBCSAE downloading).
- **Done so far:** private repo; conda env on D: (Python 3.12, PyTorch 2.11+cu128, RTX 5080 OK);
  model identified = `nvidia/Nemotron-3-Diarization` (2026-09-23), runs via Transformers on the GPU at ~800x real time;
  normalized layout + loader + validator + stats + DER/JER scorer + Nemotron harness working end to end
  (first result: AMI SDM test, 2 meetings: 8.8% DER vs forced-aligned reference, 17-19% vs manual-derived references).
- **Next:** CHiME-6 / DiPCo / MSDWild / AVA-AVD / SBCSAE / Map Task / AfriSpeech-Dialog / PriMock57 / LibriCSS recipes;
  NeMo / pyannote / Lhotse exports + tests; full Nemotron runs; dataset cards; PriMock57 analysis.
- **Needs Hasan (small, optional):** CallHome English (TalkBank) is gated on Hugging Face and the form asks for company
  and country, which I should not invent. To enable it: open https://huggingface.co/datasets/talkbank/callhome while
  logged in as `Hmehdi515`, click "Agree and access", then run `python -m diards prepare callhome_eng`.
  CallFriend English (same TalkBank family) is ungated and already verified.

## Environment decisions

- Data root (audio, caches, envs, model weights): `D:\diarization-data` (C: has ~30 GB free).
  Normalized datasets: `D:\diarization-data\normalized\<dataset>\`; raw downloads: `D:\diarization-data\raw\<dataset>\`.
- Caches: `HF_HOME`, `TORCH_HOME`, `PIP_CACHE_DIR`, `TEMP/TMP` all point under `D:\diarization-data\cache`.
  The HF token from Hasan's other cache (`D:\hf-cache\token`, account `Hmehdi515`) was copied into the new HF_HOME.
- Conda env: `D:\diarization-data\envs\diar` (Python 3.12, because NeMo Speech 3.x requires >= 3.12), not the base env.
- PyTorch 2.11.0+cu128 (supports sm_120 / Blackwell). Transformers 5.19.0.dev0 from source (Nemotron 3 Diarization support).
- WSL is not installed; everything runs natively on Windows.
- Nemotron inference uses the Transformers port in offline mode, which chunks exactly like the model card's
  30.4 s "very high latency" NeMo configuration (chunk 340, right context 40, FIFO 40, update period 300, cache 264).
- Slow official mirrors are replaced by verified mirrors where available (VoxConverse audio from the CC-BY HF mirror:
  the Oxford server delivered ~0.25 MB/s).

## Status

| Area | State |
|---|---|
| Repo skeleton + GitHub (private) | done |
| Candidate research | first pass done (~35 corpora, `docs/research_notes.md`), continuing |
| Conda env + PyTorch CUDA | done |
| Nemotron install (Transformers) | done; NeMo install optional, not attempted yet |
| Normalized layout + `diards` package (prepare/validate/stats/evaluate) | done (core), recipes in progress |
| Recipes verified | ami, voxconverse, callfriend_eng; running: notsofar1, earnings21, icsi |
| PriMock57 ground-truth analysis | not started |
| Exports (NeMo / pyannote / Lhotse) + tests | not started |
| Nemotron evaluation | harness done; 2-meeting AMI smoke test done |
| Dataset cards | not started |
| README catalog + recommendations | not started (final polish at the end, per Hasan) |

## Log

Times before 13:27 are approximate (reconstructed from commit times).

- ~12:56: created repo skeleton and this file; pushed private repo `Hasan-Mehdi/diarization-datasets`.
- ~13:00: conda env created (first attempt landed in a mangled path `D:\diarization-dataenvsdiar` because of
  bash backslash escaping; deleted it and recreated with PowerShell). Python 3.12 instead of 3.11 because NeMo needs it.
- ~13:00: found the model ("Nemotron 3 Diarization" = `nvidia/Nemotron-3-Diarization`).
- ~13:04: INBOX message from Hasan (13:05: status block + normalization spec) read and acknowledged; adopting it.
- ~13:16: committed the `diards` package (layout, loader, AMI + VoxConverse recipes, validator, stats, scorer, eval).
- 13:27: INBOX message (13:08: use real timestamps) read and acknowledged; log times corrected to commit times.
- 13:27: VoxConverse (448 files), CallFriend English (40 calls) normalized, validated (with energy VAD) and profiled.
  CallHome English blocked on the HF access form (see "Needs Hasan").

## Skipped / blocked (with reasons)

- CallHome English (TalkBank): HF gated form asks for company/country; TalkBank's own media server needs a login.
  Recipe written (`callhome_eng`), cannot be verified until Hasan clicks through.

## Open items

- Everything not marked done in the status table above.
