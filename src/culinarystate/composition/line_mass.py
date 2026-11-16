"""Ingredient line -> grams interval for the lot-state layer (S175).

Order of bases (first that applies wins):
    QUALITATIVE              pinch / handful / to taste: no grams
    UNIT_MISSING_IN_SOURCE   the source dropped units (Food.com Kaggle): no grams
    TEXT_STATED_MASS         grams written in the line (SOURCE_STATED)
    VOLUME_x_SR_DENSITY      parser mL interval x [min, max] SR density over the food's volume portions
    COUNT_x_SR_PORTION       count x SR per-item grams: size word (first token), else a portion noun in the line,
                             else the whole-item portions (small/medium/large/..., or a portion named by the SR
                             head noun, e.g. "pepper" for "Peppers, hot chili"); slices never stand in for items.
                             UK portion nouns map to SR ones: stick -> stalk, rasher -> slice
    UNKNOWN                  with a reason (NO_AMOUNT, NO_SR_FOOD, NO_SR_DENSITY, NO_SR_COUNT_PORTION,
                             HISTORICAL_UNIT_REGISTRY_MISSING)
SR portions are US customary measures, converted with the NIST HB44 values in ``quantity.units``; quart, pint,
gallon, litre and mL rows are volumes too (S179 F2). Converted grams are MODEL_DERIVED (never MEASURED); every
interval is the exact min-max over the portions used. An unsized count spans every SR size (small ... jumbo, S179 A5);
"yield" rows (e.g. "unit (yield from 1 lb ...)") are product yields, never item weights (S179 F3).

POINT is reserved for a stated mass (SSOT 285.6, S179 A6): SR-derived grams are always INTERVAL, flagged
SR_SINGLE_PORTION_NO_SPREAD when one SR value stands for the whole spread. Flags (S179 A6b):
UNIT_HULL_LOCALE_UNKNOWN when the source locale is unknown and the volume unit has several conventions (the hull
covers the registered ones only); text with historical units (Gutenberg) gets no volume grams until a historical-unit
registry exists.

q_level (SSOT 235.3): stated mass Q0; SR portion Q1 (AUTHORITATIVE_PORTION); SR density Q2 (AUTHORITATIVE_DENSITY);
else Q6. Q1/Q2 hold only once a human has verified the ING->SR link (vocab/fdc.py rule), so SR-based grams carry
``link_verification_required``; until then downstream layers label them PROVISIONAL, never evidence.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from culinarystate.composition.ing_sr_match import normalise
from culinarystate.composition.sr_legacy import Portion, SRFood
from culinarystate.quantity.grammar import QuantityParse
from culinarystate.quantity.normalize import Normalized
from culinarystate.quantity.units import BY_KEY

_US = {k: BY_KEY[k].conventions["US"][0] for k in ("cup", "tbsp", "tsp", "fl_oz", "quart", "pint", "gallon")}
_US.update({"l": BY_KEY["l"].si, "ml": BY_KEY["ml"].si})
_VOLUME_WORDS = {"cup": "cup", "cups": "cup", "tbsp": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
                 "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp", "quart": "quart", "quarts": "quart",
                 "pint": "pint", "pints": "pint", "gallon": "gallon", "gallons": "gallon", "liter": "l",
                 "liters": "l", "litre": "l", "litres": "l", "ml": "ml", "milliliter": "ml", "milliliters": "ml",
                 "millilitre": "ml", "millilitres": "ml"}
_NOT_COUNT = frozenset({"oz", "lb", "fl", "cubic", "serving", "nlea", "package", "jar", "can", "container",
                        "bottle", "packet", "inch", "g", "pat", "dash", "pinch"} | set(_VOLUME_WORDS))
SIZES = frozenset({"small", "medium", "large", "extra_small", "extra_large", "jumbo", "mini"})
WHOLE_ITEM = frozenset({"whole", "fruit", "item", "unit", "each"}) | SIZES
NOUN_ALIAS = {"stick": "stalk", "rasher": "slice"}
_WORD = re.compile(r"[a-z]+")


@dataclass(frozen=True)
class LineMass:
    status: str                 # POINT INTERVAL QUALITATIVE UNKNOWN
    low_g: float | None
    high_g: float | None
    basis: str
    value_type: str | None      # SOURCE_STATED | MODEL_DERIVED | None
    reason: str | None = None
    fdc_id: int | None = None
    portions: tuple[str, ...] = ()
    q_level: str = "Q6"
    link_verification_required: bool = False
    flags: tuple[str, ...] = ()


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _sing_words(text: str) -> list[str]:
    return [normalise(w)[0] for w in _words(text)]


def _head(food: SRFood) -> str:
    first = normalise(food.description.split(",")[0])
    return first[-1] if first else ""


def _size_key(words: list[str]) -> str | None:
    """Size word at the start of ``words``; "extra large" -> "extra_large"."""
    if len(words) > 1 and words[0] == "extra" and f"extra_{words[1]}" in SIZES:
        return f"extra_{words[1]}"
    return words[0] if words and words[0] in SIZES else None


def _lead(por: Portion, head: str) -> str:
    """Leading portion noun; a portion named by the food's head noun is a whole item (or its size word)."""
    w = _sing_words(por.description)
    if w[0] == head:
        return _size_key(w[1:]) or "whole"
    return _size_key(w) or w[0]


