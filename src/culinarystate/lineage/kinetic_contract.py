"""Pure validator for the Step 04.3 KIN / KINPT v1.1 DRAFT contract (S158, DRAFT_PENDING_H4).

Reads records (dicts shaped like registry/schemas/{KIN,KINPT}.draft_v1_1.schema.json and
OBS.draft_v1_1.schema.json) and returns issues and verdicts. It writes nothing, mints nothing and
reads no ledger. The cross-record rules are those that reports/step04/kinetic_trajectory_contract_v1.md
(R04-1..R04-16) and kinetic_trajectory_contract_v1_1_DRAFT.md assign to "the validator":

* raw time units are kept; an exact seconds value must equal the raw value times the unit factor;
* every tau and every temperature profile carries the series clock;
* C0 is stored once; relative-scale t0 points are DEFINITIONAL_NORMALISATION and are not fitted;
* companion series point at each other and pair at the same tau;
* lab_group_id is mandatory on the kinetic plane, UNKNOWN is allowed but never TEST / SIM-VAL eligible;
* censored points stay censored and the series summary agrees with them;
* digitised series follow the two-read rule THR-04K-03.

THR-04K-01..04 are DRAFT_PENDING_H4 / PROPOSED_PILOT rows of registry/preregistered_thresholds_v1.csv.
They are referenced here, never signed: every positive eligibility verdict is ELIGIBLE_UNDER_DRAFT_RULES,
not a gate result. Synthetic tests: tests/unit/test_step04_3_kinetic_contract.py.
"""
from __future__ import annotations

import functools
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

Record = Mapping[str, Any]

ERROR, WARN = "ERROR", "WARN"
ELIGIBLE, NOT_ELIGIBLE, UNKNOWN = "ELIGIBLE_UNDER_DRAFT_RULES", "NOT_ELIGIBLE", "UNKNOWN"

_SCHEMA_DIR = Path(__file__).resolve().parents[3] / "registry" / "schemas"
KIN_SCHEMA_PATH = _SCHEMA_DIR / "KIN.draft_v1_1.schema.json"
KINPT_SCHEMA_PATH = _SCHEMA_DIR / "KINPT.draft_v1_1.schema.json"
_SCHEMA_PATHS = {"KIN": KIN_SCHEMA_PATH, "KINPT": KINPT_SCHEMA_PATH}

# Exact unit factors to seconds. month / year are calendar durations and have no exact factor (07H-R).
SECONDS_PER_UNIT: Mapping[str, int] = {"s": 1, "min": 60, "h": 3600, "d": 86400, "week": 604800}
# Censor kinds with a direction (left / right / interval / unknown), 04.2-min CS registry v1.1.
CENSOR_KINDS = frozenset({"ND", "LT_LOD", "LT_LOQ", "GT_ULOQ", "GT_CAP", "GT_STATED", "LT_STATED", "CENSORED_UNKNOWN",
                          "ROUNDED_INTERVAL", "RANGE_ONLY", "TRACE_BETWEEN_LOD_LOQ"})
RELATIVE_SCALES = frozenset({"RELATIVE_TO_C0", "PERCENT_OF_C0", "LN_RELATIVE", "LOG10_RELATIVE"})
PRODUCT_PROFILE_LOCATIONS = frozenset({"MEDIUM", "CORE", "SURFACE"})
NON_DIGITISED_FORMS = frozenset({"TABLE", "TEXT", "SUPPLEMENT_FILE", "DATABASE"})


@dataclass(frozen=True)
class ThresholdRef:
    """A reference to a pre-registration row. Holding one is not signing it."""

    threshold_id: str
    status: str
    value_text: str


DRAFT_THRESHOLDS: Mapping[str, ThresholdRef] = {
    "THR-04K-01": ThresholdRef("THR-04K-01", "DRAFT_PENDING_H4", ">= 2 distinct numeric tau make a KIN mandatory"),
    "THR-04K-02": ThresholdRef("THR-04K-02", "DRAFT_PENDING_H4", ">= 3 distinct times at one temperature = K1 label"),
    "THR-04K-03": ThresholdRef("THR-04K-03", "DRAFT_PENDING_H4", "two independent reads for TEST / SIM-VAL"),
    "THR-04K-04": ThresholdRef("THR-04K-04", "DRAFT_PENDING_H4", "R04-1 verified by the second extractor"),
}
_MANDATE_MIN_TAU = 2      # THR-04K-01 draft value
_MIN_READS = 2            # THR-04K-03 draft value


