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

S178 FIX-PHYS (version 0.2.0, SCI-A M1 / m1; SSOT v16 DRAFT 199.8, PROPOSED):
- The strong cue nearest the temperature wins (the LAST cue before it, not the first): "a thermometer inserted in the centre registers
  160 F" is read from "registers"; after "inserted", "in" / "at" are not medium words; an internal / core temperature cue wins over a
  medium-thermometer suffix.
- The sugar-syrup exemption is local: a syrup / candy / jam word in the temperature's own clause, in the event's own phrase (owner
  verb to the temperature) or in the owner verb's object. "Rub the pork with brown sugar and bake until a thermometer reads 145 F" is
  a target again.
- Until-clause rule: a temperature inside an "until / till" clause is a TARGET of the food unless it is exempt: the syrup words; a
  liquid or medium as the subject of the clause or the object of the owner verb ("heat the oil until it reaches 375 F", "until the
  water reaches 180 F": the medium's own temperature); a setting phrase ("until golden at 350 F"); a medium thermometer.
- ``until_clauses`` (spans only, with the role of every temperature inside) is stored in the endpoint block, so the corpus check
  "no bound temperature inside an until-clause unless exempt" can be run on the records.
- One temperature regex (``TEMP_RE``) for the binder and this module: ranges "350 to 375 F" and "350°-375°F" are ranges, spelled-out
  units (degrees Fahrenheit / Celsius / Centigrade) are read, a lower-case "c." that continues the sentence ("250 c. of water") is cups.

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
VERSION = "endpoint-cues-0.2.0-draft"
VERSION_V01 = "endpoint-cues-0.1.0-draft"  # SUPERSEDED: first strong cue, sentence-wide syrup block, no until-clause targets
LEXICON = "registry/endpoint_cue_lexicon_v1.csv"
BLOCK_KEY = "endpoint"
ROLE = "STOPPING_CRITERION_NOT_AN_INPUT"
UNCLASSIFIED = "UNTIL_CLAUSE_UNCLASSIFIED"
TARGET_CLASS = "TARGET_FOOD_TEMPERATURE"
# names that must never be a feature column or a Layer 1 input axis
ENDPOINT_FIELDS = frozenset({BLOCK_KEY, "stopping_criterion", "endpoint_cues", "endpoint_cue", "target_food_temperature_c",
                             "target_c", "temperature_note", "until_clauses",
                             "target_food_temperature"})  # S178 FIX-PHYS m4: the non-heat COOLING target is an endpoint
CUE_CLASSES_EXTRA = (UNCLASSIFIED, TARGET_CLASS)

_TRIGGER = re.compile(r"(?<![\w'])(?:until|till|til|'til|’til)\b", re.I)
_CUT = re.compile(r"[,;()]|\bthen\b|\bbefore\b|\babout\b|\bfor\b|\bapproximately\b|\bapprox\b", re.I)
_PHRASE_REDUCE = re.compile(r"\breduc(?:e|ed|es|ing)\s+(?:it\s+|them\s+|the\s+\w+\s+)?(?:by|to)\s+(?:about\s+|roughly\s+)?"
                            r"(?:half|a\s+third|one[- ]third|two[- ]thirds|a\s+quarter|one[- ]quarter|\d+\s*%)", re.I)
_DEG = r"(?:°|º|˚|degrees?|deg\.?)"
# S178 FIX-PHYS m1: "350 to 375 F", "350°-375°F", "400 degrees Fahrenheit"; groups 1 / 2 = low / high number, ``u`` = unit
TEMP_RE = re.compile(rf"(?<![\d.])(\d{{2,3}})(?:\s*(?P<d1>{_DEG}))?(?:\s*(?:[-–]|to)\s*(\d{{2,3}}))?(?:\s*(?P<d2>{_DEG}))?\s*"
                     r"(?P<u>Fahrenheit|Celsius|Centigrade|[CF])(?![A-Za-z])", re.I)
_TEMP = TEMP_RE
_CUPS_AFTER = re.compile(r"\.(?!\s*(?:$|[A-Z\d]))|\s+(?:of|water|milk|stock|broth|cream|flour|sugar|oil|butter|rice)\b")
_FROM_BEFORE = re.compile(r"\bfrom\s*$", re.I)


def parse_temperatures(raw: str, a: int, b: int) -> list[tuple[tuple[Fraction, Fraction], tuple[int, int]]]:
    """``[((low_c, high_c), (start, end))]`` of the temperatures in ``raw[a:b]`` (exact Fractions in deg C, F converted exactly).
    A lower-case "c" with no degree word that continues the sentence ("250 c. of water") is cups, not Celsius; "from 450 to 350 F"
    is the new setting (350 F), not a range; a reversed range is the second number."""
    out = []
    for m in TEMP_RE.finditer(raw, a, b):
        u = m.group("u")
        if u == "c" and not (m.group("d1") or m.group("d2")) and _CUPS_AFTER.match(raw, m.end()):
            continue
        f = u[0].upper() == "F"
        lo = Fraction(m.group(1))
        hi = Fraction(m.group(3)) if m.group(3) else lo
        if m.group(3) and (lo > hi or _FROM_BEFORE.search(raw, max(a, m.start() - 8), m.start())):
            lo = hi  # a change of setting, or a reversed pair: the second number
        lo, hi = ((lo - 32) * Fraction(5, 9), (hi - 32) * Fraction(5, 9)) if f else (lo, hi)
        out.append(((lo, hi), (m.start(), m.end())))
    return out


def temperature_c(raw: str, s: int, e: int) -> Fraction | None:
    """The low end (deg C) of the one temperature written at ``raw[s:e]``."""
    got = parse_temperatures(raw, s, e)
    return got[0][0][0] if got else None
# strong food-target cues: the temperature that follows is the food's, not the medium's
_TARGET_CUE = re.compile(r"(?:\bthermometer|\bprobe|\binternal\s+temp(?:erature)?|\bcore\s+temp(?:erature)?|"
                         r"\bregist(?:ers?|ering)|\breads?|\breading)\b(?P<gap>[^,;.]{0,45})$", re.I)  # 0.1.0 (kept for reference)
_STRONG = re.compile(r"\b(?:thermometer|probe|(?P<core>internal\s+temp(?:erature)?|core\s+temp(?:erature)?)|"
                     r"regist(?:ers?|ering)|reads?|reading)\b", re.I)
_MEDIUM_WORDS_INSERTED = re.compile(r"\b(?:oven|water|oil|pan|pot|skillet|liquid|syrup|bath|grill|stock|milk|broth|fat|griddle|"
                                    r"steamer|cooker|then)\b", re.I)  # after "inserted": "in the centre" is the food
_MEDIUM_THERMO_PREFIX = re.compile(r"\b(?:deep[- ]fat|deep[- ]fry\w*|candy|sugar|jelly|jam|frying|oil|fat|oven)\s+thermometer\b",
                                   re.I)
_SYRUP_WORDS = r"candy|sugar|syrup|jam|jelly|marmalade|caramel|fondant|toffee|brittle|fudge|honey|molasses|treacle"
_LIQUID_WORDS = r"oil|oils|fat|lard|shortening|drippings?|water|stock|broth|milk|cream|liquid|brine|juice|wine|beer|vinegar"
_MEDIUM_PLACES = r"oven|grill|smoker|fryer|pan|skillet|griddle|bath"
_SUBJECT_SYRUP = re.compile(rf"\b(?:{_SYRUP_WORDS})\b", re.I)
_SUBJECT_LIQUID = re.compile(rf"\b(?:{_LIQUID_WORDS}|{_MEDIUM_PLACES})\b", re.I)
_OBJECT_END = re.compile(r"\b(?:in|into|with|on|over|under|for|until|till|til|at|to|from|and|then|while|about)\b|[,;(.]", re.I)
_SETTING_BEFORE = re.compile(r"\b(?:at|in\s+(?:a|an|the))\s*(?:about|around|approximately|approx\.?)?\s*$", re.I)
_UNTIL_END = re.compile(r"[,;()]|\b(?:then|before|while|and|for|or|approximately|approx)\b", re.I)
_WORD = re.compile(r"[\w'-]+")
TARGET_ROLES = ("TARGET_STRONG_CUE", "TARGET_LIST", "TARGET_UNTIL_CLAUSE")
EXEMPT_ROLES = ("EXEMPT_SYRUP_OR_CANDY", "EXEMPT_LIQUID_OR_MEDIUM_SUBJECT", "EXEMPT_SETTING_PHRASE", "EXEMPT_MEDIUM_THERMOMETER")
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


def until_clause_spans(raw: str, a: int, b: int, verbs: Sequence[int] = ()) -> list[tuple[int, int, int]]:
    """``[(trigger_start, clause_start, clause_end)]`` of the until / till clauses of ``raw[a:b]``: from the trigger to the first
    comma, semicolon, parenthesis, then / before / while / and / for / or, the next event verb, at most 90 characters (S178 FIX-PHYS).
    "about" and "approximately" do not end it ("until it reaches about 170 F")."""
    out = []
    for m in _TRIGGER.finditer(raw, a, b):
        lo = m.end()
        nxt = [v for v in verbs if v > m.start()]
        hi = min(b, lo + 90, min(nxt) if nxt else b)
        cut = _UNTIL_END.search(raw, lo, hi)
        out.append((m.start(), lo, cut.start() if cut else hi))
    return out


def _owner_start(verbs: Sequence[int], pos: int, a: int) -> int:
    prec = [v for v in verbs if v <= pos]
    return max(prec) if prec else a


def _object_phrase(raw: str, verb: int, limit: int) -> str:
    """The owner verb's object: the words after the verb up to the first preposition, conjunction or clause break (40 chars)."""
    w = _WORD.match(raw, verb)
    start = w.end() if w else verb
    hi = min(limit, start + 40)
    cut = _OBJECT_END.search(raw, start, hi)
    return raw[start:cut.start() if cut else hi]


def _syrup_context(raw: str, a: int, s: int, verbs: Sequence[int], clause_lo: int | None) -> bool:
    """A syrup / candy / jam word in the temperature's own clause, in the owner event's phrase or in its object (S178: local)."""
    own = _owner_start(verbs, s, a)
    lo = clause_lo if clause_lo is not None else max(a, s - 90)
    return bool(_SUBJECT_SYRUP.search(raw, max(own, a), s) or _SUBJECT_SYRUP.search(raw, lo, s)
                or _SUBJECT_SYRUP.search(_object_phrase(raw, own, s)))


def classify_temperatures(raw: str, a: int, b: int, temps: Iterable[tuple[Any, tuple[int, int]]],
                          verbs: Sequence[int] = ()) -> dict[tuple[int, int], str]:
    """Role of every temperature span of the sentence ``[a, b)``: one of ``TARGET_ROLES`` (a target of the food: endpoint, never a
    medium temperature), one of ``EXEMPT_ROLES`` (inside an until-clause but the liquid's / medium's own temperature or a setting)
    or ``NOT_A_TARGET``. ``verbs``: character starts of the temperature-owning event verbs of the sentence (S178 FIX-PHYS M1)."""
    verbs = sorted(verbs)
    clauses = until_clause_spans(raw, a, b, verbs)
    roles: dict[tuple[int, int], str] = {}
    prev_end = None
    for _, (s, e) in sorted(temps, key=lambda t: t[1][0]):
        clause = next((c for c in clauses if c[1] <= s and e <= c[2]), None)
        clause_lo = clause[1] if clause else None
        syrup = _syrup_context(raw, a, s, verbs, clause_lo)
        # strong cue: the LAST one before the temperature, within 45 characters, no , ; . between
        best = None
        for m in _STRONG.finditer(raw, max(a, s - 90), s):
            gap = raw[m.end():s]
            if len(gap) <= 45 and not re.search(r"[,;.]", gap):
                best = m
        role = "NOT_A_TARGET"
        if best is not None:
            gap = _FILLER.sub(" ", raw[best.end():s])
            words = _MEDIUM_WORDS_INSERTED if re.match(r"\s*inserted\b", gap, re.I) else _MEDIUM_WORDS
            medium_thermo = (not best.group("core") and _MEDIUM_THERMOMETER.match(raw[e:e + 40])) or \
                _MEDIUM_THERMO_PREFIX.search(raw, clause_lo if clause_lo is not None else max(a, s - 60), s)
            own = _owner_start(verbs, s, a)
            liquid_obj = bool(_SUBJECT_LIQUID.search(_object_phrase(raw, own, s))) and not best.group("core")
            if words.search(gap):
                role = "NOT_A_TARGET"
            elif medium_thermo:
                role = "EXEMPT_MEDIUM_THERMOMETER"
            elif syrup:
                role = "EXEMPT_SYRUP_OR_CANDY"
            elif liquid_obj and clause is not None:
                role = "EXEMPT_LIQUID_OR_MEDIUM_SUBJECT"
            else:
                role = "TARGET_STRONG_CUE"
        if role == "NOT_A_TARGET" and prev_end is not None:
            gap = raw[prev_end:s]
            if len(gap) <= 45 and not _CHAIN_BREAK.search(gap) and not syrup:
                role = "TARGET_LIST"
        if role == "NOT_A_TARGET" and clause is not None:
            own = _owner_start(verbs, s, a)
            subject = raw[clause[1]:s]
            if syrup:
                role = "EXEMPT_SYRUP_OR_CANDY"
            elif _MEDIUM_THERMO_PREFIX.search(subject) or _MEDIUM_THERMOMETER.match(raw[e:e + 40]):
                role = "EXEMPT_MEDIUM_THERMOMETER"
            elif _SETTING_BEFORE.search(raw, clause[1], s):
                role = "EXEMPT_SETTING_PHRASE"
            elif _SUBJECT_LIQUID.search(subject) or _SUBJECT_LIQUID.search(_object_phrase(raw, own, clause[0])):
                role = "EXEMPT_LIQUID_OR_MEDIUM_SUBJECT"
            else:
                role = "TARGET_UNTIL_CLAUSE"
        roles[(s, e)] = role
        prev_end = e if role in TARGET_ROLES else None
    return roles


def target_temperature_spans(raw: str, a: int, b: int, temps: Iterable[tuple[Any, tuple[int, int]]],
                             verbs: Sequence[int] = ()) -> set[tuple[int, int]]:
    """Spans (of the given ``(value, span)`` temperatures) that are TARGETS of the food (``classify_temperatures``)."""
    return {sp for sp, r in classify_temperatures(raw, a, b, temps, verbs).items() if r in TARGET_ROLES}


def until_clauses_by_event(raw: str, a: int, b: int, heat_events: Sequence[tuple[str, int]],
                           roles: Mapping[tuple[int, int], str], verbs: Sequence[int] = ()) -> dict[str, list[dict]]:
    """``until_clauses`` of the endpoint block per heat event (owner = the nearest heat verb before the trigger): span of the clause
    and the role of every temperature inside it. Spans and codes only."""
    out: dict[str, list[dict]] = {eid: [] for eid, _ in heat_events}
    if not heat_events:
        return out
    for t0, lo, hi in until_clause_spans(raw, a, b, sorted(set(verbs) | {st for _, st in heat_events})):
        idx = [i for i, (_, st) in enumerate(heat_events) if st <= t0]
        eid = heat_events[idx[-1] if idx else 0][0]
        inside = [{"span": [s, e], "role": r} for (s, e), r in sorted(roles.items()) if lo <= s and e <= hi]
        out[eid].append({"span": [t0, hi], "temperatures": inside})
    return out


def extract_sentence(raw: str, a: int, b: int, heat_events: Sequence[tuple[str, int]], *, lex: Sequence[Entry] | None = None,
                     temps: Iterable[tuple[Any, tuple[int, int]]] = (), root: Path = ROOT,
                     roles: Mapping[tuple[int, int], str] | None = None, verbs: Sequence[int] = ()) -> dict[str, list[dict]]:
    """Cues of one sentence ``[a, b)`` per heat event. ``heat_events``: [(event_id, verb char_start)] in text order. Cues are
    {class, trigger, span, proc_id, target_c?}; text is never copied. ``roles``: the temperature roles of the sentence
    (``classify_temperatures``, as the binder's temperature plan computed them); ``verbs``: owner verb starts of the sentence."""
    lex = lex or load_lexicon(root)
    temps = list(temps)
    if roles is None:
        roles = classify_temperatures(raw, a, b, temps, sorted(set(verbs) | {st for _, st in heat_events}))
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
    targets = sorted(sp for sp, r in roles.items() if r in TARGET_ROLES)
    for cues in out.values():  # an until-clause that only holds a food-target temperature is explained by that target
        cues[:] = [c for c in cues if not (c["class"] == UNCLASSIFIED and any(c["span"][0] <= s and e <= c["span"][1] for s, e in targets))]
    for (s, e) in targets:
        tc = temperature_c(raw, s, e)
        out[heat_events[owner(s)][0]].append({"class": TARGET_CLASS, "trigger": "TARGET", "span": [s, e], "proc_id": None,
                                              "target_c": str(tc) if tc is not None else None})
    for cues in out.values():
        cues.sort(key=lambda c: (c["span"][0], c["class"]))
    return out


def block(cues: Sequence[Mapping], until_clauses: Sequence[Mapping] | None = None) -> dict:
    """The ``endpoint`` block of one Layer 1 event record (QUALITATIVE, with spans; never part of ``inputs``). ``until_clauses``
    (S178 FIX-PHYS): the clause spans and the role of every temperature inside them (spans and codes only)."""
    cues = [dict(c) for c in cues]
    if not cues:
        crit = {"value": None, "status": "UNKNOWN", "basis": None, "span": None, "reason": "NO_ENDPOINT_CUE"}
    else:
        c = cues[0]
        crit = {"value": c["class"], "status": "QUALITATIVE", "basis": "TEXT_CUE", "span": list(c["span"]),
                "span_id": span_id(c["span"]), "row": f"endpoint_cue_lexicon_v1:{c['class']}", "role": ROLE}
    out = {"stopping_criterion": crit, "cues": cues, "n_cues": len(cues), "version": VERSION}
    if until_clauses is not None:
        out["until_clauses"] = [dict(c) for c in until_clauses]
    return out


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
