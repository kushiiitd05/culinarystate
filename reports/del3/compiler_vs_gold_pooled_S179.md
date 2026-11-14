# Rule compiler vs the P1 gold and the 40 dev-gold recipes (S179, T3-C11-R1)

Status: **AI_DIAGNOSTIC, counts only. NOT INDEPENDENT** (D-017, D-060). This is not a test result: every gold set
below began as an AI draft, and the engine was developed while these recipes were in view (the pilot_20 set since
S107).

- Data: `reports/del3/compiler_vs_gold_pooled_S179.json`, sha256 `2981ba0a…`; run RUN-S179-GOLD-001 at code 483efe0
  on the Mac. Re-running gave the same hash.
- Code: `tools/s179_compiler_vs_gold_pooled.py` and `src/culinarystate/evaluation/compiler_vs_gold_pooled.py`.

**What is scored.** This scores the rule compiler (`state_graph.rule_compiler.compile_recipe`) through the same cascade
as `tools/eval_compiler_vs_gold.py`: P predicted, O1 oracle concepts, O2 gold Add events, G gold ceiling. The board
item says "Rung A". The Step 17b Rung A extractor (`extraction/rung_a.py`) emits a 17a `EventGraph`, not engine
events, so it cannot be scored here without an adapter. That adapter is not built. Read "Rung A" in the board item
as "the rule compiler", which Rung A's verb slot reuses.

**Counting.** True positives, false positives and false negatives are pooled over each set, with Wilson 95 % intervals
(the S109 tool reported per-recipe means with a bootstrap). Entity labels are aligned before scoring, so naming
choices are not errors.

## Gold sets

| Set | n | Source | Label basis |
|---|---:|---|---|
| P1, side A (Kush) | 7 | BBC Good Food (Mac only) | HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND |
| pilot_20, Gold-v1.1 | 20 | BBC Good Food | AI-assisted, human-reviewed dev gold |
| Food.com, AI-assisted v1.1 (joint) | 20 | Food.com | AI-assisted, human-reviewed dev gold (one AI proposal; Kush and Parv sets identical) |

`annotation/gold/evidence_first_expansion` (Kush and Parv, 20 each) was **not** used. Those files are DRAFT and hold 0
step events (ingredient lines only), so they cannot score events or state. The "40 dev-gold recipes" are therefore
pilot_20 v1.1 plus Food.com v1.1.

## Results at level P (predicted, no oracle)

| Measure | P1 A (7) | pilot_20 v1.1 (20) | Food.com v1.1 (20) |
|---|---|---|---|
| Events, loose: precision | 0.253 [0.176, 0.348] | 0.251 [0.204, 0.305] | 0.281 [0.240, 0.327] |
| Events, loose: recall | 0.235 [0.164, 0.326] | 0.300 [0.245, 0.361] | 0.368 [0.316, 0.423] |
| Events, loose: F1 | 0.244 | 0.273 | 0.319 |
| Event type only, F1 | 0.609 | 0.685 | 0.708 |
| Alive entities: precision | 0.286 | 0.165 | 0.362 |
| Alive entities: recall | 0.667 [0.354, 0.879] | 0.536 [0.358, 0.705] | 0.581 [0.433, 0.716] |
| All state-graph edges, F1 | 0.328 | 0.334 | 0.424 |
| Structural edges (merge / split / reserve), F1 | 0.360 | 0.359 | 0.470 |
| Final state fields correct | 5 / 31 = 0.161 [0.071, 0.326] | 9 / 79 = 0.114 [0.061, 0.203] | 24 / 120 = 0.200 [0.138, 0.280] |
| Recipes with replay issues | 0 | 0 | 0 |

The G level scores 1.0 on every measure in all three sets, so the scorer has no ceiling loss.

**O1 and O2.**
- O1 (oracle concepts) moves loose-event F1 by at most 0.012: down for pilot_20 (0.261), up for Food.com (0.324),
  unchanged for P1. Ingredient linking is not the bottleneck.
- O2 equals P on every measure in every set. The S109 run showed the same, because entity alignment already does
  what O2's relabelling does.

## Reading

- **What the numbers say.** The compiler recovers the gold *kind* of step event about 60-70 % of the time (type-only
  F1). It gets the event together with its target about a quarter to a third of the time. It ends with the gold
  final state on 11-20 % of state fields.
- **Over-prediction.** Alive-entity precision is low (0.17-0.36) while recall is 0.54-0.67: the compiler leaves too
  many entities alive.
- **Consistent with earlier results.** This matches the S109 verdict on pilot_20 (per-recipe means: state 0.106,
  loose events 0.247) and the P1 handbook finding that state and event categories are where even two
  human-accepted passes disagree (final_state 0.82, event_type 0.76 per pair).
- **Not a held-out estimate.** The engine was built with these recipes in view, and the gold is not independent. On 7
  recipes the intervals are wide. Split label: near-duplicate leakage not controlled.
- **Allowed wording for the report (T9-C16-R1):** "D3 was built and run; against 7 P1 recipes and 40 AI-assisted dev
  recipes (not independent) the rule compiler matched 11-20 % of final state fields."
- **Not allowed:** any accuracy claim for D3.

## Open

- Rung A adapter: a 17a `EventGraph` to engine events, so Rung A itself can be scored. Not built.
- P1 side B: the second annotation is not in this tree, so only side A is scored.
