"""Cross-record checks of the 04.3 KIN / KINPT v1.1 DRAFT contract (S158, DRAFT_PENDING_H4).

Exercises culinarystate.lineage.kinetic_contract on SYNTHETIC SCHEMA FIXTURES (dummy numbers, unit 'u').
The module is a pure validator: it reads records, returns issues and verdicts, writes nothing. Verdicts
under the draft thresholds THR-04K-01 / -03 are labelled as draft, never as a signed gate result.
"""
from __future__ import annotations

import copy
import csv
from pathlib import Path
from typing import Any

import pytest

from culinarystate.lineage import kinetic_contract as KC
from tests.fixtures import kinetic_v1_1_fixtures as F

ROOT = Path(__file__).resolve().parents[2]


def codes(issues: list[Any], severity: str | None = None) -> set[str]:
    return {i.code for i in issues if severity is None or i.severity == severity}


def errors(issues: list[Any]) -> set[str]:
    return codes(issues, KC.ERROR)


# ----------------------------------------------------------------------------- baseline
@pytest.mark.parametrize("dig", [False, True])
def test_clean_synthetic_series_has_no_issue_and_is_schema_valid(dig: bool) -> None:
    k, pts, obs = F.series(digitised=dig)
    assert KC.schema_errors(k, "KIN") == []
    assert all(KC.schema_errors(p, "KINPT") == [] for p in pts)
    assert KC.validate_series(k, pts, obs) == []


def test_schema_errors_rejects_an_unknown_record_type() -> None:
    with pytest.raises(ValueError):
        KC.schema_errors({}, "OBS")


# ----------------------------------------------------------------------------- times: raw units, counts, clocks
def test_n_timepoints_must_equal_distinct_numeric_tau() -> None:
    k, pts, obs = F.series((0.0, 10.0, 20.0))
    assert KC.distinct_numeric_tau(pts) == 3
    k["n_timepoints"] = 4
    assert "N_TIMEPOINTS_MISMATCH" in errors(KC.validate_series(k, pts, obs))


def test_reference_without_tau_and_ranges_are_not_numeric_times() -> None:
    _, pts, _ = F.series((0.0, 10.0))
    ref = F.kinpt(9, seq=9, t=F.tau(None, "UNKNOWN", "NOT_APPLICABLE_REFERENCE"))
    rng = F.kinpt(10, seq=10, t={**F.tau(None, "min", "RANGE"), "low": 1.0, "high": 2.0})
    assert KC.distinct_numeric_tau(pts + [ref, rng]) == 2


def test_inverted_tau_range_is_an_error() -> None:
    k, pts, obs = F.series((0.0, 10.0))
    pts[1]["tau"] = {**F.tau(None, "min", "RANGE"), "low": 12.0, "high": 10.0}
    pts.append(F.kinpt(3, seq=2, t=F.tau(20.0)))
    obs["OBS-000003"] = F.obs(3, kinpt=3)
    assert "TAU_RANGE_INVERTED" in errors(KC.validate_series(k, pts, obs))


def test_exact_seconds_must_match_the_raw_value_and_unit() -> None:
    k, pts, obs = F.series((0.0, 2.0), "week")
    pts[1]["tau"]["normalised_seconds"] = F.exact_seconds(2.0, "week")
    assert KC.validate_series(k, pts, obs) == []
    pts[1]["tau"]["normalised_seconds"] = F.exact_seconds(2.0, "d")      # 2 d written as if it were 2 weeks
    assert "SECONDS_CONVERSION_MISMATCH" in errors(KC.validate_series(k, pts, obs))


def test_month_raw_unit_is_kept_and_never_rewritten() -> None:
    k, pts, obs = F.series((0.0, 3.0), "month")
    assert KC.validate_series(k, pts, obs) == []
    assert pts[1]["tau"]["unit"] == "month" and pts[1]["tau"]["normalised_seconds"]["status"] == "NOT_CONVERTED"


