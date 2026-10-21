# TRANSITION_BOOTSTRAP_V0 -- contract (MP-1; defined, NOT run)

**Name and scope.** `TRANSITION_BOOTSTRAP_V0` is a *chemical/nutrient retention + yield/weight-change* bootstrap benchmark. It is **not** a general physical-state transition benchmark. Moisture, pH, texture, colour, phase, sensory and mechanism targets are UNKNOWN/out of scope until legitimate evidence exists.
Status label: E3 aggregate evidence, **unverified**; no row is called Gold (conflict C2).

## 1. Evidence eligibility
- Tiers E1-E4 only (today: E3 = 17,978 rows). E5-E7 excluded. No simulated rows.
- Row must have: ingredient_id and process_id linked (else the row may train a global baseline but is excluded from ingredient/process-conditioned arms), a mapped state variable with registry status ACTIVE or PROVISIONAL, a retention or yield value that is MEASURED or CENSORED (CENSORED kept censored).
- Counts (active EVD): retention_factor MEASURED/CENSORED with ING+PROC linked: USDA 3,274/1,847, Bognar 1,240/1,011, Phenol-Explorer 3,718/0; yield: Bognar 496 (323 linked) food-mass rows; Phenol-Explorer attached yield on 3,718 linked rows from 103 distinct yield records (covariate, not an independent yield target).
- Independent units for resampling: matrix x process signatures: USDA 171, Bognar retention 123, Phenol-Explorer 287, Bognar yield 417. These, not row counts, set the real sample size.

## 2. Inputs and targets
INPUT: ingredient/matrix (+ food group), prior state where known (often unknown), process (+ process family), available conditions (temperature/time/medium; missing axes UNKNOWN), source family, basis (true/apparent retention, fresh/dry weight, per volume).
TARGETS v0: (T1) retention fraction per (matrix, process, state variable) with censoring; (T2) yield/weight-change factor (food mass SVAR). UNKNOWN for every other dimension. Log-retention is a secondary metric scale for ratio targets, not a replacement.

## 3. Baselines (all deterministic first; fixed before any run)
B-0 persistence / no change (retention = 1, yield = 1). B-1 global mean delta. B-2 ingredient-conditioned mean (shrinkage to food group). B-3 process-conditioned mean (process and process family). B-4 ingredient x process lookup/retrieval with hierarchical fallback (exact cell -> same ingredient + process family -> same food group + process -> global). B-5 simple tabular (gradient boosting / regularised regression) **only after B-0..B-4 are reported**. No neural model is selected here; TabPFN or learned models are out of scope for V0. These map to the existing DEL-2 D0-D7 machinery (`src/culinarystate/transition`), which already reports a negative cold-split result for USDA and Phenol-Explorer.

## 4. Leakage-safe split families (declared now)
S-1 random (reference only, expected optimistic); S-2 ingredient x process pair holdout; S-3 matrix-disjoint (unseen ingredient/matrix); S-4 process-disjoint (unseen process signature); S-5 food-group-disjoint (coarse cold start); S-6 study-disjoint (Phenol-Explorer only; USDA is one source family); S-7 source-disjoint (train on one source family, test on another; USDA <-> Bognar overlap is a cross-source agreement check). Group all rows sharing the same (matrix, process, source family) in one fold; keep near-duplicate matrices (e.g. cooked/raw variants of the same food) together; USDA values imputed from similar foods must stay in the same fold as their donors where identifiable. Headline = S-2..S-5 min; S-1 not used for claims.
Leakage risks to log: shared yield sources across Phenol-Explorer rows; one measurement appearing in several sources; multiple compounds per food-process cell treated as independent; censored rows contributing label leakage through the bound.

## 5. Metrics
Censor-aware MAE (retention in fraction) with grouped bootstrap CIs over matrix x process groups; median AE; MAE on log scale for positive uncensored rows; yield MAE; coverage/width for conformal intervals; fraction of predictions on censored rows consistent with the bound; calibration is secondary. Report n_independent_groups beside every number. Always report vs B-0 and vs the best deterministic baseline with paired bootstrap. Source and basis stratified.

## 6. Success / failure criteria (pre-registered)
- **Supported** only if a baseline above B-0 beats B-0 with paired lower bound > 0 on S-3 or S-4 (cold) for T1 or T2 separately, and no gain is explained by source/basis shortcuts (re-run with source-family and basis held constant).
- If gains hold only on S-1/S-2 (random/pair holdout), report as non-cold, as in EXP-000001/2/3.
- Failure is a valid, reportable outcome; no model-complexity escalation on V0.

## 7. Explicitly out of V0
Physical variables beyond yield; mechanism targets; any sensory output; any simulated row; any LLM-extracted unverified (E5) row; any claim of Gold status.
