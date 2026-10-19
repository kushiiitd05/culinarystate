#!/usr/bin/env bash
# GLiNER zero-shot eval on A100 server
# Transfer: scp -r gpu/ner_tasteset/ vinayak-server:/home/vinayak23597/Kush/ner_tasteset/
# Then: ssh vinayak-server 'cd /home/vinayak23597/Kush/ner_tasteset && bash run_gliner.sh'
set -euo pipefail

PY=${PY:-/opt/anaconda3/envs/recsys_env/bin/python}
export CUDA_VISIBLE_DEVICES=0

echo "=== GLiNER zero-shot eval ==="
echo "Model: urchade/gliner_large-v2.1"
echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'unknown')"
echo ""

# Install gliner if needed
$PY -c "import gliner" 2>/dev/null || pip install gliner

mkdir -p runs

# Zero-shot (no training, just threshold search on dev)
PYTHONPATH=. $PY gliner_eval.py \
    --data TASTEset.csv \
    --model urchade/gliner_large-v2.1 \
    --mode zeroshot \
    2>&1 | tee runs/gliner_zeroshot.log

echo ""
echo "=== Done. Results in runs/gliner_*.json ==="
ls -la runs/gliner_* 2>/dev/null
