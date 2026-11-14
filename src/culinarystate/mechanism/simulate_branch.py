"""Router SIMULATE branch for ascorbic acid (S178 aa-fit-sim, T5-C11-R4). AI_DRAFTED, PROPOSED, UNSIGNED.

One narrow path from a router item to a reduced-ascorbic-acid retention INTERVAL, with every refusal visible and every
UNKNOWN left UNKNOWN. On real data this path is UNREACHABLE today (no human-verified PARAM row, no frozen fit, no Step 27
held-out check, no reviewed MECH entry, no matrix-class list): ``SimulateBranch.from_repo()`` builds the REAL guard and
returns refusal codes. It is code-tested with SYNTHETIC fixtures that carry ``TEST_ONLY`` (see ``TestOnlyFixtures``).

Chain (each link can only refuse; nothing here upgrades a weaker route):
1. ``check_guard``: PARAM rows human-verified (Kush and Parv) and tied to the frozen fit; frozen fit exists, hash recorded
   in ``registry/compute_runs_v1.csv``, frozen before SIM-VAL; a Step 27 held-out VAL record exists, study-disjoint and
   evaluated; the FORM is reproduced and human-reviewed (G24.2). Any miss -> no SIMULATE, with a reason code.
2. ``DomainGate`` (v16 draft 286.3, amendment section 7): matrix class on the lock's list, water contact NO_WATER_CONTACT
   (WATER_IMMERSION is UNKNOWN: leaching unidentified), bath temperature inside the fitted range, pH inside the CAL
   range (pH-A) or declared not gated (pH-C), sole-member lot with no earlier heat or leach, target present. Any UNKNOWN
   input -> UNKNOWN; any input outside -> SIM_PROHIBITED.
3. The UNCHANGED Step 23a engine (``applicability.evaluate``) with the case gates G6/G7/G8 stated from 1 and 2. Only a
   schema-valid APPDEC with ``route == SIMULATE`` may run; with no reviewed MECH entry (today) the engine answers UNKNOWN.
4. ``systems.simulate("sim_aa_1", ...)`` through ``sim_core`` (which re-checks the APPDEC), once per corner of the input
   box and per 95 % prediction bound of the frozen Model A. The output is an interval [low, high] of retained reduced AA,
   never a point.

Labels on every output: NOT_VALIDATED, RESEARCH_ONLY, NON_CITABLE (+ SCENARIO when any input is Layer 2, + TEST_ONLY for
fixtures). Section 141 class ``physically_possible``; no number outside ``retention_interval``. Basis is REDUCED L-ascorbic
acid and carries BASIS_MISMATCH_TOTAL_VITC (the router target SVAR-000009 is total vitamin C).

S178 FIX-PHYS (version 0.2.0, SCI-A M7 / m5 / m6; Q2 ruling PROPOSED, flagged for Kush):
- M7 / Q2: a Layer 2 scenario default never counts as observed. G7 is UNKNOWN (``INPUT_UNOBSERVED_SCENARIO_ONLY``) whenever a model
  input (temperature, duration, medium) has a basis that is not a Layer 1 basis (ASSUMED_DEFAULT:<id> from ``with_scenario``, or any
  other scenario code), so a scenario-filled event reaches at most QUALITATIVE. "UNKNOWN never routes to SIMULATE" now holds for the
  ``with_scenario`` path too (property test in tests/unit/test_s178_fixphys_aasim.py).
- m5: the run treats the product as the bath (BATH_EQUALS_PRODUCT); a known Layer 1 piece size (a cut solid piece) needs the zone
  model, so the gate answers UNKNOWN ``SOLID_PIECE_NEEDS_ZONE_MODEL`` until ``physics_drivers.zone_mean_survival`` is wired here.
- m6: ``BranchConfig.query_overrides`` is refused in REAL mode (``SimulateBranchError`` at construction), and ``TestOnlyFixtures``
  can only be built inside a pytest process (explicit test-environment marker).

OPEN FOR HUMANS (not decided here): under the adopted route rule SIMULATE needs domain IN_VALIDATION_DOMAIN, i.e. a VAL
record with ``may_define_validated_domain`` (verdict MEETS_PREREGISTERED_CRITERIA, not tier V3). The pilot is pre-announced
RESEARCH_ONLY and descriptive (no threshold, amendment C4), so its VAL cannot define a validated domain and the engine
routes IN_CALIBRATION_ONLY events QUALITATIVE. This module does not fake the domain flag.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any

from culinarystate.mechanism import applicability as AP
from culinarystate.mechanism import form_param_val as FPV
from culinarystate.mechanism import process_signatures as PS
from culinarystate.simulation import aa_pilot_fit as FIT
from culinarystate.simulation import sim_core as SC
from culinarystate.simulation import systems as SYS
from culinarystate.simulation.kinetics import models as KM

STATUS = "AI_DRAFTED_PROPOSED_UNSIGNED"
VERSION = "simulate-branch-0.2.0-draft"
VERSION_V01 = "simulate-branch-0.1.0-draft"  # SUPERSEDED: G7 observed on scenario defaults, piece size ignored, REAL-mode overrides
ROOT = Path(__file__).resolve().parents[3]
SYSTEM_ID = "sim_aa_1"
ANALYTE_BASIS = "REDUCED_L_ASCORBIC_ACID"
BASIS_FLAG = "BASIS_MISMATCH_TOTAL_VITC"
LABELS = ("NOT_VALIDATED", "RESEARCH_ONLY", "NON_CITABLE")
SECTION141_SIMULATED = "physically_possible"
TEST_ONLY_MARK = "TEST_ONLY"
LAYER1_BASES = frozenset({"TEXT_STATED", "CARRIED_SETPOINT", "PHYSICAL_DEFINITION", "PROCESS_DEFINITION", "CUE",
                          "CUT_HISTORY", "FOOD_GROUP", "ING_LINK"})
LAYER2_BASE = "ASSUMED_DEFAULT"
UNOBSERVED_SCENARIO = "INPUT_UNOBSERVED_SCENARIO_ONLY"   # Q2: a scenario default is never an observation
SOLID_PIECE = "SOLID_PIECE_NEEDS_ZONE_MODEL"             # m5
FROZEN_FIT_CANDIDATES = ("reports/step10/aa_pilot_model_a_fit_FROZEN.json",   # written by tools/aa_pilot_fit.py
                         "reports/step10/aa_pilot_fit_frozen.json")           # name in the S178 execution board
GATE_FILES = ("registry/aa_simulate_matrix_class_list_v1.csv", "registry/aa_simulate_medium_contact_map_v1.csv",
              "registry/aa_simulate_domain_gate_v1.json")
FORM_REGISTRY = ROOT / "registry" / "form_registry_aa_v1_DRAFT.jsonl"
FORM_ID = "FORM-900004"                     # AA_FIRST_ORDER_ARRHENIUS_ONE_STEP in the draft registry
REPRODUCED_LIFECYCLES = ("REPRODUCED", "CALIBRATED", "VALIDATED_HELD_OUT", "RESEARCH_ONLY")
NO_WATER, IMMERSION = "NO_WATER_CONTACT", "WATER_IMMERSION"
IN, OUT, UNK = "IN", "OUT", "UNKNOWN"
Z95 = FIT.Z95


class SimulateBranchError(ValueError):
    """Programming / contract error (never a data verdict)."""


# ----------------------------------------------------------------------------- inputs
@dataclass(frozen=True)
class Q:
    """A numeric event input. ``value`` None = UNKNOWN; a number = point; (low, high) = bracket (Layer 2 or a range)."""

    value: float | tuple[float, float] | None
    unit: str
    basis: str | None
    ref: str = ""

    @property
    def bounds(self) -> tuple[float, float] | None:
        v = self.value
        if v is None:
            return None
        lo, hi = (v, v) if not isinstance(v, tuple) else v
        if not (math.isfinite(lo) and math.isfinite(hi)) or lo > hi:
            return None
        return float(lo), float(hi)

    @property
    def layer(self) -> int | None:
        if self.basis is None:
            return None
        return 2 if self.basis.startswith(LAYER2_BASE) else 1


@dataclass(frozen=True)
class AAEvent:
    """Resolved inputs of one router item. Anything not known stays None (never filled)."""

    event_id: str
    process_id: str | None
    ingredient_id: str | None
    temperature_C: Q
    duration_min: Q
    medium_code: str | None
    medium_basis: str | None = None
    ph_interval: tuple[float, float] | None = None
    ph_basis: str | None = None
    piece_size_class: str | None = None            # m5: a Layer 1 cut size (CUT_HISTORY) means a solid piece

    def scenario_only_inputs(self) -> tuple[str, ...]:
        """Model inputs whose basis is not a Layer 1 basis (Q2: never observed)."""
        out = []
        for name, q in (("temperature", self.temperature_C), ("duration", self.duration_min)):
            if q.value is not None and q.basis not in LAYER1_BASES:
                out.append(name)
        if self.medium_code is not None and self.medium_basis not in LAYER1_BASES:
            out.append("medium")
        return tuple(out)

    @staticmethod
    def _l1_num(x: Mapping[str, Any] | None, unit: str) -> Q:
        if not x or x.get("status", "UNKNOWN") == "UNKNOWN" or x.get("value") is None:
            return Q(None, unit, None, "")
        v = x["value"]
        val = tuple(float(a) for a in v) if isinstance(v, (tuple, list)) else float(v)
        return Q(val, unit, x.get("basis"), str(x.get("span_id") or ""))

    @classmethod
    def from_layer1(cls, event_id: str, process_id: str | None, ingredient_id: str | None,
                    inputs: Mapping[str, Any], *, ph_interval: tuple[float, float] | None = None,
                    ph_basis: str | None = None) -> "AAEvent":
        """From a ``condition_binding`` event record's ``inputs`` (Layer 1, TEXT_STATED + physical definitions)."""
        med = inputs.get("medium") or {}
        size = inputs.get("piece_size_class") or {}
        return cls(event_id, process_id, ingredient_id, cls._l1_num(inputs.get("temperature_profile"), "degC"),
                   cls._l1_num(inputs.get("duration"), "min"),
                   med.get("value") if med.get("status", "UNKNOWN") != "UNKNOWN" else None, med.get("basis"),
                   ph_interval, ph_basis, size.get("value") if size.get("status", "UNKNOWN") != "UNKNOWN" else None)

    @classmethod
    def with_scenario(cls, base: "AAEvent", scenario: Mapping[str, Any]) -> "AAEvent":
        """Fill UNKNOWN temperature / duration from a Layer 2 ``ScenarioLayer.run`` record (GENTLE..INTENSE bracket,
        basis ASSUMED_DEFAULT:<id>). Layer 1 values are kept; the scenario never overrides a stated value."""
        sc = scenario.get("scenarios") or {}

        def bracket(field_name: str, unit: str, current: Q) -> Q:
            if current.value is not None or not sc:
                return current
            vals = [sc[b][field_name] for b in ("GENTLE", "TYPICAL", "INTENSE") if b in sc]
            basis = (sc.get("TYPICAL") or next(iter(sc.values())))["bases"].get(field_name, "")
            if not vals or any(v is None for v in vals) or str(basis).startswith("L1:"):
                return current
            return Q((float(min(vals)), float(max(vals))), unit, f"{LAYER2_BASE}:{basis}", "L2:" + field_name)

        return cls(base.event_id, base.process_id, base.ingredient_id,
                   bracket("bath_c", "degC", base.temperature_C), bracket("duration_min", "min", base.duration_min),
                   base.medium_code, base.medium_basis, base.ph_interval, base.ph_basis, base.piece_size_class)