def test_point_unit_differing_from_the_time_base_is_flagged() -> None:
    k, pts, obs = F.series((0.0, 10.0))
    pts[1]["tau"].update(unit="h", unit_raw="h")
    assert "TAU_UNIT_DIFFERS_FROM_TIME_BASE" in codes(KC.validate_series(k, pts, obs), KC.WARN)


def test_kinpt_of_another_series_and_duplicate_mint_keys() -> None:
    k, pts, obs = F.series()
    pts[1]["kin_id"] = "KIN-000009"
    pts[2]["sequence_index"] = 0
    found = errors(KC.validate_series(k, pts, obs))
    assert {"KIN_ID_MISMATCH", "KINPT_MINT_KEY_DUPLICATE"} <= found


# ----------------------------------------------------------------------------- temperature profiles
def _with_profiles(k: dict[str, Any], *profiles: dict[str, Any]) -> None:
    k["condition_profile"].update(temperature_status="REPORTED", temperature_profiles=[copy.deepcopy(p) for p in profiles])


def test_profile_point_seconds_are_checked_and_duplicate_locations_flagged() -> None:
    k, pts, obs = F.series()
    prog = {**F.PROFILE_ISO, "schedule_type": "NON_ISOTHERMAL_PROGRAM", "isothermal_value": None,
            "points": [{"tau": 0, "tau_unit": "min", "tau_unit_raw": "min", "tau_seconds": F.exact_seconds(0, "min"),
                        "T": {"status": "MEASURED", "value": 1.0, "unit": "u"}},
                       {"tau": 5, "tau_unit": "min", "tau_unit_raw": "min", "tau_seconds": F.exact_seconds(5, "h"),
                        "T": {"status": "MEASURED", "value": 2.0, "unit": "u"}}]}
    _with_profiles(k, prog, F.PROFILE_ISO)
    assert KC.schema_errors(k, "KIN") == []
    found = KC.validate_series(k, pts, obs)
    assert "SECONDS_CONVERSION_MISMATCH" in errors(found)
    assert "DUPLICATE_PROFILE_LOCATION" in codes(found, KC.WARN)


def test_medium_and_core_profiles_are_two_clean_elements() -> None:
    k, pts, obs = F.series()
    _with_profiles(k, F.PROFILE_ISO, {**F.PROFILE_ISO, "location": "CORE"})
    assert KC.validate_series(k, pts, obs) == []


@pytest.mark.parametrize("profiles,iso,come_up,verdict", [
    ([{"location": "CORE"}], "UNKNOWN", "NOT_REPORTED", KC.ELIGIBLE),
    ([{"location": "SETPOINT"}], "PRODUCT_ISOTHERMAL_STATED", "NOT_REPORTED", KC.ELIGIBLE),
    ([{"location": "SETPOINT"}], "SETPOINT_ONLY", "EXCLUDED_FROM_TIME", KC.ELIGIBLE),
    ([{"location": "SETPOINT"}], "SETPOINT_ONLY", "INCLUDED_IN_TIME", KC.NOT_ELIGIBLE),
    ([{"location": "UNSPECIFIED"}], "UNKNOWN", "NOT_REPORTED", KC.UNKNOWN),
    ([], "UNKNOWN", "UNKNOWN", KC.UNKNOWN),
])
def test_arrhenius_eligibility_follows_r04_15(profiles: list[dict[str, str]], iso: str, come_up: str, verdict: str) -> None:
    k = F.kin()
    if profiles:
        _with_profiles(k, *({**F.PROFILE_ISO, **p} for p in profiles))
    k["condition_profile"]["isothermality"] = iso
    k["time_base"]["come_up_time"]["status"] = come_up
    v = KC.arrhenius_eligibility(k)
    assert v.verdict == verdict, v.reasons


def test_temperature_not_reported_is_not_arrhenius_eligible() -> None:
    k = F.kin()
    k["condition_profile"]["isothermality"] = "SETPOINT_ONLY"
    assert KC.arrhenius_eligibility(k).verdict == KC.NOT_ELIGIBLE


