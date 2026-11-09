# MNAR claim boundary for the 29-diag memo, the talk and the paper: allowed and forbidden wording (DRAFT, S178, T6-C08-R3)

Status: **AI_DRAFTED / PROPOSED, UNREVIEWED.** Not a decision, not a signature, not an approval (D-071). Written 2026-11-09 by the S178 EVD lane (an AI agent) for Kush to read (the board asks 0.3 h) before the text is used
verbatim in the H2 / D2 slides, the 29-diag memo and the paper. It changes no pre-registration: `reports/step29/29diag_preregistration_DRAFT.md` (and its S178 amendment draft) are untouched. Counts only; no third-party text.

Grounding (read, not recalled): SSOT v15 section 220.10 "MNAR claim boundary" (L23678-23691), section 220.5-220.8, section 222.5 "Left-censored MNAR measurements" (L23992-24001), section 227.4 (C3, still `[HYPOTHESIS]`),
plan AM4 "Propensity/MNAR" (`docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` L3615-3624), and the 29-diag pre-registration (no pass gate; the memo may not say "supported", "beats" or "validated").

## 1. The paragraph (use verbatim, or edit and say so)

> Which food-by-process-by-target cells exist in our evidence table was decided by what researchers and database compilers chose to measure and publish, not by us. That observation process is plausibly
> missing-not-at-random (MNAR), and we treat it as a structure to model and to stress-test, not as a fact we have established. In the October DEL-2 run we fitted a crude propensity model of cell coverage (food,
> process and target frequencies only) and reported each weighted error beside the unweighted one; a clipping sweep and an overlap check are planned and not yet done. Such weights can only serve as a sensitivity analysis: they ask
> whether a conclusion survives plausible corrections for who got studied, and they are not an estimate of the true missingness mechanism, which the data cannot identify without external validation. Separately, a
> third of the retention values in the table are right-censored at the source's own cap; we keep them as censored bounds with a flag and never fill them in. Nothing here supports a claim about foods, processes or
> targets that no source measured; for those the system answers UNKNOWN.

(One paragraph, 180 words; sentences 1-2 are the allowed claim of section 220.10, sentence 3 says only what exists today (DEL-2 diagnostic, no sweep, no overlap report), sentence 4 the AM4 stance, sentences 5-6 the censoring and UNKNOWN rules.
When T6-C08-R1 (propensity model with clipping sweep and positivity report, wave POST) is done, replace the last clause of sentence 3 by what was done; until then do not write that a sensitivity analysis was performed.)

## 2. Allowed wording

| # | We may say | Why it is safe | Source |
|---|---|---|---|
| A1 | "the observation process is plausibly MNAR and we model / sensitivity-test this structure" | the exact sentence the SSOT allows | SSOT 220.10 |
| A2 | "propensity weighting is a sensitivity analysis: does the conclusion survive plausible corrections" | the SSOT's stated goal of the propensity model | SSOT 220.6 |
| A3 | "coverage is concentrated: a few foods, processes and targets hold most observed cells" | a count, checkable (EVD card section 4 and 10; coverage table `reports/s178/evd/evd_coverage_vs_corpus_demand_v1.md`) | counts |
| A4 | "unweighted and weighted results are shown side by side" (DEL-2: yes, one fixed clip at 0.001). Add "with a clipping sweep and an overlap report" only after T6-C08-R1 is done | AM4 requires both and the positivity / overlap report | AM4; `transition/evaluate.py` |
| A5 | "censored values are kept as bounds with a flag" | what the builder does (`transition/dataset.py`) | S178 audit `reports/s178/evd/transition_no_imputation_audit_v1.json` |
| A6 | "naive evaluation over observed cells may overestimate generalisation into unstudied regions (hypothesis C3)" | stated as a hypothesis, as the SSOT does | SSOT 227.4 |
| A7 | "for an unmeasured food x process x target the system returns UNKNOWN, never 0 and never a mean" | project law (SSOT 141, D-077) | laws 1-2 |

## 3. Forbidden wording

