# Step 04.6-min — data-plane registry rows and firewall rules for the lineage and kinetic records

**Status: DRAFT_PENDING_H4.** Written 2026-10-26 (D-027 / Plan v2 §7: contract and documentation only). Nothing is approved or applied; the CSV in section 3 is the proposed content of `registry/data_plane_registry_v1.csv`, which is **not** created by this step.

Revision r1 (2026-10-26, still DRAFT_PENDING_H4): the two cells in section 4 that depend on the reviewed 04.1 / 04.3 rules (KIN mandate threshold, UNKNOWN handling) were updated; the plane codes and rows 1–26 are unchanged.

What the Step 04 card defines for 04.6-min: `registry/data_plane_registry_v1.csv` rows + rules for **EVD, DOC / LIN / SEXP / SMP / OBS, KIN / KINPT, recipe identity and split groups**, carrying **FW-09** (tier / provenance / verification / design stay four fields, D-018; E5–E7 and IMPUTED never test / calibration), **FW-11** (split assignment from identity / lineage keys before any test metric; UNKNOWN never in test), **FW-12** (namespaces) and **FW-15** (trajectories stored as series), plus the **plane-qualification rule for `split_group_id`**. It is a listed precondition of Step 08 (H4 approval required). The remaining audit firewall rules (FW-01…08, 10, 13, 14, 16) are **not adopted** by the plan and are not defined here (Plan Step 04 "Audit proposals NOT adopted"); where a row cites one for context it says so.

Source of the plane vocabulary and registry columns: Audit v2 Part M0 (`reports/master_plan/master_plan_research_audit_v2.md` §1, §6, ~L11680–11830) — PROPOSED, adopted here only for the rows below.

---

## 1. Planes used by these rows

| Code | Plane | Holds | Epistemic status |
|---|---|---|---|
| P-SRC | SOURCE | immutable raw source records, snapshots, raw files, source manifests | as received; never edited |
| P-REC | RECIPE SEMANTIC | recipe pointers, mentions, recipe identity / families, planned procedure | TEXT_STATED; never chemistry truth |
| P-EVD | SCIENTIFIC EVIDENCE | measured / compiled attestations and their lineage, conditions, methods, trajectories, author-reported parameters | tiered E1–E5 (all E3 today) |
| P-MOD | MODEL | predictions, imputations, learned embeddings, **fitted project parameters**, model cards | MODEL_ESTIMATED / IMPUTED; never evidence |
| P-SIM | SIMULATION | simulator runs, E7 synthetic priors | SIMULATED; never evaluation truth |
| L-GOV | GOVERNANCE / EVALUATION | splits, claims, gates, thresholds, human-verification queues | reference plane records; never feed values back |

The SSOT keeps two partitions (§232.3 four evidence planes; §233.7 five memory classes) that disagree with the six-plane list; the crosswalk is the audit's proposal (SSOT change request CR, PROPOSED_ONLY). No SSOT text is changed.

## 2. Rules

| Rule | Text | Enforced by | Negative control (scratch only) |
|---|---|---|---|
| **FW-09** | tier, provenance class, verification status and design strength are four separate fields (D-018); E5–E7 and IMPUTED rows are never in a test or calibration set; OCCURRENCE rows are never process-effect evidence. | EVD validator + split builder | an E5 row in a calibration set → reject |
| **FW-11** | Split assignment comes only from the identity / lineage keys and is made before any test metric is seen; four partitions TRAIN / VALIDATION / CALIBRATION / TEST; an UNKNOWN-independence row is never in test (this draft: TRAIN only, `lineage_contract_v1_1.md` D-5). | split builder; sealed-test access log | a lineage component spanning train and test → reject |
| **FW-12** | Namespace registry: no prefix is used for two object kinds (collision examples: `SIM-` similarity registry vs simulation ids, `MODEL-` ML card vs formula registry, `MEAS-` method not measurement, `EXP-` ML run not scientific experiment, `CLM-`). | ID minter (`_ids.jsonl`) + CI scan | minting `SIM-` for a simulation while the similarity registry uses it → reject (04.9-min) |
| **FW-15** | Trajectories are stored as series (KIN / KINPT) with the DIGITIZED flag where applicable; no kinetic parameter is derived from endpoint aggregates (SSOT §211.48). | KIN validator (Step 09) | an Arrhenius fit on USDA RF rows → reject |
| **PQ-1** (new here; name chosen to avoid claiming an audit number) | `split_group_id` is one column name in two planes. Values are plane-qualified: `SPLITGRP-EVD-######` (evidence plane) and `SPLITGRP-REC-######` (recipe plane). There is **no cross-plane join** and no record carries both. A claim that needs both planes needs its own link artefact and H4 decision (none exists). `lineage_root_id` (`LROOT-`) exists in the evidence plane only. | schema patterns (evidence drafts accept only the EVD prefix); FW-12 scan; split builder | a `SPLITGRP-REC-` value in an evidence record, or a table that mixes both prefixes → reject |