@dataclass(frozen=True)
class Issue:
    code: str
    severity: str
    record_id: str
    detail: str = ""


@dataclass(frozen=True)
class Eligibility:
    verdict: str
    reasons: tuple[str, ...]
    rule_refs: tuple[ThresholdRef, ...] = ()


@dataclass(frozen=True)
class FittingSelection:
    included: tuple[str, ...]
    excluded: Mapping[str, str] = field(default_factory=dict)
    censored: tuple[str, ...] = ()


# ----------------------------------------------------------------------------- schema
@functools.cache
def _validator(record_type: str) -> Draft202012Validator:
    schema = json.loads(_SCHEMA_PATHS[record_type].read_text(encoding="utf-8"))
    # jsonschema < 4.18 cannot resolve '#/$defs/...' under a relative $id (Step 04 README section 3).
    return Draft202012Validator({k: v for k, v in schema.items() if k != "$id"})


def schema_errors(record: Record, record_type: str) -> list[str]:
    """Record-level errors against the v1.1 draft ('KIN' or 'KINPT'), as 'path :: message'."""
    if record_type not in _SCHEMA_PATHS:
        raise ValueError(f"record_type must be one of {sorted(_SCHEMA_PATHS)}")
    return sorted("/".join(map(str, e.absolute_path)) + " :: " + e.message
                  for e in _validator(record_type).iter_errors(record))


# ----------------------------------------------------------------------------- small readers
def _tau_key(tau: Record, all_exact: bool) -> tuple[Any, ...] | None:
    """Comparable key of a numeric tau, or None (range, reference without tau)."""
    if tau["status"] == "DEFINITIONAL_ZERO" or (tau["status"] == "REPORTED" and tau["value"] == 0):
        return ("ZERO",)
    if tau["status"] != "REPORTED" or tau["value"] is None:
        return None
    if all_exact:
        return ("s", float(tau["normalised_seconds"]["value"]))
    return (tau["unit"], float(tau["value"]))


def _numeric(kinpts: Sequence[Record]) -> list[Record]:
    return [p for p in kinpts if _tau_key(p["tau"], False) is not None]


def _all_exact(kinpts: Sequence[Record]) -> bool:
    pts = [p for p in _numeric(kinpts) if _tau_key(p["tau"], False) != ("ZERO",)]
    return bool(pts) and all(p["tau"]["normalised_seconds"]["status"] == "CONVERTED_EXACT" for p in pts)


def distinct_numeric_tau(kinpts: Sequence[Record]) -> int:
    """Distinct numeric times of a series (a range or a reference without tau is not a numeric time)."""
    exact = _all_exact(kinpts)
    return len({_tau_key(p["tau"], exact) for p in _numeric(kinpts)})


def series_storage_required(n_distinct_numeric_tau: int) -> bool:
    """R04-1 under the DRAFT threshold THR-04K-01 (unsigned): a KIN is mandatory from this many times."""
    return n_distinct_numeric_tau >= _MANDATE_MIN_TAU


def _seconds_mismatch(value: float | None, unit: str, conv: Record) -> bool:
    if conv["status"] != "CONVERTED_EXACT" or value is None or unit not in SECONDS_PER_UNIT:
        return False
    expected = float(value) * SECONDS_PER_UNIT[unit]
    return abs(float(conv["value"]) - expected) > 1e-9 * max(1.0, abs(expected))


def _is_zero_tau(tau: Record) -> bool:
    return _tau_key(tau, False) == ("ZERO",)


def _point_digitised(p: Record, o: Record | None) -> bool:
    return (p["digitized"]["status"] == "YES" or p["tau"]["derivation"] == "DIGITIZED"
            or (o is not None and o.get("value_origin") == "DIGITIZED"))


