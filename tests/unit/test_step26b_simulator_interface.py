"""Step 26b one-interface simulator contract (S159, DRAFT_PENDING_26_0_H4).

Synthetic only (tests/fixtures/step26b_fixtures.py): no literature value, no PARAM row, no ledger. Card (Plan v2
Step 26): sim_aa_1 and sim_chl_1 behind one interface; every parameter a required input without default; any
UNKNOWN input or applicability UNKNOWN / NOT_APPLICABLE => SIM_PROHIBITED (R-15); deterministic; provenance.
"""
from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from culinarystate.simulation import sim_aa_1, sim_chl_1, sim_core as SC, systems as S
from tests.fixtures import step26b_fixtures as F

MODULES = (SC, sim_aa_1, sim_chl_1, S)


def run_aa(**kw):
    kw.setdefault("appdec", F.appdec())
    kw.setdefault("solver", F.solver())
    kw.setdefault("ms_limits", F.limits())
    kw.setdefault("form_id", F.FORM_ID)
    cond = kw.pop("conditions", None) or F.aa_conditions()
    params = kw.pop("params", None)
    return S.simulate(F.AA, cond, F.aa_params() if params is None else params, **kw)


# ----------------------------------------------------------------------------- module contract
@pytest.mark.parametrize("mod", MODULES)
def test_status_header_is_draft_pending_26_0_h4(mod) -> None:
    assert mod.STATUS == "DRAFT_PENDING_26_0_H4"
    assert "DRAFT_PENDING_26_0_H4" in Path(mod.__file__).read_text(encoding="utf-8").splitlines()[0]


@pytest.mark.parametrize("mod", MODULES)
def test_module_holds_no_float_literal_so_no_default_or_literature_value(mod) -> None:
    tree = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
    floats = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, (float, complex))]
    assert floats == []


@pytest.mark.parametrize("mod", MODULES)
def test_module_is_short_and_has_no_ledger_path(mod) -> None:
    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert len(src.splitlines()) < 800
    assert "ledgers/" not in src.replace("ledgers/sim/", "") and "open(" not in src


def test_one_interface_registers_exactly_the_two_card_systems() -> None:
    assert set(S.SYSTEMS) == {F.AA, F.CHL}
    for sid, spec in S.SYSTEMS.items():
        assert spec.system_id == sid and spec.card_ref and spec.model_structure_id
        assert len(spec.initial_state) == len(spec.state_names)
        assert all(len(c) == len(spec.state_names) for c in spec.conservation)


def test_exact_si_constants_only() -> None:
    from fractions import Fraction
    assert SC.CELSIUS_OFFSET_K == Fraction(27315, 100)
    assert SC.SECONDS_PER_MINUTE == 60


# ----------------------------------------------------------------------------- APPDEC gate (R-15)
def test_simulate_runs_only_with_a_simulate_appdec_for_the_event() -> None:
    out = run_aa()
    assert out.status == "COMPLETED" and out.reasons == ()
    assert out.provenance["appdec_id"] == F.appdec()["appdec_id"]


def test_missing_appdec_is_refused() -> None:
    out = run_aa(appdec=None)
    assert out.status == "SIM_PROHIBITED" and "APPDEC_MISSING" in out.reasons and out.states is None


def test_unknown_applicability_never_simulates() -> None:
    rec = F.appdec(event_resolved=False)
    assert rec["applicability"] == "UNKNOWN" and rec["route"] != "SIMULATE"
    out = run_aa(appdec=rec)
    assert out.status == "SIM_PROHIBITED" and f"APPDEC_ROUTE_{rec['route']}" in out.reasons
    assert out.states is None and out.outputs is None


def test_non_simulate_routes_are_refused() -> None:
    rec = F.appdec(domain_flag="EXTRAPOLATED_WITHIN_LIMITS")
    assert rec["route"] == "QUALITATIVE"
    assert "APPDEC_ROUTE_QUALITATIVE" in run_aa(appdec=rec).reasons
    rec = F.appdec(evidence_precheck="DIRECT")
    assert rec["route"] == "DIRECT"
    assert "APPDEC_ROUTE_DIRECT" in run_aa(appdec=rec).reasons


def test_appdec_for_another_event_is_refused() -> None:
    out = run_aa(appdec=F.appdec(event_id="E2"))
    assert "APPDEC_OTHER_EVENT" in out.reasons


def test_tampered_or_invalid_appdec_is_refused() -> None:
    rec = copy.deepcopy(F.appdec(event_resolved=False))
    rec["route"] = "SIMULATE"                      # invariant breach caught by the APPDEC schema
    assert "APPDEC_INVALID" in run_aa(appdec=rec).reasons
    rec = copy.deepcopy(F.appdec())
    rec["query"]["case_id"] = "SYNTH-CASE-OTHER"   # schema-valid edit, content id no longer matches
    assert "APPDEC_ID_MISMATCH" in run_aa(appdec=rec).reasons


