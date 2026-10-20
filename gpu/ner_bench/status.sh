#!/usr/bin/env bash
cd "$(dirname "$0")"; echo "== $(date)"; cat chain_A.out chain_L.out 2>/dev/null
echo "tasteset runs: $(ls runs/tasteset__*.json 2>/dev/null | grep -vc pred) | recipedb3 runs: $(ls runs/recipedb3__*.json 2>/dev/null | grep -vc pred) | linker runs: $(ls runs/linker__*.json 2>/dev/null | grep -vc tables) | conf/oof: $(ls runs_conf/*.json 2>/dev/null | grep -vc pred)"
echo "done markers: $(ls logs/done_* 2>/dev/null | wc -l)"; nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