# ----------------------------------------------------------------------------- domain gate
@dataclass(frozen=True)
class DomainGate:
    """The lock's domain gate (amendment section 7). All four parts come from files committed with the lock."""

    matrix_class_by_ing: Mapping[str, str]
    allowed_matrix_classes: frozenset
    medium_contact_by_code: Mapping[str, str]
    T_range_C: tuple[float, float]
    ph_mode: str                                   # PH_A (range from the CAL papers) | PH_C (not gated)
    ph_range: tuple[float, float] | None
    lock_ref: str

    def __post_init__(self) -> None:
        if self.ph_mode not in ("PH_A", "PH_C"):
            raise SimulateBranchError("ph_mode is PH_A or PH_C (PH_B needs an opened source and is not implemented)")
        if self.ph_mode == "PH_A" and not (self.ph_range and self.ph_range[0] <= self.ph_range[1]):
            raise SimulateBranchError("PH_A needs a (low, high) pH range from the CAL papers")
        if not set(self.medium_contact_by_code.values()) <= {NO_WATER, IMMERSION}:
            raise SimulateBranchError("medium contact values are NO_WATER_CONTACT or WATER_IMMERSION")

    @classmethod
    def load(cls, root: Path = ROOT) -> "DomainGate | None":
        """The lock's three files, or None when any is absent (they do not exist today)."""
        paths = [root / f for f in GATE_FILES]
        if not all(p.exists() for p in paths):
            return None
        with paths[0].open(newline="", encoding="utf-8") as fh:
            m = {r["ing_id"]: r["matrix_class"] for r in csv.DictReader(fh)}
        with paths[1].open(newline="", encoding="utf-8") as fh:
            c = {r["medium_code"]: r["medium_contact"] for r in csv.DictReader(fh)}
        cfg = json.loads(paths[2].read_text(encoding="utf-8"))
        rng = tuple(cfg["ph_range"]) if cfg.get("ph_range") else None
        return cls(m, frozenset(m.values()), c, (FIT.T_MIN_C, FIT.T_MAX_C), cfg["ph_mode"], rng, str(cfg["lock_ref"]))


