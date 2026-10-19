# Rule compiler vs pilot_20 Gold-v1 — first text → events → state evaluation (S107)

**Read this first.** Gold-v1 is the *AI-assisted, human-reviewed* set (OpenAI GPT-5.6 Sol draft, converted to gold-1.0, reviewed by Kush; Parv's review delegated to Kush; D-016/D-017). It is not independent, not blind, and not a test set; its adjudication is vacuous because both sets are identical. The compiler was not tuned on it (these 20 recipes are disjoint from the 3 development fixtures). Numbers are therefore a **development diagnostic against a noisy reference**, not a validated performance figure, and not a claim about the compiler or about any lab's system.

n = 20 recipes (BBC Good Food). Mean over recipes with bootstrap 95% CI over recipes (1,000 resamples, seed 7). Entity labels are aligned before scoring, so naming differences are not errors. Command: `tools/eval_compiler_vs_gold.py`; raw: `reports/del3/compiler_vs_gold_v1.json`.

| level | state-field acc | alive-entity F1 | merge/split/reserve F1 | relation F1 | event F1 (loose) | event-type F1 |
|---|---|---|---|---|---|---|
| P  predicted (raw text → events → state) | 0.102 [0.04, 0.16] | 0.312 [0.19, 0.42] | 0.343 [0.26, 0.44] | 0.289 [0.22, 0.36] | 0.199 [0.14, 0.27] | 0.582 [0.50, 0.66] |
| O1 oracle ingredient concepts | 0.130 [0.06, 0.22] | 0.342 [0.23, 0.45] | 0.349 [0.27, 0.45] | 0.289 [0.23, 0.36] | 0.207 [0.14, 0.28] | 0.575 [0.49, 0.66] |
| O2 gold Add events + predicted step events | 0.108 [0.05, 0.17] | 0.312 [0.19, 0.42] | 0.343 [0.26, 0.44] | 0.289 [0.22, 0.36] | 0.199 [0.14, 0.27] | 0.582 [0.50, 0.66] |
| G  gold events → replay (sanity ceiling) | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] |

Sanity: scoring gold against itself gives 1.000 on every metric (the harness is consistent); no predicted run has replay issues.

## What the oracle cascade says
- **Ingredient linking is not the bottleneck.** Giving the compiler the gold concepts (O1) or the gold Add events (O2) changes the headline numbers by at most about 0.03 (state-field accuracy 0.102 → 0.130 / 0.109).
- **Step-event construction and state tracking are.** Even with gold ingredients the compiler recovers about one third of the merge/split/reserve structure (F1 ≈ 0.34), and final alive entities (F1 ≈ 0.31).
- **Over-generation of Transform.** Event counts, gold vs predicted: Merge 80 vs 60, Transform 64 vs 169, Split 18 vs 14, Transfer 15 vs 22, Discard 6 vs 10, Reserve 0 vs 8. The compiler writes a Transform for nearly every process verb; Gold-v1 keeps far fewer, and names named intermediates (Merge) more often.
- **By recipe type (state-field accuracy, P):** {'random': 0.0, 'indian': 0.0, 'simple': 0.2444, 'multi_component': 0.0667, 'drain_discard': 0.037, 'baking': 0.0833, 'reserve_split': 0.25}. n = 2–3 per stratum, descriptive only.

## Why the absolute values are unreliable (Gold artefacts found while diagnosing)
1. 13 of 189 draft events could not be converted (8 in R003595), so some ingredients stay "alive" in Gold (for example mayonnaise in R002919 after the mixing step).
2. Single-output draft splits were padded with a "remainder" entity (4 cases), producing Gold entities no annotator named.
3. Merge `process` strings for draft RECOMBINE events ("complete with remaining bread") are not in the PROC registry (10 events kept as written); Addendum A5 canonicalisation was applied to the rest in S107 and did not change these numbers.
4. 108 of 113 coref mentions are UNKNOWN, so coreference is effectively unevaluated.
5. The draft's event model (every event names an output) differs from the compiler's; part of the gap is convention, not error.
A human correction pass on these artefacts (the lightweight correction list) would move the reference closer to truth; until then treat all P/O1/O2 differences below about 0.1 as noise.

## Consequence for H_STATE (EXP-000007)
Predicted state from the current compiler is far from Gold state, so B4-predicted should not be expected to beat B3 on state-dependent questions; the three-way design (B3 / B4-predicted / B4-gold) is exactly what separates "state is useless" from "state extraction is the bottleneck". The oracle result here already points to extraction. This is a diagnostic, not the H_STATE result.

## Not done (human-gated)
H_STATE question authoring (EXP-000007 requires human-written, state-dependent questions with gold evidence cells) and the B3/B4 run. Handbook gate: NOT_EVALUATED (identical sets; no disagreement information).
