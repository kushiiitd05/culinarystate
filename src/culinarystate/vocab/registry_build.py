"""Ingredient registry v1 (ING-/ALIAS-) from a corpus mention table.

Input columns (A1 ingredient_mentions.csv): recipe_id, ingredient_surface, ingredient_normalized,
ingredient_canonical, ingredient_family. Concepts are corpus-supported only (min recipe frequency);
nothing is added to reach a target count. Parent links come from structure (form / modifier + base),
never from guesses about biology. Crosswalks start UNRESOLVED_EXTERNAL (AH2).
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass

import pandas as pd

FORM_WORDS = ("powder", "paste", "juice", "zest", "flakes", "flake", "seeds", "seed", "leaves", "leaf", "purée",
              "puree", "extract", "oil", "stock", "syrup", "sauce", "pulp", "concentrate", "granules", "essence")
MODIFIERS = ("unsalted", "salted", "lightly salted", "smoked", "unsmoked", "dried", "fresh", "frozen", "ground",
             "full-fat", "low-fat", "half-fat", "reduced-fat", "fat-free", "skimmed", "semi-skimmed", "whole",
             "free-range", "organic", "light", "dark", "raw", "cooked", "toasted", "roasted", "baby", "young",
             "ripe", "large", "small", "plain", "natural", "greek", "wild", "sweet", "hot", "mild", "crushed",
             "chopped", "sliced", "grated", "flaked", "desiccated", "golden", "white", "brown", "red", "green",
             "yellow", "black", "roast", "mashed", "boiled", "pickled", "candied", "stewed", "steamed",
             "fried", "baked", "grilled")
# Curated polysemy (linguistic, AI-drafted -> human review). Bare form is ambiguous across senses/locales.
POLYSEMOUS = {
    "coriander": "leaf (cilantro) vs seed/ground spice", "pepper": "black pepper spice vs capsicum",
    "chilli": "fresh chilli vs chilli powder/flakes", "cream": "single/double/whipping/soured unspecified",
    "stock": "chicken/vegetable/beef unspecified; cube vs liquid", "squash": "winter squash vs UK fruit cordial",
    "mint": "fresh leaf vs dried vs mint sauce", "chips": "UK fries vs US crisps",
    "biscuit": "UK cookie vs US scone-like bread", "flour": "plain/self-raising/strong unspecified",
    "sugar": "caster/granulated/icing/brown unspecified", "oil": "type unspecified",
    "vinegar": "type unspecified", "gram": "chickpea (besan) vs unit", "corn": "maize vs UK grain generic",
    "jelly": "UK gelatin dessert vs US jam", "mince": "minced meat (UK) vs mincemeat",
}
NON_FOOD = re.compile(r"\b(cutter|tin|tray|paper|string|skewer[s]?|stick[s]? for|foil|cocktail stick|"
                      r"ice lolly stick|kitchen|baking parchment|twine|cling|board|bag|cake case[s]?)\b")
FOOD_PART = re.compile(r"\b(skin[s]?|bone[s]?|pin bone[s]?|trimming[s]?|frond[s]?|carcass)\b")
ADJECTIVE_ONLY = {"firm", "fresh", "large", "small", "medium", "ripe", "hot", "cold", "warm", "soft", "hard", "fine",
                  "dry", "wet", "raw", "cooked", "whole", "half", "extra", "plain", "light", "dark", "granary",
                  "white", "black", "red", "green", "yellow", "brown", "golden", "pink", "purple", "orange-fleshed",
                  "chinese", "indian", "thai", "italian", "mexican", "french", "greek", "spanish", "japanese",
                  "korean", "vietnamese", "british", "english", "american", "asian", "mediterranean", "middle eastern"}
GENERIC_HEADS = set(FORM_WORDS) | {"mix", "mixture", "dough", "filling", "topping", "dressing"}


@dataclass(frozen=True)
class Concept:
    name: str
    recipe_freq: int
    mention_freq: int
    parent: str | None
    relation: str | None          # FORM_OF | VARIANT_OF | HEAD_NOUN
    facets: dict
    ambiguity: str


@dataclass(frozen=True)
class AliasRow:
    surface: str
    canonical: str | None
    candidates: tuple[str, ...]
    count: int
    alias_type: str
    link_band: str


def _singular(w: str) -> str:
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith(("oes", "ses", "xes", "ches", "shes")):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    return w


def classify_reject(name: str) -> str | None:
    n = name.strip().lower()
    if not n or len(n) < 2:
        return "empty"
    if n in ADJECTIVE_ONLY:
        return "adjective_only"
    if NON_FOOD.search(n):
        return "non_food_utensil"
    if FOOD_PART.search(n):
        return "food_part_needs_part_model"
    if len(n.split()) > 5:
        return "too_long_phrase"
    if re.search(r"\d", n):
        return "contains_digit"
    return None


def structural_parent(name: str, known: set[str]) -> tuple[str | None, str | None, dict]:
    words = name.split()
    facets: dict = {}
    if len(words) >= 2 and words[-1] in FORM_WORDS:
        base = " ".join(words[:-1])
        facets["form"] = words[-1]
        if base in known:
            return base, "FORM_OF", facets
    for mod in sorted(MODIFIERS, key=len, reverse=True):
        if name.startswith(mod + " "):
            base = name[len(mod) + 1:]
            if base in known:
                facets["modifier"] = mod
                return base, "VARIANT_OF", facets
    if len(words) >= 2:
        head = words[-1]
        if head in known and head not in GENERIC_HEADS and head != name:
            return head, "HEAD_NOUN", facets           # grouping only; not a taxonomy parent
    return None, None, facets


def build_concepts(m: pd.DataFrame, min_recipes: int = 3) -> tuple[list[Concept], pd.DataFrame]:
    rf = m.groupby("ingredient_canonical")["recipe_id"].nunique()
    mf = m["ingredient_canonical"].value_counts()
    rejects, keep = [], {}
    for name, freq in rf.items():
        if freq < min_recipes:
            continue
        why = classify_reject(name)
        if why:
            rejects.append({"canonical": name, "recipe_freq": int(freq), "reason": why})
        else:
            keep[name] = int(freq)
    known = set(keep)
    surfaces_per_canon = m.groupby("ingredient_canonical")["ingredient_normalized"].nunique()
    concepts = []
    for name, freq in sorted(keep.items(), key=lambda kv: (-kv[1], kv[0])):
        parent, rel, facets = structural_parent(name, known)
        amb = "HIGH" if name in POLYSEMOUS else ("LOW" if surfaces_per_canon.get(name, 1) <= 3 else "MEDIUM")
        concepts.append(Concept(name, freq, int(mf.get(name, 0)), parent, rel, facets, amb))
    return concepts, pd.DataFrame(rejects).sort_values("recipe_freq", ascending=False) if rejects else \
        pd.DataFrame(columns=["canonical", "recipe_freq", "reason"])


def build_aliases(m: pd.DataFrame, known: set[str]) -> list[AliasRow]:
    pairs = Counter(zip(m["ingredient_normalized"].str.lower().str.strip(), m["ingredient_canonical"]))
    by_surface: dict[str, Counter] = defaultdict(Counter)
    for (surf, canon), c in pairs.items():
        if canon in known:
            by_surface[surf][canon] += c
    out = []
    for surf, cands in by_surface.items():
        total = sum(cands.values())
        top, top_c = cands.most_common(1)[0]
        if len(cands) > 1 and top_c / total < 0.9:
            out.append(AliasRow(surf, None, tuple(c for c, _ in cands.most_common()), total, "AMBIGUOUS",
                                "UNRESOLVED"))
            continue
        if surf == top:
            atype, band = "SYNONYM", "EXACT"
        elif " ".join(_singular(w) for w in surf.split()) == top:
            atype, band = "PLURAL", "HIGH"
        elif surf.replace("-", " ") == top.replace("-", " "):
            atype, band = "SPELLING", "HIGH"
        else:
            atype, band = "SYNONYM", "MEDIUM"
        out.append(AliasRow(surf, top, tuple(cands), total, atype, band))
    return out


def coverage_curve(m: pd.DataFrame, concepts: list[Concept]) -> pd.DataFrame:
    total = len(m)
    counts = m["ingredient_canonical"].value_counts()
    in_reg = {c.name for c in concepts}
    rows, cum = [], 0
    for rank, (name, c) in enumerate(counts.items(), 1):
        cum += c
        rows.append({"rank": rank, "canonical": name, "mentions": int(c), "cum_share": cum / total,
                     "in_registry": name in in_reg})
    return pd.DataFrame(rows)
