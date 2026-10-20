#!/usr/bin/env bash
# Automated chain, no operator needed (idempotent: run_cmds.sh skips finished lines). Two independent lanes started by launch_chains.sh.
#  LANE A  (decision path): wave2/3 -> DEV-only shortlist -> RecipeDB3 elimination -> RecipeDB3 out-of-fold tables -> extra RecipeDB3 seeds
#  LANE L  (linker, independent, starts now): contrastive linker grid incl. embedding-neighbour hard-negative round 2
cd "$(dirname "$0")"; PY=${PY:-/home/vinayak23597/Kush/mh-copilot/.venv/bin/python}
lane=$1
if [ "$lane" = "A" ]; then
  echo "A start $(date)" > chain_A.out
  while ! grep -q cmds-done queue_wave2.out 2>/dev/null || ! grep -q cmds-done queue_wave3.out 2>/dev/null; do sleep 120; done
  echo "A wave2/3 done $(date)" >> chain_A.out
  $PY auto_shortlist.py > shortlist.log 2>&1; echo "A shortlist written $(date)" >> chain_A.out
  bash run_cmds.sh jobs_rdb3_elim.txt > queue_rdb3_elim.out 2>&1; echo "A rdb3 elimination done $(date)" >> chain_A.out
  bash run_cmds.sh jobs_rdb3_oof.txt > queue_rdb3_oof.out 2>&1; echo "A rdb3 oof done $(date)" >> chain_A.out
  bash run_cmds.sh jobs_rdb3_seeds.txt > queue_rdb3_seeds.out 2>&1; echo "A rdb3 extra seeds done $(date)" >> chain_A.out
  echo "CHAIN-A-DONE $(date)" >> chain_A.out
else
  echo "L start $(date)" > chain_L.out
  bash run_cmds.sh jobs_linker.txt > queue_linker.out 2>&1; echo "CHAIN-L-DONE $(date)" >> chain_L.out
fi
