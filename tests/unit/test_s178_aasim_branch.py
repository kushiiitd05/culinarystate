"""S178 aa-fit-sim, T5-C11-R4: the router SIMULATE branch (guard, domain gate, engine, sim_aa_1, interval).

Every parameter, fit and VAL record below is a SYNTHETIC TEST_ONLY fixture built inside this file: shapes are real, values
are test settings (not rate constants, activation energies or literature values) and no human verified any of it. The
``verifier: Kush`` strings only satisfy the PARAM / VAL schema enum so the guard's own checks can be exercised; they are not
signatures. Real-data behaviour is asserted separately: it refuses.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import random
from typing import Any

import numpy as np
import pytest

from culinarystate.mechanism import applicability as AP
from culinarystate.mechanism import process_signatures as PS
from culinarystate.mechanism import simulate_branch as SB
from culinarystate.simulation import aa_pilot_fit as FIT
from tests.fixtures import form_param_val_v1_fixtures as FX
from tests.fixtures.step22a_23a_fixtures import mech, rule

HIER = PS.read_process_hierarchy()
STEAM = "PROC-000022"
ING = "ING-000184"                       # orange juice in the real ING ledger (used only as an opaque id here)
OTHER_ING = "ING-000103"
TEST = SB.TestOnlyFixtures("synthetic fixtures built inside tests/unit/test_s178_aasim_branch.py")
CLASS = "ACIDIC_FRUIT_PULP_TEST"


# ----------------------------------------------------------------------------- synthetic fixtures (TEST_ONLY)
def _fit() -> dict[str, Any]:
    ea, a, temps = 60_000.0, (-3.0, -3.4, -2.8), (70, 80, 90, 95)     # synthetic test settings, not literature values
    rng = np.random.default_rng(0)
    rows, i = [], 0
    for p, ai in enumerate(a):
        for t in temps:
            i += 1
            x = 1 / (t + 273.15) - 1 / FIT.T_REF_K
            rows.append({"row_id": f"R{i:03d}", "candidate_id": f"P{p}", "row_type": "K_AT_T", "T": float(t),
                         "k": math.exp(ai - ea / FIT.R * x + rng.normal(0, 0.05)), "order": "first"})
    return FIT.fit_model_a(rows)


def _frozen(fit: dict[str, Any]) -> dict[str, Any]:
    return {"record": "AA_PILOT_MODEL_A_FIT", "status": "FROZEN_BEFORE_SIM_VAL", "sim_val_opened": False,
            "returned_sha256": {"Kush": "a" * 64, "Parv": "b" * 64}, "excluded_by_verdict": {},
            "excluded_by_inclusion": {}, "fit": fit, "code_sha256": {}, "notes": "TEST_ONLY synthetic fit"}


def _sha(rec: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()


def _form() -> dict[str, Any]:
    from culinarystate.mechanism import aa_form_registry as R
    f = next(r for r in R.build_forms() if r["id"] == SB.FORM_ID)
    f.update(lifecycle_status="REPRODUCED", reproduction_refs=["SYNTH-REPRO-TEST-ONLY"],
             notes="TEST_ONLY: lifecycle and review fields are fixture shape, nothing was reproduced or reviewed",
             verification={"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": FX.NOW, "ai_reviewer": None,
                           "notes": "TEST_ONLY"})
    return f


def _param(n: int, slot: str, value: float, unit: str, sha: str) -> dict[str, Any]:
    p = FX.param(n, form_id=SB.FORM_ID, slot_symbol=slot, value=value, unit=unit, source_class="PROJECT_REFIT",
                 order=1 if slot == "k_ref" else None)
    p["value_provenance"].update(fit_run_id=f"FITRUN-{sha[:16]}", fitting_library_version="fixture")
    p["value_si"] = {"status": "CONVERTED_EXACT", "value": value, "unit_si": unit}
    p["T_ref"] = {"status": "MEASURED", "value": FIT.T_REF_K, "unit": "K", "raw": FX.Z} if slot == "k_ref" else None
    p["verification"] = {"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": FX.NOW}
    p["partition"] = "SIM_CALIBRATION"
    p["notes"] = "TEST_ONLY synthetic PARAM fixture"
    return p


def _val(param_ids: list[str], **over: Any) -> dict[str, Any]:
    v = FX.val(1, form_id=SB.FORM_ID, param_ids=tuple(param_ids), eval_ids=("KIN-000002",), tier="V1_IN_DOMAIN")
    v.update(verification={"status": "HUMAN_VERIFIED", "verifier": "Kush", "verified_at": FX.NOW},
             study_disjoint={"status": "YES", "lineage_proof": "TEST_ONLY"}, matrix_relation="SAME_CLASS",
             verdict="MEETS_PREREGISTERED_CRITERIA", preregistration_ref="TEST_ONLY-PREREG", val_plan_sha256="c" * 64,
             may_define_validated_domain=True, notes="TEST_ONLY synthetic VAL fixture")
    v.update(over)
    return v


def make_artifacts(*, val_over: dict[str, Any] | None = None, test_only: bool = True) -> SB.Artifacts:
    fit = _fit()
    frozen = _frozen(fit)
    sha = _sha(frozen)
    params = [_param(1, "Ea", fit["Ea_J_per_mol"], "J/mol", sha)]
    params += [_param(2 + i, "k_ref", math.exp(fit["intercepts"][p]) / 60.0, "1/s", sha)
               for i, p in enumerate(fit["papers"])]
    form = _form()
    vals = (_val([p["id"] for p in params], **(val_over or {})),)
    return SB.Artifacts({form["id"]: form}, SB.FORM_ID, tuple(params), vals, frozen, sha, sha,
                        TEST if test_only else None)


def make_gate(ph_mode: str = "PH_C", ph_range: tuple[float, float] | None = None) -> SB.DomainGate:
    return SB.DomainGate({ING: CLASS}, frozenset({CLASS}),
                         {"STEAM": SB.NO_WATER, "WATER_BATH_SEALED": SB.NO_WATER, "WATER": SB.IMMERSION},
                         (FIT.T_MIN_C, FIT.T_MAX_C), ph_mode, ph_range, "TEST_ONLY lock")


def _overrides(ev: SB.AAEvent, ge: SB.GateEval) -> dict[str, Any]:
    """Scaffolding for the SYNTHETIC mechanism entry (matrix 'synthetic class', one state, one pH axis)."""
    return {"target_state_key": "synthetic_target", "matrix": "synthetic class", "states": {"synthetic_state": "SYNTH_A"},
            "axes": (AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"),)}


def make_config(safety: str = "NO", ph_lookup=None) -> SB.BranchConfig:
    return SB.BranchConfig(SC_LIMITS, 1e-9, 1e-9, safety, ph_lookup, _overrides)


from culinarystate.simulation import sim_core as SC  # noqa: E402

SC_LIMITS = SC.MSLimits(373.15, "TEST_ONLY ms limits")


def make_branch(*, arts: SB.Artifacts | None = None, gate: SB.DomainGate | None = None,
                config: SB.BranchConfig | None = None, with_mech: bool = True) -> SB.SimulateBranch:
    entries = [mech()] if with_mech else []
    sigs = PS.build_signatures([PS.SignatureRule(**rule(process_ref=STEAM, mechanism_keys=("SYNTH_FIXTURE_ONE",)))],
                               entries, HIER, heat_transfer_mode_ids=frozenset()).signatures if with_mech else ()
    return SB.SimulateBranch(arts or make_artifacts(), gate or make_gate(), config or make_config(),
                             signatures=sigs, entries=entries)


def item(**over: Any) -> dict[str, Any]:
    d = {"event_id": "E1", "process_id": STEAM, "ingredient_id": ING, "route": "UNKNOWN",
         "gates": {"presence": "PRESENT", "lot_context": "SINGLE_MEMBER"}, "prior_process": []}
    d.update(over)
    return d


def event(t: Any = 95.0, d: Any = 30.0, *, medium: str | None = "STEAM", ing: str | None = ING,
          t_basis: str | None = "TEXT_STATED", d_basis: str | None = "TEXT_STATED", **kw: Any) -> SB.AAEvent:
    return SB.AAEvent("E1", STEAM, ing, SB.Q(t, "degC", t_basis if t is not None else None),
                      SB.Q(d, "min", d_basis if d is not None else None), medium, "PROCESS_DEFINITION", **kw)


def run(br: SB.SimulateBranch, ev: SB.AAEvent, it: dict[str, Any] | None = None, pre: str = "NONE") -> SB.Outcome:
    return br.evaluate(ev, it or item(), pre, HIER, "SVAR-000009")


# ----------------------------------------------------------------------------- real data: unreachable today
def test_real_branch_refuses_on_real_data_today() -> None:
    """TRIPWIRE: when real PARAM rows, a frozen fit and a VAL record exist this fails on purpose and a human re-reads it."""
    br = SB.SimulateBranch.from_repo()
    assert br.guard.mode == "REAL" and br.guard.allowed is False
    assert {"PARAM_ROWS_ABSENT", "FROZEN_FIT_ABSENT", "STEP27_HELDOUT_ABSENT", "FORM_NOT_REPRODUCED",
            "FORM_NOT_HUMAN_REVIEWED"} <= set(br.guard.reasons)
    assert br.gate is None and br.entries == () and br.signatures == ()
    out = br.evaluate(event(), item(), "NONE", HIER, "SVAR-000009")
    assert out.simulated is False and out.status == "NOT_SIMULATED"
    assert "DOMAIN_GATE_REGISTRY_ABSENT" in out.reasons and "PARAM_UNCONFIRMABLE" in out.reasons
    assert out.engine_route == "UNKNOWN"


def test_real_branch_can_never_be_test_only() -> None:
    assert SB.SimulateBranch.from_repo().guard.mode == "REAL"
    assert SB.load_artifacts().test_only is None


def test_test_only_marker_is_constructed_only_in_tests() -> None:
    import re
    from pathlib import Path
    src = Path(SB.__file__).read_text(encoding="utf-8")
    assert len(re.findall(r"TestOnlyFixtures\(", src)) == 0         # the class is declared, never instantiated, in src
    with pytest.raises(SB.SimulateBranchError):
        SB.TestOnlyFixtures("  ")


# ----------------------------------------------------------------------------- guard
def test_guard_allows_complete_synthetic_artifacts_in_test_only_mode() -> None:
    g = SB.check_guard(make_artifacts())
    assert g.allowed and g.mode == "TEST_ONLY" and g.reasons == () and g.may_define_validated_domain
    assert len(g.param_ids) == 4 and len(g.val_ids) == 1 and g.form_id == SB.FORM_ID


def test_guard_refuses_test_only_artifacts_in_real_mode() -> None:
    g = SB.check_guard(make_artifacts(test_only=False))
    assert not g.allowed and "TEST_ONLY_ARTIFACT_IN_REAL_MODE" in g.reasons and g.mode == "REAL"


def test_guard_refuses_unmarked_artifact_mixed_into_test_only() -> None:
    a = make_artifacts()
    params = list(a.params)
    params[0] = {**params[0], "notes": "plain note"}
    g = SB.check_guard(SB.Artifacts(a.forms_by_id, a.form_id, tuple(params), a.vals, a.frozen_fit, a.frozen_fit_sha256,
                                    a.recorded_fit_sha256, a.test_only))
    assert "REAL_ARTIFACT_MIXED_WITH_TEST_ONLY" in g.reasons and not g.allowed


def _mut(a: SB.Artifacts, fn) -> SB.Artifacts:
    d = {k: copy.deepcopy(getattr(a, k)) for k in ("forms_by_id", "form_id", "params", "vals", "frozen_fit",
                                                  "frozen_fit_sha256", "recorded_fit_sha256")}
    fn(d)
    return SB.Artifacts(d["forms_by_id"], d["form_id"], tuple(d["params"]), tuple(d["vals"]), d["frozen_fit"],
                        d["frozen_fit_sha256"], d["recorded_fit_sha256"], a.test_only)


def _set(path: str, value: Any):
    def f(d):
        tgt = d
        *head, last = path.split(".")
        for h in head:
            tgt = tgt[int(h)] if h.isdigit() else tgt[h]
        if last.isdigit():
            tgt[int(last)] = value
        else:
            tgt[last] = value
    return f


def _drop(key: str):
    return lambda d: d.__setitem__(key, ())


CASES = [
    ("no params", _drop("params"), "PARAM_ROWS_ABSENT"),
    ("param unverified", _set("params.0.verification", {"status": "UNVERIFIED"}), "PARAM_NOT_HUMAN_VERIFIED"),
    ("param AI prechecked", _set("params.1.verification", {"status": "AI_PRECHECKED"}), "PARAM_NOT_HUMAN_VERIFIED"),
    ("partition pending", _set("params.0.partition", "PENDING_15B"), "PARAM_PARTITION_NOT_SIM_CALIBRATION"),
    ("partition locked", _set("params.0.partition", "SIM_VALIDATION_LOCKED"), "PARAM_PARTITION_NOT_SIM_CALIBRATION"),
    ("param retracted", _set("params.0.status", "RETRACTED"), "PARAM_NOT_ACTIVE"),
    ("param value unknown", _set("params.0.value", {"status": "UNKNOWN", "value": None, "low": None, "high": None}),
     "PARAM_VALUE_NOT_NUMERIC"),
    ("param SI not converted", _set("params.0.value_si", {"status": "NOT_CONVERTED", "value": None, "unit_si": None}),
     "PARAM_SI_NOT_CONVERTED_EXACT"),
    ("param fit run", _set("params.0.value_provenance.fit_run_id", "FITRUN-0000000000000000"), "PARAM_FIT_RUN_MISMATCH"),
    ("param value drift", lambda d: (_set("params.0.value.value", 12345.0)(d), _set("params.0.value_si.value", 12345.0)(d)),
     "PARAM_FIT_VALUE_MISMATCH"),
    ("no frozen fit", _set("frozen_fit", None), "FROZEN_FIT_ABSENT"),
    ("fit not frozen", _set("frozen_fit.status", "DRAFT"), "FROZEN_FIT_NOT_FROZEN_BEFORE_SIM_VAL"),
    ("sim val opened", _set("frozen_fit.sim_val_opened", True), "FROZEN_FIT_NOT_FROZEN_BEFORE_SIM_VAL"),
    ("hash not recorded", _set("recorded_fit_sha256", None), "FROZEN_FIT_HASH_NOT_RECORDED"),
    ("hash mismatch", _set("recorded_fit_sha256", "d" * 64), "FROZEN_FIT_HASH_MISMATCH"),
    ("one human only", _set("frozen_fit.returned_sha256", {"Kush": "a" * 64}), "DUAL_HUMAN_VERIFICATION_NOT_EVIDENCED"),
    ("one paper", _set("frozen_fit.fit.n_papers", 1), "FROZEN_FIT_NEED_DATA"),
    ("wrong model", _set("frozen_fit.fit.model", "B_SEPARATE_EA"), "FROZEN_FIT_RECORD_INVALID"),
    ("no VAL", _drop("vals"), "STEP27_HELDOUT_ABSENT"),
    ("VAL not evaluated", _set("vals.0.verdict", "NOT_EVALUATED"), "STEP27_NOT_EVALUATED"),
    ("VAL failed", _set("vals.0.verdict", "FAILS_PREREGISTERED_CRITERIA"), "STEP27_FAILED_PREREGISTERED_CRITERIA"),
    ("VAL not disjoint", _set("vals.0.study_disjoint", {"status": "UNKNOWN", "lineage_proof": None}),
     "STEP27_NOT_STUDY_DISJOINT"),
    ("VAL no plan hash", _set("vals.0.val_plan_sha256", None), "STEP27_PLAN_HASH_MISSING"),
    ("VAL unreviewed", _set("vals.0.verification", {"status": "AI_PRECHECKED"}), "STEP27_NOT_HUMAN_VERIFIED"),
    ("VAL no eval series", _set("vals.0.eval_series_ids", []), "STEP27_NO_EVAL_SERIES"),
    ("form only reimplemented", _set("forms_by_id.FORM-900004.lifecycle_status", "REIMPLEMENTED"), "FORM_NOT_REPRODUCED"),
    ("form unreviewed", _set("forms_by_id.FORM-900004.verification", {"status": "UNVERIFIED"}), "FORM_NOT_HUMAN_REVIEWED"),
    ("form absent", _set("forms_by_id", {}), "FORM_ABSENT"),
    ("param for another form", _set("params.0.form_id", "FORM-900001"), "PARAM_FORM_MISMATCH"),
    ("VAL for other params", _set("vals.0.param_set_ids", ["PARAM-000099"]), "STEP27_NOT_FOR_THESE_PARAMS"),
]


@pytest.mark.parametrize("name, fn, code", CASES, ids=[c[0] for c in CASES])
def test_guard_refuses_each_missing_prerequisite(name, fn, code) -> None:
    g = SB.check_guard(_mut(make_artifacts(), fn))
    assert not g.allowed and code in g.reasons, g.reasons
    assert g.param_ids == () and g.val_ids == ()           # nothing is reported as usable when refused


def test_guard_val_that_cannot_define_a_domain_is_allowed_but_not_validated_domain() -> None:
    a = make_artifacts(val_over={"tier": "V3_HELDOUT_MATRIX", "may_define_validated_domain": False,
                                 "matrix_relation": "DIFFERENT"})
    g = SB.check_guard(a)
    assert g.allowed and g.may_define_validated_domain is False


def test_every_guard_reason_is_exercised_by_a_case() -> None:
    """Every fixed refusal code literal in the guard functions has a parametrised case above (or a mode test)."""
    import ast
    import inspect
    import re
    import textwrap
    codes: set[str] = set()
    for f in (SB._fit_reasons, SB._param_reasons, SB._val_reasons, SB.check_guard):
        tree = ast.parse(textwrap.dedent(inspect.getsource(f)))
        codes |= {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                  and re.fullmatch(r"(PARAM|FROZEN_FIT|STEP27|FORM|DUAL|TEST_ONLY|REAL_ARTIFACT)_[A-Z0-9_]+", n.value)}
    seen = {c[2] for c in CASES} | {"TEST_ONLY_ARTIFACT_IN_REAL_MODE", "REAL_ARTIFACT_MIXED_WITH_TEST_ONLY"}
    assert len(codes) == 29 and codes <= seen, (len(codes), sorted(codes - seen))


# ----------------------------------------------------------------------------- domain gate
@pytest.mark.parametrize("ev, it, verdict, code", [
    (event(), item(), SB.IN, None),
    (event(t=None), item(), SB.UNK, "TEMPERATURE_UNKNOWN"),
    (event(d=None), item(), SB.UNK, "DURATION_UNKNOWN"),
    (event(d=0.0), item(), SB.UNK, "DURATION_UNKNOWN"),
    (event(medium=None), item(), SB.UNK, "MEDIUM_UNKNOWN"),
    (event(medium="OVEN_AIR"), item(), SB.UNK, "MEDIUM_CONTACT_UNMAPPED"),
    (event(medium="WATER"), item(), SB.UNK, "LEACHING_UNIDENTIFIED_WATER_IMMERSION"),
    (event(t=105.0), item(), SB.OUT, "TEMPERATURE_OUTSIDE_FIT_RANGE"),
    (event(t=55.0), item(), SB.OUT, "TEMPERATURE_OUTSIDE_FIT_RANGE"),
    (event(t=(95.0, 105.0)), item(), SB.UNK, "TEMPERATURE_STRADDLES_FIT_RANGE"),
    (event(t=(70.0, 90.0)), item(), SB.IN, None),
    (event(t=100.0), item(), SB.IN, None),
    (event(t=60.0), item(), SB.IN, None),
    (event(ing=None), item(ingredient_id=None), SB.UNK, "NO_LINKED_INGREDIENT"),
    (event(ing=OTHER_ING), item(ingredient_id=OTHER_ING), SB.UNK, "MATRIX_UNLISTED"),
    (event(), item(gates=None), SB.UNK, "EVIDENCE_GATES_NOT_RUN"),
    (event(), item(gates={"presence": "PRESENT", "lot_context": "MERGED"}), SB.UNK, "MERGED_LOT_CONTEXT"),
    (event(), item(gates={"presence": "PRESENT", "lot_context": "NO_LOT"}), SB.UNK, "LOT_CONTEXT_NOT_CONFIRMED"),
    (event(), item(prior_process=["HEAT"]), SB.UNK, "PRIOR_PROCESS_CONTEXT"),
    (event(), item(gates={"presence": "UNKNOWN", "lot_context": "SINGLE_MEMBER"}), SB.UNK, "TARGET_PRESENCE_UNKNOWN"),
    (event(), item(gates={"presence": "ABSENT", "lot_context": "SINGLE_MEMBER"}), SB.OUT, "TARGET_ABSENT"),
])
def test_domain_gate_table(ev, it, verdict, code) -> None:
    g = SB.evaluate_gate(make_gate(), ev, it)
    assert g.verdict == verdict, g
    if code:
        assert code in g.reasons
    else:
        assert g.reasons == () and g.matrix_class == CLASS and g.medium_contact == SB.NO_WATER


def test_domain_gate_matrix_class_outside_the_list_is_out_not_unknown() -> None:
    gate = SB.DomainGate({ING: "VEGETABLE_TEST"}, frozenset({CLASS}), {"STEAM": SB.NO_WATER}, (60.0, 100.0), "PH_C", None, "x")
    g = SB.evaluate_gate(gate, event(), item())
    assert g.verdict == SB.OUT and "MATRIX_NOT_IN_CALIBRATION_CLASS" in g.reasons


def test_domain_gate_ph_modes() -> None:
    pha = make_gate("PH_A", (3.0, 4.2))
    assert SB.evaluate_gate(pha, event(ph_interval=(3.4, 3.9)), item()).verdict == SB.IN
    assert "PH_UNKNOWN" in SB.evaluate_gate(pha, event(), item()).reasons
    assert "PH_STRADDLES_CAL_RANGE" in SB.evaluate_gate(pha, event(ph_interval=(3.5, 4.6)), item()).reasons
    g = SB.evaluate_gate(pha, event(ph_interval=(5.5, 6.5)), item())
    assert g.verdict == SB.OUT and "PH_OUTSIDE_CAL_RANGE" in g.reasons
    pc = SB.evaluate_gate(make_gate("PH_C"), event(), item())
    assert pc.verdict == SB.IN and "PH_NOT_GATED" in pc.flags
    with pytest.raises(SB.SimulateBranchError):
        make_gate("PH_A", None)
    with pytest.raises(SB.SimulateBranchError):
        make_gate("PH_B")


def test_domain_gate_absent_registry_is_unknown() -> None:
    g = SB.evaluate_gate(None, event(), item())
    assert g.verdict == SB.UNK and g.reasons == ("DOMAIN_GATE_REGISTRY_ABSENT",)


def test_domain_gate_loader_reads_the_locks_three_files_and_returns_none_when_any_is_missing(tmp_path) -> None:
    reg = tmp_path / "registry"
    reg.mkdir()
    assert SB.DomainGate.load(tmp_path) is None
    (reg / "aa_simulate_matrix_class_list_v1.csv").write_text(f"ing_id,matrix_class\n{ING},{CLASS}\n", encoding="utf-8")
    (reg / "aa_simulate_medium_contact_map_v1.csv").write_text(
        "medium_code,medium_contact\nSTEAM,NO_WATER_CONTACT\nWATER,WATER_IMMERSION\n", encoding="utf-8")
    assert SB.DomainGate.load(tmp_path) is None                                # still one file short
    (reg / "aa_simulate_domain_gate_v1.json").write_text(
        json.dumps({"ph_mode": "PH_A", "ph_range": [3.0, 4.2], "lock_ref": "TEST_ONLY lock"}), encoding="utf-8")
    gate = SB.DomainGate.load(tmp_path)
    assert gate and gate.ph_mode == "PH_A" and gate.ph_range == (3.0, 4.2) and gate.T_range_C == (60.0, 100.0)
    assert SB.evaluate_gate(gate, event(ph_interval=(3.5, 4.0)), item()).verdict == SB.IN
    assert not any((SB.ROOT / f).exists() for f in SB.GATE_FILES)             # real files: none exist today (informational)


# ----------------------------------------------------------------------------- end to end: engine + sim_aa_1 + interval
def _closed_form(fit: dict[str, Any], t_c: float, minutes: float) -> tuple[float, float]:
    _, lo95, hi95 = FIT.predict_ln_k(fit, t_c)
    return math.exp(-math.exp(hi95) * minutes), math.exp(-math.exp(lo95) * minutes)


def test_simulate_runs_end_to_end_and_matches_the_closed_form_interval() -> None:
    br = make_branch()
    out = run(br, event(95.0, 30.0))
    assert out.simulated and out.status == "COMPLETED" and out.engine_route == "SIMULATE", out.reasons
    rec = out.record
    lo, hi = _closed_form(br.artifacts.frozen_fit["fit"], 95.0, 30.0)         # type: ignore[index]
    iv = rec["retention_interval"]                                              # type: ignore[index]
    assert math.isclose(iv["low"], lo, rel_tol=1e-6) and math.isclose(iv["high"], hi, rel_tol=1e-6)
    assert 0 < iv["low"] < iv["high"] < 1 and iv["coverage_claimed"] is False
    assert set(rec["labels"]) == {"NOT_VALIDATED", "RESEARCH_ONLY", "NON_CITABLE", "TEST_ONLY"}   # type: ignore[index]
    assert rec["analyte_basis"] == "REDUCED_L_ASCORBIC_ACID" and rec["basis_flags"] == ["BASIS_MISMATCH_TOTAL_VITC"]
    assert rec["param_ids"] == sorted(br.guard.param_ids) and rec["val_ids"] == list(br.guard.val_ids)
    assert rec["frozen_fit_sha256"] == br.artifacts.frozen_fit_sha256 and rec["form_id"] == SB.FORM_ID
    assert rec["appdec_id"].startswith("APPDEC-DRAFT-") and rec["system_id"] == "sim_aa_1" and rec["run_sha256"]
    assert all(i["layer"] == 1 for i in rec["inputs"])                         # type: ignore[index]
    d = out.as_item()
    assert d["section141_class"] == "physically_possible" and "SCENARIO" not in d["labels"]
    assert "retention" not in json.dumps({k: v for k, v in d.items() if k != "retention_interval"}).replace(
        "retention_tissue", "")  # no other number-bearing retention field


def test_simulate_is_deterministic() -> None:
    a, b = run(make_branch(), event()), run(make_branch(), event())
    assert a.record == b.record


def test_interval_is_the_outer_envelope_over_the_input_box() -> None:
    br = make_branch()
    fit = br.artifacts.frozen_fit["fit"]                                        # type: ignore[index]
    out = run(br, event(t=(70.0, 95.0), d=(10.0, 30.0)))
    iv = out.record["retention_interval"]                                       # type: ignore[index]
    corner_lo = min(_closed_form(fit, t, m)[0] for t in (70.0, 95.0) for m in (10.0, 30.0))
    corner_hi = max(_closed_form(fit, t, m)[1] for t in (70.0, 95.0) for m in (10.0, 30.0))
    assert math.isclose(iv["low"], corner_lo, rel_tol=1e-6) and math.isclose(iv["high"], corner_hi, rel_tol=1e-6)
    point = run(br, event(82.0, 20.0)).record["retention_interval"]             # type: ignore[index]
    assert iv["low"] <= point["low"] and point["high"] <= iv["high"]


def test_layer2_scenario_input_labels_the_output_scenario_and_brackets_it() -> None:
    br = make_branch()
    base = event(t=None, d=None, t_basis=None, d_basis=None)
    scen = {"scenarios": {b: {"bath_c": t, "duration_min": d, "bases": {"bath_c": "SD-001", "duration_min": "KGE-1"}}
                          for b, t, d in (("GENTLE", 75.0, 10.0), ("TYPICAL", 85.0, 20.0), ("INTENSE", 95.0, 40.0))}}
    ev = SB.AAEvent.with_scenario(base, scen)
    assert ev.temperature_C.value == (75.0, 95.0) and ev.temperature_C.layer == 2
    assert ev.duration_min.basis == "ASSUMED_DEFAULT:KGE-1"
    out = run(br, ev)
    assert out.simulated and "SCENARIO" in out.record["labels"]                 # type: ignore[index]
    assert {i["name"]: i["layer"] for i in out.record["inputs"]}["temperature"] == 2   # type: ignore[index]
    # Layer 1 values are never overridden by the scenario
    kept = SB.AAEvent.with_scenario(event(90.0, 20.0), scen)
    assert kept.temperature_C.value == 90.0 and kept.temperature_C.layer == 1
    # a scenario that merely repeats a Layer 1 value stays Layer 1
    l1 = {"scenarios": {b: {"bath_c": 90.0, "duration_min": 20.0, "bases": {"bath_c": "L1:TEXT_STATED",
                                                                            "duration_min": "L1:TEXT_STATED"}}
                        for b in ("GENTLE", "TYPICAL", "INTENSE")}}
    assert SB.AAEvent.with_scenario(base, l1).temperature_C.value is None


def test_in_calibration_domain_but_validated_domain_not_defined_routes_qualitative_not_simulate() -> None:
    """OPEN decision made visible: a VAL that cannot define a validated domain (pilot: no threshold) gives no SIMULATE."""
    a = make_artifacts(val_over={"verdict": "NOT_EVALUATED", "may_define_validated_domain": False})
    assert SB.check_guard(a).reasons == ("STEP27_NOT_EVALUATED",)
    a2 = make_artifacts(val_over={"tier": "V3_HELDOUT_MATRIX", "may_define_validated_domain": False,
                                  "matrix_relation": "DIFFERENT"})
    out = run(make_branch(arts=a2), event())
    assert not out.simulated and out.engine_route == "QUALITATIVE" and "ENGINE_ROUTE_QUALITATIVE" in out.reasons
    assert out.as_item()["section141_class"] == "unsupported" and "retention_interval" not in out.as_item()


def test_no_reviewed_mech_entry_means_no_simulate() -> None:
    out = run(make_branch(with_mech=False), event())
    assert not out.simulated and out.engine_route == "UNKNOWN" and "NO_CANDIDATE_MECHANISM" in out.reasons


def test_safety_not_declared_no_simulate() -> None:
    for s in ("UNKNOWN", "YES"):
        out = run(make_branch(config=make_config(safety=s)), event())
        assert not out.simulated and out.engine_route != "SIMULATE"


def test_measured_evidence_preempts() -> None:
    br = make_branch()
    out = run(br, event(), item(route="DIRECT"), pre="DIRECT")
    assert not out.simulated and out.status == "NOT_EVALUATED_PREEMPTED"
    assert run(br, event(), item(route="NOT_APPLICABLE")).status == "NOT_EVALUATED_PREEMPTED"
    assert run(br, event(), item(), pre="BRACKETING").status == "NOT_EVALUATED_PREEMPTED"


@pytest.mark.parametrize("ev, it, code", [
    (event(medium="WATER"), None, "LEACHING_UNIDENTIFIED_WATER_IMMERSION"),       # vegetables / juices boiled in water
    (event(t=105.0), None, "TEMPERATURE_OUTSIDE_FIT_RANGE"),
    (event(ing=OTHER_ING), item(ingredient_id=OTHER_ING), "MATRIX_UNLISTED"),     # a vegetable is not on the list
    (event(t=None), None, "TEMPERATURE_UNKNOWN"),
])
def test_out_of_domain_or_unknown_events_do_not_simulate(ev, it, code) -> None:
    out = run(make_branch(), ev, it)
    assert not out.simulated and code in out.reasons and out.engine_route != "SIMULATE"


def test_guard_refusal_blocks_a_perfect_event() -> None:
    a = _mut(make_artifacts(), _set("params.0.verification", {"status": "UNVERIFIED"}))
    out = run(make_branch(arts=a), event())
    assert not out.simulated and "PARAM_NOT_HUMAN_VERIFIED" in out.reasons
    assert out.engine_route in ("UNKNOWN", "QUALITATIVE")      # the synthetic MECH entry has one known sign (never SIMULATE)


# ----------------------------------------------------------------------------- property: UNKNOWN never routes to SIMULATE
def test_property_unknown_never_routes_to_simulate() -> None:
    """Random inputs: each of nine inputs known or UNKNOWN; SIMULATE iff every one is known and in range (oracle)."""
    rng = random.Random(20261109)
    base = make_artifacts()
    branches = {True: make_branch(arts=base),
                False: make_branch(arts=_mut(base, _set("params.0.verification", {"status": "UNVERIFIED"})))}
    sims = 0
    for n in range(400):
        known = {k: rng.random() < 0.8 for k in ("t", "d", "medium", "ing", "gates", "lot", "presence", "prior", "param")}
        br = branches[known["param"]]
        ev = event(t=95.0 if known["t"] else None, d=25.0 if known["d"] else None,
                   medium="STEAM" if known["medium"] else None, ing=ING if known["ing"] else None)
        gates = ({"presence": "PRESENT" if known["presence"] else "UNKNOWN",
                  "lot_context": "SINGLE_MEMBER" if known["lot"] else "NO_LOT"} if known["gates"] else None)
        it = item(ingredient_id=ev.ingredient_id, gates=gates, prior_process=[] if known["prior"] else ["HEAT"])
        out = run(br, ev, it)
        expect = all(known.values())
        assert out.simulated == expect, (known, out.reasons)
        if not expect:
            assert out.engine_route != "SIMULATE" and out.status == "NOT_SIMULATED"
        sims += out.simulated
    assert 0 < sims < 400


def test_property_engine_never_simulates_with_any_unknown_gate() -> None:
    """Direct engine invariant under the branch's own case gates: any non-A among G6/G7/G8 or UNKNOWN domain -> no SIMULATE."""
    br = make_branch()
    for g6 in ("APPLICABLE", "UNKNOWN", "NOT_APPLICABLE"):
        for g7 in ("APPLICABLE", "UNKNOWN"):
            for g8 in ("APPLICABLE", "UNKNOWN", "NOT_APPLICABLE"):
                for dom in AP.DOMAIN_FLAGS:
                    def cg(name, v):
                        if v == "APPLICABLE":
                            return AP.CaseGate(v, (), f"{name}-REF")
                        return AP.CaseGate(v, ({"G6": ("NO_FORM",), "G7": ("INPUT_UNOBSERVED",),
                                                "G8": ("PARAM_UNCONFIRMABLE",)}[name]), None) if v == "UNKNOWN" else \
                            AP.CaseGate(v, ({"G6": ("ASSUMPTION_VIOLATED",), "G8": ("NO_COMPATIBLE_PARAM",)}[name]), None)
                    q = AP.ApplicabilityQuery(
                        case_id="PROP", entity_version_id=ING, event_id="E1", target_svar_id=None,
                        target_state_key="synthetic_target", process_id=STEAM, matrix="synthetic class",
                        states={"synthetic_state": "SYNTH_A"}, axes=(AP.AxisValue("CV-013", "TISSUE", 5.0, "pH"),),
                        formula=cg("G6", g6), observability=cg("G7", g7), parameters=cg("G8", g8), domain_flag=dom,
                        safety_critical="NO")
                    rec = AP.evaluate(q, br.signatures, br.entries, HIER)
                    allok = (g6, g7, g8) == ("APPLICABLE",) * 3 and dom == "IN_VALIDATION_DOMAIN"
                    assert (rec["route"] == "SIMULATE") == allok, (g6, g7, g8, dom, rec["route"])


# ----------------------------------------------------------------------------- hygiene
def test_branch_has_no_ledger_write_and_no_literature_constant() -> None:
    import ast
    from pathlib import Path
    src = Path(SB.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert not ({"write_text", "write_bytes", "mkdir", "unlink"} & calls)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "open":
            assert len(n.args) < 2 and not n.keywords
    floats = sorted({n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)})
    # 0.0 start time, 1e-9 PROPOSED_PILOT tolerances, 1.0 in 1/T, 60.0 s per min (exact), 373.15 the card's 100 degC ceiling
    assert floats == [0.0, 1e-09, 1.0, 60.0, 373.15], floats
