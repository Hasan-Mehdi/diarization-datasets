# LibriCSS (SYNTHETIC: re-recorded simulated meetings)

60 ten-minute "meetings" built by concatenating LibriSpeech utterances of 8 speakers with a controlled amount of
overlap (0%, with short or long silences, and 10-40%), played through loudspeakers in a real meeting room and
recorded with a 7-channel array. The reference is exact by construction, but the conversation is fake: read
speech, no natural turn-taking, backchannels or laughter. **Use it to study overlap and far-field effects, not as
evidence of real-conversation performance.**

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-4.0 (LibriSpeech-derived) ([link](https://creativecommons.org/licenses/by/4.0/)) |
| Annotations redistributable here | yes |
| Access | Free download (Google Drive, 6.4 GB). |
| Source version used | for_release.zip (Google Drive id 1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l) |
| Domain | synthetic meetings (read speech replayed in a room) |
| Views (normalized) | `sdm`: Channel 0 of the 7-channel room recording; `clean-mix`: Original digital mixture before playback |
| Reference used as primary RTTM | Exact playback times of each LibriSpeech utterance (by construction). |
| Ground-truth rating | **S (synthetic)** - Timing is exact by construction but covers whole read-speech utterances (with their silences); no natural turn-taking, backchannels or laughter; useful for controlled overlap studies only. |
| Prepared splits (sessions) | dev: 6, eval: 54 |
<!-- /auto:meta -->

## Source and access

- <https://github.com/chenzhuo1011/libri_css>, data `for_release.zip` (6.4 GB) on Google Drive
  (id `1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l`). LibriSpeech-derived, CC BY 4.0.
- Lhotse recipe: `lhotse.recipes.prepare_libricss`.

## Annotation methodology

`transcription/meeting_info.txt` lists, for every played utterance, its start/end time in the session, the
LibriSpeech speaker id and the text. These are the exact playback times. They include the leading and trailing
silences of each LibriSpeech utterance, so segments are slightly longer than the actual speech.

## Known issues and errata

- Read speech replayed by loudspeakers: no real interaction, loudspeaker directivity instead of human heads.
- Segment edges include LibriSpeech's own silence padding.
- Conditions: `0L` / `0S` (no overlap; long/short silences), `OV10`-`OV40` (target overlap ratio). Session 0 of each
  condition is used as dev, sessions 1-9 as eval.

## Verified statistics

<!-- auto:stats -->
| split | sessions | hours | speech h | speech ratio | overlap ratio | >=3-spk ovl | speakers min/med/max | segment p5/p50/p95 s | segs < 0.2 s | same-spk pause p50 s | spk changes / min |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| dev | 6 | 1.01 | 0.94 | 0.94 | 0.103 | 0.0002 | 8/8/8 | 1.913/5.505/16.077 | 0.0 | 25.95 | 7.65 |
| eval | 54 | 9.09 | 8.49 | 0.935 | 0.103 | 0.0015 | 8/8/8 | 1.919/5.88/19.25 | 0.0 | 30.394 | 7.16 |
| ALL | 60 | 10.1 | 9.43 | 0.935 | 0.103 | 0.0013 | 8/8/8 | 1.911/5.85/19.18 | 0.0 | 29.942 | 7.21 |

Computed by `python -m diards stats libricss` from the normalized primary reference inside each UEM (overlap ratio = time with >= 2 speakers / speech time). Source: [`results/stats/stats.libricss.md`](../../results/stats/stats.libricss.md).
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
View `clean-mix`: 60 sessions, **0 errors**, 0 warnings (normalized files); 0 sessions had problems in the ORIGINAL labels that normalization fixed.
- energy-VAD cross-check: energy speech outside the reference (+/-0.25 s, >= 0.5 s chunks) = 0.2% of reference speech; reference speech without energy = 1.5%. Most-flagged sessions: `libricss__0L_session8` (0.00), `libricss__0L_session2` (0.00), `libricss__0L_session5` (0.00), `libricss__0L_session3` (0.00), `libricss__0L_session4` (0.00)
- full report: [`results/validation/validation.libricss.clean-mix.md`](../../results/validation/validation.libricss.clean-mix.md)
- **Silero VAD x2 audit** (view `clean-mix`, from the [VAD study](../../docs/silero_vad_study.md)): 6.67% of reference speech is silence to Silero (padding / pauses labelled as speech; collar 0); Silero speech outside the reference = 0.0% of reference speech.
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
| view (subset) | sessions | hours | reference | DER % (collar 0) | FA | Miss | Conf | JER % | DER % (collar 0.25) | spk-count acc |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| clean-mix (eval) | 54 | 9.08 | primary | **5.09** | 0.14 | 4.51 | 0.44 | 5.83 | 4.44 | 100% |
| sdm (eval) | 54 | 9.09 | primary | **14.30** | 0.58 | 8.21 | 5.52 | 20.33 | 13.02 | 69% |

Model `nvidia/Nemotron-3-Diarization` (Transformers port, offline 30.4 s chunking, threshold 0.5, no post-processing); pyannote.metrics, overlap scored, UEM applied, collar = half-width. Per-session tables: `results/nemotron/libricss.*/results.md`.
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
| hypothesis view | audio used for energy | sessions | missed speech % | ...in silence (reference padding) | ...with energy (model miss) | false alarm % | ...with energy (unlabelled sound?) | ...in silence (model) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| clean-mix | clean-mix | 54 | 3.98 | 0.27 | 3.71 | 0.09 | 0.07 | 0.03 |
| sdm | clean-mix | 54 | 7.38 | 0.26 | 7.11 | 0.32 | 0.18 | 0.14 |

Speech-detection errors of Nemotron (speaker-agnostic, primary reference, collar 0), as % of reference speech, split by whether the audio has energy there (`python -m diards.diagnose`; level threshold calibrated per session). "Miss in silence" is a lower bound on reference padding; "FA with energy" mixes unlabelled speech and non-speech sounds and needs listening (examples in `results/diagnosis/*.json`).

**Whisper audit of the longest audible false alarms (clean-mix):** 0 of 0 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (0 of 0 s).

**Time-offset check (clean-mix):** 0 of 54 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.0 s.

**Whisper audit of the longest audible false alarms (sdm):** 0 of 0 regions (>= 1 s) contain intelligible speech (>= 3 non-repetitive words; Whisper's loops on music/laughter are rejected), i.e. speech the reference does not label (0 of 0 s).

**Time-offset check (sdm):** 0 of 54 sessions look shifted against the audio (|best lag| >= 0.3 s and agreement gain >= 2 points); median best lag 0.05 s.
<!-- /auto:diagnosis -->

**Reading the LibriCSS numbers: exact labels, so the errors are the model's.** On the 54 eval sessions (room
recording, channel 0) DER is 14.3% at collar 0 and 13.0% at 0.25 s. The collar barely helps because the boundaries are
exact. The diagnosis confirms clean labels: no time shifts, essentially no missed speech in silence (0.3 points), no
audible unlabelled speech. The interesting pattern is by condition: the **no-overlap, long-silence sessions (0L) are
the worst (20.8%)**, versus 10-15% for the overlapped ones. In 0L the model reports only 6-7 of the 8 speakers and
merges voices (10-20% confusion per session). Eight read-speech voices taking isolated turns, separated by long
pauses, stress the arrival-order speaker cache more than overlap does. Overall the model finds exactly 8 speakers in
68% of sessions on the room recording. On the **clean digital mixture** of the same sessions DER is only 5.1% with
the correct speaker count in every session, so the merging is caused by the far-field room playback (reverberation
and loudspeaker colouring make voices harder to tell apart), not by the conversation structure alone. Synthetic, so
do not read this as real-meeting performance.


## Quality rating

**S (synthetic).** Exact by construction, but not natural conversation; rated separately from real data.

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare libricss            # download (resumable) + normalize (idempotent)
python -m diards validate libricss --vad     # ground-truth checks
python -m diards stats libricss
python -m diards export libricss --format nemo      # or pyannote / lhotse
python -m diards evaluate libricss --view sdm  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("libricss", view="sdm"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

Z. Chen et al., "Continuous speech separation: dataset and analysis", ICASSP 2020.
