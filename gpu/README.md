# GPU jobs (A100, vinayak-server) — VPN must be connected and confirmed by Kush first

| Job | What | Launch |
|---|---|---|
| `ner_tasteset/` | X8 encoder NER on TASTEset: bert-base-cased, roberta-base (GPU 0), deberta-v3-base (GPU 1) × 5 seeds | `bash gpu/push_ner.sh` (copies scorer + data, rsyncs to `/home/vinayak23597/Kush/culinarystate-ner/`, starts `run_all.sh` in nohup) |

Protocol: handoff/NER_RUNBOOK.md. Never send BBC text to the server (D-003); TASTEset is MIT.
Pull results: `rsync -a vinayak-server:/home/vinayak23597/Kush/culinarystate-ner/runs/ gpu/ner_tasteset/runs/`, then
`py tools/summarise_ner_runs.py`.
