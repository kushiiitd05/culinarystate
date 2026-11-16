"""AA FORM rows: formula / structure only (S178 aa-fit-sim, T5-C07-R2). AI_DRAFTED, UNVERIFIED, NOT_MINTED.

Builds the draft FORM records for ascorbic-acid (AA) degradation kinetics and writes three draft files under
``registry/``: ``form_registry_aa_v1_DRAFT.jsonl`` (FORM v1 records), ``..._index.csv`` (flat view) and
``..._model_cards.md`` (one short card per FORM). Nothing here reads or writes a ledger.

What a row holds: equation (LaTeX plus a small evaluable AST), state variables, inputs, parameter SLOTS with
dimension, order and positivity, assumptions as constraints, validity-domain fields (``ms_limits``) and the
implementation pointer with a code hash. What it never holds: a parameter value, a default, a prior or a literature
number (D-076: PARAM rows come only from rows both humans verified). Every row is lifecycle ``REIMPLEMENTED`` at best
(code exists and agrees with its own equation on synthetic inputs); ``REPRODUCED`` needs a source figure or table
reproduced within tolerance (G24.2) and is NOT claimed. ``verification.status`` is ``UNVERIFIED``: an AI draft is not
a human signature (D-071).

ids: ``FORM-9xxxxx`` is a DRAFT id block, not minted (``ledgers/data/_ids.jsonl`` has no FORM prefix). The 24f
FORM- versus MODEL- prefix decision is OPEN; the validator is called with ``form_id_prefix="FORM"`` as a working choice
and the rows are re-keyed by the orchestrator when the ledger id is minted.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from culinarystate.mechanism import form_param_val as FPV
from culinarystate.simulation import sim_aa_1
from culinarystate.simulation.kinetics import models as M
from culinarystate.simulation.kinetics import units as U

STATUS = "AI_DRAFTED_UNVERIFIED_NOT_MINTED"
VERSION = "aa-form-registry-0.1.0-draft"
ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "registry"
JSONL_PATH = REGISTRY / "form_registry_aa_v1_DRAFT.jsonl"
INDEX_PATH = REGISTRY / "form_registry_aa_v1_DRAFT_index.csv"
CARDS_PATH = REGISTRY / "form_registry_aa_v1_DRAFT_model_cards.md"
FORM_ID_PREFIX = "FORM"                      # working choice; 24f is OPEN
NOW = "2026-11-09T00:00:00+00:00"
SCHEMA_VERSION = "1.0.0-draft"
MODELS_PY = Path(M.__file__)
SIM_AA_PY = Path(sim_aa_1.__file__)
# Validity domain of the AA pilot as written in the pre-registration (reports/step10/aa_pilot_preregistration_DRAFT.md
# section 6: 60-100 degC cooking range) and the Step 26 card M&S ceiling (T <= 100 degC, ambient pressure, water/steam).
# Kelvin by the exact 273.15 offset. These are design limits of the pilot, not fitted numbers.
T_RANGE_K = (333.15, 373.15)
ENERGY_PER_AMOUNT = "ENERGY*AMOUNT^-1"

# ----------------------------------------------------------------------------- a tiny evaluable AST
def sym(name: str) -> dict:
    return {"op": "sym", "name": name}


def num(value: int) -> dict:
    return {"op": "num", "value": value}


def node(op: str, *args: dict) -> dict:
    return {"op": op, "args": list(args)}


def eval_ast(n: Mapping[str, Any], env: Mapping[str, float]) -> float:
    """Evaluate an AST node: ops sym, num, neg, add, sub, mul, div, pow, exp, ln."""
    op = n["op"]
    if op == "sym":
        return float(env[n["name"]])
    if op == "num":
        return float(n["value"])
    a = [eval_ast(x, env) for x in n["args"]]
    if op == "neg":
        return -a[0]
    if op == "add":
        return a[0] + a[1]
    if op == "sub":
        return a[0] - a[1]
    if op == "mul":
        return math.prod(a)
    if op == "div":
        return a[0] / a[1]
    if op == "pow":
        return a[0] ** a[1]
    if op == "exp":
        return math.exp(a[0])
    if op == "ln":
        return math.log(a[0])
    raise ValueError(f"unknown AST op {op!r}")


def _arrh_exponent() -> dict:
    """-(Ea/R) * (1/T - 1/T_ref)"""
    return node("neg", node("mul", node("div", sym("Ea"), sym("R")),
                            node("sub", node("div", num(1), sym("T")), node("div", num(1), sym("T_ref")))))


AST: Mapping[str, dict] = {
    "ZERO_ORDER": {"op": "eq", "lhs": sym("C"), "rhs": node("sub", sym("C0"), node("mul", sym("k0"), sym("tau")))},
    "FIRST_ORDER": {"op": "eq", "lhs": node("ln", node("div", sym("C"), sym("C0"))),
                    "rhs": node("neg", node("mul", sym("k"), sym("tau")))},
    "WEIBULL": {"op": "eq", "lhs": node("ln", node("div", sym("C"), sym("C0"))),
                "rhs": node("neg", node("pow", node("div", sym("tau"), sym("alpha")), sym("beta")))},
    "ARRHENIUS_REF_T": {"op": "eq", "lhs": node("ln", sym("k")),
                        "rhs": node("add", node("ln", sym("k_ref")), _arrh_exponent())},
    "FIRST_ORDER_ARRHENIUS": {"op": "eq", "lhs": node("ln", node("div", sym("C"), sym("C0"))),
                              "rhs": node("neg", node("mul", sym("k_ref"), node("exp", _arrh_exponent()),
                                                      sym("tau")))},
}


# ----------------------------------------------------------------------------- building blocks
def _slot(symbol: str, role: str, dimension: str, order: float | None, *, positive: bool = True,
          needs_t_ref: bool = False, description: str) -> dict[str, Any]:
    ro = ({"status": "STATED", "value": order} if order is not None else {"status": "NOT_APPLICABLE", "value": None})
    return {"symbol": symbol, "role": role, "dimension": dimension, "reaction_order": ro, "positive": positive,
            "needs_T_ref": needs_t_ref, "description": description}


def _assume(expr: str, note: str) -> dict[str, str]:
    return {"constraint_expr": expr, "kind": "CONSTRAINT", "consequence": "INVALIDATES_FROM_VIOLATION",
            "source_note": note}


_REF = "reports/step10/aa_pilot_preregistration_DRAFT.md; reports/step10/aa_pilot_preregistration_AMENDMENT_S178_DRAFT.md"
_BASIS = _assume("analyte_basis == REDUCED_L_ASCORBIC_ACID (no DHA compartment); every output carries "
                 "BASIS_MISMATCH_TOTAL_VITC beside a total-vitamin-C value (SVAR-000009)",
                 "sim_aa_1 docstring; REV-A V7; amendment section 7 (analyte basis)")
_KELVIN = _assume("T and T_ref are absolute temperatures in K (> 0); the model uses 1/T - 1/T_ref",
                  "G24.3 Kelvin in Arrhenius; models.arrhenius_rate")
_ISO = _assume("bath temperature is piecewise constant and product temperature equals bath temperature "
               "(BATH_EQUALS_PRODUCT); no come-up or cool-down is modelled; LUMPED_LAG only for Bi <~ 0.1 and only "
               "with a tau_h PARAM for the size class",
               "sim_core TP_MODES; REV-A V7 (two inconsistent thermal models)")
_LUMP = _assume("one apparent first-order step: aerobic and anaerobic pathways are lumped "
                "(ASCORBIC_ACID_APPARENT_LOSS_LUMPED); the oxygen regime of the calibration is not modelled",
                "registry/mechanism_seed_roster_draft_v1.csv; plan Step 26 architecture")
_DOMAIN = _assume("k_ref and Ea hold only inside the calibration matrix class and the stated pH range (pH-A) or with "
                  "'pH not gated' (pH-C), and inside the fitted temperature range; no pH, a_w or concentration "
                  "dependence of k is modelled",
                  "REV-A V7 / Q16; amendment section 7 (domain gate); v16 draft 286.3")
_NOLEACH = _assume("NO_WATER_CONTACT: k_L = 0, no cooking-water compartment; WATER_IMMERSION events are UNKNOWN "
                   "because leaching (k_L, K_p) is not identified by any calibration paper",
                   "pre-registration section 6; amendment section 7; sim_aa_1 docstring")
_NOENZ = _assume("no ascorbate-oxidase activity: the raw cut-tissue come-up window before enzyme inactivation is "
                 "outside the model", "plan Step 26 architecture (prohibitions); mechanism roster ENZYME_THERMAL_INACTIVATION")
_CTX = ("RESEARCH_ONLY. Reduced-ascorbic-acid retention interval under NO_WATER_CONTACT, from human-verified PARAM rows "
        "only; no number exists until M3 (D-076) and Step 27; never evidence, never citable.")


def _inputs(*names: str) -> list[dict[str, Any]]:
    table = {
        "tau": {"name": "tau", "cv_id": "CV-001", "required_location": "NOT_APPLICABLE", "dimension": "TIME",
                "clock": "PROCESS_TAU", "observability_required": True},
        "T": {"name": "T", "cv_id": "CV-006", "required_location": "MEDIUM", "dimension": "TEMPERATURE",
              "clock": "PROCESS_TAU", "observability_required": True},
        "r": {"name": "r", "cv_id": None, "required_location": "NOT_APPLICABLE", "dimension": "LENGTH^3*MASS^-1",
              "clock": "NOT_APPLICABLE", "observability_required": True},
    }
    return [dict(table[n]) for n in names]


def _ms(status: str, **kw: Any) -> dict[str, Any]:
    if status == "NOT_YET_STATED":
        return {"status": status, "medium": [], "temperature_range": None, "pressure_note": None,
                "phase_note": None, "geometry_class_note": None}
    return {"status": status, "medium": kw["medium"],
            "temperature_range": {"status": "RANGE", "low": T_RANGE_K[0], "high": T_RANGE_K[1], "unit": "K",
                                  "raw": "60-100 degC, pre-registration section 6; card M&S ceiling 100 degC"},
            "pressure_note": "ambient pressure (1 atm); water or steam medium only (plan Step 26 card M&S)",
            "phase_note": kw["phase"], "geometry_class_note": kw["geometry"]}


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _impl(path: Path) -> dict[str, str]:
    return {"path": str(path.relative_to(ROOT)), "code_sha256": _hash(path), "library_version": M.LIBRARY_VERSION}


def _record(n: int, key: str, *, tier: str, family: str, kind: str, latex: str, text: str, ast: dict | None,
            states: list[dict], inputs: list[dict], slots: list[dict], assumptions: list[dict], ms: dict,
            impl: dict, notes: str, initial: list[str], context: str = _CTX) -> dict[str, Any]:
    return {
        "id": f"FORM-{900000 + n:06d}", "record_type": "FORM", "schema_version": SCHEMA_VERSION, "version": 1,
        "status": "ACTIVE", "superseded_by": None, "created_at": NOW,
        "created_by": "AI_AGENT:aa-fit-sim:S178 (AI draft, not a human signature)",
        "provenance": {"method": "DERIVED", "source_ids": [], "agent": "aa-fit-sim lane S178 (AI agent)",
                       "locator": f"{M.LIBRARY_VERSION} FORMS / sim_aa_1.SPEC; Plan v2 Step 24 card 24b",
                       "notes": "built by culinarystate.mechanism.aa_form_registry; ledger id NOT minted"},
        "verification": {"status": "UNVERIFIED", "verifier": None, "verified_at": None, "ai_reviewer": None,
                         "notes": "AI_DRAFTED; Kush and Parv model-card review pending (Step 24 human gate)"},
        "external_refs": [f"NAME:{key}", "SYSTEM:sim_aa_1", "MECHKEY:ASCORBIC_ACID_APPARENT_LOSS_LUMPED"],
        "notes": notes, "model_discriminator": None, "mechanism_ids": [],
        "model_tier": tier, "model_family": family, "model_kind": kind,
        "equation": {"latex": latex, "ast": ast, "ast_status": "PRESENT" if ast else "NOT_YET_WRITTEN",
                     "text_raw": text},
        "state_variables": states, "inputs": inputs, "parameter_slots": slots, "assumptions": assumptions,
        "initial_conditions_required": initial,
        "boundary_conditions": {"description": "none: a lumped, well-mixed, spatially uniform matrix"},
        "effective_or_mechanistic": "EFFECTIVE", "ms_limits": ms, "calibration_domain_ref": None,
        "validated_domain_refs": [], "identifiability_status": "NOT_ASSESSED", "implementation": impl,
        "solver": {"kind": "ANALYTIC", "curie": None}, "uncertainty_representation": "NONE_YET",
        "context_of_use": context, "model_risk_grade": "NOT_ASSESSED",
        "domain_of_verification": "synthetic inputs only: analytic vs numeric, tests/unit/test_s178_aasim_forms.py",
        "credibility_levels": ["VERIFICATION_SYNTHETIC_ONLY"], "lifecycle_status": "REIMPLEMENTED",
        "reproduction_refs": [], "source_refs": [], "licence_status": "ASSUMED"}


def _conc_state() -> list[dict]:
    return [{"symbol": "C", "svar_id": None, "dimension": "CONCENTRATION",
             "description": "reduced L-ascorbic acid in the matrix; SVAR-000009 is TOTAL vitamin C, so no svar_id "
                            "is claimed (basis mismatch is explicit)"}]


def build_forms() -> list[dict[str, Any]]:
    """The six draft FORM records, deterministic. No parameter value anywhere."""
    m_impl, a_impl = _impl(MODELS_PY), _impl(SIM_AA_PY)
    k1 = _slot("k_ref", "RATE_CONSTANT", "TIME^-1", 1, needs_t_ref=True,
               description="first-order rate constant at T_ref; SI 1/s, reported as 1/min or 1/h, exact conversion "
                           "in registry/kinetic_units_v1_DRAFT.csv; no value held here")
    ea = _slot("Ea", "ACTIVATION_ENERGY", ENERGY_PER_AMOUNT, None, positive=False,
               description="activation energy; SI J/mol, reported as kJ/mol or kcal/mol (calorie convention must be "
                           "declared); sign not constrained by the library; no value held here")
    rows = [
        _record(1, "AA_ZERO_ORDER_STUB", tier="PRIMARY", family="ZERO_ORDER", kind="KINETIC",
                latex=r"C(\tau) = C_0 - k_0\,\tau", text="C = C0 - k0*tau", ast=AST["ZERO_ORDER"],
                states=_conc_state(), inputs=_inputs("tau"),
                slots=[_slot("C0", "INITIAL_VALUE", "CONCENTRATION", None, description="initial concentration"),
                       _slot("k0", "RATE_CONSTANT", "CONCENTRATION*TIME^-1", 0,
                             description="zero-order rate constant (order 0); concentration unit declared by the "
                                         "series, never reduced")],
                assumptions=[_BASIS, _assume("C0 - k0*tau >= 0 (valid while C >= 0)", "models._zero; SSOT 210.3")],
                ms=_ms("NOT_YET_STATED"), impl=m_impl, initial=["C0"],
                notes="STUB. Alternative form for series that are linear in time; not used by sim_aa_1."),
        _record(2, "AA_FIRST_ORDER_FIXED_T", tier="PRIMARY", family="FIRST_ORDER", kind="KINETIC",
                latex=r"\ln\!\left(C/C_0\right) = -k\,\tau", text="ln(C/C0) = -k*tau", ast=AST["FIRST_ORDER"],
                states=_conc_state(), inputs=_inputs("tau"),
                slots=[_slot("k", "RATE_CONSTANT", "TIME^-1", 1,
                             description="first-order rate constant at one fixed temperature and matrix")],
                assumptions=[_BASIS, _LUMP, _assume("temperature is constant over tau", "SSOT 210.4")],
                ms=_ms("NOT_YET_STATED"), impl=m_impl, initial=["C0"],
                notes="Primary rate form at fixed T; one k per (matrix, T)."),
        _record(3, "AA_ARRHENIUS_REFERENCE_T", tier="SECONDARY", family="ARRHENIUS_SECONDARY", kind="KINETIC",
                latex=r"\ln k(T) = \ln k_{ref} - \frac{E_a}{R}\left(\frac{1}{T}-\frac{1}{T_{ref}}\right)",
                text="ln k(T) = ln k_ref - (Ea/R)*(1/T - 1/T_ref)", ast=AST["ARRHENIUS_REF_T"],
                states=[], inputs=_inputs("T"), slots=[k1, ea], assumptions=[_KELVIN, _DOMAIN],
                ms=_ms("STATED", medium=["WATER", "STEAM"],
                       phase="aqueous liquid or pulp; calibration matrix class and pH decided at the pre-registration lock",
                       geometry="temperature of the medium; no product-temperature lag"),
                impl=m_impl, initial=[],
                notes="Secondary (temperature) model with the declared reference temperature T_ref (Kelvin, a fixed "
                      "input of the fit, not a slot). R is the exact SI product N_A*k_B."),
        _record(4, "AA_FIRST_ORDER_ARRHENIUS_ONE_STEP", tier="TERTIARY", family="FIRST_ORDER", kind="KINETIC",
                latex=r"\ln\!\left(C/C_0\right) = -k_{ref}\exp\!\left[-\frac{E_a}{R}\left(\frac{1}{T}-"
                      r"\frac{1}{T_{ref}}\right)\right]\tau",
                text="ln(C/C0) = -k_ref*exp(-(Ea/R)*(1/T - 1/T_ref))*tau", ast=AST["FIRST_ORDER_ARRHENIUS"],
                states=_conc_state(), inputs=_inputs("tau", "T"), slots=[k1, ea],
                assumptions=[_BASIS, _KELVIN, _ISO, _LUMP, _DOMAIN, _NOLEACH, _NOENZ],
                ms=_ms("STATED", medium=["WATER", "STEAM"],
                       phase="aqueous liquid or pulp (matrix-class list decided at the lock); NO_WATER_CONTACT only",
                       geometry="BATH_EQUALS_PRODUCT; piecewise-constant bath temperature"),
                impl=m_impl, initial=["C0"],
                notes="The form the SIMULATE branch evaluates when k_L = 0 (NO_WATER_CONTACT, k_dw OFF): "
                      "A_t of sim_aa_1 reduces exactly to this solution (tested)."),
        _record(5, "AA_WEIBULL_STUB", tier="PRIMARY", family="WEIBULL", kind="KINETIC",
                latex=r"\ln\!\left(C/C_0\right) = -\left(\tau/\alpha\right)^{\beta}",
                text="ln(C/C0) = -(tau/alpha)^beta", ast=AST["WEIBULL"], states=_conc_state(),
                inputs=_inputs("tau"),
                slots=[_slot("alpha", "SCALE_TIME", "TIME", None, description="Weibull scale (time)"),
                       _slot("beta", "SHAPE", "1", None, description="Weibull shape (dimensionless)")],
                assumptions=[_BASIS, _assume("tau >= 0; ln(C/C0) = 0 at tau = 0", "models._weibull")],
                ms=_ms("NOT_YET_STATED"), impl=m_impl, initial=["C0"],
                notes="STUB (reference-only alternative; Weibull parameterisation alpha scale, beta shape accepted "
                      "as drafted in D-052). Not used by sim_aa_1."),
        _record(6, "AA_COMPARTMENT_SIM_AA_1", tier="TERTIARY", family="FIRST_ORDER", kind="COMPOSITE",
                latex=r"\dot A_t = -k_d(T_p)A_t - k_L\left(A_t - \tfrac{K_p}{r}A_w\right),\quad "
                      r"\dot A_w = k_L\left(A_t-\tfrac{K_p}{r}A_w\right)-k_{dw}A_w,\quad "
                      r"\dot D = k_d(T_p)A_t + k_{dw}A_w",
                text="dA_t/dt = -k_d(T_p)*A_t - k_L*(A_t - (K_p/r)*A_w); dA_w/dt = k_L*(A_t - (K_p/r)*A_w) - k_dw*A_w; "
                     "dD/dt = k_d(T_p)*A_t + k_dw*A_w; k_d(T) Arrhenius reference-T",
                ast=None,
                states=[{"symbol": "A_t", "svar_id": None, "dimension": "1", "description": "tissue fraction of initial"},
                        {"symbol": "A_w", "svar_id": None, "dimension": "1", "description": "cooking-water fraction"},
                        {"symbol": "D", "svar_id": None, "dimension": "1", "description": "degraded fraction"}],
                inputs=_inputs("tau", "T", "r"),
                slots=[k1, ea,
                       _slot("T_ref", "REFERENCE_TEMPERATURE", "TEMPERATURE", None,
                             description="pre-declared reference temperature in K (a slot in sim_aa_1, a fixed input of "
                                         "the fit in the two-step forms); no value held here"),
                       _slot("k_L", "TRANSFER_COEFFICIENT", "TIME^-1", None,
                             description="lumped leaching rate constant; UNIDENTIFIED by the pilot, so water-immersion "
                                         "events stay UNKNOWN; 0 under NO_WATER_CONTACT"),
                       _slot("K_p", "PARTITION_COEFFICIENT", "LENGTH^3*MASS^-1", None,
                             description="partition coefficient in the r = V_w/m_t dimension (card default 1 not used)"),
                       _slot("k_dw", "RATE_CONSTANT", "TIME^-1", 1,
                             description="first-order degradation in the water; explicit ON/OFF switch, no default"),
                       _slot("tau_h", "SCALE_TIME", "TIME", None,
                             description="lumped product-temperature time constant per piece-size class "
                                         "(LUMPED_LAG only; none exists)")],
                assumptions=[_BASIS, _KELVIN, _ISO, _LUMP, _DOMAIN, _NOENZ,
                             _assume("k_L is independent of temperature; k_dw first order; leaching terms are identified "
                                     "only by studies that assay the cooking water", "D-052 H3; sim_aa_1 docstring")],
                ms=_ms("STATED", medium=["WATER", "STEAM"],
                       phase="three compartments: tissue, cooking water, degraded; leaching branch not identified",
                       geometry="BATH_EQUALS_PRODUCT, or LUMPED_LAG flagged T_P_LAG_EXTRAPOLATED"),
                impl=a_impl, initial=["A_t(0)=1", "A_w(0)=0", "D(0)=0"],
                notes="SIM-AA-1 structure from the Step 26 card (D-052 selected sim_aa_1). The leaching branch has no "
                      "identifying data; only the k_L = 0 case is reachable by the SIMULATE branch."),
    ]
    return rows


# ----------------------------------------------------------------------------- checks
def validate(rows: list[dict[str, Any]] | None = None) -> list[str]:
    """Problems of the registry rows: schema and validator errors, parameter-value leakage, code-hash drift, AST vs code."""
    rows = rows if rows is not None else build_forms()
    out: list[str] = []
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        out.append("DUPLICATE_ID")
    for r in rows:
        out += [f"{r['id']}:{i.code}:{i.detail}" for i in FPV.validate_form(r, form_id_prefix=FORM_ID_PREFIX)
                if i.severity == "ERROR"]
        if r["lifecycle_status"] in ("REPRODUCED", "CALIBRATED", "VALIDATED_HELD_OUT") or r["reproduction_refs"]:
            out.append(f"{r['id']}:LIFECYCLE_OVERCLAIM")
        if r["verification"]["status"] != "UNVERIFIED":
            out.append(f"{r['id']}:VERIFICATION_OVERCLAIM")
        if any(s.get("value") is not None for s in r["parameter_slots"]):
            out.append(f"{r['id']}:SLOT_HOLDS_VALUE")
        impl = r["implementation"]
        if impl and _hash(ROOT / impl["path"]) != impl["code_sha256"]:
            out.append(f"{r['id']}:CODE_HASH_DRIFT")
    return out


def check_ast_against_models(rows: list[dict[str, Any]] | None = None, *, rel_tol: float = 1e-9) -> dict[str, float]:
    """Evaluate each AST rhs on synthetic inputs and compare with models.FORMS: max relative error per form."""
    rows = rows if rows is not None else build_forms()
    # synthetic inputs chosen here for verification only: not a rate constant, an Ea or a literature value
    env = {"C0": 1.0, "k0": 0.01, "k": 0.002, "k_ref": 0.003, "Ea": 5.0e4, "alpha": 400.0, "beta": 1.3,
           "T": 350.0, "T_ref": 340.0, "tau": 900.0, "R": U.GAS_CONSTANT_J_PER_MOL_K}
    covs = {"tau_s": [env["tau"]], "T_K": [env["T"]]}
    out: dict[str, float] = {}
    for r in rows:
        key = next((e[5:] for e in r["external_refs"] if e.startswith("NAME:")), "")
        form = {"AA_ZERO_ORDER_STUB": "ZERO_ORDER", "AA_FIRST_ORDER_FIXED_T": "FIRST_ORDER",
                "AA_ARRHENIUS_REFERENCE_T": "ARRHENIUS_REF_T", "AA_FIRST_ORDER_ARRHENIUS_ONE_STEP": "FIRST_ORDER_ARRHENIUS",
                "AA_WEIBULL_STUB": "WEIBULL"}.get(key)
        if form is None or r["equation"]["ast"] is None:
            continue
        theta = {s: env[s] for s in M.FORMS[form].symbols}
        want = float(M.FORMS[form].predict(theta, covs, {"T_ref_K": env["T_ref"]})[0])
        got = eval_ast(r["equation"]["ast"]["rhs"], env)
        out[form] = abs(got - want) / max(abs(want), 1e-300)
    return out


# ----------------------------------------------------------------------------- files
def jsonl_text(rows: list[dict[str, Any]] | None = None) -> str:
    rows = rows if rows is not None else build_forms()
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows)


INDEX_COLUMNS = ("form_id", "name", "model_tier", "model_family", "model_kind", "lifecycle_status",
                 "verification_status", "slots", "ms_limits_status", "temperature_range_K", "medium",
                 "assumptions", "implementation_path", "code_sha256", "equation_text")


def index_rows(rows: list[dict[str, Any]] | None = None) -> list[dict[str, str]]:
    rows = rows if rows is not None else build_forms()
    out = []
    for r in rows:
        tr = r["ms_limits"]["temperature_range"]
        out.append({
            "form_id": r["id"], "name": next(e[5:] for e in r["external_refs"] if e.startswith("NAME:")),
            "model_tier": r["model_tier"], "model_family": r["model_family"], "model_kind": r["model_kind"],
            "lifecycle_status": r["lifecycle_status"], "verification_status": r["verification"]["status"],
            "slots": "; ".join(f"{s['symbol']}[{s['dimension']}]" for s in r["parameter_slots"]),
            "ms_limits_status": r["ms_limits"]["status"],
            "temperature_range_K": "" if tr is None else f"{tr['low']}-{tr['high']}",
            "medium": "|".join(r["ms_limits"]["medium"]), "assumptions": str(len(r["assumptions"])),
            "implementation_path": r["implementation"]["path"], "code_sha256": r["implementation"]["code_sha256"],
            "equation_text": r["equation"]["text_raw"]})
    return out


def index_text(rows: list[dict[str, Any]] | None = None) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=INDEX_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(index_rows(rows))
    return buf.getvalue()


def cards_text(rows: list[dict[str, Any]] | None = None) -> str:
    rows = rows if rows is not None else build_forms()
    out = ["# AA FORM draft model cards (S178 aa-fit-sim)", "",
           "Status: **AI_DRAFTED / UNVERIFIED / NOT_MINTED**. An AI draft is not a human review, signature or approval "
           "(D-071). Generated by `culinarystate.mechanism.aa_form_registry`; do not edit by hand. Every row holds "
           "formula, slots, assumptions, validity-domain fields and units, and **no parameter value** (D-076). "
           "Lifecycle is at most REIMPLEMENTED: no source figure or table has been reproduced, so nothing here is "
           "REPRODUCED (G24.2), CALIBRATED or VALIDATED.", ""]
    for r in rows:
        name = next(e[5:] for e in r["external_refs"] if e.startswith("NAME:"))
        ms = r["ms_limits"]
        tr = ms["temperature_range"]
        out += [f"## {r['id']} {name}", "",
                f"- Tier / family / kind: {r['model_tier']} / {r['model_family']} / {r['model_kind']}; lifecycle "
                f"{r['lifecycle_status']}; verification {r['verification']['status']}.",
                f"- Equation: `{r['equation']['text_raw']}`",
                "- Slots: " + "; ".join(f"`{s['symbol']}` {s['role']} [{s['dimension']}]" for s in r["parameter_slots"]),
                "- Validity domain (ms_limits " + ms["status"] + "): " + (
                    "not stated (stub)" if tr is None else
                    f"T {tr['low']}-{tr['high']} K (60-100 degC, pre-registration section 6); medium "
                    f"{', '.join(ms['medium'])}; {ms['phase_note']}; {ms['geometry_class_note']}"),
                "- Assumptions (a violation invalidates the result from that point):"]
        out += [f"  - {a['constraint_expr']}" for a in r["assumptions"]]
        out += [f"- Implementation: `{r['implementation']['path']}` sha256 `{r['implementation']['code_sha256'][:16]}...`",
                f"- Context of use: {r['context_of_use']}", f"- Note: {r['notes']}", ""]
    return "\n".join(out)


def write_files(root: Path = ROOT) -> dict[str, str]:
    """Write the three draft files; returns sha256 per file. Refuses nothing else: these paths are this lane's."""
    reg = root / "registry"
    rows = build_forms()
    problems = validate(rows)
    if problems:
        raise ValueError(f"refusing to write an invalid registry: {problems[:3]}")
    files = {"form_registry_aa_v1_DRAFT.jsonl": jsonl_text(rows), "form_registry_aa_v1_DRAFT_index.csv": index_text(rows),
             "form_registry_aa_v1_DRAFT_model_cards.md": cards_text(rows)}
    sha = {}
    for name, text in files.items():
        (reg / name).write_text(text, encoding="utf-8")
        sha[name] = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return sha


if __name__ == "__main__":
    print(json.dumps(write_files(), indent=1, sort_keys=True))
