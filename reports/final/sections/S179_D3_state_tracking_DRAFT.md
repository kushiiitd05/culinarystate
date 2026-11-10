# Report section draft: D3 state-tracking engine (S179)

Status: **AI_DRAFTED** for the final report (board items T9-C16-R1 and T3-C17-R2). Counts only. No figure here is
an accuracy claim. Written 2026-11-10 by the Mac agent on `kush/s179-finish-fixes`.

**One-line verdict for the report.** D3 is built and has run on the full corpus. Its replay is deterministic and
catches every planted structural error. Gold comparison is limited to 7 P1 recipes and 40 AI-assisted development
recipes, none of them independent; on those, the rule compiler ends with the gold final state on 11-20 % of state
fields.

## 1. What D3 is and where it ran

- **Pipeline.** Recipe text goes through the rule compiler (`state_graph.rule_compiler`, also Rung A's verb slot) to
  an event log. The replay engine (`state_graph.engine`) turns the log into a per-step state graph.
- **Corpus run.** The Step 18 replay ran on every non-BBC recipe with instructions: 599,971 texts (Food.com 522,517;
  Gutenberg segments 73,778; Wikibooks 3,676).
  - Source: `reports/s178/corpus/replay_invariants_corpus_v2.json`, sha256 `2abe7ae7…`, run RUN-S179-CORP-002.
  - Not run: TASTEset has no instruction text, and BBC is not on the server (D-003).

## 2. Metrics that need no gold (T9-C16-R1: replay consistency and property tests)

| Check | Result | Source |
|---|---|---|
| Same-worker determinism (texts replayed twice) | 12,046 of 12,046 identical (Food.com 10,416; Gutenberg 1,550; Wikibooks 80) | replay invariants v2 |
| Cross-process determinism (PYTHONHASHSEED 0 vs 1) | 12,046 of 12,046 identical snapshot and JSONL | same |
| Engine vs an independent re-derivation of the 7 structural invariants | 0 disagreements on 599,971 texts | same |
| Planted errors detected at the planted position: double consume | 28,854 / 28,854 | same (mutation power) |
| Planted errors: order swap | 29,945 / 29,945 | same |
| Planted errors: reuse after discard | 902 / 902 | same |
| Planted errors: split fractions above one | 390 / 390 | same |
| Texts whose replay FAILs an invariant | 12,774 of 599,971 (2.1 %) | same |

**Limits.**
- These tests show the engine applies its own rules consistently. They say nothing about whether the events match
  the recipe.
- The split-sum check is almost empty: 0 of 88,817 partition groups have a checkable basis and fraction.
- Lot accounting, invented values and quantity propagation are not checked by replay (`not_checked_by_replay`).

## 3. Gold comparison (T3-C11-R1, T3-C17-R2)

Sources:
- `reports/del3/compiler_vs_gold_pooled_S179.json` (RUN-S179-GOLD-001) and
  `reports/del3/event_type_table_S179.json` (RUN-S179-GOLD-002);
- method and caveats: `reports/del3/compiler_vs_gold_pooled_S179.md`.

All three sets are **NOT INDEPENDENT**. The engine was developed with them in view, and every set began as an AI
draft. Split label: near-duplicate leakage not controlled.

**Pooled counts, Wilson 95 % intervals:**

| Set | n | Label basis | Final state fields correct | Loose-event F1 | Event-type F1 |
|---|---:|---|---|---:|---:|
| P1, side A | 7 | HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND | 5 / 31 = 0.16 [0.07, 0.33] | 0.24 | 0.61 |
| pilot_20 v1.1 (BBC) | 20 | AI-assisted, human-reviewed dev gold | 9 / 79 = 0.11 [0.06, 0.20] | 0.27 | 0.69 |
| Food.com v1.1 | 20 | AI-assisted, human-reviewed dev gold | 24 / 120 = 0.20 [0.14, 0.28] | 0.32 | 0.71 |

**Event types at level P, P1 set (7 recipes).** Matched is the per-recipe count match, min(gold, predicted). Intervals
come from a recipe-cluster bootstrap with 2,000 resamples.

| Type | Gold | Predicted | Matched | Precision | Recall |
|---|---:|---:|---:|---|---|
| Merge | 36 | 21 | 21 | 1.00 [1.00, 1.00] | 0.58 [0.43, 0.72] |
| Transform | 35 | 63 | 33 | 0.52 [0.40, 0.70] | 0.94 [0.81, 1.00] |
| Transfer | 22 | 6 | 6 | 1.00 [1.00, 1.00] | 0.27 [0.05, 0.47] |
| Split | 8 | 1 | 0 | 0.00 | 0.00 |
| Discard | 1 | 1 | 0 | 0.00 | 0.00 |
| Reserve | 0 | 3 | 0 | 0.00 | n/a |

The dev sets show the same shape:
- Transform: precision 0.54-0.55, recall 0.96-0.98.
- Merge: precision 0.97, recall 0.67-0.74.
- Transfer and Split: under 0.6 on recall in both sets.
- Reserve: too few gold events to read (8 and 1).

The compiler emits a Transform for almost every heat or process verb. It misses many merges and most transfers and
splits. The P1 handbook finding agrees: two human-accepted passes disagree most on final_state (0.82 per pair) and
event_type (0.76).

## 4. Allowed and forbidden wording

- **Allowed:** "built and run on 599,971 texts"; "replay deterministic and catches 100 % of planted structural
  errors"; "against 7 P1 and 40 AI-assisted development recipes (not independent), 11-20 % of final state fields
  match".
- **Forbidden:** "accurate", "validated", "state tracking works", or any number without its n, its label basis and
  "not independent".
- **D3 accuracy** stays NOT MEASURED until an independent gold exists. That is P1b or later, and the decision on the
  minimum gold size is human (Q28).

## 5. Not done

- **Rung A extractor:** the 17a EventGraph is not scored directly; there is no adapter to engine events.
- **P1 side B:** not in this tree.
- **BBC replay invariants:** a Mac run is possible but has not been done.