# ----------------------------------------------------------------------------- two-read rule (THR-04K-03, draft)
def two_read_status(kinpts: Sequence[Record], obs_by_id: Mapping[str, Record]) -> str:
    """Series-level two-read status computed from the points (mirrors KIN.digitisation_summary)."""
    dig = [(p, obs_by_id.get(p["obs_id"])) for p in kinpts if _point_digitised(p, obs_by_id.get(p["obs_id"]))]
    if not dig:
        return "NOT_APPLICABLE"
    complete = True
    for p, o in dig:
        reads = ((o or {}).get("digitization") or {}).get("n_reads") or {}
        if (reads.get("status") == "REPORTED" and reads.get("value") is not None and reads["value"] < _MIN_READS) \
                or p["digitized"].get("read_independence") == "SINGLE_READ":
            return "SOME_DIGITISED_POINTS_FEWER_READS"
        ok = reads.get("status") == "REPORTED" and (reads.get("value") or 0) >= _MIN_READS
        complete = complete and ok and p["digitized"].get("read_independence") == "INDEPENDENT_READERS"
    return "ALL_DIGITISED_POINTS_TWO_INDEPENDENT_READS" if complete else "NOT_ASSESSED"


# ----------------------------------------------------------------------------- one series
def validate_series(kin: Record, kinpts: Sequence[Record], obs_by_id: Mapping[str, Record], *,
                    companions: Mapping[str, tuple[Record, Sequence[Record]]] | None = None,
                    analyte_form_tokens: frozenset[str] | None = None) -> list[Issue]:
    """Cross-record checks of one KIN, its KINPT and their OBS. Returns issues; raises nothing on bad data.

    companions maps a companion kin_id to (KIN, its KINPT); None means "not supplied" (pairing not checked).
    analyte_form_tokens is the token set of an APPROVED analyte-form registry; None means none is approved.
    """
    out: list[Issue] = []

    def add(code: str, sev: str, rid: str, detail: str = "") -> None:
        out.append(Issue(code, sev, rid, detail))

    kid = kin["id"]
    _check_points(kin, kinpts, add)
    _check_profiles(kin, add)
    _check_obs_links(kin, kinpts, obs_by_id, add)
    _check_c0_and_scale(kin, kinpts, obs_by_id, add)
    _check_censoring(kin, kinpts, obs_by_id, add)
    if kin["replicate_structure"]["design"] == "REPEATED_MEASURES_SAME_UNITS":
        for p in kinpts:
            if not p["replicate"].get("unit_label"):
                add("UNIT_LABEL_REQUIRED", ERROR, p["id"], "repeated-measures design needs a stable unit label (R04-10)")
    if companions is not None and kin.get("companion_status") == "LINKED":
        _check_companions(kin, kinpts, obs_by_id, companions, add)
    af = kin["target"]["analyte_form"]
    if af.get("token_status") == "REGISTRY_TOKEN":
        if analyte_form_tokens is None:
            add("ANALYTE_TOKEN_WITHOUT_APPROVED_REGISTRY", ERROR, kid, "no analyte-form registry is approved (D21-22)")
        elif af.get("token") not in analyte_form_tokens:
            add("ANALYTE_TOKEN_NOT_IN_REGISTRY", ERROR, kid, str(af.get("token")))
    return out


def _check_points(kin: Record, kinpts: Sequence[Record], add: Any) -> None:
    kid, tb = kin["id"], kin["time_base"]
    keys = Counter()
    for p in kinpts:
        r, t = p["replicate"], p["tau"]
        if p["kin_id"] != kid:
            add("KIN_ID_MISMATCH", ERROR, p["id"], f"{p['kin_id']} != {kid}")
        keys[(p["kin_id"], p["sequence_index"], r.get("run_id") or "SINGLE", r.get("unit_label") or "AGG")] += 1
        if t["clock"] != tb["clock"]:
            add("TAU_CLOCK_MISMATCH", ERROR, p["id"], f"{t['clock']} != {tb['clock']}")
        if (tb["unit"] != "UNKNOWN" and t["status"] in ("REPORTED", "RANGE") and t["unit"] != tb["unit"]):
            add("TAU_UNIT_DIFFERS_FROM_TIME_BASE", WARN, p["id"], f"{t['unit']} vs {tb['unit']} (raw units kept)")
        value = 0 if t["status"] == "DEFINITIONAL_ZERO" else t["value"]
        if _seconds_mismatch(value, t["unit"], t["normalised_seconds"]):
            add("SECONDS_CONVERSION_MISMATCH", ERROR, p["id"], "exact seconds differ from raw value x unit factor")
        if t["status"] == "RANGE" and t["low"] is not None and t["high"] is not None and t["low"] > t["high"]:
            add("TAU_RANGE_INVERTED", ERROR, p["id"], "low > high")
    for key, n in keys.items():
        if n > 1:
            add("KINPT_MINT_KEY_DUPLICATE", ERROR, kid, "|".join(map(str, key)))
    n = distinct_numeric_tau(kinpts)
    if n != kin["n_timepoints"]:
        add("N_TIMEPOINTS_MISMATCH", ERROR, kid, f"n_timepoints {kin['n_timepoints']} vs {n} distinct numeric tau")


