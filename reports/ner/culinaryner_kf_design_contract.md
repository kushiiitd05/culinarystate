# CulinaryNER-KF — design contract (adopted 2026-10-20, Kush)

The target system is a set of HYPOTHESES to test, not a build list. Every component must earn promotion by ablation; the final system may be a strict subset, and every omission must be evidence-based.

**CulinaryNER-KF** = knowledge-aware contextual encoder → CRF → span-boundary auxiliary learning → canonical ING linker (contrastive, top-K) → cross-fitted knowledge/metadata → calibration → risk router (ACCEPT / REVIEW / NOVEL / REJECT).
Principle: *metadata supports the encoder; it does not replace it.* Question: can we keep strong span extraction while improving unseen-surface generalisation, canonical linking, tail handling, calibration, novelty detection and safe abstention?

## Rules
1. **Hygiene:** DEV selects models/components; CALIBRATION (or true out-of-fold) sets thresholds; TEST only after the configuration is frozen. TASTEset TEST was exposed once at the E0 stage (2026-10-20) and that is recorded here; RecipeDB3 TEST is untouched.
2. **Knowledge integration (per source ask):** available at inference? leaks benchmark labels? helps DEV or calibration? helps unseen/tail/regional? statistically credible? what happens when removed?
3. **Dependency order:** linker trained and frozen → out-of-fold linker outputs → linker confidence + top-K margin → linked ING category → linked process family → ledger aliases ONLY after an alias/concept leakage audit → deterministic rule agreement. No gold canonical identity is ever used as inference-time metadata.
4. **Calibrator first, fusion second:** feature → leakage-safe generation → calibration/auxiliary ablation → promotion → optional fusion → fusion ablation → promotion/rejection. Encoder confidence/entropy stay calibrator-only.
5. **Ablate separately:** encoder, CRF, knowledge context, linker, cross-fitted metadata, calibration, fusion, span-boundary head, router. Report exact micro/macro F1, relaxed, boundary errors, unseen + tail, calibration, risk/coverage, runtime, memory, seeds, statistics.
6. **Claim gate:** no "SOTA / beats RecipeDB3 / beats CoSyLab" before H6 (frozen architecture, clean grouped eval, external/unseen eval, fair baselines, adequate statistics). Allowed wording: best CulinaryState candidate, SPAN_CHAMPION, Pareto-leading candidate, improves over our baseline, SOTA-oriented architecture.
7. **Event model is out of scope** until H_STATE decides.
8. **Reporting:** after each milestone report: what/why/data+split/results/leakage check/statistics/unseen+tail/compute/promote-reject-inconclusive/effect on final architecture/next step.
9. **Final freeze (A–N):** RecipeDB3 baseline; SPAN_CHAMPION or Pareto set; CRF; knowledge; linker; metadata; calibration; fusion; boundary head; exact ordered architecture; risk-coverage; compute; H6 status; one next action.

## Optional CulinaryState-specific layer (proposed 2026-10-20; NOT promoted — must earn its place by experiment)
**Evidence-key extraction:** NER + linking output canonical keys (ING id x PROC id) that index the evidence ledger; scored by evidence-cell recall/precision and a downstream-utility weighting tied to H_STATE. Not an event model (no Merge/Split/lineage); it reads out which (ingredient, process) cells a recipe needs.
Baseline (local, rule stack only, Food.com v1.1 Gold, 20 recipes): recovers 30 of 51 Gold-supported pairs (recall 0.588; precision vs Gold lineage 0.508, a lower bound). Of the 21 misses, 20 are NO_COOCCURRENCE (ingredient and process both detected but never in the same step: implicit reference / carry-over), 1 is an unmentioned ingredient, 0 are undetected processes. Reading: the ceiling for evidence coverage is set by coreference / state carry-over (event side), not by span extraction. Caveat: the Gold pairs come from AI-authored, batch-reviewed events.
Related smaller proposals: NOVEL-queue -> ledger growth loop (NOVEL precision vs NIL gold, discovery yield per 100 reviews); regional robustness slice (unseen/tail by alias language/region).

## Evidence log (2026-10-20, DEV)
REJECTED from mainline: knowledge prompts K1-K4; span-boundary auxiliary head; RoBERTa-base, BERT-base. INCONCLUSIVE: CRF on base (+0.0006), v3-large vs base (+0.0047, 5/5 seeds, not significant), fusion (concat/gated: no gain; metadata ON vs OFF −0.0007). MAINLINE NOW: encoder (base or large pending RecipeDB3 seeds) + CRF -> candidate spans. Focus moves to linking, metadata reliability, calibration, routing.