| # | We must not say | Why not |
|---|---|---|
| F1 | "our propensity model recovers the true missing-data mechanism" (or "identifies", "estimates the MNAR mechanism") | SSOT 220.10 forbids it without external validation; MNAR is not identifiable from the observed cells alone |
| F2 | "we corrected for MNAR" / "propensity-corrected results are unbiased" / "the weighting removes selection bias" | the weights depend on observed covariates only (three marginal frequencies); they cannot correct selection on unobserved values |
| F3 | "the AUC of 0.81-0.91 proves strong MNAR" | that AUC (DEL-2, plan v2 L1304; not recomputed in this lane) says marginal food / process / target frequencies predict which cells exist, i.e. coverage is concentrated. It is a statement about observed covariates, not about dependence on unobserved values |
| F4 | "random row splits are fine after weighting" / "weighting replaces study-disjoint tests" | SSOT 220.8: propensity weighting does not license random row splits; rows from one paper stay dependent |
| F5 | "the model generalises to unstudied foods or processes" (from a cold-split score alone) | an unstudied cell has no measurement; a held-out cell is still a studied one. 29-diag has no pass gate and no performance claim |
| F6 | "missing cells mean no change", "unmeasured means zero loss", or any mean / zero / half-minimum fill | breaks law 1 (UNKNOWN is never 0). The cell builders do not fill (tests `tests/unit/test_s178_evd_no_imputation.py`) |
| F7 | "the censored retention values were imputed" or "are missing at random" | they are right-censored at the source's cap (USDA 97.5 %, Bognar 99.5 %) and carried as bounds; their share (below) is a feature of the source's rounding rule, not random missingness |
| F8 | "the table is representative of the food-science literature" | one USDA table, one Bognar review and the Phenol-Explorer set; USDA and Bognar are one independence group each; no coverage claim beyond the counts |
| F9 | "supported", "beats", "validated" in the 29-diag memo | the pre-registration forbids them; every number carries DIAGNOSTIC, BOOTSTRAP_UNVERIFIED, NON_CITABLE |

## 4. Two kinds of missingness, never merged in wording

1. **Cell-level (which cells were studied): the MNAR / propensity question.** Handle with a coverage propensity, positivity and overlap report, unweighted beside weighted, and sensitivity to the propensity model (AM4). 
2. **Value-level (a measured value reported only as "at least the cap"): left or right censoring.** SSOT 222.5: prefer censored likelihoods; use censoring-aware imputation only for analyses that need complete covariates; retain the flag. In the DEL-2 builders a censored cell enters training at its stated bound (a documented substitution, not a zero, mean or half-minimum). The 29-diag cap-artefact rerun exists to show how much of any lead comes from that bound.

## 5. Numbers on file that the paragraph may cite (counts only, all E3 UNVERIFIED, COND_UNAUDITED)

- Cells that reach the cell tables: 17,458 of 17,978 ACTIVE rows (the other 520 are 496 Bognar mass-yield rows with no retention factor and 24 USDA rows whose retention is UNKNOWN: dropped, not filled).
- Censored (GT_CAP) cells: 5,894 of 17,458 (33.76 %): Bognar 3,274 of 6,594 (49.65 %), USDA 2,620 of 6,994 (37.46 %), Phenol-Explorer 0. Source: `reports/s178/evd/transition_no_imputation_audit_v1.json`.
- Zero cells that are a builder fill: 0. The 61 cells with y = 0 are all Phenol-Explorer rows whose ledger value is MEASURED 0 (the source's after/before ratio is 0); whether those mean a true zero or a not-detected value is not stated in the ledger and should be checked at the source before any log-scale model is read (the log-target wrapper floors y at 0.001).
- USDA values: the SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE flag stands; the ledger cannot say which USDA values the source itself imputed from similar foods.
- Pair coverage against corpus demand: a seeded 1,000-recipe non-BBC sample asks about 12,501 distinct (ingredient, process) pairs and 111 (0.89 %) hold an EVD pair; EVD has 338 routable pairs in all, 115 for vitamin C, 102 of which the full non-BBC census saw among 125,172 distinct pairs (`reports/s178/evd/evd_coverage_vs_corpus_demand_v1.md`).

## 6. What the 29-diag memo must also carry (from AM4 and the pre-registration)

AM4 asks for the items below. The 29-diag pre-registration contains no propensity analysis and T6-C08-R1 is deferred (POST), so today the memo can carry only the DEL-2 facts (marginal-frequency propensity, a fixed clip at 0.001, unweighted beside IPW-weighted MAE, no sweep, no overlap report) and must say the rest is not done. Variables used in the propensity model (food frequency, process frequency, target frequency, as in DEL-2), its calibration, the positivity / overlap check, a clipping sweep, and unweighted metrics beside weighted ones. No weighted number is a headline.
The propensity is labelled "diagnostic / modelling assumption, not known truth". If a statement needs more than this, it is a new claim and needs its own pre-registration.

## 7. Open questions for Kush

1. Keep sentence 5-6 (censoring, UNKNOWN) inside the MNAR paragraph, or move them to the data section of the slide? 
2. Is the 61-cell Phenol-Explorer zero question worth a source check before 29-diag runs (Sat 14 Nov), because the log-target models floor those cells?
3. The H2 / D2 slide identifiers named on the board were not opened by this lane; place the paragraph where you want it.
