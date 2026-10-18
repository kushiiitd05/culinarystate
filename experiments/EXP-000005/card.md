# Plan Part K hybrid NER layers on TASTEset (X8)

**Hypothesis:** each Part K layer (encoder > rules; + CRF; + kNN-NER; larger encoder) improves entity-level exact F1
on held-out TASTEset recipes over the layer below, beyond seed variation.

**Command:** `gpu/ner_tasteset/run_all.sh` on the A100 (mh-copilot venv, read-only), summary
`tools/summarise_ner_runs.py` -> `reports/ner/tasteset_encoders_v1.md`.
**Data:** TASTEset (700 recipes), recipe-level split seed 7, 70/15/15 (test 105 recipes); word-level BIO so
tokenizers are comparable; selection on DEV only; 5 seeds per variant; rule floor CI = grouped bootstrap.

| layer | test exact F1 (mean ± sd, 5 seeds) | vs layer below |
|---|---|---|
| rules (floor) | 0.774 [0.739, 0.808] | — |
| BERT / RoBERTa / DeBERTa-v3-base | 0.919 / 0.925 / 0.922 | +0.15 over rules |
| DeBERTa-base + kNN-NER | 0.924 ± 0.001 | +0.002 (marginal) |
| DeBERTa-base + CRF | 0.929 ± 0.003 | +0.007 |
| DeBERTa-large | 0.928 ± 0.003 | +0.006 over base |
| **DeBERTa-large + CRF** (dev-selected, 0.944) | **0.933 ± 0.003** (relaxed 0.957) | +0.005 over large |

**Verdict:** SUPPORTED for encoder > rules and CRF; kNN-NER NULL (within seed spread, not promoted).
Weak labels: PART and TASTE (< 0.70; rules beat encoders on PART).

**Caveats:** published TASTEset best (0.935) uses a different split — not a like-for-like comparison. No RecipeDB
matched run (API blocked), so no claim against Bagler-lab NER. GLiNER layer pending package approval.
**Decision:** KEEP DeBERTa-large+CRF as the NER layer; next layer (GLiNER / verifier) NEED_DATA/approval.
