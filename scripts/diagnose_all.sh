#!/bin/bash
# Model-vs-reference error attribution + Whisper audit of long audible false alarms,
# for every dataset/view with cached Nemotron hypotheses.
# Usage: bash scripts/diagnose_all.sh [dataset.view ...]
PY=${PY:-python}
WORK=$($PY -c "from diards.config import work_root; print(work_root().as_posix())")
TAGS=${@:-$(ls $WORK/nemotron/)}
for tag in $TAGS; do
  name=${tag%%.*}; view=${tag#*.}
  echo "=== $name / $view"
  $PY -m diards.diagnose "$name" --view "$view" --out results/diagnosis > /dev/null || { echo "FAILED diagnose $tag"; continue; }
  $PY scripts/audit_false_alarms.py "$name" --view "$view" 2>/dev/null | tail -1 || echo "FAILED audit $tag"
done
echo ALLDONE
