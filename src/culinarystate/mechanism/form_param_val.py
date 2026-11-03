"""Step 24a FORM / PARAM / VAL v1 DRAFT validator (S159, DRAFT_PENDING_H4).

Pure: reads records shaped like registry/schemas/{FORM,PARAM,VAL}.draft_v1.schema.json (and KIN v1.1 records
for cross-checks) and returns issues and verdicts. It writes nothing, mints nothing and reads no ledger.
Everything it returns is an AI-side engineering check (D-045), not human verification.

Shared with KIN v1.1 (``culinarystate.lineage.kinetic_contract``): envelope fields, ``value_obj``,
``dispersion``, ``locator``, ``time_conversion``, the lineage key names and patterns, the K-level, fit-method
and model-family vocabularies, clock PROCESS_TAU, raw values kept with SI / seconds in separate fields, the
``Issue`` and ``Eligibility`` records and the verdict tokens (ELIGIBLE_UNDER_DRAFT_RULES / NOT_ELIGIBLE /
UNKNOWN; NOT_ELIGIBLE wins over UNKNOWN; UNKNOWN never becomes eligible).

FORM- versus MODEL- prefix (Step 24f, H4) is **not decided**: the schemas accept both and every function takes
a required ``form_id_prefix`` keyword (no default). Under MODEL- a FORM carries
``model_discriminator = FORMULA_MODEL`` (kept apart from the ML model card ``ledgers/schemas/MODEL``).

Rules checked here (beyond the schemas): slot dimension by role and reaction order (SSOT 210.30), PARAM unit
dimension against its slot (no cross-order harmonisation), positivity, T_ref in Kelvin (G24.3), exact SI
conversion, author-fit and KIN references, no PARAM from K0 series (SSOT 211.48), fitted_on lineage equals the
KIN lineage, no non-hierarchical pooling (SSOT 211.38), VAL study disjointness and eval series not used in the
fit, validated domain only from defining VAL records, and the draft calibration-use eligibility (G24.4).
Synthetic tests: tests/unit/test_step24a_form_param_val_{schema,contract}.py.
"""
from __future__ import annotations

import functools
import json
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from culinarystate.lineage.kinetic_contract import ELIGIBLE, ERROR, NOT_ELIGIBLE, UNKNOWN, WARN, Eligibility, Issue
from culinarystate.simulation.kinetics import units as U

STATUS = "DRAFT_PENDING_H4"
FORM_ID_PREFIX_OPTIONS = ("FORM", "MODEL")
FORM_ID_PREFIX_DECISION = "OPEN_24f_H4"
OPEN_FOR_HUMANS: tuple[str, ...] = (
    "24f FORM- versus MODEL- prefix (H4): both accepted; callers name the prefix; no default chosen",
    "H4 approval of FORM / PARAM / VAL v1 drafts and their later copy to ledgers/schemas/ (Step 24 card outputs)",
    "FITRUN- content-id namespace for PROJECT_REFIT provenance (AI proposal; not a minted ledger id)",
    "lifecycle_status name for the J1.3.4 FORM lifecycle (J1.3.4 says `status`, which KIN uses for record status)",
    "PARAM.value reuses KIN value_obj: MEASURED means point-value shape, not a laboratory measurement",
    "PENDING_15B partition value and the pooling vocabulary (AI additions operationalising SSOT 211.38)",
    "slot role vocabulary and the opaque CONCENTRATION dimension (concentration units are never reduced)",
    "VAL verdict vocabulary; shared lab group between eval series and fit reported as WARN, not ERROR",
    "draft calibration-use eligibility rules (G24.4 operationalisation) and their reason codes",
    "kinetic UNIT entries (R-02 additive UNIT contract) not created here; units are checked by grammar only",
)

_SCHEMA_DIR = Path(__file__).resolve().parents[3] / "registry" / "schemas"
SCHEMA_PATHS: Mapping[str, Path] = {t: _SCHEMA_DIR / f"{t}.draft_v1.schema.json" for t in ("FORM", "PARAM", "VAL")}
NUMERIC = ("MEASURED", "RANGE")

