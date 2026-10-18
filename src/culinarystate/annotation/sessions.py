"""Scripted state-tracking sessions for DEL-3 (plan line 1250, AH6: ≥ 30 course minimum, 80–100 target).

A session is a cook-through: starting ingredients, user turns (utterance + the events it implies, in the gold event
vocabulary) and the expected end state (alive/dead entities, field values, structural edges). `check_session`
replays the events and reports every failed expectation plus replay determinism.

Provenance: AI_DRAFTED sessions are engine tests, not Gold. Only HUMAN_REVIEWED sessions (reviewer named) count
toward the DEL-3 contract.
"""
from __future__ import annotations

from jsonschema import Draft202012Validator

from culinarystate.scoring.state_metrics import edge_tuples, final_fields, replay_consistency
from culinarystate.state_graph.engine import Add, replay

from .gold import EVENT_TYPES, _base_from_text, compile_event

SCENARIOS = ["SUBSTITUTION", "OBSERVATION_OVERRIDE", "RESERVE_RECOMBINE", "SPLIT_PORTION", "MERGE", "DISCARD",
             "TRANSFER", "PARTIAL_USE", "MISTAKE", "MULTI_COMPONENT"]
SESSION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["session_id", "title", "scenario", "ingredients", "turns", "expected", "provenance"],
    "properties": {
        "session_id": {"type": "string", "pattern": r"^SES-[A-Z0-9]+$"}, "title": {"type": "string"},
        "scenario": {"enum": SCENARIOS}, "locale": {"type": ["string", "null"]}, "recipe_ref": {"type": "string"},
        "ingredients": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False, "required": ["entity", "concept", "quantity"],
            "properties": {"entity": {"type": "string"}, "concept": {"type": "string"}, "quantity": {"type": "string"},
                           "form": {"type": "string"}}}},
        "turns": {"type": "array", "minItems": 1, "items": {
            "type": "object", "additionalProperties": False, "required": ["turn", "user", "events"],
            "properties": {"turn": {"type": "integer", "minimum": 1}, "user": {"type": "string"},
                           "events": {"type": "array", "items": {"type": "object", "required": ["type"],
                                                                  "properties": {"type": {"enum": EVENT_TYPES}}}}}}},
        "expected": {"type": "object", "additionalProperties": False, "properties": {
            "alive": {"type": "array", "items": {"type": "string"}},
            "dead": {"type": "array", "items": {"type": "string"}},
            "fields": {"type": "object", "additionalProperties": {"type": "string"}},
            "edges": {"type": "array", "items": {"type": "array", "minItems": 3, "maxItems": 3}},
            "issues": {"type": "integer", "minimum": 0}}},            # engine issues the script expects
        "provenance": {"type": "object", "required": ["authored_by", "status", "reviewed_by"], "properties": {
            "authored_by": {"type": "string"}, "status": {"enum": ["AI_DRAFTED", "HUMAN_DRAFTED", "HUMAN_REVIEWED"]},
            "reviewed_by": {"type": ["string", "null"]}, "notes": {"type": "string"}}},
    },
}
_VALIDATOR = Draft202012Validator(SESSION_SCHEMA)


def validate_session(doc: dict) -> list[str]:
    errs = [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in _VALIDATOR.iter_errors(doc)]
    prov = doc.get("provenance") or {}
    if prov.get("status") == "HUMAN_REVIEWED" and not prov.get("reviewed_by"):
        errs.append("provenance: HUMAN_REVIEWED requires reviewed_by")
    return errs


def to_events(doc: dict) -> list:
    loc = doc.get("locale")
    events = [Add(i["entity"], None if i["concept"] == "UNKNOWN" else i["concept"],
                  _base_from_text(i["quantity"], loc), form=i.get("form"), step=0) for i in doc["ingredients"]]
    for t in doc["turns"]:
        events += [compile_event(ev, t["turn"], loc) for ev in t["events"]]
    return events


def check_session(doc: dict) -> dict:
    events = to_events(doc)
    g = replay(events)
    exp, failures, n = doc["expected"], [], 0
    alive = set(g.alive())
    for ent in exp.get("alive", []):
        n += 1
        if ent not in alive:
            failures.append(f"expected alive: {ent}")
    for ent in exp.get("dead", []):
        n += 1
        if ent in alive or ent not in g.versions:
            failures.append(f"expected dead (existed, then consumed): {ent}")
    ff = final_fields(g)
    for key, want in exp.get("fields", {}).items():
        n += 1
        ent, fld = key.rsplit(".", 1)
        got = ff.get((ent, fld))
        if got != want:
            failures.append(f"{key}: expected {want!r}, got {got!r}")
    edges = set(edge_tuples(g))
    for e in exp.get("edges", []):
        n += 1
        if tuple(e) not in edges:
            failures.append(f"missing edge {tuple(e)}")
    if "issues" in exp:
        n += 1
        if len(g.issues) != exp["issues"]:
            failures.append(f"expected {exp['issues']} engine issue(s), got {len(g.issues)}: {list(g.issues)}")
    rc = replay_consistency(events)
    return {"session_id": doc["session_id"], "pass": not failures and rc["deterministic"], "checks": n,
            "failures": failures, "issues": list(g.issues), "replay": rc}
