# Results

Everything here was produced by the code in this repo from the normalized datasets.

| folder | content | produced by |
|---|---|---|
| `stats/` | per-dataset statistics (`stats.<dataset>.{md,json}`; JSON has per-session rows) | `python -m diards stats <dataset> --out results/stats` |
| `validation/` | ground-truth validation reports incl. energy-VAD cross-check (`validation.<dataset>.<view>.{md,json}`) | `python -m diards validate <dataset> [--view V] --vad --out results/validation` |
| `nemotron/<dataset>.<view>[.<subset>]/` | Nemotron 3 Diarization DER/JER per session and overall, for every reference variant, collars 0 and 0.25 s (`results.{md,json}`) | `python -m diards evaluate <dataset> --view V [--split S] --out results/nemotron/<dataset>.<view>` |
| `primock57/` | PriMock57 ground-truth audit + channel-activity RTTMs (CC BY 4.0) | `python scripts/analyze_primock57.py` |
| `SUMMARY.md` | cross-dataset tables (auto-generated) | `python scripts/make_cards.py` |

## Exact commands

```bash
# environment used: Windows 11, conda env (Python 3.12.15), torch 2.11.0+cu128, transformers 5.19.0.dev0 (git),
# pyannote.metrics 4.1, RTX 5080 16 GB, DIARDS_BASE=D:\diarization-data
for d in ami icsi notsofar1 chime6 dipco libricss voxconverse callhome_eng callfriend_eng earnings21 \
         msdwild_en ava_avd_en sbcsae maptask afrispeech_dialog primock57 easycom scotus; do
  python -m diards prepare $d
done
PY=python bash scripts/validate_all.sh        # stats + validation (+VAD on the close-talk view where one exists)
PY=python bash scripts/run_nemotron_all.sh    # Nemotron on the evaluation subsets listed in the script
python scripts/analyze_primock57.py --hyp-dir $DIARDS_BASE/work/nemotron/primock57.mix/hyp
python scripts/make_cards.py                  # fills dataset cards, README catalog and SUMMARY.md
```

## Evaluation protocol (Nemotron 3 Diarization)

| item | value |
|---|---|
| model | `nvidia/Nemotron-3-Diarization`, HF revision `f667ed73aee57d40cc39428eb768b4fd87a0a29e` |
| implementation | Hugging Face Transformers port (`AutoModelForAudioFrameClassification`), offline mode |
| streaming settings | chunk_length 340, chunk_right_context 40, fifo_length 40, speaker_cache_update_period 300, speaker_cache_length 264 (80 ms frames) = the model card's "very high latency (30.4 s)" configuration |
| post-processing | none: per-frame sigmoid > 0.5 at 10 ms resolution (as `processor.extract_speaker_dict`) |
| precision / hardware | fp32, batch 1, RTX 5080 |
| audio | normalized 16 kHz mono WAV of the given view |
| reference | primary RTTM of the normalized dataset, plus every `rttm_alt/` variant (reported separately) |
| UEM | per-session UEM from the normalized dataset (see each card) |
| overlap | included in scoring |
| collar | 0 and 0.25 s *half-width* (md-eval / NeMo convention; pyannote receives 2 x collar) |
| metrics | pyannote.metrics `DiarizationErrorRate` and `JaccardErrorRate`, accumulated over sessions; speaker-count accuracy and MAE as in NeMo |

Hypothesis RTTMs and 10 ms speaker probabilities are cached under `$DIARDS_BASE/work/nemotron/<dataset>.<view>/`
and are not committed (they are derived from audio with assorted licences).

Note on "scored ref speaker-time h" in the tables: pyannote's DER denominator counts overlapped speech once per
active speaker, so it can exceed the audio duration of heavily overlapped data.

## Practical notes

- **Memory for long recordings.** The Transformers offline mode computes the spectrogram of the whole recording
  at once: a 100-minute recording needs about 2.4 GB of RAM for the STFT alone (one SCOTUS run failed with
  `not enough memory` while other jobs were running and succeeded on a rerun). The GPU part is chunked and small.
- **Speed.** ~800-1,100x real time on an RTX 5080 (fp32, batch 1); DER scoring with pyannote.metrics on long, heavily
  overlapped sessions (CHiME-6) takes longer than inference.
- **Caching.** Hypotheses are cached per session; re-running `diards evaluate` only re-scores (e.g. after adding an
  alternative reference). Delete `$DIARDS_BASE/work/nemotron/<dataset>.<view>/hyp` to recompute.
