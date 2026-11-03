"""SYNTHETIC SCHEMA FIXTURES for the 04.3 KIN / KINPT v1.1 DRAFT contract (S158, DRAFT_PENDING_H4).

Structure only: placeholder strings, dummy unit "u" and dummy numbers (1.0, 0.5 ...). None of these
numbers is a measurement, a rate constant or a literature value. Nothing here reads a ledger.
The builders follow the scratch contract test in reports/step04/README.md section 3 (v1) and add the
v1.1 keys (analyte_form token, digitisation_summary, digitized.read_independence).
"""
from __future__ import annotations

import copy
from typing import Any

Z = "SYNTHETIC-PLACEHOLDER"
NOW = "2026-11-03T00:00:00+00:00"
SCHEMA_VERSION = "1.1.0-draft"

DISP_NONE: dict[str, Any] = {
    "type": "NONE_REPORTED", "value": None, "low": None, "high": None, "ci_level": None, "unit": None,
    "n_basis": "NOT_APPLICABLE", "scope": "NOT_APPLICABLE", "significance_raw": None, "derivation": "NOT_APPLICABLE"}
CENS_NR: dict[str, Any] = {
    "kind": "NOT_REPORTED", "registry_id": "CS-007", "limit_low": None, "limit_high": None, "limit_unit": None,
    "limit_origin": "NOT_APPLICABLE", "resolution": None, "basis_note": None}
CENS_DETECTED: dict[str, Any] = {**CENS_NR, "kind": "DETECTED", "registry_id": "CS-001"}
CENS_ND: dict[str, Any] = {**CENS_NR, "kind": "ND", "registry_id": "CS-002", "limit_origin": "NOT_STATED"}
MEAS_NR: dict[str, Any] = {"status": "NOT_REPORTED", "value": None, "unit": None}
CNT_NR: dict[str, Any] = {"status": "NOT_REPORTED", "value": None}
LOC: dict[str, Any] = {"doc_id": "DOC-000001", "locator_type": "TABLE_CELL", "page": None, "table_id": None,
                       "row_label": None, "column_label": None, "figure_id": None, "char_span": None, "raw_text": Z}
METH_NR: dict[str, Any] = {"status": "NOT_REPORTED", "method_id": None, "platform_family": None, "platform_raw": None}
SECONDS_NC: dict[str, Any] = {"status": "NOT_CONVERTED", "value": None, "convention": None}
COND_NR: dict[str, Any] = {"status": "NOT_REPORTED", "condition_id": None}
AF_NR: dict[str, Any] = {"status": "NOT_REPORTED", "text": None, "token": None, "token_status": "NOT_APPLICABLE"}
AF_OBS: dict[str, Any] = {"status": "NOT_REPORTED", "text": None}
MATRIX: dict[str, Any] = {"ingredient_id": None, "raw_name": Z}
PROCESS: dict[str, Any] = {"process_id": None, "raw_name": Z}
PROFILE_ISO: dict[str, Any] = {
    "location": "MEDIUM", "clock": "PROCESS_TAU", "schedule_type": "ISOTHERMAL", "derivation": "AS_REPORTED",
    "uncertainty": DISP_NONE, "isothermal_value": {"status": "MEASURED", "value": 1.0, "unit": "u"}, "points": [],
    "raw_text": None, "condition_id": None}
LIN_ASSIGNED: dict[str, Any] = {
    "study_id": "STUDY-000001", "study_id_status": "PRESENT", "lineage_root_id": "LROOT-000001",
    "split_group_id": "SPLITGRP-EVD-000001", "independence_resolution": "STUDY", "assignment_status": "ASSIGNED",
    "rule_version": "fixture-rule-v0"}
DIG_TWO_READS: dict[str, Any] = {
    "tool": "synthetic-tool", "tool_version": "0", "uncertainty": None, "uncertainty_unit": None,
    "uncertainty_status": "UNKNOWN", "uncertainty_type": "UNKNOWN", "axis_scale_x": "LINEAR", "axis_scale_y": "LINEAR",
    "calibration_points_raw": None, "digitizer": None, "n_reads": {"status": "REPORTED", "value": 2},
    "read_sd": {"status": "REPORTED", "value": 0.5, "unit": "u"}, "figure_locator": None}
DIG_ONE_READ: dict[str, Any] = {**DIG_TWO_READS, "n_reads": {"status": "REPORTED", "value": 1}, "read_sd": dict(MEAS_NR)}

FACTOR = {"s": 1, "min": 60, "h": 3600, "d": 86400, "week": 604800}


