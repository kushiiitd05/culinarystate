# Step 04.9-min — namespace reservation (no schemas)

**Status: DRAFT_PENDING_H4.** Written 2026-10-26 (D-027 / Plan v2 §7: contract and documentation only). Nothing is reserved yet: the CSV below is the proposed content of `registry/namespace_registry_v1.csv` (the 01.3-min artifact), which this step does **not** create. 04.9-min is a listed precondition of Step 08 (H4 approval required; CHG-04-6, CHG-01-2).

**Revision r1 (2026-10-26, still DRAFT_PENDING_H4):** two further prefixes that the reviewed 04.1 / 04.3 drafts need (`LABGRP-`, `MBSET-`) are proposed in §4 and re-scanned in §5; `PARAM-` is referenced (not proposed) by the LIN node patterns; the `EXP-` count is stated in ids and ledger lines.

What the Step 04 card defines for 04.9-min: **reserve the namespaces of 01.3-min (no schemas)** — `DOC-`, `SEXP-`, `SMP-`, `OBS-`, `LIN-`, `AGG-`, `DRV-`, `KIN-`, `KINPT-`, `XTR-`, `ADJ-`, `SPLITGRP-EVD-`, `SPLITGRP-REC-`; keep `MEAS-` = method and `EXP-` = ML run (never reused); record the `split_group_id` homonym rule. Pass-gate element: *namespace scan: 0 collisions*.

---

## 1. Reserved by the card (13 prefixes)

```csv
prefix,id_format,object_kind,plane,status,owner_step,planned_store,must_not_be_confused_with,draft_schema
DOC-,DOC-######,"concrete manifestation of a source actually read (file / page / record, sha256)",P-SRC,RESERVED_DRAFT_PENDING_H4,08a.1; 08b,ledgers/data/DOC.jsonl (08a),"SRC- (source), SNAP- (hashed retrieval)",registry/schemas/DOC.draft_v1_1.schema.json
SEXP-,SEXP-######,scientific experiment: one comparison set within a study,P-EVD,RESERVED_DRAFT_PENDING_H4,08a; 09,ledgers/data/SEXP.jsonl,EXP- (ML / benchmark run: stays),registry/schemas/SEXP.draft_v1_1.schema.json
SMP-,SMP-######,sample: food material at a state within one experiment,P-EVD,RESERVED_DRAFT_PENDING_H4,08a; 09,ledgers/data/SMP.jsonl,"SNAP-, SRC-",registry/schemas/SMP.draft_v1_1.schema.json
OBS-,OBS-######,observation: one property value of one sample by one method,P-EVD,RESERVED_DRAFT_PENDING_H4,08a; 09,ledgers/data/OBS.jsonl,MEAS- (analytical method: stays),registry/schemas/OBS.draft_v1_1.schema.json
LIN-,LIN-######,typed lineage / independence edge,P-EVD,RESERVED_DRAFT_PENDING_H4,08a; 08b,ledgers/data/LIN.jsonl,-,registry/schemas/LIN.draft_v1_1.schema.json
AGG-,AGG-######,aggregate evidence-level record (compiled value); default = export-v2 view key,P-EVD,RESERVED_DRAFT_PENDING_H4,08a; export builder,export v2 rows (separate ledger = human option),-,registry/schemas/AGG.draft_v1_1.schema.json
DRV-,DRV-######,derived evidence-level record (deterministic computation); default = export-v2 view key,P-EVD,RESERVED_DRAFT_PENDING_H4,08a.5; export builder,export v2 rows (separate ledger = human option),-,registry/schemas/DRV.draft_v1_1.schema.json
KIN-,KIN-######,kinetic / trajectory series header,P-EVD,RESERVED_DRAFT_PENDING_H4,04.3 -> 09,ledgers/data/KIN.jsonl (Step 09),KINETIC (D-024 names a never-created KINETIC ledger; confirm no KINETIC- prefix is intended),registry/schemas/KIN.draft_v1.schema.json
KINPT-,KINPT-######,one time point of a series,P-EVD,RESERVED_DRAFT_PENDING_H4,04.3 -> 09,ledgers/data/KINPT.jsonl (Step 09),-,registry/schemas/KINPT.draft_v1.schema.json
XTR-,XTR-######,extraction record (one extractor's reading of one field set),P-EVD,RESERVED_DRAFT_PENDING_H4,09,ledgers/data/XTR.jsonl (Step 09),-,none in this step (reservation only)
ADJ-,ADJ-######,adjudication record linking >= 2 XTR to the final OBS,P-EVD,RESERVED_DRAFT_PENDING_H4,09,ledgers/data/ADJ.jsonl (Step 09),-,none in this step (reservation only)
SPLITGRP-EVD-,SPLITGRP-EVD-######,"split group, evidence plane (evaluation unit)",L-GOV,RESERVED_DRAFT_PENDING_H4,08a; 08b,registry/independence_registry_v1.csv (08a),SPLITGRP-REC- (no cross-plane join),(value pattern pinned in every evidence draft)
SPLITGRP-REC-,SPLITGRP-REC-######,"split group, recipe plane (recall-oriented, OP-SPLIT of 07I-C)",L-GOV,RESERVED_DRAFT_PENDING_H4,07I-S,ledgers/recipe_identity/recipe_split_groups_v1.parquet (07I-S),SPLITGRP-EVD-; duplicate_group_id; FAM-; split_lock_group_id,(none; recipe plane)
```

