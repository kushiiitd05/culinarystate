"""S178 aa-fit-sim, T5-C07-R2: AA FORM rows (formula, slots, assumptions, validity domain, units; no parameter value).

Synthetic inputs only (test settings, not rate constants or literature values). Lifecycle stays REIMPLEMENTED: no source
figure or table is reproduced here (G24.2 first half needs a human-supplied source), so nothing is REPRODUCED.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

from culinarystate.mechanism import aa_form_registry as R
from culinarystate.mechanism import form_param_val as FPV
from culinarystate.simulation import aa_pilot_fit as FIT
from culinarystate.simulation import sim_aa_1, sim_core as SC, systems as S
from culinarystate.simulation.kinetics import models as M
from culinarystate.simulation.kinetics import units as U
from tests.fixtures import step26b_fixtures as F

ROWS = R.build_forms()
BY_NAME = {next(e[5:] for e in r["external_refs"] if e.startswith("NAME:")): r for r in ROWS}
MODEL_FORM = {"AA_ZERO_ORDER_STUB": "ZERO_ORDER", "AA_FIRST_ORDER_FIXED_T": "FIRST_ORDER",
              "AA_ARRHENIUS_REFERENCE_T": "ARRHENIUS_REF_T", "AA_FIRST_ORDER_ARRHENIUS_ONE_STEP": "FIRST_ORDER_ARRHENIUS",
              "AA_WEIBULL_STUB": "WEIBULL"}


def _numbers(x: Any) -> list[float]:
    if isinstance(x, bool):
        return []
    if isinstance(x, (int, float)):
        return [x]
    if isinstance(x, dict):
        return [n for v in x.values() for n in _numbers(v)]
    if isinstance(x, list):
        return [n for v in x for n in _numbers(v)]
    return []


# ----------------------------------------------------------------------------- the files are the builder's output
def test_registry_files_equal_the_builder_output() -> None:
    assert R.JSONL_PATH.read_text(encoding="utf-8") == R.jsonl_text(ROWS)
    assert R.INDEX_PATH.read_text(encoding="utf-8") == R.index_text(ROWS)
    assert R.CARDS_PATH.read_text(encoding="utf-8") == R.cards_text(ROWS)
    on_disk = [json.loads(line) for line in R.JSONL_PATH.read_text(encoding="utf-8").splitlines()]
    assert on_disk == json.loads(json.dumps(ROWS))


def test_six_rows_in_the_draft_id_block_and_valid() -> None:
    assert len(ROWS) == 6 and R.validate(ROWS) == []
    assert [r["id"] for r in ROWS] == [f"FORM-{900000 + n:06d}" for n in range(1, 7)]
    assert set(BY_NAME) == set(MODEL_FORM) | {"AA_COMPARTMENT_SIM_AA_1"}
    for r in ROWS:
        assert FPV.validate_form(r, form_id_prefix="FORM") == [] or all(
            i.severity != "ERROR" for i in FPV.validate_form(r, form_id_prefix="FORM"))


def test_prefix_decision_24f_stays_open_the_rows_do_not_pretend_otherwise() -> None:
    for r in ROWS:
        assert any(i.code == "FORM_ID_PREFIX_MISMATCH" for i in FPV.validate_form(r, form_id_prefix="MODEL"))
    assert FPV.FORM_ID_PREFIX_DECISION == "OPEN_24f_H4"


def test_the_one_step_form_is_the_one_the_simulate_branch_names() -> None:
    from culinarystate.mechanism import simulate_branch as SB
    assert BY_NAME["AA_FIRST_ORDER_ARRHENIUS_ONE_STEP"]["id"] == SB.FORM_ID


# ----------------------------------------------------------------------------- no value, no overclaim
def test_no_parameter_value_default_or_literature_number_anywhere() -> None:
    allowed = {0, 1, 333.15, 373.15}
    for r in ROWS:
        for s in r["parameter_slots"]:
            assert not ({"value", "default", "prior", "estimate", "low", "high"} & set(s))
        assert set(_numbers(r)) <= allowed, (r["id"], set(_numbers(r)) - allowed)
    text = R.JSONL_PATH.read_text(encoding="utf-8")
    for bad in ('"default"', '"prior"', '"fitted_value"'):
        assert bad not in text


def test_lifecycle_and_verification_are_not_overclaimed() -> None:
    for r in ROWS:
        assert r["lifecycle_status"] == "REIMPLEMENTED" and r["reproduction_refs"] == []
        assert r["verification"]["status"] == "UNVERIFIED" and r["verification"]["verifier"] is None
        assert r["calibration_domain_ref"] is None and r["validated_domain_refs"] == []
        assert r["identifiability_status"] == "NOT_ASSESSED" and r["model_risk_grade"] == "NOT_ASSESSED"
        assert "RESEARCH_ONLY" in r["context_of_use"]
        assert r["created_by"].startswith("AI_AGENT")


@pytest.mark.parametrize("mut, code", [
    (lambda r: r.update(lifecycle_status="REPRODUCED"), "LIFECYCLE_OVERCLAIM"),
    (lambda r: r["verification"].update(status="HUMAN_VERIFIED"), "VERIFICATION_OVERCLAIM"),
    (lambda r: r["parameter_slots"][0].update(value=1.0), "SLOT_HOLDS_VALUE"),
    (lambda r: r["implementation"].update(code_sha256="0" * 64), "CODE_HASH_DRIFT"),
])
def test_validate_catches_overclaims(mut, code) -> None:
    rows = copy.deepcopy(ROWS)
    mut(rows[3])
    assert any(code in p for p in R.validate(rows)), R.validate(rows)


def test_implementation_hash_matches_the_files() -> None:
    for r in ROWS:
        impl = r["implementation"]
        assert hashlib.sha256((R.ROOT / impl["path"]).read_bytes()).hexdigest() == impl["code_sha256"]
        assert impl["library_version"] == M.LIBRARY_VERSION


# ----------------------------------------------------------------------------- parity with the code (slots, units, equation)
@pytest.mark.parametrize("name, form", sorted(MODEL_FORM.items()))
def test_slots_units_and_equation_agree_with_models_py(name: str, form: str) -> None:
    row, mf = BY_NAME[name], M.FORMS[form]
    assert [s["symbol"] for s in row["parameter_slots"]] == list(mf.symbols)
    for s, p in zip(row["parameter_slots"], mf.parameters):
        assert U.dimension(s["dimension"]) == U.dimension(p.dimension)
        assert s["positive"] == (p.transform == "LOG")
        assert FPV.U.dimension(s["dimension"]) is not None
    assert row["equation"]["text_raw"] == mf.equation
    assert row["model_family"] == mf.kin_family or (name == "AA_ARRHENIUS_REFERENCE_T" and
                                                    row["model_family"] == "ARRHENIUS_SECONDARY")
    assert M.check_form_dimensions(mf).verdict == U.CONSISTENT                         # G24.3


def test_composite_slots_agree_with_sim_aa_1() -> None:
    row = BY_NAME["AA_COMPARTMENT_SIM_AA_1"]
    syms = [s["symbol"] for s in row["parameter_slots"]]
    assert set(syms) == set(sim_aa_1.SLOTS)
    for s in row["parameter_slots"]:
        assert U.dimension(s["dimension"]) == U.dimension(sim_aa_1.SLOTS[s["symbol"]].dimension)
    assert row["model_kind"] == "COMPOSITE" and row["implementation"]["path"].endswith("sim_aa_1.py")


def test_rate_constant_slots_carry_their_reaction_order_and_arrhenius_needs_t_ref() -> None:
    for r in ROWS:
        for s in r["parameter_slots"]:
            if s["role"] == "RATE_CONSTANT":
                assert s["reaction_order"]["status"] == "STATED"
                assert U.dimension(s["dimension"]) == U.rate_constant_dimension(s["reaction_order"]["value"])
            if s["symbol"] == "k_ref":
                assert s["needs_T_ref"] is True
            if s["role"] == "ACTIVATION_ENERGY":
                assert U.dimension(s["dimension"]) == U.dimension("ENERGY*AMOUNT^-1")


def test_equation_ast_evaluates_to_the_code_on_synthetic_inputs() -> None:
    errs = R.check_ast_against_models(ROWS)
    assert set(errs) == set(MODEL_FORM.values())
    assert max(errs.values()) <= 1e-12


def test_ast_is_the_declared_expression_not_a_constant() -> None:
    ast = BY_NAME["AA_FIRST_ORDER_ARRHENIUS_ONE_STEP"]["equation"]["ast"]
    env = {"k_ref": 0.003, "Ea": 5.0e4, "T": 350.0, "T_ref": 340.0, "tau": 900.0, "R": U.GAS_CONSTANT_J_PER_MOL_K}
    base = R.eval_ast(ast["rhs"], env)
    assert R.eval_ast(ast["rhs"], {**env, "tau": 1800.0}) == pytest.approx(2 * base, rel=1e-12)
    assert R.eval_ast(ast["rhs"], {**env, "T": 360.0}) < base                              # hotter, more loss
    with pytest.raises(ValueError):
        R.eval_ast({"op": "bogus", "args": []}, env)


# ----------------------------------------------------------------------------- analytic vs numeric (G24.2, second half)
def _aa_run(method: str) -> tuple[SC.SimulationRun, list[tuple[float, float, float]]]:
    sched = [(0.0, 900.0, 355.0), (900.0, 1800.0, 365.0)]
    cond = F.aa_conditions(contact="NO_WATER_CONTACT", ratio=None, kdw="OFF", sched=F.schedule(*sched))
    params = F.aa_params(k_l=None, k_p=None)                       # synthetic test settings (step26b fixtures)
    run = S.simulate(F.AA, cond, params, appdec=F.appdec(), solver=F.solver(method), ms_limits=F.limits(),
                     form_id=F.FORM_ID)
    return run, sched


@pytest.mark.parametrize("method, tol", [("EXPM_PIECEWISE", 1e-9), ("RK4_FIXED", 1e-6), ("TRAPEZOID_FIXED", 1e-6)])
def test_sim_aa_1_with_no_water_contact_reduces_to_the_first_order_arrhenius_form(method: str, tol: float) -> None:
    run, sched = _aa_run(method)
    assert run.status == "COMPLETED", run.reasons
    th = {p.symbol: p.value_si for p in F.aa_params(k_l=None, k_p=None)}
    ln_a = M.ln_retention_first_order_piecewise(th["k_ref"], th["Ea"], th["T_ref"], sched, run.times_s)
    got = run.outputs["retention_tissue"]                               # type: ignore[index]
    for g, want in zip(got, ln_a):
        assert abs(g - math.exp(want)) / math.exp(want) <= tol
    assert run.states["A_w"] == (0.0,) * len(run.times_s)               # type: ignore[index]  no leaching, no water


def test_form_prediction_equals_the_analytic_solution_at_constant_temperature() -> None:
    mf = M.FORMS["FIRST_ORDER_ARRHENIUS"]
    th = {"k_ref": 2.0e-4, "Ea": 7.0e4}
    tau = [0.0, 600.0, 1800.0]
    pred = mf.predict(th, {"tau_s": tau, "T_K": [365.0] * 3}, {"T_ref_K": 360.0})
    k = M.arrhenius_rate(th["k_ref"], th["Ea"], [365.0], 360.0)[0]
    for p, t in zip(pred, tau):
        assert abs(p - (-k * t)) <= 1e-12 * max(1.0, abs(k * t))


# ----------------------------------------------------------------------------- validity-domain fields
def test_validity_domain_fields_come_from_the_preregistration_not_from_a_fit() -> None:
    lo, hi = (float(Fraction(str(x)) + Fraction(27315, 100)) for x in (FIT.T_MIN_C, FIT.T_MAX_C))
    assert (lo, hi) == R.T_RANGE_K
    for name in ("AA_ARRHENIUS_REFERENCE_T", "AA_FIRST_ORDER_ARRHENIUS_ONE_STEP", "AA_COMPARTMENT_SIM_AA_1"):
        ms = BY_NAME[name]["ms_limits"]
        assert ms["status"] == "STATED" and ms["temperature_range"] == {
            "status": "RANGE", "low": lo, "high": hi, "unit": "K", "raw": ms["temperature_range"]["raw"]}
        assert "WATER" in ms["medium"] and "STEAM" in ms["medium"]
        assert "pressure" in ms["pressure_note"] or "ambient" in ms["pressure_note"]
    for name in ("AA_ZERO_ORDER_STUB", "AA_FIRST_ORDER_FIXED_T", "AA_WEIBULL_STUB"):
        assert BY_NAME[name]["ms_limits"]["status"] == "NOT_YET_STATED"
        assert BY_NAME[name]["ms_limits"]["temperature_range"] is None


def test_assumptions_state_the_pilot_scope_conditions() -> None:
    text = " ".join(a["constraint_expr"] for a in BY_NAME["AA_FIRST_ORDER_ARRHENIUS_ONE_STEP"]["assumptions"])
    for must in ("REDUCED_L_ASCORBIC_ACID", "BASIS_MISMATCH_TOTAL_VITC", "NO_WATER_CONTACT", "BATH_EQUALS_PRODUCT",
                 "pH", "ascorbate-oxidase", "K"):
        assert must in text, must
    for r in ROWS:
        assert all(a["kind"] == "CONSTRAINT" and a["consequence"] == "INVALIDATES_FROM_VIOLATION"
                   for a in r["assumptions"])


def test_model_cards_say_what_is_not_claimed() -> None:
    text = Path(R.CARDS_PATH).read_text(encoding="utf-8")
    for must in ("UNVERIFIED", "no parameter value", "REPRODUCED", "NOT_MINTED"):
        assert must in text
    assert text.count("## FORM-9") == 6


def test_builder_is_deterministic_and_does_not_touch_the_ledgers() -> None:
    assert R.jsonl_text() == R.jsonl_text()
    src = Path(R.__file__).read_text(encoding="utf-8")
    assert "ledgers/data" not in src.replace("``ledgers/data/_ids.jsonl``", "")