def env(prefix: str, n: int = 1) -> dict[str, Any]:
    return {"id": f"{prefix}-{n:06d}", "record_type": prefix, "schema_version": SCHEMA_VERSION, "version": 1,
            "status": "ACTIVE", "created_at": NOW, "created_by": "fixture",
            "provenance": {"method": "MANUAL", "source_ids": ["SRC-000001"]},
            "verification": {"status": "UNVERIFIED"}, "notes": "SYNTHETIC SCHEMA FIXTURE"}


def obs(n: int = 1, *, value: float | None = 1.0, kinpt: int | None = None, origin: str = "MEASURED",
        censoring: dict[str, Any] | None = None, digitization: dict[str, Any] | None = None,
        sample: int = 1) -> dict[str, Any]:
    """An OBS.draft_v1_1 record behind one KINPT (value is a dummy number, unit 'u')."""
    o = env("OBS", n)
    cens = copy.deepcopy(censoring if censoring is not None else CENS_DETECTED)
    val: dict[str, Any] = {"status": "MEASURED", "value": value, "unit": "u", "raw": Z}
    if cens["kind"] == "ND":
        val = {"status": "CENSORED", "value": None, "unit": "u", "raw": Z}
    o.update({
        "sample_id": f"SMP-{sample:06d}", "state_variable_id": "SVAR-000001", "analyte_raw_name": Z, "molecule_id": None,
        "analyte_form": dict(AF_OBS), "compartment": "UNKNOWN", "n_biological": dict(CNT_NR),
        "n_technical": dict(CNT_NR), "aggregation_level": "UNKNOWN", "locator": copy.deepcopy(LOC),
        "series_link": ({"status": "LINKED_KINPT", "kinpt_id": f"KINPT-{kinpt:06d}"} if kinpt is not None
                        else {"status": "UNKNOWN", "kinpt_id": None}),
        "measurement_dedup": {"status": "UNKNOWN", "canonical_obs_id": None, "report_priority": None},
        "value": val, "statistic": "UNKNOWN", "dispersion": copy.deepcopy(DISP_NONE), "censoring": cens,
        "lod": dict(MEAS_NR), "loq": dict(MEAS_NR), "basis_id": "MB-008", "basis_raw": None,
        "retention_definition": "NOT_APPLICABLE", "retention_definition_evidence": "NOT_APPLICABLE",
        "method_indicator": "UNKNOWN", "method": dict(METH_NR), "condition_ref": dict(COND_NR),
        "value_origin": origin, "digitization": copy.deepcopy(digitization), "licence_status": "UNKNOWN",
        "extraction_version": "fixture"})
    return o


def tau(value: float | None, unit: str = "min", status: str = "REPORTED", *, derivation: str = "AS_REPORTED",
        seconds: dict[str, Any] | None = None) -> dict[str, Any]:
    t: dict[str, Any] = {"clock": "PROCESS_TAU", "status": status, "value": value, "low": None, "high": None,
                         "unit": unit, "unit_raw": unit, "derivation": derivation, "uncertainty": None,
                         "uncertainty_unit": None, "uncertainty_type": None, "uncertainty_status": None,
                         "normalised_seconds": copy.deepcopy(seconds or SECONDS_NC)}
    if derivation == "DIGITIZED":
        t.update(uncertainty_status="UNKNOWN", uncertainty_type="UNKNOWN")
    return t


def exact_seconds(value: float, unit: str) -> dict[str, Any]:
    return {"status": "CONVERTED_EXACT", "value": value * FACTOR[unit], "convention": None}


def kinpt(n: int = 1, *, kin: int = 1, seq: int = 0, t: dict[str, Any] | None = None, obs_n: int | None = None,
          role: str = "INTERMEDIATE", digitized: str = "NO", reads: str | None = None,
          unit_label: str | None = None) -> dict[str, Any]:
    p = env("KINPT", n)
    dig: dict[str, Any] = {"status": digitized, "tool": None, "tool_version": None,
                           "read_independence": reads or {"NO": "NOT_APPLICABLE", "UNKNOWN": "UNKNOWN"}.get(
                               digitized, "INDEPENDENT_READERS")}
    if digitized == "YES":
        dig.update(tool="synthetic-tool", tool_version="0")
    p.update({"kin_id": f"KIN-{kin:06d}", "sequence_index": seq, "tau": copy.deepcopy(t or tau(0.0)),
              "point_role": role,
              "replicate": {"status": "AGGREGATED_OVER_REPLICATES", "index": None, "unit_label": unit_label,
                            "run_status": "UNKNOWN", "run_id": None},
              "obs_id": f"OBS-{(obs_n or n):06d}", "paired_kinpt_ids": [],
              "temperature_at_point": {"status": "NOT_REPORTED", "value": None, "location": None},
              "digitized": dig})
    return p


