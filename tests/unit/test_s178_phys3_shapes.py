"""S178 PHYS3 (T4-C08-R1): cylinder / sphere / product-shape eigen-series, verification pack, shape map, shape diagnostic. Synthetic."""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

from culinarystate.quantity import rc2_dryrun as D
from culinarystate.simulation import phys_verification_shapes as V
from culinarystate.simulation import physics_drivers as PD
from culinarystate.simulation import shape_series as S

ROOT = Path(__file__).resolve().parents[2]
SENTINEL = "ZQXSENTINEL"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------ series
def test_verification_pack_quick_passes_every_check():
    checks = V.run_all(quick=True)
    assert [c["id"] for c in checks] == [f"SV{i:02d}" for i in range(1, 16)]
    failed = [(c["id"], c["max_abs_error"], c["tolerance"]) for c in checks if not c["passed"]]
    assert failed == []
    by = {c["id"]: c for c in checks}
    assert by["SV11"]["violations"] == 0 and by["SV11"]["ordering_violations"] == 0
    assert by["SV09"]["source_status"] == V.RECALLED


@pytest.mark.parametrize("shape", S.SHAPES_1D)
def test_theta_basic_properties(shape):
    assert S.center_theta(shape, fo=0.0, bi=3.0) == 1.0 and S.mean_theta(shape, fo=0.0, bi=3.0) == 1.0
    prev = 1.0
    for fo in (0.01, 0.05, 0.2, 1.0, 3.0):  # monotone in time, inside [0, 1], centre >= mean >= surface while heating
        c, m, s = S.center_theta(shape, fo=fo, bi=3.0), S.mean_theta(shape, fo=fo, bi=3.0), S.theta(shape, 1.0, fo=fo, bi=3.0)
        assert 0.0 <= s <= m <= c <= prev + 1e-15
        prev = c


def test_known_exact_values():
    z, c, _ = S.coefficients("SPHERE", 1.0, 1)
    assert z[0] == pytest.approx(math.pi / 2, abs=1e-14) and c[0] == pytest.approx(4 / math.pi, abs=1e-14)
    assert S.eigenvalues("SLAB", math.inf, 2) == pytest.approx([math.pi / 2, 3 * math.pi / 2], abs=1e-15)
    # the shape_series slab is the physics_drivers slab
    for fo in (0.05, 0.3, 1.2):
        assert S.center_theta("SLAB", fo=fo, bi=7.0) == pytest.approx(PD.slab_center_theta(fo=fo, bi=7.0), abs=1e-12)


def test_inputs_are_validated():
    with pytest.raises(ValueError):
        S.eigenvalues("SLAB", 0.0, 3)
    with pytest.raises(ValueError):
        S.eigenvalues("CONE", 1.0, 3)
    with pytest.raises(ValueError):
        S.eigenvalues("SPHERE", 1.0, S.MAX_TERMS + 1)
    with pytest.raises(ValueError):
        S.theta("SPHERE", 1.5, fo=0.1, bi=1.0)
    with pytest.raises(ValueError):
        S.mean_theta("SPHERE", fo=-0.1, bi=1.0)
    with pytest.raises(ValueError):
        S.mean_theta("SPHERE", fo=S.fo_min() / 10, bi=1.0)
    with pytest.raises(ValueError):
        S.Geometry("FINITE_CYLINDER", (0.01,))
    with pytest.raises(ValueError):
        S.Geometry("SPHERE", (-0.01,))
    with pytest.raises(ValueError):
        S.theta_center_and_mean(S.Geometry("SPHERE", (0.01,)), time_s=10.0, alpha_m2_s=0.0, h_w_m2k=10.0, k_w_mk=0.5)