# ----------------------------------------------------------------------------- OBS mirror, C0, value scale
def test_obs_link_must_mirror_the_kinpt() -> None:
    k, pts, obs = F.series()
    obs["OBS-000002"]["series_link"] = {"status": "UNKNOWN", "kinpt_id": None}
    pts[2]["obs_id"] = "OBS-000001"
    found = errors(KC.validate_series(k, pts, obs))
    assert {"OBS_SERIES_LINK_MISMATCH", "OBS_SHARED_BY_KINPTS"} <= found
    del obs["OBS-000001"]
    assert "OBS_MISSING" in errors(KC.validate_series(k, pts, obs))


def test_c0_is_stored_once_and_is_the_t0_point() -> None:
    k, pts, obs = F.series()
    k["target"].update(c0_reference="T0_SAMPLE", c0_obs_id="OBS-000001")
    k["condition_profile"]["initial_conditions"].update(
        status="REPORTED", initial_concentration={"status": "MEASURED", "value": 1.0, "unit": "u"})
    assert KC.validate_series(k, pts, obs) == []
    k["condition_profile"]["initial_conditions"]["initial_concentration"]["value"] = 2.0
    assert "C0_VALUE_MISMATCH" in errors(KC.validate_series(k, pts, obs))
    k["condition_profile"]["initial_conditions"]["initial_concentration"]["value"] = 1.0
    k["target"]["c0_obs_id"] = "OBS-000002"
    assert "C0_NOT_A_T0_POINT" in errors(KC.validate_series(k, pts, obs))
    k["target"]["c0_obs_id"] = "OBS-000077"
    assert "C0_OBS_MISSING" in codes(KC.validate_series(k, pts, obs), KC.WARN)


def test_relative_scale_t0_point_is_definitional_and_excluded_from_fitting() -> None:
    k, pts, obs = F.series()
    k["target"].update(value_scale="RELATIVE_TO_C0", c0_reference="T0_SAMPLE", c0_obs_id="OBS-000001")
    assert "RELATIVE_T0_NOT_DEFINITIONAL" in errors(KC.validate_series(k, pts, obs))
    obs["OBS-000001"]["value_origin"] = "DEFINITIONAL_NORMALISATION"
    assert KC.validate_series(k, pts, obs) == []
    sel = KC.fitting_selection(k, pts, obs)
    assert "KINPT-000001" not in sel.included and sel.excluded["KINPT-000001"] == "DEFINITIONAL_NORMALISATION"
    assert sel.included == ("KINPT-000002", "KINPT-000003")


def test_definitional_normalisation_on_an_absolute_scale_or_nonzero_tau_is_an_error() -> None:
    k, pts, obs = F.series()
    obs["OBS-000002"]["value_origin"] = "DEFINITIONAL_NORMALISATION"
    assert "DEFINITIONAL_NORMALISATION_MISPLACED" in errors(KC.validate_series(k, pts, obs))


def test_relative_scale_with_unknown_c0_source_is_a_warning_not_an_error() -> None:
    k, pts, obs = F.series()
    k["target"].update(value_scale="PERCENT_OF_C0", c0_reference="UNKNOWN")
    obs["OBS-000001"]["value_origin"] = "DEFINITIONAL_NORMALISATION"
    found = KC.validate_series(k, pts, obs)
    assert errors(found) == set() and "RELATIVE_SCALE_C0_UNKNOWN" in codes(found, KC.WARN)


def test_unknown_time_unit_makes_points_unusable_for_fitting_but_keeps_them() -> None:
    k, pts, obs = F.series((0.0, 10.0, 20.0), "UNKNOWN")
    sel = KC.fitting_selection(k, pts, obs)
    assert sel.included == () and set(sel.excluded.values()) == {"TAU_UNIT_UNKNOWN"}
    assert len(pts) == 3                                              # nothing is discarded (R04-2)


