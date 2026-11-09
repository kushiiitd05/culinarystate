"""Board T6-C09-R2 (acceptance: "tests/unit/test_transition_firewall.py passes; refuses any E7 or Layer-2 row"). S178 FIX-GOV, GOV-10.

The cell-table builder ``transition.dataset.cells_from_rows`` is the firewall between the EVD ledger and every transition
fit (DEL-2, 29-diag, D5). Rules pinned here (TB-V0 contract section 1; SSOT 222.9; law 1 "UNKNOWN is never 0"):

  * only evidence tiers E1-E4 enter (E5-E7 and a missing or unknown tier are refused);
  * a Layer-2 / scenario / simulated / assumed-default row is refused whatever its tier;
  * an imputed-target row (evidence class ``I``, SSOT 222.9) never enters a table that feeds test, validation or
    calibration roles; only an explicit ``role="train"`` table may hold it;
  * a CENSORED row with no usable limit is UNKNOWN (no row, never a zero bound);
  * an ``LT_*`` limit is an upper bound: it is never stored as ``y_lower`` (the v0 table holds lower-bound censoring only,
    so the row is left out and counted); a ``GT_*`` limit is a lower bound; any other censor kind is UNKNOWN;
  * every refusal is counted in ``CellTable.excluded`` by reason code.

Synthetic EVD rows only (invented ids); no ledger is read.
"""
from __future__ import annotations

import pytest

from culinarystate.transition import dataset as DS

FAM = "USDA-RETN-R6"
COND = {"COND-1": {"id": "COND-1", "completeness_mask": {"temperature": "MEASURED", "duration": "UNKNOWN"}, "medium": "water"}}


def row(i, rf, *, tier="E3", **extra):
    e = {"id": f"EVD-{i:06d}", "status": "ACTIVE", "source_family_id": FAM, "tier": tier,
         "matrix": {"raw_name": "CARROT", "food_group": "Vegetables", "form": None, "ingredient_id": "ING-1"},
         "process": {"steps": ["boil"], "condition_id": "COND-1", "modifiers": {}},
         "target": {"raw_name": "Vitamin C", "basis": "TRUE_RETENTION", "state_variable_id": "SVAR-000009"},
         "derived": {"retention_factor": rf}, "independence_group": FAM, "study_ids": []}
    e.update(extra)
    return e


def M(v, unit="%"):
    return {"status": "MEASURED", "value": v, "unit": unit}


def C(limit=97.5, kind="GT_CAP", unit="%"):
    cen = {"kind": kind}
    if limit is not None:
        cen["limit"] = limit
    return {"status": "CENSORED", "unit": unit, "censor": cen}


def table(rows, **kw):
    return DS.cells_from_rows(rows, COND, FAM, **kw)


# ---------------------------------------------------------------- tiers
@pytest.mark.parametrize("tier", ["E1", "E2", "E3", "E4"])
def test_e1_to_e4_enter(tier):
    assert list(table([row(1, M(50.0), tier=tier)]).df["evd_id"]) == ["EVD-000001"]


@pytest.mark.parametrize("tier", ["E5", "E6", "E7", "E8", "I", "", None, "e3", "GOLD"])
def test_any_other_tier_is_refused_and_counted(tier):
    t = table([row(1, M(50.0)), row(2, M(60.0), tier=tier)])
    assert list(t.df["evd_id"]) == ["EVD-000001"]
    assert sum(t.excluded.values()) == 1


def test_missing_tier_key_is_refused():
    e = row(1, M(50.0))
    del e["tier"]
    t = table([e])
    assert len(t.df) == 0 and t.excluded == {"TIER_NOT_E1_E4": 1}


def test_e7_is_refused_with_its_reason():
    t = table([row(1, M(50.0), tier="E7")])
    assert len(t.df) == 0 and t.excluded == {"TIER_NOT_E1_E4": 1}


# ---------------------------------------------------------------- Layer 2 / simulated rows
@pytest.mark.parametrize("extra", [
    {"layer": "SCENARIO"}, {"layer": "L2"}, {"layer": "LAYER_2"},
    {"derived": {"retention_factor": {**M(50.0), "basis": "MODEL_DERIVED"}}},
    {"derived": {"retention_factor": {**M(50.0), "basis": "ASSUMED_DEFAULT"}}},
    {"derived": {"retention_factor": {**M(50.0), "label": "SIMULATED"}}},
    {"origin_type": "SIMULATION"},
    {"provenance": {"labels": ["SCENARIO", "NON_CITABLE"]}},
])
def test_layer2_or_simulated_row_is_refused_even_at_tier_e3(extra):
    t = table([row(1, M(50.0)), row(2, M(50.0), **extra)])
    assert list(t.df["evd_id"]) == ["EVD-000001"] and t.excluded == {"LAYER2_OR_SIMULATED": 1}


