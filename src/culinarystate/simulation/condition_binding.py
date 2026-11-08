"""Layer 1 TEXT_STATED condition binding (S172, D-077): recipe text -> per-event simulator inputs, traced. DRAFT.

Reads the frozen Rung A graph and the raw text (Rung A is not modified). For each heat event it records each sim_aa_1
input with a value, status (MEASURED / RANGE / UNKNOWN), basis and span, and emits contract ``ConditionBinding``s
(source class STRUCTURAL_RECIPE) for the bound ones. Bases, all deterministic:
- TEXT_STATED: a duration (Rung A) or a temperature written in the event's sentence (°C, or °F converted exactly).
- CARRIED_SETPOINT: an oven temperature stated at "preheat", carried to later dry-heat events until restated.
- PHYSICAL_DEFINITION: the verb fixes the bath temperature (boil, steam: 100 °C at 1 atm), from
  registry/process_medium_map_v1.csv; PROCESS_DEFINITION: the medium the verb implies (same registry).
- CUE: lid and start-mode words in the sentence; CUT_HISTORY: the nearest upstream cut verb of a consumed lot;
  FOOD_GROUP: the consumed ingredients' ING food group when they all agree.
Nothing is defaulted: gas marks are kept as a code (GAS_n) with no number; water ratio stays UNKNOWN in v0.
"""
from __future__ import annotations

import csv
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.mechanism.router_demo import _attr
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.simulation import recipe_adapter as RA
from culinarystate.state_graph.source_class import SourceClass

ROOT = Path(__file__).resolve().parents[3]
VERSION = "condition-binding-L1-0.1.0-draft"
HEAT = ("WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL")
INPUTS = ("duration", "temperature_profile", "medium", "lid_state", "start_mode", "piece_size_class", "water_ratio",
          "matrix_class")
_T = re.compile(r"(?<![\d.])(\d{2,3})(?:\s*[-–]\s*(\d{2,3}))?\s*(?:°|º|˚|degrees?|deg\.?)?\s*([CF])(?![A-Za-z])",
                re.I)
_GAS = re.compile(r"\bgas(?:\s*mark)?\s*(\d{1,2})\b", re.I)
_SENT = re.compile(r"[.!?;\n]+")
_UNCOV = re.compile(r"\buncover(?:ed)?\b|\bwithout (?:a |the )?lid\b|\blid off\b", re.I)
_PART = re.compile(r"\bpartially cover|\bhalf[- ]cover|\blid ajar\b", re.I)
_COV = re.compile(r"\bcover(?:ed)?\b|\blid on\b|\bwith (?:a|the) lid\b", re.I)
_HOT = re.compile(r"\b(?:into|to|in)\s+(?:a\s+)?(?:large\s+)?(?:(?:pan|pot|saucepan)\s+of\s+)?(?:salted\s+)?boiling\b",
                  re.I)
_COLD = re.compile(r"\bcold water\b", re.I)
CUT_CLASS = {"PROC-000045": "DICED", "PROC-000044": "SLICED", "PROC-000043": "CHOPPED", "PROC-000048": "GRATED",
             "PROC-000050": "MINCED", "PROC-000051": "SHREDDED", "PROC-000047": "HALVED", "PROC-000049": "CRUSHED"}
SETPOINT_FAMILIES = ("DRY_HEAT",)
T_MIN_C, T_MAX_C = Fraction(30), Fraction(320)


def _latest(path: Path) -> dict:
    out: dict = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                if r["id"] not in out or r.get("version", 0) >= out[r["id"]].get("version", 0):
                    out[r["id"]] = r
    return out


def _c(v: Fraction, unit: str) -> Fraction:
    return (v - 32) * Fraction(5, 9) if unit.upper() == "F" else v


def _unknown() -> dict:
    return {"value": None, "status": "UNKNOWN", "basis": None, "span": None}


def _known(value, basis: str, span=None) -> dict:
    status = "RANGE" if isinstance(value, tuple) and value[0] != value[1] else "MEASURED"
    return {"value": value[0] if isinstance(value, tuple) and value[0] == value[1] else value, "status": status,
            "basis": basis, "span": span}