# ----------------------------------------------------------------------------- censoring
def test_censored_points_stay_censored_and_the_summary_must_agree() -> None:
    k, pts, obs = F.series()
    obs["OBS-000003"] = F.obs(3, kinpt=3, censoring=F.CENS_ND)
    assert "CENSORING_SUMMARY_MISMATCH" in errors(KC.validate_series(k, pts, obs))
    k["censoring_summary"].update(any_censored="YES", kinds_present=["ND"])
    assert KC.validate_series(k, pts, obs) == []
    sel = KC.fitting_selection(k, pts, obs)
    assert sel.censored == ("KINPT-000003",) and "KINPT-000003" in sel.included
    assert obs["OBS-000003"]["value"]["value"] is None                 # no substituted bound (R04-9)
    k["censoring_summary"]["kinds_present"] = ["ND", "LT_LOD"]
    assert "CENSORING_SUMMARY_MISMATCH" in errors(KC.validate_series(k, pts, obs))


def test_summary_no_is_wrong_when_a_point_has_censoring_not_reported() -> None:
    k, pts, obs = F.series()
    obs["OBS-000002"]["censoring"] = dict(F.CENS_NR)
    assert "CENSORING_SUMMARY_MISMATCH" in errors(KC.validate_series(k, pts, obs))
    k["censoring_summary"]["any_censored"] = "UNKNOWN"
    assert errors(KC.validate_series(k, pts, obs)) == set()


# ----------------------------------------------------------------------------- digitisation and the two-read rule
def test_digitised_flag_must_mirror_obs_and_tau() -> None:
    k, pts, obs = F.series()
    obs["OBS-000002"]["value_origin"] = "DIGITIZED"
    obs["OBS-000002"]["digitization"] = copy.deepcopy(F.DIG_TWO_READS)
    found = errors(KC.validate_series(k, pts, obs))
    assert {"DIGITIZED_FLAG_MISMATCH", "ORIGIN_FORM_DIGITISATION_MISMATCH", "DIGITISATION_SUMMARY_MISMATCH"} <= found


def test_mixed_form_needs_both_kinds_of_point() -> None:
    k, pts, obs = F.series(digitised=True)
    k["series_origin_form"] = "MIXED_TABLE_AND_FIGURE"
    assert "ORIGIN_FORM_DIGITISATION_MISMATCH" in errors(KC.validate_series(k, pts, obs))


def test_two_read_status_is_computed_from_the_points() -> None:
    k, pts, obs = F.series(digitised=True)
    assert KC.two_read_status(pts, obs) == "ALL_DIGITISED_POINTS_TWO_INDEPENDENT_READS"
    obs["OBS-000002"]["digitization"] = copy.deepcopy(F.DIG_ONE_READ)
    assert KC.two_read_status(pts, obs) == "SOME_DIGITISED_POINTS_FEWER_READS"
    assert "DIGITISATION_SUMMARY_MISMATCH" in errors(KC.validate_series(k, pts, obs))
    _, plain, pobs = F.series()
    assert KC.two_read_status(plain, pobs) == "NOT_APPLICABLE"


def test_same_reader_repeats_leave_the_two_read_status_not_assessed() -> None:
    _, pts, obs = F.series(digitised=True, reads="SAME_READER_REPEATED")
    assert KC.two_read_status(pts, obs) == "NOT_ASSESSED"


# ----------------------------------------------------------------------------- eligibility (draft rules, never a signed gate)
def test_clean_series_is_eligible_only_under_draft_rules() -> None:
    k, pts, obs = F.series(digitised=True)
    v = KC.split_eligibility(k, pts, obs)
    assert v.verdict == KC.ELIGIBLE == "ELIGIBLE_UNDER_DRAFT_RULES", v.reasons
    assert any(r.threshold_id == "THR-04K-03" and r.status == "DRAFT_PENDING_H4" for r in v.rule_refs)


