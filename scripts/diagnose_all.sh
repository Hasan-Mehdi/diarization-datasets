#!/bin/bash
# Model-vs-reference error attribution for every evaluated dataset/view (needs cached Nemotron hypotheses).
PY=${PY:-python}
for d in $(ls -d $(${PY} -c "from diards.config import work_root; print(work_root().as_posix())")/nemotron/*/ 2>/dev/null); do
  tag=$(basename "$d"); name=${tag%%.*}; view=${tag#*.}
  echo "=== $name / $view"
  $PY -m diards.diagnose "$name" --view "$view" --out results/diagnosis > /dev/null || echo "FAILED $name $view"
done
echo ALLDONE