Record = Mapping[str, Any]


class FormParamValError(ValueError):
    """Programming / contract error (bad prefix option, bad record type); never a data verdict."""


# ----------------------------------------------------------------------------- helpers
@functools.cache
def _validator(record_type: str) -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATHS[record_type].read_text(encoding="utf-8"))
    return Draft202012Validator({k: v for k, v in schema.items() if k != "$id"})


def schema_errors(record: Record, record_type: str) -> list[str]:
    """Record-level errors against the v1 draft ('FORM', 'PARAM' or 'VAL'), as 'path :: message'."""
    if record_type not in SCHEMA_PATHS:
        raise ValueError(f"record_type must be one of {sorted(SCHEMA_PATHS)}")
    return sorted("/".join(map(str, e.absolute_path)) + " :: " + e.message
                  for e in _validator(record_type).iter_errors(record))


def _check_prefix(prefix: str) -> None:
    if prefix not in FORM_ID_PREFIX_OPTIONS:
        raise FormParamValError(f"form_id_prefix must be one of {FORM_ID_PREFIX_OPTIONS} (24f is OPEN)")


def _g(d: Any, *keys: Any) -> Any:
    for k in keys:
        if isinstance(d, Mapping):
            d = d.get(k)
        elif isinstance(d, Sequence) and not isinstance(d, str) and isinstance(k, int) and 0 <= k < len(d):
            d = d[k]
        else:
            return None
    return d


def _rid(r: Record) -> str:
    return str(r.get("id", "?"))


def _schema_issues(record: Record, record_type: str) -> list[Issue]:
    return [Issue("SCHEMA_INVALID", ERROR, _rid(record), e) for e in schema_errors(record, record_type)]


def _prefix_issue(form_id: Any, prefix: str, rid: str) -> list[Issue]:
    if isinstance(form_id, str) and not form_id.startswith(prefix + "-"):
        return [Issue("FORM_ID_PREFIX_MISMATCH", ERROR, rid, f"{form_id} under configured prefix {prefix}-")]
    return []


def _dim(expr: Any) -> U.Dimension | None:
    try:
        return U.dimension(expr)
    except (U.UnitError, TypeError):
        return None


_ROLE_DIMENSIONS = {"ACTIVATION_ENERGY": ("ENERGY*AMOUNT^-1", "ACTIVATION_ENERGY_DIMENSION_MISMATCH"),
                    "REFERENCE_TEMPERATURE": ("TEMPERATURE", "REFERENCE_TEMPERATURE_DIMENSION_MISMATCH"),
                    "SCALE_TIME": ("TIME", "SCALE_TIME_DIMENSION_MISMATCH"),
                    "SHAPE": ("1", "SHAPE_DIMENSION_MISMATCH")}


# ----------------------------------------------------------------------------- FORM
def validate_form(form: Record, *, form_id_prefix: str) -> list[Issue]:
    _check_prefix(form_id_prefix)
    rid = _rid(form)
    issues = _schema_issues(form, "FORM") + _prefix_issue(form.get("id"), form_id_prefix, rid)
    seen: set[str] = set()
    for slot in form.get("parameter_slots") or []:
        sym = _g(slot, "symbol")
        if sym in seen:
            issues.append(Issue("SLOT_SYMBOL_DUPLICATE", ERROR, rid, str(sym)))
        seen.add(sym)
        dim = _dim(_g(slot, "dimension"))
        if dim is None:
            issues.append(Issue("SLOT_DIMENSION_UNPARSEABLE", ERROR, rid, f"{sym}: {_g(slot, 'dimension')!r}"))
            continue
        role, order = _g(slot, "role"), _g(slot, "reaction_order") or {}
        if role == "RATE_CONSTANT":
            if order.get("status") == "STATED" and isinstance(order.get("value"), (int, float)):
                want = U.rate_constant_dimension(order["value"])
                if dim != want:
                    issues.append(Issue("RATE_CONSTANT_DIMENSION_ORDER_MISMATCH", ERROR, rid,
                                        f"{sym}: {dim} for order {order['value']}, expected {want}"))
            elif order.get("status") == "UNKNOWN":
                issues.append(Issue("RATE_CONSTANT_ORDER_UNKNOWN", WARN, rid, f"{sym}: unit by order not checkable"))
            else:
                issues.append(Issue("RATE_CONSTANT_ORDER_NOT_APPLICABLE", ERROR, rid, f"{sym}: a rate constant has "
                                                                                      "an order"))
        elif role in _ROLE_DIMENSIONS:
            want_expr, code = _ROLE_DIMENSIONS[role]
            if dim != U.dimension(want_expr):
                issues.append(Issue(code, ERROR, rid, f"{sym}: {dim}, expected {want_expr}"))
    return issues