@pytest.mark.parametrize("mutate,verdict,reason", [
    (lambda k, p, o: k["lineage"].update(lab_group_id=None, lab_group_status="UNKNOWN", lab_group_basis="UNKNOWN"),
     KC.NOT_ELIGIBLE, "LAB_GROUP_UNKNOWN"),
    (lambda k, p, o: k["lineage"].update(lab_group_id=None, lab_group_status="PENDING"), KC.UNKNOWN, "LAB_GROUP_PENDING"),
    (lambda k, p, o: k["lineage"].update(independence_resolution="UNKNOWN", study_id=None, study_id_status="NOT_IDENTIFIABLE"),
     KC.NOT_ELIGIBLE, "INDEPENDENCE_UNKNOWN"),
    (lambda k, p, o: k.update(evidence_tier="E5"), KC.NOT_ELIGIBLE, "EVIDENCE_TIER_E5"),
    (lambda k, p, o: o["OBS-000002"].update(digitization=copy.deepcopy(F.DIG_ONE_READ)), KC.NOT_ELIGIBLE, "SINGLE_READ"),
    (lambda k, p, o: o["OBS-000002"]["digitization"].update(n_reads={"status": "NOT_REPORTED", "value": None}),
     KC.NOT_ELIGIBLE, "READ_COUNT_NOT_REPORTED"),
    (lambda k, p, o: p[1]["digitized"].update(read_independence="SAME_READER_REPEATED"), KC.UNKNOWN, "READ_INDEPENDENCE_OPEN_H4"),
    (lambda k, p, o: o["OBS-000002"]["digitization"].update(read_sd={"status": "NOT_REPORTED", "value": None, "unit": None}),
     KC.UNKNOWN, "READ_SD_NOT_STORED"),
])
def test_eligibility_failures(mutate: Any, verdict: str, reason: str) -> None:
    k, pts, obs = F.series(digitised=True)
    mutate(k, pts, obs)
    v = KC.split_eligibility(k, pts, obs)
    assert v.verdict == verdict and reason in v.reasons, (v.verdict, v.reasons)


def test_not_eligible_dominates_unknown() -> None:
    k, pts, obs = F.series(digitised=True)
    k["lineage"].update(lab_group_id=None, lab_group_status="PENDING")
    k["evidence_tier"] = "E5"
    assert KC.split_eligibility(k, pts, obs).verdict == KC.NOT_ELIGIBLE


# ----------------------------------------------------------------------------- repeated measures, companions, sets
def test_repeated_measures_need_a_stable_unit_label() -> None:
    k, pts, obs = F.series()
    k["replicate_structure"]["design"] = "REPEATED_MEASURES_SAME_UNITS"
    assert "UNIT_LABEL_REQUIRED" in errors(KC.validate_series(k, pts, obs))
    for p in pts:
        p["replicate"]["unit_label"] = "synthetic unit A"
    assert KC.validate_series(k, pts, obs) == []


def _companion_pair() -> tuple[Any, Any]:
    tissue = F.series((0.0, 10.0), kin_n=1, first_point=1)
    medium = F.series((0.0, 10.0), kin_n=2, first_point=11)
    for kk, other in ((tissue[0], "KIN-000002"), (medium[0], "KIN-000001")):
        kk.update(companion_status="LINKED", companion_series=[{"kin_id": other, "role": "COOKING_MEDIUM_CONC"}],
                  mass_balance_set_id="MBSET-000001")
    return tissue, medium


def test_companion_series_pairs_at_the_same_tau() -> None:
    (k1, p1, o1), (k2, p2, o2) = _companion_pair()
    comp = {"KIN-000002": (k2, p2)}
    obs = {**o1, **o2}
    assert codes(KC.validate_series(k1, p1, obs, companions=comp)) == {"COMPANION_POINT_UNPAIRED"}
    for a, b in zip(p1, p2):
        a["paired_kinpt_ids"] = [b["id"]]
    assert KC.validate_series(k1, p1, obs, companions=comp) == []
    k2["mass_balance_set_id"] = "MBSET-000002"
    assert "COMPANION_MASS_BALANCE_SET_MISMATCH" in errors(KC.validate_series(k1, p1, obs, companions=comp))
    assert "COMPANION_MISSING" in codes(KC.validate_series(k1, p1, obs, companions={}), KC.WARN)


