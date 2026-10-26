# Step 04 v1.1 additive contracts and Step 01 / 02 registers — index

**Status of everything listed here: DRAFT_PENDING_H4.** Written 2026-10-26 on branch `plan/v2-reconciliation` under D-027 / Execution Plan v2 §7 ("exact next authorised implementation step": contract and documentation work only). Nothing is approved, frozen, signed or applied. Numeric values are PROPOSED_PILOT, except the seven Step-07 gate rows (THR-07A-01..07), which are `PROPOSED_VERBATIM_UNSIGNED` (the unchanged gate, values copied verbatim, unsigned). Every row of both registers carries `registry_status = DRAFT_PENDING_H4`. **Step 08 is not started and not authorised.**

**Revision r1 (2026-10-26, same day, still DRAFT_PENDING_H4):** the governance review A (28 findings) and the scientific review B (32 findings) were applied by a fixer pass; the finding-by-finding log (APPLIED / ADAPTED / REJECTED) is a scratch file outside the repo. Every threshold added or edited in r1 is PROPOSED_PILOT and unsigned; no existing gate was weakened. Review B's structural findings (hub collapse, UNKNOWN-independence leakage, lab group, KIN mandate, value scale / C0, temperature profiles) are in the contracts as PROPOSED rules with H4 items (§4).

## 1. Index

| Step | Path | Bytes | What it is |
|---|---|---|---|
| 04.1 | `reports/step04/lineage_contract_v1_1.md` | 52,079 | Entity chain SRC → DOC → STUDY → SEXP → SMP → OBS → AGG/DRV, non-destructive mapping, 9 typed LIN edge types with research justification, the three keys (+ lab group on the kinetic plane), hub rule, plane-qualified `split_group_id`, 21 leakage rules (L-04b, L-11b, L-19 added in r1), negative controls, open decisions D-1..D-17 |
| 04.1 | `registry/schemas/DOC.draft_v1_1.schema.json` | 13,934 | DOC schema draft (hub flag, authorship) |
| 04.1 | `registry/schemas/LIN.draft_v1_1.schema.json` | 14,223 | LIN schema draft (per-type node-pair rules incl. KIN / PARAM nodes, human-confirmation rule) |
| 04.1 | `registry/schemas/SEXP.draft_v1_1.schema.json` | 15,327 | SEXP schema draft (optional context; an absent key means UNKNOWN) |
| 04.1 | `registry/schemas/SMP.draft_v1_1.schema.json` | 16,523 | SMP schema draft (COOKING_MEDIUM role, material origin) |
| 04.1 / 04.2-min | `registry/schemas/OBS.draft_v1_1.schema.json` | 61,983 | OBS schema draft (n, dispersion type + n-basis, censoring + TRACE + LOD/LOQ, basis + raw, retention definition + evidence, method/platform ref, condition ref, digitisation record, `series_link`, `measurement_dedup`) |
| 04.1 (beyond the Plan §7 list; optional; presupposes the D-2 outcome) | `registry/schemas/AGG.draft_v1_1.schema.json` | 71,754 | AGG schema draft (membership screen status, PARTIAL rule) |
| 04.1 (beyond the Plan §7 list; optional; presupposes the D-2 outcome) | `registry/schemas/DRV.draft_v1_1.schema.json` | 47,163 | DRV schema draft (correlation assumption, lab fields with a KIN parent) |
| 04.3 | `reports/step04/kinetic_trajectory_contract_v1.md` | 33,744 | KIN / KINPT contract: guarantees, field tables, rules R04-1..16, endpoint-to-series link, SSOT field crosswalk, conformance tests K-1..16 |
| 04.3 | `registry/schemas/KIN.draft_v1.schema.json` | 86,589 | KIN (series header) schema draft (value scale / C0, temperature profiles, companion series, fit record, lab group) |
| 04.3 | `registry/schemas/KINPT.draft_v1.schema.json` | 33,494 | KINPT (one time point) schema draft (raw time units + separate seconds, tau status / range, replicate run ids) |
| 04.2-min | `reports/step04/04_2_min_value_documentation.md` | 24,125 | Minimal OBS value documentation; draft censoring_registry_v1_1, value_origin_registry_v1_1 and measurement_basis_registry_v1_1 content |
| 04.6-min | `reports/step04/04_6_min_data_plane_rules.md` | 14,123 | FW-09 / FW-11 / FW-12 / FW-15 + PQ-1; draft data_plane_registry_v1 (26 rows) |
| 04.9-min | `reports/step04/04_9_min_namespace_reservation.md` | 15,002 | Namespace reservation (13 prefixes + 7 proposed additions; `PARAM-` referenced), collision scan, baseline of existing prefixes |
| 01.6 | `registry/preregistered_thresholds_v1.csv` | 37,141 | 47 rows: 07.A (8: the verbatim gate THR-07A-01..07 as `PROPOSED_VERBATIM_UNSIGNED` + the provenance preconditions), 07I-C (12), 08a.0 (23), 04.3 (4); nothing signed |
| 02.4 | `registry/negative_results_register_v1.csv` | 21,741 | 30 rows seeded from the Step 02 list, figures re-checked by the agent against the cited reports (not human-verified) |
| 02.R-min | `reports/step02/r_min_08a_input_classification.md` | 13,307 | Presence / licence / environment record for every 08a input |
| archive | `reports/step07/v3_not_counted_archive/step07h_human_gate_result_v3_NOT_COUNTED.json` | 4,238 | Immutable byte copy of the v3 agreement output (mode 0444, sha256 `b1c856ba…` re-verified after the move). Moved from `reports/step07/archive/`, which is git-ignored (`.gitignore:35`) |
| archive | `reports/step07/v3_not_counted_archive/README.md` | 4,382 | sha256 of both files; the tool's hard-coded output path (X3); handling rule for 07.A |
| index | `reports/step04/README.md` | (this file) | this file |

Card outputs that are **not** created as files (their proposed content is embedded in the documents above, to be materialised after H4): `registry/lineage_edge_type_registry_v1.csv` and `registry/independence_key_contract_v1.csv` (lineage contract §3.1, §4.8), `registry/evidence_entity_model_v1.csv` (lineage contract §1.2), `registry/kinetic_series_schema_v1.csv` (kinetic contract §3–4), `registry/censoring_registry_v1_1.csv`, `registry/value_origin_registry_v1_1.csv` and `registry/measurement_basis_registry_v1_1.csv` (04.2-min §1a, §2–3), `registry/data_plane_registry_v1.csv` (04.6-min §3), `registry/namespace_registry_v1.csv` (04.9-min). Not drafted at all (outside the requested set): 01.1-min `plan_authority_map_v1_1.csv`, 03.3 clock registry, 04.8-min `schema_diff_proposal_v1.md` (due before Step 15), 02.6-min count definitions, 07I-S / 08b / 09 threshold rows.

## 2. What was and was not touched

- Created: only the files in the index, plus the directories `reports/step04/`, `reports/step02/`, `reports/step07/v3_not_counted_archive/` (revision r1 moved the archive there from the git-ignored `reports/step07/archive/`, a rename without content change; `.gitignore` was not edited).
- Not touched (by construction): every ledger row, every data file, every frozen artifact, every existing schema file (`ledgers/schemas/*`, `registry/schemas/condition_value_v1.schema.json`, `evd_export_v1.schema.json` keep their 2026-10-22 timestamps), tool code (`tools/step07_agreement.py` is hard-coded and was **not** edited), the SSOT, the packets, `DECISIONS.md`, `WORKLOG.md`, `STATUS.md`, tests. No pipeline was run over data; Step 08 was not started.
- Read-only lookups beyond the named documents: licence fields of three SRC rows (USDA R6, Bognár, Phenol-Explorer) and the id-minter state `ledgers/data/_ids.jsonl` (prefix counts only); `wc -l` / `stat` / `ls` of ledgers, exports and `data/raw` (existence only, no third-party file opened). In the first pass one read-only `git status` was run by mistake in a compound command (the brief said not to run git). Revision r1 used read-only git commands only (`log`, `show`, `status`, `check-ignore`) to verify NEG-0027 (commits e4045f4, c192b51, 5e91d38, d3339b9) and the first-commit anchor of the Step-07 gate (4e7db13); no git write command was issued, nothing was staged or committed, and no project tool or pipeline was run.

## 3. Validation performed, and the Mac contract test

- All 9 schema drafts parse (`python3 -I`), declare draft 2020-12, and keep `additionalProperties: false` on every nested object (checked by a structural test; the only open sub-schemas are `if` / `contains` matcher fragments) with the existing ledger envelope; no schema contains a `default` keyword.
- `jsonschema` is **not installed** on this server (nor pytest, pandas, pyarrow). A throw-away stdlib checker (scratch, not in the repo) implementing the JSON Schema subset the drafts use was run on 2026-10-26 after revision r1: the proposed test below through a shim of the same checker, **220 test cases (135 negative controls, 56 accepted variants, 29 structural checks), all as expected**; every new negative control was also checked to fail for its intended reason. Representative law cases: an UNKNOWN digitisation uncertainty is accepted and an uncertainty of 0 is rejected; a MEASURED 0 with censoring NOT_REPORTED / DETECTED / ROUNDED_INTERVAL is rejected and TRUE_ZERO with a basis note is accepted; a raw `week` / `month` / `year` time unit is accepted (and a month converted EXACTLY to seconds is rejected). This is evidence about the drafts' logic, **not** a substitute for the real validator.
- **A contract test should be added on the Mac.** Proposed content for `tests/contract/test_step04_draft_schemas.py` (not created here):

