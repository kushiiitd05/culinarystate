# D-028 (DRAFT, UNSIGNED) — residual rulings still needed before Step 08

Not recorded in `DECISIONS.md`. A human (Kush, with Parv) must approve, edit or reject each item. Nothing here is in force.
Numbering: D-026 is the recipe-usage decision; D-027 is the Execution Plan v2 rulings R-01..R-20 (recorded, `reports/master_plan/review_queue/rulings_D-027_R01-R20.md`). This draft was first written as "D-027" and is renamed because D-027 is taken. Items already settled by D-027 are marked SUPERSEDED; only the unmarked items still need a signature.

## Rulings requested
1. **[SUPERSEDED by D-027 R-05]** **07-DEP (dependency edge).** Step 08 SOFT-depends on the Step-07 human condition audit (07.A). 07.A stays a HARD gate for Step 15 condition fields and for Steps 23, 29-33 (any condition-using claim). 07I-C / `split_group_id` stays a HARD gate for any recipe-level test split (15 recipe plane, 16-20, 35, 36) but NOT for Step 08. Replaces the S133/S134 wording "Step 08 only after the gate". Reason: lineage uses source/document/study structure, not condition values.
2. **[PARTLY SUPERSEDED by D-027 R-02; remainder open]** **Base declaration (Steps 03/04).** Declare the existing MP-1 contracts and Step 03/04 v1 as the FROZEN base, so that later needs are additive versions (v1.1; 04.L lineage addendum; 04.K kinetic/trajectory addendum) rather than evidence that the steps were never complete. Record rulings C2-C8 (only C1 is recorded, D-018). Resolves the audit's finding that MP-1 is "DRAFT FOR REVIEW" in its header but FROZEN_CONTRACT in the authority map.
3. **[SUPERSEDED by D-027 R-03]** **Lineage contract 04.L.** Approve the entity chain SRC>DOC>STUDY>SEXP>SMP>OBS>AGG/DRV with typed LIN edges, the keys `study_id`, `lineage_root_id`, `split_group_id` and `independence_resolution` {STUDY, PUBLICATION_ONLY, SOURCE_FAMILY_ONLY, UNKNOWN}; UNKNOWN never in test sets; fallback grouping named "publication-component CV", never "study-disjoint". Additive only; EVD stays the consumer view.
4. **Pre-registration of Step 08 gates.** Approve (or change BEFORE any lineage computation) the rows in `registry/preregistered_thresholds_v1.csv (47 rows, THR-*; the older 14-row `_v1_DRAFT.csv` is redundant)`. After signing, a gate may not be loosened post hoc.
5. **07.A amendment.** Approve the process-integrity amendment in `reports/step07/condition_audit_protocol_amendment_v4_1_DRAFT.md` BEFORE any v4 label exists. The primary gate is unchanged: pooled Cohen's kappa >= 0.80 AND no systematic critical-field disagreement.
6. **[SUPERSEDED by D-027 R-06, R-07, R-14, R-17, R-18]** **Rejected items (recorded so they are not reopened by accident).** Per-field kappa >= 0.80 as a new mandatory criterion; any edit to packet v4; freezing ascorbic acid as the simulator before the Step 10/11 census; the large Deep Gold build before the 19A pilot; breaking Step-36 schema changes before Steps 08/09/23.

## Effects if approved
Step 08a may be authorised (CPU, Mac, existing 17,978 EVD rows, no new values). Step 08 remains NOT STARTED until a separate go-ahead.

Signed: ____________ (Kush)   ____________ (Parv)   Date: ____________
