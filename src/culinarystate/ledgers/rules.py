"""Cross-field scientific/provenance laws that JSON Schema cannot express.

Each rule returns a list of human-readable violations (empty = OK).
"""
from __future__ import annotations

import re
from typing import Callable

from .common import HUMANS

Rule = Callable[[dict], list[str]]
AI_NAME = re.compile(r"(claude|gpt|llm|gemini|agent|\bai\b|bot|model)", re.IGNORECASE)
GROUNDED_TIERS = {"E1", "E2", "E3", "E4"}
MASS_UNITS = {"g", "gram", "grams", "kg", "mg", "oz", "lb"}


def _qv_num(qv: dict | None) -> float | None:
    if qv and qv.get("status") == "MEASURED":
        return qv.get("value")
    return None


def rule_human_verification(r: dict) -> list[str]:
    v = r.get("verification", {})
    errs = []
    if v.get("status") in {"HUMAN_VERIFIED", "HUMAN_REJECTED"}:
        who = v.get("verifier") or ""
        if who not in HUMANS:
            errs.append(f"verification.status={v['status']} requires verifier in {sorted(HUMANS)}, got {who!r}")
        if AI_NAME.search(who):
            errs.append("AI review is never human verification")
        if not v.get("verified_at"):
            errs.append("human verification requires verified_at")
    if v.get("status") == "AI_PRECHECKED" and v.get("verifier") in HUMANS:
        errs.append("AI_PRECHECKED must not name a human verifier; use ai_reviewer")
    return errs


def rule_supersession(r: dict) -> list[str]:
    if r.get("status") == "SUPERSEDED" and not r.get("superseded_by"):
        return ["status=SUPERSEDED requires superseded_by"]
    if r.get("superseded_by") == r.get("id"):
        return ["record cannot supersede itself"]
    return []


def rule_evd(r: dict) -> list[str]:
    errs = []
    tier, v, prov = r["tier"], r["verification"]["status"], r["provenance"]
    # AH1: study lineage
    if r["origin_type"] == "PRIMARY_STUDY":
        if r["study_id_status"] == "PRESENT" and not r.get("study_ids"):
            errs.append("study_id_status=PRESENT but study_ids empty")
        if r["study_id_status"] == "NOT_APPLICABLE":
            errs.append("PRIMARY_STUDY rows cannot mark study_id_status NOT_APPLICABLE")
    if r.get("study_ids") and r["study_id_status"] != "PRESENT":
        errs.append("study_ids given but study_id_status != PRESENT")
    # tiers
    if tier == "E4" and v != "HUMAN_VERIFIED":
        errs.append("tier E4 requires HUMAN_VERIFIED (LLM-extracted, human-verified)")
    if tier == "E5" and v == "HUMAN_VERIFIED":
        errs.append("HUMAN_VERIFIED LLM-extracted row must be tier E4, not E5")
    if tier in {"E4", "E5"} and prov["method"] != "LLM":
        errs.append(f"tier {tier} means LLM-extracted; provenance.method must be LLM")
    # E3 = database-curated: aggregates, or primary-study values imported from a curated database
    curated_primary = r["origin_type"] == "PRIMARY_STUDY" and prov["method"] == "IMPORT"
    if tier == "E3" and not (r["origin_type"] in {"DATABASE_AGGREGATE", "REVIEW_AGGREGATE"} or curated_primary):
        errs.append("tier E3 is for database-curated rows (aggregate, or imported primary values)")
    if tier in {"E6", "E7"} and r["origin_type"] == "PRIMARY_STUDY":
        errs.append("E6/E7 are model/simulator outputs, not primary-study evidence")
    if tier in GROUNDED_TIERS and not prov.get("locator"):
        errs.append(f"tier {tier} requires provenance.locator (page/table/figure/span/row)")
    # censoring flag must agree with values
    values = [r.get("before"), r.get("after"), *(r.get("derived") or {}).values()]
    censored_vals = any(isinstance(v, dict) and v.get("status") == "CENSORED" for v in values)
    if censored_vals != r["censored"]:
        errs.append(f"censored={r['censored']} disagrees with CENSORED values ({censored_vals})")
    # percent_change consistency when both sides measured in same unit
    b, a = r.get("before"), r.get("after")
    pc = (r.get("derived") or {}).get("percent_change")
    if _qv_num(b) not in (None, 0) and _qv_num(a) is not None and _qv_num(pc) is not None \
            and b.get("unit") == a.get("unit"):
        expect = (a["value"] - b["value"]) / b["value"] * 100
        if abs(expect - pc["value"]) > max(1.0, abs(expect) * 0.01):
            errs.append(f"percent_change {pc['value']} inconsistent with before/after ({expect:.2f})")
    return errs


def rule_qnt(r: dict) -> list[str]:
    """No invented grams: mass from a non-mass unit needs a sourced POR- record."""
    errs = []
    norm, parsed = r["normalized"], r["parsed"]
    unit_raw = (parsed.get("unit_raw") or "").strip().lower()
    if norm.get("status") in {"MEASURED", "RANGE"} and (norm.get("unit") or "").lower() == "g":
        if unit_raw not in MASS_UNITS and not r.get("portion_id"):
            errs.append(f"grams from unit {unit_raw or '<none>'!r} require portion_id (POR-); else UNKNOWN")
    mass = r.get("mass_g") or {}
    if mass.get("status") in {"MEASURED", "RANGE"} and unit_raw not in MASS_UNITS \
            and r.get("conversion_method") not in {"SOURCE_STATED", "PORTION_RECORD"}:
        errs.append("mass_g from a non-mass unit needs SOURCE_STATED mass or a PORTION_RECORD (POR-)")
    if r.get("conversion_method") == "PORTION_RECORD" and not r.get("portion_id"):
        errs.append("conversion_method PORTION_RECORD requires portion_id")
    if parsed.get("kind") == "QUALITATIVE" and any(
            (r.get(k) or {}).get("status") in {"MEASURED", "RANGE"} for k in ("normalized", "mass_g", "volume_ml")):
        errs.append("qualitative quantities (pinch, to taste) never get numeric totals")
    return errs