PQ-1 resolves plan conflict X1 / open conflict 2 (R-03 evidence components vs R-08 recipe recall-oriented groups) and needs Kush's ratification (ID scheme, H4).

---

## 3. Draft `registry/data_plane_registry_v1.csv`

Columns as proposed by the audit (§6): `record_type_or_path, plane, discriminator_field, discriminator_value, owner_step, writers, readers, may_supply_magnitudes, may_supply_labels, may_enter_test_or_calibration, countable_as_independent_evidence, firewall_rules, status, notes` — one row per (record type × discriminator value). `*` = any value. `Y only if …` rows are conditional, not unconditional.

```csv
record_type_or_path,plane,discriminator_field,discriminator_value,owner_step,writers,readers,may_supply_magnitudes,may_supply_labels,may_enter_test_or_calibration,countable_as_independent_evidence,firewall_rules,status,notes
SRC,P-SRC,,,pre-spine; 06,ingest tools,all steps,N,N,N,N,FW-12,EXISTS_APPEND_ONLY,source identity; carries licence_status and storage_rule; not evidence
SNAP,P-SRC,,,pre-spine,ingest tools,08a; 09,N,N,N,N,FW-12,EXISTS_APPEND_ONLY,hashed retrieval of a source file; DOC.snapshot_id reuses it
DOC,P-SRC,doc_kind,*,08a.1; 08b; 09,08a; 08b; Step-09 intake,08a; 08b; 09; 15,N,N,N,N,FW-12,DRAFT_PENDING_H4,manifest of a file actually held (sha256); join point between P-SRC and P-EVD; the plane choice P-SRC is a draft decision
STUDY,P-EVD,design,*,04.1 -> 08a.2,08a,08a; 08b; 15; 27; 29-33,N,N,N,N,FW-11; FW-12,EXISTS_APPEND_ONLY,"125 rows, all design=UNKNOWN; study identity only; new versions appended in 08a.2"
LIN,P-EVD,edge_type,*,08a; 08b,08a; 08b detector,split builder; reports,N,N,N,N,FW-11; FW-12,DRAFT_PENDING_H4,typed lineage edges; an edge is not evidence; only Kush or Parv can set HUMAN_CONFIRMED
SEXP,P-EVD,comparison_type,*,04.1 -> 08a (PE subset); 09,08a; 09 extractors,09; 12-15; 24-27,N,N,N,N,FW-12,DRAFT_PENDING_H4,scientific experiment; NOT EXP- (ML run)
SMP,P-EVD,role,*,04.1 -> 08a (PE subset); 09,08a; 09 extractors,09; 12-15; 23-27,N,N,N,N,FW-12,DRAFT_PENDING_H4,food material at a state
OBS,P-EVD,value_origin,MEASURED,09; 08a (PE subset),09 extractors; 08a,12; 14; 15; 23-27; 29-33,Y,Y,"Y only if tier E1-E4 AND human verified (G14-3, G15-H) AND independence_resolution != UNKNOWN","Y (counted per lineage_root_id, never per row)",FW-09; FW-11; FW-12,DRAFT_PENDING_H4,what the document reports; licence_status per row
OBS,P-EVD,value_origin,DIGITIZED,09,09 extractors,24-27,Y,Y,"Y only as above AND tool, version and uncertainty present",Y (per lineage_root_id),FW-09; FW-11; FW-15,DRAFT_PENDING_H4,never silently merged with tabular values
OBS,P-EVD,value_origin,ESTIMATED_FROM_SUMMARY,09,09 extractors,reports,Y,N,N,N,FW-09,DRAFT_PENDING_H4,flagged estimate (median/range -> mean/SD); never recorded as MEASURED; label/test exclusion is a draft decision
AGG,P-EVD,origin_type,DATABASE_AGGREGATE,12; 08a,08a; export builder,12; 15; 23-27; 29-33,Y,Y,"Y only after human verification of held-out labels (no E3 row is Gold until verified, MP-1 C2); SOURCE_FAMILY_ONLY: leave-one-source-family-out only","Y, as ONE node per source family / release",FW-09; FW-11; FW-15,DRAFT_PENDING_H4,"USDA R6, Bognar; member lineage NOT_IDENTIFIABLE; no kinetic parameter may be derived from AGG rows"
DRV,P-EVD,value_origin,DERIVED_DETERMINISTIC,08a.5; export builder,08a; export builder,23-27; 29-33,Y,Y if all parents are eligible,Y iff every parent is eligible AND in the same partition,N (counted through the parents' lineage roots),FW-09; FW-11,DRAFT_PENDING_H4,parents are evidence-plane ids only; parent union = one split group (G08-2)
DRV,P-EVD,value_origin,ESTIMATED_FROM_SUMMARY,09,09 extractors,reports,Y,N,N,N,FW-09,DRAFT_PENDING_H4,flagged estimate; label/test exclusion is a draft decision
KIN,P-EVD,evidence_tier,E1-E4,04.3 -> 09; 10; 11,09 extractors,24; 26; 27; 32,Y,Y,"Y only if human verified; series atomic (all KINPT, all KIN of a condition grid in one partition)",Y (per lineage_root_id),FW-09; FW-11; FW-15,DRAFT_PENDING_H4,time series stored as series; fits AUTHOR_REPORTED only
KIN,P-EVD,evidence_tier,E5,09,09 extractors,reports,Y,N,N,N,FW-09; FW-15,DRAFT_PENDING_H4,"LLM-extracted, unverified; candidate generation only"
KINPT,P-EVD,evidence_tier,(follows parent KIN),04.3 -> 09,09 extractors,24; 26; 27; 32,Y,Y,follows the parent KIN,N (counted through the KIN),FW-09; FW-11; FW-15,DRAFT_PENDING_H4,exactly one OBS per point; never merged into an endpoint
EVD,P-EVD,tier,E1-E4,05 (export v2 in 08a); 09-15,ingest tools; ES-1.1 exporter; 09 verifier,08; 12-15; 23-25; 27; 29-33; 36,Y,Y,Y only if human verified (E3 held-out labels need verification),Y (per lineage_root_id),FW-09; FW-11,EXISTS_APPEND_ONLY,"consumer view of the evidence graph; today 17,978 ACTIVE rows, all E3"
EVD,P-EVD,tier,E5,09,09 extractors,reports,Y,N,N,N,FW-09,EXISTS_APPEND_ONLY,never silently promoted E5 -> E4
EVD,P-MOD,provenance_class,IMPUTED | MODEL_ESTIMATED (tier E6),24; 30,model builders,30; 33; 34,N,N,N,N,FW-09,DRAFT_PENDING_H4,prior or stress test only; never evidence; stated here because the evaluation-use column of the provenance registry disagrees with SSOT 223.13 on IMPUTED
EVD,P-SIM,provenance_class,SIMULATED (tier E7),26; 28,simulator,27; 30; 33; 34,N,N,N,N,FW-09; SSOT 223.14,DRAFT_PENDING_H4,"never evidence, never Gold, never test or calibration; generated only from a Step-27-passed simulator version"
XTR / ADJ,P-EVD,,,09,09 extractors; adjudicators,09; 10; 11,N,N,N,N,FW-12,DRAFT_PENDING_H4,prefixes reserved only (04.9-min); no schema in this step
recipe_base_v1 (ledgers/recipe_base),P-REC,quality_tier,SOURCE_RAW | SILVER_AUTO,07H-R,frozen builders,16-20; 29; 35; 36,N,N,recipe-level splits only through SPLITGRP-REC-,N,FW-12,EXISTS_FROZEN,TEXT_STATED; recipes are not chemistry truth (R-20)
recipe_base_v1 (ledgers/recipe_base),P-REC,quality_tier,GOLD_PENDING_INDEPENDENT_IAA,07H-R,frozen builders,16-20,N,N,"N for calibration: registry v1 allows it, contrary to SSOT invariant 14 (X9); additive v1.1 proposal pending",N,FW-12,EXISTS_FROZEN,"40 AI-drafted, human-reviewed, not independent (D-016, D-017)"
recipe identity (duplicate_group_id; recipe_family_id),P-REC,family_method,PROVISIONAL_STAR_V1 (calibrated=false),07I-R; 07I-C,07I tools,07I-S; 16-20,N,N,N,N,FW-12,EXISTS_PROVISIONAL,"candidates until calibrated; no destructive merge; exact copies coalesce, near-duplicates do not"
split_group_id,L-GOV,plane,EVD,08a; 08b,split builder,15; 27; 29-33,N,N,n/a (it is the split key),N,FW-11; FW-12; PQ-1,DRAFT_PENDING_H4,values SPLITGRP-EVD-######; the EVALUATION unit for evidence; lineage_root_id (LROOT-) is the COUNTING unit
split_group_id,L-GOV,plane,REC,07I-S,split builder,15 (recipe plane); 16-20; 35; 36,N,N,n/a (it is the split key),N,FW-11; FW-12; PQ-1,DRAFT_PENDING_H4,"values SPLITGRP-REC-######; recall-oriented (OP-SPLIT of 07I-C); distinct from duplicate_group_id, FAM- and split_lock_group_id"
```