Id format follows the ledger convention `PREFIX-` + 6 digits (`id_pattern` in `src/culinarystate/ledgers/common.py`); numbers are minted by the idempotent minter and **never reused** (`IdMinter`, `_ids.jsonl`). Reserving a prefix here does not add it to the Python registry `R`: until a prefix is in `R` the minter refuses it (`KeyError: unknown prefix`), which is the intended guard until H4 approval and until 08a ports the schemas (lineage contract D-6).

## 2. Kept meanings

```csv
prefix,kept_meaning,never_reused_for
MEAS-,analytical METHOD / platform (3 rows today),an observation or measurement value (that is OBS-)
EXP-,"ML / benchmark experiment card, run, result (7 ids; 8 ledger lines)",a scientific experiment (that is SEXP-)
```

## 3. Homonym rule for `split_group_id`

One column name, two planes, plane-qualified values `SPLITGRP-EVD-######` (evidence; R-03) and `SPLITGRP-REC-######` (recipe; R-08); no cross-plane join; a record carries at most one; a table mixing both prefixes fails the FW-12 scan (rule PQ-1, `04_6_min_data_plane_rules.md`). Needs Kush's ratification (ID scheme, H4). Also distinct from `duplicate_group_id` (exact copies), `FAM-` family (precision-oriented, provisional) and `split_lock_group_id` (Gold firewall v1).

## 4. Additional prefixes the 04.1 / 04.3 / 01.6 / 02.4 drafts need (NOT in the card)

```csv
prefix_or_name,id_format,object_kind,plane,status,reason_not_in_card,decision
LROOT-,LROOT-######,lineage root: connected component over MERGING edges (the statistical / counting unit),L-GOV (evidence plane only),PROPOSED_ADDITION_H4,lineage_root_id needs a stable value format; the card reserves no prefix for it,D-3 in lineage_contract_v1_1.md
CGRID-,CGRID-######,condition grid: the set of series that form one T x t design,P-EVD,PROPOSED_ADDITION_H4,`condition_grid_id` was moved to 04.1 / 04.3 (Step 07 card) without a prefix,A-6 in kinetic_trajectory_contract_v1.md
DFORM-,DFORM-###,"derivation formula id (registry/derivation_formula_registry_v1.csv, 08a.5) used by DRV.formula_id",L-REF,PROPOSED_ADDITION_H4,formula ids need a prefix distinct from MODEL- (ML card) and the audit's FMOD-; the name is a suggestion,D-3 in lineage_contract_v1_1.md
LABGRP-,LABGRP-######,"lab group: connected component over SAME_LAB_AS edges (recall-oriented, computed from DOC.authorship); the unit of independence of the kinetic plane (Steps 11 / 26 / 27 / 32)",L-GOV (evidence plane only),PROPOSED_ADDITION_H4,`lab_group_id` is a mandatory key on KIN and on DRV with a KIN parent (review B #4); no prefix exists for it,D-15 in lineage_contract_v1_1.md
MBSET-,MBSET-######,"mass-balance set: the series of one run (tissue, cooking medium, food mass / yield, medium volume) that close one mass balance",P-EVD,PROPOSED_ADDITION_H4,`KIN.mass_balance_set_id` (review B #13); no prefix exists for it,A-11 in kinetic_trajectory_contract_v1.md
THR-,THR-<step>-<nn>,"threshold row key in registry/preregistered_thresholds_v1.csv (registry key, not a ledger id)",L-GOV,PROPOSED_ADDITION_H4,used by this step's draft register,confirm or rename
NEG-,NEG-####,"row key in registry/negative_results_register_v1.csv (registry key, not a ledger id)",L-GOV,PROPOSED_ADDITION_H4,used by this step's draft register; `NR-` was rejected because it is the notation-rule registry prefix,confirm or rename
```