def portion_ml(por: Portion) -> float | None:
    """mL of one SR portion row if it is a US volume measure, else None."""
    unit = por.unit_name.lower() if por.unit_id != 9999 else ""
    words = _words(unit or por.description)
    if not words:
        return None
    if words[:2] == ["fl", "oz"]:
        return por.amount * _US["fl_oz"]
    key = _VOLUME_WORDS.get(words[0])
    return por.amount * _US[key] if key else None


_Q = {"TEXT_STATED_MASS": "Q0", "COUNT_x_SR_PORTION": "Q1", "VOLUME_x_SR_DENSITY": "Q2"}


def _interval(lo: float, hi: float, basis: str, vtype: str, fdc: int | None, used: tuple[str, ...],
              flags: tuple[str, ...] = ()) -> LineMass:
    stated = basis == "TEXT_STATED_MASS"
    status = "POINT" if lo == hi and stated else "INTERVAL"
    return LineMass(status, lo, hi, basis, vtype, None, fdc, used, _Q[basis], not stated, flags)


def _spread_flag(values: list[float]) -> tuple[str, ...]:
    return ("SR_SINGLE_PORTION_NO_SPREAD",) if min(values) == max(values) else ()


def _unknown(reason: str, basis: str = "UNKNOWN", fdc: int | None = None) -> LineMass:
    return LineMass("UNKNOWN", None, None, basis, None, reason, fdc)


def _bounds(ch: dict) -> tuple[float, float] | None:
    if ch.get("status") == "MEASURED":
        return ch["value"], ch["value"]
    if ch.get("status") == "RANGE":
        return ch["low"], ch["high"]
    return None


def _from_volume(ml: tuple[float, float], food: SRFood, flags: tuple[str, ...] = ()) -> LineMass:
    dens = [(por.gram_weight / v, por.description) for por in food.portions
            if (v := portion_ml(por)) and por.gram_weight > 0]
    if not dens:
        return _unknown("NO_SR_DENSITY", fdc=food.fdc_id)
    vals = [d for d, _ in dens]
    return _interval(ml[0] * min(vals), ml[1] * max(vals), "VOLUME_x_SR_DENSITY", "MODEL_DERIVED", food.fdc_id,
                     tuple(sorted({s for _, s in dens})), _spread_flag(vals) + flags)


def _count_portions(q: QuantityParse, food: SRFood) -> list[Portion]:
    countable = [por for por in food.portions
                 if (w := _words(por.description)) and w[0] not in _NOT_COUNT and portion_ml(por) is None
                 and "yield" not in w and por.amount > 0]
    head = _head(food)
    first = {id(por): _lead(por, head) for por in countable}
    if q.size:
        size = _size_key(q.size.lower().split()) or q.size.lower()
        chosen = [por for por in countable if first[id(por)] == size]
        if chosen:
            return chosen
    line = {NOUN_ALIAS.get(w, w) for w in _sing_words(q.raw)} - WHOLE_ITEM - {head}
    chosen = [por for por in countable if first[id(por)] in line]
    return chosen or [por for por in countable if first[id(por)] in WHOLE_ITEM]


def _from_count(n: tuple[float, float], q: QuantityParse, food: SRFood) -> LineMass:
    chosen = _count_portions(q, food)
    if not chosen:
        return _unknown("NO_SR_COUNT_PORTION", fdc=food.fdc_id)
    per = [por.gram_weight / por.amount for por in chosen]
    return _interval(n[0] * min(per), n[1] * max(per), "COUNT_x_SR_PORTION", "MODEL_DERIVED", food.fdc_id,
                     tuple(por.description for por in chosen), _spread_flag(per))


def _hull_flags(q: QuantityParse, locale_known: bool) -> tuple[str, ...]:
    unit = BY_KEY.get(q.unit_key) if q.unit_key else None
    if locale_known or unit is None or unit.si is not None:
        return ()
    return ("UNIT_HULL_LOCALE_UNKNOWN",) if len({v for v, _ in unit.conventions.values()}) > 1 else ()


def line_mass(q: QuantityParse, norm: Normalized, food: SRFood | None, *, units_missing: bool = False,
              locale_known: bool = True, historical_units: bool = False) -> LineMass:
    if norm.mass_g.get("status") == "QUALITATIVE":
        return LineMass("QUALITATIVE", None, None, "QUALITATIVE", None, None, food.fdc_id if food else None)
    if units_missing:
        return _unknown("UNIT_MISSING_IN_SOURCE", "UNIT_MISSING_IN_SOURCE", food.fdc_id if food else None)
    if (m := _bounds(norm.mass_g)) is not None:
        return _interval(m[0], m[1], "TEXT_STATED_MASS", "SOURCE_STATED", food.fdc_id if food else None, ())
    vol, cnt = _bounds(norm.volume_ml), _bounds(norm.count)
    if vol is None and cnt is None:
        return _unknown("NO_AMOUNT", fdc=food.fdc_id if food else None)
    if food is None:
        return _unknown("NO_SR_FOOD")
    if vol is not None:
        if historical_units:
            return _unknown("HISTORICAL_UNIT_REGISTRY_MISSING", fdc=food.fdc_id)
        return _from_volume(vol, food, _hull_flags(q, locale_known))
    return _from_count(cnt, q, food)