def validated_domain_issues(form: Record, vals_by_id: Mapping[str, Record]) -> list[Issue]:
    """G24.5 / J1.3.6: a validated domain is set only from VAL records with may_define_validated_domain."""
    rid, out = _rid(form), []
    for vid in form.get("validated_domain_refs") or []:
        v = vals_by_id.get(vid)
        if v is None:
            out.append(Issue("VALIDATED_DOMAIN_REF_MISSING", ERROR, rid, vid))
        elif v.get("form_id") != form.get("id"):
            out.append(Issue("VALIDATED_DOMAIN_VAL_OTHER_FORM", ERROR, rid, vid))
        elif v.get("may_define_validated_domain") is not True:
            out.append(Issue("VALIDATED_DOMAIN_FROM_NON_DEFINING_VAL", ERROR, rid, vid))
    return out


# ----------------------------------------------------------------------------- PARAM
def _slot(form: Record, symbol: Any) -> Mapping[str, Any] | None:
    for s in form.get("parameter_slots") or []:
        if _g(s, "symbol") == symbol:
            return s
    return None


def _numbers(value: Mapping[str, Any]) -> list[float]:
    keys = ("value",) if value.get("status") == "MEASURED" else ("low", "high")
    return [float(value[k]) for k in keys if isinstance(value.get(k), (int, float))]


def _slot_checks(p: Record, slot: Mapping[str, Any], rid: str, opaque: Mapping[str, str] | None) -> list[Issue]:
    out: list[Issue] = []
    value = p.get("value") or {}
    numeric = value.get("status") in NUMERIC
    dim = _dim(slot.get("dimension"))
    if numeric and dim is not None:
        chk = U.check_unit(value.get("unit"), dim, opaque=opaque)
        if chk.verdict == U.INCONSISTENT:
            out.append(Issue("PARAM_UNIT_DIMENSION_MISMATCH", ERROR, rid, chk.detail))
        elif chk.verdict == U.UNKNOWN:
            out.append(Issue("PARAM_UNIT_UNKNOWN", WARN, rid, chk.detail))
    so, po = slot.get("reaction_order") or {}, p.get("reaction_order") or {}
    if so.get("status") == "STATED" and po.get("status") == "STATED" and so.get("value") != po.get("value"):
        out.append(Issue("PARAM_ORDER_MISMATCH_WITH_SLOT", ERROR, rid, f"{po.get('value')} vs {so.get('value')}"))
    if (so.get("status") == "NOT_APPLICABLE") != (po.get("status") == "NOT_APPLICABLE"):
        out.append(Issue("PARAM_ORDER_MISMATCH_WITH_SLOT", ERROR, rid, "order applicability differs from slot"))
    if numeric and slot.get("positive") is True and any(x <= 0 for x in _numbers(value)):
        out.append(Issue("PARAM_NOT_POSITIVE", ERROR, rid, "slot is positive"))
    if slot.get("needs_T_ref") is True:
        t_ref = p.get("T_ref")
        if t_ref is None:
            out.append(Issue("PARAM_T_REF_REQUIRED", ERROR, rid, "slot needs a reference temperature"))
        elif t_ref.get("status") in NUMERIC:
            chk = U.check_arrhenius_units("J/mol", t_ref.get("unit"), opaque=opaque)
            if chk.verdict != U.CONSISTENT:
                out.append(Issue("T_REF_NOT_KELVIN", ERROR, rid, chk.detail))
    return out


