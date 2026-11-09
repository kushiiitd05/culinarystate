"""Counts-only lot census (S175): one RECIPE_POOL lot per recipe, every ingredient line a member.

A recipe pool is the upper envelope of what any lot in that recipe can contain; event-level lots (router lineage)
come next. Reports, per family: lots, water mass-fraction status and width buckets, pH flags and provisional
counts. Integers and fixed labels only.
"""
from __future__ import annotations

from collections import Counter
from typing import Callable, Iterable, Mapping

from culinarystate.composition.food_ph import PHTable
from culinarystate.composition.line_census import LABELS, Resolved, _line
from culinarystate.composition.lot_state import Member, lot_state
from culinarystate.composition.sr_legacy import SRFood

VERSION = "s175-lot-census-0.1.0"
WIDTHS = ((0.05, "lt_0.05"), (0.2, "lt_0.2"), (0.5, "lt_0.5"))


def width_bucket(lo: float, hi: float | None) -> str:
    if hi is None:
        return "unbounded"
    w = hi - lo
    return next((name for cut, name in WIDTHS if w < cut), "ge_0.5")


def _empty() -> dict:
    return {"recipes": 0, "lots": 0, "water_g_status": Counter(), "water_g_width": Counter(), "ph_flags": Counter(),
            "provisional": 0}


def census(records: Iterable[Mapping], *, find_food: Callable[[str], str | None],
           resolve: Callable[[str], Resolved], foods: Mapping[int, SRFood], ph: PHTable) -> dict:
    fams: dict[str, dict] = {}
    for rec in records:
        fam = rec["source_family"]
        acc = fams.setdefault(fam, _empty())
        acc["recipes"] += 1
        members = []
        for line in rec.get("ingredient_lines") or []:
            name = find_food(line) or ""
            res, mass = _line(line, fam, find_food, resolve, foods)
            food = foods.get(res.fdc_id) if res.fdc_id is not None else None
            members.append(Member(name, food, mass, ph.lookup(name)))
        if not members:
            continue
        s = lot_state(members)
        acc["lots"] += 1
        w = s.composition["water_g"]
        acc["water_g_status"][w.status] += 1
        if w.status == "INTERVAL":
            acc["water_g_width"][width_bucket(w.low, w.high)] += 1
        for f in s.ph_flags:
            acc["ph_flags"][f] += 1
        acc["provisional"] += "PROVISIONAL_SR_LINK_UNVERIFIED" in s.labels
    out = {fam: {k: dict(sorted(v.items())) if isinstance(v, Counter) else int(v) for k, v in acc.items()}
           for fam, acc in sorted(fams.items())}
    return {"version": VERSION, "labels": list(LABELS), "lot_kind": "RECIPE_POOL", "families": out}
