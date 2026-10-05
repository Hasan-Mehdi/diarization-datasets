# HCRC Map Task Corpus

128 unscripted task-oriented dialogues (~15 h) between pairs of Glasgow university students. One "giver" guides a
"follower" along a route on a map, with or without eye contact. Each speaker was recorded on a separate close-talk
channel in a studio, and every word is time-stamped, with silences and noises explicitly marked. It is the
cleanest free two-speaker reference set: clean channels, word timing, natural (if task-bound) overlap and
backchannels.

<!-- auto:meta -->
| | |
|---|---|
| License | CC-BY-NC-SA-2.5 (audio + NXT zip); download page states CC BY 4.0 for annotations v2.1 ([link](https://groups.inf.ed.ac.uk/maptask/maptasknxt.html)) |
| Annotations redistributable here | no (scripts only) |
| Access | Free download, no registration. |
| Source version used | NXT annotations v2.1 (2011-02-10); signals/dialogues *.mix.wav |
| Domain | two-person task dialogue (close-talk) |
| Views (normalized) | `default`: Official stereo mix of the two close-talk channels, downmixed to mono 16 kHz |
| Reference used as primary RTTM | Word-level timed units per speaker (silence and noise also time-marked). |
| Ground-truth rating | **A-** - Each speaker on a separate close-talk channel with word-level timings, silences explicitly marked, overlap naturally represented; task-oriented (not free) conversation, studio audio. |
| Prepared splits (sessions) | all: 128 |
<!-- /auto:meta -->

## Source and access

- <https://groups.inf.ed.ac.uk/maptask/maptasknxt.html>: NXT annotation zip v2.1 (12 MB) and
  `signals/dialogues/<id>.mix.wav` (stereo mix of the two speaker channels, 20 kHz). No registration.
- License: the download page states CC BY 4.0 for the v2.1 annotations; the `00LICENSE.html` inside the zip and
  in the audio folder is CC BY-NC-SA 2.5. Treat the stricter terms (non-commercial, share-alike) as binding.
- LDC also distributes it (LDC93S12).

## Annotation methodology

Orthographic transcription per speaker channel with word-level "timed units" (`<tu start end>`), plus explicitly
timed silences (`<sil>`) and noises (`<noi>`, e.g. breaths). The reference merges a speaker's words across pauses
< 0.2 s (DIHARD convention). Speaker ids are the corpus' global participant ids, so the same person keeps the
same id across their four dialogues.

## Known issues and errata

- Task dialogue: speakers talk about landmarks on a map. It is natural in timing and overlap but narrow in content
  and register (Scottish English).
- The corpus README notes NXT data-model irregularities for tokens/POS layers; they do not affect the timed units.
- 20 kHz studio audio, very clean; easier than real-world phone or meeting audio.

## Verified statistics

<!-- auto:stats -->
_Statistics not computed yet._
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
_Validation not run yet._
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
_Not evaluated yet._
<!-- /auto:nemotron -->

### Model error or reference error?

<!-- auto:diagnosis -->
_Not run yet._
<!-- /auto:diagnosis -->

## Quality rating

**A-.** Separate close-talk channels plus word-level timing gives diarization-grade references with natural
overlap and backchannels. Minus: narrow task domain, studio audio, license ambiguity (use non-commercially).

## Download and prepare

<!-- auto:prepare -->
```bash
python -m diards prepare maptask            # download (resumable) + normalize (idempotent)
python -m diards validate maptask --vad     # ground-truth checks
python -m diards stats maptask
python -m diards export maptask --format nemo      # or pyannote / lhotse
python -m diards evaluate maptask --view default  # Nemotron 3 Diarization + DER/JER
```

```python
from diards import load_dataset
for s in load_dataset("maptask", view="default"):
    s.audio_path, s.segments, s.uem, s.words
```
<!-- /auto:prepare -->

## Citation

A. H. Anderson et al., "The HCRC Map Task Corpus", Language and Speech 34(4), 1991.