# ----------------------------------------------------------------------------- required inputs, no default
def test_every_parameter_is_required_without_default() -> None:
    full = F.aa_params()
    for i, missing in enumerate(full):
        params = full[:i] + full[i + 1:]
        out = run_aa(params=params)
        assert out.status == "SIM_PROHIBITED" and f"PARAM_MISSING_{missing.symbol.upper()}" in out.reasons


def test_unexpected_or_duplicate_parameters_are_refused() -> None:
    out = run_aa(params=F.aa_params(tau_h=100.0))            # tau_h without the lag mode
    assert "PARAM_UNEXPECTED_TAU_H" in out.reasons
    out = run_aa(params=F.aa_params() + [F.p("k_ref", 1e-4, "1/s", pid="SYNTH-PARAM-DUP")])
    assert "PARAM_DUPLICATE_K_REF" in out.reasons


def test_parameter_units_must_be_coherent_si_of_the_slot_dimension() -> None:
    bad = [x if x.symbol != "k_ref" else F.p("k_ref", 1e-2, "1/min") for x in F.aa_params()]
    assert "PARAM_UNIT_K_REF" in run_aa(params=bad).reasons            # not coherent SI
    bad = [x if x.symbol != "Ea" else F.p("Ea", 7e4, "J") for x in F.aa_params()]
    assert "PARAM_UNIT_EA" in run_aa(params=bad).reasons               # wrong dimension
    bad = [x if x.symbol != "K_p" else F.p("K_p", 2e-3, "1") for x in F.aa_params()]
    assert "PARAM_UNIT_K_P" in run_aa(params=bad).reasons


def test_parameter_constraints() -> None:
    for sym, val, unit in (("k_ref", -1e-4, "1/s"), ("T_ref", 0.0, "K"), ("K_p", 0.0, "m^3/kg"),
                           ("k_L", -1e-6, "1/s")):
        bad = [x if x.symbol != sym else F.p(sym, val, unit) for x in F.aa_params()]
        assert f"PARAM_CONSTRAINT_{sym.upper()}" in run_aa(params=bad).reasons


def test_matrix_class_mismatch_is_no_compatible_set() -> None:
    bad = [x if x.symbol != "Ea" else F.p("Ea", 7e4, "J/mol", matrix="MATRIX_Y") for x in F.aa_params()]
    out = run_aa(params=bad)
    assert out.status == "SIM_PROHIBITED" and "NO_COMPATIBLE_SET_EA" in out.reasons


def test_param_value_structural_contract() -> None:
    with pytest.raises(SC.SimulationError):
        SC.ParamValue("PARAM-1", "k_ref", 1e-4, "1/s", "MATRIX_X", None, None, "PARAM_RECORD")   # id pattern
    with pytest.raises(SC.SimulationError):
        SC.ParamValue("SYNTH-PARAM-K", "k_ref", float("nan"), "1/s", "MATRIX_X", None, None, "SYNTHETIC")
    with pytest.raises(SC.SimulationError):
        SC.ParamValue("SYNTH-PARAM-K", "k_ref", True, "1/s", "MATRIX_X", None, None, "SYNTHETIC")
    with pytest.raises(SC.SimulationError):
        SC.ParamValue("SYNTH-PARAM-K", "k_ref", 1e-4, "1/s", "matrix x", None, None, "SYNTHETIC")
    with pytest.raises(SC.SimulationError):
        SC.ParamValue("SYNTH-PARAM-K", "k_ref", 1e-4, "1/s", "MATRIX_X", None, None, "LITERATURE")
    ok = SC.ParamValue("PARAM-000001", "k_ref", 1e-4, "1/s", "MATRIX_X", None, None, "PARAM_RECORD")
    assert ok.origin == "PARAM_RECORD"


def test_param_from_24a_record_needs_an_exact_si_value() -> None:
    rec = {"id": "PARAM-000007", "record_type": "PARAM", "status": "ACTIVE", "slot_symbol": "k_ref",
           "value_si": {"status": "CONVERTED_EXACT", "value": 1e-4, "unit_si": "1/s"},
           "verification": {"status": "UNVERIFIED"}}
    pv = SC.param_from_record(rec, matrix_class="MATRIX_X", piece_size_class=None, ph_validity=None)
    assert (pv.param_id, pv.symbol, pv.value_si, pv.unit_si, pv.origin) == (
        "PARAM-000007", "k_ref", 1e-4, "1/s", "PARAM_RECORD")
    for bad in ({**rec, "value_si": {"status": "NOT_CONVERTED", "value": None, "unit_si": None}},
                {**rec, "status": "RETRACTED"}, {**rec, "record_type": "VAL"}):
        with pytest.raises(SC.SimulationError):
            SC.param_from_record(bad, matrix_class="MATRIX_X", piece_size_class=None, ph_validity=None)


def test_unknown_condition_inputs_are_refused() -> None:
    out = run_aa(conditions=F.aa_conditions(ratio=None))
    assert "INPUT_MISSING_WATER_RATIO_M3_PER_KG" in out.reasons
    out = run_aa(conditions=F.aa_conditions(contact="UNKNOWN"))
    assert "INPUT_INVALID_MEDIUM_CONTACT" in out.reasons
    out = run_aa(conditions=F.aa_conditions(kdw="UNKNOWN"))
    assert "INPUT_INVALID_K_DW_MODE" in out.reasons
    out = run_aa(conditions=F.aa_conditions(mode="LUMPED_LAG", tp0=None), params=F.aa_params(tau_h=120.0))
    assert "INPUT_MISSING_INITIAL_PRODUCT_TEMPERATURE" in out.reasons


