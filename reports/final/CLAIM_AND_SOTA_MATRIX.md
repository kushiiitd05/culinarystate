# Claim and SOTA matrix

**`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · 17 Nov 2026.** **No overall SOTA claim is made anywhere.**
Claim status ∈ {BEATS, TIES, BELOW, NOT_COMPARABLE, SYSTEM_CONTRIBUTION_ONLY, DIAGNOSTIC_ONLY}.
No component is BEATS.

Source keys: `[NER]` `reports/ner/culinaryner_kf_final_report.md` · `[BT]` `docs/BUILD_TRACKER.md` ·
`[S7]` `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md` · `[ST]` `STATUS.md` ·
`[FR]` `reports/final/FINAL_REPORT_DRAFT_S179_2026-11-11.md` · `[D]` `DECISIONS.md` ·
`[MP]` `handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md` · `[SI]` `reports/s179/state_inventory_FINAL_2026-11-15.md` ·
`[CM]` `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md`.

| Component | Prior method / benchmark | Prior score or capability | Our score or capability | Same protocol? | Statistically comparable? | **Claim status** |
|---|---|---|---|---|---|---|
| **NER — RecipeDB3, clean grouped split** | RecipeDB3 baseline reproduced by us on a clean grouped split, selection on dev `[NER §A]` | macro 0.9504 ± 0.0034, micro 0.9594 `[NER §A]` | frozen primary DeBERTa-base+CRF: micro 0.9581 ± 0.0012, macro 0.9545 ± 0.0037 `[NER §A]` | Yes (same grouped TEST) | "no improvement over the clean baseline: same encoder family" `[NER §A]` | **TIES** |
| **NER — RecipeDB3 standard protocol (finding, not a score)** | Their protocol: random 80/20, select on test `[NER §A]` | macro 0.9543 ± 0.0020 (5 seeds), notebook 0.9557 `[NER §A]` | Protocol **leaks**: 13.6% masked-family overlap, 5.4% exact duplicate test rows; leaked rows micro 0.9937 vs 0.9558; gap +0.0039 (Welch p = 0.067) `[NER §A]` | n/a — the protocol itself is the object | The leak rates are counts; the score gap is p = 0.067, **not** significant at 0.05 | **SYSTEM_CONTRIBUTION_ONLY** (protocol-leak finding; the stronger result `[MP §7]`) |
| NER — TASTEset | DeBERTa-v3-large+CRF challenger (internal) `[NER]` | micro 0.9371 ± 0.0035 `[NER]` | primary micro 0.9371 ± 0.0024; paired dF1 +0.0000 [CI −0.0053, +0.0054] `[NER]` | Yes (internal) | Yes, paired bootstrap | **TIES** (internal only). External published TASTEset score: `NOT_EVIDENCED` → **NOT_COMPARABLE** externally |
| NER — external domain | FoodBase | `NOT_EVIDENCED` ("FoodBase not obtained" `[NER]`) | unavailable `[NER]` | No | No | **NOT_COMPARABLE** |
| NER span router / calibration | none external opened | `NOT_EVIDENCED` | RecipeDB3 R6 ACCEPT coverage 0.717, ACCEPT error 0.0209 [0.0172, 0.0249]; calibrated+M6 ECE 0.0056 `[NER]`. Tolerance does **not** hold on accepted unseen spans (ACCEPT error 0.1250) `[NER]` | No | No | **SYSTEM_CONTRIBUTION_ONLY** |
| Entity linking | internal Pareto pair BGE-large vs E5-large `[NER]` | E5 held-out alias Acc@1 0.662 `[NER]` | BGE held-out alias Acc@1 0.704 (n=96), Recall@5 0.854, MRR 0.765; NIL AUROC 0.665 (advisory only); paired dev diff 0.026, CI [−0.030, 0.082] "indistinguishable" `[NER]` | Internal only | Indistinguishable on 61 dev aliases `[NER]` | **SYSTEM_CONTRIBUTION_ONLY** `[MP §7]`; external benchmark score `NOT_EVIDENCED` |
| Quantity grounding | none opened | `NOT_EVIDENCED` | quantity grammar "90% lines" `[BT RQ07]`; mass "0.6% groundable" by census, DEFER `[SI §3]` | No | No | **SYSTEM_CONTRIBUTION_ONLY** |
| Structured evidence retrieval (silver) | BM25; hybrid; cross-encoder (internal baselines) `[BT]` | BM25 0.597, hybrid 0.704 (MRR, silver) `[BT RQ02]` | structured MRR 0.856 (silver) `[BT RQ02]`; cross-encoders negative `[BT C6]` | Internal silver only | "headline NEED_DATA (human-labelled pairs)" `[BT RQ03]` | **SYSTEM_CONTRIBUTION_ONLY** `[MP §7]` — silver, no human gold |
| State-vector retrieval views (V0/V1) | none | n/a | 5,181 states, 40 queries, k=10; chance Jaccard 0.001; V0/V1 overlaps 0.0455–0.1164; nothing shared by all three views on 34/40 queries `[ST]` | n/a | No — "no relevance gold" `[ST]`; overlap is not precision `[MP §6]` | **DIAGNOSTIC_ONLY** |
| Recipe flow graphs / lot graph | prior art exists `[MP §7]` | specific prior method and score: `NOT_EVIDENCED` in files opened | lot-aware event graph, corpus-wide replay | No | No | **NOT_COMPARABLE** — do **not** claim invention `[MP §7]` |
| Lineage vNext (coreference) | no gold | n/a | 611,902 recipes, 0 exceptions raised; 29.3% of recipes changed — DIAGNOSTIC; **no gold regression set** `[D] D-134` | n/a | No | **DIAGNOSTIC_ONLY** — never "clean / validated / verified" |
| LLM Layer-1 proposer (sealed 60 cases) | arms 7B v1 / 72B v1 / 7B v3 (internal) `[S7]` | grounded: 0 / 0 / 1 `[S7 §1]` | 72B v3: 63 returned, 21 accepted, **21 grounded**; 0 of 63 quotes failed to locate `[S7 §1]` | Internal; single-sample arms; 59 + 1 repaired call `[S7 §5]` | No — **no gold**, AI-delegated, raters not independent `[S7 §4]` | **DIAGNOSTIC_ONLY** — no accuracy number may be quoted |
| Typed Event IR + V4 validator | none benchmarked | n/a | six invariants mapped to code; alternatives invariant closed 15 Nov; five scopes still open `docs/EVENT_IR_CONTRACT.md` | n/a | n/a | **SYSTEM_CONTRIBUTION_ONLY** |
| State representation S_t + evidence compatibility + claim-constrained RAG | no single prior system benchmarked on the same task in files opened | `NOT_EVIDENCED` | the integration `[MP §7]`; D3 gold evaluation not performed `[CM]` | No | No | **SYSTEM_CONTRIBUTION_ONLY** ("our contribution: the integration" `[MP §7]`) |
| pH axis 7 | FDA/CFSAN 2003 table (a source, not a method) | 479 rows `[ST]` | 140 ING bands: 31 acidic, 101 low-acid, 8 inconclusive; crosswalk `UNVERIFIED_CROSSWALK_AI_DRAFTED` `[ST]` | n/a | n/a | **SYSTEM_CONTRIBUTION_ONLY** |
| D2 completion / transition fallback | persistence, process-mean, nearest-evidence, LightGBM (contract baselines `[CM]`) | scores `NOT_EVIDENCED` (reports/del2 not opened) | "DEL-2 negative result (cold) — report as such"; "gains vanish cold" `[BT RQ20, C9]` | Internal | `NOT_EVIDENCED` | **BELOW / negative result retained** (exact figures: `NOT_EVIDENCED`) |
| **H1** (system vs baselines, 24 AI-gold questions) | B0, B1, B2 `[FR]` | B0 = 2/24; B1 = B2 = 6/24 `[FR]` | B4 = 6/24; 4 discordant pairs, exact two-sided McNemar p = 1.0 `[FR]` | Yes (internal ladder) | Yes — and it fails the rule | **RULE_NOT_MET** (D-092) → mapped to **TIES**; "not equivalence … and not evidence of absence of an effect" `[FR]`. NON_CITABLE / MODEL_ASSISTED_GOLD `[FR]`. **Retained.** |
| **H3** (B7 vs B2) | B2 `[FR]` | B2 abstains 3/10 on P3 `[FR]` | sign test 16 discordant in B7's direction, 0 other, p = 0.000030517578125; **but** P3 condition fails: B7 abstains 0/10 `[FR]` | Yes (internal) | Sign test yes; preregistered conjunction not met | **RULE_NOT_MET** (D-092). The sign-test result alone may not be reported as a win. **Retained.** |
| Vitamin C Model A formula | — | — | `FORMULA_RESEARCH_ONLY`, NOT_VALIDATED; SIM-VAL zero eligible rows `[ST]` | No | No | **DIAGNOSTIC_ONLY** |
| Demo / deployment | — | — | stdlib demo server exists (`src/culinarystate/app/server.py`) | n/a | n/a | **SYSTEM_CONTRIBUTION_ONLY** |

## Rules for use

1. Say **"NER ties the baseline on a clean grouped split; the standard RecipeDB3 protocol leaks."**
   Never "SOTA NER" `[MP §6]`.
2. H1 and H3 stay **RULE_NOT_MET**; neither "is repaired by a favourable secondary statistic" `[FR]`.
3. Any figure from a DIAGNOSTIC_ONLY row carries that label in the same sentence.

## Contradictions / NOT_EVIDENCED

- **Layer-1 "real choice" count, 72B v3:** `[S7 §1]` says "19 of 21 — 90%"; `[D] D-139` resolved
  count says "17 of 21"; `[MP §6]` says "17 judged well-formed". (`[S7 §3]`: 9 + 8 + 2 duplicates
  + 2 not-a-choice; 17 excludes the duplicates.) Parent must pick one and state the rule.
- **Clean-baseline macro vs ours:** ours 0.9545 is numerically above the clean-split baseline 0.9504
  `[NER §A]`, but `[NER]` itself words it "no improvement … same encoder family"; no test of that
  specific difference was found → status TIES, significance of that pair `NOT_EVIDENCED`.
- `[BT]` E16-A row gives older NER numbers (DeBERTa 0.922; +CRF base 0.927) — an earlier protocol,
  superseded by `[NER]`.
- External prior scores (TASTEset, FoodBase, linker benchmarks, recipe flow-graph papers), D2 baseline
  figures: `NOT_EVIDENCED`.
