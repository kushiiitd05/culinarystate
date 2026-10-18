"""Gold recipe annotation format v1: JSON Schema, validator, and compiler to state-engine events.

One file per recipe per annotator: annotation/gold/<recipe_id>.<annotator>.json
Label set (handbook §3): FOOD QUANTITY UNIT SIZE FORM STATE ACTION TOOL MEDIUM TIME TEMPERATURE ENDPOINT
INTERMEDIATE OPTIONAL ALTERNATIVE, plus event types and coreference. UNKNOWN is a legal value everywhere a
fact is not stated.
"""
from __future__ import annotations

import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from culinarystate.quantity.grammar import parse_line
from culinarystate.quantity.normalize import normalize
from culinarystate.state_graph.engine import (Add, Discard, Merge, Observe, Recombine, Reserve, Split, Transfer,
                                              Transform)
from culinarystate.state_graph.symqty import Base

SPAN_LABELS = ["FOOD", "QUANTITY", "UNIT", "SIZE", "FORM", "STATE", "ACTION", "TOOL", "MEDIUM", "TIME", "TEMPERATURE",
               "ENDPOINT", "INTERMEDIATE", "OPTIONAL", "ALTERNATIVE"]
EVENT_TYPES = ["Transform", "Merge", "Split", "Reserve", "Discard", "Recombine", "Transfer", "Observe"]

_SPAN = {"type": "object", "required": ["start", "end", "label", "text"], "additionalProperties": False,
         "properties": {"start": {"type": "integer", "minimum": 0}, "end": {"type": "integer", "minimum": 1},
                        "label": {"enum": SPAN_LABELS}, "text": {"type": "string"}}}
_FRACTION = {"anyOf": [{"type": "string", "pattern": r"^\d+/\d+$"}, {"const": "UNKNOWN"}, {"type": "null"}]}

GOLD_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "CulinaryState gold recipe annotation v1",
    "type": "object", "additionalProperties": False,
    "required": ["schema_version", "recipe_id", "annotator", "status", "ingredient_lines", "steps"],
    "properties": {
        "schema_version": {"const": "gold-1.0"},
        "recipe_id": {"type": "string"}, "source_ref": {"type": "string"},
        "annotator": {"enum": ["Kush", "Parv", "ADJUDICATED"]},
        "status": {"enum": ["DRAFT", "DONE", "ADJUDICATED"]},
        "locale": {"type": "string"},
        "ingredient_lines": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["line_index", "text", "spans", "entity", "concept"],
            "properties": {
                "line_index": {"type": "integer", "minimum": 0}, "text": {"type": "string"},
                "spans": {"type": "array", "items": _SPAN},
                "entity": {"type": "string", "minLength": 1},
                "concept": {"type": "string", "minLength": 1},          # canonical name or "UNKNOWN"
                "optional": {"type": "boolean"},
                "alternatives": {"type": "array", "items": {"type": "string"}},
                "quantity_override": {"type": ["string", "null"]},       # when the line text misleads the parser
                "notes": {"type": "string"}}}},
        "steps": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["step_index", "text", "spans", "events"],
            "properties": {
                "step_index": {"type": "integer", "minimum": 0}, "text": {"type": "string"},
                "spans": {"type": "array", "items": _SPAN},
                "events": {"type": "array", "items": {
                    "type": "object", "additionalProperties": False, "required": ["type"],
                    "properties": {
                        "type": {"enum": EVENT_TYPES},
                        "target": {"type": "string"}, "inputs": {"type": "array", "items": {"type": "string"}},
                        "output": {"type": "string"},
                        "outputs": {"type": "array", "items": {"type": "object", "required": ["label", "fraction"],
                                                               "additionalProperties": False,
                                                               "properties": {"label": {"type": "string"},
                                                                              "fraction": _FRACTION}}},
                        "process": {"type": "string"}, "tool": {"type": "string"}, "medium": {"type": "string"},
                        "time": {"type": "string"}, "temperature": {"type": "string"}, "endpoint": {"type": "string"},
                        "portion": {"type": "string"}, "fraction": _FRACTION, "location": {"type": "string"},
                        "field": {"type": "string"}, "value": {"type": "string"},
                        "sets": {"type": "object", "additionalProperties": {"type": "string"}},
                        "evidence_span": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                        "implicit": {"type": "boolean"}}}},
                "coref": {"type": "array", "items": {
                    "type": "object", "additionalProperties": False, "required": ["mention", "start", "end", "entity"],
                    "properties": {"mention": {"type": "string"}, "start": {"type": "integer"},
                                   "end": {"type": "integer"}, "entity": {"type": "string"}}}}}}},
        "unknowns": {"type": "array", "items": {"type": "object", "required": ["what", "why"],
                                                "properties": {"what": {"type": "string"},
                                                               "why": {"type": "string"}}}},
        "notes": {"type": "string"},
    },
}
_VALIDATOR = Draft202012Validator(GOLD_SCHEMA)


