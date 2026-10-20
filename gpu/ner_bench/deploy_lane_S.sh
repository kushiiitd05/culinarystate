#!/usr/bin/env bash
# Run from the repo root on the Mac once the VPN is up:  bash gpu/ner_bench/deploy_lane_S.sh
set -e
S=vinayak-server; D=/home/vinayak23597/Kush/culinarystate-ner-bench
scp -q gpu/ner_bench/{typespec_train.py,rerank_train.py,linker_train.py,knowledge.py,jobs_s.txt,bench_train.py} $S:$D/_stage/
ssh $S "cd $D && for f in typespec_train.py rerank_train.py linker_train.py knowledge.py jobs_s.txt bench_train.py; do cp _stage/\$f \$f.tmp && mv \$f.tmp \$f; done
  # 1-epoch smoke of the two new trainers before queueing (fails the deploy if they crash)
  CUDA_VISIBLE_DEVICES=1 /home/vinayak23597/Kush/mh-copilot/.venv/bin/python typespec_train.py --dataset tasteset --model microsoft/deberta-base --epochs 1 --limit 40 --seed 9 --out runs_smoke | tail -1
  CUDA_VISIBLE_DEVICES=1 /home/vinayak23597/Kush/mh-copilot/.venv/bin/python rerank_train.py --epochs 1 --seed 9 --tag _smoke --out runs_smoke | tail -1
  (setsid nohup bash run_cmds.sh jobs_s.txt > queue_s.out 2>&1 < /dev/null &); sleep 2; bash status.sh | head -8"
