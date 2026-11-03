"""MECH v1.1 DRAFT contract: semantic validator and the read API for Steps 22a / 23a (S158, DRAFT_PENDING_H4).

Pure functions over MECH entries shaped like registry/schemas/MECH.draft_v1_1.schema.json. Nothing here
writes, mints or reads a ledger, and nothing here evaluates applicability: the three-valued evaluation and
the route rule belong to Step 23 (R-15). The helpers only expose what an entry declares so that a consumer
cannot silently drop a gate, a modifier axis or an open question:

* ``schema_errors``                 record-level errors against the v1.1 draft;
* ``semantic_problems``             checks the schema cannot express (ported from the v1 README design + v1.1);
* ``asymmetric_links`` / ``unresolved_links``  registry-level link checks;
* ``required_condition_axes``       every gate axis, marking gates a modifier is evaluated through (rule M-1);
* ``required_state_inputs``         precondition, history and inline-modifier states;
* ``candidate_effects``             (target, effect type, allowed sign set): never a magnitude (G21.8);
* ``consumable_for_applicability``  only ACCEPTED, human-verified, gates-known entries with no open question.

Synthetic tests: tests/unit/test_step21_mech_v1_1_semantics.py.
"""
from __future__ import annotations

import csv
import functools
import io
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

Entry = Mapping[str, Any]
Row = Mapping[str, str]

# R-15 verdict tokens (Step 23 vocabulary). This module returns none of them as a verdict.
APPLICABLE, NOT_APPLICABLE, UNKNOWN = "APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"
SCHEMA_VERSION = "1.1.0-draft"

_ROOT = Path(__file__).resolve().parents[3]
MECH_SCHEMA_PATH = _ROOT / "registry" / "schemas" / "MECH.draft_v1_1.schema.json"
CV_REGISTRY_PATH = _ROOT / "registry" / "condition_variable_registry_v1.csv"
EFFECT_REGISTRY_PATH = _ROOT / "registry" / "effect_type_registry_draft_v1.csv"

# Rule E-7 (OPEN_QUESTION D21-20 / EQ21-07): temperature, pH and water-activity axes.
_E7_AXES = frozenset({"CV-005", "CV-006", "CV-007", "CV-008", "CV-013", "CV-015"})
_CSV_CLASS = {"SPECIES": {"SPECIES"}, "TRANSFERRED_AMOUNT": {"TRANSFERRED_AMOUNT"}, "STATE": {"STATE"},
              "OBSERVABLE_OR_STATE": {"OBSERVABLE", "STATE"},
              "ANY": {"SPECIES", "TRANSFERRED_AMOUNT", "OBSERVABLE", "STATE"}}
_ITEM_COLLECTIONS = ("preconditions", "condition_gates", "inhibitors_mitigators", "competes_with", "consecutive_with",
                     "affected_targets", "markers", "history_dependence")


@dataclass(frozen=True)
class AxisRequirement:
    """A condition axis an entry needs to be evaluated (Step 22 required_condition_axes)."""

    cv_id: str
    location: str
    basis: str
    clock: str
    gate_key: str
    gate_type: str
    via: str                     # GATE, or MODIFIER_GATE when a modifier is evaluated through this gate (M-1)


@dataclass(frozen=True)
class StateInput:
    """A state an entry reads (Step 22 required_state_inputs)."""

    state_key: str | None
    svar_id: str | None
    ref_status: str
    source: str                  # PRECONDITION / HISTORY / MODIFIER
    item_key: str                # precondition_key, history role, or inhibitor_key


@dataclass(frozen=True)
class CandidateEffect:
    """What an entry may do to one target: a sign set, never an amount or a rate."""

    mechanism_key: str
    target_key: str
    target_svar_id: str | None
    target_state_key: str | None
    target_class: str
    target_role: str
    compartment: str
    effect_type: str
    allowed_directions: tuple[str, ...]
    trajectory_shape: str
    analyte_form_token: str | None
    status: str


