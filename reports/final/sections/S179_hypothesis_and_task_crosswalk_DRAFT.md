# Report section draft: hypotheses and benchmark tasks crosswalk (S179)

Status: **AI_DRAFTED** for the final report (board items T0-C07-R2 and T0-C11-R3). It records mappings only: it makes
no claim that a hypothesis holds, and it decides nothing. Where the mapping needs a human choice, the open decision is
named. Written 2026-11-10 by the Mac agent on `kush/s179-finish-fixes`.

Sources:
- SSOT v15 §5.4 (H1-H5) and §12 (Tasks 1-9): `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md` L697-717, L1258-1288.
- Proposal brief §2 (H1-H4): `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf`.
- D-008 (benchmark task types, PROPOSED, revised 2026-10-18): `DECISIONS.md` L40-48.
- D5 pre-registration (DRAFT, unsigned): `reports/del5/d5_benchmark_preregistration_DRAFT.md` §1, §4, and the S178
  amendment draft `reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md`.

## 1. SSOT H1-H5 against proposal H1-H4 (T0-C07-R2)

The two lists use the same labels for different claims. Only H1 means the same thing in both. In this report,
"H1-H4" without a prefix means the **proposal** numbering, because the proposal is the course contract.

| SSOT §5.4 | Statement (SSOT) | Proposal | Statement (proposal) | Match | Planned test |
|---|---|---|---|---|---|
| H1 | State-aware models beat text-only / RAG-only models on current-state and next-action tasks | H1 | State-aware retrieval beats text-only / dense RAG on current-state and next-action questions | same claim | D5 S1+S2, B4 vs B1 and B4 vs B2, exact McNemar (prereg §4) |
| H2 | Process-effect grounding improves transformation-sensitive questions and explanations | H2 (part) | Process information beats food-identity-only models on unseen ingredient × process pairs and unseen studies | related, different unit: the SSOT claim is about answers, the proposal claim is about a learned model on held-out pairs and studies | proposal H2: D2 learning diagnostic only (29-diag); SSOT H2 has no test of its own |
| H3 | User-context constraints increase the feasible-action rate | H4 (part) | Feasibility filtering and recovery reasoning respect user constraints and state divergence better than a generic chatbot | SSOT H3 = the feasibility half of proposal H4 | none before 25 Nov |
| H4 | State-distance reasoning improves mistake-recovery recommendations | H4 (part) | (as above) | SSOT H4 = the recovery half of proposal H4 | none before 25 Nov |
| H5 | Selective routing keeps quality while reducing unnecessary process-effect retrieval or model calls | none | — | no proposal hypothesis; nearest is proposal H3 (routing), but H3 measures unsupported claims, not calls saved | relevance-gate precision/recall (T0-C07-R1, not measured) |
| none | — | H3 | Evidence-class routing with calibrated abstention lowers the unsupported-claim rate at a small cost in coverage | no SSOT §5.4 hypothesis states it; it draws on SSOT H2 (evidence) and H5 (routing) | D5 P1-P3 + C, UCR(B7) < UCR(B2), question-level bootstrap (prereg §4) |

Notes:
- **Proposal H3 wording.** The proposal says "calibrated abstention". The S178 amendment draft (D-D5-8, not yet
  decided) would describe B7 as "rule-based evidence-sufficiency abstention (uncalibrated)". If adopted, the report
  must not call the abstention calibrated.
- **Scope.** Proposal H4 (both halves, so SSOT H3 and H4) and the full proposal H2 test are candidates for the H8
  scope decision (T9-C07-R4, human). Until it is recorded, the report lists them as "not tested", not as dropped.
- **Status today.** No hypothesis has been tested. The D5 benchmark is drafted but not reviewed, frozen or run, and
  the pre-registration is unsigned.

## 2. SSOT Tasks 1-9, D5 blocks and D-008 T1-T8 (T0-C11-R3)

D-008 (revised) proposes eight task types from the nine SSOT tasks by merging equipment and ingredient adaptation.
That merge is still open for Kush and Parv. The D5 benchmark has eight blocks, but they are not the eight D-008 types:
P1-P3 split one task by evidence regime (DIRECT, similar-only, none), and X holds router controls.

| SSOT §12 task | D-008 (revised, PROPOSED) | D5 block(s), n per prereg draft | Hypothesis | Covered? |
|---|---|---|---|---|
| 1 Current-state tracking | T1 CURRENT_STATE | S1 current state, 15 | H1 | yes |
| 2 Next-action prediction | T2 NEXT_ACTION | S2 next action, 15 | H1 | yes |
| 3 Transformation explanation ("why brown the onions?") | T3 TRANSFORMATION_EXPLANATION | none | — | **no** |
| 4 Process substitution | T4 PROCESS_SUBSTITUTION | U substitution, 5 (shared with task 6) | descriptive only | partly |
| 5 Equipment adaptation | T5 ADAPTATION (merged with 6) | none | — | **no** |
| 6 Ingredient adaptation | T5 ADAPTATION (merged with 5) | U substitution, 5 (shared with task 4) | descriptive only | partly |
| 7 Mistake recovery | T6 MISTAKE_RECOVERY | none | — | **no** |
| 8 Process comparison | T7 PROCESS_COMPARISON | C comparison, 10 | H3 | yes |
| 9 Chemistry relevance | T8 CHEMISTRY_RELEVANCE | P1 DIRECT 10, P2 similar-only 10, P3 none / OOD (gold ABSTAIN) 10; X controls 5 | H3 (P); descriptive (X) | partly: see below |

**Not covered by D5:** SSOT Tasks 3, 5 and 7 (D-008 T3, T5 for equipment, T6). No D5 question asks for an
explanation, an equipment adaptation or a recovery from a wrong state. These tasks have no result in the report.

**Partly covered:**
- Tasks 4 and 6 share one block of 5 questions, reported descriptively; no claim rests on it.
- Task 9. The P blocks test evidence-bounded answers once chemistry is in play. They do not test the relevance
  decision itself, that is, whether a question needs process-effect reasoning at all. X tests router controls; the
  amendment draft would make X three food-safety questions (gold REFUSE) and two out-of-scope, empty or vague
  questions. Precision and recall of the relevance gate are not measured (T0-C07-R1).

**Size.** The pre-registration draft uses S1 and S2 at 15 each (n = 30 for H1). The amendment draft offers 30 each
(n = 60) as an option. The report states whichever is signed.

## 3. Open human decisions this section depends on

- D-008: approve the 8-type list and the merge of SSOT Tasks 5 and 6.
- D-D5-8: the "uncalibrated" wording for B7 (proposal H3).
- H8 scope decision (T9-C07-R4): drop or defer proposal H4 and the full H2 test before the talk.
- D5 pre-registration signatures (Kush, Parv; D-071).
