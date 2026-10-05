#!/bin/bash
# Nemotron 3 Diarization on every catalogued dataset, from the normalized data.
# Results (summary JSON/MD per dataset/view) go to results/nemotron/<dataset>.<view>/;
# hypotheses and frame probabilities are cached under $DIARDS_WORK/nemotron/.
# Usage: bash scripts/run_nemotron_all.sh [dataset ...]
PY=${PY:-python}
run() {  # dataset view tag [extra args]  -> results/nemotron/<dataset>.<view><tag>/
  local d=$1 v=$2 t=$3; shift 3
  echo "=== $d / $v $*"
  $PY -m diards evaluate "$d" --view "$v" --out "results/nemotron/$d.$v$t" "$@" > /dev/null || echo "FAILED $d $v"
}
want() { [ $# -eq 0 ] && return 0; for x in "${SEL[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }
SEL=("$@")
want ami && { run ami sdm '' --split test; run ami ihm-mix '' --split test; }
want icsi && { run icsi ihm-mix '' --split test; run icsi sdm '' --split test; }
want notsofar1 && { run notsofar1 sc '' --split eval; run notsofar1 ihm-mix '' --split eval; }
want chime6 && { run chime6 farfield '' --split eval; run chime6 ihm-mix '' --split eval; run chime6 farfield .dev --split dev; }
want dipco && { run dipco farfield '' --split eval; run dipco ihm-mix '' --split eval; }
want libricss && { run libricss sdm '' --split eval; run libricss clean-mix '' --split eval; }
want voxconverse && run voxconverse default '' --split test
want callhome_eng && run callhome_eng default ''
want callfriend_eng && run callfriend_eng default ''
want earnings21 && run earnings21 default ''
want msdwild_en && run msdwild_en default '' --split few.val --split many.val
want ava_avd_en && run ava_avd_en default '' --split test --split val
want sbcsae && run sbcsae default ''
want maptask && run maptask default ''
want afrispeech_dialog && run afrispeech_dialog default ''
want primock57 && run primock57 mix ''
want easycom && run easycom glasses ''
echo ALLDONE