@dataclass(frozen=True)
class GateEval:
    verdict: str                                   # IN | OUT | UNKNOWN
    reasons: tuple[str, ...]
    matrix_class: str | None = None
    medium_contact: str | None = None
    flags: tuple[str, ...] = ()

    @property
    def domain_flag_base(self) -> str:
        return {IN: "IN_CALIBRATION_ONLY", OUT: "SIM_PROHIBITED", UNK: "UNKNOWN"}[self.verdict]


def _within(b: tuple[float, float], lo: float, hi: float) -> str:
    if lo <= b[0] and b[1] <= hi:
        return IN
    return OUT if (b[1] < lo or b[0] > hi) else UNK


def evaluate_gate(gate: DomainGate | None, ev: AAEvent, item: Mapping[str, Any]) -> GateEval:
    """Per-event eligibility. Any OUT beats UNKNOWN beats IN (Kleene), as in the engine."""
    if gate is None:
        return GateEval(UNK, ("DOMAIN_GATE_REGISTRY_ABSENT",))
    out: list[str] = []
    unk: list[str] = []
    flags: list[str] = []
    cls_ = contact = None
    if ev.ingredient_id is None:
        unk.append("NO_LINKED_INGREDIENT")
    elif ev.ingredient_id not in gate.matrix_class_by_ing:
        unk.append("MATRIX_UNLISTED")
    else:
        cls_ = gate.matrix_class_by_ing[ev.ingredient_id]
        if cls_ not in gate.allowed_matrix_classes:
            out.append("MATRIX_NOT_IN_CALIBRATION_CLASS")
    g = item.get("gates")
    if not isinstance(g, Mapping):
        unk.append("EVIDENCE_GATES_NOT_RUN")
    else:
        if g.get("lot_context") != "SINGLE_MEMBER":
            unk.append("MERGED_LOT_CONTEXT" if g.get("lot_context") == "MERGED" else "LOT_CONTEXT_NOT_CONFIRMED")
        if item.get("prior_process"):
            unk.append("PRIOR_PROCESS_CONTEXT")
        if g.get("presence") == "ABSENT":
            out.append("TARGET_ABSENT")
        elif g.get("presence") != "PRESENT":
            unk.append("TARGET_PRESENCE_UNKNOWN")
    if ev.medium_code is None:
        unk.append("MEDIUM_UNKNOWN")
    else:
        contact = gate.medium_contact_by_code.get(ev.medium_code)
        if contact is None:
            unk.append("MEDIUM_CONTACT_UNMAPPED")
        elif contact == IMMERSION:
            unk.append("LEACHING_UNIDENTIFIED_WATER_IMMERSION")
    tb = ev.temperature_C.bounds
    if tb is None:
        unk.append("TEMPERATURE_UNKNOWN")
    else:
        v = _within(tb, *gate.T_range_C)
        (out if v == OUT else unk if v == UNK else []).append(
            "TEMPERATURE_OUTSIDE_FIT_RANGE" if v == OUT else "TEMPERATURE_STRADDLES_FIT_RANGE")
    db = ev.duration_min.bounds
    if db is None or db[0] <= 0:
        unk.append("DURATION_UNKNOWN")
    if ev.piece_size_class:  # m5: BATH_EQUALS_PRODUCT is wrong for a cut solid piece until the zone model is wired
        unk.append(SOLID_PIECE)
    if gate.ph_mode == "PH_A":
        if ev.ph_interval is None:
            unk.append("PH_UNKNOWN")
        else:
            v = _within((float(ev.ph_interval[0]), float(ev.ph_interval[1])), *gate.ph_range)  # type: ignore[misc]
            (out if v == OUT else unk if v == UNK else []).append("PH_OUTSIDE_CAL_RANGE" if v == OUT
                                                                   else "PH_STRADDLES_CAL_RANGE")
    else:
        flags.append("PH_NOT_GATED")
    verdict = OUT if out else (UNK if unk else IN)
    return GateEval(verdict, tuple(sorted(set(out + unk))), cls_, contact, tuple(flags))


