#!/bin/bash
# VAD-assisted Nemotron variants (post-hoc, CPU) for every results/nemotron/<tag> evaluation, several tags in
# parallel. Needs the VAD cache (scripts/vad_compute_all.sh) and the main agent's cached Nemotron outputs.
# Output: results/vad/pipeline/posthoc.<tag>.json (existing outputs are skipped; delete to recompute).
# Usage: JOBS=6 bash scripts/vad_pipeline_all.sh [tag ...]
PY=${PY:-python}
JOBS=${JOBS:-6}
OUT=results/vad/pipeline
mkdir -p $OUT
TAGS=${@:-$(ls results/nemotron/ | while read t; do [ -f results/nemotron/$t/results.json ] && echo $t; done)}
for t in $TAGS; do [ -f $OUT/posthoc.$t.json ] || echo $t; done |
  xargs -P "$JOBS" -I{} sh -c "$PY -m diards.vad_assist posthoc --tags {} --out $OUT > $OUT/log.{}.txt 2>&1 || echo FAILED {}"
echo ALLDONE