def test_companion_points_on_the_same_sample_are_paired() -> None:
    (k1, p1, o1), (k2, p2, o2) = _companion_pair()
    for a, b in zip(p1, p2):
        o2[b["obs_id"]]["sample_id"] = o1[a["obs_id"]]["sample_id"]
    assert KC.validate_series(k1, p1, {**o1, **o2}, companions={"KIN-000002": (k2, p2)}) == []


def test_split_group_must_nest_in_one_lab_group() -> None:
    a, b = F.kin(1), F.kin(2)
    b["lineage"]["lab_group_id"] = "LABGRP-000002"
    assert "LAB_GROUP_NESTING_VIOLATED" in errors(KC.validate_series_set([a, b]))
    b["lineage"]["split_group_id"] = "SPLITGRP-EVD-000002"
    assert KC.validate_series_set([a, b]) == []


def test_grid_level_fit_must_name_every_grid_member() -> None:
    a, b = F.kin(1), F.kin(2)
    for x in (a, b):
        x["condition_profile"].update(grid_role="MEMBER_OF_GRID", condition_grid_id="CGRID-000001")
    a["fit"] = [{"scope": "CONDITION_GRID", "input_kin_status": "STATED", "input_kin_ids": ["KIN-000001"]}]
    assert "GRID_FIT_INPUTS_INCOMPLETE" in errors(KC.validate_series_set([a, b]))
    a["fit"][0]["input_kin_ids"] = ["KIN-000001", "KIN-000002"]
    assert KC.validate_series_set([a, b]) == []


# ----------------------------------------------------------------------------- analyte-form tokens
def test_registry_token_needs_an_approved_registry() -> None:
    k, pts, obs = F.series()
    k["target"]["analyte_form"] = {"status": "STATED", "text": "x", "token": "SYNTH_FORM_A", "token_status": "REGISTRY_TOKEN"}
    assert "ANALYTE_TOKEN_WITHOUT_APPROVED_REGISTRY" in errors(KC.validate_series(k, pts, obs))
    assert "ANALYTE_TOKEN_NOT_IN_REGISTRY" in errors(
        KC.validate_series(k, pts, obs, analyte_form_tokens=frozenset({"SYNTH_FORM_B"})))
    assert KC.validate_series(k, pts, obs, analyte_form_tokens=frozenset({"SYNTH_FORM_A"})) == []


# ----------------------------------------------------------------------------- draft thresholds are referenced, not signed
def test_mandate_follows_draft_thr_04k_01() -> None:
    assert KC.series_storage_required(2) and not KC.series_storage_required(1)
    ref = KC.DRAFT_THRESHOLDS["THR-04K-01"]
    assert ref.status == "DRAFT_PENDING_H4"


def test_threshold_rows_are_still_unsigned_drafts_in_the_registry() -> None:
    with open(ROOT / "registry" / "preregistered_thresholds_v1.csv", newline="", encoding="utf-8") as fh:
        rows = {r["threshold_id"]: r for r in csv.DictReader(fh)}
    for tid, ref in KC.DRAFT_THRESHOLDS.items():
        assert rows[tid]["registry_status"] == ref.status == "DRAFT_PENDING_H4", tid
        assert not rows[tid].get("signed_by"), f"{tid} is signed: the module must be updated by a human decision"


def test_module_is_pure() -> None:
    src = Path(KC.__file__).read_text(encoding="utf-8")
    for banned in ("open(", "write_text", "write_bytes", "ledgers/data", "subprocess", "requests"):
        assert banned not in src.replace("read_text(", "READ("), banned