```python
"""Contract test for the Step 04.1 / 04.3 DRAFT schemas (status DRAFT_PENDING_H4).

PROPOSED content for tests/contract/test_step04_draft_schemas.py (not created in this step).
Run on the Mac:  /opt/anaconda3/bin/python -m pytest -q tests/contract/test_step04_draft_schemas.py
Needs jsonschema >= 4.18 (Draft 2020-12). Fixtures are SYNTHETIC SCHEMA FIXTURES: structure only, placeholder
strings and dummy numbers, never data. Nothing here reads a ledger.
"""
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "registry" / "schemas"
FILES = {
    "DOC": "DOC.draft_v1_1.schema.json", "LIN": "LIN.draft_v1_1.schema.json", "SEXP": "SEXP.draft_v1_1.schema.json",
    "SMP": "SMP.draft_v1_1.schema.json", "OBS": "OBS.draft_v1_1.schema.json", "AGG": "AGG.draft_v1_1.schema.json",
    "DRV": "DRV.draft_v1_1.schema.json", "KIN": "KIN.draft_v1.schema.json", "KINPT": "KINPT.draft_v1.schema.json",
}
Z = "SYNTHETIC-PLACEHOLDER"
NOW = "2026-10-26T00:00:00+00:00"


def load(name):
    return json.loads((SCHEMA_DIR / FILES[name]).read_text())


def errors(name, inst):
    return sorted(e.message for e in Draft202012Validator(load(name)).iter_errors(inst))


def env(prefix, n=1):
    return {"id": f"{prefix}-{n:06d}", "record_type": prefix, "schema_version": "1.1.0-draft", "version": 1, "status": "ACTIVE",
            "created_at": NOW, "created_by": "fixture", "provenance": {"method": "MANUAL", "source_ids": ["SRC-000001"]},
            "verification": {"status": "UNVERIFIED"}, "notes": "SYNTHETIC SCHEMA FIXTURE"}


DISP_NONE = {"type": "NONE_REPORTED", "value": None, "low": None, "high": None, "ci_level": None, "unit": None, "n_basis": "NOT_APPLICABLE",
             "scope": "NOT_APPLICABLE", "significance_raw": None, "derivation": "NOT_APPLICABLE"}
CENS_NR = {"kind": "NOT_REPORTED", "registry_id": "CS-007", "limit_low": None, "limit_high": None, "limit_unit": None,
           "limit_origin": "NOT_APPLICABLE", "resolution": None, "basis_note": None}
MEAS_NR = {"status": "NOT_REPORTED", "value": None, "unit": None}
CNT_NR = {"status": "NOT_REPORTED", "value": None}
LOC = {"doc_id": "DOC-000001", "locator_type": "TABLE_CELL", "page": None, "table_id": None, "row_label": None, "column_label": None,
       "figure_id": None, "char_span": None, "raw_text": Z}
METH_NR = {"status": "NOT_REPORTED", "method_id": None, "platform_family": None, "platform_raw": None}
DIG_OK = {"tool": "t", "tool_version": "1", "uncertainty": 0.1, "uncertainty_unit": "u", "uncertainty_status": "READ_FROM_TOOL",
          "uncertainty_type": "HALF_WIDTH", "axis_scale_x": "LINEAR", "axis_scale_y": "LINEAR", "calibration_points_raw": None,
          "digitizer": None, "n_reads": {"status": "NOT_REPORTED", "value": None}, "read_sd": {"status": "NOT_REPORTED", "value": None, "unit": None},
          "figure_locator": None}
DIG_UNKNOWN = {**DIG_OK, "uncertainty": None, "uncertainty_unit": None, "uncertainty_status": "UNKNOWN", "uncertainty_type": "UNKNOWN"}
SECONDS_NC = {"status": "NOT_CONVERTED", "value": None, "convention": None}
PROFILE_ISO = {"location": "MEDIUM", "clock": "PROCESS_TAU", "schedule_type": "ISOTHERMAL", "derivation": "AS_REPORTED",
               "uncertainty": DISP_NONE, "isothermal_value": {"status": "MEASURED", "value": 1.0, "unit": "u"}, "points": [],
               "raw_text": None, "condition_id": None}
COND_NR = {"status": "NOT_REPORTED", "condition_id": None}
AF = {"status": "NOT_REPORTED", "text": None}
MATRIX = {"ingredient_id": None, "raw_name": Z}
PROCESS = {"process_id": None, "raw_name": Z}
LIN_ASSIGNED = {"study_id": "STUDY-000001", "study_id_status": "PRESENT", "lineage_root_id": "LROOT-000001",
                "split_group_id": "SPLITGRP-EVD-000001", "independence_resolution": "STUDY", "assignment_status": "ASSIGNED",
                "rule_version": "fixture-rule-v0"}
LIN_AGG = {"study_id": None, "study_id_status": "NOT_IDENTIFIABLE", "lineage_root_id": "LROOT-000002",
           "split_group_id": "SPLITGRP-EVD-000002", "independence_resolution": "SOURCE_FAMILY_ONLY", "assignment_status": "ASSIGNED",
           "rule_version": "fixture-rule-v0",
           "parent_union": {"parent_lineage_root_ids": [], "parent_split_group_ids": [], "union_status": "PENDING"}}


def value_block():
    return {"value": {"status": "MEASURED", "value": 1.0, "unit": "u", "raw": Z}, "statistic": "UNKNOWN", "dispersion": copy.deepcopy(DISP_NONE),
            "censoring": copy.deepcopy(CENS_NR), "lod": copy.deepcopy(MEAS_NR), "loq": copy.deepcopy(MEAS_NR), "basis_id": "MB-008",
            "basis_raw": None, "retention_definition": "NOT_APPLICABLE", "retention_definition_evidence": "NOT_APPLICABLE", "method_indicator": "UNKNOWN", "method": copy.deepcopy(METH_NR),
            "condition_ref": copy.deepcopy(COND_NR), "value_origin": "UNKNOWN", "digitization": None, "licence_status": "UNKNOWN",
            "extraction_version": "fixture"}


def obs():
    o = env("OBS")
    o.update({"sample_id": "SMP-000001", "state_variable_id": "SVAR-000001", "analyte_raw_name": Z, "molecule_id": None,
              "analyte_form": copy.deepcopy(AF), "compartment": "UNKNOWN", "n_biological": copy.deepcopy(CNT_NR),
              "n_technical": copy.deepcopy(CNT_NR), "aggregation_level": "UNKNOWN", "locator": copy.deepcopy(LOC),
              "series_link": {"status": "UNKNOWN", "kinpt_id": None},
              "measurement_dedup": {"status": "UNKNOWN", "canonical_obs_id": None, "report_priority": None}})
    o.update(value_block())
    return o


def agg():
    a = env("AGG")
    a.update({"evidence_level": "AGG", "compiler_src_id": "SRC-000001", "state_variable_id": "SVAR-000001", "analyte_raw_name": Z,
              "molecule_id": None, "analyte_form": copy.deepcopy(AF), "matrix": copy.deepcopy(MATRIX), "process": copy.deepcopy(PROCESS),
              "aggregation_method": "UNKNOWN", "aggregation_level": "UNKNOWN", "member_lineage_status": "NOT_IDENTIFIABLE",
              "membership_screen_status": "NOT_SCREENED", "parent_ids": [],
              "n_members": copy.deepcopy(CNT_NR), "imputation": {"status": "POSSIBLE_NOT_ROW_IDENTIFIABLE", "donor_ids": [], "note": None},
              "locator": copy.deepcopy(LOC), "lineage": copy.deepcopy(LIN_AGG)})
    a.update(value_block())
    return a


def drv():
    r = env("DRV")
    r.update({"evidence_level": "DRV", "derived_quantity": "DELTA", "state_variable_id": "SVAR-000001", "formula_id": "FORMULA-FIXTURE",
              "formula_version": "0", "parent_ids": ["OBS-000001", "OBS-000002"],
              "value": {"status": "MEASURED", "value": 1.0, "unit": "u", "raw": None}, "dispersion": copy.deepcopy(DISP_NONE),
              "censoring": copy.deepcopy(CENS_NR),
              "uncertainty_propagation": {"status": "NOT_PROPAGATED_PARENT_UNCERTAINTY_UNKNOWN", "method": None,
                                          "correlation_assumption": "UNKNOWN", "shared_parent_set_id": None},
              "censor_propagation": "NOT_NEEDED_ALL_PARENTS_UNCENSORED", "basis_id": "MB-008", "retention_definition": "NOT_APPLICABLE",
              "retention_definition_evidence": "NOT_APPLICABLE",
              "value_origin": "DERIVED_DETERMINISTIC", "licence_status": "UNKNOWN",
              "lineage": {**copy.deepcopy(LIN_ASSIGNED), "parent_union": {"parent_lineage_root_ids": ["LROOT-000001"],
                                                                         "parent_split_group_ids": ["SPLITGRP-EVD-000001"],
                                                                         "union_status": "SINGLE_GROUP"}}})
    return r


def kin():
    k = env("KIN")
    k.update({"sexp_id": "SEXP-000001", "series_label_raw": None, "series_origin_form": "TABLE",
              "target": {"state_variable_id": "SVAR-000001", "analyte_raw_name": Z, "molecule_id": None, "analyte_form": copy.deepcopy(AF),
                         "compartment": "UNKNOWN", "basis_id": "MB-008", "basis_raw": None, "value_scale": "UNKNOWN",
                         "c0_reference": "NOT_REPORTED", "c0_obs_id": None},
              "matrix": copy.deepcopy(MATRIX), "reference_sample_id": None, "process": copy.deepcopy(PROCESS),
              "condition_profile": {"condition_grid_id": None, "grid_role": "SINGLE_SERIES", "condition_ids": [],
                                    "condition_status": "NOT_REPORTED", "normalizer_fingerprint_12": None,
                                    "temperature_status": "NOT_REPORTED", "temperature_profiles": [], "isothermality": "UNKNOWN",
                                    "initial_conditions": {"status": "NOT_REPORTED", "initial_concentration": None, "ph_initial": None,
                                                           "moisture_initial": None, "note": None}},
              "time_base": {"clock": "PROCESS_TAU", "unit": "UNKNOWN", "unit_raw": None, "t0_definition": "NOT_REPORTED",
                            "come_up_time": {"status": "NOT_REPORTED", "duration": None}, "note": None},
              "n_timepoints": 3,
              "replicate_structure": {"design": "UNKNOWN", "n_biological_per_timepoint": copy.deepcopy(CNT_NR),
                                      "n_technical_per_unit": copy.deepcopy(CNT_NR), "reporting": "UNKNOWN"},
              "companion_status": "NOT_REPORTED", "companion_series": [], "mass_balance_set_id": None,
              "censoring_summary": {"any_censored": "UNKNOWN", "kinds_present": [], "lod": copy.deepcopy(MEAS_NR), "loq": copy.deepcopy(MEAS_NR)},
              "method": copy.deepcopy(METH_NR), "k_level": {"value": "UNKNOWN", "scope": "UNKNOWN", "classifier_version": None},
              "fit": [], "evidence_tier": "E5", "locator": copy.deepcopy(LOC),
              "lineage": {**copy.deepcopy(LIN_ASSIGNED), "lab_group_id": None, "lab_group_status": "UNKNOWN", "lab_group_basis": "UNKNOWN"},
              "licence_status": "UNKNOWN", "extraction_version": "fixture"})
    return k


TAU_ZERO = {"clock": "PROCESS_TAU", "status": "DEFINITIONAL_ZERO", "value": 0, "low": None, "high": None, "unit": "UNKNOWN",
            "unit_raw": None, "derivation": "AS_REPORTED", "uncertainty": None, "uncertainty_unit": None, "uncertainty_type": None,
            "uncertainty_status": None, "normalised_seconds": SECONDS_NC}


def kinpt():
    p = env("KINPT")
    p.update({"kin_id": "KIN-000001", "sequence_index": 0,
              "tau": copy.deepcopy(TAU_ZERO),
              "point_role": "INITIAL", "replicate": {"status": "AGGREGATED_OVER_REPLICATES", "index": None, "unit_label": None,
                                                     "run_status": "UNKNOWN", "run_id": None},
              "obs_id": "OBS-000001", "paired_kinpt_ids": [],
              "temperature_at_point": {"status": "NOT_REPORTED", "value": None, "location": None},
              "digitized": {"status": "NO", "tool": None, "tool_version": None}})
    return p


def doc():
    d = env("DOC")
    d.update({"src_id": "SRC-000001", "snapshot_id": None, "sha256": "0" * 64, "doc_kind": "UNKNOWN", "content_access": "UNKNOWN",
              "report_kind": "UNKNOWN", "is_compilation_hub": "UNKNOWN",
              "authorship": {"status": "UNKNOWN", "authors_raw": [], "affiliations_raw": [], "corresponding_author_raw": None, "year_published": None},
              "version_label": "UNKNOWN", "identifiers": {}, "licence_status": "UNKNOWN",
              "storage_rule": "LOCAL_ONLY"})
    return d


def lin():
    e = env("LIN")
    e.update({"from_id": "DOC-000001", "to_id": "DOC-000002", "edge_type": "SAME_STUDY_AS", "detection_method": "DOI_MATCH",
              "detector_level": "B1", "score": 1.0, "edge_status": "PROVISIONAL", "reviewer": None, "rule_version": "fixture-rule-v0"})
    return e


def sexp():
    s = env("SEXP")
    s.update({"study_id": "STUDY-000001", "comparison_type": "UNKNOWN", "factors_varied": [], "reference_design": "NOT_REPORTED",
              "borrowed_reference_sample_ids": [], "condition_ids": [], "condition_status": "NOT_REPORTED", "protocol_locator": None})
    return s


def smp():
    s = env("SMP")
    s.update({"sexp_id": "SEXP-000001", "role": "UNKNOWN",
              "derived_from": {"status": "UNKNOWN", "sample_id": None, "process_id": None, "process_raw_name": None, "condition_id": None,
                               "condition_status": "NOT_REPORTED"},
              "matrix": copy.deepcopy(MATRIX), "pooled": "UNKNOWN",
              "material_origin": {"status": "UNKNOWN", "batch_label_raw": None, "cultivar_raw": None, "purchase_or_harvest_raw": None},
              "n_biological_units": copy.deepcopy(CNT_NR)})
    return s


BUILDERS = {"DOC": doc, "LIN": lin, "SEXP": sexp, "SMP": smp, "OBS": obs, "AGG": agg, "DRV": drv, "KIN": kin, "KINPT": kinpt}
HUMAN = {"status": "HUMAN_VERIFIED", "verifier": "Parv", "verified_at": NOW}


def _cens(**kw):
    return {**CENS_NR, **kw}


# (schema, label, mutator) -- every mutation must make the baseline INVALID
NEGATIVES = [
    ("OBS", "extra property", lambda o: o.update(foo=1)),
    ("OBS", "human verification by an AI name", lambda o: o.update(verification={**HUMAN, "verifier": "claude"})),
    ("OBS", "bad id", lambda o: o.update(id="OBS-12")),
    ("OBS", "UNKNOWN value carrying a number", lambda o: o.update(value={"status": "UNKNOWN", "value": 0, "unit": None})),
    ("OBS", "MEASURED without unit", lambda o: o.update(value={"status": "MEASURED", "value": 1.0, "unit": None})),
    ("OBS", "LT_LOD kind with a MEASURED value", lambda o: o.update(censoring=_cens(kind="LT_LOD", limit_high=1.0, limit_unit="u", limit_origin="STATED_IN_SOURCE"))),
    ("OBS", "CENSORED value with kind NOT_REPORTED", lambda o: o.update(value={"status": "CENSORED", "value": None, "unit": "u"})),
    ("OBS", "LT_LOD without a limit", lambda o: o.update(value={"status": "CENSORED", "value": None, "unit": "u"}, censoring=_cens(kind="LT_LOD", limit_origin="NOT_STATED"))),
    ("OBS", "TRUE_ZERO without basis note", lambda o: o.update(value={"status": "MEASURED", "value": 0, "unit": "u"}, censoring=_cens(kind="TRUE_ZERO"))),
    ("OBS", "TRUE_ZERO with a non-zero value", lambda o: o.update(value={"status": "MEASURED", "value": 2, "unit": "u"}, censoring=_cens(kind="TRUE_ZERO", basis_note="x"))),
    ("OBS", "ROUNDED_INTERVAL without resolution", lambda o: o.update(censoring=_cens(kind="ROUNDED_INTERVAL"))),
    ("OBS", "RANGE_ONLY with a MEASURED value", lambda o: o.update(censoring=_cens(kind="RANGE_ONLY"))),
    ("OBS", "SD without a value", lambda o: o.update(dispersion={**DISP_NONE, "type": "SD", "derivation": "AS_REPORTED"})),
    ("OBS", "CI without a level", lambda o: o.update(dispersion={**DISP_NONE, "type": "CI", "low": 1, "high": 2, "derivation": "AS_REPORTED"})),
    ("OBS", "NONE_REPORTED dispersion with a value", lambda o: o.update(dispersion={**DISP_NONE, "value": 1.0})),
    ("OBS", "n = 0", lambda o: o.update(n_biological={"status": "REPORTED", "value": 0})),
    ("OBS", "NOT_REPORTED n with a number", lambda o: o.update(n_technical={"status": "NOT_REPORTED", "value": 3})),
    ("OBS", "DIGITIZED without digitization", lambda o: o.update(value_origin="DIGITIZED")),
    ("OBS", "digitization on a MEASURED origin", lambda o: o.update(value_origin="MEASURED", digitization=copy.deepcopy(DIG_OK))),
    ("OBS", "method REFERENCED without an id", lambda o: o.update(method={**METH_NR, "status": "REFERENCED"})),
    ("OBS", "condition LINKED without an id", lambda o: o.update(condition_ref={"status": "LINKED", "condition_id": None})),
    ("OBS", "ratio basis with NOT_APPLICABLE retention", lambda o: o.update(basis_id="MB-007")),
    ("OBS", "locator without raw_text", lambda o: o["locator"].pop("raw_text")),
    ("AGG", "KNOWN member lineage with no parents", lambda a: a.update(member_lineage_status="KNOWN")),
    ("AGG", "NOT_IDENTIFIABLE with parents", lambda a: a.update(parent_ids=["OBS-000001"])),
    ("AGG", "recipe-plane split group", lambda a: a["lineage"].update(split_group_id="SPLITGRP-REC-000001")),
    ("AGG", "NOT_IDENTIFIABLE but resolution STUDY", lambda a: a["lineage"].update(independence_resolution="STUDY")),
    ("AGG", "ASSIGNED without rule_version", lambda a: a["lineage"].update(rule_version=None)),
    ("AGG", "PENDING with a resolution other than UNKNOWN", lambda a: a["lineage"].update(assignment_status="PENDING", lineage_root_id=None, split_group_id=None)),
    ("AGG", "assignment_status UNKNOWN is not in the vocabulary", lambda a: a["lineage"].update(assignment_status="UNKNOWN")),
    ("DRV", "SIM- parent", lambda r: r.update(parent_ids=["SIM-000001"])),
    ("DRV", "no parents", lambda r: r.update(parent_ids=[])),
    ("DRV", "computed value despite a censored parent", lambda r: r.update(censor_propagation="NOT_COMPUTED_CENSORED_PARENT")),
    ("DRV", "ENDPOINT_FROM_SERIES without a KIN parent", lambda r: r.update(derived_quantity="ENDPOINT_FROM_SERIES")),
    ("DRV", "non-derived value origin", lambda r: r.update(value_origin="MEASURED")),
    ("DRV", "parent union PENDING on an ASSIGNED row", lambda r: r["lineage"]["parent_union"].update(union_status="PENDING")),
    ("LIN", "ALTERNATE_OF between studies", lambda e: e.update(edge_type="ALTERNATE_OF", from_id="STUDY-000001", to_id="STUDY-000002")),
    ("LIN", "PRIMARY_SOURCE without membership_status", lambda e: e.update(edge_type="PRIMARY_SOURCE")),
    ("LIN", "HUMAN_CONFIRMED by an AI name", lambda e: e.update(edge_status="HUMAN_CONFIRMED", reviewer="Claude", reviewed_at=NOW)),
    ("LIN", "HUMAN_CONFIRMED without reviewed_at", lambda e: e.update(edge_status="HUMAN_CONFIRMED", reviewer="Kush")),
    ("LIN", "REJECTED without a reason", lambda e: e.update(edge_status="REJECTED")),
    ("LIN", "edge type outside the vocabulary", lambda e: e.update(edge_type="DUPLICATE_OF")),
    ("LIN", "score out of range", lambda e: e.update(score=1.5)),
    ("LIN", "MANUAL detection with detector B3", lambda e: e.update(detection_method="MANUAL", detector_level="B3")),
    ("LIN", "KIN node on an edge type that does not allow it", lambda e: e.update(edge_type="SAME_LAB_AS", from_id="KIN-000001")),
    ("SEXP", "BORROWED reference without ids", lambda s: s.update(reference_design="BORROWED_REFERENCE")),
    ("SEXP", "ids with NO_REFERENCE", lambda s: s.update(reference_design="NO_REFERENCE", borrowed_reference_sample_ids=["SMP-000001"])),
    ("SEXP", "REPORTED context item with no value", lambda s: s.update(context={"lid_covered": {"status": "REPORTED", "value_text": None, "value_number": None, "unit": None}})),
    ("SEXP", "condition LINKED without ids", lambda s: s.update(condition_status="LINKED")),
    ("SMP", "DERIVED without parent sample", lambda s: s["derived_from"].update(status="DERIVED")),
    ("SMP", "ROOT with a parent sample", lambda s: s["derived_from"].update(status="ROOT", sample_id="SMP-000002")),
    ("DOC", "bad sha256", lambda d: d.update(sha256="abc")),
    ("DOC", "identifiers missing", lambda d: d.pop("identifiers")),
    ("KIN", "single time point", lambda k: k.update(n_timepoints=1)),
    ("KIN", "PROJECT_FIT in the evidence plane", lambda k: k.update(fit=[_fit(fit_origin="PROJECT_FIT")])),
    ("KIN", "E4 without HUMAN_VERIFIED", lambda k: k.update(evidence_tier="E4")),
    ("KIN", "E6 tier in the evidence plane", lambda k: k.update(evidence_tier="E6")),
    ("KIN", "time_base without clock", lambda k: k["time_base"].pop("clock")),
    ("KIN", "historical clock", lambda k: k["time_base"].update(clock="HISTORICAL_T")),
    ("KIN", "grid member without grid id", lambda k: k["condition_profile"].update(grid_role="MEMBER_OF_GRID")),
    ("KIN", "programme with one point", lambda k: k["condition_profile"].update(temperature_status="REPORTED", temperature_profiles=[{**PROFILE_ISO, "schedule_type": "NON_ISOTHERMAL_PROGRAM", "isothermal_value": None, "points": [{"tau": 0, "tau_unit": "min", "tau_unit_raw": "min", "tau_seconds": SECONDS_NC, "T": {"status": "MEASURED", "value": 1.0, "unit": "u"}}]}])),
    ("KIN", "isothermal without a value", lambda k: k["condition_profile"].update(temperature_status="REPORTED", temperature_profiles=[{**PROFILE_ISO, "isothermal_value": None}])),
    ("KIN", "any_censored YES without kinds", lambda k: k["censoring_summary"].update(any_censored="YES")),
    ("KIN", "recipe-plane split group", lambda k: k["lineage"].update(split_group_id="SPLITGRP-REC-000001")),
    ("KINPT", "tau without clock", lambda p: p["tau"].pop("clock")),
    ("KINPT", "no obs_id", lambda p: p.pop("obs_id")),
    ("KINPT", "digitized tau without an uncertainty status", lambda p: p.update(tau={**TAU_ZERO, "status": "REPORTED", "value": 1, "unit": "min", "unit_raw": "min", "derivation": "DIGITIZED"})),
    ("KINPT", "digitized YES without tool", lambda p: p.update(digitized={"status": "YES", "tool": None, "tool_version": None})),
    ("KINPT", "individual replicate without index", lambda p: p.update(replicate={"status": "INDIVIDUAL_REPLICATE", "index": None})),

    # ---- review fixes (F1-F3, F12, F13, F21 and review B findings): record-level negatives
    ("OBS", "MEASURED zero with kind NOT_REPORTED (no 0 from an unreported value)", lambda o: o.update(value={"status": "MEASURED", "value": 0, "unit": "u"})),
    ("OBS", "MEASURED zero with kind DETECTED", lambda o: o.update(value={"status": "MEASURED", "value": 0, "unit": "u"}, censoring=_cens(kind="DETECTED"))),
    ("AGG", "MEASURED zero with kind NOT_REPORTED", lambda a: a.update(value={"status": "MEASURED", "value": 0, "unit": "u"})),
    ("AGG", "MEASURED zero with kind ROUNDED_INTERVAL", lambda a: a.update(value={"status": "MEASURED", "value": 0, "unit": "u"}, censoring=_cens(kind="ROUNDED_INTERVAL", resolution=0.05))),
    ("OBS", "DIGITIZED read uncertainty 0 (false precision)", lambda o: o.update(value_origin="DIGITIZED", digitization={**DIG_OK, "uncertainty": 0})),
    ("OBS", "DIGITIZED uncertainty_status UNKNOWN but a number given", lambda o: o.update(value_origin="DIGITIZED", digitization={**DIG_OK, "uncertainty_status": "UNKNOWN"})),
    ("OBS", "DIGITIZED READ_FROM_TOOL with null uncertainty", lambda o: o.update(value_origin="DIGITIZED", digitization={**DIG_OK, "uncertainty": None})),
    ("OBS", "DIGITIZED without uncertainty_status key", lambda o: o.update(value_origin="DIGITIZED", digitization={k: v for k, v in DIG_OK.items() if k != "uncertainty_status"})),
    ("AGG", "DIGITIZED read uncertainty 0", lambda a: a.update(value_origin="DIGITIZED", digitization={**DIG_OK, "uncertainty": 0})),
    ("OBS", "basis_raw missing (normalised basis without its raw)", lambda o: o.pop("basis_raw")),
    ("AGG", "basis_raw missing", lambda a: a.pop("basis_raw")),
    ("OBS", "LT_LOD with limit_high 0 (a zero limit is not a limit)", lambda o: o.update(value={"status": "CENSORED", "value": None, "unit": "u"}, censoring=_cens(kind="LT_LOD", limit_high=0, limit_unit="u", limit_origin="STATED_IN_SOURCE"))),
    ("OBS", "series_link LINKED_KINPT without kinpt_id", lambda o: o.update(series_link={"status": "LINKED_KINPT", "kinpt_id": None})),
    ("OBS", "series_link ENDPOINT_ONLY_SOURCE with a kinpt_id", lambda o: o.update(series_link={"status": "ENDPOINT_ONLY_SOURCE", "kinpt_id": "KINPT-000001"})),
    ("OBS", "series_link missing", lambda o: o.pop("series_link")),
    ("OBS", "TRACE with a MEASURED value", lambda o: o.update(censoring=_cens(kind="TRACE_BETWEEN_LOD_LOQ", limit_low=1.0, limit_high=2.0, limit_unit="u", limit_origin="STATED_IN_SOURCE"))),
    ("OBS", "TRACE without the LOQ (limit_high)", lambda o: o.update(value={"status": "CENSORED", "value": None, "unit": "u"}, censoring=_cens(kind="TRACE_BETWEEN_LOD_LOQ", limit_low=1.0, limit_unit="u", limit_origin="STATED_IN_SOURCE"))),
    ("OBS", "CV_PERCENT with a non-percent unit", lambda o: o.update(dispersion={**DISP_NONE, "type": "CV_PERCENT", "value": 5.0, "unit": "fraction", "n_basis": "NOT_REPORTED", "scope": "PER_VALUE", "derivation": "AS_REPORTED"})),
    ("OBS", "SE with n_basis NOT_APPLICABLE", lambda o: o.update(dispersion={**DISP_NONE, "type": "SE", "value": 0.1, "scope": "PER_VALUE", "derivation": "AS_REPORTED"})),
    ("OBS", "POOLED_SE with PER_VALUE scope", lambda o: o.update(dispersion={**DISP_NONE, "type": "POOLED_SE", "value": 0.1, "n_basis": "BIOLOGICAL", "scope": "PER_VALUE", "derivation": "AS_REPORTED"})),
    ("OBS", "NONE_REPORTED dispersion with n_basis BIOLOGICAL", lambda o: o.update(dispersion={**DISP_NONE, "n_basis": "BIOLOGICAL"})),
    ("OBS", "dispersion without n_basis key", lambda o: o["dispersion"].pop("n_basis")),
    ("OBS", "retention TRUE_MURPHY contradicts RT-002", lambda o: o.update(retention_definition="TRUE_MURPHY", retention_definition_evidence="STATED_IN_PRIMARY", retention_type_id="RT-002")),
    ("OBS", "NOT_APPLICABLE retention with a stated evidence", lambda o: o.update(retention_definition_evidence="STATED_IN_PRIMARY")),
    ("OBS", "card token TRUE is replaced by TRUE_MURPHY", lambda o: o.update(retention_definition="TRUE")),
    ("OBS", "DUPLICATE_OF_CANONICAL without canonical_obs_id", lambda o: o.update(measurement_dedup={"status": "DUPLICATE_OF_CANONICAL", "canonical_obs_id": None, "report_priority": 2})),
    ("OBS", "value unit_id MAPPED without an id", lambda o: o["value"].update(unit_id_status="MAPPED", unit_id=None)),
    ("AGG", "PARTIAL membership resolved at STUDY level", lambda a: (a.update(member_lineage_status="PARTIAL", parent_ids=["OBS-000001"]), a["lineage"].update(independence_resolution="STUDY", study_id="STUDY-000001", study_id_status="PRESENT"))),
    ("AGG", "PARTIAL membership without any known parent", lambda a: a.update(member_lineage_status="PARTIAL")),
    ("AGG", "membership_screen_status missing", lambda a: a.pop("membership_screen_status")),
    ("DOC", "REVIEW flagged as not a hub", lambda d: d.update(report_kind="REVIEW", is_compilation_hub="NO")),
    ("DOC", "PRIMARY_REPORT flagged as hub", lambda d: d.update(report_kind="PRIMARY_REPORT", is_compilation_hub="YES")),
    ("DOC", "authorship READ_FROM_DOCUMENT without authors", lambda d: d["authorship"].update(status="READ_FROM_DOCUMENT")),
    ("DOC", "authorship UNKNOWN carrying authors", lambda d: d["authorship"].update(authors_raw=["A. Author"])),
    ("DOC", "authorship missing", lambda d: d.pop("authorship")),
    ("LIN", "KIN node on SAME_STUDY_AS", lambda e: e.update(from_id="KIN-000001")),
    ("LIN", "PARAM node on SHARES_SAMPLES_WITH", lambda e: e.update(edge_type="SHARES_SAMPLES_WITH", from_id="PARAM-000001", to_id="STUDY-000002")),
    ("SMP", "material_origin REPORTED with no field", lambda s: s["material_origin"].update(status="REPORTED")),
    ("SMP", "material_origin missing", lambda s: s.pop("material_origin")),
    ("DRV", "KIN parent without lab group fields", lambda r: r.update(derived_quantity="ENDPOINT_FROM_SERIES", parent_ids=["KIN-000001"])),
    ("DRV", "SHARED_PARENT without shared_parent_set_id", lambda r: r["uncertainty_propagation"].update(correlation_assumption="SHARED_PARENT")),
    ("DRV", "INDEPENDENT_ASSUMED with a shared_parent_set_id", lambda r: r["uncertainty_propagation"].update(correlation_assumption="INDEPENDENT_ASSUMED", shared_parent_set_id="OBS-000001")),
    ("DRV", "BASIS_CONVERSION without a conversion-input parent", lambda r: r.update(derived_quantity="BASIS_CONVERSION")),
    ("KIN", "C0 from T0_SAMPLE without c0_obs_id", lambda k: k["target"].update(c0_reference="T0_SAMPLE")),
    ("KIN", "c0_obs_id given although C0 is NOT_REPORTED", lambda k: k["target"].update(c0_obs_id="OBS-000001")),
    ("KIN", "value_scale missing", lambda k: k["target"].pop("value_scale")),
    ("KIN", "temperature REPORTED without a profile", lambda k: k["condition_profile"].update(temperature_status="REPORTED")),
    ("KIN", "temperature NOT_REPORTED with a profile", lambda k: k["condition_profile"].update(temperature_profiles=[copy.deepcopy(PROFILE_ISO)])),
    ("KIN", "profile without a clock tag", lambda k: k["condition_profile"].update(temperature_status="REPORTED", temperature_profiles=[{x: y for x, y in PROFILE_ISO.items() if x != "clock"}])),
    ("KIN", "time_base OTHER unit without unit_raw", lambda k: k["time_base"].update(unit="OTHER")),
    ("KIN", "companion LINKED without a series", lambda k: k.update(companion_status="LINKED")),
    ("KIN", "mass_balance_set_id without LINKED companions", lambda k: k.update(mass_balance_set_id="MBSET-000001")),
    ("KIN", "lab_group ASSIGNED without an id", lambda k: k["lineage"].update(lab_group_status="ASSIGNED")),
    ("KIN", "lab group fields missing (mandatory on the kinetic plane)", lambda k: k["lineage"].pop("lab_group_status")),
    ("KIN", "fit with STATED input series but no ids", lambda k: k.update(fit=[_fit(input_kin_status="STATED")])),
    ("KIN", "fit without the new model_level key", lambda k: k.update(fit=[{x: y for x, y in _fit().items() if x != "model_level"}])),
    ("KINPT", "unit OTHER without unit_raw", lambda p: p["tau"].update(unit="OTHER")),
    ("KINPT", "month converted EXACTLY to seconds (calendar duration)", lambda p: p.update(tau={**_kinpt_tau()["tau"], "unit": "month", "unit_raw": "mo", "normalised_seconds": {"status": "CONVERTED_EXACT", "value": 15552000, "convention": None}})),
    ("KINPT", "convention-based conversion without the convention text", lambda p: p.update(tau={**_kinpt_tau()["tau"], "unit": "month", "unit_raw": "mo", "normalised_seconds": {"status": "CONVERTED_BY_STATED_CONVENTION", "value": 15552000, "convention": None}})),
    ("KINPT", "tau RANGE without low / high", lambda p: p["tau"].update(status="RANGE", value=None)),
    ("KINPT", "DEFINITIONAL_ZERO with a non-zero value", lambda p: p["tau"].update(value=5)),
    ("KINPT", "NOT_APPLICABLE_REFERENCE with a fabricated tau 0", lambda p: p["tau"].update(status="NOT_APPLICABLE_REFERENCE")),
    ("KINPT", "digitized tau READ_FROM_TOOL with uncertainty 0", lambda p: p.update(tau={**_kinpt_tau()["tau"], "derivation": "DIGITIZED", "uncertainty": 0, "uncertainty_unit": "wk", "uncertainty_type": "HALF_WIDTH", "uncertainty_status": "READ_FROM_TOOL"})),
    ("KINPT", "tau UNKNOWN uncertainty status with a number", lambda p: p.update(tau={**_kinpt_tau()["tau"], "derivation": "DIGITIZED", "uncertainty": 0.5, "uncertainty_unit": "wk", "uncertainty_type": "HALF_WIDTH", "uncertainty_status": "UNKNOWN"})),
    ("KINPT", "REPLICATE_RUNS without run_id", lambda p: p["replicate"].update(run_status="REPLICATE_RUNS")),
    ("KINPT", "paired_kinpt_ids missing", lambda p: p.pop("paired_kinpt_ids")),
]


def _mk(name, **kw):
    inst = BUILDERS[name]()
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(inst.get(k), dict) and k in ("lineage", "verification"):
            inst[k].update(v)
        else:
            inst[k] = v
    return inst


def _agg_pending():
    a = agg()
    a["lineage"].update(assignment_status="PENDING", lineage_root_id=None, split_group_id=None, independence_resolution="UNKNOWN", rule_version=None)
    return a


def _agg_unknown_train_only():
    a = agg()
    a["lineage"].update(independence_resolution="UNKNOWN")
    return a


def _obs(**kw):
    o = obs()
    o.update(kw)
    return o


def _drv(**kw):
    r = drv()
    r.update(kw)
    return r


def _kin_grid():
    k = kin()
    k["condition_profile"].update(grid_role="MEMBER_OF_GRID", condition_grid_id="CGRID-000001", temperature_status="REPORTED",
                                  temperature_profiles=[copy.deepcopy(PROFILE_ISO)], isothermality="PRODUCT_ISOTHERMAL_STATED")
    return k


def _fit(**kw):
    f = {"fit_origin": "AUTHOR_REPORTED", "candidate_model_family": "UNKNOWN", "equation_raw": None, "model_level": "UNKNOWN",
         "scope": "UNKNOWN", "input_kin_status": "UNKNOWN", "input_kin_ids": [], "fit_method": "UNKNOWN",
         "n_points_used": copy.deepcopy(CNT_NR), "temperature_basis": "UNKNOWN", "parameter_covariance": {"status": "NOT_REPORTED", "raw": None},
         "parameters": [], "fit_diagnostics": [], "effective_or_mechanistic": "UNKNOWN", "identifiability_status": "UNKNOWN",
         "valid_domain": {"temperature_range_note": None, "matrix_scope_note": None}, "fit_locator": None}
    f.update(kw)
    return f


LAB_OK = {"lab_group_id": "LABGRP-000001", "lab_group_status": "ASSIGNED", "lab_group_basis": "MANUAL"}
LAB_UNKNOWN = {"lab_group_id": None, "lab_group_status": "UNKNOWN", "lab_group_basis": "UNKNOWN"}


def _kinpt_tau(**kw):
    p = kinpt()
    p["tau"] = {**TAU_ZERO, "status": "REPORTED", "value": 6, "unit": "week", "unit_raw": "wk", **kw}
    return p


def _drv_kin(**kw):
    r = drv()
    r.update(derived_quantity="ENDPOINT_FROM_SERIES", parent_ids=["KIN-000001", "KINPT-000003"])
    r["lineage"].update(kw or LAB_UNKNOWN)
    return r


# accepted variants that must stay valid
POSITIVES = [
    ("OBS", "left-censored LT_LOD", lambda: _obs(value={"status": "CENSORED", "value": None, "unit": "u", "raw": "<LOD"}, censoring=_cens(kind="LT_LOD", limit_high=1.0, limit_unit="u", limit_origin="STATED_IN_SOURCE", registry_id="CS-003"))),
    ("OBS", "TRUE_ZERO with basis", lambda: _obs(value={"status": "MEASURED", "value": 0, "unit": "u", "raw": "0"}, censoring=_cens(kind="TRUE_ZERO", basis_note="zero stated by the source"))),
    ("OBS", "ROUNDED_INTERVAL", lambda: _obs(censoring=_cens(kind="ROUNDED_INTERVAL", resolution=0.05, registry_id="CS-008"))),
    ("OBS", "DIGITIZED with tool", lambda: _obs(value_origin="DIGITIZED", digitization=copy.deepcopy(DIG_OK),
                                                dispersion={**DISP_NONE, "type": "SD", "value": 0.1, "n_basis": "NOT_REPORTED", "scope": "PER_VALUE", "derivation": "DIGITIZED"})),
    ("AGG", "pending lineage", _agg_pending),
    ("AGG", "ASSIGNED ids with UNKNOWN resolution (train-only)", _agg_unknown_train_only),
    ("DRV", "endpoint from series (lab group UNKNOWN is a valid answer)", _drv_kin),
    ("DRV", "not computed from a censored parent", lambda: _drv(censor_propagation="NOT_COMPUTED_CENSORED_PARENT", value={"status": "UNKNOWN", "value": None, "unit": None})),
    ("LIN", "PRIMARY_SOURCE agg -> doc, membership known", lambda: {**lin(), "edge_type": "PRIMARY_SOURCE", "from_id": "AGG-000001", "to_id": "DOC-000001", "membership_status": "KNOWN"}),
    ("LIN", "human-confirmed edge", lambda: {**lin(), "edge_status": "HUMAN_CONFIRMED", "reviewer": "Kush", "reviewed_at": NOW}),
    ("SEXP", "context items", lambda: {**sexp(), "context": {"lid_covered": {"status": "REPORTED", "value_text": "lid on", "value_number": None, "unit": None}, "start_mode": {"status": "NOT_REPORTED"}}}),
    ("KIN", "E4 human verified", lambda: {**kin(), "evidence_tier": "E4", "verification": HUMAN}),
    ("KIN", "grid member, isothermal", _kin_grid),
    # ---- review fixes: accepted variants
    ("OBS", "DIGITIZED with UNKNOWN read uncertainty (UNKNOWN is not forced to a number)", lambda: _obs(value_origin="DIGITIZED", digitization=copy.deepcopy(DIG_UNKNOWN))),
    ("AGG", "DIGITIZED with UNKNOWN read uncertainty", lambda: {**agg(), "value_origin": "DIGITIZED", "digitization": copy.deepcopy(DIG_UNKNOWN)}),
    ("OBS", "ND with an unknown limit (no 0)", lambda: _obs(value={"status": "CENSORED", "value": None, "unit": "u", "raw": "ND"}, censoring=_cens(kind="ND", registry_id="CS-002", limit_origin="NOT_STATED"))),
    ("OBS", "TRACE between LOD and LOQ", lambda: _obs(value={"status": "CENSORED", "value": None, "unit": "u", "raw": "tr"}, censoring=_cens(kind="TRACE_BETWEEN_LOD_LOQ", registry_id="CS-011", limit_low=0.1, limit_high=0.5, limit_unit="u", limit_origin="STATED_IN_SOURCE"))),
    ("OBS", "cap kept as printed together with the rounding resolution", lambda: _obs(value={"status": "CENSORED", "value": None, "unit": "%", "raw": "100"}, censoring=_cens(kind="GT_CAP", registry_id="CS-005", limit_low=100, limit_unit="%", limit_origin="FROM_CAP_RULE", resolution=5))),
    ("OBS", "CV_PERCENT", lambda: _obs(dispersion={**DISP_NONE, "type": "CV_PERCENT", "value": 5.0, "unit": "%", "n_basis": "NOT_REPORTED", "scope": "PER_VALUE", "derivation": "AS_REPORTED"})),
    ("OBS", "POOLED_SE for a whole table with significance letters", lambda: _obs(dispersion={**DISP_NONE, "type": "POOLED_SE", "value": 0.2, "n_basis": "BIOLOGICAL", "scope": "POOLED_TABLE", "significance_raw": "a b c", "derivation": "AS_REPORTED"})),
    ("OBS", "apparent retention on a dry basis (RT-002)", lambda: _obs(basis_id="MB-007", retention_definition="APPARENT_DRY_BASIS", retention_definition_evidence="STATED_IN_PRIMARY", retention_type_id="RT-002")),
    ("OBS", "true retention stated in a secondary source (Phenol-Explorer RT-003)", lambda: _obs(basis_id="MB-007", retention_definition="TRUE_MURPHY", retention_definition_evidence="STATED_IN_SECONDARY", retention_type_id="RT-003")),
    ("OBS", "series_link LINKED_KINPT", lambda: _obs(series_link={"status": "LINKED_KINPT", "kinpt_id": "KINPT-000001"})),
    ("OBS", "definitional normalisation point (t0 = 1 by construction)", lambda: _obs(value_origin="DEFINITIONAL_NORMALISATION")),
    ("OBS", "duplicate report of a canonical measurement", lambda: _obs(measurement_dedup={"status": "DUPLICATE_OF_CANONICAL", "canonical_obs_id": "OBS-000009", "report_priority": 2})),
    ("OBS", "raw unit with a mapped unit id", lambda: _obs(value={"status": "MEASURED", "value": 1.0, "unit": "mg/100 g", "raw": "1.0", "unit_id": "UNIT-000001", "unit_id_status": "MAPPED"})),
    ("AGG", "PARTIAL membership at source-family level", lambda: (lambda a: (a.update(member_lineage_status="PARTIAL", parent_ids=["OBS-000001"]), a)[1])(agg())),
    ("DOC", "REVIEW hub with authorship read", lambda: {**doc(), "report_kind": "REVIEW", "is_compilation_hub": "YES", "authorship": {"status": "FROM_METADATA_RECORD", "authors_raw": ["A. Author"], "affiliations_raw": ["Univ X"], "corresponding_author_raw": "A. Author", "year_published": 2005}}),
    ("LIN", "re-plotted series: QUOTES_VALUES_FROM KIN -> KIN", lambda: {**lin(), "edge_type": "QUOTES_VALUES_FROM", "from_id": "KIN-000002", "to_id": "KIN-000001", "detection_method": "NUMERIC_FINGERPRINT", "detector_level": "B3"}),
    ("LIN", "compendium re-reports a parameter: QUOTES_VALUES_FROM PARAM -> DOC", lambda: {**lin(), "edge_type": "QUOTES_VALUES_FROM", "from_id": "PARAM-000001", "to_id": "DOC-000001"}),
    ("LIN", "SAME_STUDY_AS between a held DOC and a cited-only SRC", lambda: {**lin(), "from_id": "DOC-000001", "to_id": "SRC-000002"}),
    ("SMP", "cooking-medium sample with material origin", lambda: {**smp(), "role": "COOKING_MEDIUM", "material_origin": {"status": "REPORTED", "batch_label_raw": "lot 7", "cultivar_raw": None, "purchase_or_harvest_raw": None}}),
    ("DRV", "SHARED_PARENT correlation with a set id", lambda: (lambda r: (r["uncertainty_propagation"].update(correlation_assumption="SHARED_PARENT", shared_parent_set_id="OBS-000001"), r)[1])(drv())),
    ("DRV", "BASIS_CONVERSION with a moisture parent", lambda: _drv(derived_quantity="BASIS_CONVERSION", parent_roles=[{"parent_id": "OBS-000001", "role": "BEFORE"}, {"parent_id": "OBS-000002", "role": "MOISTURE_CORRECTION"}])),
    ("DRV", "apparent retention on fresh weight", lambda: _drv(derived_quantity="APPARENT_RETENTION_FW", retention_definition="APPARENT_FRESH_BASIS", retention_definition_evidence="INFERRED_FROM_FORMULA")),
    ("KIN", "relative scale with C0 from the t0 sample", lambda: (lambda k: (k["target"].update(value_scale="RELATIVE_TO_C0", c0_reference="T0_SAMPLE", c0_obs_id="OBS-000001"), k)[1])(kin())),
    ("KIN", "medium + core profiles, product isothermal stated", lambda: (lambda k: (k["condition_profile"].update(temperature_status="REPORTED", isothermality="COME_UP_SIGNIFICANT", temperature_profiles=[copy.deepcopy(PROFILE_ISO), {**PROFILE_ISO, "location": "CORE", "derivation": "DIGITIZED"}]), k)[1])(kin())),
    ("KIN", "raw week time axis", lambda: (lambda k: (k["time_base"].update(unit="week", unit_raw="weeks"), k)[1])(kin())),
    ("KIN", "OTHER time axis with the printed label", lambda: (lambda k: (k["time_base"].update(unit="OTHER", unit_raw="cycles"), k)[1])(kin())),
    ("KIN", "tissue + cooking-medium companion with a mass-balance set", lambda: {**kin(), "companion_status": "LINKED", "companion_series": [{"kin_id": "KIN-000002", "role": "COOKING_MEDIUM_CONC"}], "mass_balance_set_id": "MBSET-000001"}),
    ("KIN", "lab group ASSIGNED", lambda: (lambda k: (k["lineage"].update(**LAB_OK), k)[1])(kin())),
    ("KIN", "grid-level secondary Arrhenius fit with its input series", lambda: {**kin(), "fit": [_fit(model_level="SECONDARY_ARRHENIUS", scope="CONDITION_GRID", input_kin_status="STATED", input_kin_ids=["KIN-000001", "KIN-000002"], fit_method="LINEARISED_LN", temperature_basis="SETPOINT")]}),
    ("KIN", "per-series context override", lambda: {**kin(), "context_override": {"lid_covered": {"status": "REPORTED", "value_text": "lid on", "value_number": None, "unit": None}}}),
    ("KINPT", "raw 'week' unit, printed label kept, seconds exact", lambda: {**_kinpt_tau(), "tau": {**_kinpt_tau()["tau"], "normalised_seconds": {"status": "CONVERTED_EXACT", "value": 3628800, "convention": None}}}),
    ("KINPT", "raw 'month' unit stays NOT_CONVERTED", lambda: _kinpt_tau(unit="month", unit_raw="mo")),
    ("KINPT", "raw 'month' converted only by a stated convention", lambda: _kinpt_tau(unit="month", unit_raw="mo", normalised_seconds={"status": "CONVERTED_BY_STATED_CONVENTION", "value": 15552000, "convention": "1 month = 30 d"})),
    ("KINPT", "raw 'year' unit", lambda: _kinpt_tau(unit="year", unit_raw="y")),
    ("KINPT", "OTHER unit with the printed label", lambda: _kinpt_tau(unit="OTHER", unit_raw="cycles")),
    ("KINPT", "tau range", lambda: _kinpt_tau(status="RANGE", value=None, low=10, high=12, unit="min", unit_raw="min")),
    ("KINPT", "untreated reference with no defined tau", lambda: _kinpt_tau(status="NOT_APPLICABLE_REFERENCE", value=None, unit="UNKNOWN", unit_raw=None)),
    ("KINPT", "digitized tau with UNKNOWN read uncertainty", lambda: _kinpt_tau(derivation="DIGITIZED", uncertainty_status="UNKNOWN")),
    ("KINPT", "digitized tau with a read uncertainty", lambda: _kinpt_tau(derivation="DIGITIZED", uncertainty=0.5, uncertainty_unit="wk", uncertainty_type="HALF_WIDTH", uncertainty_status="READ_FROM_TOOL")),
    ("KINPT", "replicate run and stable unit label", lambda: (lambda p: (p["replicate"].update(status="INDIVIDUAL_REPLICATE", index=1, unit_label="pot A", run_status="REPLICATE_RUNS", run_id="run-2"), p)[1])(kinpt())),
    ("KIN", "author-reported fit with a parameter and a typed uncertainty", lambda: {**kin(), "fit": [_fit(parameters=[{"name": "k", "symbol": "k", "value": {"status": "MEASURED", "value": 0.1, "unit": "1/min"}, "uncertainty": {**DISP_NONE, "type": "SE", "value": 0.01, "n_basis": "NOT_REPORTED", "scope": "PER_VALUE", "derivation": "AS_REPORTED"}, "valid_range_note": None}], parameter_covariance={"status": "REPORTED", "raw": "r(k,Ea) = -0.97"})]}),
    ("KIN", "non-isothermal programme with a digitised core profile (two points, each with a clock-tagged unit)", lambda: (lambda k: (k["condition_profile"].update(temperature_status="REPORTED", isothermality="NON_ISOTHERMAL", temperature_profiles=[{**PROFILE_ISO, "location": "CORE", "schedule_type": "NON_ISOTHERMAL_PROGRAM", "derivation": "DIGITIZED", "isothermal_value": None, "points": [{"tau": 0, "tau_unit": "min", "tau_unit_raw": "min", "tau_seconds": SECONDS_NC, "T": {"status": "MEASURED", "value": 20.0, "unit": "degC"}}, {"tau": 5, "tau_unit": "min", "tau_unit_raw": "min", "tau_seconds": SECONDS_NC, "T": {"status": "MEASURED", "value": 90.0, "unit": "degC"}}]}]), k)[1])(kin())),
    ("AGG", "screened compilation with KNOWN members", lambda: (lambda a: (a.update(member_lineage_status="KNOWN", membership_screen_status="BIBLIOGRAPHY_SCREENED", parent_ids=["OBS-000001"]), a)[1])(agg())),
]


@pytest.mark.parametrize("name", sorted(FILES))
def test_schema_is_valid_draft_2020_12(name):
    s = load(name)
    Draft202012Validator.check_schema(s)
    assert s["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert "DRAFT_PENDING_H4" in s["title"]
    assert s["additionalProperties"] is False


@pytest.mark.parametrize("name", sorted(FILES))
def test_baseline_instance_is_valid(name):
    assert errors(name, BUILDERS[name]()) == []


@pytest.mark.parametrize("name,label,make", [(n, l, m) for n, l, m in POSITIVES], ids=[f"{n}:{l}" for n, l, _ in POSITIVES])
def test_accepted_variants(name, label, make):
    assert errors(name, make()) == []


@pytest.mark.parametrize("name,label,mutate", NEGATIVES, ids=[f"{n}:{l}" for n, l, _ in NEGATIVES])
def test_negative_controls_are_rejected(name, label, mutate):
    inst = BUILDERS[name]()
    mutate(inst)
    assert errors(name, inst), f"{name}: '{label}' should be rejected"


def test_existing_schemas_are_untouched_by_the_drafts():
    # the drafts are additive: no draft may redefine an id pattern of an existing ledger
    for name, fname in FILES.items():
        s = load(name)
        assert s["$id"].startswith("culinarystate/draft/")


def test_no_cross_plane_split_group_in_evidence_drafts():
    for name in ("AGG", "DRV", "KIN"):
        pat = load(name)["$defs"]["lineage"]["properties"]["split_group_id"]["anyOf"][0]["pattern"]
        assert pat == r"^SPLITGRP-EVD-\d{6}$"


def _walk(node, path=""):
    """Yield (path, schema-dict) for every sub-schema except matcher fragments under if / contains / not."""
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            if k in ("if", "contains", "not"):
                continue
            yield from _walk(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}[{i}]")


@pytest.mark.parametrize("name", sorted(FILES))
def test_nested_objects_are_closed_and_nothing_defaults(name):
    for path, sub in _walk(load(name)):
        if sub.get("type") == "object" and "properties" in sub:
            assert sub.get("additionalProperties") is False, f"{name}{path} is an open object"
        assert "default" not in sub or path.endswith("/properties/default"), f"{name}{path}: a 'default' keyword (UNKNOWN is never defaulted)"
```