def test_real_origin_types_are_not_mistaken_for_layer2():
    for o in ("PRIMARY_STUDY", "DATABASE_AGGREGATE", "REVIEW_AGGREGATE", "AUTHORITY_STANDARD", "PROJECT_MEASUREMENT"):
        assert len(table([row(1, M(50.0), origin_type=o)]).df) == 1, o


# ---------------------------------------------------------------- imputed-target class I (SSOT 222.9)
def test_class_i_rows_never_reach_a_table_that_feeds_test_or_calibration():
    rows = [row(1, M(50.0)), row(2, M(55.0), tier="I")]
    for role in (None, "all", "test", "validation", "calibration"):
        t = table(rows) if role is None else table(rows, role=role)
        assert list(t.df["evd_id"]) == ["EVD-000001"], role
        assert t.excluded.get("IMPUTED_CLASS_I_NOT_IN_HOLDOUT_ROLES") == 1, role


def test_class_i_rows_may_enter_only_an_explicit_training_table():
    t = table([row(1, M(50.0)), row(2, M(55.0), tier="I")], role="train")
    assert list(t.df["evd_id"]) == ["EVD-000001", "EVD-000002"]


def test_unknown_role_is_an_error():
    with pytest.raises(ValueError):
        table([row(1, M(50.0))], role="holdout")


def test_role_rule_is_explicit():
    assert DS.tier_allowed("E3", "test") and DS.tier_allowed("E4", "calibration")
    assert DS.tier_allowed("I", "train") and not DS.tier_allowed("I", "test") and not DS.tier_allowed("I", "calibration")
    assert not DS.tier_allowed("E7", "train") and not DS.tier_allowed(None, "train")


# ---------------------------------------------------------------- censoring
def test_censored_without_limit_is_unknown_not_zero():
    for rf in (C(limit=None), {"status": "CENSORED", "unit": "%"}, {"status": "CENSORED", "unit": "%", "censor": {"kind": "GT_CAP", "limit": None}},
               {"status": "CENSORED", "unit": "%", "censor": {"kind": "GT_CAP", "limit": "n/a"}}):
        t = table([row(1, rf)])
        assert len(t.df) == 0 and t.excluded == {"CENSOR_LIMIT_MISSING": 1}


def test_gt_limit_is_a_lower_bound_on_the_fraction_scale():
    df = table([row(1, C(97.5, "GT_CAP")), row(2, C(0.5, "GT_STATED", unit="fraction"))]).df.set_index("evd_id")
    assert df.loc["EVD-000001", "y_lower"] == pytest.approx(0.975) and df.loc["EVD-000001", "censored"]
    assert df.loc["EVD-000002", "y_lower"] == pytest.approx(0.5)
    assert df["y"].isna().all()


def test_a_zero_limit_that_is_stated_stays_a_stated_zero_lower_bound():
    df = table([row(1, C(0.0, "GT_STATED"))]).df
    assert list(df["y_lower"]) == [0.0]                    # stated in the source: a bound, not an imputation


@pytest.mark.parametrize("kind", ["LT_LOD", "LT_STATED", "LT_LOQ"])
def test_lt_limit_is_an_upper_bound_never_a_lower_bound(kind):
    t = table([row(1, C(5.0, kind))])
    assert len(t.df) == 0 and t.excluded == {"LEFT_CENSORED_UPPER_BOUND_NOT_IN_V0_TABLE": 1}
    b = DS.retention_bounds(row(1, C(5.0, kind)))
    assert b.lower is None and b.upper == pytest.approx(0.05) and b.status == "CENSORED_UPPER"


@pytest.mark.parametrize("kind", [None, "", "BETWEEN", "ND"])
def test_unknown_censor_kind_is_unknown(kind):
    rf = {"status": "CENSORED", "unit": "%", "censor": {"limit": 50.0, **({"kind": kind} if kind is not None else {})}}
    t = table([row(1, rf)])
    assert len(t.df) == 0 and t.excluded == {"CENSOR_KIND_UNKNOWN": 1}


def test_unknown_and_absent_retention_never_become_cells():
    t = table([row(1, {"status": "UNKNOWN"}), row(2, None), row(3, M(40.0))])
    assert list(t.df["evd_id"]) == ["EVD-000003"] and t.excluded == {"NO_RETENTION_VALUE": 2}


def test_build_cells_and_cells_from_rows_keep_the_column_contract():
    df = table([row(1, M(50.0)), row(2, C())]).df
    assert list(df.columns) == DS.COLUMNS
    assert DS.y_train(df).tolist() == [0.5, 0.975]