def test_products_and_dimensional_wrapper():
    props = dict(time_s=300.0, alpha_m2_s=1.4e-7, h_w_m2k=600.0, k_w_mk=0.5)
    slab = S.theta_center_and_mean(S.Geometry("SLAB", (0.005,)), **props)
    cube = S.theta_center_and_mean(S.Geometry("CUBE", (0.005,)), **props)
    brick = S.theta_center_and_mean(S.Geometry("BRICK", (0.005, 0.005, 0.005)), **props)
    assert cube == pytest.approx((slab[0] ** 3, slab[1] ** 3), abs=1e-14) and brick == pytest.approx(cube, abs=1e-14)
    fc = S.theta_center_and_mean(S.Geometry("FINITE_CYLINDER", (0.005, 0.05)), **props)  # long: -> infinite cylinder at the centre
    cyl = S.theta_center_and_mean(S.Geometry("INFINITE_CYLINDER", (0.005,)), **props)
    assert fc[0] == pytest.approx(cyl[0], abs=1e-9)
    for g in (S.Geometry("SPHERE", (0.005,)), S.Geometry("CUBE", (0.005,)), S.Geometry("FINITE_CYLINDER", (0.02, 0.005))):
        c, m = S.theta_center_and_mean(g, **props)
        assert c <= slab[0] + 1e-12 and m <= slab[1] + 1e-12  # the slab of the smallest half-dimension is the slow-side bound
        assert g.bound_half_thickness_m == 0.005
    t_c, t_m = S.core_and_mean_temperature(S.Geometry("SLAB", (0.005,)), t0_c=20.0, bath_c=100.0, **props)
    assert (t_c, t_m) == pytest.approx(PD.core_and_mean_temperature(t0_c=20.0, bath_c=100.0, half_thickness_m=0.005, **props),
                                       abs=1e-9)


# ------------------------------------------------------------------------------------------------ shape map
def test_shape_map_rows_and_precedence():
    rows = S.load_shape_map(ROOT / "registry/shape_map_v1.csv")
    assert all(r.basis == "ASSUMED_DEFAULT" for r in rows)
    pick = lambda cut, cls: S.shape_for(rows, cut, cls).shape  # noqa: E731
    assert pick("SLICED", "MEAT") == "SLAB" and pick("SLICED", "VEGETABLE") == "FINITE_CYLINDER"
    assert pick("DICED", None) == "CUBE" and pick("DICED", "EGG") == "CUBE"  # a cut class wins over an ingredient row
    assert pick(None, "EGG") == "SPHERE" and pick(None, None) == "SLAB_BOUND_UNRESOLVED"
    assert pick("HALVED", "FRUIT") == "SLAB_BOUND_UNRESOLVED" and pick("SHREDDED", None) == "SLAB"
    assert pick("UNMAPPED_CUT", "EGG") == "SLAB_BOUND_UNRESOLVED"
    fc = S.shape_for(rows, "SLICED", "FRUIT")
    g_lo, g_hi = S.geometry_for(fc, 0.0025, bracket=0), S.geometry_for(fc, 0.0025, bracket=2)
    assert g_lo.dims_m[1] == g_hi.dims_m[1] == 0.0025 and g_lo.dims_m[0] < g_hi.dims_m[0]
    assert S.geometry_for(S.shape_for(rows, None, None), 0.0025) is None


def _write_map(path: Path, rows: list[dict]) -> Path:
    with open(ROOT / "registry/shape_map_v1.csv", newline="", encoding="utf-8") as fh:
        header = next(csv.reader(fh))
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in header})
    return path


def test_shape_map_loader_refuses_bad_rows(tmp_path):
    ok = [{"map_id": "SM-1", "cut_class": "NONE", "ingredient_class": "*", "shape": "SLAB_BOUND_UNRESOLVED", "basis": "ASSUMED_DEFAULT"}]
    assert len(S.load_shape_map(_write_map(tmp_path / "ok.csv", ok))) == 1
    bad = [
        ok + [{"map_id": "SM-2", "cut_class": "DICED", "ingredient_class": "*", "shape": "CONE", "basis": "ASSUMED_DEFAULT"}],
        ok + [{"map_id": "SM-2", "cut_class": "DICED", "ingredient_class": "*", "shape": "CUBE", "basis": "MEASURED"}],
        ok + [{"map_id": "SM-2", "cut_class": "NONE", "ingredient_class": "*", "shape": "SLAB", "basis": "ASSUMED_DEFAULT"}],
        ok + [{"map_id": "SM-2", "cut_class": "SLICED", "ingredient_class": "*", "shape": "FINITE_CYLINDER", "basis": "ASSUMED_DEFAULT"}],
        [{"map_id": "SM-2", "cut_class": "DICED", "ingredient_class": "*", "shape": "CUBE", "basis": "ASSUMED_DEFAULT"}],
    ]
    for i, rows in enumerate(bad):
        with pytest.raises(ValueError):
            S.load_shape_map(_write_map(tmp_path / f"bad{i}.csv", rows))


# ------------------------------------------------------------------------------------------------ shape diagnostic tool
def _l1(rid, eid, cut, cls):
    unk = {"value": None, "status": "UNKNOWN", "basis": None, "span": None, "reason": "X"}
    inp = {"piece_size_class": {"value": cut, "status": "MEASURED", "basis": "CUT_HISTORY", "span": None} if cut else unk,
           "matrix_class": {"value": cls, "status": "MEASURED", "basis": "FOOD_GROUP", "span": None} if cls else unk}
    return {"recipe_id": rid, "event_id": eid, "family": "WET_HEAT", "version": "condition-binding-L1-0.2.0-draft", "inputs": inp}