## 4. Checklist: human decisions needed (Kush, Parv; H4 unless stated)

Order follows the Step 08 preconditions: (i) 04.1 + 04.2-min + 04.6-min + 04.9-min approved (H4); (ii) 08a.0 pre-registration signed and registered in 01.6; (iii) 02.R-min names the execution environment; (iv) Kush's explicit written authorisation.

**A. Approvals (precondition i)**
- [ ] 04.1 lineage contract and 7 schema drafts: entity chain; the 9 edge types and their merge classes (D-1, D-4, D-8..D-10 in the lineage contract); DOC mint key `<src_id>|sha256:<hex>` (D-11).
- [ ] **Hub rule (D-12)**: compilation / review / database hubs never connect their primaries (per-record edges, locator DOC not a structural edge, hub DOC never in `STUDY.report_doc_ids`); KNOWN-member AGG never evaluated and trains only if no member is held out; shared-input DRV merge kept as the primary analysis with a sensitivity run. This narrows the card's blanket "parent union of every AGG" for hubs only (DRV parent union and G08-2 unchanged).
- [ ] **UNKNOWN-independence leakage (D-5 + D-13)**: UNKNOWN stays TRAIN-only and gets the L-04b recall-oriented near-duplicate screen plus a sensitivity run without UNKNOWN rows; the screen threshold value is OPEN (THR-08A-19).
- [ ] **Giant-component refinement (D-14, THR-08A-20)**: evaluation-eligible pool + Kish n_eff ≥ K (K = 10) + largest share ≤ 0.40, evaluated once on the frozen rule_version, side by side with the unchanged card rule (the weaker label wins).
- [ ] **Lab group (D-15)**: `lab_group_id` mandatory (status UNKNOWN allowed) for KIN and DRV with a KIN parent; `DOC.authorship`; SAME_LAB_AS rule with N OPEN (THR-08A-22); accept or decline the prefixes `LABGRP-`, `MBSET-`.
- [ ] AGG / DRV as export-v2 views (default) or separate ledgers (D-2). The AGG and DRV schema drafts are beyond the Plan §7 list, optional, and presuppose the D-2 outcome.
- [ ] 04.2-min field set and enumerations: unmapped ledger censor tokens `GT_ULOQ`, `GT_STATED`, `LT_STATED` (proposed CS-012..014); CS-011 TRACE_BETWEEN_LOD_LOQ; cap + resolution vs a `kinds[]` list; **`retention_definition` split** with an evidence field instead of the card's TRUE / APPARENT / YIELD_ADJUSTED (D-16); proposed measurement bases MB-009..011 and the alias settlements; the digitisation record and the two-read rule; `lod` / `loq` on OBS; `measurement_dedup` and `series_link` on OBS.
- [ ] `SEXP.context`: an absent key means UNKNOWN (draft) vs NOT_REPORTED (plan card) (D-17, A-12).
- [ ] 04.6-min six-plane codes; rule PQ-1; DOC plane (P-SRC vs P-EVD); `ESTIMATED_FROM_SUMMARY` never a label / test value.
- [ ] 04.9-min: reserve the 13 prefixes; accept or decline `LROOT-`, `CGRID-`, `DFORM-`, `LABGRP-`, `MBSET-`, `THR-`, `NEG-` (`PARAM-` is referenced, not proposed); ratify the `split_group_id` homonym rule (X1); confirm no `KINETIC-` prefix is intended.
- [ ] How approved drafts enter `ledgers/schemas/`: they are generated from `src/culinarystate/ledgers/registry.py` by `tools/export_schemas.py`, and the minter refuses prefixes not in `R`; copying files would be overwritten (D-6, CHG-04-7).
- [ ] 04.3 (needed before Step 09 freezes any KIN / KINPT file, not before 08a): AUTHOR_REPORTED-only fits; parameter-only reports (A-2); K-level scope; `CGRID-`; PROCESS_TAU-only clock until 03.3 is approved; raw time units week / month / year (A-9); UNKNOWN uncertainty spelled UNKNOWN (A-10); value scale / C0, temperature profiles with isothermality, companion series, richer fit records (A-13); two independent digitiser reads for TEST / SIM-VAL (A-14).