If H4 declines an addition, the corresponding draft field must be re-specified: `lineage_root_id` (LROOT-), `condition_grid_id` (CGRID-), `formula_id` (DFORM-), `lab_group_id` (LABGRP-), `mass_balance_set_id` (MBSET-), and the register row keys.

Referenced, not proposed: `PARAM-` (Step 24 fitted-parameter record: FORM / PARAM / VAL schemas, plan Step 24 card) appears in the `LIN.from_id` / `to_id` patterns of QUOTES_VALUES_FROM so that a compendium that re-reports k / Ea can be linked. Step 24 owns the prefix; this step does not reserve it, and a LIN row naming a PARAM id is meaningful only after Step 24 reserves it.

## 5. Collision scan (what was checked, 2026-10-26)

- Method: recursive grep for each reserved or proposed prefix (as an id-like token `PREFIX-…`) over `registry/`, `src/`, `tools/`, `tests/`, `ledgers/schemas/`, `docs/`, `DECISIONS.md`, `WORKLOG.md`, `STATUS.md`, `CLAUDE.md`, `reports/`, `annotation/`, `benchmark/` (md, csv, py, json, txt), run **before this step's drafts were written** and repeated excluding them; plus the minter state `ledgers/data/_ids.jsonl` (prefix counts only).
- Result: **0 id-like occurrences** of any reserved or proposed prefix outside the plan documents themselves (`docs/plan/*`, `registry/execution_spine_v2.csv`, `reports/master_plan/*`, where they are the reservation proposals). Non-id text hits: `DRV-merge` (a rule name in the audit, twice) and `DOC-attached` (a phrase in the plan). `_ids.jsonl` holds **no** minted id for any of them. The first candidate row key for the negative-results register, `NR-`, **did collide** with the notation-rule registry (`NR-001…`) and was renamed `NEG-` before the register was written; `T-` was replaced by `THR-` because `T-` is close to the lane-plan task ids.
- Revision r1 re-scan (2026-10-26, run before the r1 drafts were written; same method and directories): `LABGRP-` and `MBSET-` have **0** occurrences and no minted id in `_ids.jsonl`; `PARAM-` occurs only in plan / audit documents (`docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`, `reports/master_plan/*`), where it names the Step 24 PARAM record, and has no minted id.
- Not scanned: contents of `ledgers/data/*.jsonl` other than the minter state, the parquet ledgers (`pyarrow` absent here), Mac-only files and the Mac copy (D-026 exists only there). The card's gate "namespace scan 0 collisions" should be re-run on the Mac and on the merged tree.
- Observation, not investigated: `_ids.jsonl` has 18,157 minted EVD ids while the plan states 18,156 ids in the ledger (one id minted without a record, or a counting difference).

## 6. Baseline: existing ledger prefixes (collision reference)

37 ledger schemas exist; `minted_ids_in__ids.jsonl` is the count of ids the minter has issued (ids only; 0 = schema exists, no rows).

