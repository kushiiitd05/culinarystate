# H_STATE — does explicit reconstructed culinary state improve evidence retrieval and decisions? (RQ16-01, pre-registered 2026-10-19, NOT RUN)

**Claim (falsifiable):** on questions whose ingredient and/or process are supplied only by the cooking context, the rung B4 (B3 plus slots and retrieval
text filled from the reconstructed session state) returns more condition-compatible evidence in the top 5 and a better answer mode than the same system
without state (B3), with a paired grouped-bootstrap 95% CI excluding 0 and no increase in unsupported-claim rate.

**Unit:** one (recipe, cut point, question) triple. **Population:** English BBC Good Food recipes in the Gold set (+ ≥5 Wikibooks recipes if available,
for the source-disjoint check); food/process families those recipes contain; evidence tiers E1–E4 in the ledger as of the frozen EVD snapshot.
**Frozen before viewing results:** recipe list, cut points, question texts, gold labels, EVD/COND snapshot hash, code commit, seed 7.

## Human Gold inputs (exact)
| id | input | who | amount | notes |
|---|---|---|---|---|
| G1 | Gold events for 20 recipes (`annotation/batches/pilot_20.csv`), double-annotated and adjudicated | Kush + Parv (ADJUDICATED) | 20 recipes | κ/span-F1 agreement reported; gold events give the oracle state at every step |
| G2 | State-dependent questions: 3 cut points per recipe, question written by a human who sees the recipe up to the cut point and the ledger target list, but not any system output | Kush or Parv | 60 questions | each question omits the ingredient and/or process that the gold state supplies (e.g. "how much vitamin C is left?" after boiling broccoli); ≥2 target types |
| G3 | Gold evidence cell per question: (ING, PROC, target) from the ledger, or UNSUPPORTED; and gold mode ∈ ANSWER/ASK/ABSTAIN/COMPARE/DIAGNOSE/RECOVER/RECOMMEND | same | 60 | ≥40 supported, ≥10 UNSUPPORTED, ≥5 ASK-correct (state genuinely ambiguous) |
| G4 | Controls: fully specified questions on the same recipes | same | 20 | state should not change the answer; tests that B4 does not hurt |
| G5 | Blind relevance judgments (condition-compatible: yes / partial / no) for the pooled top-5 of B3, B4-predicted, B4-oracle; system identity hidden, order shuffled | second annotator | ≤ 80 × 15 rows | pooling avoids favouring the system that defined the gold cell |
| G6 | Second annotation of G3/G5 on 20 questions | other annotator | 20 | Cohen κ for cell, mode, relevance |

## Systems (all run with the same ledger snapshot, retriever, policy and k)
- **B3:** `answer(q, …, session=None, use_state=False)` — question text only (structured metadata via `parse_query`).
- **B4-pred:** same with `session = replay(rule_compiler(recipe text up to the cut point))`, `use_state=True` (fills empty ingredient/process slots, adds them to the retrieval text; question slots always win).
- **B4-oracle:** same with `session = replay(G1 gold events up to the cut point)`.
- **Optional diagnostic:** B2 hybrid RAG (BM25+e5) without structured slots, to place B3 in the ladder.

## Metrics
- **Primary:** ConditionCompatible@5 (CC@5): fraction of questions with ≥1 `yes` judgment in the top 5 (UNSUPPORTED-gold questions are scored on ModeF1/UCR only). Also CC@1.
- **Decision:** ModeF1 (macro over gold modes), correct-ASK rate, unsupported-claim rate (UCR, claims checker on the verbalised answer).
- **Mechanism:** slot accuracy for ingredient and process after conditioning; fraction of questions where B3 slots were already complete (the "state-independent" stratum).
- **Oracle gap:** (B4-oracle − B4-pred) = loss attributable to event extraction (stages 1–6); (B4-oracle − B3) = ceiling of state value on this set.
- **Uncertainty:** paired grouped bootstrap (10,000 resamples, groups = recipe family), Holm over the three primary contrasts; per-stratum numbers reported, not hidden.

