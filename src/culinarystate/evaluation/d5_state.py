"""D5 S-block gold helpers (reports/del5/d5_benchmark_preregistration_DRAFT.md §1, §3). AI draft gold; humans review.

graph(text): the current Rung A event graph. heated_ingredient_ids: ingredients whose lots (walking parent lots, as
the router demo does) were consumed by an event whose process is in a heat family. next_action: the first event in
the steps after the cut. seeded_cut: a cut after step k, 2 <= k <= n-1, from sha256(seed || recipe_id).
"""
from __future__ import annotations

import hashlib
from typing import Mapping, Sequence

from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.mechanism.router_demo import _attr, _lot_ingredients
from culinarystate.quantity import rc2_dryrun as D

HEAT_FAMILIES = ("WET_HEAT", "DRY_HEAT", "FAT_HEAT")
_RUNG: RungA | None = None
_SCHEMA = None


def graph(text: str, locale: str | None = None):
    global _RUNG, _SCHEMA
    _RUNG = _RUNG or RungA()
    _SCHEMA = _SCHEMA or D.load_schema()
    return _RUNG.run(SourceText.from_raw("D5", text), _RUNG.config(locale=locale), schema=_SCHEMA).graph


def linked_ingredient_ids(g) -> set[str]:
    return {i for e in g.entities for i in [_attr(e.attributes, "ingredient_id")] if i}


def heated_ingredient_ids(g, family_of: Mapping[str, str]) -> set[str]:
    out: set[str] = set()
    for ev in g.events:
        if family_of.get(_attr(ev.attributes, "proc_id")) in HEAT_FAMILIES:
            out.update(_lot_ingredients(g, ev.consumes))
    return out


def next_action(steps: Sequence[str], cut: int, locale: str | None = None) -> dict | None:
    """First event of steps[cut:] when the recipe is read whole (context carried), or None if nothing follows."""
    if cut >= len(steps):
        return None
    prefix = "\n".join(steps[:cut])
    offset = len(prefix) + (1 if prefix else 0)
    g = graph("\n".join(steps), locale)
    after = sorted((ev for ev in g.events if ev.span.char_start >= offset), key=lambda e: e.span.char_start)
    if not after:
        return None
    ev = after[0]
    starts, pos = [], 0
    for s in steps:
        starts.append(pos)
        pos += len(s) + 1
    idx = max(i for i, st in enumerate(starts) if st <= ev.span.char_start)
    return {"action": ev.span.surface, "process_id": _attr(ev.attributes, "proc_id"), "step_index": idx}


def seeded_cut(recipe_id: str, n_steps: int, *, seed: str) -> int:
    if n_steps < 3:
        raise ValueError("need at least 3 steps")
    h = int(hashlib.sha256((seed + recipe_id).encode()).hexdigest(), 16)
    return 2 + h % (n_steps - 2)
