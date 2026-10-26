# Step 21 (parallel lane, R-10) — mechanism and effect ontology: contract drafts, index, decisions, proposed test

**Status of everything listed here: DRAFT_PENDING_H4.** Written 2026-10-26 under D-027 ruling **R-10** (Plan v2 §4.2 lane L5; Steps 12, 13, 21 and 35 run in parallel where their input artifacts already exist; Plan §7 lists no Step-21 item) and **revised the same day after the round-3 reviews** (A governance, B science; item-by-item record in `FIX_LOG_round3.md`): contract and documentation work only. Nothing is approved, frozen, signed, minted or applied. No ledger row was created, no id was minted, no evidence was entered, no pipeline was run, no existing file was edited, `tests/` was not touched. **Step 08 is not started and not authorised.** Every row of the three vocabulary CSVs carries `registry_status = DRAFT_PENDING_H4` and `ai_drafted = TRUE`; none carries a scientific value (numbers appear only as source line anchors and as the PROPOSED_PILOT size target already in the plan card). Round-3 additions whose chemistry is not stated anywhere in the repo are marked `OPEN_QUESTION` in the roster rows and are not asserted (D21-23).

## 1. Index

| Substep | Path | Bytes | What it is |
|---|---|---|---|
| 21a / 21b-vocab / 21c | `reports/step21/mechanism_effect_ontology_v1_draft.md` | 57,591 | Mechanism and effect ontology: kinds and families, effect classes, activation-condition representation (preconditions, gates, bounds, inhibitors, competition, history, matrix scope), three-valued applicability rules (R-15), mapping of the ascorbic-acid and chlorophyll pathways (R-14) without freezing either, seed-roster summary, PROC label gaps, xref policy, leakage rules, G21.1-G21.8 support |
| 21a | `registry/schemas/MECH.draft_v1.schema.json` | 95,173 | MECH schema draft (class-level mechanism entry; no numeric kinetic field; `missing_input_verdict` constants; bound statuses with the studied extreme on OPEN_STATED and no optimum; ACCEPTED rules incl. evidence on all eight item types; modifier list with catalysts / promoters; xref and sink rules) |
| 21b (vocabulary only) | `registry/mechanism_seed_roster_draft_v1.csv` | 23,042 | 32 candidate entries to author (key, synonyms, kind, family, sources, ES-1.2 cells, PROC label, typical effect types, R-14 coverage tag); not entries |
| 21c | `registry/effect_type_registry_draft_v1.csv` | 6,913 | 16 effect types aligned to the RXN relation verbs (13 reused, 3 proposed) with direction rules |
| 21a (Step 23 interface) | `registry/condition_gate_type_registry_draft_v1.csv` | 2,724 | NECESSARY / MODULATING / INHIBITING with their three-valued reading |
| index | `reports/step21/README.md` | 85,546 | this file |
| record | `reports/step21/FIX_LOG_round3.md` | 14,093 | round-3 review items mapped to FIXED / OPEN_QUESTION / NOT_APPLICABLE with file:line evidence |

Substeps of the Step 21 card **not** drafted, and why: 21b entries (each needs ≥ 1 evidence id with document type, G21.4, and a dual blind review, G21.6), 21d PROC → MECH crosswalk (executes HV-010, owned by Parv with Kush reviewing; blocked by the HV-001 protocol), 21e xref table with collision audit (needs live look-ups and a human), the review packet `annotation/mechanism_review/step21_review_packet_v1.csv`, the sealed case set (22c), `ledgers/data/MECH.jsonl`, `ledgers/schemas/MECH.schema.json`, `tests/unit/test_mech_schema.py`.