def validate_gold(doc: dict) -> list[str]:
    errs = [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in _VALIDATOR.iter_errors(doc)]
    if errs:
        return errs
    for li in doc["ingredient_lines"]:
        errs += _span_errors(li["text"], li["spans"], f"line {li['line_index']}")
    if "TODO" in json.dumps(doc):
        errs.append("unfinished: replace every TODO (entity/concept) before validating as DONE")
    entities = {li["entity"] for li in doc["ingredient_lines"]}
    if len(entities) != len(doc["ingredient_lines"]):
        errs.append("ingredient entities must be unique labels")
    for st in doc["steps"]:
        errs += _span_errors(st["text"], st["spans"], f"step {st['step_index']}")
        for c in st.get("coref", []):
            if st["text"][c["start"]:c["end"]] != c["mention"]:
                errs.append(f"step {st['step_index']}: coref span text mismatch '{c['mention']}'")
        for ev in st["events"]:
            errs += _event_errors(ev, st["step_index"])
    return errs


def _span_errors(text: str, spans: list, where: str) -> list[str]:
    out = []
    for s in spans:
        if s["end"] <= s["start"] or s["end"] > len(text):
            out.append(f"{where}: bad offsets {s['start']}-{s['end']}")
        elif text[s["start"]:s["end"]] != s["text"]:
            out.append(f"{where}: span text '{s['text']}' != '{text[s['start']:s['end']]}'")
    return out


REQUIRED = {"Transform": ("target", "process"), "Merge": ("inputs", "output"), "Split": ("target", "outputs"),
            "Reserve": ("target", "output"), "Discard": ("target",), "Recombine": ("target", "output"),
            "Transfer": ("target", "location"), "Observe": ("target", "field", "value")}


def _event_errors(ev: dict, step: int) -> list[str]:
    missing = [k for k in REQUIRED[ev["type"]] if k not in ev]
    return [f"step {step}: {ev['type']} missing {missing}"] if missing else []


def _frac(x) -> Fraction | None:
    return Fraction(x) if isinstance(x, str) and "/" in x else None


def _base_from_text(text: str, locale: str | None) -> Base:
    p = parse_line(text)
    z = normalize(p, locale=locale)
    return Base.from_channels(z.mass_g, z.volume_ml, z.count, text.strip())


def to_events(doc: dict) -> list:
    """Compile a validated gold doc into engine events (deterministic)."""
    loc = doc.get("locale")
    events: list = []
    for li in doc["ingredient_lines"]:
        qtext = li.get("quantity_override") or li["text"]
        form = next((s["text"] for s in li["spans"] if s["label"] == "FORM"), None)
        concept = None if li["concept"] == "UNKNOWN" else li["concept"]
        events.append(Add(li["entity"], concept, _base_from_text(qtext, loc), form=form, step=0))
    for st in doc["steps"]:
        k = st["step_index"]
        for ev in st["events"]:
            t = ev["type"]
            cond = {key: ev[key] for key in ("tool", "medium", "time", "temperature", "endpoint") if key in ev}
            if t == "Transform":
                events.append(Transform(ev["target"], ev["process"], cond, tuple(sorted(ev.get("sets", {}).items())),
                                        step=k))
            elif t == "Merge":
                events.append(Merge(tuple(ev["inputs"]), ev["output"], ev.get("process", "combine"), step=k))
            elif t == "Split":
                events.append(Split(ev["target"], tuple((o["label"], _frac(o["fraction"])) for o in ev["outputs"]),
                                    step=k))
            elif t == "Reserve":
                portion = _base_from_text(ev["portion"], loc) if ev.get("portion") else None
                events.append(Reserve(ev["target"], ev["output"], portion=portion,
                                      fraction=_frac(ev.get("fraction")), step=k))
            elif t == "Discard":
                portion = _base_from_text(ev["portion"], loc) if ev.get("portion") else None
                events.append(Discard(ev["target"], portion=portion, fraction=_frac(ev.get("fraction")),
                                      what=ev.get("value"), step=k))
            elif t == "Recombine":
                events.append(Recombine(ev["target"], ev["output"], step=k))
            elif t == "Transfer":
                events.append(Transfer(ev["target"], ev["location"], step=k))
            elif t == "Observe":
                events.append(Observe(ev["target"], ev["field"], ev["value"], step=k))
    return events