def _si_checks(p: Record, rid: str, opaque: Mapping[str, str] | None) -> list[Issue]:
    si, value = p.get("value_si") or {}, p.get("value") or {}
    if si.get("status") != "CONVERTED_EXACT":
        return []
    if value.get("status") != "MEASURED":
        return [Issue("PARAM_SI_RANGE_NOT_CONVERTIBLE", ERROR, rid, "one SI number cannot hold a range or UNKNOWN")]
    unit, unit_si = value.get("unit"), si.get("unit_si")
    try:
        raw, tgt = U.parse_unit(unit, opaque=opaque), U.parse_unit(unit_si, opaque=opaque)
    except (U.UnitError, TypeError) as exc:
        return [Issue("PARAM_SI_NOT_EXACT", ERROR, rid, str(exc))]
    if raw.dimension != tgt.dimension:
        return [Issue("PARAM_SI_UNIT_DIMENSION_MISMATCH", ERROR, rid, f"{unit} vs {unit_si}")]
    if tgt.factor_to_si != 1:
        return [Issue("PARAM_SI_UNIT_NOT_COHERENT", ERROR, rid, f"{unit_si} is not a coherent SI unit")]
    expect = U.to_si(value["value"], unit, opaque=opaque)
    if expect is None:
        return [Issue("PARAM_SI_NOT_EXACT", ERROR, rid, f"{unit} has no exact SI factor (month / year / opaque)")]
    if not math.isclose(float(si.get("value")), expect, rel_tol=1e-12, abs_tol=0.0):
        return [Issue("PARAM_SI_CONVERSION_MISMATCH", ERROR, rid, f"{si.get('value')} != {expect}")]
    return []


def _kin_checks(p: Record, kins_by_id: Mapping[str, Record], rid: str) -> list[Issue]:
    out: list[Issue] = []
    prov = p.get("value_provenance") or {}
    kin_ids = list(prov.get("kin_ids") or [])
    kins = []
    for kid in kin_ids:
        k = kins_by_id.get(kid)
        if k is None:
            out.append(Issue("PROVENANCE_KIN_MISSING", ERROR, rid, kid))
            continue
        kins.append(k)
        if k.get("status") != "ACTIVE":
            out.append(Issue("PROVENANCE_KIN_NOT_ACTIVE", WARN, rid, kid))
        if _g(k, "k_level", "value") == "K0":
            out.append(Issue("PARAM_FROM_K0_AGGREGATE", ERROR, rid, f"{kid} is K0 (SSOT 211.48)"))
    ref = prov.get("author_fit_ref")
    if isinstance(ref, Mapping) and ref.get("kin_id") in kins_by_id:
        fits = kins_by_id[ref["kin_id"]].get("fit") or []
        idx = ref.get("fit_index")
        if not isinstance(idx, int) or not 0 <= idx < len(fits):
            out.append(Issue("AUTHOR_FIT_REF_MISSING", ERROR, rid, f"{ref.get('kin_id')} fit[{idx}]"))
        elif _g(fits[idx], "fit_origin") != "AUTHOR_REPORTED":
            out.append(Issue("AUTHOR_FIT_ORIGIN_MISMATCH", ERROR, rid, f"{ref.get('kin_id')} fit[{idx}]"))
    if kins and len(kins) == len(kin_ids):
        fo = p.get("fitted_on") or {}
        for key, kin_key, code in (("lineage_root_ids", "lineage_root_id", "FITTED_ON_LINEAGE_MISMATCH"),
                                   ("lab_group_ids", "lab_group_id", "FITTED_ON_LAB_GROUP_MISMATCH")):
            from_kin = {_g(k, "lineage", kin_key) for k in kins} - {None}
            if from_kin and from_kin != set(fo.get(key) or []):
                out.append(Issue(code, ERROR, rid, f"{sorted(fo.get(key) or [])} vs KIN {sorted(from_kin)}"))
    return out