def _check_profiles(kin: Record, add: Any) -> None:
    kid, clock = kin["id"], kin["time_base"]["clock"]
    profiles = kin["condition_profile"]["temperature_profiles"]
    for loc, n in Counter(pr["location"] for pr in profiles).items():
        if n > 1:
            add("DUPLICATE_PROFILE_LOCATION", WARN, kid, f"{n} profiles at {loc}")
    for i, pr in enumerate(profiles):
        if pr["clock"] != clock:
            add("PROFILE_CLOCK_MISMATCH", ERROR, kid, f"profile {i}: {pr['clock']} != {clock}")
        for j, pt in enumerate(pr["points"]):
            if _seconds_mismatch(pt["tau"], pt["tau_unit"], pt["tau_seconds"]):
                add("SECONDS_CONVERSION_MISMATCH", ERROR, kid, f"profile {i} point {j}")


def _check_obs_links(kin: Record, kinpts: Sequence[Record], obs_by_id: Mapping[str, Record], add: Any) -> None:
    kid = kin["id"]
    used = Counter(p["obs_id"] for p in kinpts)
    flags: list[bool] = []
    unknown_flag = False
    for p in kinpts:
        o = obs_by_id.get(p["obs_id"])
        if used[p["obs_id"]] > 1:
            add("OBS_SHARED_BY_KINPTS", ERROR, p["id"], f"{p['obs_id']} behind {used[p['obs_id']]} KINPT")
        if o is None:
            add("OBS_MISSING", ERROR, p["id"], p["obs_id"])
        elif o["series_link"] != {"status": "LINKED_KINPT", "kinpt_id": p["id"]}:
            add("OBS_SERIES_LINK_MISMATCH", ERROR, p["id"], f"{p['obs_id']} series_link {o['series_link']}")
        flag = p["digitized"]["status"]
        obs_dig = o is not None and o.get("value_origin") == "DIGITIZED"
        tau_dig = p["tau"]["derivation"] == "DIGITIZED"
        if (flag == "YES" and not (obs_dig or tau_dig)) or (flag != "YES" and (obs_dig or tau_dig)):
            add("DIGITIZED_FLAG_MISMATCH", ERROR, p["id"], f"digitized {flag}, OBS {obs_dig}, tau {tau_dig}")
        flags.append(_point_digitised(p, o))
        unknown_flag = unknown_flag or flag == "UNKNOWN"
    form = kin["series_origin_form"]
    if flags and ((form == "FIGURE_DIGITIZED" and not all(flags))
                  or (form == "MIXED_TABLE_AND_FIGURE" and (all(flags) or not any(flags)))
                  or (form in NON_DIGITISED_FORMS and any(flags))):
        add("ORIGIN_FORM_DIGITISATION_MISMATCH", ERROR, kid, f"{form} with {sum(flags)}/{len(flags)} digitised points")
    summ = kin["digitisation_summary"]
    if summ["any_digitised"] != "UNKNOWN":
        actual = "YES" if any(flags) else ("UNKNOWN" if unknown_flag else "NO")
        if summ["any_digitised"] != actual:
            add("DIGITISATION_SUMMARY_MISMATCH", ERROR, kid, f"any_digitised {summ['any_digitised']} vs {actual}")
        computed = two_read_status(kinpts, obs_by_id)
        if summ["two_read_status"] != "NOT_ASSESSED" and summ["two_read_status"] != computed:
            add("DIGITISATION_SUMMARY_MISMATCH", ERROR, kid, f"two_read_status {summ['two_read_status']} vs {computed}")