def rule_por(r: dict) -> list[str]:
    if not r["provenance"].get("source_ids"):
        return ["POR- (ingredient-specific grams) requires provenance.source_ids"]
    return []


def rule_imap(r: dict) -> list[str]:
    rel, c = r["relation"], r.get("concentration") or {}
    errs = []
    if rel == "MEASURED_CONCENTRATION" and c.get("status") not in {"MEASURED", "RANGE", "CENSORED"}:
        errs.append("MEASURED_CONCENTRATION requires a measured/range/censored concentration")
    if rel != "MEASURED_CONCENTRATION" and c.get("status") in {"MEASURED", "RANGE"}:
        errs.append(f"{rel} must not carry a numeric concentration")
    if rel == "PROCESS_CHANGE" and not r.get("evidence_ids"):
        errs.append("PROCESS_CHANGE requires evidence_ids (EVD-)")
    return errs


def rule_cond(r: dict) -> list[str]:
    errs = []
    for t in r.get("temperatures", []):
        raw = (t["value"].get("raw") or "").lower()
        if re.search(r"\b(low|medium|high|moderate)\b.*\bheat\b", raw) and t["value"]["status"] == "MEASURED":
            errs.append(f"'{raw}' is qualitative heat; store status=QUALITATIVE, not a number")
    return errs


def rule_state(r: dict) -> list[str]:
    errs = []
    if r["state_version"] > 0 and not r.get("previous_state_id"):
        errs.append("state_version>0 requires previous_state_id (append-only history)")
    if r.get("overrides_state_id") and r["belief"] != "OBSERVED":
        errs.append("only OBSERVED states may override a prior state")
    return errs


def rule_allergen(r: dict) -> list[str]:
    note = (r.get("notes") or "") + " " + (r["provenance"].get("agent") or "")
    if "flavordb" in note.lower():
        return ["FlavorDB is never an allergen authority (AH3)"]
    return []


def rule_clm(r: dict) -> list[str]:
    errs = []
    if not (r.get("evidence_ids") or r.get("experiment_ids")):
        errs.append("claims need evidence_ids or experiment_ids")
    if r["approval"] == "HUMAN_APPROVED" and r.get("approved_by") not in HUMANS:
        errs.append("HUMAN_APPROVED claim needs approved_by in humans")
    if r["claim_type"] == "SOTA" and not r.get("gate_ids"):
        errs.append("SOTA / 'beats baseline' claims require a GATE (H6) record")
    return errs


def rule_model(r: dict) -> list[str]:
    if r["reproduction_status"] == "REPRODUCED" and r.get("selected_on") == "TEST":
        return ["checkpoint selected on TEST cannot be labelled REPRODUCED clean; mark deviation"]
    return []


VALUE_PREDICATES = {"ING_HAS_CATEGORY", "ING_USED_IN_CUISINE", "PROC_IN_FAMILY", "TOOL_HAS_CATEGORY",
                    "COMPONENT_CONTAINS_ING"}
STAT_PREDICATES = {"PROC_TYPICAL_DURATION", "PROC_TYPICAL_TEMPERATURE"}


def rule_kge(r: dict) -> list[str]:
    errs = []
    has_id, has_val = bool(r.get("object_id")), bool(r.get("object_value"))
    if r["predicate"] in STAT_PREDICATES:
        if not r.get("quantiles"):
            errs.append(f"{r['predicate']} needs quantiles")
    elif r["predicate"] in VALUE_PREDICATES:
        if not has_val:
            errs.append(f"{r['predicate']} needs object_value")
    elif has_id == has_val or not has_id:
        errs.append(f"{r['predicate']} needs object_id (and no object_value)")
    if r["method"] in ("CO_OCCURRENCE", "SEQUENCE") and r["support"]["recipes"] < 1:
        errs.append("statistical edge needs recipe support ≥ 1")
    if r["confidence_band"] == "HIGH" and r["method"] == "LLM" and r["verification"]["status"] != "HUMAN_VERIFIED":
        errs.append("LLM-proposed edges cannot be HIGH confidence without human verification")
    return errs


RULES: dict[str, list[Rule]] = {
    "EVD": [rule_evd], "QNT": [rule_qnt], "POR": [rule_por], "IMAP": [rule_imap], "COND": [rule_cond],
    "STATE": [rule_state], "ALLERGEN": [rule_allergen], "CLM": [rule_clm], "MODEL": [rule_model],
    "KGE": [rule_kge],
}
UNIVERSAL: list[Rule] = [rule_human_verification, rule_supersession]


def check(record: dict) -> list[str]:
    errs: list[str] = []
    for rule in UNIVERSAL + RULES.get(record.get("record_type", ""), []):
        errs.extend(rule(record))
    return errs