**B. Threshold pre-registration (precondition ii) — `registry/preregistered_thresholds_v1.csv`**
- [ ] Record, before any v4 label exists, how prevalence-only critical-field flags are discharged (the plan card proposes: adjudicate every flagged field, kappa stays computed on the original independent labels) — THR-07A-06; a clarification, not a gate change, and NOT decided by the draft.
- [ ] Confirm that the 7 `PROPOSED_VERBATIM_UNSIGNED` rows are the unchanged Step-07 gate (THR-07A-01..07); decide the added provenance preconditions (THR-07A-08, PROPOSED_PILOT). Only after Kush sets `signed_by` / `signed_at` may a gate row become `PREREGISTERED_<date>`.
- [ ] 07I-C: label mapping to Y_copy / Y_dish / UNCERTAIN, binary kappa target, OP-MERGE / OP-SPLIT selection rules (agent drafts; the card gives only the numbers 0.70 / 0.90 / 0.95, the sealed-packet sizes and the principle) — THR-07IC-01..12.
- [ ] 08a.0: 23 rows. The card rows THR-08A-01..15 (giant-component 40% sits next to the B0 shares 39.0% / 39.4%; audit size; pooled precision) are unchanged. Review-B additions to decide: per-stratum precision (THR-08A-16), seeded-copy recall per perturbation class with n and Wilson bound (THR-08A-17), natural-duplicate recall estimate (THR-08A-18), UNKNOWN screen (THR-08A-19, value OPEN), giant-component refinement (THR-08A-20), hub rule sensitivity (THR-08A-21), SAME_LAB_AS / N (THR-08A-22, N OPEN), membership screen label (THR-08A-23).
- [ ] `data_seen_before_registration`: the 08a.0 rows carry `DESCRIPTIVE_COUNTS_SEEN` (the B0 group counts were known to the drafter; no lineage component, edge or label was computed). Decide whether that token satisfies the Step 01.6 rule "a gate may run only if its row exists with data_seen_before_registration = N", or whether N must be restored by a different signer.
- [ ] 04.3: minimum distinct numeric times that make a KIN mandatory — **edited from 3 to 2** (THR-04K-01, PROPOSED_PILOT, unsigned; history and reasons in the row); ≥ 3 stays the K1 label (THR-04K-02); digitiser reads (THR-04K-03); verification of the mandate by the second extractor (THR-04K-04).
- [ ] Sign (set `signed_by` / `signed_at`) or change each PROPOSED_PILOT value; none is signed. Rows for 07I-S, 08b and 09 are still to be registered before those steps start (Step 01 card).

