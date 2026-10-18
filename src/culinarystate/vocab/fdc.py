"""USDA FoodData Central SR Legacy (2018-04, CC0) — crosswalk candidates and portion candidates.

Crosswalk output is CANDIDATE only: a human verifies ING<->FDC links before any POR- record built
from FDC portions may be used to turn a count/volume into grams (SSOT §235.3 Q1 AUTHORITATIVE_PORTION).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from culinarystate.quantity.units import lookup

SIZE_WORDS = ("extra large", "jumbo", "large", "medium", "small", "mini")
BRAND_HINT = re.compile(r"[A-Z][a-z]+['’]s\b|\b(KRAFT|PILLSBURY|KELLOGG|KEEBLER|NABISCO|GENERAL MILLS)\b|®|™",
                        re.IGNORECASE)


def _sing(w: str) -> str:
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith(("oes", "ches", "shes", "xes", "sses")):
        return w[:-2]
    if w.endswith("s") and not w.endswith(("ss", "us")) and len(w) > 3:
        return w[:-1]
    return w


def tokens(text: str) -> list[str]:
    return [_sing(w) for w in re.findall(r"[a-z]+", text.lower())]


def load_sr(sr_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = Path(sr_dir)
    food = pd.read_csv(d / "food.csv")[["fdc_id", "description", "food_category_id"]]
    cat = pd.read_csv(d / "food_category.csv").rename(columns={"id": "food_category_id", "description": "category"})
    food = food.merge(cat[["food_category_id", "category"]], on="food_category_id", how="left")
    por = pd.read_csv(d / "food_portion.csv")[["id", "fdc_id", "amount", "modifier", "gram_weight", "data_points"]]
    return food, por


@dataclass(frozen=True)
class PortionUnit:
    unit_key: str | None
    size: str | None
    note: str


def parse_portion_modifier(modifier: str) -> PortionUnit:
    m = (modifier or "").strip().lower()
    head, _, note = m.partition(",")
    head = re.sub(r"\(.*?\)", "", head).strip()
    for s in SIZE_WORDS:
        if head == s or head.startswith(s + " "):
            rest = head[len(s):].strip()
            u = lookup(rest.split()[0]) if rest else None
            return PortionUnit(u.key if u else None, s, note.strip())
    first = head.split()[0] if head else ""
    u = lookup(first) if first else None
    if u is None and len(head.split()) > 1:
        u = lookup(" ".join(head.split()[:2]))
    return PortionUnit(u.key if u else None, None, (head[len(first):].strip() + " " + note).strip())


NEUTRAL = {"raw", "fresh", "whole", "plain", "regular", "commercial", "cooking", "salad", "enriched", "ripe",
           "unenriched", "bleached", "unbleached", "all", "purpose", "mature", "uncooked", "year", "round", "average"}
CATEGORY_PREFIX = {"spices", "seeds", "nuts", "beverages", "snacks", "sweeteners", "candies", "soup", "cereals",
                   "leavening agents", "alcoholic beverage", "fish", "crustaceans", "mollusks", "game meat"}
# UK -> US / FDC naming (AI-drafted linguistic table; human review before relying on it)
UK_US = {
    "plain flour": ["all-purpose flour", "wheat flour white all-purpose"], "self-raising flour": ["self-rising flour"],
    "strong flour": ["bread flour"], "caster sugar": ["sugar granulated"], "golden caster sugar": ["sugar granulated"],
    "icing sugar": ["sugar powdered"], "double cream": ["cream heavy whipping"], "single cream": ["cream light"],
    "soured cream": ["sour cream"], "spring onion": ["onions spring scallions"], "coriander": ["coriander cilantro leaves"],
    "courgette": ["squash summer zucchini"], "aubergine": ["eggplant"], "rocket": ["arugula"], "prawn": ["shrimp"],
    "king prawn": ["shrimp"], "minced beef": ["beef ground"], "beef mince": ["beef ground"], "pork mince": ["pork ground"],
    "lamb mince": ["lamb ground"], "bicarbonate of soda": ["leavening agents baking soda"], "cornflour": ["cornstarch"],
    "chilli": ["peppers hot chili"], "red chilli": ["peppers hot chili red"], "green chilli": ["peppers hot chili green"],
    "chilli flakes": ["spices pepper red"], "mangetout": ["peas edible-podded"], "swede": ["rutabagas"],
    "beetroot": ["beets"], "treacle": ["molasses"], "streaky bacon": ["pork cured bacon"], "gammon": ["ham"],
    "natural yogurt": ["yogurt plain"], "red pepper": ["peppers sweet red"], "green pepper": ["peppers sweet green"],
    "yellow pepper": ["peppers sweet yellow"], "pepper": ["spices pepper black"], "black pepper": ["spices pepper black"],
    "vegetable oil": ["oil vegetable"], "sunflower oil": ["oil sunflower"], "rapeseed oil": ["oil canola"],
    "wine vinegar": ["vinegar red wine"], "chickpea": ["chickpeas garbanzo beans"], "broad bean": ["broadbeans fava beans"],
    "butter bean": ["lima beans"], "haricot bean": ["beans navy"], "jacket potato": ["potatoes baked"],
    "porridge oat": ["oats"], "sultana": ["raisins seedless golden"], "desiccated coconut": ["coconut meat dried"],
    "dark chocolate": ["chocolate dark"], "stock cube": ["soup bouillon cubes"], "chicken stock": ["soup stock chicken"],
    "vegetable stock": ["soup stock vegetable"], "tomato purée": ["tomato puree"], "tomato puree": ["tomato puree"],
}
FORM_SYN = {"powder": "ground", "unsalted": "without salt", "salted": "salted", "minced": "ground"}


def _variants(ing_name: str) -> list[str]:
    out = [ing_name] + UK_US.get(ing_name, [])
    words = ing_name.split()
    if words and words[-1] in FORM_SYN:
        out.append(" ".join(words[:-1] + [FORM_SYN[words[-1]]]))
    if words and words[0] in FORM_SYN:
        out.append(" ".join([FORM_SYN[words[0]]] + words[1:]))
    return list(dict.fromkeys(out))


def score_candidate(ing_name: str, description: str) -> tuple[float, str]:
    it = tokens(ing_name)
    if not it:
        return 0.0, "NONE"
    segs = [s.strip() for s in description.lower().split(",")]
    if len(segs) > 1 and segs[0] in CATEGORY_PREFIX:               # "Spices, cinnamon, ground"
        segs = segs[1:]
    dt = set(tokens(description))
    cover = sum(1 for t in it if t in dt) / len(it)
    seg0 = tokens(segs[0]) if segs else []
    seg01 = tokens(" ".join(segs[:2])) if segs else []
    exact = seg0 == it or sorted(seg01) == sorted(it)
    head = seg0[-1:] == it[-1:] or (seg0[:1] == it[-1:] and len(segs) > 1)   # "Oil, olive"
    early = set(tokens(" ".join(segs[:3])))
    extras = len(early - set(it) - NEUTRAL)
    s = cover + (0.35 if exact else 0.0) + (0.10 if head else 0.0)
    s += 0.10 if "raw" in segs and not any(w in it for w in ("cooked", "roast", "fried", "dried")) else 0.0
    s -= 0.04 * extras
    s -= 0.25 if BRAND_HINT.search(description) else 0.0
    band = ("HIGH" if cover == 1.0 and (exact or (head and extras <= 2)) else
            "MEDIUM" if cover == 1.0 else "LOW" if cover >= 0.5 else "NONE")
    return round(s, 4), band


@dataclass(frozen=True)
class Candidate:
    fdc_id: int
    description: str
    category: str
    score: float
    band: str
    via: str = ""


def candidates_for(ing_name: str, food: pd.DataFrame, index: dict[str, set[int]], k: int = 3) -> list[Candidate]:
    best: dict[int, Candidate] = {}
    for var in _variants(ing_name):
        it = tokens(var)
        pool: set[int] = set()
        for t in it:
            pool |= index.get(t, set())
        for r in food[food["fdc_id"].isin(pool)].itertuples(index=False):
            sc, band = score_candidate(var, r.description)
            if band == "NONE":
                continue
            c = Candidate(int(r.fdc_id), r.description, str(r.category), sc, band, "" if var == ing_name else var)
            if c.fdc_id not in best or c.score > best[c.fdc_id].score:
                best[c.fdc_id] = c
    ranked = sorted(best.values(), key=lambda c: (-c.score, len(c.description)))
    return ranked[:k]


def token_index(food: pd.DataFrame) -> dict[str, set[int]]:
    idx: dict[str, set[int]] = {}
    for r in food.itertuples(index=False):
        for t in set(tokens(r.description)):
            idx.setdefault(t, set()).add(int(r.fdc_id))
    return idx
