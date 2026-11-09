"""Counts-only census of ingredient line -> grams over recipe records (S175).

Per family: lines by basis, q_level, UNKNOWN reason and ING->SR match status, lines with grams (Q0-Q2), lines whose
grams rest on an unverified SR link, and recipes whose every quantified line has grams. The food finder and the
name resolver are injected (the tool wires Rung A's lexicon and ``ing_sr_match.resolve``). No text leaves: the
output holds integers and fixed labels only.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping

from culinarystate.composition.line_mass import line_mass
from culinarystate.composition.sr_legacy import SRFood
from culinarystate.quantity.grammar import parse_line
from culinarystate.quantity.normalize import normalize

VERSION = "s179-line-census-0.2.0"
LOCALE: Mapping[str, str | None] = {"A1_BBC_GOOD_FOOD": "UK", "FOODCOM": "US", "WIKIBOOKS": None,
                                    "GUTENBERG_SEGMENT": None, "TASTESET": None}
UNITS_MISSING = frozenset({"FOODCOM"})
HISTORICAL_UNITS = frozenset({"GUTENBERG_SEGMENT"})     # S179 A6b: no volume grams before a historical-unit registry
_SLASHES = str.maketrans({"\u2044": "/", "\u2215": "/"})   # S179 A4: FRACTION SLASH, DIVISION SLASH
LABELS = ["COUNTS_ONLY", "MODEL_DERIVED_GRAMS", "SR_LINK_UNVERIFIED"]
_STR_KEYS = frozenset({"labels", "version", "lot_kind"})


@dataclass(frozen=True)
class Resolved:
    fdc_id: int | None
    status: str


def _line(line: str, family: str, find_food: Callable[[str], str | None], resolve: Callable[[str], Resolved],
          foods: Mapping[int, SRFood]):
    line = line.translate(_SLASHES)
    name = find_food(line)
    res = resolve(name) if name else Resolved(None, "NO_FOOD_MENTION")
    q = parse_line(line)
    food = foods.get(res.fdc_id) if res.fdc_id is not None else None
    locale = LOCALE.get(family)
    return res, line_mass(q, normalize(q, locale), food, units_missing=family in UNITS_MISSING,
                          locale_known=locale is not None, historical_units=family in HISTORICAL_UNITS)


def _empty() -> dict:
    return {"recipes": 0, "lines": 0, "basis": Counter(), "q_level": Counter(), "reason": Counter(),
            "match_status": Counter(), "flags": Counter(), "lines_with_grams": 0, "lines_with_grams_link_unverified": 0,
            "recipes_all_quantified_lines_with_grams": 0}


def census(records: Iterable[Mapping], *, find_food: Callable[[str], str | None],
           resolve: Callable[[str], Resolved], foods: Mapping[int, SRFood]) -> dict:
    fams: dict[str, dict] = {}
    for rec in records:
        fam = rec["source_family"]
        acc = fams.setdefault(fam, _empty())
        acc["recipes"] += 1
        all_ok, any_quant = True, False
        for line in rec.get("ingredient_lines") or []:
            res, m = _line(line, fam, find_food, resolve, foods)
            acc["lines"] += 1
            acc["basis"][m.basis] += 1
            acc["q_level"][m.q_level] += 1
            acc["match_status"][res.status] += 1
            if m.reason:
                acc["reason"][m.reason] += 1
            for fl in m.flags:
                acc["flags"][fl] += 1
            has = m.q_level in ("Q0", "Q1", "Q2")
            acc["lines_with_grams"] += has
            acc["lines_with_grams_link_unverified"] += has and m.link_verification_required
            if m.status != "QUALITATIVE":
                any_quant = True
                all_ok = all_ok and has
        acc["recipes_all_quantified_lines_with_grams"] += any_quant and all_ok
    out = {fam: {k: dict(sorted(v.items())) if isinstance(v, Counter) else int(v) for k, v in acc.items()}
           for fam, acc in sorted(fams.items())}
    return {"version": VERSION, "labels": list(LABELS), "families": out}


def assert_counts_only(obj, key: str = "") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise ValueError(f"non-string key under {key!r}")
            assert_counts_only(v, k)
    elif isinstance(obj, list):
        for v in obj:
            assert_counts_only(v, key)
    elif isinstance(obj, bool) or not isinstance(obj, (int, str)):
        raise ValueError(f"non-count value under {key!r}: {type(obj).__name__}")
    elif isinstance(obj, str) and key not in _STR_KEYS:
        raise ValueError(f"free text under {key!r}")