# ----------------------------------------------------------------------------- guard
@dataclass(frozen=True)
class TestOnlyFixtures:
    """Explicit marker that the artifacts below are SYNTHETIC test fixtures. Never build one outside a test."""

    __test__ = False                       # not a pytest class
    reason: str

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise SimulateBranchError("TestOnlyFixtures needs a reason")
        if "pytest" not in sys.modules:  # m6: explicit test-environment marker (production code never imports pytest)
            raise SimulateBranchError("TestOnlyFixtures can only be built inside a pytest run")


@dataclass(frozen=True)
class Artifacts:
    forms_by_id: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    form_id: str = FORM_ID
    params: tuple[Mapping[str, Any], ...] = ()
    vals: tuple[Mapping[str, Any], ...] = ()
    frozen_fit: Mapping[str, Any] | None = None
    frozen_fit_sha256: str | None = None
    recorded_fit_sha256: str | None = None          # sha256 recorded in registry/compute_runs_v1.csv
    test_only: TestOnlyFixtures | None = None


@dataclass(frozen=True)
class GuardVerdict:
    allowed: bool
    mode: str                                       # REAL | TEST_ONLY
    reasons: tuple[str, ...]
    param_ids: tuple[str, ...] = ()
    val_ids: tuple[str, ...] = ()
    fit_sha256: str | None = None
    form_id: str | None = None
    may_define_validated_domain: bool = False


def _is_test_only(rec: Mapping[str, Any]) -> bool:
    return TEST_ONLY_MARK in str(rec.get("notes") or "")


def _hex64(x: Any) -> bool:
    return isinstance(x, str) and len(x) == 64 and all(c in "0123456789abcdef" for c in x)


def _fit_reasons(fit_rec: Mapping[str, Any] | None, sha: str | None, recorded: str | None) -> list[str]:
    if fit_rec is None:
        return ["FROZEN_FIT_ABSENT"]
    out: list[str] = []
    fit = fit_rec.get("fit") or {}
    if fit_rec.get("record") != "AA_PILOT_MODEL_A_FIT" or fit.get("model") != "A_SHARED_EA_PAPER_INTERCEPTS":
        out.append("FROZEN_FIT_RECORD_INVALID")
    if fit_rec.get("status") != "FROZEN_BEFORE_SIM_VAL" or fit_rec.get("sim_val_opened") is not False:
        out.append("FROZEN_FIT_NOT_FROZEN_BEFORE_SIM_VAL")
    if recorded is None:
        out.append("FROZEN_FIT_HASH_NOT_RECORDED")
    elif recorded != sha:
        out.append("FROZEN_FIT_HASH_MISMATCH")
    ret = fit_rec.get("returned_sha256") or {}
    if not (_hex64(ret.get("Kush")) and _hex64(ret.get("Parv"))):
        out.append("DUAL_HUMAN_VERIFICATION_NOT_EVIDENCED")
    need = ("n_papers", "dof", "Ea_J_per_mol", "T_ref_K", "intercepts", "papers", "cov", "sigma_between", "residual_sd")
    if any(k not in fit for k in need) or fit.get("n_papers", 0) < 2 or fit.get("dof", 0) < 1:
        out.append("FROZEN_FIT_NEED_DATA")
    return out


def _param_reasons(params: Sequence[Mapping[str, Any]], a: Artifacts, fit_rec: Mapping[str, Any] | None,
                   sha: str | None) -> list[str]:
    if not params:
        return ["PARAM_ROWS_ABSENT"]
    out: list[str] = []
    form = a.forms_by_id.get(a.form_id)
    by = {p.get("id"): p for p in params}
    for p in params:
        issues = FPV.validate_param(p, form_id_prefix="FORM", forms_by_id=a.forms_by_id)
        out += [f"PARAM_VALIDATOR_ERROR:{i.code}" for i in issues if i.severity == "ERROR"]
        v = p.get("verification") or {}
        if p.get("status") != "ACTIVE":
            out.append("PARAM_NOT_ACTIVE")
        if not (v.get("status") == "HUMAN_VERIFIED" and v.get("verifier") in ("Kush", "Parv") and v.get("verified_at")):
            out.append("PARAM_NOT_HUMAN_VERIFIED")
        if p.get("partition") != "SIM_CALIBRATION":
            out.append("PARAM_PARTITION_NOT_SIM_CALIBRATION")
        if (p.get("value") or {}).get("status") not in ("MEASURED", "RANGE"):
            out.append("PARAM_VALUE_NOT_NUMERIC")
        if p.get("form_id") != a.form_id:
            out.append("PARAM_FORM_MISMATCH")
        if (p.get("value_si") or {}).get("status") != "CONVERTED_EXACT":
            out.append("PARAM_SI_NOT_CONVERTED_EXACT")
        prov = p.get("value_provenance") or {}
        if sha is not None and (prov.get("source_class") != "PROJECT_REFIT"
                                or prov.get("fit_run_id") != f"FITRUN-{sha[:16]}"):
            out.append("PARAM_FIT_RUN_MISMATCH")
    if form is None:
        return sorted(set(out))
    if fit_rec is not None and not out:
        fit = fit_rec["fit"]
        ea = [p["value_si"]["value"] for p in by.values() if p.get("slot_symbol") == "Ea"]
        kr = sorted(p["value_si"]["value"] for p in by.values() if p.get("slot_symbol") == "k_ref")
        want_k = sorted(math.exp(v) / 60.0 for v in fit["intercepts"].values())
        if not (len(ea) == 1 and math.isclose(ea[0], fit["Ea_J_per_mol"], rel_tol=1e-9)
                and len(kr) == len(want_k) and all(math.isclose(x, y, rel_tol=1e-9) for x, y in zip(kr, want_k))):
            out.append("PARAM_FIT_VALUE_MISMATCH")
    return sorted(set(out))


