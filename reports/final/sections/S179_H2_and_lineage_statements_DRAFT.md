# H2 and lineage: report/deck wording (S179 draft, 2026-11-11)

Status: AI_DRAFTED / AI_PRECHECKED. The passages below are ready for report/deck assembly. They do not record a
human reading of this new draft. T2-C06-R2 and T6-C04-R3 human-review acceptance remains open.

## Lineage statement (T2-C06-R2)

The G08-3 edge-audit gate **FAILED for both reviewers**. In the committed audit, STRONG edges are 50/50 correct
for each reviewer, Wilson lower bound 0.9286523998213857. For B2, the audit records 49/50 for Kush
(lower bound 0.8950455630610349) and 0/50 for Parv (lower bound 0.0). For B3 the corresponding counts are
13/50 (lower bound 0.15871527430089563) and 0/50 (lower bound 0.0). The gate's Wilson lower-bound threshold
is 0.9. Uncertain edges count as errors under the registered conservative rule. These are historical human
audit results, transcribed without assigning a new AI reviewer a human identity.

Source, exact fields: `reports/step08/step08a_audit_result_v2.json`,
`G08-3`, `edge_precision.<reviewer>.<stratum>.correct`, `.n` and `.wilson_lower`.
The miss-rate check is REPORT_ONLY: 2/200 duplicates for Kush and 0/200 for Parv
(`THR-08A-18_miss_rate`). It does not repair the edge gate.

The provisional feasibility export has 127 groups, with USDA and Bognár one group each. Its headline under
reading A (tier eligibility alone) is **publication-component CV**; the weakest label across target families
and readings is **leave-one-source-family-out**. Under reading B (also human verification), eligible pool n=0.
Phenol-Explorer has 125 publication-key groups; these are not confirmed experiment boundaries. Lab-disjoint
feasibility is NEED_DATA. Source: `exports/lineage/step08a_v1/feasibility.json` and `feasibility_report.txt`.

**One-line implication for every H2 figure:** provisional publication keys and the failed lineage edge audit
prevent reading these diagnostics as evidence of generalisation across independently verified studies.
USDA and Bognár have no study-disjoint estimate.

## Honest H2 slide text (T6-C04-R3)

**Title:** Process information versus food identity: diagnostic, no direction established.

**Labels applying to every slide number:** DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE /
PRIOR_EXPOSURE_REANALYSIS / PROVISIONAL_08A / COND_UNAUDITED / NO_HUMAN_SIGNOFF_D085.

On Phenol-Explorer's provisional publication/study-key-disjoint split, process-mean loss minus ingredient-mean
loss is **0.0992 [−0.0446, 0.2401]**, with **362 rows / 20 clusters**. Positive means lower ingredient-mean
loss; the interval crosses zero. Matrix-disjoint favours the process arm by construction; process-disjoint
favours the ingredient arm. Only the provisional study-key split compares the arms on equal terms.

Source: `reports/step29/diag/diag_results_S179.json`,
`result.families.PHENOL-EXPLORER-3.6.contrast_d2_vs_b2.splits.study_disjoint`.

Bognár repeated-value share is **0.9489** and USDA **0.5874** within their diagnostic subsets
(`duplicate_control.share_of_rows`); each source is one lineage group. The original data were already used
by DEL-2 and the exploratory Step 30 run. This is prior-exposure reanalysis, not a fresh independent test.
D7's Phenol-Explorer random predictions equal the global mean D1 exactly
(`d7_vs_d1_max_abs_pred_diff = 0.0`); no learned-model advantage follows.

**Conclusion to show:** Full proposal H2 is DECLARED_NOT_RUN before the talk (D-089; H8-02). The diagnostic
cannot replace that test. No process-information advantage or independent-study generalisation is claimed.

## Review and assembly boundary

The writer checked these statements against the cited committed files. This is an AI precheck, not a human
signature or inter-rater result. The original audit, feasibility export, failed gate and frozen outputs remain
unchanged. Human review required by the board and incorporation into the final deck remain pending.
