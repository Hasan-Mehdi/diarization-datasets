#!/bin/bash
# Silero / WebRTC / energy VAD on every normalized dataset (cached under $DIARDS_VAD_STUDY/vad/, default
# <base>/vad-study/vad/). CPU only; resumable (finished sessions are skipped).
# Audit views: the close-talk view where a dataset has one, else its default view (all sessions).
# Far-field views: the subsets Nemotron was evaluated on (for the VAD-assisted diarization experiments).
# Usage: WORKERS=8 bash scripts/vad_compute_all.sh [dataset ...]
PY=${PY:-python}
W=${WORKERS:-8}
want() { [ ${#SEL[@]} -eq 0 ] && return 0; for x in "${SEL[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }
SEL=("$@")
run() { $PY -m diards.vads "$@" --workers "$W" || echo "FAILED $*"; }
want primock57 && { run primock57 --view mix; run primock57 --channels; }
want maptask && run maptask
for d in afrispeech_dialog callfriend_eng callhome_eng scotus sbcsae ava_avd_en msdwild_en earnings21 voxconverse; do
  want $d && run $d
done
want easycom && run easycom --view glasses
want chime6 && { run chime6 --view ihm-mix; run chime6 --view farfield; }
want dipco && { run dipco --view ihm-mix; run dipco --view farfield; }
want libricss && { run libricss --view clean-mix; run libricss --view sdm; }
want notsofar1 && { run notsofar1 --view ihm-mix; run notsofar1 --view sc; }
want ami && { run ami --view ihm-mix --split test; run ami --view sdm --split test; run ami --view ihm-mix; }
want icsi && { run icsi --view ihm-mix --split test; run icsi --view sdm --split test; run icsi --view ihm-mix; }
echo ALLDONE