def _l2(rid, eid, L):
    scen = {}
    for name, h in zip(("GENTLE", "TYPICAL", "INTENSE"), (200.0, 600.0, 1500.0)):
        if L is None:
            scen[name] = {"core_end_c": None}
            continue
        core = PD.core_temperature(t0_c=20.0, bath_c=100.0, time_s=600.0, half_thickness_m=L, alpha_m2_s=1.4e-7, h_w_m2k=h, k_w_mk=0.5)
        scen[name] = {"h": h, "half_thickness_m": L, "initial_c": 20.0, "boundary_c": 100.0, "duration_min": 10.0,
                      "core_end_c": round(core, 3)}
    return {"recipe_id": rid, "event_id": eid, "status": "SCENARIO_COMPUTED", "scenarios": scen}


def test_shape_census_counts_only_and_slab_bound(tmp_path):
    tool = _load("s178_phys3_shape_census", "tools/s178_phys3_shape_census.py")
    (tmp_path / "l1").mkdir()
    (tmp_path / "l2").mkdir()
    rid = f"SYN-{SENTINEL}"
    l1 = [_l1(rid, "E1", "DICED", "VEGETABLE"), _l1(rid, "E2", "SLICED", "MEAT"), _l1(rid, "E3", None, "EGG"),
          _l1(rid, "E4", "SLICED", "FRUIT")]
    l2 = [_l2(rid, "E1", 0.008), _l2(rid, "E2", 0.0025), _l2(rid, "E3", None), _l2(rid, "E4", 0.0025), _l2("OTHER", "E1", 0.001)]
    (tmp_path / "l1/part-00000.jsonl").write_text("".join(json.dumps(r) + "\n" for r in l1))
    (tmp_path / "l2/part-00000.jsonl").write_text("".join(json.dumps(r) + "\n" for r in l2))
    rep = tool.run([tmp_path / "l1"], [tmp_path / "l2"])
    D.assert_counts_only(rep)
    assert SENTINEL not in json.dumps(rep) and rep["wired_into_layer2"] is False
    assert rep["l1_heat_events"] == 4 and rep["events_shape_class_would_change"] == 3  # cube, sphere, finite cylinder
    assert rep["events_by_shape"] == {"CUBE": 1, "SLAB": 1, "SPHERE": 1, "FINITE_CYLINDER": 1}
    assert rep["l2_not_joined_to_l1"] == 1 and rep["l2_core_computed"] == 3 and rep["l2_core_computed_shape_would_change"] == 2
    assert rep["slab_recompute_matches_record_by_bracket"] == {"GENTLE": 2, "INTENSE": 2, "TYPICAL": 2}
    assert rep["slab_bound_holds_by_bracket"] == {"GENTLE": 2, "INTENSE": 2, "TYPICAL": 2}
    assert rep["slab_bound_violated_by_bracket"] == {}
    assert sum(rep["core_end_change_if_shape_replaced_slab_by_bracket"]["TYPICAL"].values()) == 2
    assert rep == tool.run([tmp_path / "l1"], [tmp_path / "l2"], workers=2)
    out = tmp_path / "rep.json"
    assert tool.main(["--l1", str(tmp_path / "l1"), "--l2", str(tmp_path / "l2"), "--out", str(out)]) == 0
    with pytest.raises(SystemExit):
        tool.main(["--l1", str(tmp_path / "l1"), "--l2", str(tmp_path / "l2"), "--out", str(out)])
    with pytest.raises(SystemExit):
        tool.main(["--l1", str(tmp_path / "l1"), "--l2", str(tmp_path / "l2"), "--out", str(tmp_path / "x.json"), "--workers", "25"])


def test_verification_tool_writes_reports_once(tmp_path):
    tool = _load("s178_phys3_shape_verification", "tools/s178_phys3_shape_verification.py")
    j, m = tmp_path / "v.json", tmp_path / "v.md"
    assert tool.main(["--out-json", str(j), "--out-md", str(m), "--quick"]) == 0
    rep = json.loads(j.read_text())
    assert rep["all_passed"] is True and rep["checks_passed"] == 15 and rep["wired_into_layer2"] is False
    assert "15 of 15 checks pass" in m.read_text()
    with pytest.raises(SystemExit):
        tool.main(["--out-json", str(j), "--out-md", str(tmp_path / "w.md")])
