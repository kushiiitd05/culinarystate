"""S178 PHYS2 T4-C07-R1: the verification pack runs, passes, can fail, and its committed report is current and reproducible."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path

import pytest

from culinarystate.simulation import physics_drivers as PD
from culinarystate.simulation import phys_verification as V

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "reports/s178/phys/verification_pack_S178.json"
FAST = ("check_lumped_limit", "check_dirichlet_limit", "check_semi_infinite_surface", "check_front_to_series_continuity",
        "check_textbook_constants", "check_one_term_chart_curve", "check_mean_by_quadrature", "check_modal_stepper_convergence",
        "check_modal_stepper_two_stage_superposition", "check_modal_vs_crank_nicolson", "check_n_terms_convergence",
        "check_plank_identities", "check_fickian_slab")


@pytest.mark.parametrize("name", FAST)
def test_check_passes(name):
    r = getattr(V, name)()
    assert r["passed"], r
    assert r["n_cases"] > 0 and r["max_abs_error"] >= 0 and r["tolerance"] > 0


def test_series_against_the_finite_difference_solve_is_tight():
    r = V.check_fd_reference(n=100)  # coarser FD than the report (200): still agrees to the FD discretisation error
    assert r["passed"] and r["max_abs_error"] < 1e-3


def test_reported_error_levels():
    assert V.check_dirichlet_limit()["max_abs_error"] < 1e-7
    assert V.check_semi_infinite_surface()["max_abs_error"] < 1e-12
    assert V.check_mean_by_quadrature()["max_abs_error"] < 1e-10
    assert V.check_front_to_series_continuity()["max_abs_error"] < 1e-6
    assert V.check_n_terms_convergence()["max_abs_error"] < 1e-12
    r = V.check_modal_stepper_convergence()
    assert r["max_abs_error"] < 2e-5
    for orders in r["observed_order_by_case"].values():
        assert all(abs(o - 2.0) < 0.05 for o in orders)  # second-order spatial convergence
    assert V.check_plank_identities()["max_rel_error"] < 1e-6


def test_n_terms_default_has_a_margin():
    r = V.check_n_terms_convergence()
    assert r["n_terms_default"] == PD.N_TERMS and r["largest_needed_n"] * 3 <= PD.N_TERMS
    # and a truncated series would be caught: 3 terms are not converged at the smallest Fo
    assert abs(PD.slab_center_theta(fo=PD.FO_FRONT, bi=1000.0, n_terms=3) - PD.slab_center_theta(fo=PD.FO_FRONT, bi=1000.0, n_terms=400)) > 1e-6


def test_plank_error_falls_with_the_stefan_number():
    r = V.check_plank_vs_stefan_enthalpy(stes=(0.4, 0.2))
    assert r["passed"] and r["error_decreases_with_stefan_number"]
    t = r["results_by_stefan_number"]
    assert t["Ste_0.4"]["plank_over_enthalpy"] < t["Ste_0.2"]["plank_over_enthalpy"] < 1.0  # Plank neglects the sensible heat


def test_references_are_independent_and_correct():
    assert theta_close(V.theta_center_dirichlet(0.2), PD.slab_center_theta(fo=0.2, bi=1e8), 1e-6)
    assert math.isclose(V.theta_lumped(0.5, 2.0), math.exp(-1.0))
    assert math.isclose(V.theta_surface_semi_infinite(1.0, 0.0), 1.0)
    fd = V.fd_slab(1.0, [0.5], n=100)[0.5]
    assert abs(fd[0] - PD.slab_center_theta(fo=0.5, bi=1.0)) < 1e-3
    up = V.fd_diffusion_uptake([0.5], n=100)[0.5]
    assert abs(up - PD.slab_uptake_fraction(d_m2_s=1.0, half_thickness_m=1.0, time_s=0.5)) < 2e-3


def theta_close(a, b, tol):
    return abs(a - b) < tol


def test_the_pack_can_fail(monkeypatch):
    # a driver that is wrong must be reported as failing
    real_mean = PD.slab_mean_theta
    monkeypatch.setattr(PD, "slab_mean_theta", lambda **kw: real_mean(**kw) * 1.01)
    assert not V.check_mean_by_quadrature()["passed"]
    assert not V.check_dirichlet_limit()["passed"]
    monkeypatch.undo()
    real_plank = PD.plank_freezing_time_s
    monkeypatch.setattr(PD, "plank_freezing_time_s", lambda **kw: real_plank(**{**kw, "p": 0.25}))
    assert not V.check_plank_identities()["passed"]
    monkeypatch.undo()
    monkeypatch.setattr(PD, "slab_eigenvalues", lambda bi, n: [(k + 0.5) * math.pi for k in range(n)])  # wrong roots
    assert not V.check_textbook_constants()["passed"]


def test_committed_report_is_complete_current_and_reproducible():
    rep = json.loads(REPORT.read_text())
    assert rep["headline"]["all_passed"] and rep["headline"]["checks"] == 15 == len(rep["checks"])
    assert [c["id"] for c in rep["checks"]] == [f"V{i:02d}" for i in range(1, 16)]
    assert rep["results_sha256"] == hashlib.sha256(json.dumps(rep["checks"], sort_keys=True).encode()).hexdigest()
    for f, h in rep["code_sha256"].items():  # the report is stale if the verified code changed after it was written
        assert hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h, f
    assert rep["recalled_constants_source_status"] == "SOURCE_UNVERIFIED_AGENT_RECALLED"
    assert all("tolerance" in c and "max_rel_error" in c and "max_abs_error" in c for c in rep["checks"])
    md = (ROOT / "reports/s178/phys/verification_pack_S178.md").read_text()
    assert rep["results_sha256"] in md and "SOURCE_UNVERIFIED_AGENT_RECALLED" in md


def test_tool_writes_both_files_reproduces_the_hash_and_never_overwrites(tmp_path):
    spec = importlib.util.spec_from_file_location("s178_phys_verification", ROOT / "tools/s178_phys_verification.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    j, m = tmp_path / "v.json", tmp_path / "v.md"
    assert mod.main(["--out-json", str(j), "--out-md", str(m), "--quick"]) == 0
    rep = json.loads(j.read_text())
    assert rep["headline"]["all_passed"] and m.read_text().startswith("# Physical-layer verification pack")
    again = [mod._round(c) for c in V.run_all(quick=True)]
    assert hashlib.sha256(json.dumps(again, sort_keys=True).encode()).hexdigest() == rep["results_sha256"]
    with pytest.raises(SystemExit):
        mod.main(["--out-json", str(j), "--out-md", str(tmp_path / "other.md")])