def test_ms_limits_duration_and_output_times() -> None:
    assert "OUT_OF_MS_LIMITS_TEMPERATURE" in run_aa(ms_limits=F.limits(t_max=360.0)).reasons
    out = run_aa(conditions=F.aa_conditions(duration=2400.0))
    assert "DURATION_BEYOND_SCHEDULE" in out.reasons
    out = run_aa(solver=F.solver(times=(0.0, 2400.0)))
    assert "OUTPUT_TIME_BEYOND_DURATION" in out.reasons


def test_solver_config_is_validated_and_has_no_default() -> None:
    with pytest.raises(SC.SimulationError):
        SC.SolverConfig("SCIPY_BDF", (0.0, 1.0), None, 1e-12, None, None, 1e-12, 1e-12)   # rtol required
    with pytest.raises(SC.SimulationError):
        SC.SolverConfig("TRAPEZOID_FIXED", (0.0, 1.0), None, None, None, None, 1e-12, 1e-12)  # steps required
    for fixed_step in ("RK4_FIXED", "TRAPEZOID_FIXED"):
        with pytest.raises(SC.SimulationError):
            SC.SolverConfig(fixed_step, (0.0, 1.0), None, None, 8, None, 1e-12, 1e-12)   # stiffness limit
    with pytest.raises(SC.SimulationError):
        SC.SolverConfig("EULER", (0.0, 1.0), None, None, None, None, 1e-12, 1e-12)
    with pytest.raises(SC.SimulationError):
        SC.SolverConfig("EXPM_PIECEWISE", (1.0, 0.5), None, None, None, None, 1e-12, 1e-12)  # not increasing
    with pytest.raises(SC.SimulationError):
        SC.SolverConfig("EXPM_PIECEWISE", (0.0, 1.0), 1e-8, None, None, None, 1e-12, 1e-12)  # unused setting


def test_analytic_solver_refuses_a_time_varying_product_temperature() -> None:
    out = run_aa(conditions=F.aa_conditions(mode="LUMPED_LAG", tp0=300.0), params=F.aa_params(tau_h=120.0))
    assert "SOLVER_NOT_APPLICABLE_TIME_VARYING" in out.reasons


# ----------------------------------------------------------------------------- outputs, provenance, determinism
def test_outputs_carry_provenance_status_and_no_validation_claim() -> None:
    out = run_aa()
    prov = out.provenance
    assert prov["system_id"] == F.AA and prov["form_id"] == F.FORM_ID
    assert prov["kinetic_forms"] == ["ARRHENIUS_REF_T"]
    assert prov["param_ids"] == sorted(x.param_id for x in F.aa_params())
    assert len(prov["solver_config_sha256"]) == 64 and len(prov["code_sha256"]) == 64
    assert len(prov["inputs_sha256"]) == 64 and prov["solver"]["method"] == "EXPM_PIECEWISE"
    assert prov["condition_source"] == "CONSTRUCTED_CASE"
    assert out.validation_status == "NOT_VALIDATED" and out.domain_flag == "NOT_VALIDATED"
    assert out.is_evidence is False and out.sim_run_id is None and out.label == "DRAFT_PENDING_26_0_H4"
    assert "SYNTHETIC_PARAMETERS" in out.flags
    assert out.times_s == (0.0, 600.0, 1200.0, 1800.0)


def test_runs_are_deterministic_and_hash_stable() -> None:
    a, b = run_aa(), run_aa()
    assert a.run_sha256 == b.run_sha256 and a.states == b.states
    c = run_aa(params=F.aa_params(k_ref=2.1e-4))
    assert c.run_sha256 != a.run_sha256 and c.provenance["inputs_sha256"] != a.provenance["inputs_sha256"]
    d = run_aa(solver=F.solver(mb_tol=1e-11))
    assert d.provenance["solver_config_sha256"] != a.provenance["solver_config_sha256"]


def test_form_id_is_required_and_patterned() -> None:
    with pytest.raises(SC.SimulationError):
        run_aa(form_id="")
    with pytest.raises(SC.SimulationError):
        run_aa(form_id="FORM-12")
    assert run_aa(form_id="MODEL-000002").provenance["form_id"] == "MODEL-000002"


def test_unknown_system_is_a_programming_error() -> None:
    with pytest.raises(SC.SimulationError):
        S.simulate("sim_other", F.aa_conditions(), F.aa_params(), appdec=F.appdec(), solver=F.solver(),
                   ms_limits=F.limits(), form_id=F.FORM_ID)


def test_open_items_are_listed() -> None:
    joined = " ".join(S.OPEN_FOR_HUMANS)
    for word in ("26.0", "g(pH)", "K_p", "Choi", "M&S", "KiSAO", "tau_h"):
        assert word in joined
