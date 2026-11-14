# Technical results update — draft13 November2026

AI_DELEGATED_D085 · NOT_INDEPENDENT · NOT_HUMAN_VERIFIED_UNTIL_REVIEW · NO_HUMAN_SIGNOFF_D085

D-094 author facts and final edits remain excluded. This is a separate technical insert for later author review; the existing report/deck remain unchanged.

| Diagnostic result | Value | Committed/source JSON field |
|---|---|---|
| D-097 DEV_FOODCOM_V1_1 pooled count-match precision/recall | 0.5906 / 0.8097 | `reports/s179/d097_runga_type_table_2026-11-13.json` → `sets.DEV_FOODCOM_V1_1.pooled` |
| D-097 DEV_PILOT20_V1_1 pooled count-match precision/recall | 0.5168 / 0.7131 | `reports/s179/d097_runga_type_table_2026-11-13.json` → `sets.DEV_PILOT20_V1_1.pooled` |
| D-097 P1_A_KUSH pooled count-match precision/recall | 0.6186 / 0.5882 | `reports/s179/d097_runga_type_table_2026-11-13.json` → `sets.P1_A_KUSH.pooled` |
| Blinded AI claim/checker agreement | 14/27; unclear3 | `reports/s179/prv_claim_review_2026-11-13.json` → `agreement` |
| Supplemental AI branch-Gold/router accuracy | 45/74 (0.6081); exact-binomial95%CI [0.4877, 0.7196] | `reports/s179/prv_branch_review_2026-11-13.json` → `result.accuracy` |
| prv CAL metadata verdicts | {'CORRECTED': 13, 'VERIFIED': 3} | `reports/s179/prv_CAL_source_review_2026-11-13.json` → `verdict_counts` |

All numbers above are DIAGNOSTIC, not independent evidence or confirmatory results. D-097 uses per-recipe min(type counts), not aligned event correctness or state accuracy. Its first output remains the predeclared structural result; the subsequently declared D-102 process-aware amendment is POST_HOC_AMENDMENT and must never replace the first result in presentation.

The paired diagnostic comparison with D0 now exists in `reports/step29/diag/paired_vs_d0_S179_2026-11-13.json` → `result.families`. The Phenol-Explorer rungs mostly perform worse than D0: this negative outcome must remain visible, alongside the source/split-specific exceptions. PRIOR_EXPOSURE_REANALYSIS is not held-out D2/H2 confirmation. Full D2/H2 are not supplied by these contrasts.

The checkpoint/seal/P1 data remain with Kush; their upstream counts/hash-bound results resolve availability at project level, not receipt or local rerun on Parv’s Mac. NER-vs-lexicon overlap is agreement, not labelled NER accuracy. See the dependency supersession note.

Scientific limits remain: eligible SIM-VAL0 and G15 PASS0 in the existing scorecards, no new validation eligibility or causal claim. No author contributions, personal agreement, final signoff or actual rehearsal is inferred.
