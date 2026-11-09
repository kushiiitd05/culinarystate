"""Endpoint-cue extractor for Layer 1 (S178 PHYS2, T4-C03-R1; SSOT 199.8 "Endpoint leakage"). DRAFT, AI_DRAFTED.

"until golden", "until tender", "until reduced by half" are OBSERVED endpoint information, not clean causal inputs: if a model
predicts browning, "until golden" must not be one of its inputs. This module stores such phrases as a separate, QUALITATIVE
block of the Layer 1 event record (the ``endpoint`` key, never inside ``inputs``): a stopping criterion with its span and
provenance, plus every cue found. Nothing here becomes a simulator input, a ConditionBinding or a feature.

Rules (deterministic, no text kept: spans and class codes only):
- Trigger: "until", "till", "til" in the sentence of a heat event. The clause runs from the trigger to the first comma,
  semicolon, parenthesis, " then ", " before ", " about ", " for " or the next heat event, at most 90 characters. Every lexicon
  state word in the clause is a cue (``registry/endpoint_cue_lexicon_v1.csv``, classes keyed to the ledger ENDPOINT PROCs where
  one exists); a clause with a trigger but no lexicon word is ``UNTIL_CLAUSE_UNCLASSIFIED`` (counted, never dropped).
- Phrase cues without "until": "reduce(d) by half / a third / to ...": class EVAPORATE_REDUCE.
- Target food temperature: a temperature that follows a strong cue (thermometer, probe, internal / core temperature, reads,
  registers) within 45 characters, with no comma, semicolon, "then", "at", "in" or medium word between and no sugar-syrup word
  (candy, sugar, syrup, jam, caramel ...) before it, is a TARGET of the food, not a medium temperature: class
  TARGET_FOOD_TEMPERATURE, ``target_c`` kept; the later temperatures of the same list ("140 F for medium rare, 155 F for medium") are targets
  too. A syrup temperature ("boil to 240 F", candy stages) is the temperature of the
  LIQUID and stays a stated temperature (S177: the cap never goes below a stated liquid temperature). ``condition_binding`` removes such a
  temperature from the candidates of the bath temperature (0.1.0 bound them to the heat event).
- Owner: the nearest heat event whose verb precedes the cue in the sentence, else the first heat event after it.
- ``stopping_criterion`` of an event = its first cue by position (status QUALITATIVE, basis TEXT_CUE).

Leakage guard: ``physical_feature_row`` flattens the fields a downstream model may use (the Layer 1 ``inputs`` axes and the
Layer 2 scenario inputs); ``assert_no_endpoint_fields`` fails if any column or any axis is an endpoint field. The tests pin that
two texts that differ only in an endpoint phrase give identical feature rows.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[3]
VERSION = "endpoint-cues-0.1.0-draft"
LEXICON = "registry/endpoint_cue_lexicon_v1.csv"
BLOCK_KEY = "endpoint"
ROLE = "STOPPING_CRITERION_NOT_AN_INPUT"
UNCLASSIFIED = "UNTIL_CLAUSE_UNCLASSIFIED"
TARGET_CLASS = "TARGET_FOOD_TEMPERATURE"
# names that must never be a feature column or a Layer 1 input axis
ENDPOINT_FIELDS = frozenset({BLOCK_KEY, "stopping_criterion", "endpoint_cues", "endpoint_cue", "target_food_temperature_c",
                             "target_c", "temperature_note"})
CUE_CLASSES_EXTRA = (UNCLASSIFIED, TARGET_CLASS)

_TRIGGER = re.compile(r"(?<![\w'])(?:until|till|til|'til|’til)\b", re.I)
_CUT = re.compile(r"[,;()]|\bthen\b|\bbefore\b|\babout\b|\bfor\b|\bapproximately\b|\bapprox\b", re.I)
_PHRASE_REDUCE = re.compile(r"\breduc(?:e|ed|es|ing)\s+(?:it\s+|them\s+|the\s+\w+\s+)?(?:by|to)\s+(?:about\s+|roughly\s+)?"
                            r"(?:half|a\s+third|one[- ]third|two[- ]thirds|a\s+quarter|one[- ]quarter|\d+\s*%)", re.I)
_TEMP = re.compile(r"(?<![\d.])(\d{2,3})(?:\s*[-–]\s*(\d{2,3}))?\s*(?:°|º|˚|degrees?|deg\.?)?\s*([CF])(?![A-Za-z])", re.I)
# strong food-target cues: the temperature that follows is the food's, not the medium's
_TARGET_CUE = re.compile(r"(?:\bthermometer|\bprobe|\binternal\s+temp(?:erature)?|\bcore\s+temp(?:erature)?|"
                         r"\bregist(?:ers?|ering)|\breads?|\breading)\b(?P<gap>[^,;.]{0,45})$", re.I)
_MEDIUM_WORDS = re.compile(r"\b(?:oven|water|oil|pan|pot|skillet|liquid|syrup|bath|grill|stock|milk|broth|fat|griddle|"
                           r"steamer|cooker|then|at|in)\b", re.I)
# a sugar syrup's temperature is the temperature of the LIQUID (candy stages), never a target of a solid food
_SYRUP = re.compile(r"\b(?:candy|sugar|syrup|jam|caramel|fondant|toffee|brittle)\b", re.I)


@dataclass(frozen=True)
class Entry:
    code: str
    priority: int
    regex: re.Pattern
    proc_id: str | None


_CACHE: dict[str, tuple[Entry, ...]] = {}


def load_lexicon(root: Path = ROOT) -> tuple[Entry, ...]:
    key = str(Path(root).resolve())
    if key not in _CACHE:
        with open(Path(root) / LEXICON, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        _CACHE[key] = tuple(sorted((Entry(r["class_code"], int(r["priority"]), re.compile(rf"\b(?:{r['pattern']})\b", re.I),
                                          r["ledger_proc_id"] or None) for r in rows), key=lambda e: e.priority))
    return _CACHE[key]


def classes(root: Path = ROOT) -> tuple[str, ...]:
    return tuple(e.code for e in load_lexicon(root)) + CUE_CLASSES_EXTRA


def span_id(span: Sequence[int]) -> str:
    return f"C:{int(span[0])}-{int(span[1])}"


def _clause_states(raw: str, lo: int, hi: int, lex: Sequence[Entry]) -> list[tuple[int, int, Entry]]:
    cand = []
    for e in lex:
        for m in e.regex.finditer(raw, lo, hi):
            cand.append((m.start(), -(m.end() - m.start()), e.priority, m.end(), e))
    cand.sort()
    out, last = [], lo
    for s, _, _, end, e in cand:
        if s >= last:
            out.append((s, end, e))
            last = end
    return out


_FILLER = re.compile(r"\bat (?:least|most|about|around)\b", re.I)  # "reads at least 170 F": the "at" is not a medium phrase
_MEDIUM_THERMOMETER = re.compile(r"\s*(?:\)|\])?\s*(?:on|by|with|using)\s+(?:a|an|the)\s+(?:deep[- ]fat|deep[- ]fry\w*|candy|sugar|jelly|jam|frying|oil)\s+"
                                 r"thermometer", re.I)  # the thermometer reads the liquid medium, not a food
_CHAIN_BREAK = re.compile(r"\b(?:oven|water|oil|pan|pot|skillet|liquid|syrup|bath|grill|stock|milk|broth|fat|griddle|steamer|cooker|then|until|"
                          r"bake|roast|fry|boil|simmer|cook)\b", re.I)


def target_temperature_spans(raw: str, a: int, b: int, temps: Iterable[tuple[Any, tuple[int, int]]]) -> set[tuple[int, int]]:
    """Spans (of the given ``(value, span)`` temperatures) that are TARGETS of the food: after a strong cue, or in the same list as a
    target ("140 F for medium rare, 155 F for medium, and 165 F for well": at most 45 characters after the previous target, no medium
    or verb word between)."""
    out: set[tuple[int, int]] = set()
    prev_end = None
    for _, (s, e) in sorted(temps, key=lambda t: t[1][0]):
        before = raw[max(a, s - 90):s]
        m = _TARGET_CUE.search(before)
        gap = _FILLER.sub(" ", m.group("gap")) if m else ""
        direct = bool(m and not _MEDIUM_WORDS.search(gap) and not _SYRUP.search(before) and not _MEDIUM_THERMOMETER.match(raw[e:e + 40]))
        chained = False
        if not direct and prev_end is not None:
            gap = raw[prev_end:s]
            chained = len(gap) <= 45 and not _CHAIN_BREAK.search(gap) and not _SYRUP.search(before)
        if direct or chained:
            out.add((s, e))
            prev_end = e
        else:
            prev_end = None
    return out


def extract_sentence(raw: str, a: int, b: int, heat_events: Sequence[tuple[str, int]], *, lex: Sequence[Entry] | None = None,
                     temps: Iterable[tuple[Any, tuple[int, int]]] = (), root: Path = ROOT) -> dict[str, list[dict]]:
    """Cues of one sentence ``[a, b)`` per heat event. ``heat_events``: [(event_id, verb char_start)] in text order. Cues are
    {class, trigger, span, proc_id, target_c?}; text is never copied."""
    lex = lex or load_lexicon(root)
    out: dict[str, list[dict]] = {eid: [] for eid, _ in heat_events}
    if not heat_events:
        return out

    def owner(pos: int) -> int:
        idx = [i for i, (_, st) in enumerate(heat_events) if st <= pos]
        return idx[-1] if idx else 0

    def next_heat(pos: int) -> int:
        later = [st for _, st in heat_events if st > pos]
        return min(later) if later else b

    for m in _TRIGGER.finditer(raw, a, b):
        oi = owner(m.start())
        lo = m.end()
        hi = min(b, lo + 90, next_heat(m.start()) if next_heat(m.start()) > lo else b)
        cut = _CUT.search(raw, lo, hi)
        if cut:
            hi = cut.start()
        states = _clause_states(raw, lo, hi, lex)
        eid = heat_events[oi][0]
        if states:
            for s, e, ent in states:
                out[eid].append({"class": ent.code, "trigger": "UNTIL", "span": [s, e], "proc_id": ent.proc_id})
        else:
            out[eid].append({"class": UNCLASSIFIED, "trigger": "UNTIL", "span": [m.start(), max(m.end(), hi)], "proc_id": None})
    for m in _PHRASE_REDUCE.finditer(raw, a, b):
        eid = heat_events[owner(m.start())][0]
        if not any(c["span"][0] <= m.start() < c["span"][1] for c in out[eid] if c["class"] == "EVAPORATE_REDUCE"):
            out[eid].append({"class": "EVAPORATE_REDUCE", "trigger": "PHRASE", "span": [m.start(), m.end()],
                             "proc_id": "PROC-000145"})
    targets = sorted(target_temperature_spans(raw, a, b, temps))
    for cues in out.values():  # an until-clause that only holds a food-target temperature is explained by that target
        cues[:] = [c for c in cues if not (c["class"] == UNCLASSIFIED and any(c["span"][0] <= s and e <= c["span"][1] for s, e in targets))]
    for (s, e) in targets:
        mt = _TEMP.fullmatch(raw[s:e])
        tgt = None
        if mt:
            lo_ = Fraction(mt.group(1))
            lo_ = (lo_ - 32) * Fraction(5, 9) if mt.group(3).upper() == "F" else lo_
            tgt = str(lo_)
        out[heat_events[owner(s)][0]].append({"class": TARGET_CLASS, "trigger": "TARGET", "span": [s, e], "proc_id": None,
                                              "target_c": tgt})
    for cues in out.values():
        cues.sort(key=lambda c: (c["span"][0], c["class"]))
    return out


def block(cues: Sequence[Mapping]) -> dict:
    """The ``endpoint`` block of one Layer 1 event record (QUALITATIVE, with spans; never part of ``inputs``)."""
    cues = [dict(c) for c in cues]
    if not cues:
        crit = {"value": None, "status": "UNKNOWN", "basis": None, "span": None, "reason": "NO_ENDPOINT_CUE"}
    else:
        c = cues[0]
        crit = {"value": c["class"], "status": "QUALITATIVE", "basis": "TEXT_CUE", "span": list(c["span"]),
                "span_id": span_id(c["span"]), "row": f"endpoint_cue_lexicon_v1:{c['class']}", "role": ROLE}
    return {"stopping_criterion": crit, "cues": cues, "n_cues": len(cues), "version": VERSION}


# ------------------------------------------------------------------------------------------------ leakage guard
def physical_feature_row(l1: Mapping, l2: Mapping | None = None) -> dict[str, Any]:
    """Flat feature columns a downstream model may use: every Layer 1 ``inputs`` axis (value, status, basis) and, when given,
    the Layer 2 per-bracket scenario inputs. Only these keys are read; the ``endpoint`` block, ``cues`` and notes never are."""
    row: dict[str, Any] = {"process_id": l1.get("process_id"), "family": l1.get("family")}
    for axis, x in sorted((l1.get("inputs") or {}).items()):
        row[f"l1.{axis}.value"] = x.get("value")
        row[f"l1.{axis}.status"] = x.get("status")
        row[f"l1.{axis}.basis"] = x.get("basis")
    if l2:
        for bracket, sc in sorted((l2.get("scenarios") or {}).items()):
            for k in ("bath_c", "duration_min", "initial_c", "h", "half_thickness_m"):
                if k in sc:
                    row[f"l2.{bracket}.{k}"] = sc[k]
    return row


def assert_no_endpoint_fields(columns: Iterable[str], axes: Iterable[str] = ()) -> None:
    """Raise AssertionError when a feature column or a Layer 1 axis is an endpoint field."""
    bad = [c for c in columns if any(seg in ENDPOINT_FIELDS for seg in str(c).split("."))]
    bad += [a for a in axes if a in ENDPOINT_FIELDS]
    if bad:
        raise AssertionError(f"endpoint field(s) in the feature matrix: {sorted(set(map(str, bad)))}")
