# HCRC Map Task Corpus

128 unscripted task-oriented dialogues (~15 h) between pairs of Glasgow university students. One "giver" guides a
"follower" along a route on a map, with or without eye contact. Each speaker was recorded on a separate close-talk
channel in a studio, and every word is time-stamped, with silences and noises explicitly marked. It is the
cleanest free two-speaker reference set: clean channels, word timing, natural (if task-bound) overlap and
backchannels.

<!-- auto:meta -->
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
<!-- /auto:stats -->

## Ground-truth validation

<!-- auto:validation -->
<!-- /auto:validation -->

## Nemotron 3 Diarization

<!-- auto:nemotron -->
<!-- /auto:nemotron -->

## Quality rating

**A-.** Separate close-talk channels plus word-level timing gives diarization-grade references with natural
overlap and backchannels. Minus: narrow task domain, studio audio, license ambiguity (use non-commercially).

## Download and prepare

<!-- auto:prepare -->
<!-- /auto:prepare -->

## Citation

A. H. Anderson et al., "The HCRC Map Task Corpus", Language and Speech 34(4), 1991.
