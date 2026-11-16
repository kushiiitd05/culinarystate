# 29-diag results synopsis

Status: AI_DRAFTED, 2026-11-11. **Every number in this memo carries DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE / PRIOR_EXPOSURE_REANALYSIS / COND_UNAUDITED / PROVISIONAL_08A / NO_HUMAN_SIGNOFF_D085.**

Source: `reports/step29/diag/diag_results_S179.json`, RUN-S179-DIAG29-001 (D-085; WORKLOG S191).
This is a read-only transcription/interpretation of committed output, not a new model run or a new gate.
No human skim of this newly separated memo is recorded. Existing combined memo remains unchanged.

## Results synopsis

For Phenol-Explorer, D7's random-split predictions are exactly D1 (maximum absolute difference 0.0).
The optimizer has no distinct usable prediction output there; see `d7_vs_d1_review.md` for the fallback
mechanism and the limits of this diagnosis. The basis-removal control leaves D5 unchanged in every family.

For the process-vs-ingredient contrast, only the publication/study-key-disjoint Phenol-Explorer split compares
the arms on equal terms: the paired cluster estimate (D2 loss minus B2 loss) is 0.0992, interval
[-0.0446, 0.2401], from 362 rows in 20 clusters. The interval crosses zero; no direction is read.
S-3 matrix-disjoint makes B2 fall back; S-4 process-disjoint makes D2 fall back, so their differences cannot
be interpreted as a fair test of process information against food identity.

The duplicate control reports 748 Bognár groups (4,916 rows; share 0.9489), 750 USDA groups (3,314;
0.5874) and 138 Phenol-Explorer groups (354; 0.1114). These shares are over each family's diagnostic
subset, not over all ACTIVE EVD rows. Fold grouping changes test compositions; paired loss values from
those distinct folds must not be treated as a paired causal effect of deduplication.

## Permitted wording for report/deck

The diagnostic finds censor-cap sensitivity, repeated source values and an MF fallback to the global mean.
It does not establish a process-information advantage or a learned-model generalisation result.
The full proposal H2 test is DECLARED_NOT_RUN in the H8 register (D-089); the diagnostic cannot replace it.
The remaining tables are in the companion memo files and the frozen JSON; no new threshold or model
selection is made from them.
