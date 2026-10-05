#!/bin/bash
# Statistics + ground-truth validation (with energy-VAD cross-check) for every prepared dataset.
# The VAD check uses the close-talk / clean view where one exists (energy VAD is meaningless on far-field audio).
# Usage: bash scripts/validate_all.sh [dataset ...]
PY=${PY:-python}
declare -A VADVIEW=( [ami]=ihm-mix [icsi]=ihm-mix [notsofar1]=ihm-mix [chime6]=ihm-mix [dipco]=ihm-mix [libricss]=clean-mix )
DATASETS=${@:-ami icsi notsofar1 chime6 dipco libricss voxconverse callhome_eng callfriend_eng earnings21 msdwild_en ava_avd_en sbcsae maptask afrispeech_dialog primock57}
for d in $DATASETS; do
  echo "=== $d"
  $PY -m diards stats "$d" --out results/stats > /dev/null || { echo "stats failed for $d"; continue; }
  v=${VADVIEW[$d]}
  $PY -m diards validate "$d" ${v:+--view $v} --vad --out results/validation > /dev/null
  echo "done $d"
done
