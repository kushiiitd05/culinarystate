# V2-DM guide: how a decision model can *learn* our task, and what to do if it does not help NER

No result here is a SOTA claim. v1 (H6-C) is frozen; v1 TEST is burned, so any v2 claim needs fresh data. Pre-registered gates in `v2dm_protocol.md` decide.

## 1. Is RL needed?
Jev's RLCD rewards calibrated probabilities. A *proper scoring rule* (log loss, Brier) already makes the best possible probability the optimum, so training the decision model **supervised with log loss on the option tokens, then temperature/isotonic calibration on CALIBRATION**, is the simple equivalent. RL (e.g. GRPO with a Brier reward) is only worth adding if the model must generate multi-step reasoning before answering or if the reward is non-differentiable (e.g. "safe coverage at <= 2% error"). Plan: supervised first; RL only as a later ablation.

## 2. What could actually beat the earlier NER numbers
Span F1 is near ceiling (RecipeDB3 micro 0.958, boundary error 1.8%; encoder/CRF/knowledge/fusion variants gave nothing). A decision model changes F1 only if it **chooses between candidates**:
- **Track A (selective NER, our strongest lane):** KEEP/REVIEW decision over every prediction; metric = safe coverage at <= 2% error, error capture. Hard baselines: R0 raw per-stratum confidence (RecipeDB3 0.828 coverage), CD-S gradient boosting (TASTEset 0.650).
- **Track B (F1 lane):** n-best reranking: the CRF supplies the top-k alternative segmentations/labels of a span; a decision model (choice: candidate_1..k / none) picks one. This is the only route to a real F1 gain; the upper bound is the oracle n-best F1, to be measured before any training (needs n-best decoding from a retrained checkpoint).
- **Track C (linker):** choice among top-K ledger candidates + NONE given the mention in context. Retrieval has a 15-point gap between Acc@1 (0.70) and Recall@5 (0.85); the earlier cross-encoder reranker failed, a context-aware decision model is a different test.

## 3. Prompt design (pre-listed, frozen before DEV is scored)
Constraints from the model cards: short `state` (Tev ~2,000 tokens, Nimble 8,192), options 2-26, add a NONE/insufficient option, no chat, no free text. Variants: **p1** text with the span marked `[[ ]]` + proposed label + label glossary; **p2** p1 + 6 most frequent *train-gold* surfaces of the label as exemplars (no gold from DEV/TEST); **p3** p2 + a coarse CRF-confidence band (very high/high/medium/low). Questions: Q3 exact-correct (noul, primary), Q1 boundary (noul), Q2 label (choice). Choose among p1-p3 by AUROC on OOF TRAIN spans only; then freeze; DEV is scored once per model. Known risk: TASTEset docs are whole ingredient lists (long state) -> a `--window` option (the line containing the span) is the first fix if latency/accuracy suffers.

## 4. Making our own model a good learner (after a Stage-1 GO)
1. Data: OOF TRAIN spans (TASTEset 8,225; RecipeDB3 65,716) with gold-derived targets: correct / boundary error / label error / spurious; add hard cases by oversampling errors and unseen mentions; no DEV/CAL/TEST rows.
2. Teacher: Tev1/Nimble zero-shot probabilities on the same rows, calibrated on OOF before use as soft targets.
3. Student CD-S (tabular, already built) then CD-T (span/context representation + the same features); optional LoRA fine-tune of Tev1-0.8B/4B using the public recipe (rank 8, lr 5e-5, 1 epoch, completion-only loss) on our bounded questions.
4. Loss = gold decision (log loss) + lambda x teacher KL + calibration term; select lambda on DEV; thresholds from CALIBRATION; fresh data for the final claim.
5. Compare against R0, R1, CD-S; promote only if safe coverage or error capture improves with CI separation and no extra damage.

## 5. If the decision model does NOT help NER review, what else (ranked)
1. **Linker verification (Track C)** -- cleanest fit (bounded choice, gold concept IDs exist, v2 data valid, small dev_alias n=61 so use pooled dev+held-out with paired bootstrap and a fresh annotated set later).
2. **NIL / NOVEL adjudication** (KNOWN / POSSIBLE_NEW_ALIAS / UNKNOWN) on the valid v2 NIL sets; today cosine AUROC is only 0.66.
3. **Label disambiguation** where type errors occur (STATE vs DF vs SIZE, PHYSICAL_QUALITY vs TASTE): small error mass, cheap to test.
4. **Ledger alias discovery** (offline suggestion of aliases for human approval, not auto-merge).
5. **H_STATE evidence screening**: "is process P applied to ingredient I in this recipe step?" is exactly a noul decision; the 210-row AI screen awaiting your confirmation could be cross-checked by a local decision model (Food.com text stays local; needs your OK to run it on the lab server).
6. Stop if all of the above show no gain: record the lane as REJECTED with the negative evidence.
