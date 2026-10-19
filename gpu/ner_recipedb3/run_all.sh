#!/usr/bin/env bash
# RecipeDB3 NER matched reproduction (theirs, seed 48 = their random_state) + clean grouped re-evaluation, 5 seeds each.
#   PY=/path/to/python bash run_all.sh   (from this directory; data file copied alongside; logs in runs/)
set -euo pipefail
PY=${PY:-python}
D=Ingredient_Annotated_Dataset.csv
mkdir -p runs
CUDA_VISIBLE_DEVICES=0 bash -c "for s in 48 1 2 3 4; do [[ -f runs/theirs_seed\$s.json ]] || $PY repro.py --data $D --protocol theirs --seed \$s > runs/theirs_seed\$s.log 2>&1; done" &
CUDA_VISIBLE_DEVICES=1 bash -c "for s in 1 2 3 4 5; do [[ -f runs/clean_seed\$s.json ]] || $PY repro.py --data $D --protocol clean --seed \$s > runs/clean_seed\$s.log 2>&1; done" &
wait
echo done
