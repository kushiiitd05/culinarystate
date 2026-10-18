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


BENIGN = {"unknown", "color", "colour", "species", "variety", "cultivar", "type", "pure", "highbush", "lowbush",
          "whole", "raw", "fresh", "common", "grain"}
FORM_TOKENS = {"juice", "jam", "oil", "flour", "puree", "purée", "paste", "powder", "seed", "peel", "skin", "leaf",
               "sauce", "wine", "vinegar", "syrup", "extract", "grits", "bran", "flake", "meal"}
FORM_TOKENS = {_sing(w) for w in FORM_TOKENS}            # same normalisation as toks() (grits -> grit)


class IngredientLinker:
    def __init__(self, concepts: dict[str, tuple[str, int]], polysemous: set[str] | None = None):
        """concepts: canonical_name -> (ING id, corpus frequency); polysemous names never auto-link."""
        self.concepts = concepts
        self.polysemous = polysemous or set()
        self.tok = {name: frozenset(toks(name)) for name in concepts}

    def link(self, matrix_raw: str) -> IngLink:
        name = re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", matrix_raw.lower())).strip()
        if name in self.concepts:
            band = "MEDIUM" if name in self.polysemous else "EXACT"
            return IngLink(self.concepts[name][0], name, band)
        mt = set(toks(matrix_raw))
        first = matrix_raw.lower().split(",")[0]
        head_seg = set(toks(re.sub(r"\[.*?\]", " ", first)))          # food segment without [qualifiers]
        cands = [(len(t), n) for n, t in self.tok.items()
                 if t and t <= mt and toks(n)[-1:] and toks(n)[-1] in head_seg]   # concept head must be the food
        if not cands:
            return IngLink(None, None, "NONE")
        best = max(c[0] for c in cands)
        top = sorted((n for k, n in cands if k == best), key=lambda n: (-self.concepts[n][1], n))
        chosen = top[0]
        extra = (head_seg | (mt & FORM_TOKENS)) - self.tok[chosen] - BENIGN
        if len(top) == 1 and not extra and chosen not in self.polysemous:
            return IngLink(self.concepts[chosen][0], chosen, "HIGH")
        return IngLink(self.concepts[chosen][0], chosen, "MEDIUM", tuple(top[1:4]) + tuple(sorted(extra))[:3])


def keep_linker_fields(prev: dict | None, rec: dict) -> dict:
    """Builders rewrite EVD from source; fields owned by link_evidence / review tools carry over (RUNBOOK §4)."""
    if not prev:
        return rec
    m = {**rec["matrix"], "ingredient_id": prev["matrix"].get("ingredient_id")}
    p = {**rec["process"], **{k: prev["process"][k] for k in ("process_id", "step_process_ids") if k in prev["process"]}}
    out = {**rec, "matrix": m, "process": p}
    if (prev.get("verification") or {}).get("status", "UNVERIFIED") != "UNVERIFIED":
        out["verification"] = prev["verification"]
    return out