def _check_c0_and_scale(kin: Record, kinpts: Sequence[Record], obs_by_id: Mapping[str, Record], add: Any) -> None:
    kid, tgt = kin["id"], kin["target"]
    cid, ref, scale = tgt["c0_obs_id"], tgt["c0_reference"], tgt["value_scale"]
    if cid is not None:
        o0 = obs_by_id.get(cid)
        ic = kin["condition_profile"]["initial_conditions"]["initial_concentration"]
        if o0 is None:
            add("C0_OBS_MISSING", WARN, kid, f"{cid} not supplied; C0 consistency not checked")
        elif ic is not None and (ic.get("value"), ic.get("unit")) != (o0["value"].get("value"), o0["value"].get("unit")):
            add("C0_VALUE_MISMATCH", ERROR, kid, "initial_concentration differs from the C0 OBS (C0 is stored once)")
        if ref == "T0_SAMPLE" and cid not in {p["obs_id"] for p in kinpts if _is_zero_tau(p["tau"])}:
            add("C0_NOT_A_T0_POINT", ERROR, kid, f"{cid} is not the OBS of a t = 0 point of this series")
    if scale in RELATIVE_SCALES and ref == "UNKNOWN":
        add("RELATIVE_SCALE_C0_UNKNOWN", WARN, kid, "relative series without a stated C0 source (R04-13)")
    for p in kinpts:
        o = obs_by_id.get(p["obs_id"])
        if o is None:
            continue
        definitional = o.get("value_origin") == "DEFINITIONAL_NORMALISATION"
        if scale in RELATIVE_SCALES and _is_zero_tau(p["tau"]) and not definitional:
            add("RELATIVE_T0_NOT_DEFINITIONAL", ERROR, p["id"], "t0 point of a relative series is 1 by definition")
        if definitional and (scale == "ABSOLUTE" or not _is_zero_tau(p["tau"])):
            add("DEFINITIONAL_NORMALISATION_MISPLACED", ERROR, p["id"], f"scale {scale}, tau {p['tau']['status']}")
        elif definitional and scale in ("OTHER", "UNKNOWN"):
            add("DEFINITIONAL_NORMALISATION_SCALE_UNSTATED", WARN, p["id"], f"scale {scale}")


def _check_censoring(kin: Record, kinpts: Sequence[Record], obs_by_id: Mapping[str, Record], add: Any) -> None:
    kinds = [obs_by_id[p["obs_id"]]["censoring"]["kind"] for p in kinpts if p["obs_id"] in obs_by_id]
    censored = {k for k in kinds if k in CENSOR_KINDS}
    s = kin["censoring_summary"]
    listed = set(s["kinds_present"]) & CENSOR_KINDS
    bad = ((s["any_censored"] == "YES" and (not censored or listed != censored))
           or (s["any_censored"] == "NO" and (censored or "NOT_REPORTED" in kinds)))
    if bad:
        add("CENSORING_SUMMARY_MISMATCH", ERROR, kin["id"],
            f"summary {s['any_censored']} {sorted(listed)} vs points {sorted(censored)}")


def _check_companions(kin: Record, kinpts: Sequence[Record], obs_by_id: Mapping[str, Record],
                      companions: Mapping[str, tuple[Record, Sequence[Record]]], add: Any) -> None:
    kid, msid = kin["id"], kin["mass_balance_set_id"]
    for c in kin["companion_series"]:
        if c["kin_id"] not in companions:
            add("COMPANION_MISSING", WARN, kid, f"{c['kin_id']} not supplied")
            continue
        ck, cpts = companions[c["kin_id"]]
        if msid is not None and ck.get("mass_balance_set_id") not in (msid, None):
            add("COMPANION_MASS_BALANCE_SET_MISMATCH", ERROR, kid, f"{ck['id']} in {ck['mass_balance_set_id']}")
        elif msid is not None and ck.get("mass_balance_set_id") is None:
            add("COMPANION_MASS_BALANCE_SET_ABSENT", WARN, kid, ck["id"])
        for p in kinpts:
            key = _tau_key(p["tau"], False)
            same = [q for q in cpts if key is not None and _tau_key(q["tau"], False) == key
                    and q["replicate"].get("run_id") == p["replicate"].get("run_id")]
            if same and not any(_paired(p, q, obs_by_id) for q in same):
                add("COMPANION_POINT_UNPAIRED", WARN, p["id"], f"no pairing with {c['kin_id']} at the same tau")


def _paired(p: Record, q: Record, obs_by_id: Mapping[str, Record]) -> bool:
    if q["id"] in p["paired_kinpt_ids"] or p["id"] in q["paired_kinpt_ids"]:
        return True
    a, b = obs_by_id.get(p["obs_id"]), obs_by_id.get(q["obs_id"])
    return a is not None and b is not None and a["sample_id"] == b["sample_id"]