def kin(n: int = 1, *, n_timepoints: int = 3) -> dict[str, Any]:
    k = env("KIN", n)
    k.update({
        "sexp_id": "SEXP-000001", "series_label_raw": None, "series_origin_form": "TABLE",
        "target": {"state_variable_id": "SVAR-000001", "analyte_raw_name": Z, "molecule_id": None,
                   "analyte_form": dict(AF_NR), "compartment": "UNKNOWN", "basis_id": "MB-008", "basis_raw": None,
                   "value_scale": "ABSOLUTE", "c0_reference": "NOT_REPORTED", "c0_obs_id": None},
        "matrix": dict(MATRIX), "reference_sample_id": None, "process": dict(PROCESS),
        "condition_profile": {"condition_grid_id": None, "grid_role": "SINGLE_SERIES", "condition_ids": [],
                              "condition_status": "NOT_REPORTED", "normalizer_fingerprint_12": None,
                              "temperature_status": "NOT_REPORTED", "temperature_profiles": [],
                              "isothermality": "UNKNOWN",
                              "initial_conditions": {"status": "NOT_REPORTED", "initial_concentration": None,
                                                     "ph_initial": None, "moisture_initial": None, "note": None}},
        "time_base": {"clock": "PROCESS_TAU", "unit": "min", "unit_raw": "min", "t0_definition": "NOT_REPORTED",
                      "come_up_time": {"status": "NOT_REPORTED", "duration": None}, "note": None},
        "n_timepoints": n_timepoints,
        "replicate_structure": {"design": "UNKNOWN", "n_biological_per_timepoint": dict(CNT_NR),
                                "n_technical_per_unit": dict(CNT_NR), "reporting": "UNKNOWN"},
        "companion_status": "NOT_REPORTED", "companion_series": [], "mass_balance_set_id": None,
        "censoring_summary": {"any_censored": "NO", "kinds_present": [], "lod": dict(MEAS_NR), "loq": dict(MEAS_NR)},
        "digitisation_summary": {"any_digitised": "NO", "two_read_status": "NOT_APPLICABLE",
                                 "rule_ref": "THR-04K-03"},
        "method": dict(METH_NR), "k_level": {"value": "UNKNOWN", "scope": "UNKNOWN", "classifier_version": None},
        "fit": [], "evidence_tier": "E3", "locator": copy.deepcopy(LOC),
        "lineage": {**copy.deepcopy(LIN_ASSIGNED), "lab_group_id": "LABGRP-000001", "lab_group_status": "ASSIGNED",
                    "lab_group_basis": "MANUAL"},
        "licence_status": "UNKNOWN", "extraction_version": "fixture"})
    return k


def series(times: tuple[float, ...] = (0.0, 10.0, 20.0), unit: str = "min", *, kin_n: int = 1,
           first_point: int = 1, digitised: bool = False,
           reads: str = "INDEPENDENT_READERS") -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """One schema-valid synthetic series: KIN + one KINPT and one OBS per time (dummy values)."""
    k = kin(kin_n, n_timepoints=len(set(times)))
    k["time_base"].update(unit=unit, unit_raw=unit)
    pts: list[dict[str, Any]] = []
    obs_by_id: dict[str, dict[str, Any]] = {}
    for i, v in enumerate(times):
        n = first_point + i
        status = "DEFINITIONAL_ZERO" if v == 0 else "REPORTED"
        t = tau(0 if v == 0 else v, unit, status, derivation="DIGITIZED" if digitised else "AS_REPORTED")
        role = "INITIAL" if i == 0 else ("FINAL" if i == len(times) - 1 else "INTERMEDIATE")
        pts.append(kinpt(n, kin=kin_n, seq=i, t=t, role=role, digitized="YES" if digitised else "NO",
                         reads=reads if digitised else None))
        o = obs(n, kinpt=n, origin="DIGITIZED" if digitised else "MEASURED",
                digitization=DIG_TWO_READS if digitised else None)
        obs_by_id[o["id"]] = o
    if digitised:
        k["series_origin_form"] = "FIGURE_DIGITIZED"
        k["provenance"]["locator"] = "synthetic figure locator"
        k["digitisation_summary"] = {"any_digitised": "YES",
                                     "two_read_status": "ALL_DIGITISED_POINTS_TWO_INDEPENDENT_READS",
                                     "rule_ref": "THR-04K-03"}
    return k, pts, obs_by_id