class Binder:
    def __init__(self, *, rung: RungA, schema: Any, medium_map: Mapping[str, Mapping], family: Mapping[str, str],
                 food_group: Mapping[str, str]) -> None:
        self.rung, self.schema, self.medium_map, self.family, self.food_group = rung, schema, medium_map, family, \
            food_group

    @classmethod
    def load(cls, root: Path = ROOT) -> "Binder":
        with open(root / "registry/process_medium_map_v1.csv", newline="", encoding="utf-8") as fh:
            mm = {r["process_id"]: r for r in csv.DictReader(fh)}
        procs = _latest(root / "ledgers/data/PROC.jsonl")
        ings = _latest(root / "ledgers/data/ING.jsonl")
        groups = {i: (r.get("category") or r.get("food_group")) for i, r in ings.items() if r.get("status") == "ACTIVE"}
        return cls(rung=RungA(), schema=D.load_schema(root), medium_map=mm,
                   family={p: r.get("family") for p, r in procs.items()},
                   food_group={i: g for i, g in groups.items() if g})

    # ---------------------------------------------------------------- helpers
    @staticmethod
    def _sentence(raw: str, pos: int) -> tuple[int, int]:
        starts = [0] + [m.end() for m in _SENT.finditer(raw)]
        start = max(s for s in starts if s <= pos)
        nxt = _SENT.search(raw, pos)
        return start, (nxt.start() if nxt else len(raw))

    @staticmethod
    def _temperatures(raw: str, a: int, b: int) -> list[tuple[Any, tuple[int, int]]]:
        out = []
        for m in _T.finditer(raw, a, b):
            lo = _c(Fraction(m.group(1)), m.group(3))
            hi = _c(Fraction(m.group(2)), m.group(3)) if m.group(2) else lo
            if T_MIN_C <= lo <= hi <= T_MAX_C:
                out.append(((lo, hi), (m.start(), m.end())))
        return out

    def _cut_class(self, g, lot_ids) -> str | None:
        producers = {p: ev for ev in g.events for p in ev.produces}
        ents = {e.entity_id: e for e in g.entities}
        stack, seen = list(lot_ids), set()
        while stack:
            lid = stack.pop()
            if lid in seen:
                continue
            seen.add(lid)
            ev = producers.get(lid)
            if ev is not None and _attr(ev.attributes, "proc_id") in CUT_CLASS:
                return CUT_CLASS[_attr(ev.attributes, "proc_id")]
            if lid in ents:
                stack.extend(ents[lid].parent_entity_ids)
        return None

    def _groups(self, g, lot_ids) -> set[str]:
        from culinarystate.mechanism.router_demo import _lot_ingredients
        return {self.food_group[i] for i in _lot_ingredients(g, lot_ids) if i in self.food_group}

    # ---------------------------------------------------------------- main
    def bind_text(self, raw: str, locale: str | None = None) -> dict:
        g = self.rung.run(SourceText.from_raw("BIND", raw), self.rung.config(locale=locale), schema=self.schema).graph
        events, bindings = [], []
        setpoint, gas = None, None
        for ev in sorted(g.events, key=lambda e: e.span.char_start):
            pid = _attr(ev.attributes, "proc_id")
            fam = self.family.get(pid)
            a, b = self._sentence(raw, ev.span.char_start)
            temps = self._temperatures(raw, a, b)
            gm = _GAS.search(raw, a, b)
            if fam == "HEAT_CONTROL":
                setpoint = (temps[0], ev.event_id) if temps else setpoint
                gas = f"GAS_{gm.group(1)}" if gm else (None if temps else gas)
            rec = {"event_id": ev.event_id, "action": ev.span.surface, "process_id": pid, "family": fam,
                   "heat": fam in HEAT, "inputs": {}, "oven_setpoint_code": None}
            if fam in HEAT:
                rec["inputs"], rec["oven_setpoint_code"] = self._inputs(raw, g, ev, pid, fam, (a, b), temps, setpoint,
                                                                         gas, gm)
                bindings += self._bindings(ev.event_id, rec["inputs"])
            events.append(rec)
        return {"version": VERSION, "events": events, "bindings": tuple(bindings)}

    def _inputs(self, raw, g, ev, pid, fam, sent, temps, setpoint, gas, gm):
        a, b = sent
        text = raw[a:b]
        inp = {k: _unknown() for k in INPUTS}
        dur = _attr(ev.attributes, "duration_min")
        if dur is not None:
            inp["duration"] = _known(tuple(Fraction(x) for x in dur) if isinstance(dur, tuple) else
                                     (Fraction(dur), Fraction(dur)), "TEXT_STATED")
        mm = self.medium_map.get(pid) or {}
        code = None
        if temps:
            near = min(temps, key=lambda t: abs(t[1][0] - ev.span.char_start))
            inp["temperature_profile"] = _known(near[0], "TEXT_STATED", near[1])
        elif fam in SETPOINT_FAMILIES and setpoint is not None:
            inp["temperature_profile"] = _known(setpoint[0][0], "CARRIED_SETPOINT", setpoint[0][1])
        elif mm.get("physical_definition_degC"):
            v = Fraction(mm["physical_definition_degC"])
            inp["temperature_profile"] = _known((v, v), "PHYSICAL_DEFINITION")
        elif fam in SETPOINT_FAMILIES and (gm or gas):
            code = f"GAS_{gm.group(1)}" if gm else gas
        if mm.get("medium_code"):
            inp["medium"] = _known(mm["medium_code"], "PROCESS_DEFINITION")
        lid = "UNCOVERED" if _UNCOV.search(text) else "PARTIAL" if _PART.search(text) else \
            "COVERED" if _COV.search(text) else None
        if lid:
            inp["lid_state"] = _known(lid, "CUE")
        start = "HOT_START" if _HOT.search(text) else "COLD_START" if _COLD.search(text) else None
        if start:
            inp["start_mode"] = _known(start, "CUE")
        cut = self._cut_class(g, ev.consumes)
        if cut:
            inp["piece_size_class"] = _known(cut, "CUT_HISTORY")
        groups = self._groups(g, ev.consumes)
        if len(groups) == 1:
            inp["matrix_class"] = _known(next(iter(groups)), "FOOD_GROUP")
        return inp, code

    @staticmethod
    def _bindings(event_id: str, inp: Mapping[str, dict]) -> list[RA.ConditionBinding]:
        out = []
        sc = SourceClass.STRUCTURAL_RECIPE
        for name in ("duration", "medium", "lid_state", "start_mode", "piece_size_class", "matrix_class"):
            x = inp[name]
            if x["status"] == "UNKNOWN":
                continue
            unit = RA.INPUT_SPECS[name].unit
            out.append(RA.ConditionBinding(event_id, name, x["value"], "EVT", event_id, sc, unit))
        d, t = inp["duration"], inp["temperature_profile"]
        if t["status"] != "UNKNOWN" and d["status"] == "MEASURED" and d["value"] > 0:
            lo, hi = t["value"] if isinstance(t["value"], tuple) else (t["value"], t["value"])
            seg = RA.ProfileSegment(Fraction(0), d["value"], lo, hi)
            out.append(RA.ConditionBinding(event_id, "temperature_profile", (seg,), "EVT", event_id, sc, "min|degC"))
        return out