# ----------------------------------------------------------------------------- sets of series
def validate_series_set(kins: Iterable[Record]) -> list[Issue]:
    """Checks across series: split group nested in one lab group (L-10); grid fits name every grid member."""
    kins = list(kins)
    out: list[Issue] = []
    labs: dict[str, set[str]] = defaultdict(set)
    grids: dict[str, set[str]] = defaultdict(set)
    for k in kins:
        lin = k["lineage"]
        if lin.get("split_group_id") and lin.get("lab_group_id"):
            labs[lin["split_group_id"]].add(lin["lab_group_id"])
        if k["condition_profile"].get("condition_grid_id"):
            grids[k["condition_profile"]["condition_grid_id"]].add(k["id"])
    for sg, ls in sorted(labs.items()):
        if len(ls) > 1:
            out.append(Issue("LAB_GROUP_NESTING_VIOLATED", ERROR, sg, f"split group spans {sorted(ls)}"))
    for k in kins:
        members = grids.get(k["condition_profile"].get("condition_grid_id") or "", set())
        for i, f in enumerate(k.get("fit") or []):
            if f.get("scope") == "CONDITION_GRID" and f.get("input_kin_status") == "STATED" \
                    and not members <= set(f.get("input_kin_ids") or []):
                out.append(Issue("GRID_FIT_INPUTS_INCOMPLETE", ERROR, k["id"],
                                 f"fit {i} misses {sorted(members - set(f.get('input_kin_ids') or []))} (R04-16)"))
    return out


# ----------------------------------------------------------------------------- verdicts
def _verdict(levels: list[tuple[str, str]], refs: tuple[ThresholdRef, ...] = ()) -> Eligibility:
    reasons = tuple(sorted({r for _, r in levels}))
    if any(v == NOT_ELIGIBLE for v, _ in levels):
        return Eligibility(NOT_ELIGIBLE, reasons, refs)
    if any(v == UNKNOWN for v, _ in levels):
        return Eligibility(UNKNOWN, reasons, refs)
    return Eligibility(ELIGIBLE, reasons, refs)


def split_eligibility(kin: Record, kinpts: Sequence[Record], obs_by_id: Mapping[str, Record]) -> Eligibility:
    """TEST / SIM-VAL eligibility of one series under the DRAFT rules. Anything but ELIGIBLE_UNDER_DRAFT_RULES
    means "do not place in TEST / SIM-VAL"; UNKNOWN never becomes eligible."""
    lin, lv = kin["lineage"], []
    if kin.get("status") != "ACTIVE":
        lv.append((NOT_ELIGIBLE, "RECORD_NOT_ACTIVE"))             # a deprecated / superseded / retracted record
    ver = (kin.get("verification") or {}).get("status")
    if ver == "HUMAN_REJECTED":
        lv.append((NOT_ELIGIBLE, "HUMAN_REJECTED"))
    elif ver != "HUMAN_VERIFIED":
        lv.append((UNKNOWN, "NOT_HUMAN_VERIFIED"))                 # 04.6-min KIN row: test / calibration only if human verified
    if lin["independence_resolution"] == "UNKNOWN":
        lv.append((NOT_ELIGIBLE, "INDEPENDENCE_UNKNOWN"))          # D-029 D-5: UNKNOWN independence = TRAIN only
    if lin["assignment_status"] == "PENDING":
        lv.append((UNKNOWN, "LINEAGE_PENDING"))
    if lin["lab_group_status"] == "UNKNOWN":
        lv.append((NOT_ELIGIBLE, "LAB_GROUP_UNKNOWN"))             # contract section 10
    elif lin["lab_group_status"] == "PENDING":
        lv.append((UNKNOWN, "LAB_GROUP_PENDING"))
    if kin["evidence_tier"] == "E5":
        lv.append((NOT_ELIGIBLE, "EVIDENCE_TIER_E5"))              # FW-09: E5-E7 never test / calibration
    for p in kinpts:
        o = obs_by_id.get(p["obs_id"])
        if o is None:
            lv.append((UNKNOWN, "OBS_MISSING"))
            continue
        if not _point_digitised(p, o):
            continue
        dig = o.get("digitization") or {}
        reads = dig.get("n_reads") or {}
        indep = p["digitized"].get("read_independence")
        if reads.get("status") != "REPORTED" or reads.get("value") is None:
            lv.append((NOT_ELIGIBLE, "READ_COUNT_NOT_REPORTED"))
        elif reads["value"] < _MIN_READS or indep == "SINGLE_READ":
            lv.append((NOT_ELIGIBLE, "SINGLE_READ"))
        if indep == "SAME_READER_REPEATED":
            lv.append((UNKNOWN, "READ_INDEPENDENCE_OPEN_H4"))
        elif indep in ("NOT_REPORTED", "UNKNOWN"):
            lv.append((UNKNOWN, "READ_INDEPENDENCE_NOT_REPORTED"))
        if (dig.get("read_sd") or {}).get("status") != "REPORTED":
            lv.append((UNKNOWN, "READ_SD_NOT_STORED"))
    return _verdict(lv, (DRAFT_THRESHOLDS["THR-04K-03"],))