**C. Environment and authorisation (preconditions iii, iv)**
- [ ] Execution environment for 08a / 08b / 07I-S: this server (CPU-only, stdlib Python only, no pytest / jsonschema) vs the Mac vs another approved environment (`reports/step02/r_min_08a_input_classification.md` §4). If the Mac: compare ledger hashes with this clone first (D-026 exists only there). Record the decision in DECISIONS.
- [ ] Baseline sha256 of the seven ledger files recorded before any 08a write (none found for STUDY and SNAP).
- [ ] Whether `registry/data_source_acquisition_manifest_v1_1.csv` (planned 06.3-min) is a hidden precondition of 08a or v1 suffices.
- [ ] Real DECISIONS ids for the rulings and registries (D-026 clash; X17).
- [ ] Kush's explicit written authorisation of 08a.

**D. Registers**
- [ ] Negative-results register: accept row ids `NEG-####` (not `NR-`, the notation-rule prefix) and the status vocabulary (`RECORDED_AGENT_CHECKED*`, `SUPERSEDED_KEPT`; `HUMAN_CHECKED` is for Kush or Parv only). NEG-0027 (linker kappa 0.13) is now backed by git history (commit e4045f4) and recorded as SUPERSEDED_KEPT by the final 0.500 file (NEG-0025); the provenance caution about the earlier Parv files is part of the row.
- [ ] Archive: keep the original v3 file at the hard-coded path (done) or remove it once the archive is accepted; choose the post-run handling (archive README); confirm the archive location `reports/step07/v3_not_counted_archive/` (moved out of the git-ignored `archive/`) or prefer the plan's path `reports/step07/step07h_human_gate_result_v3_NOT_COUNTED.json`.

