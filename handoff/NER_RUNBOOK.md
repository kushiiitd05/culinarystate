# NER RUNBOOK — ingredient-line + step NER (P5 / X8)

## Targets and data
| Set | What | Labels | Use |
|---|---|---|---|
| TASTEset (MIT, 700 recipes, 13,362 spans) | ingredient lists | FOOD, QUANTITY, UNIT, PROCESS, PHYSICAL_QUALITY, COLOR, TASTE, PURPOSE, PART | external benchmark (train/dev/test split by recipe, seed 7) |
| Wikibooks silver spans (local, ~49k) | ingredient lines + steps | INGREDIENT, TOOL, UNIT, PROCESS (+ link target) | silver pre-training / linking supervision |
| Gold pilot (annotation/, humans) | BBC recipes | handbook v1 labels | final evaluation only — never train on it |

## Floor to beat (CPU, measured S047)
`py tools/eval_tasteset.py` → `reports/ner/tasteset_rule_baseline.md`:
micro F1 **0.791 exact / 0.898 relaxed**; FOOD 0.753 / 0.952; QUANTITY 0.840; UNIT 0.863; PHYSICAL_QUALITY 0.554 (weakest).

## Encoder run (A100 — ask Kush to connect FortiClient VPN first; never SSH without confirmation)
1. `ssh vinayak-server`, `mkdir -p /home/vinayak23597/Kush/culinarystate-ner`, `scp` src/culinarystate/{ner,scoring} + data/raw/tasteset.
2. Env: existing conda env with transformers + torch (no new venv). Model candidates: `bert-base-cased`,
   `roberta-base`, `microsoft/deberta-v3-base` (token classification, BIO tags, max_len 256).
3. Protocol: 5 seeds; split by recipe (70/15/15); select on dev only; report test exact/relaxed span F1 per label
   with grouped bootstrap CI over recipes (scoring.metrics.grouped_bootstrap). Record a MODEL + EXP ledger card
   (`selected_on: DEV`; `REPRODUCED` only if the published TASTEset numbers are matched within CI).
4. Silver ablation: (a) TASTEset only; (b) Wikibooks silver → TASTEset fine-tune. Claim silver helps only if CI separates.
5. Pull back predictions + metrics to `reports/ner/`; never copy BBC text to the server (D-003).

## Linking (after NER)
FOOD span → ING via `LineLinker.link` (lexicon + aliases); report Acc@1 on Wikibooks editor links (held-out recipes)
with `scoring.metrics.linking_scores`; NIL allowed.