def _val_reasons(vals: Sequence[Mapping[str, Any]], a: Artifacts) -> tuple[list[str], bool]:
    if not vals:
        return ["STEP27_HELDOUT_ABSENT"], False
    out: list[str] = []
    params_by_id = {p.get("id"): p for p in a.params}
    best = False
    for v in vals:
        issues = FPV.validate_val(v, form_id_prefix="FORM", forms_by_id=a.forms_by_id, params_by_id=params_by_id)
        out += [f"STEP27_VALIDATOR_ERROR:{i.code}" for i in issues if i.severity == "ERROR"]
        if v.get("form_id") != a.form_id or not set(params_by_id) <= set(v.get("param_set_ids") or []):
            out.append("STEP27_NOT_FOR_THESE_PARAMS")
        if not v.get("eval_series_ids"):
            out.append("STEP27_NO_EVAL_SERIES")
        if (v.get("study_disjoint") or {}).get("status") != "YES":
            out.append("STEP27_NOT_STUDY_DISJOINT")
        if v.get("verdict") in ("NOT_EVALUATED", "UNKNOWN", None):
            out.append("STEP27_NOT_EVALUATED")
        if v.get("verdict") == "FAILS_PREREGISTERED_CRITERIA":
            out.append("STEP27_FAILED_PREREGISTERED_CRITERIA")
        if not _hex64(v.get("val_plan_sha256")):
            out.append("STEP27_PLAN_HASH_MISSING")
        if (v.get("verification") or {}).get("status") != "HUMAN_VERIFIED":
            out.append("STEP27_NOT_HUMAN_VERIFIED")
        best = best or v.get("may_define_validated_domain") is True
    return sorted(set(out)), best and not out


def check_guard(a: Artifacts) -> GuardVerdict:
    """May SIMULATE be offered at all? Pure; every refusal is a code. REAL mode refuses any TEST_ONLY artifact."""
    mode = "TEST_ONLY" if a.test_only is not None else "REAL"
    reasons: list[str] = []
    form = a.forms_by_id.get(a.form_id)
    everything = [*(a.params), *(a.vals), *([a.frozen_fit] if a.frozen_fit else []), *([form] if form else [])]
    marked = [_is_test_only(r) for r in everything]
    if mode == "REAL" and any(marked):
        reasons.append("TEST_ONLY_ARTIFACT_IN_REAL_MODE")
    if mode == "TEST_ONLY" and not all(marked):
        reasons.append("REAL_ARTIFACT_MIXED_WITH_TEST_ONLY")
    if form is None:
        reasons.append("FORM_ABSENT")
    else:
        reasons += [f"FORM_VALIDATOR_ERROR:{i.code}" for i in FPV.validate_form(form, form_id_prefix="FORM")
                    if i.severity == "ERROR"]
        if form.get("lifecycle_status") not in REPRODUCED_LIFECYCLES:
            reasons.append("FORM_NOT_REPRODUCED")                    # G24.2
        if (form.get("verification") or {}).get("status") != "HUMAN_VERIFIED":
            reasons.append("FORM_NOT_HUMAN_REVIEWED")
    reasons += _fit_reasons(a.frozen_fit, a.frozen_fit_sha256, a.recorded_fit_sha256)
    reasons += _param_reasons(a.params, a, a.frozen_fit, a.frozen_fit_sha256)
    vr, may = _val_reasons(a.vals, a)
    reasons += vr
    allowed = not reasons
    return GuardVerdict(allowed, mode, tuple(sorted(set(reasons))),
                        tuple(sorted(str(p.get("id")) for p in a.params)) if allowed else (),
                        tuple(sorted(str(v.get("id")) for v in a.vals)) if allowed else (), a.frozen_fit_sha256,
                        a.form_id, may)