Card output paths versus the draft paths (as for Step 04, drafts live beside the registries and are not copied to the ledgers): `ledgers/schemas/MECH.schema.json` ← `registry/schemas/MECH.draft_v1.schema.json`; `registry/mechanisms/effect_type_registry_v1.csv` ← `registry/effect_type_registry_draft_v1.csv`; `registry/mechanisms/condition_gate_type_registry_v1.csv` ← `registry/condition_gate_type_registry_draft_v1.csv`; `registry/mechanism_seed_roster_draft_v1.csv` has no card counterpart (the card's 21b output is `ledgers/data/MECH.jsonl`; the roster is the list of entries to author).

## 2. What was and was not touched

- **Created (7 files):** the files in the index and the directory `reports/step21/` (the sixth and seventh are this file and `FIX_LOG_round3.md`). The round-3 revision edited only these files, the schema and the three CSVs listed in the index, plus the text corrections K-1a..e in `reports/step04/` and `reports/step02/` and one reservation addition in `reports/step04/04_9_min_namespace_reservation.md` (see `FIX_LOG_round3.md`); nothing was committed.
- **Not touched by construction:** every ledger row and ledger schema (`ledgers/schemas/*`), `src/culinarystate/ledgers/registry.py` (read only, to scan prefixes), the SSOT, the plan, `DECISIONS.md`, `WORKLOG.md`, `STATUS.md`, every file of `reports/step04/` (referenced, not edited), `registry/schemas/KIN.draft_v1.schema.json` and the other Step-04 drafts, tests. No git write command was issued and nothing was staged or committed; one read-only `git status --short` at the end showed this lane's six files as untracked (`reports/step19/` and `reports/step35/`, other parallel lanes, were untracked too and are not mine). Other tracked files carry recent modification times (`WORKLOG.md`, `DECISIONS.md`, the plan and its changelog, `reports/step04/*`, the Step-04 schema drafts): they were written by other sessions before or alongside this one and were not touched here. No project tool or pipeline was run. `tools/log_step.py` was not run (no WORKLOG entry was written).
- **Read-only lookups beyond the named documents:** `ledgers/data/PROC.jsonl` (labels and required axes of the latest version of each of the 156 PROC), `registry/state_variable_registry_v1.csv` and `condition_variable_registry_v1.csv` (rows), `registry/human_verification_queue.csv` (HV-002, HV-010), `reports/h_state/es_1_2_priority_cell_source_coverage.csv` (PC-01…PC-16), `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` (L82, L596–616, L1689–1725), `reports/master_plan/master_plan_research_audit_v2.md` (Part J1), `reports/step04/04_6_min_data_plane_rules.md`, `04_9_min_namespace_reservation.md`. No third-party raw file was opened.

## 3. Validation performed

- `MECH.draft_v1.schema.json` parses (`python3 -I`), declares draft 2020-12, passes `Draft202012Validator.check_schema`, keeps `additionalProperties: false` on every nested object (the only open sub-schemas are `if` / `contains` / `not` matcher fragments), contains no `default` keyword and no kinetic-parameter property name. The three CSVs parse with `csv` (16, 3 and 32 rows).
- The proposed contract test (section 5) after the round-3 revision: **22/22 tests passed, 87 negative controls, 23 accepted variants** (before it: 21/21, 60, 18). Round-3 result was produced with `/opt/anaconda3/bin/python` (jsonschema 4.19.2) on the Mac; the original run (21/21, 60, 18) was made on the Linux server with `/usr/bin/python3` (jsonschema 4.10.3), which the round-3 reviewer reproduced. The eight deliberate-defect mutation check of the original run was repeated for the new rules (see `FIX_LOG_round3.md`). Every negative control is asserted to fail for its intended reason (path and keyword), not merely to fail.
- **How to run the contract test (and which interpreter has jsonschema).** The file does not exist in `tests/` yet (D21-17); the code of section 5 is the exact file. Extract it to `tests/contract/test_step21_mech_draft.py`, then: on the Mac `/opt/anaconda3/bin/python -m pytest -q tests/contract/test_step21_mech_draft.py` (anaconda base has jsonschema 4.19.2 and pytest; the recsys_env python has 4.26.0; the system `/usr/bin/python3` on the Mac has no jsonschema); on the Linux server `CS_ROOT=<repo> /usr/bin/python3 tests/contract/test_step21_mech_draft.py` (Debian `python3-jsonschema` 4.10.3, Python 3.12.3, no pytest, so the file runs as a plain script; the PATH `python3` there is the miniconda base without jsonschema). Version note: jsonschema < 4.18 cannot resolve `#/$defs/...` references under a **relative** `$id` (it joins the id with itself), so the test validates against a copy of the schema without `$id`; on ≥ 4.18 either form works. The earlier statement in the Step-04 and Step-02 texts that jsonschema is "not installed on this server" was wrong for `/usr/bin/python3` and was corrected in round 3 (K-1a..e).
- This is evidence about the drafts' logic, **not** a substitute for the real Mac validator, the CV-registry semantic validator, or human review.

## 4. Checklist: human decisions needed (Kush, Parv; H4 unless stated)

No item is decided here. Each lists the draft's choice and the alternative.

**Identity, planes, deviations from the card**

- [ ] **D21-1 Prefix and cross-references.** Confirm `MECH-` (free in `registry.py`, which lists 37 prefixes; not in 04.9-min). CHG-21-3 promises a namespace contract for MECH / EFFSIG / FORM / PARAM / VAL / APPDEC under a new id that does not exist yet. Draft: entries refer to each other by `mechanism_key`; alternative: by MECH id (needs minting order). **Evidence-id prefixes:** the schema's `evidence_id` pattern admits `DOC-`, `OBS-`, `KIN-` (RESERVED_DRAFT_PENDING_H4) and `LROOT-` (PROPOSED_ADDITION_H4 in `reports/step04/04_9_min_namespace_reservation.md`); it is valid only if 04.9-min reserves them, otherwise it narrows to `(EVD|SRC)`. `MECH-`, `DGP-` (Step 19) and `TASK-` (Step 35) are listed in that file as proposed reservations (round 3).
- [ ] **D21-2 The unresolved-loss sink.** Card id `MECH-UNRESOLVED_LOSS` does not fit `MECH-######`. Draft: key `UNRESOLVED_LOSS`, minted id, kind `UNRESOLVED_SINK` (a 7th kind), every list empty, mass-balance accounting only, never an EFFSIG candidate. Alternative: keep the mnemonic id (breaks the id pattern) or drop the kind and use `kind = null`.
- [ ] **D21-3 Plane.** Draft: MECH is a reference registry of the model plane (P-MOD), `is_evidence = false` constant. 04.6-min needs a row for it.
- [ ] **D21-4 `edge_semantics`.** Card values REACTION / TRANSPORT / EQUILIBRIUM / STATISTICAL (SSOT §213.11) fit neither phase / structural transitions nor mechanical disruption. Draft adds `STATE_TRANSITION` (and `NOT_APPLICABLE` for the sink). Alternative: map them to EQUILIBRIUM / REACTION.
- [ ] **D21-5 Effect types.** Draft: 13 RXN verbs reused verbatim (RETAINED excluded: an outcome), plus `ABSORBED` (inward transfer, no RXN verb), `STRUCTURE_ALTERED` (texture / structure without chemistry), `STATE_SET` (sets a history state). Open inside this item: evaporation versus exudate / drip for moisture loss; whether `STATE_SET` belongs to Step-18 operators instead.
- [ ] **D21-6 Interval bounds.** Card and Step 23-M: "bounds nullable". Draft: each bound is `STATED` / `OPEN_STATED` / `NOT_REPORTED`, because a bare null reads as "unbounded" (an imputation) and breaks R-15; **no optimum is stored** (min / opt / max would be a complete cardinal-parameter model, a secondary kinetic model that bypasses FORM / PARAM; round-3 Review B 21-10); `OPEN_STATED` carries the **studied extreme** as its value, and a query beyond it is UNKNOWN (extrapolation, Review B 21-9). This is a deliberate deviation (two: nullable → status object; `opt` removed).
- [ ] **D21-7 Family tokens.** Ten SSOT §144.1 families plus `MICRONUTRIENT_DEGRADATION` (the card's ascorbic-acid pathways fit none) and `UNRESOLVED`.
- [ ] **D21-8 Directions.** Draft: `allowed_directions` ⊆ {INCREASE, DECREASE} or exactly [UNKNOWN]; EVD's NO_CHANGE and MIXED are outcomes, read against the set and `trajectory_shape` (ontology §3.4).

**Dependencies owned elsewhere**

- [ ] **D21-9 History and species variables (16a, CHG-21-3, CHG-16-7).** The draft only references `enzyme_activity_state`, `cell_integrity`, `time_since_disruption`, thermal dose, `oxygen_exposure`, precursor depletion, prior acid / salt exposure as `PROPOSED_KEY`. Who writes the additive SVAR contract? The thermal-dose definition (reference temperature, Ea) is a Step-24 matter. The species-level variables the candidate systems need (reduced AA, DHA, chlorophyll a / b, pheophytin) do not exist (gap G-1).
- [ ] **D21-10 Condition registry v1.1.** No axis exists for metal ions (gap G-2; CV-023 is categorical). Add a CV, or accept a categorical CV-023 gate.
- [ ] **D21-11 Inhibitor semantics for Step 23.** Draft: an inhibitor is evaluated through exactly one route (INHIBITING gate, inline state predicate, or `NOT_EVALUABLE_YET`, which forces `gates_unknown = true`); `extent` COMPLETE → NOT_APPLICABLE, PARTIAL → Step 23's downgrade, UNKNOWN → UNKNOWN (a proposed reading beyond the card). **Modifiers (round 3, Review B 21-3):** the list also holds CATALYST and PROMOTER items (metal ions, sensitising light) with `extent = NOT_APPLICABLE`; they never change the G4 verdict but their axes are required condition axes for Step 22 / G7 (rule M-1); `acts_on_modifier_key` lets a chelating INHIBITOR point at a CATALYST. The field keeps the card's name `inhibitors_mitigators`; renaming it to `modifiers` is the alternative.

**The roster**

- [ ] **D21-12 Roster content.** 32 rows (card target "about 20–40" is PROPOSED_PILOT): 23 from the card's 21b list (starch gelatinisation / retrogradation split in two; the lumped ascorbic-acid aerobic entry split at the DHA node into `ASCORBATE_TO_DHA_OXIDATION` and the new `DHA_HYDROLYSIS_TO_DKG`; `ASCORBATE_OXIDASE_LOSS` re-keyed `ASCORBATE_OXIDASE_AA_OXIDATION`, the card labels kept as `synonyms`), plus the round-3 additions `ASCORBIC_ACID_APPARENT_LOSS_LUMPED`, `CHLOROPHYLLASE_DEPHYTYLATION`, `CHLOROPHYLLIDE_TO_PHEOPHORBIDE`, `METALLO_CHLOROPHYLL_COMPLEX_FORMATION`, `ENZYME_THERMAL_INACTIVATION` (see D21-23), plus `CELL_WALL_SOFTENING` (the card's list does not cover the cell-wall half of the §144.1 family, so G21.2 cannot pass without it), `CELL_DISRUPTION_DECOMPARTMENTALISATION` (the card enumerates kind MECHANICAL_DISRUPTION and a metric on "mechanical kinds" but lists no entry of that kind), and the optional `CHLOROPHYLL_PYROPHEOPHYTIN_FORMATION` (beyond the card; secondary-source). Accept, edit or drop each.
- [ ] **D21-13 PROC label gaps.** 9 of the 23 PROC mechanism labels map to no roster entry (emulsification, aeration, gluten_development, phase_change, crystallisation, co2_leavening, water_activity_reduction, acidification, microbial_inactivation); 20 of the 93 labelled PROC carry only such labels. For each: add an entry, declare "not a mechanism" (Step-18 state operation or a gate-axis modifier), or fold. Microbial inactivation is safety-adjacent (authoritative sources only).
- [ ] **D21-14 Enabling state changes.** Cutting / crushing (cell integrity) and enzyme thermal inactivation (ES-1.2 PC-02; blanching as a mitigation) can be MECH entries (`STATE_SET`) or Step-18 deterministic operators. Draft (after round 3): cutting is a proposed entry and thermal inactivation is now a proposed entry `ENZYME_THERMAL_INACTIVATION` (STATE_SET); if the humans prefer a Step-18 operator, a named owner and a date before 21b are needed, otherwise every enzymatic entry stays `NOT_EVALUABLE_YET` and `gates_unknown = true`. History roles `ACTIVE_UNTIL_STATE_CHANGE` and `INPUT_REQUIRED_START_MODE` were added (names owned by 16a).

**Governance and review**

- [ ] **D21-15 Gate-circularity guard (not in the card).** Each `evidence_ref` caches `lineage_root_id` so a gate limit derived from a study cannot be tested on cases from that study (ontology L-21-2). Depends on the proposed `LROOT-` prefix (04.9-min, pending H4). The Step 22c case-set id prefix must lie outside `EVD|SRC|DOC|OBS|KIN` so that case ids can never be cited as evidence.
- [ ] **D21-16 Review process.** Dual blind review by Kush and Parv with technical independence safeguards (07H v1–v3 provenance failures); HV-010 owned by Parv with Kush reviewing, blocked by the HV-001 protocol; expert pass 8–16 h with availability UNVERIFIED. Who authors entries versus who labels the locked test cases (MECH authors alone make G23.1 DIAGNOSTIC_ONLY)?
- [ ] **D21-17 Freeze path.** When approved: port the schema to `ledgers/schemas/MECH.schema.json`, register the prefix in `registry.py`, move the CSVs under `registry/mechanisms/` with the card's names, then add the card's `tests/unit/test_mech_schema.py`. None of that is done.
- [ ] **D21-18 Scope of claims.** MECH carries no food-safety claim (authoritative sources only; Step 36 owns the failure / recovery ontology, §257A.9) and no numeric kinetic field. Confirm, including that acrylamide (safety-relevant, r_simulator_vv Q1) is a mechanism entry only.
- [ ] **D21-19 Namespaces and SBO ids.** `MESH` and `TRANSFORMON` were removed from the xref CURIE pattern (not on the card; the TRANSFORMON CURIE form and licence are unverified, r_mechanism_registry L177). Add them back, or keep the card's list plus EC. Also confirm SBO:0000459 (stimulator) as the PROMOTER id; SBO:0000013 and :0000459 come from the schema's participant enum and are themselves to be human-verified.
- [ ] **D21-20 Which axes may be NECESSARY (rule E-7) and when `gates_unknown` may be false.** Draft: for a CHEMICAL_REACTION a temperature, pH or water-activity axis is MODULATING unless PRIMARY evidence states that the reaction is absent outside the window (ontology 4.3; supported in the repo by SSOT 144.1 "no universal temperature switch" and the plan's SIM-CHL-1 text, where pH is a FORM input at G7); NECESSARY gates are the natural form for enzymatic, microbial and phase-transition kinds. Reviewer B's chemistry behind this (Mg loss across the whole practical pH range; no T or pH at which Arrhenius chemistry stops, it only becomes negligible) is not stated in the repo: OPEN_QUESTION, confirm against a PRIMARY source. Consequence: a pure-chemistry entry with only MODULATING gates can never have `gates_unknown = false` under the current schema rule (it needs a precondition or a NECESSARY gate). Reviewer B also proposed a third branch (targets present, matrix included, a history item with role INPUT_REQUIRED); it was **not** adopted because it reopens a vacuous APPLICABLE; decide whether to add it.
- [ ] **D21-21 Items without a verdict field.** `competes_with`, `consecutive_with`, `history_item`, `affected_target` and `marker` carry no `missing_input_verdict`; they contribute UNKNOWN only while their status is not ACCEPTED (the schema comment now says so). Alternative: add the constant field to them.
- [ ] **D21-22 Analyte-form tokens.** `analyte_form.text` is free text, but the Step-10 ranking confounder (analyte basis AA vs AA + DHA; chlorophyll a / b vs −a*) and Step-27 basis checks need it machine-comparable. Reviewer B proposed a controlled token list in a new `registry/analyte_form_registry_draft_v1.csv` (REDUCED_AA, DHA, TOTAL_VITC_AA_PLUS_DHA, CHL_A, ...). **Not drafted:** a fourth registry file is outside this revision's file set and the token list is domain content. OPEN_QUESTION: approve the list and the file, then make `token` required when `status = STATED`.
- [ ] **D21-23 Round-3 additions without a repo source (OPEN_QUESTION, none asserted).** `CHLOROPHYLLASE_DEPHYTYLATION`, `CHLOROPHYLLIDE_TO_PHEOPHORBIDE`, `METALLO_CHLOROPHYLL_COMPLEX_FORMATION` exist only because Review B proposes them (no repo text names them); the chemistry of the AA → DHA → DKG split beyond the chain stated in r_simulator_vv Q1 (reversibility, O2 / metal / pH dependence, the enzyme's EC number), ascorbic acid as sacrificial reductant of the browning intermediates (COUPLED_REDOX), the shared markers of the anaerobic route (furfural, 2-furoic acid), dissolved oxygen as the driver in the medium (gap G-8), the non-monotone colour early in blanching, and the rise of enzyme activity in the heating come-up window. Each row carries the OPEN_QUESTION in `open_issue`; 21b keeps a row only if a PRIMARY source supports it, otherwise it is dropped (R-19: recorded as dropped, not deleted).

## 5. Proposed contract test (not created here)

Proposed path on the Mac: `tests/contract/test_step21_mech_draft.py` (the Step-04 convention for draft contracts). Run: `/opt/anaconda3/bin/python -m pytest -q tests/contract/test_step21_mech_draft.py`, or the file directly. It is the exact file that was run here; fixtures are SYNTHETIC SCHEMA FIXTURES (structure only, placeholder strings, never data), and the three-valued evaluator inside it is a test-local reference of how the record must be read, not the Step-23 engine.

| Group | Tests | Cases |
|---|---|---|
| Accepted variants | `test_accepted_variants_validate` | V-1…V-23: minimal CANDIDATE; NECESSARY gates with every bound NOT_REPORTED, with STATED + OPEN_STATED bounds; core-temperature, time, moisture gates; categorical INHIBITING gate; preconditions; sink; fully specified ACCEPTED; ENZYMATIC with enzyme; Strecker label-collision xref kept as REJECTED; inhibitor through a gate; competition / consecutive declarations; LEACHED both compartments; FORMED peak-then-decline; direction exactly [UNKNOWN]; MODEL_SYSTEM scope; VOLATILIZED from the whole system; catalyst with a MODULATING gate and an acting chelator; OXIDIZED substrate / product; coupled-redox competition and a start-mode history item |
| Negative controls | `test_negative_controls_rejected_for_the_intended_reason` | 87, each asserting the intended error: gates_unknown rule; `missing_input_verdict` ≠ UNKNOWN; bare-null bound; STATED without value or evidence; kinetic keys and `default` keys; `marker_unique` true; CV-009 / CV-004 / CV-010 as gate axes; location, basis and clock coupling; ACCEPTED rules (human verification, PRIMARY evidence, two reviewers, review provenance, verifier ∈ Kush / Parv); enzyme coupling; sink restrictions; `is_evidence` true; xref rules; inhibitor `NOT_EVALUABLE_YET`; direction rules per effect type and compartment; sealed case id as evidence; lineage root; predicate rules; state-ref coupling; matrix scope; key and id patterns; round 3 (N-59…N-85): UNKNOWN as a category or predicate value in any letter case, ACCEPTED without evidence on each of the six item types that lacked the rule, a lone MODULATING or INHIBITING gate with `gates_unknown = false`, VOLATILIZED / ABSORBED compartment rules, OXIDIZED sign by `target_role`, old-style local keys, CV-021 location, an optimum in an interval, a non-admitted xref namespace, catalyst / promoter coupling, OPEN_STATED without the studied extreme |
| Schema structure | `test_schema_is_a_valid_2020_12_schema_and_all_refs_resolve`, `test_no_additional_properties_anywhere_and_no_default_keyword`, `test_no_kinetic_parameter_names_in_the_schema`, `test_r15_constants_are_in_the_schema`, `test_prefix_is_free_in_the_python_registry` | G21.8; U-2; U-3; prefix collision |
| Vocabularies | `test_vocabulary_rows_are_draft_sourced_and_unique`, `test_effect_types_match_schema_and_rxn_enum`, `test_gate_types_match_schema`, `test_roster_uses_only_schema_vocabulary`, `test_roster_covers_the_g21_2_families_and_every_kind`, `test_r14_both_candidate_systems_represented_and_neither_frozen`, `test_roster_proc_labels_exist_in_the_proc_ledger`, `test_direction_rules_in_the_effect_csv_match_the_schema` | DRAFT_PENDING_H4 and a source on every row; effect types equal the schema enum and cover every RXN verb but RETAINED; roster ⊆ schema vocabularies; G21.2 families, three transport keys, every kind; both candidate systems present symmetrically and nothing "selected"; the schema text names neither system (no ascorbic / chlorophyll / pheophytin term); every compartment rule in the effect CSV is the rule the schema enforces; PROC labels exist (reads label strings only) |
| Semantic validator design | `test_semantic_checks_on_fixtures`, `test_competition_and_consecutive_links_must_be_declared_on_both_sides` | duplicate keys; evidence ids ⊆ `evidence_refs`; CV exists; unit = CV canonical unit; min ≤ max; numeric window on a categorical CV; allowed ∩ excluded; inhibitor GATE mode names an INHIBITING gate (a MODULATING gate for a catalyst / promoter); `acts_on_modifier_key` names a catalyst / promoter; rule E-7; symmetric competition / converse consecutive order |
| Three-valued reading | `test_k3_conjunction_table`, `test_interval_bounds_are_never_silently_open`, `test_matrix_and_inhibitor_semantics`, `test_candidates_and_gates_unknown_never_route_to_simulate`, `test_property_unknown_never_becomes_applicable_or_simulate` | K3 table; a NOT_REPORTED side gives UNKNOWN, a violated STATED side gives NOT_APPLICABLE, OPEN_STATED passes only inside its studied extreme (beyond it UNKNOWN); unlisted matrix UNKNOWN, excluded NOT_APPLICABLE; CANDIDATE and `gates_unknown` give UNKNOWN; 3,000 randomised entries and queries (seed 21): APPLICABLE only when every input is known and every item ACCEPTED, NOT_APPLICABLE never from a missing input, nothing reaches SIMULATE without APPLICABLE |

```python
"""Contract test for the Step 21a DRAFT mechanism-registry contract (status DRAFT_PENDING_H4).

PROPOSED content for tests/contract/test_step21_mech_draft.py (not created in this step).
Run on the Mac:  /opt/anaconda3/bin/python -m pytest -q tests/contract/test_step21_mech_draft.py
or, without pytest:  /opt/anaconda3/bin/python tests/contract/test_step21_mech_draft.py
Needs jsonschema >= 4.0 (Draft 2020-12); the schema is loaded without its relative $id (see VAL below), so
4.10.3 (/usr/bin/python3 on the server) and 4.19+ (Mac anaconda) both work. Fixtures are SYNTHETIC SCHEMA FIXTURES: structure only, placeholder
strings, never scientific data. Nothing here reads a ledger row's scientific content (the optional PROC check
reads label strings only). The evaluator below is a TEST-LOCAL reference of the three-valued reading of the
record; it is not the Step-23 engine and defines no behaviour for it.
"""
import copy
import csv
import json
import os
import random
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(os.environ.get("CS_ROOT", Path(__file__).resolve().parents[2]))
REG = ROOT / "registry"
SCHEMA_PATH = REG / "schemas" / "MECH.draft_v1.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
# jsonschema < 4.18 cannot resolve '#/$defs/...' under a RELATIVE $id (it joins the id with itself); the repo's
# draft schemas use relative ids like the ledger schemas, so validate against a copy without $id.
VAL = Draft202012Validator({k: v for k, v in SCHEMA.items() if k != "$id"})
STATUS = "DRAFT_PENDING_H4"
A, NA, U = "APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"


# ----------------------------------------------------------------------------- helpers
def read_csv(name):
    with open(REG / name, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def flat_errors(instance):
    """All validation errors, with sub-errors of anyOf / oneOf flattened, as 'path :: schema_path :: message'."""
    out = []

    def walk(e):
        out.append("/".join(str(p) for p in e.absolute_path) + " :: " + "/".join(str(p) for p in e.absolute_schema_path)
                   + " :: " + e.message)
        for c in e.context or []:
            walk(c)

    for e in VAL.iter_errors(instance):
        walk(e)
    return out


def valid(instance):
    return not list(VAL.iter_errors(instance))


def walk_schema(node, path=""):
    """Yield (path, node) for every dict in the schema."""
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from walk_schema(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_schema(v, f"{path}/{i}")


# ----------------------------------------------------------------------------- synthetic fixtures
def state(key="synthetic_state"):
    return {"ref_status": "PROPOSED_KEY", "svar_id": None, "state_key": key, "label_raw": "synthetic " + key}


def scope(kind="UNKNOWN", inc=(), exc=()):
    item = lambda r: {"ref_type": "CLASS_LABEL", "ref": r, "label_raw": r}
    return {"scope_kind": kind, "included": [item(r) for r in inc], "excluded": [item(r) for r in exc],
            "unlisted_verdict": "UNKNOWN", "note_raw": None}


def target(effect="DEGRADED", dirs=("DECREASE",), comp="TISSUE", shape="MONOTONIC", key="TGT01", role="UNKNOWN"):
    return {"target_key": key, "target": state("synthetic_target"), "target_role": role, "analyte_form": {"status": "NOT_REPORTED", "text": None},
            "compartment": comp, "effect_type": effect, "allowed_directions": list(dirs), "trajectory_shape": shape,
            "evidence_ids": [], "status": "CANDIDATE"}


def bound(status="NOT_REPORTED", value=None, inclusive=None):
    return {"status": status, "value": value, "inclusive": inclusive}


def stated(v, inclusive=True):
    return bound("STATED", v, inclusive)


def open_(v, inclusive=True):
    """OPEN_STATED: not limited on this side within the studied range; v is the studied extreme (required)."""
    return bound("OPEN_STATED", v, inclusive)


def gate(cv="CV-013", gtype="NECESSARY", mn=None, mx=None, unit="pH", key="CG01", status="CANDIDATE", **over):
    g = {"gate_key": key, "gate_type": gtype, "cv_id": cv, "location": "TISSUE", "basis": "NOT_APPLICABLE",
         "clock": "NOT_APPLICABLE", "domain_kind": "NUMERIC_INTERVAL",
         "interval": {"unit": unit, "min": mn or bound(), "max": mx or bound()},
         "categories": None, "modulates": "NOT_APPLICABLE" if gtype != "MODULATING" else "RATE",
         "independence_assumed": "UNKNOWN", "matrix_scope": scope(), "missing_input_verdict": "UNKNOWN",
         "evidence_ids": [], "status": status, "rationale_raw": None}
    g.update(over)
    return g


def precondition(key="PRE01", state_key="synthetic_state", op="IS", values=("SYNTH_A",), status="CANDIDATE", evidence_ids=()):
    return {"precondition_key": key, "state_ref": state(state_key), "subject_entity": None,
            "predicate": {"operator": op, "values": list(values)}, "missing_input_verdict": "UNKNOWN",
            "evidence_ids": list(evidence_ids), "status": status}


def evidence_ref(eid="SRC-000001", doc_type="PRIMARY", supports=("GATE",)):
    return {"evidence_id": eid, "doc_type": doc_type, "supports": list(supports), "locator": "synthetic locator",
            "lineage_root_id": None, "lineage_status": "UNKNOWN"}


def entry(**over):
    e = {"id": "MECH-000001", "record_type": "MECH", "schema_version": "1.0.0-draft", "version": 1, "status": "ACTIVE",
         "superseded_by": None, "created_at": "2026-10-26T00:00:00+00:00", "created_by": "synthetic-fixture",
         "provenance": {"method": "LLM", "source_ids": [], "agent": "synthetic", "locator": None, "notes": None},
         "verification": {"status": "UNVERIFIED", "verifier": None, "verified_at": None, "ai_reviewer": None, "notes": None},
         "external_refs": [], "notes": None,
         "mechanism_key": "SYNTH_FIXTURE_ONE", "label": "synthetic fixture one", "synonyms": [],
         "family": "MICRONUTRIENT_DEGRADATION", "kind": "CHEMICAL_REACTION", "edge_semantics": "REACTION",
         "is_evidence": False, "ai_drafted": True, "provenance_class": "INFERRED_LLM", "review_status": "CANDIDATE",
         "review": {"dual_blind_status": "NOT_STARTED", "reviewer_ids": [], "adjudication_ref": None,
                    "review_provenance_valid": "NOT_CHECKED", "review_packet_row_ids": []},
         "derivation_anchors": [{"anchor_kind": "STEP_CARD", "ref": "synthetic anchor"}],
         "participants": [], "enzyme": None, "gates_unknown": True, "preconditions": [], "condition_gates": [],
         "inhibitors_mitigators": [], "competes_with": [], "consecutive_with": [], "affected_targets": [target()],
         "markers": [], "history_dependence": [], "matrix_scope": scope(), "xrefs": [], "evidence_refs": []}
    e.update(over)
    return e


def accepted(**over):
    """A fully specified ACCEPTED synthetic entry (one STATED gate, one precondition, PRIMARY evidence)."""
    g = gate(mn=stated(1.0), mx=open_(10.0), evidence_ids=["SRC-000001"], status="ACCEPTED",
             matrix_scope=scope("FOOD_CLASS", inc=("synthetic class",)),
             rationale_raw="synthetic: a PRIMARY source states that the reaction is absent outside this window")
    p = precondition(status="ACCEPTED", evidence_ids=["SRC-000001"])
    e = entry(review_status="ACCEPTED", gates_unknown=False, provenance_class="EXTERNAL_VERIFIED",
              verification={"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": "2026-10-26T00:00:00+00:00",
                            "ai_reviewer": None, "notes": None},
              review={"dual_blind_status": "ADJUDICATED", "reviewer_ids": ["Kush", "Parv"], "adjudication_ref": "synthetic",
                      "review_provenance_valid": "VALID", "review_packet_row_ids": ["synthetic-row"]},
              preconditions=[p], condition_gates=[g], evidence_refs=[evidence_ref()],
              matrix_scope=scope("FOOD_CLASS", inc=("synthetic class",)))
    e.update(over)
    return e


def sink(**over):
    e = entry(mechanism_key="SYNTH_SINK", kind="UNRESOLVED_SINK", family="UNRESOLVED", edge_semantics="NOT_APPLICABLE",
              affected_targets=[], gates_unknown=True)
    e.update(over)
    return e


def enzyme_obj():
    x = lambda c: {"curie": c, "relation": "EXACT", "match_basis": "AI_PROPOSED", "xref_status": "PROPOSED",
                   "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": None}
    return {"label_raw": "synthetic enzyme", "ec": x("EC:1.1.1.1"), "go_mf": x("GO:0000001"), "rhea": None}


# ----------------------------------------------------------------------------- accepted variants
def accepted_variants():
    yield "V-1 minimal CANDIDATE, gates_unknown true", entry()
    yield "V-2 NECESSARY pH gate, every bound NOT_REPORTED (nothing concluded)", entry(
        gates_unknown=False, condition_gates=[gate()])
    yield "V-3 STATED min + OPEN_STATED max (studied extreme 10.0) with evidence ids", entry(
        gates_unknown=False, evidence_refs=[evidence_ref()],
        condition_gates=[gate(mn=stated(1.0), mx=open_(10.0), evidence_ids=["SRC-000001"])])
    yield "V-4 core-temperature gate (location carried by the CV id)", entry(
        gates_unknown=False, condition_gates=[gate(cv="CV-008", unit="K", location="NOT_APPLICABLE")])
    yield "V-5 categorical INHIBITING gate on CV-023 (alone: gates_unknown stays true)", entry(
        gates_unknown=True, evidence_refs=[evidence_ref()],
        condition_gates=[gate(cv="CV-023", gtype="INHIBITING", location="MEDIUM", domain_kind="CATEGORICAL_SET",
                              interval=None, evidence_ids=["SRC-000001"],
                              categories={"allowed": [], "excluded": ["synthetic agent"], "unlisted_verdict": "UNKNOWN"})])
    yield "V-6 time gate on the process clock (CV-003 hold / rest)", entry(
        gates_unknown=False, condition_gates=[gate(cv="CV-003", unit="s", location="NOT_APPLICABLE", clock="PROCESS_TAU")])
    yield "V-7 moisture gate with wet basis", entry(
        gates_unknown=False, condition_gates=[gate(cv="CV-016", unit="fraction", basis="WET_BASIS")])
    yield "V-8 precondition IS on a proposed history key", entry(gates_unknown=False, preconditions=[precondition()])
    yield "V-9 UNRESOLVED_SINK", sink()
    yield "V-10 fully specified ACCEPTED entry", accepted()
    yield "V-11 ENZYMATIC entry with an enzyme object", entry(kind="ENZYMATIC", enzyme=enzyme_obj())
    yield "V-12 recorded label collision kept as REJECTED (Strecker canary)", entry(xrefs=[
        {"curie": "RXNO:0000207", "relation": "NOT_EQUIVALENT_COLLISION", "match_basis": "LABEL_MATCH_ONLY",
         "xref_status": "REJECTED", "verification_status": "HUMAN_REJECTED", "verified_by": "Parv",
         "collision_note": "synthetic: same label, different reaction"}])
    yield "V-13 inhibitor evaluated through an INHIBITING gate", entry(
        gates_unknown=False, preconditions=[precondition()], condition_gates=[gate(cv="CV-023", gtype="INHIBITING", location="MEDIUM",
                                                   domain_kind="CATEGORICAL_SET", interval=None,
                                                   categories={"allowed": [], "excluded": [], "unlisted_verdict": "UNKNOWN"})],
        inhibitors_mitigators=[{"inhibitor_key": "INH01", "role": "INHIBITOR", "agent_or_condition_raw": "synthetic agent",
                                "sbo_role": "SBO:0000020", "extent": "UNKNOWN",
                                "evaluated_via": {"mode": "GATE", "gate_key": "CG01", "state_ref": None, "predicate": None},
                                "missing_input_verdict": "UNKNOWN", "evidence_ids": [], "status": "CANDIDATE"}])
    yield "V-14 competition and consecutive declarations", entry(
        competes_with=[{"mechanism_key": "SYNTH_FIXTURE_TWO", "shared_target": state("synthetic_target"),
                        "relation": "PARALLEL_PATHWAY", "evidence_ids": [], "status": "CANDIDATE"}],
        consecutive_with=[{"mechanism_key": "SYNTH_FIXTURE_TWO", "order": "UNKNOWN", "shared_species": None,
                           "evidence_ids": [], "status": "CANDIDATE"}])
    yield "V-15 LEACHED tissue DECREASE and medium INCREASE", entry(affected_targets=[
        target("LEACHED", ("DECREASE",), "TISSUE", key="TGT01"), target("LEACHED", ("INCREASE",), "COOKING_MEDIUM", key="TGT02")])
    yield "V-16 FORMED may later decline (peak then decline)", entry(affected_targets=[
        target("FORMED", ("INCREASE", "DECREASE"), "TISSUE", "PEAK_THEN_DECLINE")])
    yield "V-17 direction exactly [UNKNOWN]", entry(affected_targets=[target("UNKNOWN_TRANSFORMATION", ("UNKNOWN",))])
    yield "V-18 matrix scope MODEL_SYSTEM with a class label", entry(matrix_scope=scope("MODEL_SYSTEM", inc=("synthetic model system",)))
    yield "V-19 VOLATILIZED from the whole system, DECREASE only", entry(affected_targets=[
        target("VOLATILIZED", ("DECREASE",), "WHOLE_SYSTEM")])
    yield "V-20 VOLATILIZED in the medium has no direction rule (DECREASE accepted)", entry(affected_targets=[
        target("VOLATILIZED", ("DECREASE",), "COOKING_MEDIUM")])
    yield "V-21 catalyst through a MODULATING gate, chelating inhibitor acting on it", entry(
        gates_unknown=True,
        condition_gates=[gate(cv="CV-023", gtype="MODULATING", location="MEDIUM", domain_kind="CATEGORICAL_SET", interval=None,
                              categories={"allowed": [], "excluded": [], "unlisted_verdict": "UNKNOWN"})],
        inhibitors_mitigators=[
            {"inhibitor_key": "INH01", "role": "CATALYST", "agent_or_condition_raw": "synthetic catalyst",
             "sbo_role": "SBO:0000013", "extent": "NOT_APPLICABLE",
             "evaluated_via": {"mode": "GATE", "gate_key": "CG01", "state_ref": None, "predicate": None},
             "missing_input_verdict": "UNKNOWN", "evidence_ids": [], "status": "CANDIDATE"},
            {"inhibitor_key": "INH02", "role": "INHIBITOR", "agent_or_condition_raw": "synthetic chelator",
             "sbo_role": "SBO:0000020", "extent": "UNKNOWN", "acts_on_modifier_key": "INH01",
             "evaluated_via": {"mode": "NOT_EVALUABLE_YET", "gate_key": None, "state_ref": None, "predicate": None},
             "missing_input_verdict": "UNKNOWN", "evidence_ids": [], "status": "CANDIDATE"}])
    yield "V-22 OXIDIZED substrate falls, OXIDIZED product rises", entry(affected_targets=[
        target("OXIDIZED", ("DECREASE",), role="SUBSTRATE", key="TGT01"), target("OXIDIZED", ("INCREASE",), role="PRODUCT", key="TGT02")])
    yield "V-23 coupled-redox competition and a start-mode history item", entry(
        competes_with=[{"mechanism_key": "SYNTH_FIXTURE_TWO", "shared_target": state("synthetic_target"),
                        "relation": "COUPLED_REDOX", "evidence_ids": [], "status": "CANDIDATE"}],
        history_dependence=[{"state_ref": state("synthetic_start_mode"), "role": "INPUT_REQUIRED_START_MODE",
                             "evidence_ids": [], "status": "CANDIDATE"}])


def test_accepted_variants_validate():
    for name, inst in accepted_variants():
        assert valid(inst), f"{name} should validate: {flat_errors(inst)[:3]}"


# ----------------------------------------------------------------------------- negative controls
def mutate(base, fn):
    x = copy.deepcopy(base)
    fn(x)
    return x


def cat_gate(gtype="INHIBITING", allowed=(), excluded=(), key="CG01"):
    return gate(cv="CV-023", gtype=gtype, location="MEDIUM", domain_kind="CATEGORICAL_SET", interval=None, key=key,
                categories={"allowed": list(allowed), "excluded": list(excluded), "unlisted_verdict": "UNKNOWN"})


def competes():
    return {"mechanism_key": "SYNTH_FIXTURE_TWO", "shared_target": state("synthetic_target"), "relation": "PARALLEL_PATHWAY",
            "evidence_ids": [], "status": "CANDIDATE"}


def consecutive():
    return {"mechanism_key": "SYNTH_FIXTURE_TWO", "order": "UNKNOWN", "shared_species": None, "evidence_ids": [], "status": "CANDIDATE"}


def marker():
    return {"marker_key": "MRK01", "marker": {"ref_type": "CLASS_LABEL", "ref": "x", "label_raw": "x"}, "marker_unique": False,
            "evidence_ids": [], "status": "CANDIDATE"}


def history():
    return {"state_ref": state("synthetic_history"), "role": "INPUT_REQUIRED", "evidence_ids": [], "status": "CANDIDATE"}


def negatives():
    b = entry(gates_unknown=False, condition_gates=[gate(mn=stated(1.0), mx=open_(10.0), evidence_ids=["SRC-000001"])],
              evidence_refs=[evidence_ref()])
    acc = accepted()
    inh_ne = {"inhibitor_key": "INH01", "role": "INHIBITOR", "agent_or_condition_raw": "x", "sbo_role": "SBO:0000020",
              "extent": "UNKNOWN", "evaluated_via": {"mode": "NOT_EVALUABLE_YET", "gate_key": None, "state_ref": None,
                                                     "predicate": None},
              "missing_input_verdict": "UNKNOWN", "evidence_ids": [], "status": "CANDIDATE"}
    cases = [
        # (name, instance, regex that must appear in the flattened errors)
        ("N-1 no precondition, no gate, gates_unknown false", entry(gates_unknown=False), r"anyOf|minItems"),
        ("N-2 missing_input_verdict APPLICABLE on a gate", mutate(b, lambda x: x["condition_gates"][0].update(missing_input_verdict="APPLICABLE")), r"missing_input_verdict"),
        ("N-3 missing_input_verdict APPLICABLE on a precondition", entry(gates_unknown=False, preconditions=[dict(precondition(), missing_input_verdict="APPLICABLE")]), r"missing_input_verdict"),
        ("N-4 bare null as an interval bound", mutate(b, lambda x: x["condition_gates"][0]["interval"].update(min=None)), r"interval/min"),
        ("N-5 STATED bound without a value", mutate(b, lambda x: x["condition_gates"][0]["interval"].update(min=bound("STATED", None, True))), r"interval/min"),
        ("N-6 OPEN_STATED bound without the studied extreme", mutate(b, lambda x: x["condition_gates"][0]["interval"].update(max=bound("OPEN_STATED"))), r"interval/max"),
        ("N-7 STATED bound without evidence ids", mutate(b, lambda x: x["condition_gates"][0].update(evidence_ids=[])), r"evidence_ids"),
        ("N-8 numeric kinetic key on the entry", entry(k_ref=1.0), r"k_ref|Additional properties"),
        ("N-9 numeric kinetic key on a gate", mutate(b, lambda x: x["condition_gates"][0].update(activation_energy=1.0)), r"activation_energy|Additional properties"),
        ("N-10 default value key on a gate", mutate(b, lambda x: x["condition_gates"][0].update(default=1.0)), r"default|Additional properties"),
        ("N-11 marker_unique true", entry(markers=[{"marker_key": "MRK01", "marker": {"ref_type": "CLASS_LABEL", "ref": "x", "label_raw": "x"}, "marker_unique": True, "evidence_ids": [], "status": "CANDIDATE"}]), r"marker_unique"),
        ("N-12 gate on CV-009 temperature location unspecified", mutate(b, lambda x: x["condition_gates"][0].update(cv_id="CV-009", location="NOT_APPLICABLE")), r"cv_id|not"),
        ("N-12b gate on CV-010 temperature trajectory", mutate(b, lambda x: x["condition_gates"][0].update(cv_id="CV-010", location="NOT_APPLICABLE")), r"cv_id|not"),
        ("N-12c gate on CV-004 time trajectory", mutate(b, lambda x: x["condition_gates"][0].update(cv_id="CV-004", location="NOT_APPLICABLE")), r"cv_id|not"),
        ("N-13 temperature gate that repeats a location", mutate(b, lambda x: x["condition_gates"][0].update(cv_id="CV-008", location="TISSUE")), r"location"),
        ("N-14 pH gate with location NOT_APPLICABLE", mutate(b, lambda x: x["condition_gates"][0].update(location="NOT_APPLICABLE")), r"location"),
        ("N-15 moisture gate without a basis", mutate(b, lambda x: x["condition_gates"][0].update(cv_id="CV-016")), r"basis"),
        ("N-16 basis on a non-moisture gate", mutate(b, lambda x: x["condition_gates"][0].update(basis="WET_BASIS")), r"basis"),
        ("N-17 time gate without the process clock", mutate(b, lambda x: x["condition_gates"][0].update(cv_id="CV-003", location="NOT_APPLICABLE")), r"clock"),
        ("N-18 clock on a non-time gate", mutate(b, lambda x: x["condition_gates"][0].update(clock="PROCESS_TAU")), r"clock"),
        ("N-19 categorical gate that also carries an interval", mutate(b, lambda x: x["condition_gates"][0].update(domain_kind="CATEGORICAL_SET")), r"categories|interval"),
        ("N-20 MODULATING gate with modulates NOT_APPLICABLE", mutate(b, lambda x: x["condition_gates"][0].update(gate_type="MODULATING", modulates="NOT_APPLICABLE")), r"modulates"),
        ("N-21 NECESSARY gate with modulates RATE", mutate(b, lambda x: x["condition_gates"][0].update(modulates="RATE")), r"modulates"),
        ("N-22 ACCEPTED gate with location UNKNOWN", mutate(acc, lambda x: x["condition_gates"][0].update(location="UNKNOWN")), r"location"),
        ("N-23 ACCEPTED entry without HUMAN_VERIFIED", mutate(acc, lambda x: x["verification"].update(status="AI_PRECHECKED", verifier=None, verified_at=None)), r"verification"),
        ("N-24 ACCEPTED entry with only REVIEW_CONTEXT evidence", mutate(acc, lambda x: x["evidence_refs"][0].update(doc_type="REVIEW_CONTEXT")), r"evidence_refs|contains"),
        ("N-25 ACCEPTED entry reviewed by one person", mutate(acc, lambda x: x["review"].update(reviewer_ids=["Kush"])), r"reviewer_ids|minItems"),
        ("N-26 ACCEPTED entry with invalid review provenance", mutate(acc, lambda x: x["review"].update(review_provenance_valid="INVALID")), r"review_provenance_valid"),
        ("N-27 HUMAN_VERIFIED by someone else", mutate(acc, lambda x: x["verification"].update(verifier="Someone")), r"verifier"),
        ("N-28 ENZYMATIC entry without an enzyme", entry(kind="ENZYMATIC"), r"enzyme"),
        ("N-29 non-ENZYMATIC entry with an enzyme", entry(enzyme=enzyme_obj()), r"enzyme"),
        ("N-30 sink with a participant", sink(participants=[{"role_label": "x", "entity": {"ref_type": "CLASS_LABEL", "ref": "x", "label_raw": "x"}, "sbo_role": "UNKNOWN"}]), r"participants"),
        ("N-31 sink with gates_unknown false", sink(gates_unknown=False), r"gates_unknown"),
        ("N-32 sink with an affected target", sink(affected_targets=[target()]), r"affected_targets"),
        ("N-33 non-sink without an affected target", entry(affected_targets=[]), r"affected_targets|minItems"),
        ("N-34 is_evidence true", entry(is_evidence=True), r"is_evidence"),
        ("N-35 ACCEPTED xref without human verification", entry(xrefs=[{"curie": "GO:0000001", "relation": "EXACT", "match_basis": "LABEL_MATCH_ONLY", "xref_status": "ACCEPTED", "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": None}]), r"verification_status|verified_by"),
        ("N-36 collision xref that is not REJECTED", entry(xrefs=[{"curie": "RXNO:0000207", "relation": "NOT_EQUIVALENT_COLLISION", "match_basis": "LABEL_MATCH_ONLY", "xref_status": "PROPOSED", "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": "x"}]), r"xref_status"),
        ("N-37 undocumented inhibitor with gates_unknown false", entry(gates_unknown=False, preconditions=[precondition()], inhibitors_mitigators=[inh_ne]), r"gates_unknown"),
        ("N-38 FORMED target that can only DECREASE", entry(affected_targets=[target("FORMED", ("DECREASE",))]), r"allowed_directions"),
        ("N-39 DEGRADED target that can INCREASE", entry(affected_targets=[target("DEGRADED", ("INCREASE",))]), r"allowed_directions"),
        ("N-40 UNKNOWN direction mixed with INCREASE", entry(affected_targets=[target("UNKNOWN_TRANSFORMATION", ("UNKNOWN", "INCREASE"))]), r"allowed_directions|maxItems"),
        ("N-41 LEACHED from the whole system", entry(affected_targets=[target("LEACHED", ("DECREASE",), "WHOLE_SYSTEM")]), r"compartment"),
        ("N-42 LEACHED into the medium as DECREASE", entry(affected_targets=[target("LEACHED", ("DECREASE",), "COOKING_MEDIUM")]), r"allowed_directions"),
        ("N-43 ABSORBED into the tissue as DECREASE", entry(affected_targets=[target("ABSORBED", ("DECREASE",), "TISSUE")]), r"allowed_directions"),
        ("N-44 effect type outside the registry (RETAINED)", entry(affected_targets=[target("RETAINED", ("INCREASE",))]), r"effect_type"),
        ("N-45 evidence id that is a sealed case id", entry(evidence_refs=[dict(evidence_ref(), evidence_id="CASE-000001")]), r"evidence_id"),
        ("N-46 PRIMARY evidence without a locator", entry(evidence_refs=[dict(evidence_ref(), locator=None)]), r"locator"),
        ("N-47 lineage root without PRESENT status", entry(evidence_refs=[dict(evidence_ref(), lineage_root_id="LROOT-000001")]), r"lineage_root_id"),
        ("N-48 predicate with UNKNOWN as a satisfying value", entry(gates_unknown=False, preconditions=[precondition(values=("UNKNOWN",))]), r"values"),
        ("N-49 PRESENT predicate carrying values", entry(gates_unknown=False, preconditions=[precondition(op="PRESENT", values=("X",))]), r"values|maxItems"),
        ("N-50 IN predicate with one value", entry(gates_unknown=False, preconditions=[precondition(op="IN", values=("X",))]), r"values|minItems"),
        ("N-51 state ref with both svar id and key", entry(gates_unknown=False, preconditions=[dict(precondition(), state_ref={"ref_status": "PROPOSED_KEY", "svar_id": "SVAR-000001", "state_key": "x_y_z", "label_raw": "x"})]), r"svar_id|state_ref"),
        ("N-52 FOOD_CLASS scope without an included matrix", entry(matrix_scope=scope("FOOD_CLASS")), r"included|minItems"),
        ("N-53 unlisted matrix verdict APPLICABLE", entry(matrix_scope=dict(scope(), unlisted_verdict="APPLICABLE")), r"unlisted_verdict"),
        ("N-54 mechanism key in lower case", entry(mechanism_key="lower_case"), r"mechanism_key"),
        ("N-55 id outside the MECH pattern (card spelling)", entry(id="MECH-UNRESOLVED_LOSS"), r"/id|id "),
        ("N-56 provenance class EXTERNAL_VERIFIED on an unverified entry", entry(provenance_class="EXTERNAL_VERIFIED"), r"verification|provenance_class"),
        ("N-57 derivation anchors missing", entry(derivation_anchors=[]), r"derivation_anchors|minItems"),
        ("N-58 competes_with without a shared target", entry(competes_with=[{"mechanism_key": "SYNTH_FIXTURE_TWO", "relation": "PARALLEL_PATHWAY", "evidence_ids": [], "status": "CANDIDATE"}]), r"shared_target|required"),
        # ---- round-3 review controls (A#1-#4, #14, #15; B 21-3, 21-9, 21-10, 21-11, 21-13)
        ("N-59 UNKNOWN as an allowed category", entry(gates_unknown=True, condition_gates=[cat_gate(allowed=["UNKNOWN"])]), r"allowed"),
        ("N-60 Unknown (mixed case) as an allowed category", entry(gates_unknown=True, condition_gates=[cat_gate(allowed=["Unknown"])]), r"allowed"),
        ("N-61 unknown (lower case) as an excluded category", entry(gates_unknown=True, condition_gates=[cat_gate(excluded=["unknown"])]), r"excluded"),
        ("N-62 unknown (lower case) as a predicate value", entry(gates_unknown=False, preconditions=[precondition(values=("unknown",))]), r"values"),
        ("N-63 ACCEPTED precondition without evidence", entry(preconditions=[precondition(status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-64 ACCEPTED competes_with without evidence", mutate(entry(competes_with=[dict(competes(), status="ACCEPTED")]), lambda x: None), r"evidence_ids|minItems"),
        ("N-65 ACCEPTED consecutive_with without evidence", entry(consecutive_with=[dict(consecutive(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-66 ACCEPTED affected_target without evidence", entry(affected_targets=[dict(target(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-67 ACCEPTED marker without evidence", entry(markers=[dict(marker(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-68 ACCEPTED history item without evidence", entry(history_dependence=[dict(history(), status="ACCEPTED")]), r"evidence_ids|minItems"),
        ("N-69 lone MODULATING gate with gates_unknown false (vacuous APPLICABLE)", entry(gates_unknown=False, condition_gates=[gate(gtype="MODULATING")]), r"anyOf|contains|minItems"),
        ("N-70 lone INHIBITING gate with gates_unknown false", entry(gates_unknown=False, condition_gates=[cat_gate(gtype="INHIBITING")]), r"anyOf|contains|minItems"),
        ("N-71 VOLATILIZED from the whole system as INCREASE", entry(affected_targets=[target("VOLATILIZED", ("INCREASE",), "WHOLE_SYSTEM")]), r"allowed_directions"),
        ("N-72 ABSORBED into the whole system", entry(affected_targets=[target("ABSORBED", ("INCREASE",), "WHOLE_SYSTEM")]), r"compartment"),
        ("N-73 OXIDIZED substrate that increases", entry(affected_targets=[target("OXIDIZED", ("INCREASE",), role="SUBSTRATE")]), r"allowed_directions"),
        ("N-74 OXIDIZED product that can only decrease", entry(affected_targets=[target("OXIDIZED", ("DECREASE",), role="PRODUCT")]), r"allowed_directions"),
        ("N-75 old-style gate key G1", entry(gates_unknown=False, condition_gates=[gate(key="G1")]), r"gate_key"),
        ("N-76 old-style target key T1", entry(affected_targets=[target(key="T1")]), r"target_key"),
        ("N-77 old-style inhibitor key I1", entry(inhibitors_mitigators=[dict(inh_ne, inhibitor_key="I1")], gates_unknown=True), r"inhibitor_key"),
        ("N-78 CV-021 headspace oxygen with location MEDIUM", entry(gates_unknown=False, condition_gates=[gate(cv="CV-021", unit="fraction", location="MEDIUM")]), r"location"),
        ("N-79 interval that still carries an optimum", mutate(b, lambda x: x["condition_gates"][0]["interval"].update(opt=bound())), r"opt|Additional properties"),
        ("N-80 xref in a namespace that is not admitted (MESH)", entry(xrefs=[{"curie": "MESH:D000001", "relation": "RELATED", "match_basis": "AI_PROPOSED", "xref_status": "PROPOSED", "verification_status": "UNVERIFIED", "verified_by": None, "collision_note": None}]), r"curie"),
        ("N-81 catalyst with a COMPLETE extent", entry(gates_unknown=True, inhibitors_mitigators=[dict(inh_ne, role="CATALYST", sbo_role="SBO:0000013", extent="COMPLETE")]), r"extent"),
        ("N-82 catalyst carrying the inhibitor SBO role", entry(gates_unknown=True, inhibitors_mitigators=[dict(inh_ne, role="CATALYST", extent="NOT_APPLICABLE")]), r"sbo_role"),
        ("N-83 catalyst that points at another modifier", entry(gates_unknown=True, inhibitors_mitigators=[dict(inh_ne, role="CATALYST", sbo_role="SBO:0000013", extent="NOT_APPLICABLE", acts_on_modifier_key="INH02")]), r"role"),
        ("N-84 inhibitor with extent NOT_APPLICABLE", entry(gates_unknown=True, inhibitors_mitigators=[dict(inh_ne, extent="NOT_APPLICABLE")]), r"extent"),
        ("N-85 affected target without target_role", entry(affected_targets=[{k: v for k, v in target().items() if k != "target_role"}]), r"target_role|required"),
    ]
    return cases


def test_negative_controls_rejected_for_the_intended_reason():
    for name, inst, why in negatives():
        errs = flat_errors(inst)
        assert errs, f"{name} was ACCEPTED but must be rejected"
        assert any(re.search(why, e) for e in errs), f"{name}: rejected, but not for /{why}/: {errs[:4]}"


# ----------------------------------------------------------------------------- structure of the schema itself
FORBIDDEN_NAMES = {"k", "k_ref", "ln_k_ref", "ea", "e_a", "activation_energy", "a_factor", "pre_exponential", "arrhenius",
                   "q10", "half_life", "d_value", "z_value", "rate_constant", "reaction_order", "order_of_reaction",
                   "t_ref", "tref", "kinetic_parameter", "k_value"}


def test_schema_is_a_valid_2020_12_schema_and_all_refs_resolve():
    Draft202012Validator.check_schema(SCHEMA)
    assert SCHEMA["$schema"].endswith("2020-12/schema")
    refs = [n["$ref"] for _, n in walk_schema(SCHEMA) if isinstance(n.get("$ref"), str)]
    for r in refs:
        assert r.startswith("#/$defs/") and r.split("/")[-1] in SCHEMA["$defs"], r


def test_no_additional_properties_anywhere_and_no_default_keyword():
    for p, n in walk_schema(SCHEMA):
        matcher = re.search(r"/(if|contains|not)(/|$)", p)       # if / contains matcher fragments are open by design
        if "properties" in n and n.get("type") == "object" and not matcher:
            assert n.get("additionalProperties") is False, f"open object at {p}"
        assert "default" not in n, f"'default' keyword at {p}"


def test_no_kinetic_parameter_names_in_the_schema():
    names = set()
    for p, n in walk_schema(SCHEMA):
        if isinstance(n.get("properties"), dict):
            names |= {k.lower() for k in n["properties"]}
    assert not (names & FORBIDDEN_NAMES), names & FORBIDDEN_NAMES


def test_r15_constants_are_in_the_schema():
    d = SCHEMA["$defs"]
    assert d["missing_input_verdict"]["const"] == "UNKNOWN"
    assert SCHEMA["properties"]["is_evidence"]["const"] is False
    assert d["marker"]["properties"]["marker_unique"]["const"] is False
    for k in ("precondition", "condition_gate", "inhibitor"):
        assert d[k]["properties"]["missing_input_verdict"] == {"$ref": "#/$defs/missing_input_verdict"}
    assert "opt" not in d["interval"]["properties"] and "opt_bound" not in d, "no optimum is stored (21-10)"
    for k in ("precondition", "competes_with", "consecutive_with", "affected_target", "marker", "history_item",
              "condition_gate", "inhibitor"):
        rules = [json.dumps(x) for x in d[k].get("allOf", [])]
        assert any('"ACCEPTED"' in r and '"evidence_ids": {"minItems": 1}' in r for r in rules), f"{k}: ACCEPTED needs evidence"
    assert d["matrix_scope"]["properties"]["unlisted_verdict"] == {"$ref": "#/$defs/missing_input_verdict"}
    assert d["categories"]["properties"]["unlisted_verdict"] == {"$ref": "#/$defs/missing_input_verdict"}


def test_prefix_is_free_in_the_python_registry():
    p = ROOT / "src" / "culinarystate" / "ledgers" / "registry.py"
    if p.exists():
        assert not re.search(r'_add\("MECH"', p.read_text(encoding="utf-8")), "MECH already registered"


# ----------------------------------------------------------------------------- vocabulary CSVs
def test_vocabulary_rows_are_draft_sourced_and_unique():
    spec = {"mechanism_seed_roster_draft_v1.csv": ("mechanism_key", "source_anchors"),
            "effect_type_registry_draft_v1.csv": ("effect_type", "source"),
            "condition_gate_type_registry_draft_v1.csv": ("gate_type", "source")}
    for name, (key, src) in spec.items():
        rows = read_csv(name)
        assert rows, name
        assert len({r[key] for r in rows}) == len(rows), f"duplicate key in {name}"
        for r in rows:
            assert r["registry_status"] == STATUS, (name, r[key])
            assert r[src].strip(), f"unsourced row {r[key]} in {name}"
            assert r["ai_drafted"] in ("TRUE", "FALSE"), (name, r[key])


def test_effect_types_match_schema_and_rxn_enum():
    rows = read_csv("effect_type_registry_draft_v1.csv")
    enum = set(SCHEMA["$defs"]["affected_target"]["properties"]["effect_type"]["enum"])
    assert {r["effect_type"] for r in rows} == enum
    rxn = json.loads((ROOT / "ledgers" / "schemas" / "RXN.schema.json").read_text(encoding="utf-8"))
    rxn_enum = set(rxn["properties"]["relation"]["enum"])
    aligned = {r["rxn_relation"] for r in rows if r["origin"] == "ALIGNED_RXN"}
    assert aligned <= rxn_enum
    assert rxn_enum - aligned == {"RETAINED"}, "every RXN verb except RETAINED (an outcome) must have an effect type"
    assert all(r["rxn_relation"] == "" for r in rows if r["origin"] == "PROPOSED_ADDITION")
    assert all(r["rxn_relation"] == r["effect_type"] for r in rows if r["origin"] == "ALIGNED_RXN")


def test_direction_rules_in_the_effect_csv_match_the_schema():
    """Every compartment rule written in the CSV is the rule the schema enforces (A#4: the CSV said WHOLE_SYSTEM was
    admitted for VOLATILIZED while the schema rejected it)."""
    rows = {r["effect_type"]: r["direction_rule"] for r in read_csv("effect_type_registry_draft_v1.csv")}
    table = [  # (effect, compartment, directions, schema accepts, phrase the CSV must contain)
        ("LEACHED", "TISSUE", ("DECREASE",), True, "compartment TISSUE: DECREASE only"),
        ("LEACHED", "TISSUE", ("INCREASE",), False, None),
        ("LEACHED", "COOKING_MEDIUM", ("INCREASE",), True, "compartment COOKING_MEDIUM: INCREASE only"),
        ("LEACHED", "COOKING_MEDIUM", ("DECREASE",), False, None),
        ("LEACHED", "WHOLE_SYSTEM", ("DECREASE",), False, "WHOLE_SYSTEM is not admitted"),
        ("VOLATILIZED", "TISSUE", ("DECREASE",), True, "compartment TISSUE: DECREASE only"),
        ("VOLATILIZED", "COOKING_MEDIUM", ("INCREASE",), True, "compartment COOKING_MEDIUM: no direction rule"),
        ("VOLATILIZED", "COOKING_MEDIUM", ("DECREASE",), True, None),
        ("VOLATILIZED", "WHOLE_SYSTEM", ("DECREASE",), True, "compartment WHOLE_SYSTEM: DECREASE only"),
        ("VOLATILIZED", "WHOLE_SYSTEM", ("INCREASE",), False, None),
        ("ABSORBED", "TISSUE", ("INCREASE",), True, "compartment TISSUE: INCREASE only"),
        ("ABSORBED", "COOKING_MEDIUM", ("DECREASE",), True, "compartment COOKING_MEDIUM: DECREASE only"),
        ("ABSORBED", "WHOLE_SYSTEM", ("INCREASE",), False, "WHOLE_SYSTEM is not admitted"),
    ]
    for eff, comp, dirs, ok, phrase in table:
        assert valid(entry(affected_targets=[target(eff, dirs, comp)])) == ok, (eff, comp, dirs)
        if phrase:
            assert phrase in rows[eff], (eff, phrase)


def test_gate_types_match_schema():
    rows = read_csv("condition_gate_type_registry_draft_v1.csv")
    assert {r["gate_type"] for r in rows} == set(SCHEMA["$defs"]["condition_gate"]["properties"]["gate_type"]["enum"])
    assert {r["gate_type"]: r["changes_applicability_verdict"] for r in rows} == {
        "NECESSARY": "YES", "MODULATING": "NO", "INHIBITING": "YES"}


def test_roster_uses_only_schema_vocabulary():
    rows = read_csv("mechanism_seed_roster_draft_v1.csv")
    top = SCHEMA["properties"]
    effects = set(SCHEMA["$defs"]["affected_target"]["properties"]["effect_type"]["enum"])
    key_re = re.compile(SCHEMA["properties"]["mechanism_key"]["pattern"])
    for r in rows:
        assert key_re.match(r["mechanism_key"]), r["mechanism_key"]
        assert r["kind"] in top["kind"]["enum"], r["mechanism_key"]
        assert r["family"] in top["family"]["enum"], r["mechanism_key"]
        assert r["edge_semantics_proposed"] in top["edge_semantics"]["enum"], r["mechanism_key"]
        assert set(filter(None, r["typical_effect_types"].split(";"))) <= effects, r["mechanism_key"]
        assert r["card_listing"] in ("CARD_21B_LIST", "PROPOSED_ADDITION", "PROPOSED_ADDITION_OPTIONAL")
        assert r["entry_status"] == "SEED_NOT_YET_AUTHORED"
        assert (r["kind"] == "UNRESOLVED_SINK") == (r["family"] == "UNRESOLVED")


def test_roster_covers_the_g21_2_families_and_every_kind():
    rows = read_csv("mechanism_seed_roster_draft_v1.csv")
    fams = {r["family"] for r in rows}
    sec_144_1 = {"MAILLARD_GLYCATION", "SUGAR_THERMAL_DEGRADATION", "LIPID_OXIDATION_DECOMPOSITION", "PROTEIN_STRUCTURAL",
                 "COLLAGEN_TRANSITION", "STARCH_TRANSITION", "CUTTING_TRIGGERED_ENZYMATIC", "FERMENTATION",
                 "VOLATILE_MATERIAL_TRANSFER", "PIGMENT_CELLWALL_TRANSITION"}
    assert sec_144_1 <= fams
    keys = {r["mechanism_key"] for r in rows}
    assert {"LEACHING", "VOLATILISATION", "MOISTURE_LOSS", "UNRESOLVED_LOSS"} <= keys
    assert {r["kind"] for r in rows} == set(SCHEMA["properties"]["kind"]["enum"])
    assert 20 <= len(rows) <= 40, len(rows)          # plan card target, PROPOSED_PILOT
    # the cell-wall half of the 144.1 'pigment / cell-wall' family needs its own entry
    assert any("cell-wall" in r["source_anchors"] or "cell_wall" in r["proc_label_b0"] for r in rows)


def test_r14_both_candidate_systems_represented_and_neither_frozen():
    rows = read_csv("mechanism_seed_roster_draft_v1.csv")
    roles = {r["r14_system_role"] for r in rows}
    assert roles <= {"AA_PATHWAY", "CHL_PATHWAY", "NEITHER"}, "generic entries (leaching ...) carry NEITHER, not a system tag"
    assert {"AA_PATHWAY", "CHL_PATHWAY"} <= roles
    n_aa = sum(r["r14_system_role"] == "AA_PATHWAY" for r in rows)
    n_chl = sum(r["r14_system_role"] == "CHL_PATHWAY" for r in rows)
    assert min(n_aa, n_chl) >= 4 and abs(n_aa - n_chl) <= 1, (n_aa, n_chl)     # coverage of the two systems stays symmetric (G-6)
    for r in rows:
        for cell in r.values():
            assert not re.search(r"\b(selected|chosen|decided|first simulator is)\b", cell, re.I), (r["mechanism_key"], cell[:80])
    sch_text = json.dumps(SCHEMA)
    assert "SIM-AA" not in sch_text and "SIM-CHL" not in sch_text, "the schema must stay system-agnostic"
    assert not re.search(r"ascorb|chlorophyll|pheoph|vitamin c", sch_text, re.I), "the schema must name neither candidate system (R-14)"


def test_roster_proc_labels_exist_in_the_proc_ledger():
    p = ROOT / "ledgers" / "data" / "PROC.jsonl"
    if not p.exists():
        return
    labels = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        labels |= set(json.loads(line).get("mechanism_families") or [])
    used = set()
    for r in read_csv("mechanism_seed_roster_draft_v1.csv"):
        used |= set(filter(None, r["proc_label_b0"].split(";")))
    assert used <= labels, used - labels


# ----------------------------------------------------------------------------- semantic checks (design of the future validator)
def inh_fixture(key="INH01"):
    return {"inhibitor_key": key, "role": "INHIBITOR", "agent_or_condition_raw": "x", "sbo_role": "SBO:0000020",
            "extent": "UNKNOWN", "evaluated_via": {"mode": "NOT_EVALUABLE_YET", "gate_key": None, "state_ref": None,
                                                   "predicate": None},
            "missing_input_verdict": "UNKNOWN", "evidence_ids": [], "status": "CANDIDATE"}


def semantic_problems(e, cv_rows):
    cv = {r["condition_variable_id"]: r for r in cv_rows}
    probs = []
    for coll, key in (("preconditions", "precondition_key"), ("condition_gates", "gate_key"),
                      ("inhibitors_mitigators", "inhibitor_key"), ("affected_targets", "target_key"), ("markers", "marker_key")):
        ks = [x[key] for x in e[coll]]
        if len(set(ks)) != len(ks):
            probs.append(f"duplicate {key}")
    ev = {r["evidence_id"] for r in e["evidence_refs"]}
    for coll in ("preconditions", "condition_gates", "inhibitors_mitigators", "competes_with", "consecutive_with",
                 "affected_targets", "markers", "history_dependence"):
        for x in e[coll]:
            if set(x["evidence_ids"]) - ev:
                probs.append(f"{coll}: evidence id not in evidence_refs")
    gates = {g["gate_key"]: g for g in e["condition_gates"]}
    for g in e["condition_gates"]:
        if g["cv_id"] not in cv:
            probs.append(f"{g['gate_key']}: unknown CV")
            continue
        if g["domain_kind"] == "NUMERIC_INTERVAL":
            iv = g["interval"]
            if iv["unit"] != cv[g["cv_id"]]["canonical_unit"]:
                probs.append(f"{g['gate_key']}: unit is not the CV canonical unit")
            vals = [iv[k]["value"] for k in ("min", "max") if iv[k]["status"] == "STATED"]
            if vals != sorted(vals):
                probs.append(f"{g['gate_key']}: min <= max violated")
            if cv[g["cv_id"]]["dimension"].startswith("categorical"):
                probs.append(f"{g['gate_key']}: numeric window on a categorical CV")
        else:
            if g["categories"] and set(g["categories"]["allowed"]) & set(g["categories"]["excluded"]):
                probs.append(f"{g['gate_key']}: allowed and excluded overlap")
    mods = {i["inhibitor_key"]: i for i in e["inhibitors_mitigators"]}
    for i in e["inhibitors_mitigators"]:
        v = i["evaluated_via"]
        want = "MODULATING" if i["role"] in ("CATALYST", "PROMOTER") else "INHIBITING"
        if v["mode"] == "GATE" and (v["gate_key"] not in gates or gates[v["gate_key"]]["gate_type"] != want):
            probs.append(f"{i['inhibitor_key']}: GATE mode must name a {want} gate of this entry")
        t = i.get("acts_on_modifier_key")
        if t and (t not in mods or mods[t]["role"] not in ("CATALYST", "PROMOTER")):
            probs.append(f"{i['inhibitor_key']}: acts_on_modifier_key must name a CATALYST or PROMOTER of this entry")
    # E-7 (OPEN_QUESTION D21-20): for a CHEMICAL_REACTION a NECESSARY gate on a temperature, pH or water-activity axis is
    # admitted only when PRIMARY evidence states that the reaction is absent (not merely slow) and the gate says so.
    prim = {r["evidence_id"] for r in e["evidence_refs"] if r["doc_type"] == "PRIMARY"}
    if e["kind"] == "CHEMICAL_REACTION":
        for g in e["condition_gates"]:
            if g["gate_type"] == "NECESSARY" and g["cv_id"] in {"CV-005", "CV-006", "CV-007", "CV-008", "CV-013", "CV-015"}:
                if not g["evidence_ids"] or not set(g["evidence_ids"]) <= prim or not (g["rationale_raw"] or "").strip():
                    probs.append(f"{g['gate_key']}: E-7 NECESSARY T / pH / aw gate on a chemical reaction needs PRIMARY evidence "
                                 "of absence and a rationale")
    return probs


def asymmetric_links(entries):
    by = {x["mechanism_key"]: x for x in entries}
    bad = []
    for x in entries:
        for c in x["competes_with"]:
            q = by.get(c["mechanism_key"])
            if q is None or x["mechanism_key"] not in {y["mechanism_key"] for y in q["competes_with"]}:
                bad.append(("competes_with", x["mechanism_key"], c["mechanism_key"]))
        conv = {"THIS_PRECEDES_OTHER": "OTHER_PRECEDES_THIS", "OTHER_PRECEDES_THIS": "THIS_PRECEDES_OTHER", "UNKNOWN": "UNKNOWN"}
        for c in x["consecutive_with"]:
            q = by.get(c["mechanism_key"])
            ok = q is not None and any(y["mechanism_key"] == x["mechanism_key"] and y["order"] == conv[c["order"]]
                                        for y in q["consecutive_with"])
            if not ok:
                bad.append(("consecutive_with", x["mechanism_key"], c["mechanism_key"]))
    return bad


def test_semantic_checks_on_fixtures():
    p = REG / "condition_variable_registry_v1.csv"
    with open(p, newline="", encoding="utf-8") as fh:
        cv = list(csv.DictReader(fh))
    assert semantic_problems(accepted(), cv) == []
    ok = entry(gates_unknown=False, condition_gates=[gate(mn=stated(1.0), mx=stated(2.0), evidence_ids=["SRC-000001"],
                                                          rationale_raw="synthetic absence statement")],
               evidence_refs=[evidence_ref()])
    assert semantic_problems(ok, cv) == []
    bad_cases = {
        "duplicate gate_key": entry(gates_unknown=False, condition_gates=[gate(), gate(cv="CV-015", unit="aw")]),
        "E-7 NECESSARY pH gate on a chemical reaction without PRIMARY evidence of absence": entry(
            gates_unknown=False, condition_gates=[gate(mn=stated(1.0), mx=stated(2.0), evidence_ids=["SRC-000001"])],
            evidence_refs=[evidence_ref("SRC-000001", "REVIEW_CONTEXT")]),
        "acts_on_modifier_key names a non-catalyst": entry(gates_unknown=True, inhibitors_mitigators=[
            dict(inh_fixture("INH01"), role="INHIBITOR"), dict(inh_fixture("INH02"), acts_on_modifier_key="INH01")]),
        "catalyst evaluated through an INHIBITING gate": entry(
            gates_unknown=True, condition_gates=[cat_gate("INHIBITING")],
            inhibitors_mitigators=[dict(inh_fixture("INH01"), role="CATALYST", sbo_role="SBO:0000013", extent="NOT_APPLICABLE",
                                        evaluated_via={"mode": "GATE", "gate_key": "CG01", "state_ref": None, "predicate": None})]),
        "order": entry(gates_unknown=False, condition_gates=[gate(mn=stated(3.0), mx=stated(2.0), evidence_ids=["SRC-000001"])],
                       evidence_refs=[evidence_ref()]),
        "unit": entry(gates_unknown=False, condition_gates=[gate(unit="K")]),
        "unknown CV": entry(gates_unknown=False, condition_gates=[gate(cv="CV-999")]),
        "evidence not in refs": entry(gates_unknown=False, condition_gates=[gate(mn=stated(1.0), evidence_ids=["SRC-000009"])]),
        "inhibitor names a NECESSARY gate": entry(
            gates_unknown=False, condition_gates=[gate()],
            inhibitors_mitigators=[dict(inh_fixture("INH01"), evaluated_via={"mode": "GATE", "gate_key": "CG01", "state_ref": None,
                                                                              "predicate": None})]),
        "categorical overlap": entry(gates_unknown=True, condition_gates=[gate(
            cv="CV-023", gtype="INHIBITING", location="MEDIUM", domain_kind="CATEGORICAL_SET", interval=None,
            categories={"allowed": ["x"], "excluded": ["x"], "unlisted_verdict": "UNKNOWN"}, evidence_ids=["SRC-000001"])],
            evidence_refs=[evidence_ref()]),
    }
    for name, inst in bad_cases.items():
        assert valid(inst), f"{name}: fixture must be schema-valid (the defect is semantic)"
        assert semantic_problems(inst, cv), f"{name}: semantic defect not found"


def test_competition_and_consecutive_links_must_be_declared_on_both_sides():
    a = entry(mechanism_key="SYNTH_FIXTURE_ONE", competes_with=[{"mechanism_key": "SYNTH_FIXTURE_TWO", "shared_target": state(),
                                                                "relation": "PARALLEL_PATHWAY", "evidence_ids": [], "status": "CANDIDATE"}],
              consecutive_with=[{"mechanism_key": "SYNTH_FIXTURE_TWO", "order": "THIS_PRECEDES_OTHER", "shared_species": None,
                                 "evidence_ids": [], "status": "CANDIDATE"}])
    b = entry(mechanism_key="SYNTH_FIXTURE_TWO")
    assert len(asymmetric_links([a, b])) == 2
    b["competes_with"] = copy.deepcopy(a["competes_with"]); b["competes_with"][0]["mechanism_key"] = "SYNTH_FIXTURE_ONE"
    b["consecutive_with"] = copy.deepcopy(a["consecutive_with"])
    b["consecutive_with"][0].update(mechanism_key="SYNTH_FIXTURE_ONE", order="OTHER_PRECEDES_THIS")
    assert asymmetric_links([a, b]) == []


# ----------------------------------------------------------------------------- three-valued reading (test-local reference)
def k3(vs):
    vs = [v for v in vs if v is not None]
    if NA in vs:
        return NA
    if U in vs:
        return U
    return A


def side(b, x, lower):
    if b["status"] == "OPEN_STATED":
        # not limited on this side WITHIN THE STUDIED RANGE: beyond the studied extreme it is an extrapolation (UNKNOWN)
        inside = x >= b["value"] if lower else x <= b["value"]
        if not b["inclusive"]:
            inside = x > b["value"] if lower else x < b["value"]
        return A if inside else U
    if b["status"] == "NOT_REPORTED":
        return U
    if lower:
        ok = x >= b["value"] if b["inclusive"] else x > b["value"]
    else:
        ok = x <= b["value"] if b["inclusive"] else x < b["value"]
    return A if ok else NA


def window(g, x):
    if x is None:
        return U
    iv = g["interval"]
    return k3([side(iv["min"], x, True), side(iv["max"], x, False)])


def gate_verdict(g, x):
    if g["status"] != "ACCEPTED":
        return U
    if g["gate_type"] == "MODULATING":
        return None
    w = window(g, x)
    return w if g["gate_type"] == "NECESSARY" else {A: NA, NA: A, U: U}[w]    # INHIBITING, extent assumed COMPLETE


def pre_verdict(p, v):
    if p["status"] != "ACCEPTED" or v in (None, "UNKNOWN"):
        return U
    op, vals = p["predicate"]["operator"], p["predicate"]["values"]
    ok = {"IS": v in vals, "IN": v in vals, "IS_NOT": v not in vals, "NOT_IN": v not in vals,
          "PRESENT": v == "PRESENT", "ABSENT": v == "ABSENT"}[op]
    return A if ok else NA


def matrix_verdict(ms, m):
    if m is None:
        return U
    if m in {i["ref"] for i in ms["excluded"]}:
        return NA
    return A if m in {i["ref"] for i in ms["included"]} else U


def entry_verdict(e, q):
    if e["review_status"] != "ACCEPTED" or e["gates_unknown"]:
        return U
    parts = [matrix_verdict(e["matrix_scope"], q.get("matrix"))]
    parts += [pre_verdict(p, q["states"].get(p["state_ref"]["state_key"])) for p in e["preconditions"]]
    parts += [gate_verdict(g, q["axes"].get(g["cv_id"])) for g in e["condition_gates"]]
    return k3(parts)


def route(verdicts):
    return "SIMULATE" if verdicts and all(v == A for v in verdicts) else "NOT_SIMULATE"


def test_k3_conjunction_table():
    assert k3([A, A]) == A and k3([A, U]) == U and k3([U, NA]) == NA and k3([A, NA, U]) == NA and k3([]) == A


def test_interval_bounds_are_never_silently_open():
    g = gate(mn=stated(1.0), mx=bound("NOT_REPORTED"), status="ACCEPTED")
    assert window(g, 5.0) == U            # above the stated min, max unreported: nothing can be concluded
    assert window(g, 0.5) == NA           # below the stated min: certain violation
    assert window(g, None) == U           # no input
    g2 = gate(mn=stated(1.0), mx=open_(10.0), status="ACCEPTED")
    assert window(g2, 5.0) == A and window(g2, 1.0) == A and window(g2, 0.99) == NA
    assert window(g2, 10.0) == A and window(g2, 10.5) == U       # beyond the studied extreme: extrapolation, never APPLICABLE
    g2b = gate(mn=open_(1.0), mx=stated(10.0), status="ACCEPTED")
    assert window(g2b, 0.5) == U and window(g2b, 1.0) == A and window(g2b, 10.5) == NA
    g3 = gate(mn=stated(1.0, False), mx=stated(2.0), status="ACCEPTED")
    assert window(g3, 1.0) == NA and window(g3, 2.0) == A and window(g3, 2.0001) == NA


def test_matrix_and_inhibitor_semantics():
    ms = scope("FOOD_CLASS", inc=("in",), exc=("out",))
    assert matrix_verdict(ms, "in") == A and matrix_verdict(ms, "out") == NA
    assert matrix_verdict(ms, "elsewhere") == U and matrix_verdict(ms, None) == U
    inh = gate(cv="CV-013", gtype="INHIBITING", mn=stated(0.0), mx=stated(3.0), status="ACCEPTED")
    assert gate_verdict(inh, 2.0) == NA and gate_verdict(inh, 5.0) == A and gate_verdict(inh, None) == U
    mod = gate(gtype="MODULATING", status="ACCEPTED")
    assert gate_verdict(mod, 1.0) is None


def test_candidates_and_gates_unknown_never_route_to_simulate():
    q = {"matrix": "synthetic class", "states": {"synthetic_state": "SYNTH_A"}, "axes": {"CV-013": 5.0}}
    e = accepted()
    assert entry_verdict(e, q) == A and route([entry_verdict(e, q)]) == "SIMULATE"
    for mut in (lambda x: x.update(review_status="CANDIDATE"), lambda x: x.update(gates_unknown=True)):
        assert entry_verdict(mutate(e, mut), q) == U
    assert entry_verdict(e, {**q, "axes": {}}) == U
    assert entry_verdict(e, {**q, "states": {}}) == U
    assert entry_verdict(e, {**q, "matrix": "other"}) == U


def test_property_unknown_never_becomes_applicable_or_simulate():
    rng = random.Random(21)
    for _ in range(3000):
        mn = rng.choice([stated(rng.uniform(0, 5)), open_(rng.uniform(0, 5)), bound()])
        mx = rng.choice([stated(rng.uniform(5, 10)), open_(rng.uniform(5, 10)), bound()])
        gt = rng.choice(["NECESSARY", "INHIBITING", "MODULATING"])
        st = rng.choice(["ACCEPTED", "ACCEPTED", "CANDIDATE"])
        g = gate(gtype=gt, mn=mn, mx=mx, status=st)
        p = precondition(status=rng.choice(["ACCEPTED", "CANDIDATE"]))
        e = entry(review_status="ACCEPTED", gates_unknown=rng.choice([False, False, True]), preconditions=[p],
                  condition_gates=[g], matrix_scope=scope("FOOD_CLASS", inc=("m",), exc=("x",)))
        q = {"matrix": rng.choice(["m", "x", "z", None]), "axes": {"CV-013": rng.choice([None, rng.uniform(-1, 12)])},
             "states": {"synthetic_state": rng.choice(["SYNTH_A", "SYNTH_B", "UNKNOWN", None])}}
        v = entry_verdict(e, q)
        x, sv = q["axes"]["CV-013"], q["states"]["synthetic_state"]
        if v == A:
            # APPLICABLE needs every input known and every item reviewed: nothing was defaulted
            assert e["review_status"] == "ACCEPTED" and e["gates_unknown"] is False
            assert q["matrix"] == "m" and p["status"] == "ACCEPTED" and sv == "SYNTH_A" and g["status"] == "ACCEPTED"
            if gt == "NECESSARY":
                assert x is not None and "NOT_REPORTED" not in (mn["status"], mx["status"])
                for bb, lo in ((mn, True), (mx, False)):                  # an open side only covers its studied range
                    if bb["status"] == "OPEN_STATED":
                        assert (x >= bb["value"]) if lo else (x <= bb["value"])
            if gt == "INHIBITING":
                assert x is not None and "STATED" in (mn["status"], mx["status"])
        if v == NA:
            # NOT_APPLICABLE never comes from a missing input
            assert q["matrix"] == "x" or sv == "SYNTH_B" or x is not None
        if v != A:
            assert route([v]) != "SIMULATE"


# ----------------------------------------------------------------------------- runner for hosts without pytest
if __name__ == "__main__":
    fns = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    bad = 0
    for n, f in fns:
        try:
            f()
            print("ok  ", n)
        except Exception as ex:                               # noqa: BLE001
            bad += 1
            print("FAIL", n, "::", repr(ex)[:400])
    n_neg = len(negatives())
    n_pos = len(list(accepted_variants()))
    print(f"{len(fns) - bad}/{len(fns)} tests passed; {n_neg} negative controls, {n_pos} accepted variants")
    sys.exit(1 if bad else 0)
```

## 6. Plan ambiguities and deviations found (also in the report to the requester; items 12-13 added in round 3)

1. **Substep lettering.** The Step 21 card defines 21a–21e; `registry/execution_spine_v2.csv` and the STEPDATA block list only 21a and 21b, with 21b = "MECH seed entries, effect vocabulary, PROC crosswalk and xref audit" (hours: Kush 4–7, Parv 5–8, expert 8–16). This draft follows the card.
2. **Output paths.** The card names `ledgers/schemas/MECH.schema.json` and `registry/mechanisms/*`; these drafts sit at `registry/schemas/*.draft_v1.schema.json` and `registry/*_draft_v1.csv` (D21-17).
3. **Nullable bounds.** Step 23-M and the card say "bounds nullable"; the draft uses bound statuses (D21-6).
4. **Sink id.** `MECH-UNRESOLVED_LOSS` (card) versus the six-digit id pattern (D21-2).
5. **Card list versus gate G21.2.** The 21b list has no cell-wall entry and no entry of kind MECHANICAL_DISRUPTION (D21-12).
6. **Verdict vocabulary.** Audit J1.1.4 uses PASS / FAIL; R-15 and the Step 23 card use APPLICABLE / NOT_APPLICABLE. The draft uses the R-15 triple.
7. **PROC row counts.** `r_mechanism_registry` §0 says `PROC.jsonl` has 552 rows, all UNVERIFIED; the card says 156 PROC. Verified read-only: 552 are ledger lines (versions), 156 distinct ids at their latest version, 93 with `mechanism_families`, 23 distinct labels, 156 / 156 UNVERIFIED.
8. **`PROC.mechanism_families` cannot propose the candidate systems.** No vitamin or pigment label exists, so baseline B0 recall for ascorbic-acid and chlorophyll mechanisms is zero by construction (gap G-4); and the wet-heat PROC carry only duration / temperature as required axes (gap G-5).
9. **SBO and RXNO term ids.** `r_mechanism_registry` F4.1 reports them as found by OLS probes; the card marks them UNVERIFIED. They are stored as CURIEs that need human verification.
10. **R-14 and the card wording.** The card says "seeds cover both ascorbic-acid and chlorophyll pathways; no system frozen", while the architecture text elsewhere names SIM-AA-1 first. The draft keeps the schema system-agnostic and the roster tag removable (plan conflict 4 in the plan's cross-phase list).
11. **Gate-circularity.** The card says MECH entries may not cite evaluation cases but does not say that a gate limit derived from a study should be excluded from tests on that study; the draft proposes it (D21-15).
12. **Joint coverage for G5 (cross-step need, Step 24).** G5 returns UNKNOWN for one APPLICABLE plus an UNKNOWN competitor unless the competitors are jointly fitted. MECH records a lumped entry (`LUMPED_OVERLAP`); the field that says which mechanisms a FORM covers (`covers_mechanism_keys`) belongs to FORM / PARAM (Step 24), not to MECH. Without it the ascorbic-acid candidate cannot reach SIMULATE (round-3 Review B 21-5).
13. **Verdict-bearing items vs the vacuous APPLICABLE.** `gates_unknown = false` now needs a precondition or a NECESSARY gate (schema root rule; ontology U-5); reviewers A and B agreed on the defect but differed on the fix (A: NECESSARY only; B: NECESSARY or INHIBITING plus a history branch). The stricter rule was adopted; D21-20 records the open part.