## Leakage and validity audit (before looking at outcomes)
1. Question authors write before any system run; question text is checked so that `parse_query(question)` recovers gold ingredient/process in < 30% of the state-dependent set (otherwise the set is not state-dependent and is rewritten).
2. Gold cells must exist in the frozen EVD snapshot or be marked UNSUPPORTED; no question is dropped after results.
3. Recipes are family-disjoint from every recipe used to develop the compiler (the 3 GOLD-EX recipes are excluded) and from `test_rule_compiler` fixtures.
4. Retrieval text for B4 contains only slot names derived from state, never the answer or gold cell.
5. Report headline split as within-source (BBC) unless ≥5 Wikibooks recipes are added; external validity otherwise limited to UK web recipes and the three evidence sources.

## Gates
- **Success (promote the state module for the course system):** B4-pred − B3 on CC@5 has CI lower bound > 0, UCR(B4) ≤ UCR(B3) + 1 pt, and the controls (G4) show no loss (CI includes 0 or positive). Also report whether B4-oracle − B4-pred > 0.10 (then extraction, not state, is the bottleneck).
- **Null gate:** CI of B4-pred − B3 includes 0 while B4-oracle − B3 > 0 with CI excluding 0 → the idea is right but extraction is too weak: KEEP B3 in the headline, report state as NEED_DATA/MODIFY (improve stages 4–5 first).
- **Negative gate:** B4-pred < B3 (CI excludes 0) on CC@5 or UCR worse by > 3 pts → DROP state conditioning from retrieval; inspect state-parser errors (the SSOT's stated alternative explanation); the DEL-3 engine remains a separate deliverable (RQ16-14).
- **Invalid-experiment gate:** B4-oracle − B3 ≈ 0 (CI contains 0) → the questions are not state-dependent or the evidence ledger cannot reward the extra information; do not interpret as "state is useless"; fix the question set.
- **Not justified by this experiment:** multi-turn memory value (RQ16-14), quantity-conditioned answers, languages other than English, recipes outside the Gold set, anything about FlavorTwin.

## Required code after Gold exists (not built now)
Harness that cuts a recipe at a step, replays predicted/gold events, runs B3/B4, writes pooled top-5 for blind judging, and scores CC@K/ModeF1/UCR with grouped bootstrap. Everything else needed (`answer(use_state)`, `state_conditioning`, scorer, claims checker, bootstrap helpers) exists.

**Status:** PLANNED. Blocked on G1–G6 (human Gold). Registering in the EXP ledger is deferred (EXP-000005/6 also unregistered; register all in one step).

---
## Amendment A1 (S114, 2026-10-20) — evidence-coverage split (original text above is unchanged)

AMENDMENT_REASON: empirical evidence coverage discovered before question authoring and before any B3/B4 system output
was observed. Not performance-driven tuning. Only Gold-v1.1 state and EVD-ledger coverage were inspected.

Finding (S112/S114): only 10/20 Gold recipes carry any compatible ingredient+process retention cell anywhere in their
trajectory; 8 recipes carry one at a valid cut; 14 distinct (recipe, cell) pairs exist. The preregistered >=40 supported
state-dependent questions is unreachable without repetitive/artificial questions.

Design after amendment (target; actual maximum reported, never forced):
- H_STATE-R (supported retrieval): up to 40 state-dependent questions with a compatible Gold evidence cell, distinct
  cell per question within a recipe. Primary metric ConditionCompatible@5 (grouped by recipe/family); secondary MRR, ModeF1,
  unsupported-claim rate. Actual maximum achievable under current ledger: 14.
- H_STATE-A (unsupported/abstention): 20 state-dependent questions with Gold evidence UNSUPPORTED. Measures: correct
  ASK/ABSTAIN, unsupported-claim rate, false-support rate. Excluded from ConditionCompatible@5.
- CONTROL: 20 fully specified questions, one per recipe.
Slot selection is deterministic (tools/build_hstate_r_candidates.py). Freeze (question, cut, Gold state, evidence labels,
stratum, mode hashed) precedes any B3/B4 output. The H_STATE-R success gate must be re-read at n actually frozen.