def validate_param(param: Record, *, form_id_prefix: str, forms_by_id: Mapping[str, Record],
                   kins_by_id: Mapping[str, Record] | None = None,
                   opaque_units: Mapping[str, str] | None = None) -> list[Issue]:
    """All PARAM checks. ``kins_by_id`` None skips the KIN cross-checks (they are not passed, not failed)."""
    _check_prefix(form_id_prefix)
    rid = _rid(param)
    issues = _schema_issues(param, "PARAM") + _prefix_issue(param.get("form_id"), form_id_prefix, rid)
    form = forms_by_id.get(param.get("form_id"))  # type: ignore[arg-type]
    if form is None:
        issues.append(Issue("PARAM_FORM_MISSING", ERROR, rid, str(param.get("form_id"))))
    else:
        slot = _slot(form, param.get("slot_symbol"))
        if slot is None:
            issues.append(Issue("PARAM_SLOT_NOT_IN_FORM", ERROR, rid, str(param.get("slot_symbol"))))
        else:
            issues += _slot_checks(param, slot, rid, opaque_units)
    issues += _si_checks(param, rid, opaque_units)
    if _g(param, "fitted_on", "pooling") == "POOLED_NON_HIERARCHICAL":
        issues.append(Issue("POOLING_WITHOUT_HIERARCHY", ERROR, rid, "SSOT 211.38"))
    prov = param.get("value_provenance") or {}
    ref = prov.get("author_fit_ref")
    if isinstance(ref, Mapping) and ref.get("kin_id") not in (prov.get("kin_ids") or []):
        issues.append(Issue("AUTHOR_FIT_REF_NOT_IN_KIN_IDS", ERROR, rid, str(ref.get("kin_id"))))
    if kins_by_id is not None:
        issues += _kin_checks(param, kins_by_id, rid)
    return issues


# ----------------------------------------------------------------------------- VAL
def validate_val(val: Record, *, form_id_prefix: str, forms_by_id: Mapping[str, Record],
                 params_by_id: Mapping[str, Record], kins_by_id: Mapping[str, Record] | None = None) -> list[Issue]:
    _check_prefix(form_id_prefix)
    rid = _rid(val)
    issues = _schema_issues(val, "VAL") + _prefix_issue(val.get("form_id"), form_id_prefix, rid)
    if val.get("form_id") not in forms_by_id:
        issues.append(Issue("VAL_FORM_MISSING", ERROR, rid, str(val.get("form_id"))))
    params = []
    for pid in val.get("param_set_ids") or []:
        p = params_by_id.get(pid)
        if p is None:
            issues.append(Issue("VAL_PARAM_MISSING", ERROR, rid, pid))
            continue
        params.append(p)
        if p.get("form_id") != val.get("form_id"):
            issues.append(Issue("VAL_PARAM_FORM_MISMATCH", ERROR, rid, pid))
    fit_kins = {k for p in params for k in _g(p, "value_provenance", "kin_ids") or []}
    evals = list(val.get("eval_series_ids") or [])
    for kid in sorted(set(evals) & fit_kins):
        issues.append(Issue("VAL_EVAL_SERIES_USED_IN_FIT", ERROR, rid, kid))
    if kins_by_id is not None:
        fit_roots = {r for p in params for r in _g(p, "fitted_on", "lineage_root_ids") or []}
        fit_labs = {r for p in params for r in _g(p, "fitted_on", "lab_group_ids") or []}
        for kid in evals:
            k = kins_by_id.get(kid)
            if k is None:
                issues.append(Issue("VAL_EVAL_KIN_MISSING", WARN, rid, kid))
                continue
            root, lab = _g(k, "lineage", "lineage_root_id"), _g(k, "lineage", "lab_group_id")
            if _g(val, "study_disjoint", "status") == "YES" and root in fit_roots:
                issues.append(Issue("VAL_NOT_STUDY_DISJOINT", ERROR, rid, f"{kid} shares {root} with the fit"))
            if lab is not None and lab in fit_labs:
                issues.append(Issue("VAL_SHARES_LAB_GROUP_WITH_FIT", WARN, rid, f"{kid} shares {lab}"))
    return issues


