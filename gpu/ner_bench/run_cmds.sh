#!/usr/bin/env bash
# usage: bash run_cmds.sh jobs.txt   (each line = script + args). Two workers (GPU0 even lines, GPU1 odd). Skips lines already done (marker in logs/).
JOBS=$1; PY=${PY:-/home/vinayak23597/Kush/mh-copilot/.venv/bin/python}; mkdir -p logs
worker() { g=$1; n=0
  while IFS= read -r line; do
    n=$((n+1)); [ $((n % 2)) -eq $g ] || continue
    h=$(echo "$line" | md5sum | cut -c1-12); [ -f logs/done_$h ] && continue
    CUDA_VISIBLE_DEVICES=$g $PY $line > logs/cmd_$h.log 2>&1 && touch logs/done_$h
  done < $JOBS; }
worker 0 & worker 1 & wait; echo cmds-done