# ----------------------------------------------------------------------------- schema and registries
@functools.cache
def _validator() -> Draft202012Validator:
    schema = json.loads(MECH_SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator({k: v for k, v in schema.items() if k != "$id"})


def schema_errors(entry: Entry) -> list[str]:
    """Record-level errors against MECH v1.1, as 'path :: message' (empty list = schema-valid)."""
    return sorted("/".join(map(str, e.absolute_path)) + " :: " + e.message for e in _validator().iter_errors(entry))


def _read_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def read_cv_rows(path: Path = CV_REGISTRY_PATH) -> list[dict[str, str]]:
    return _read_rows(path)


def read_effect_rows(path: Path = EFFECT_REGISTRY_PATH) -> list[dict[str, str]]:
    return _read_rows(path)


# ----------------------------------------------------------------------------- semantic validator
def semantic_problems(entry: Entry, cv_rows: Iterable[Row], *, effect_rows: Iterable[Row] | None = None,
                      analyte_form_tokens: frozenset[str] | None = None) -> list[str]:
    """Problems the schema cannot express. cv_rows = registry/condition_variable_registry_v1.csv rows;
    effect_rows (optional) enables the target-class check; analyte_form_tokens = an APPROVED token set
    (None: no registry is approved, so any REGISTRY_TOKEN is a problem)."""
    cv = {r["condition_variable_id"]: r for r in cv_rows}
    probs: list[str] = []
    for coll, key in (("preconditions", "precondition_key"), ("condition_gates", "gate_key"),
                      ("inhibitors_mitigators", "inhibitor_key"), ("affected_targets", "target_key"),
                      ("markers", "marker_key"), ("open_questions", "question_ref")):
        dup = [k for k, n in Counter(x[key] for x in entry.get(coll, [])).items() if n > 1]
        if dup:
            probs.append(f"duplicate {key}: {sorted(dup)}")
    refs = {r["evidence_id"] for r in entry["evidence_refs"]}
    for coll in _ITEM_COLLECTIONS:
        for x in entry[coll]:
            if set(x["evidence_ids"]) - refs:
                probs.append(f"{coll}: evidence id not in evidence_refs")
    probs += _gate_problems(entry, cv)
    probs += _modifier_problems(entry)
    probs += _e7_problems(entry)
    probs += _v1_1_problems(entry, effect_rows, analyte_form_tokens)
    return probs


def _gate_problems(entry: Entry, cv: Mapping[str, Row]) -> list[str]:
    out: list[str] = []
    for g in entry["condition_gates"]:
        k = g["gate_key"]
        if g["cv_id"] not in cv:
            out.append(f"{k}: unknown CV {g['cv_id']}")
            continue
        row = cv[g["cv_id"]]
        if g["domain_kind"] == "NUMERIC_INTERVAL":
            iv = g["interval"]
            if iv["unit"] != row["canonical_unit"]:
                out.append(f"{k}: unit {iv['unit']} is not the CV canonical unit {row['canonical_unit']}")
            vals = [iv[s]["value"] for s in ("min", "max") if iv[s]["status"] == "STATED"]
            if vals != sorted(vals):
                out.append(f"{k}: min <= max violated")
            if row["dimension"].startswith("categorical"):
                out.append(f"{k}: numeric window on a categorical CV")
        elif g["categories"] and set(g["categories"]["allowed"]) & set(g["categories"]["excluded"]):
            out.append(f"{k}: allowed and excluded categories overlap")
    return out


def _modifier_problems(entry: Entry) -> list[str]:
    out: list[str] = []
    gates = {g["gate_key"]: g for g in entry["condition_gates"]}
    mods = {i["inhibitor_key"]: i for i in entry["inhibitors_mitigators"]}
    for i in entry["inhibitors_mitigators"]:
        v = i["evaluated_via"]
        want = "MODULATING" if i["role"] in ("CATALYST", "PROMOTER") else "INHIBITING"
        if v["mode"] == "GATE" and (v["gate_key"] not in gates or gates[v["gate_key"]]["gate_type"] != want):
            out.append(f"{i['inhibitor_key']}: GATE mode must name a {want} gate of this entry")
        t = i.get("acts_on_modifier_key")
        if t and (t not in mods or mods[t]["role"] not in ("CATALYST", "PROMOTER")):
            out.append(f"{i['inhibitor_key']}: acts_on_modifier_key must name a CATALYST or PROMOTER of this entry")
    return out


def _e7_problems(entry: Entry) -> list[str]:
    """E-7 (OPEN_QUESTION D21-20): a NECESSARY T / pH / aw gate on a CHEMICAL_REACTION needs PRIMARY evidence of
    absence (not merely slowness) and a rationale."""
    if entry["kind"] != "CHEMICAL_REACTION":
        return []
    prim = {r["evidence_id"] for r in entry["evidence_refs"] if r["doc_type"] == "PRIMARY"}
    return [f"{g['gate_key']}: E-7 NECESSARY gate on {g['cv_id']} needs PRIMARY evidence of absence and a rationale"
            for g in entry["condition_gates"]
            if g["gate_type"] == "NECESSARY" and g["cv_id"] in _E7_AXES
            and (not g["evidence_ids"] or not set(g["evidence_ids"]) <= prim or not (g["rationale_raw"] or "").strip())]


def _v1_1_problems(entry: Entry, effect_rows: Iterable[Row] | None, tokens: frozenset[str] | None) -> list[str]:
    out: list[str] = []
    admitted = None if effect_rows is None else {r["effect_type"]: _CSV_CLASS.get(r["target_class"], set())
                                                 for r in effect_rows}
    for t in entry["affected_targets"]:
        cls = t.get("target_class", "UNKNOWN")
        if admitted is not None and cls != "UNKNOWN" and cls not in admitted.get(t["effect_type"], set()):
            out.append(f"{t['target_key']}: target_class {cls} is not admitted for {t['effect_type']} (effect CSV)")
        af = t["analyte_form"]
        if af.get("token_status") == "REGISTRY_TOKEN":
            if tokens is None:
                out.append(f"{t['target_key']}: REGISTRY_TOKEN but no analyte-form registry is approved (D21-22)")
            elif af.get("token") not in tokens:
                out.append(f"{t['target_key']}: token {af.get('token')} is not in the approved registry")
    for m in entry["markers"]:
        if entry["mechanism_key"] in m.get("shared_with_mechanism_keys", []):
            out.append(f"{m['marker_key']}: a marker cannot be shared with its own entry")
    return out


# ----------------------------------------------------------------------------- registry-level links
_CONVERSE = {"THIS_PRECEDES_OTHER": "OTHER_PRECEDES_THIS", "OTHER_PRECEDES_THIS": "THIS_PRECEDES_OTHER",
             "UNKNOWN": "UNKNOWN"}


def asymmetric_links(entries: Sequence[Entry]) -> list[tuple[str, str, str]]:
    """competes_with must be declared on both sides; consecutive_with with the converse order."""
    by = {x["mechanism_key"]: x for x in entries}
    bad: list[tuple[str, str, str]] = []
    for x in entries:
        k = x["mechanism_key"]
        for c in x["competes_with"]:
            q = by.get(c["mechanism_key"])
            if q is None or k not in {y["mechanism_key"] for y in q["competes_with"]}:
                bad.append(("competes_with", k, c["mechanism_key"]))
        for c in x["consecutive_with"]:
            q = by.get(c["mechanism_key"])
            if q is None or not any(y["mechanism_key"] == k and y["order"] == _CONVERSE[c["order"]]
                                    for y in q["consecutive_with"]):
                bad.append(("consecutive_with", k, c["mechanism_key"]))
    return bad


def unresolved_links(entries: Sequence[Entry]) -> list[tuple[str, str, str]]:
    """Links (competition, consecutive order, marker sharing) to keys that are not in this set of entries."""
    keys = {x["mechanism_key"] for x in entries}
    out: set[tuple[str, str, str]] = set()
    for x in entries:
        k = x["mechanism_key"]
        for coll in ("competes_with", "consecutive_with"):
            out |= {(coll, k, c["mechanism_key"]) for c in x[coll] if c["mechanism_key"] not in keys}
        for m in x["markers"]:
            out |= {("markers", k, s) for s in m.get("shared_with_mechanism_keys", []) if s not in keys}
    return sorted(out)


# ----------------------------------------------------------------------------- Step 22 / 23 read API
def required_condition_axes(entry: Entry) -> tuple[AxisRequirement, ...]:
    """Every gate axis in declaration order. Rule M-1: a gate that a modifier is evaluated through is marked
    MODIFIER_GATE; its axis is required although a MODULATING gate never changes the G4 verdict."""
    modifier_gates = {i["evaluated_via"]["gate_key"] for i in entry["inhibitors_mitigators"]
                      if i["evaluated_via"]["mode"] == "GATE"}
    return tuple(AxisRequirement(g["cv_id"], g["location"], g["basis"], g["clock"], g["gate_key"], g["gate_type"],
                                 "MODIFIER_GATE" if g["gate_key"] in modifier_gates else "GATE")
                 for g in entry["condition_gates"])


def required_state_inputs(entry: Entry) -> tuple[StateInput, ...]:
    """States read by preconditions, history items and inline (STATE_PREDICATE) modifiers, in that order."""
    out = [StateInput(p["state_ref"]["state_key"], p["state_ref"]["svar_id"], p["state_ref"]["ref_status"],
                      "PRECONDITION", p["precondition_key"]) for p in entry["preconditions"]]
    out += [StateInput(h["state_ref"]["state_key"], h["state_ref"]["svar_id"], h["state_ref"]["ref_status"],
                       "HISTORY", h["role"]) for h in entry["history_dependence"]]
    for i in entry["inhibitors_mitigators"]:
        v = i["evaluated_via"]
        if v["mode"] == "STATE_PREDICATE" and v["state_ref"]:
            s = v["state_ref"]
            out.append(StateInput(s["state_key"], s["svar_id"], s["ref_status"], "MODIFIER", i["inhibitor_key"]))
    return tuple(out)


def candidate_effects(entry: Entry) -> tuple[CandidateEffect, ...]:
    """One CandidateEffect per affected target (signs only; status carried so CANDIDATE stays visible)."""
    return tuple(CandidateEffect(
        mechanism_key=entry["mechanism_key"], target_key=t["target_key"], target_svar_id=t["target"]["svar_id"],
        target_state_key=t["target"]["state_key"], target_class=t.get("target_class", "UNKNOWN"),
        target_role=t["target_role"], compartment=t["compartment"], effect_type=t["effect_type"],
        allowed_directions=tuple(t["allowed_directions"]), trajectory_shape=t["trajectory_shape"],
        analyte_form_token=t["analyte_form"].get("token"), status=t["status"]) for t in entry["affected_targets"])


def consumable_for_applicability(entry: Entry) -> tuple[bool, tuple[str, ...]]:
    """Whether Step 23 may evaluate this entry at all (plan Step 21 fail action: Steps 22-23 consume only
    ACCEPTED entries). False means the entry contributes UNKNOWN, never NOT_APPLICABLE and never APPLICABLE."""
    why: list[str] = []
    if entry["review_status"] != "ACCEPTED":
        why.append("NOT_ACCEPTED")
    if entry["verification"].get("status") != "HUMAN_VERIFIED":
        why.append("NOT_HUMAN_VERIFIED")
    if entry["gates_unknown"]:
        why.append("GATES_UNKNOWN")
    if any(q["status"] != "CLOSED_BY_HUMAN_DECISION" for q in entry.get("open_questions", [])):
        why.append("OPEN_QUESTIONS")
    if entry["kind"] == "UNRESOLVED_SINK":
        why.append("UNRESOLVED_SINK")
    return (not why, tuple(why))