# ----------------------------------------------------------------------------- loaders (REAL data)
def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonl(path: Path) -> tuple[dict, ...]:
    if not path.exists():
        return ()
    return tuple(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _recorded_sha(root: Path, rel: str) -> str | None:
    p = root / "registry" / "compute_runs_v1.csv"
    if not p.exists():
        return None
    with p.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("output_path", "").endswith(Path(rel).name) and r.get("status", "DONE") == "DONE":
                return r.get("output_sha256") or None
    return None


def load_artifacts(root: Path = ROOT) -> Artifacts:
    """What is on disk now: the draft FORM registry (REIMPLEMENTED, UNVERIFIED), and PARAM / VAL / frozen fit when present."""
    forms = {r["id"]: r for r in _jsonl(root / "registry" / "form_registry_aa_v1_DRAFT.jsonl")}
    fit_rec = sha = rec_sha = None
    for rel in FROZEN_FIT_CANDIDATES:
        p = root / rel
        if p.exists():
            fit_rec, sha, rec_sha = json.loads(p.read_text(encoding="utf-8")), _sha(p), _recorded_sha(root, rel)
            break
    return Artifacts(forms, FORM_ID, _jsonl(root / "ledgers" / "data" / "PARAM.jsonl"),
                     _jsonl(root / "ledgers" / "data" / "VAL.jsonl"), fit_rec, sha, rec_sha, None)


# ----------------------------------------------------------------------------- configuration
@dataclass(frozen=True)
class BranchConfig:
    """Caller settings that no document fixes yet (no default hidden in the code path)."""

    ms_limits: SC.MSLimits
    mass_balance_tol: float
    nonnegativity_tol: float
    safety_critical: str                                   # YES | NO | UNKNOWN (a human declaration)
    ph_lookup: Callable[[str | None], tuple[tuple[float, float] | None, str | None]] | None = None
    query_overrides: Callable[[AAEvent, GateEval], Mapping[str, Any]] | None = None

    @classmethod
    def pilot_draft(cls) -> "BranchConfig":
        """PROPOSED_PILOT, UNSIGNED: M&S ceiling = the card's 100 degC (373.15 K); tolerances are engineering settings;
        safety-criticality stays UNKNOWN until a human declares it (so the engine will not route SIMULATE)."""
        return cls(SC.MSLimits(373.15, "Plan v2 Step 26 card M&S ceiling 100 degC (26e model card unsigned)"),
                   1e-9, 1e-9, "UNKNOWN")


# ----------------------------------------------------------------------------- outcome
@dataclass(frozen=True)
class Outcome:
    simulated: bool
    mode: str
    status: str                                            # COMPLETED | NOT_SIMULATED | NOT_EVALUATED_PREEMPTED
    reasons: tuple[str, ...]
    engine_route: str | None = None
    gate: GateEval | None = None
    guard_reasons: tuple[str, ...] = ()
    record: Mapping[str, Any] | None = None

    def as_item(self) -> dict[str, Any]:
        d: dict[str, Any] = {"record": "AA_SIMULATE_BRANCH", "version": VERSION, "mode": self.mode,
                             "status": self.status, "simulated": self.simulated, "engine_route": self.engine_route,
                             "reasons": list(self.reasons), "guard_reasons": list(self.guard_reasons),
                             "domain_gate": None if self.gate is None else {
                                 "verdict": self.gate.verdict, "reasons": list(self.gate.reasons),
                                 "matrix_class": self.gate.matrix_class, "medium_contact": self.gate.medium_contact,
                                 "flags": list(self.gate.flags)},
                             "section141_class": SECTION141_SIMULATED if self.simulated else "unsupported",
                             "labels": list(LABELS) + ([TEST_ONLY_MARK] if self.mode == "TEST_ONLY" else [])}
        if self.record:
            d.update(self.record)
        return d


# ----------------------------------------------------------------------------- the branch
class SimulateBranch:
    def __init__(self, artifacts: Artifacts, gate: DomainGate | None, config: BranchConfig, *,
                 signatures: Sequence[PS.ProcessSignature] = (), entries: Sequence[Mapping[str, Any]] = ()) -> None:
        self.artifacts, self.gate, self.config = artifacts, gate, config
        self.signatures, self.entries = tuple(signatures), tuple(entries)
        self.guard = check_guard(artifacts)
        if config.query_overrides is not None and self.guard.mode == "REAL":  # m6: no production backdoor
            raise SimulateBranchError("query_overrides are test scaffolding and are refused in REAL mode")
        self._binder = None

    @classmethod
    def from_repo(cls, root: Path = ROOT, config: BranchConfig | None = None) -> "SimulateBranch":
        """The REAL branch: today it refuses everything (guard + gate registry + MECH entries all absent)."""
        return cls(load_artifacts(root), DomainGate.load(root), config or BranchConfig.pilot_draft())

    # -- Layer 1 inputs for the router hook (lazy: condition_binding imports router_demo)
    def layer1(self, raw: str, locale: str | None = None) -> dict[str, Mapping[str, Any]]:
        if self._binder is None:
            from culinarystate.simulation import condition_binding as CB
            self._binder = CB.Binder.load()
        return {e["event_id"]: e["inputs"] for e in self._binder.bind_text(raw, locale)["events"] if e.get("heat")}

    # -- one router item
    def evaluate_item(self, item: Mapping[str, Any], *, layer1: Mapping[str, Any] | None, precheck: str,
                      hierarchy: PS.ProcessHierarchy, target_svar: str,
                      scenario: Mapping[str, Any] | None = None) -> Outcome:
        ph, ph_basis = (None, None)
        ing = item.get("ingredient_id")
        if self.config.ph_lookup is not None:
            ph, ph_basis = self.config.ph_lookup(ing)
        if layer1 is None:
            return self.evaluate(AAEvent(item["event_id"], item.get("process_id"), ing, Q(None, "degC", None),
                                         Q(None, "min", None), None), item, precheck, hierarchy, target_svar)
        ev = AAEvent.from_layer1(item["event_id"], item.get("process_id"), ing, layer1, ph_interval=ph, ph_basis=ph_basis)
        if scenario is not None:
            ev = AAEvent.with_scenario(ev, scenario)
        return self.evaluate(ev, item, precheck, hierarchy, target_svar)

    def evaluate(self, ev: AAEvent, item: Mapping[str, Any], precheck: str, hierarchy: PS.ProcessHierarchy,
                 target_svar: str) -> Outcome:
        mode = self.guard.mode
        if item.get("route") in ("DIRECT", "INTERPOLATE", "NOT_APPLICABLE") or precheck in ("DIRECT", "BRACKETING"):
            return Outcome(False, mode, "NOT_EVALUATED_PREEMPTED", ("MEASURED_EVIDENCE_OR_GATE_PREEMPTS",),
                           item.get("route"))
        ge = evaluate_gate(self.gate, ev, item)
        flag = ge.domain_flag_base
        if flag == "IN_CALIBRATION_ONLY" and self.guard.allowed and self.guard.may_define_validated_domain:
            flag = "IN_VALIDATION_DOMAIN"
        scenario_only = ev.scenario_only_inputs()
        observed = ge.verdict != UNK and not scenario_only
        g6 = (AP.CaseGate("APPLICABLE", (), self.guard.form_id) if (self.guard.allowed and ge.verdict == IN)
              else AP.CaseGate("NOT_APPLICABLE", ("ASSUMPTION_VIOLATED",), None) if ge.verdict == OUT
              else AP.CaseGate("UNKNOWN", ("NO_FORM",), None))
        g7 = (AP.CaseGate("APPLICABLE", (), f"AAEVENT-{ev.event_id}") if observed  # the engine's G7 code; the branch says why
              else AP.CaseGate("UNKNOWN", ("INPUT_UNOBSERVED",), None))
        g8 = (AP.CaseGate("APPLICABLE", (), ",".join(self.guard.param_ids)) if self.guard.allowed
              else AP.CaseGate("NOT_APPLICABLE", ("NO_COMPATIBLE_PARAM",), None)
              if "MATRIX_NOT_IN_CALIBRATION_CLASS" in ge.reasons
              else AP.CaseGate("UNKNOWN", ("PARAM_UNCONFIRMABLE",), None))
        kw: dict[str, Any] = dict(
            case_id=f"AASIM-{ev.event_id}-{ev.ingredient_id or 'UNLINKED'}",
            entity_version_id=ev.ingredient_id or f"UNLINKED-{ev.event_id}", event_id=ev.event_id,
            target_svar_id=target_svar, target_state_key=None, process_id=ev.process_id,
            event_resolved=ev.process_id is not None, matrix=ge.matrix_class, evidence_precheck=precheck,
            formula=g6, observability=g7, parameters=g8, domain_flag=flag,
            safety_critical=self.config.safety_critical)
        if self.config.query_overrides is not None:
            kw.update(self.config.query_overrides(ev, ge))
        rec = AP.evaluate(AP.ApplicabilityQuery(**kw), self.signatures, self.entries, hierarchy)
        if rec["route"] != "SIMULATE":
            why = sorted(set(ge.reasons) | set(self.guard.reasons) | {
                r for g in rec["gates"].values() for r in g["reasons"]} | {f"ENGINE_ROUTE_{rec['route']}"} |
                ({UNOBSERVED_SCENARIO} | {f"SCENARIO_ONLY_INPUT:{n}" for n in scenario_only} if scenario_only else set()))
            return Outcome(False, mode, "NOT_SIMULATED", tuple(why), rec["route"], ge, self.guard.reasons)
        if not (self.guard.allowed and ge.verdict == IN) or scenario_only:     # defence in depth, never expected
            return Outcome(False, mode, "NOT_SIMULATED", ("GUARD_OR_GATE_DISAGREES_WITH_ENGINE",) +
                           ((UNOBSERVED_SCENARIO,) if scenario_only else ()), rec["route"], ge, self.guard.reasons)
        try:
            out = self._run(ev, ge, rec)
        except (SC.SimulationError, SimulateBranchError, KM.ModelError, ValueError) as exc:
            return Outcome(False, mode, "NOT_SIMULATED", (f"SIM_INPUT_REFUSED:{type(exc).__name__}",), rec["route"], ge,
                           self.guard.reasons)
        if isinstance(out, tuple):
            return Outcome(False, mode, "NOT_SIMULATED", out, rec["route"], ge, self.guard.reasons)
        return Outcome(True, mode, "COMPLETED", (), rec["route"], ge, self.guard.reasons, out)

    # -- interval from the frozen fit through sim_aa_1 (corners of the input box x the 95 % prediction bounds)
    def _run(self, ev: AAEvent, ge: GateEval, appdec: Mapping[str, Any]) -> dict[str, Any] | tuple[str, ...]:
        a = self.artifacts
        fit = a.frozen_fit["fit"]                                              # type: ignore[index]
        tb, db = ev.temperature_C.bounds, ev.duration_min.bounds
        assert tb is not None and db is not None
        t_corners = sorted({tb[0], tb[1]})
        d_s = sorted({float(Fraction(d).limit_denominator(10**9) * 60) for d in db})
        ph_v = self.gate.ph_range if (self.gate and self.gate.ph_mode == "PH_A") else None
        solver = SC.SolverConfig("EXPM_PIECEWISE", tuple(d_s), None, None, None, None, self.config.mass_balance_tol,
                                 self.config.nonnegativity_tol)
        lows: list[float] = []
        highs: list[float] = []
        derived: list[str] = []
        run_hashes: list[str] = []
        for tc in t_corners:
            tk = float(Fraction(tc).limit_denominator(10**9) + Fraction(27315, 100))
            mid, lo95, hi95 = FIT.predict_ln_k(fit, tc)
            for bound, target in ((lo95, highs), (hi95, lows)):
                k_s = math.exp(bound) / 60.0                                   # fit unit is 1/min
                k_ref = k_s / math.exp(-(fit["Ea_J_per_mol"] / KM.R) * (1.0 / tk - 1.0 / fit["T_ref_K"]))
                pid = lambda s, v: "DERIVED-" + SC.sha256_canonical({"fit": a.frozen_fit_sha256, "sym": s, "v": v,
                                                                      "T": tc, "b": bound})[:16]
                params = [SC.ParamValue(pid("k_ref", k_ref), "k_ref", k_ref, "1/s", ge.matrix_class or "UNKNOWN",
                                        None, ph_v, "MODEL_DERIVED"),
                          SC.ParamValue(pid("Ea", fit["Ea_J_per_mol"]), "Ea", fit["Ea_J_per_mol"], "J/mol",
                                        ge.matrix_class or "UNKNOWN", None, ph_v, "MODEL_DERIVED"),
                          SC.ParamValue(pid("T_ref", fit["T_ref_K"]), "T_ref", fit["T_ref_K"], "K",
                                        ge.matrix_class or "UNKNOWN", None, ph_v, "MODEL_DERIVED")]
                cond = SC.EventConditions(
                    event_id=ev.event_id, matrix_class=ge.matrix_class or "UNKNOWN",
                    bath_schedule=(SC.BathSegment(0.0, d_s[-1], tk),), duration_s=d_s[-1],
                    product_temperature_mode="BATH_EQUALS_PRODUCT", initial_product_temperature_K=None,
                    piece_size_class="NOT_APPLICABLE",
                    system_inputs={"medium_contact": NO_WATER, "k_dw_mode": "OFF"},
                    carried_codes={"medium": ev.medium_code or "UNKNOWN"},
                    input_refs=tuple(r for r in (f"{ev.event_id}:T:{ev.temperature_C.basis}",
                                                 f"{ev.event_id}:t:{ev.duration_min.basis}") if r))
                run = SYS.simulate(SYSTEM_ID, cond, params, appdec=appdec, solver=solver, ms_limits=self.config.ms_limits,
                                   form_id=self.guard.form_id or FORM_ID)
                if run.status != "COMPLETED":
                    return tuple(sorted({f"SIM_RUN_{run.status}", *run.reasons}))
                target.extend(float(x) for x in run.outputs["retention_tissue"])      # type: ignore[index]
                derived += [p.param_id for p in params]
                run_hashes.append(run.run_sha256)
        low, high = min(lows), max(highs)
        inputs = [self._input("temperature", ev.temperature_C), self._input("duration", ev.duration_min),
                  {"name": "medium", "value": ev.medium_code, "unit": None, "basis": ev.medium_basis,
                   "layer": 1 if ev.medium_basis in LAYER1_BASES else None, "ref": "process_medium_map"},
                  {"name": "matrix_class", "value": ge.matrix_class, "unit": None, "basis": "ING_LINK", "layer": 1,
                   "ref": "lock matrix-class list"}]
        if self.gate and self.gate.ph_mode == "PH_A":
            inputs.append({"name": "ph_interval", "value": list(ev.ph_interval or ()), "unit": "pH",
                           "basis": ev.ph_basis, "layer": 2 if (ev.ph_basis or "").startswith(LAYER2_BASE) else 1,
                           "ref": "gate only; not a model input"})
        layer2 = any(i["layer"] == 2 for i in inputs)
        flags = sorted({"T_P_BATH_EQUALS_PRODUCT_ASSUMED", "COME_UP_TIME_NOT_MODELLED", "INTERVAL_COVERAGE_NOT_CLAIMED",
                        "MODEL_DERIVED_PARAMETERS", BASIS_FLAG, *ge.flags})
        return {"route": "SIMULATE", "analyte_basis": ANALYTE_BASIS, "basis_flags": [BASIS_FLAG],
                "retention_interval": {"low": low, "high": high, "unit": "FRACTION_OF_INITIAL_REDUCED_AA",
                                       "kind": "OUTER_ENVELOPE_OF_95PCT_PREDICTION_BOUNDS_OVER_INPUT_BOX",
                                       "coverage_claimed": False},
                "labels": list(LABELS) + (["SCENARIO"] if layer2 else []) + (
                    [TEST_ONLY_MARK] if self.guard.mode == "TEST_ONLY" else []),
                "inputs": inputs, "param_ids": list(self.guard.param_ids), "derived_param_ids": sorted(set(derived)),
                "frozen_fit_sha256": a.frozen_fit_sha256, "val_ids": list(self.guard.val_ids),
                "form_id": self.guard.form_id, "system_id": SYSTEM_ID, "appdec_id": appdec["appdec_id"],
                "run_sha256": sorted(run_hashes), "flags": flags,
                "model_basis": "reduced L-ascorbic acid, k_L = 0 (NO_WATER_CONTACT), k_dw OFF; Model A unseen-matrix prediction"}

    @staticmethod
    def _input(name: str, q: Q) -> dict[str, Any]:
        v = list(q.value) if isinstance(q.value, tuple) else q.value
        return {"name": name, "value": v, "unit": q.unit, "basis": q.basis, "layer": q.layer, "ref": q.ref}


def summarize(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Counts only: simulate statuses and reason codes over router items that carry a ``simulate`` block."""
    from collections import Counter
    st, rs = Counter(), Counter()
    for it in items:
        s = it.get("simulate")
        if s:
            st[s["status"]] += 1
            rs.update(s["reasons"])
    return {"status": dict(sorted(st.items())), "reasons": dict(sorted(rs.items())), "simulate_routes": sum(
        1 for it in items if it.get("route") == "SIMULATE")}