Reading notes. (a) "Countable as independent evidence" means counted per `lineage_root_id` as "k independent lineages"; no row is ever counted as an independent study by itself. (b) The `OBS`/`DRV` `ESTIMATED_FROM_SUMMARY` exclusions and the `DOC` plane (P-SRC) are draft decisions flagged in `notes`. (c) The `EVD … IMPUTED` row states the plane because `registry/provenance_class_registry_v1.csv` ("IMPUTED … E6 or inherited … no as Gold truth unless declared and censor-aware") and SSOT §223.13 are not fully aligned (audit note); the row follows the stricter reading. (d) Rows for COND, KGE, IMAP, STATE / EVT, claims and the other audit classes are **out of scope** of the card and not listed.

## 4. How the rules map onto the draft schemas

| Rule | Where the drafts help | Where a semantic validator is still needed (Mac) |
|---|---|---|
| FW-09 | KIN: `evidence_tier` ∈ E1–E5; E1 / E2 / E4 need `HUMAN_VERIFIED`; DRV parents cannot be `SIM-` | partition membership by tier; provenance-class checks on export-v2 rows (e.g. `EXTERNAL_VERIFIED` on a DATABASE_AGGREGATE row) |
| FW-11 | `lineage.independence_resolution` and `assignment_status` present on KIN / AGG / DRV | split builder: disjointness across the four partitions, UNKNOWN → TRAIN only, plus the L-04b contamination screen and L-11b cross-task holdout |
| FW-12 | id patterns per prefix; node-type patterns on LIN | prefix scan over all ledgers and registries; mint refusal for unregistered prefixes |
| FW-15 | KIN / KINPT shape, clock tag, AUTHOR_REPORTED-only fits, `ENDPOINT_FROM_SERIES` needs a KIN parent | KIN-mandatory rule (≥ 2 distinct numeric τ, THR-04K-01 PROPOSED_PILOT; verified by the second extractor), no parameter with an AGG parent |
| PQ-1 | `split_group_id` pattern is evidence-only in every evidence draft | scan for mixed-prefix tables and cross-plane joins |

## 5. Open decisions for H4

1. Approve the six-plane vocabulary as the codes used by this registry (SSOT crosswalk remains PROPOSED_ONLY).
2. DOC in P-SRC (draft) or P-EVD.
3. Flagged exclusions: `ESTIMATED_FROM_SUMMARY` never a label / test value.
4. PQ-1 wording and name; `LROOT-` as an evidence-plane-only prefix (see `04_9_min_namespace_reservation.md`).
5. Whether the registry is created now (rows 1–26 as `DRAFT_PENDING_H4`) or only after approval of 04.1 / 04.3.
