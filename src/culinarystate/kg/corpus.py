"""One recipe view over every recipe source, for concept-level KG statistics (X3c).

Each RecipeView: rec_id, source family, ING ids, ingredient lines (text, ING id), steps, cuisines,
components (sub-section group -> ING ids). Raw text is read from local copies only; nothing is written back.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import pandas as pd

from culinarystate.vocab.foodon import norm
from culinarystate.vocab.line_link import LineLinker

GROUP_NOISE = re.compile(r"^(for (the )?|the |to serve|optional)|\b(ingredients?|recipe|part \d+)\b")


@dataclass
class RecipeView:
    rec_id: str
    family: str
    ing_ids: set[str]
    lines: list[tuple[str, str | None]]
    steps: list[str]
    cuisines: list[str] = field(default_factory=list)
    components: dict[str, set[str]] = field(default_factory=dict)


def component_name(group: str | None) -> str | None:
    if not group:
        return None
    g = norm(GROUP_NOISE.sub("", group.lower()).strip(" :-"))
    return g if g and len(g.split()) <= 3 else None


def bbc(a1_processed: Path, rec_ids: dict[str, str], linker: LineLinker, names: dict[str, str]) -> Iterator[RecipeView]:
    for line in a1_processed.open():
        r = json.loads(line)
        rid = rec_ids.get(r["recipe_id"])
        if not rid:
            continue
        ings = {names[norm(c)] for c in r.get("ingredients_canonical") or [] if norm(c) in names}
        lines = [(t, linker.link(t)[0]) for t in r.get("ingredient_phrases_raw") or []]
        cuisines = [c.strip() for c in (r.get("cuisine_raw") or "").split(",") if c.strip()]
        yield RecipeView(rid, "BBCGF-A1", ings | {i for _, i in lines if i}, lines,
                         r.get("instruction_steps_raw") or [], cuisines)


def wikibooks(recipes_jsonl: Path, links_csv: Path, rec_ids: dict[int, str], cuisine_of: dict[str, str | None]) \
        -> Iterator[RecipeView]:
    links = pd.read_csv(links_csv)
    by_rec = {k: g.sort_values("line") for k, g in links.groupby("rec_id")}
    for line in recipes_jsonl.open():
        r = json.loads(line)
        rid = rec_ids.get(r["pageid"])
        if not rid or rid not in by_rec:
            continue
        lk = by_rec[rid]
        ing_of_line = dict(zip(lk.line, lk.ing_id.where(lk.ing_id.notna(), None)))
        lines, comps = [], {}
        for i, ln in enumerate(r["ingredients"]):
            iid = ing_of_line.get(i)
            lines.append((ln["text"], iid))
            c = component_name(ln.get("group"))
            if c and iid:
                comps.setdefault(c, set()).add(iid)
        yield RecipeView(rid, "WIKIBOOKS-COOKBOOK", {i for _, i in lines if i}, lines, [s["text"] for s in r["steps"]],
                         (cuisine_of.get(rid) or "").split("|") if cuisine_of.get(rid) else [], comps)
