"""Link EVD rows to internal PROC- and ING- ids (AH2: internal identity first).

Process: every evidence step -> PROC id via map_step_name; primary process_id = first heat-family step,
else first step. Ingredient: longest registry concept whose (singularised) tokens are all present in the
matrix name; band EXACT (equal) / HIGH (unique longest) / MEDIUM (tie broken by corpus frequency) / NONE.
Only EXACT and HIGH are written to matrix.ingredient_id; MEDIUM goes to the review table.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from culinarystate.process.vocab import BY_CANON, map_step_name

HEAT = {"DRY_HEAT", "FAT_HEAT", "WET_HEAT", "HEAT_GENERAL", "PRESERVATION", "COOLING", "FERMENT_LEAVEN"}
STOP = {"raw", "fresh", "whole", "common", "and", "or", "with", "without", "in", "of", "the", "etc", "other", "type",
        "variety", "cooked", "boiled", "baked", "fried", "peeled", "unpeeled", "dried", "frozen", "canned"}


def _sing(w: str) -> str:
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith(("oes", "ches", "shes", "sses")):
        return w[:-2]
    if w.endswith("s") and not w.endswith(("ss", "us")) and len(w) > 3:
        return w[:-1]
    return w


def toks(s: str) -> list[str]:
    return [_sing(w) for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP]


def link_process(steps: list[str], proc_ids: dict[str, str]) -> tuple[str | None, list[str]]:
    canon = [map_step_name(s) for s in steps]
    ids = [proc_ids[c] for c in canon if c and c in proc_ids]
    primary = next((proc_ids[c] for c in canon if c and c in proc_ids and BY_CANON[c].family in HEAT), None)
    return primary or (ids[0] if ids else None), list(dict.fromkeys(ids))


@dataclass(frozen=True)
class IngLink:
    ing_id: str | None
    concept: str | None
    band: str
    alternatives: tuple[str, ...] = ()


class IngredientLinker:
    def __init__(self, concepts: dict[str, tuple[str, int]]):
        """concepts: canonical_name -> (ING id, corpus frequency)."""
        self.concepts = concepts
        self.tok = {name: frozenset(toks(name)) for name in concepts}

    def link(self, matrix_raw: str) -> IngLink:
        name = re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", matrix_raw.lower())).strip()
        if name in self.concepts:
            return IngLink(self.concepts[name][0], name, "EXACT")
        mt = set(toks(matrix_raw))
        # "Onion [Red]" -> also try bracket-first order tokens (already order-free via sets)
        cands = [(len(t), n) for n, t in self.tok.items() if t and t <= mt]
        if not cands:
            return IngLink(None, None, "NONE")
        best = max(c[0] for c in cands)
        top = sorted((n for k, n in cands if k == best), key=lambda n: (-self.concepts[n][1], n))
        if len(top) == 1:
            return IngLink(self.concepts[top[0]][0], top[0], "HIGH")
        return IngLink(self.concepts[top[0]][0], top[0], "MEDIUM", tuple(top[1:4]))
