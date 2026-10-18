#!/usr/bin/env bash
# Package and start the X8 NER sweep on vinayak-server. Requires VPN (confirmed by Kush) and an existing conda env
# with torch + transformers on the server: PY_REMOTE=/path/to/python bash gpu/push_ner.sh
set -euo pipefail
cd "$(dirname "$0")/.."
REMOTE=/home/vinayak23597/Kush/culinarystate-ner
cp src/culinarystate/scoring/metrics.py gpu/ner_tasteset/
cp data/raw/tasteset/TASTEset.csv gpu/ner_tasteset/
ssh vinayak-server "mkdir -p $REMOTE"
rsync -a --exclude runs gpu/ner_tasteset/ vinayak-server:$REMOTE/
ssh vinayak-server "cd $REMOTE && PY=${PY_REMOTE:?set PY_REMOTE} nohup bash run_all.sh > sweep.log 2>&1 &"
echo "started on vinayak-server:$REMOTE (tail sweep.log / runs/*.log)"