# ----------------------------------------------------------------------------- calibration eligibility
def calibration_eligibility(param: Record, *, form_id_prefix: str, forms_by_id: Mapping[str, Record],
                            kins_by_id: Mapping[str, Record], locked_lineage_root_ids: frozenset[str],
                            opaque_units: Mapping[str, str] | None = None) -> Eligibility:
    """May this PARAM row enter a Step 26d calibration under the draft rules (G24.4)?

    NOT_ELIGIBLE: any validator ERROR, record not ACTIVE, HUMAN_REJECTED, value UNKNOWN, partition other than
    SIM_CALIBRATION, fitted on a SIM-VAL-locked lineage root. UNKNOWN: not HUMAN_VERIFIED, partition
    PENDING_15B, lineage not ASSIGNED, K level UNKNOWN, pooling UNKNOWN, needed T_ref UNKNOWN.
    """
    na: list[str] = []
    un: list[str] = []
    issues = validate_param(param, form_id_prefix=form_id_prefix, forms_by_id=forms_by_id, kins_by_id=kins_by_id,
                            opaque_units=opaque_units)
    na += sorted({f"VALIDATOR_ERROR:{i.code}" for i in issues if i.severity == ERROR})
    if param.get("status") != "ACTIVE":
        na.append("RECORD_NOT_ACTIVE")
    vstatus = _g(param, "verification", "status")
    if vstatus == "HUMAN_REJECTED":
        na.append("HUMAN_REJECTED")
    elif vstatus != "HUMAN_VERIFIED":
        un.append("NOT_HUMAN_VERIFIED")
    if _g(param, "value", "status") not in NUMERIC:
        na.append("VALUE_UNKNOWN")
    part = param.get("partition")
    if part == "PENDING_15B":
        un.append("PARTITION_PENDING")
    elif part != "SIM_CALIBRATION":
        na.append("PARTITION_NOT_SIM_CALIBRATION")
    fo = param.get("fitted_on") or {}
    roots = set(fo.get("lineage_root_ids") or [])
    roots |= {_g(kins_by_id.get(k), "lineage", "lineage_root_id") for k in _g(param, "value_provenance", "kin_ids")
              or []} - {None}
    if roots & set(locked_lineage_root_ids):
        na.append("FITTED_ON_SIM_VAL_LINEAGE")
    if fo.get("lineage_status") != "ASSIGNED":
        un.append("LINEAGE_NOT_ASSIGNED")
    if fo.get("k_level") == "UNKNOWN" or any(_g(kins_by_id.get(k), "k_level", "value") == "UNKNOWN"
                                             for k in _g(param, "value_provenance", "kin_ids") or []):
        un.append("KIN_K_LEVEL_UNKNOWN")
    if fo.get("pooling") == "UNKNOWN":
        un.append("POOLING_UNKNOWN")
    form = forms_by_id.get(param.get("form_id"))  # type: ignore[arg-type]
    slot = _slot(form, param.get("slot_symbol")) if form else None
    if slot and slot.get("needs_T_ref") is True and _g(param, "T_ref", "status") == "UNKNOWN":
        un.append("T_REF_UNKNOWN")
    verdict = NOT_ELIGIBLE if na else (UNKNOWN if un else ELIGIBLE)
    return Eligibility(verdict, tuple(na + un))
