# V2-DM de-risked plan (R&D reasoning): where a decision layer can pay off, in what order, with kill criteria

v1 is frozen (H6-C); v1 TEST is burned. Everything below is DEV-level until a fresh test set exists. No SOTA language.

## 1. What our NER does today, per entity type (DEV gold spans; crude resolvability audit)
| Entity label | Detected by NER | Linked / normalised by | Resolvable by that ledger/rule | Share of DEV span errors |
|---|---|---|---|---|
| FOOD (TASTEset) / NAME (RecipeDB3) | yes | **ING + ALIAS ledger via the BGE/E5 linker** (2,110 ING, 4,116 ALIAS) | ledger exact 0.71 / 0.46; head word 0.84 / 0.70; linker Acc@1 0.70, R@5 0.85 | **47% / 55%** (mostly boundary: 45/60, 107/175) |
| QUANTITY | yes | grammar parser (`quantity/grammar.py`), no ledger | n/a (parsing) | 13% / 6% |
| UNIT | yes | **UNIT ledger** (74 units) / alias catalogue | 0.96 / 0.85 | 8% / 11% |
| PROCESS (TASTEset) / STATE (RecipeDB3) | yes | **no usable ledger**: the PROC ledger (156) holds cooking-*step* verbs (bake, simmer) while these labels are preparation words (chopped, ground); mapping 0.7% / 10%; STATE ledger is empty | ~0 | 13% / 23% (mostly spurious spans) |
| DF, TEMP, SIZE, PHYSICAL_QUALITY, COLOR, TASTE, PART, PURPOSE | yes (some) | none | none | 2-13% each |
So the NER detects spans for every type, but **linking exists only for ingredients (and units by catalogue)**. EVD (18,156), SRC, MOL are evidence/source/molecule ledgers: not NER vocabulary. A decision layer is therefore **not** "one model for all ledgers": per type it asks a different bounded question, and for several types there is no ledger to choose from yet.

## 2. Where the money is (ranked by error mass x feasibility)
1. **Ingredient-name boundary errors** (45/129 TASTEset, 107/318 RecipeDB3 DEV errors). Only a *candidate-choosing* decision can raise F1: CRF n-best segmentations -> choice. Headroom if all FOOD/NAME boundary errors were fixed: about +2.2 pp (TASTEset) / +1.2 pp (RecipeDB3) span F1; realistic 20-40% of that. Unknown until the n-best oracle (does the right segmentation appear in the top-k?) is measured.
2. **Selective release of REVIEW spans** (Track A; hard baselines R0/CD-S). Value = safe coverage, not F1.
3. **Ingredient linking** (choice among top-K ledger candidates + NONE): Acc@1 0.70 vs R@5 0.85 gap; NIL AUROC 0.66.
4. **STATE spurious spans** (55/72 RecipeDB3 STATE errors are spurious): a KEEP/DROP decision.
5. UNIT/QUANTITY: errors are few and parsing is deterministic -> **no LLM**; PROCESS/STATE/DF normalisation first needs a *ledger* (vocabulary-building, not modelling).

## 3. Why attempts like this fail, and the countermeasure for each
| Failure mode | Countermeasure |
|---|---|
| zero-shot decision model is no better than raw CRF confidence | stage-1 kill criterion below, tested before any training |
| gain is real but only on easy spans | evaluate per label x seen/unseen, report released-error CIs |
| prompt overfitting to DEV | prompts frozen from 3 pre-listed variants on OOF TRAIN only; DEV scored once per model |
| probabilities not calibrated | temperature/logistic/isotonic on OOF, thresholds from CALIBRATION |
| right candidate never in the n-best | measure n-best oracle first; if oracle gain < +0.3 pp, drop Track B |
| TASTEset docs are whole ingredient lists (long state) | `--window` = the ingredient line containing the span |
| everything evidence-level because TEST is burned | reserve a fresh labelled sample (A1/A3 amendments) as V2-FINAL, opened once |
| over-claiming | claim wording limited to what the gate shows; no SOTA wording before an H6-style gate on fresh data |

## 4. Stages with kill criteria (each is a go/no-go; no stage starts before the previous passes)
- **S0 (no new model):** error-mass audit (done above); retrain DeBERTa-base+CRF seed 1 with checkpoint saved + n-best Viterbi (k=5) on OOF/DEV; n-best oracle F1. *Kill Track B if oracle gain < +0.3 pp.*
- **S1 (zero-shot teacher):** Tev1-4B / Nimble on Q3 (exact-correct) for REVIEW spans, and a choice question over CRF n-best candidates for boundary-error cases; p1-p3 prompts. *Stop the whole lane if neither beats the best simple baseline (R0 / CD-S) on safe coverage by a CI-separated margin AND shows no boundary-choice accuracy above the CRF 1-best.*
- **S2 (learning):** supervised fine-tune (LoRA, log loss on the answer tokens = proper scoring rule, equivalent in intent to Jev's calibration objective) on OOF TRAIN decision examples; teacher distillation as an ablation; RL (GRPO, Brier or safe-coverage reward) only if supervised plateaus. *Promote only with CI-separated safe-coverage/error-capture gain over R0/CD-S and damage rate <= fixed errors.*
- **S3 (scope growth):** ingredient-link choice (TOP-K + NONE) and NIL adjudication on linker v2; STATE spurious-span drop. Ledger-less labels: build the vocabulary first.
- **S4 (fresh test):** one frozen evaluation on the fresh labelled sample; then H6-style classification.

## 5. Immediate next actions
1. VPN + server: finish `tev1:4b` pull, smoke test (probability schema, repeatability, malformed rate, latency).
2. S0: retrain/checkpoint + n-best oracle (also needed by the external-validation checkpoint gate).
3. S1 on REVIEW spans of TASTEset and RecipeDB3 DEV.
