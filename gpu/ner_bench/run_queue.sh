#!/usr/bin/env bash
# usage: bash run_queue.sh jobs.txt dataset   -> two workers (GPU0 gets even lines, GPU1 odd); skips finished runs; one job per GPU at a time
JOBS=$1; DS=$2; PY=${PY:-/home/vinayak23597/Kush/mh-copilot/.venv/bin/python}; mkdir -p runs logs
worker() { g=$1; n=0
  while read -r model seed crf; do
    n=$((n+1)); [ $((n % 2)) -eq $g ] || continue
    name=${model##*/}; [ -n "$crf" ] && name=${name}_crf
    [ -f runs/${DS}__${name}__seed${seed}.json ] && continue
    CUDA_VISIBLE_DEVICES=$g $PY bench_train.py --dataset $DS --model $model --seed $seed $crf --out runs > logs/${DS}__${name}__seed${seed}.log 2>&1
  done < $JOBS; }
worker 0 & worker 1 & wait; echo queue-done
