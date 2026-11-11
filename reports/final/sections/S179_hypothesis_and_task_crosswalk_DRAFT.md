# Report draft: hypotheses, task crosswalk and current outcomes (S179, 2026-11-11)

Status: AI_DRAFTED / AI_PRECHECKED. D5 and 29-diag outputs carry NON_CITABLE /
NO_HUMAN_SIGNOFF_D085; no independent human gold or AI-persona inter-rater result exists.
This updates report prose after D-080..D-092 without changing any frozen specification or output.

Sources:
- SSOT v15 §5.4 (H1-H5), §12 (Tasks 1-9):
  `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` L697-717 and L1258-1288.
- Proposal brief §2 (H1-H4): `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf`.
- D-008 revised task list, adopted merge in D-080; scope cuts D-089 and
  `registry/h8_scope_cut_register_v1.csv`.
- D5 locked prereg `reports/del5/d5_benchmark_preregistration_DRAFT.md`, locks/freezes under D-085/D-090;
  results D-092 and `reports/del5/d5_score_v1_D085/`.

## 1. Hypothesis numbering and present outcomes (T0-C07-R2)

SSOT and proposal reuse labels for different claims. Unqualified H1-H4 in the final report means
**proposal numbering**, the course contract. Mapping a hypothesis does not establish it.

| SSOT §5.4 | SSOT statement | Proposal mapping | Test/outcome |
|---|---|---|---|
| H1 | State-aware models improve current-state/next-action questions against text/RAG comparators | H1, same claim | D5 S1+S2, B4 vs B1 and B2: RULE_NOT_MET; n=24, AI_DRAFTED_GOLD, CIRCULAR_SELF_CONSISTENCY_ONLY |
| H2 | Process-effect grounding improves transformation-sensitive answers | H2 partly related; proposal instead tests process versus food identity on held-out pairs/studies | 29-diag only, DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / PRIOR_EXPOSURE_REANALYSIS; full proposal H2 DECLARED_NOT_RUN (D-089) |
| H3 | User-context constraints improve feasible actions | Feasibility half of proposal H4 | DECLARED_NOT_RUN (D-089) |
| H4 | State-distance reasoning improves recovery recommendations | Recovery half of proposal H4 | DECLARED_NOT_RUN (D-089) |
| H5 | Selective routing preserves quality while reducing retrieval/model calls | No equivalent proposal hypothesis; proposal H3 instead concerns unsupported claims | Relevance-gate precision/recall NOT_RUN; router control accuracy is a different metric |
| None | No SSOT §5.4 counterpart | Proposal H3, evidence routing/abstention | D5 P1-P3+C, H3 RULE_NOT_MET: P3 abstention condition fails despite sign-test result |

The proposal says calibrated abstention; **D-080 adopted “rule-based evidence-sufficiency abstention
(uncalibrated)”** for B7. No calibration claim is made. D-089 declares proposal H4 and full H2 not run
before the talk. The Step 35 package remains designed/not run under D-080; these tests are not Step 35 results.

### H1 provenance and power

Frozen n=74 differs from planned n=80: S1 and S2 have 12 each instead of 15 each. The ranked overdraft ran
out after review exclusions (D-090); the remaining blocks retain their planned counts. H1 n=24 is the count
used in the result, not n=30. The raw `d5_scoring_result.json`/Markdown retain H1 NOT_COMPUTED because
some answers were unresolved. A separate rung-blind AI check of six unresolved answers is preserved at
`reports/del5/d5_score_v1_D085/d5_h1_after_rung_blind_check_D085.json`; its H1 result, recorded in D-092,
is **RULE_NOT_MET**: B1=B2=B4=6/24 (0.25), each B4 comparison has four discordant pairs, exact two-sided
p=1.0. Six perfectly directional discordant pairs would be the smallest significant configuration; the
realised four cannot reach that criterion. This is not an equivalence result or independent-gold accuracy.
The AI gold is not HUMAN_BLIND; no Kush–Parv agreement statistic exists.

### H3 provenance

The selected test is H3-A, two-sided (D-081/D-083), n=40 P/C questions.
`d5_scoring_result.json.h3_selected` has discordance 16:0 and exact p=0.000030517578125, but
`ood_abstention` records B7 P3 abstention 0/10 versus B2 3/10. The conjunctive rule therefore fails
(D-092; NEG-0051). The 30-claim veto audit was NOT_RUN because it cannot make a failed conjunction pass.
An evidence-boundary amendment must be dated and separately frozen/run; it cannot replace this result.

## 2. SSOT Tasks 1-9, D-008 and actual frozen D5 coverage (T0-C11-R3)

D-080 adopted the revised D-008 merge of equipment and ingredient adaptation into T5 ADAPTATION.
The D5 blocks are not the eight D-008 types: P1-P3 divide evidence regimes, and X is routing controls.

| SSOT task | Adopted D-008 type | Actual D5 block/count | Scope |
|---|---|---|---|
| 1 Current-state tracking | T1 CURRENT_STATE | S1, 12 | H1 |
| 2 Next-action prediction | T2 NEXT_ACTION | S2, 12 | H1 |
| 3 Transformation explanation | T3 TRANSFORMATION_EXPLANATION | None | Not covered |
| 4 Process substitution | T4 PROCESS_SUBSTITUTION | U, 5 shared with task 6 | Partial, descriptive |
| 5 Equipment adaptation | T5 ADAPTATION, merged with 6 | None | Equipment not covered |
| 6 Ingredient adaptation | T5 ADAPTATION, merged with 5 | U, 5 shared with task 4 | Partial, descriptive |
| 7 Mistake recovery | T6 MISTAKE_RECOVERY | None | Not covered |
| 8 Process comparison | T7 PROCESS_COMPARISON | C, 10 | H3 |
| 9 Chemistry relevance | T8 CHEMISTRY_RELEVANCE | P1/P2/P3, 10 each; X, 5 controls | Partial; evidence-regime/control tasks do not measure relevance-gate precision/recall |

Unique questions: S1 12 + S2 12 + P1/P2/P3/C 40 + U 5 + X 5 = 74. The shared U block is counted once.
SEMANTIC is explicit abstention for the talk under D-080 #17. D5 has no result for explanation,
equipment adaptation or mistake recovery. The H8 register controls claim scope; code existing for a
broader task does not imply the task has been evaluated.

## 3. Status and remaining assembly

The pre-registration locks, benchmark review and freezes are AI-delegated (D-085/D-090), labelled
NO_HUMAN_SIGNOFF_D085. No independent-labelling gate is passed by the personas. 07.A-R1 remains NOT_RUN,
and the historical v4 FAIL stays on record. D-092 gives H1/H3 RULE_NOT_MET; full H2/H4 are DECLARED_NOT_RUN.
The earlier open-merge/unsigned/unrun wording in the first S179 draft is superseded by these dated records.
This section and its cited output distinction must be carried into final report/deck assembly.
