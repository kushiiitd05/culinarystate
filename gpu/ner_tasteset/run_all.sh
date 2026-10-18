#!/usr/bin/env bash
# X8 NER sweep on the A100 server: 3 encoders x 5 seeds, one model family per GPU queue.
#   PY=/path/to/env/python bash run_all.sh            (from this directory; logs in runs/*.log)
set -euo pipefail
PY=${PY:-python}
mkdir -p runs
queue() {                       # $1 = GPU index, rest = models
  local gpu=$1; shift
  for m in "$@"; do
    lr=3e-5; [[ $m == *deberta* ]] && lr=2e-5
    for seed in 1 2 3 4 5; do
      name=$(basename "$m")_seed$seed
      [[ -f runs/$name.json ]] && continue           # resumable
      CUDA_VISIBLE_DEVICES=$gpu $PY train_ner.py --data TASTEset.csv --model "$m" --seed "$seed" --lr $lr \
        --epochs 10 --out runs > "runs/$name.log" 2>&1
    done
  done
}
queue 0 bert-base-cased roberta-base &
queue 1 microsoft/deberta-v3-base &
wait
echo done