## 5. Register conventions

- `registry/negative_results_register_v1.csv`: columns `result_id, registry_status, claim_tested, data_version, split, metric, value, ci, source_path, consequence, status, recorded_at`. `registry_status = DRAFT_PENDING_H4` on every row. Append-only **once committed** (the file is uncommitted, so r1 corrected rows in place); afterwards rows are never edited, and a correction or supersession is a new row that cites the old `result_id` (NEG-0014 cites NEG-0013). `status` ∈ RECORDED_AGENT_CHECKED (figure re-read by the agent against the cited report on 2026-10-26; **not human-verified**), RECORDED_AGENT_CHECKED_CAUSE_UNKNOWN, RECORDED_AGENT_CHECKED_FROM_PROTOCOL_AND_DECISIONS, SUPERSEDED_KEPT (original number kept with the supersession note), UNVERIFIED (not found in any cited source; none left). `HUMAN_CHECKED` is set only by Kush or Parv. DEL-2 figures were regenerated from the cited JSON at generation time; other figures were read from the cited reports. Rows beyond the Step 02 seed list: NEG-0007 only (Phenol-Explorer conformal coverage, the same finding as the USDA row). Rows still to add from the same gov table when wanted: RecipeDB3 leakage, evidence-key baseline, slot parsing, Gold independence, Gutenberg silver precision, scripted sessions, DEL-1 clauses.
- `registry/preregistered_thresholds_v1.csv`: columns `threshold_id, registry_status, step, quantity, value, value_status, rationale, source, data_seen_before_registration, signed_by, signed_at, commit, ci_rule, unit_of_independence, n_min, supersedes` (the Step 01 card's `CI_rule`, `unit_of_independence`, `n_min`, `commit` are columns again; `registered_by` / `registered_at` are `signed_by` / `signed_at`). `registry_status = DRAFT_PENDING_H4` on every row. `value_status` ∈ PROPOSED_PILOT, PROPOSED_VERBATIM_UNSIGNED (the unchanged Step-07 gate: values copied from the protocol and the tool, unsigned), `SIGNED_<date>` / `PREREGISTERED_<signed_at date>` (none yet; only after Kush sets `signed_by` / `signed_at`). `data_seen_before_registration` ∈ N, DESCRIPTIVE_COUNTS_SEEN (descriptive counts known, nothing computed), Y. A gate may run only if its row exists, is signed and has `data_seen_before_registration = N` (whether DESCRIPTIVE_COUNTS_SEEN is acceptable is a human decision, §4 B). `commit` is filled at signing. The file is **append-only once a row has `signed_at`**: a change is a new row whose `supersedes` names the old `threshold_id`, plus a DECISIONS entry, and the old row stays (CHG-01-3). While nothing is signed, r1 edited THR-04K-01 in place and recorded the history in the row.

## 6. Plan ambiguities and deviations found (also in the report to the requester)

1. Edge names: the brief's examples (REPORTS, REPUBLISHES, COMPILES_FROM, SHARES_SAMPLE, DERIVED_FROM, DUPLICATE_OF) differ from the card's nine types; the card was followed and the others cross-walked (lineage contract §3.2).
2. The card calls SAME_LAB_AS and SHARES_REFERENCE_SAMPLE "grouping-only" without saying whether they enter the default `split_group_id`; PRIMARY_SOURCE with unknown membership is unspecified; the draft rules are in lineage contract §3.1.
3. `lineage_root_id`, `condition_grid_id` and the formula-registry id have no reserved prefix in 01.3-min.
4. `kinetic_experiment_id (= sexp_id)` vs one experiment owning several series; K-level is a property of a set of series; the card lists PROJECT_FIT in the header but FW-14 puts project fits in the model plane; parameter-only reports have no KIN home.
5. The 07I-C label mapping and operating-point rules are asked to be pre-registered, but the card gives no explicit mapping or rule (drafted); "binary kappa" does not say which binary.
6. `registry/data_source_acquisition_manifest_v1_1.csv` (Step 08 inputs) does not exist; only v1 does.
7. The seed figures of Step 02.4 needed corrections: conformal-90 coverage on USDA cold splits is 0.7182-0.8885 (not 0.72-0.87; that is the D4/D5/D7 sub-range); Bognár's degenerate CI affects all 7 models (0.0096 is the extreme); D7 ≡ D1 holds for the raw-target Phenol-Explorer run only; the v3-large "no TEST gain" result is S128, not S125-S127; linker kappa 0.13 is not in the current reports (0.500 and 0.317 are) but is recorded in git history (commit e4045f4, a rejected third Parv file version) and is now NEG-0027 (SUPERSEDED_KEPT).
8. `ledgers/schemas/*.json` are generated from Python (`registry.py`); the plan's "08a copies the approved drafts" would be overwritten at the next export.
9. Measurement-basis aliases: ledger bases `WET`, `AS_CONSUMED`, `PER_SERVING`, `APPARENT_RETENTION`, `HEADSPACE` have no (or no explicit) alias in `measurement_basis_registry_v1.csv` (settlements proposed in 04.2-min §1a).
10. Deviations from the plan card introduced by review fixes, all PROPOSED and listed in §4: the split `retention_definition` (card: TRUE / APPARENT / YIELD_ADJUSTED / TR_OR_AR_UNDISCLOSED / UNKNOWN); `SEXP.context` absent key = UNKNOWN (card: default NOT_REPORTED); the hub rule narrowing the card's AGG parent union for compilation hubs; the KIN mandate at ≥ 2 numeric times (the card fixes no number); lab group mandatory on the kinetic plane (card: optional tier); three more prefixes (`LABGRP-`, `MBSET-`, `PARAM-` referenced).
11. The AGG and DRV schema drafts go beyond the Plan §7 list (DOC, LIN, SEXP, SMP, OBS; KIN, KINPT) and presuppose the D-2 outcome (full ledger envelope vs export-view keys).