def arrhenius_eligibility(kin: Record) -> Eligibility:
    """R04-15: Arrhenius-eligible only with a MEDIUM / CORE / SURFACE profile, PRODUCT_ISOTHERMAL_STATED, or the
    come-up time EXCLUDED and stated. UNSPECIFIED is never promoted; missing facts give UNKNOWN. A positive verdict
    needs a REPORTED temperature: with temperature NOT_REPORTED it becomes NOT_ELIGIBLE, with temperature status
    UNKNOWN it becomes UNKNOWN, whatever the isothermality or come-up statement (S158 AI review R2)."""
    v = _arrhenius_from_profile(kin)
    status = kin["condition_profile"]["temperature_status"]
    if v.verdict == ELIGIBLE and status == "NOT_REPORTED":             # no temperature: no route to ELIGIBLE
        return Eligibility(NOT_ELIGIBLE, ("TEMPERATURE_NOT_REPORTED",))
    if v.verdict == ELIGIBLE and status == "UNKNOWN":
        return Eligibility(UNKNOWN, ("TEMPERATURE_STATUS_UNKNOWN",))
    return v


def _arrhenius_from_profile(kin: Record) -> Eligibility:
    cp, cut = kin["condition_profile"], kin["time_base"]["come_up_time"]["status"]
    locs = {p["location"] for p in cp["temperature_profiles"]}
    if locs & PRODUCT_PROFILE_LOCATIONS:
        return Eligibility(ELIGIBLE, ("PRODUCT_OR_MEDIUM_PROFILE",))
    if cp["isothermality"] == "PRODUCT_ISOTHERMAL_STATED":
        return Eligibility(ELIGIBLE, ("PRODUCT_ISOTHERMAL_STATED",))
    if cut == "EXCLUDED_FROM_TIME":
        return Eligibility(ELIGIBLE, ("COME_UP_EXCLUDED",))
    unknown = [r for r, c in (("TEMPERATURE_STATUS_UNKNOWN", cp["temperature_status"] == "UNKNOWN"),
                               ("ISOTHERMALITY_UNKNOWN", cp["isothermality"] == "UNKNOWN"),
                               ("COME_UP_UNKNOWN", cut == "UNKNOWN"),
                               ("PROFILE_LOCATION_UNSPECIFIED", "UNSPECIFIED" in locs)) if c]
    if unknown:
        return Eligibility(UNKNOWN, tuple(unknown))
    return Eligibility(NOT_ELIGIBLE, ("SETPOINT_ONLY_OR_NO_PRODUCT_TEMPERATURE",))


def fitting_selection(kin: Record, kinpts: Sequence[Record], obs_by_id: Mapping[str, Record]) -> FittingSelection:
    """Which points fitting code may use as observations. Nothing is discarded: excluded points keep their
    records (R04-2); censored points are included and listed so that they are fitted as censored (R04-9)."""
    included: list[str] = []
    excluded: dict[str, str] = {}
    censored: list[str] = []
    for p in kinpts:
        o, t = obs_by_id.get(p["obs_id"]), p["tau"]
        if o is None:
            excluded[p["id"]] = "OBS_MISSING"
        elif o.get("value_origin") == "DEFINITIONAL_NORMALISATION":
            excluded[p["id"]] = "DEFINITIONAL_NORMALISATION"       # R04-13
        elif t["status"] == "NOT_APPLICABLE_REFERENCE":
            excluded[p["id"]] = "NO_TAU_REFERENCE"
        elif t["unit"] == "UNKNOWN" or kin["time_base"]["unit"] == "UNKNOWN":
            excluded[p["id"]] = "TAU_UNIT_UNKNOWN"                 # R04-5
        else:
            included.append(p["id"])
            if o["censoring"]["kind"] in CENSOR_KINDS:
                censored.append(p["id"])
    return FittingSelection(tuple(included), excluded, tuple(censored))
