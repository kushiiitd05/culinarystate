"""D-110: state dataset cells are value+basis or UNKNOWN+reason; never guessed."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("sdf", ROOT / "tools" / "s179_state_dataset_fill.py")
sdf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sdf)
FIT = {"n_papers": 2, "papers": ["A", "B"], "intercepts": {"A": -4.0, "B": -3.0}, "Ea_J_per_mol": 64000.0,
       "cov": [[0.01, 0, 0], [0, 0.01, 0], [0, 0, 1e8]], "sigma_between": 0.8, "residual_sd": 0.2, "T_ref_K": 363.15}


def test_l1_cell_value_basis_or_reason():
    r1 = {"inputs": {"medium": {"value": "LIQUID", "basis": "TEXT_STATED"}, "duration": {"value": None, "reason": "NO_DURATION_STATED"}}}
    assert sdf.l1_cell(r1, "medium") == {"v": "LIQUID", "b": "TEXT_STATED"}
    assert sdf.l1_cell(r1, "duration") == {"v": None, "u": "NO_DURATION_STATED"}
    assert sdf.l1_cell(None, "medium") == {"v": None, "u": "NOT_A_HEAT_EVENT"}


def test_l2_cells_scenario_default_and_formula_gate():
    r1 = {"inputs": {"matrix_class": {"value": "FRUIT"}, "medium": {"value": "LIQUID"}}}
    r2 = {"status": "SCENARIO_COMPUTED", "scenarios": {"TYPICAL": {"bath_c": 95.0, "t_cap_c": 100.0, "duration_min": 20.0}}}
    c = sdf.l2_cells(r1, r2, FIT)
    assert c["food_T_typical_C"] == {"v": 95.0, "b": "SCENARIO_DEFAULT"}
    assert c["aa_retention_typical"]["b"] == "FORMULA_RESEARCH_ONLY" and 0 < c["aa_retention_typical"]["v"] < 1
    r1w = {"inputs": {"matrix_class": {"value": "FRUIT"}, "medium": {"value": "WATER"}}}
    assert sdf.l2_cells(r1w, r2, FIT)["aa_retention_typical"] == {"v": None, "u": "WATER_CONTACT"}


def test_non_heat_event_is_unknown_with_reason():
    c = sdf.l2_cells(None, None, FIT)
    assert all(v == {"v": None, "u": "NOT_A_HEAT_EVENT"} for v in c.values())


def test_merge_sums_shards():
    spec = importlib.util.spec_from_file_location("m", ROOT / "tools" / "s179_state_dataset_fill_merge.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    p = {"recipes": 2, "rows": 5, "exceptions": 0, "shard": "0/2", "heat_rows_joined_to_physics": {"F": 1},
         "fill_by_basis_or_reason": {"F": {"medium": {"VALUE:TEXT_STATED": 3, "UNKNOWN:NO_MEDIUM": 2}}}}
    q = dict(p, shard="1/2")
    r = m.merge([p, q])
    assert r["recipes"] == 4 and r["rows"] == 10 and r["value_rate_pct"]["F"]["medium"] == 60.0
