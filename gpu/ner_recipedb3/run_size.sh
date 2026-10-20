#!/usr/bin/env bash
# SIZE-included variant (clean grouped protocol, 3 seeds) after the main 10 runs. Run from this directory: PY=... bash run_size.sh
set -euo pipefail
PY=${PY:-python}; D=Ingredient_Annotated_Dataset.csv; mkdir -p runs
for s in 1 2 3; do [[ -f runs/clean_size_seed$s.json ]] || CUDA_VISIBLE_DEVICES=$(( s % 2 )) $PY repro.py --data $D --protocol clean --with-size --seed $s > runs/clean_size_seed$s.log 2>&1; done