```csv
prefix,id_format,object_kind (ledgers/schemas title),minted_ids_in__ids.jsonl,status
ALIAS-,ALIAS-######,surface / regional / language alias,4116,EXISTING
ALLERGEN-,ALLERGEN-######,authoritative allergen record (AH3),8,EXISTING
ALLOC-,ALLOC-######,split / reserve / recombine allocation,0,EXISTING
API-,API-######,API endpoint / auth / rate limit / terms,0,EXISTING
CLM-,CLM-######,final claim with support,0,EXISTING
COND-,COND-######,full condition profile (W2),4414,EXISTING
DATASET-,DATASET-######,dataset release,5,EXISTING
ENTITY-,ENTITY-######,physical recipe/session entity (not the concept),0,EXISTING
EVD-,EVD-######,state-change evidence atom (W4),18157,EXISTING
EVT-,EVT-######,atomic recipe/session event,0,EXISTING
EXP-,EXP-######,experiment card / run / result,7,EXISTING
GATE-,GATE-######,promotion / stop decision,0,EXISTING
GRAPH-,GRAPH-######,recipe/session event-state graph,0,EXISTING
IMAP-,IMAP-######,ingredient <-> molecule evidence mapping,30294,EXISTING
ING-,ING-######,canonical food / ingredient concept,2110,EXISTING
INST-,INST-######,instruction semantic record,0,EXISTING
KGE-,KGE-######,"typed concept-level edge with support, association and confidence",48181,EXISTING
MEAS-,MEAS-######,measurement method / platform,3,EXISTING
MODEL-,MODEL-######,trained / released model,0,EXISTING
MOL-,MOL-######,canonical molecule,1726,EXISTING
POR-,POR-######,ingredient/form/locale portion or density evidence,0,EXISTING
PROC-,PROC-######,canonical process / action family,156,EXISTING
QNT-,QNT-######,parsed quantity expression,0,EXISTING
REC-,REC-######,recipe (immutable raw),89565,EXISTING
REF-,REF-######,coreference / reference relation,0,EXISTING
RQ-,RQ-######,research question,0,EXISTING
RS-,RS-######,research spawn,0,EXISTING
RXN-,RXN-######,reaction / transformation relation (partial allowed),0,EXISTING
SNAP-,SNAP-######,exact source snapshot,346,EXISTING
SPLIT-,SPLIT-######,split / fold registry,0,EXISTING
SRC-,SRC-######,source / dataset / paper / API identity,488,EXISTING
STATE-,STATE-######,entity version / state (append-only),0,EXISTING
STUDY-,STUDY-######,study design / experiment family,125,EXISTING
SVAR-,SVAR-######,state variable registry (W3),224,EXISTING
TOOL-,TOOL-######,utensil / tool / material,119,EXISTING
UNIT-,UNIT-######,unit concept,74,EXISTING
WARN-,WARN-######,evidence-backed warning rule,0,EXISTING
```

Existing registry-key and other id families (not ledger ids, but part of the same address space):

```csv
prefix,found_in,object_kind
AM-,registry/measurement_method_registry_v1.csv,measurement method registry key
CS-,registry/censoring_registry_v1.csv,censoring kind
CV-,registry/condition_variable_registry_v1.csv,condition variable
DM-,registry/source_dialect_mapping_registry_v1.csv,source dialect mapping
DS-,registry/data_source_acquisition_manifest.csv; source_claim_capability_matrix.csv,data source (64)
G14- / G15- / RQ16-,registry/ssot15_state_experiment_map.csv,SSOT gate and research-question ids
HT-,registry/heat_transfer_mode_registry_v1.csv,heat-transfer mode
HV-,registry/human_verification_queue.csv,human-verification task
LC-,registry/recipe_location_cues_v1.csv,recipe location cue
MB-,registry/measurement_basis_registry_v1.csv,measurement basis
ML-,registry/measurement_location_registry_v1.csv,temperature measurement location
NR-,registry/notation_rule_registry_v1.csv,notation rule
QF-,registry/quantity_form_registry_v1.csv,quantity form
RT-,registry/retention_type_registry_v1.csv,retention type
SIM-,registry/ssot15_similarity_registry.csv,similarity type SIM-01..21 (MP-1 s.1.G also lists SIM- as a simulation id: the FW-12 collision example)
SX-,registry/ssot15_state_experiment_map.csv; plan text,master-plan state experiment ids
VO-,registry/value_origin_registry_v1.csv,value origin
VT-,registry/value_type_registry_v1.csv,condition value type
FAM-,recipe identity / REC family_id,recipe family
MTX- / PST-,exports/evd/*_table_v1.csv; evd_export_v1.schema.json,hash ids of normalised matrix / prior-state descriptors (12 hex)
```

## 7. Open decisions for H4

1. Reserve the 13 prefixes (and confirm the id format `PREFIX-######`).
2. Accept or decline `LROOT-`, `CGRID-`, `DFORM-`, `LABGRP-`, `MBSET-`, `THR-`, `NEG-` (section 4); note that `PARAM-` is referenced, not proposed.
3. Ratify the `split_group_id` homonym rule (section 3).
4. Confirm that no `KINETIC-` prefix is intended (D-024 mentions a never-created KINETIC ledger).
5. Whether AGG-/DRV- are minted for real (separate ledgers) or only as export-view keys (lineage contract D-2).
6. Other audit namespace fixes (`SIMTYPE-`, `FMOD-`, `RCLM-`, `SIMRUN-` for the SIM-/MODEL-/CLM- collisions) are **not adopted** by the plan and not touched here (Phase E/F authors).
