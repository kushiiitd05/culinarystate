"""Step 1: deterministic lexical ING -> USDA SR Legacy matcher (AI_DRAFTED, never auto-ACCEPTED).

Method (no model, no network, no randomness; ties broken by shorter description then fdc_id):
- SR descriptions are split on commas into segments (SR puts the head noun first: "Onions, raw",
  "Oil, olive, salad or cooking"). Category prefixes such as "Spices," are skipped for identity.
- Words that name a processing state (raw, cooked, canned, dried, frozen, salted, ...) are FACETS, not identity: they
  are removed from the identity token sets of both sides and compared separately.
- Score = 0.45 coverage (IDF-weighted share of the ING identity tokens found in the SR description; early
  segments count fully, later ones half) + 0.25 head-noun hit (last ING token in SR segment 0 / 1 / later)
  + 0.20 precision of the first two SR segments (extra early words lower it) + 0.10 facet agreement + 0.05
  ING-category agreement - penalties (brand, baby / fast / restaurant / meal categories).
- Synonym variants (UK -> US names, AI-drafted table) are scored separately; the best variant wins and is named.
- Bands: HIGH (all tokens covered, head noun in segment 0/1, clear margin over the next candidate),
  MEDIUM (most tokens covered with the head noun), LOW (weak), NONE (no candidate). Bands are rule-defined and
  NOT calibrated against any human-verified set (none exists yet).
"""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from .sr_legacy import SRLegacy
from .text import STOP, singular, strip_marks, tokens

MATCHER_VERSION = "lotstate-ing-sr-match-0.1.0-draft"
STATUS = "AI_DRAFTED"
GENERIC_HEAD_DOCS = 25   # a one-word ING name that heads >= this many SR foods (cheese, beef, ...) is capped at MEDIUM
GENERIC_NEAR_TIES = 6   # >= this many SR foods within 0.10 of the best score: generic ING name, capped at MEDIUM

FACET_WORDS: dict[str, str] = {
    "raw": "raw", "fresh": "raw", "uncooked": "raw", "unprepared": "raw",
    "cooked": "cooked", "boiled": "cooked", "baked": "cooked", "steamed": "cooked", "roasted": "cooked",
    "grilled": "cooked", "fried": "cooked", "braised": "cooked", "stewed": "cooked", "broiled": "cooked",
    "canned": "canned", "tinned": "canned", "dried": "dried", "dehydrated": "dried", "frozen": "frozen",
    "pickled": "pickled", "smoked": "smoked", "cured": "cured", "salted": "salted", "unsalted": "unsalted",
}
PROCESSED_FACETS = frozenset({"cooked", "canned", "dried", "frozen", "pickled", "smoked", "cured"})
# words dropped from ING names before matching (preparation / size / marketing words, not identity)
IGNORE = frozenset({"chopped", "sliced", "diced", "minced", "grated", "shredded", "crushed", "peeled", "large", "small",
                    "medium", "organic", "free", "range", "good", "quality", "ready", "ripe", "plain", "whole", "extra",
                    "finely", "roughly", "bought", "store", "homemade", "fine", "thick", "thin", "big", "mini", "baby",
                    "natural", "pure", "best", "golden", "light", "dark"})
# identity words that IGNORE would wrongly drop for specific ING names are kept through the synonym phrases below
CATEGORY_PREFIX = frozenset({"spice", "seed", "nut", "beverage", "snack", "sweetener", "candy", "soup", "cereal",
                             "leavening agent", "alcoholic beverage", "fish", "crustacean", "mollusk", "game meat",
                             "babyfood", "usda commodity", "fast food", "restaurant", "candies"})
CATEGORY_PENALTY = {"Baby Foods": 0.35, "Fast Foods": 0.35, "Meals": 0.30, "Restaurant Foods": 0.35,
                    "American Indian/Alaska Native Foods": 0.25, "Snacks": 0.10, "Branded Food Products Database": 1.0,
                    "Quality Control Materials": 1.0, "Sausages and Luncheon Meats": 0.0}
ING_CATEGORY_TO_SR = {
    "VEGETABLE": {"Vegetables and Vegetable Products"}, "FRUIT": {"Fruits and Fruit Juices"},
    "CEREAL": {"Cereal Grains and Pasta", "Baked Products", "Breakfast Cereals"}, "HERB_SPICE": {"Spices and Herbs"},
    "DAIRY": {"Dairy and Egg Products"}, "EGG": {"Dairy and Egg Products"},
    "NUT_SEED": {"Nut and Seed Products"}, "BEVERAGE": {"Beverages", "Alcoholic Beverages"},
    "MEAT": {"Beef Products", "Pork Products", "Poultry Products", "Lamb, Veal, and Game Products",
             "Sausages and Luncheon Meats"}, "LEGUME": {"Legumes and Legume Products"},
    "SEAFOOD": {"Finfish and Shellfish Products"}, "FAT_OIL": {"Fats and Oils"}, "SWEETENER": {"Sweets"},
    "CONDIMENT": {"Spices and Herbs", "Soups, Sauces, and Gravies", "Vegetables and Vegetable Products"},
}
BRAND_HINT = re.compile(r"[A-Z][a-z]+['’]s\b|\b(KRAFT|PILLSBURY|KELLOGG|KEEBLER|NABISCO|GENERAL MILLS|CAMPBELL|"
                        r"GERBER|HEINZ|NESTLE|MCDONALD)\b|®|™")

# token-level UK -> US names applied to any ING name (AI-drafted; a human should review)
TOKEN_MAP = {"courgette": "zucchini", "aubergine": "eggplant", "rocket": "arugula", "prawn": "shrimp", "mince": "ground",
             "minced": "ground", "caster": "granulated", "icing": "powdered", "cornflour": "cornstarch",
             "beetroot": "beet", "swede": "rutabaga", "chilli": "chili", "yoghurt": "yogurt", "coriander": "cilantro",
             "spring": "spring", "pepper": "pepper", "bicarbonate": "baking", "treacle": "molasses",
             "sultana": "raisin", "gammon": "ham", "mangetout": "snow", "chickpea": "chickpea"}
# phrase variants in SR word order (AI-drafted). Extends vocab.fdc.UK_US, which is imported when available.
EXTRA_PHRASES: dict[str, list[str]] = {
    "egg": ["egg whole raw fresh"], "eggs": ["egg whole raw fresh"], "butter": ["butter salted"],
    "unsalted butter": ["butter without salt"], "salted butter": ["butter salted"],
    "milk": ["milk whole 3.25% milkfat"], "whole milk": ["milk whole 3.25% milkfat"],
    "semi-skimmed milk": ["milk reduced fat 2% milkfat"], "skimmed milk": ["milk nonfat fluid"],
    "olive oil": ["oil olive salad cooking"], "extra virgin olive oil": ["oil olive salad cooking"],
    "sugar": ["sugars granulated"], "granulated sugar": ["sugars granulated"], "brown sugar": ["sugars brown"],
    "soft brown sugar": ["sugars brown"], "light brown sugar": ["sugars brown"], "dark brown sugar": ["sugars brown"],
    "demerara sugar": ["sugars brown"], "muscovado sugar": ["sugars brown"],
    "plain flour": ["wheat flour white all-purpose enriched bleached"],
    "flour": ["wheat flour white all-purpose enriched bleached"],
    "self-raising flour": ["wheat flour white self-rising enriched"],
    "strong flour": ["wheat flour white bread"], "bread flour": ["wheat flour white bread"],
    "wholemeal flour": ["wheat flour whole-grain"], "salt": ["salt table"], "sea salt": ["salt table"],
    "black pepper": ["spices pepper black"], "pepper": ["spices pepper black"],
    "garlic": ["garlic raw"], "garlic clove": ["garlic raw"], "onion": ["onions raw"], "red onion": ["onions raw"],
    "white onion": ["onions raw"], "shallot": ["shallots raw"], "tomato": ["tomatoes red ripe raw year round average"],
    "tomatoes": ["tomatoes red ripe raw year round average"], "cherry tomato": ["tomatoes red ripe raw"],
    "potato": ["potatoes flesh and skin raw"], "carrot": ["carrots raw"], "lemon": ["lemons raw without peel"],
    "lime": ["limes raw"], "orange": ["oranges raw all commercial varieties"],
    "lemon juice": ["lemon juice raw"], "lime juice": ["lime juice raw"], "orange juice": ["orange juice raw"],
    "double cream": ["cream fluid heavy whipping"], "single cream": ["cream fluid light"],
    "cream": ["cream fluid heavy whipping"], "whipping cream": ["cream fluid heavy whipping"],
    "sour cream": ["cream sour cultured"], "soured cream": ["cream sour cultured"],
    "yogurt": ["yogurt plain whole milk"], "natural yogurt": ["yogurt plain whole milk"],
    "greek yogurt": ["yogurt greek plain"], "cheddar": ["cheese cheddar"], "cheddar cheese": ["cheese cheddar"],
    "parmesan": ["cheese parmesan grated"], "parmesan cheese": ["cheese parmesan grated"],
    "mozzarella": ["cheese mozzarella whole milk"], "feta": ["cheese feta"], "ricotta": ["cheese ricotta whole milk"],
    "vegetable oil": ["oil vegetable soybean refined"], "sunflower oil": ["oil sunflower"],
    "rapeseed oil": ["oil canola"], "baking powder": ["leavening agents baking powder double-acting"],
    "baking soda": ["leavening agents baking soda"], "bicarbonate of soda": ["leavening agents baking soda"],
    "yeast": ["leavening agents yeast baker's active dry"], "honey": ["honey"],
    "cinnamon": ["spices cinnamon ground"], "ginger": ["ginger root raw"], "ground ginger": ["spices ginger ground"],
    "parsley": ["parsley fresh"], "basil": ["spices basil fresh"], "thyme": ["spices thyme fresh"],
    "mint": ["spearmint fresh"], "cilantro": ["coriander cilantro leaves raw"], "coriander": ["coriander cilantro leaves raw"],
    "vanilla extract": ["vanilla extract"], "vinegar": ["vinegar distilled"], "wine vinegar": ["vinegar red wine"],
    "water": ["beverages water tap drinking"], "chicken breast": ["chicken broiler or fryers breast skinless boneless meat only raw"],
    "chicken": ["chicken broilers or fryers meat and skin raw"], "chicken stock": ["soup stock chicken home-prepared"],
    "vegetable stock": ["soup stock vegetable"], "beef stock": ["soup stock beef home-prepared"],
    "rice": ["rice white long-grain regular raw enriched"], "pasta": ["pasta dry enriched"],
    "spaghetti": ["pasta dry enriched"], "oats": ["oats"],
    "porridge oats": ["cereals oats regular and quick not fortified dry"], "cornstarch": ["cornstarch"],
    "cocoa powder": ["cocoa dry powder unsweetened"], "dark chocolate": ["chocolate dark 70-85% cacao solids"],
    "almond": ["nuts almonds"], "walnut": ["nuts walnuts english"], "peanut": ["peanuts all types raw"],
    "soy sauce": ["soy sauce made from soy and wheat shoyu"], "mustard": ["mustard prepared yellow"],
    "dijon mustard": ["mustard prepared yellow"], "tomato puree": ["tomato products canned paste"],
    "tomato paste": ["tomato products canned paste"], "bacon": ["pork cured bacon unprepared"],
    "streaky bacon": ["pork cured bacon unprepared"], "ham": ["ham sliced regular"], "mushroom": ["mushrooms white raw"],
    "button mushroom": ["mushrooms white raw"], "spinach": ["spinach raw"], "broccoli": ["broccoli raw"],
    "cabbage": ["cabbage raw"], "celery": ["celery raw"], "cucumber": ["cucumber with peel raw"],
    "apple": ["apples raw with skin"], "banana": ["bananas raw"], "raisin": ["raisins seedless"],
    "coconut milk": ["nuts coconut milk canned"], "chickpea": ["chickpeas garbanzo beans mature seeds raw"],
    "lentil": ["lentils raw"], "red wine": ["alcoholic beverage wine table red"],
    "white wine": ["alcoholic beverage wine table white"], "ketchup": ["catsup"], "tomato ketchup": ["catsup"],
    "courgette": ["squash summer zucchini includes skin raw"], "zucchini": ["squash summer zucchini includes skin raw"],
    "coriander leaf": ["coriander cilantro leaves raw"], "coriander leaves": ["coriander cilantro leaves raw"],
    "dill": ["dill weed fresh"], "oat": ["oats"], "bread": ["bread white commercially prepared"],
    "sesame seed": ["seeds sesame seeds whole dried"], "cornmeal": ["cornmeal whole-grain yellow"],
    "chocolate": ["candies semisweet chocolate"], "chocolate chips": ["candies semisweet chocolate"],
    "chocolate chip": ["candies semisweet chocolate"], "chile flakes": ["spices pepper red or cayenne"],
    "chili flakes": ["spices pepper red or cayenne"], "red pepper flakes": ["spices pepper red or cayenne"],
    "sherry": ["alcoholic beverage wine dessert dry"],
    "white sugar": ["sugars granulated"], "granulated white sugar": ["sugars granulated"],
    "monterey jack cheese": ["cheese monterey"], "monterey jack": ["cheese monterey"], "peas": ["peas green raw"], "pea": ["peas green raw"], "red lentil": ["lentils pink or red raw"],
}


def _norm_name(s: str) -> str:
    return " ".join(tokens(s))


@dataclass(frozen=True)
class SRDoc:
    fdc_id: int
    description: str
    category: str
    seg_ids: tuple[frozenset, ...]   # identity tokens per segment (category prefix removed)
    early: frozenset
    allid: frozenset
    core_all: frozenset              # allid without parenthetical words
    facets: frozenset
    penalty: float
    seg0: frozenset = frozenset()


@dataclass(frozen=True)
class Candidate:
    fdc_id: int
    description: str
    category: str
    score: float
    coverage: float
    head: str
    precision: float
    facet: str
    via: str
    reason: str


def _facets_of(text: str) -> set[str]:
    low = strip_marks(text).lower()
    out = {FACET_WORDS[singular(w) if singular(w) in FACET_WORDS else w] for w in re.findall(r"[a-z]+", low)
           if w in FACET_WORDS or singular(w) in FACET_WORDS}
    if re.search(r"\bwithout salt\b|\bno salt\b|\bunsalted\b", low):
        out.discard("salted")
        out.add("unsalted")
    return out


def _id_tokens(text: str, ignore: bool = False) -> list[str]:
    """Identity tokens: no stop words, no facet words; ING names also drop IGNORE words (SR descriptions keep them)."""
    return [t for t in tokens(text) if t not in STOP and t not in FACET_WORDS and len(t) > 1
            and not (ignore and t in IGNORE)]


def _strip_category(toks: list[str]) -> list[str]:
    """Drop a leading SR category word ("spices", "alcoholic beverage") from a phrase variant: SR docs skip it too."""
    for n in (2, 1):
        if len(toks) > n and " ".join(toks[:n]) in CATEGORY_PREFIX:
            return toks[n:]
    return toks


class Matcher:
    def __init__(self, sr: SRLegacy, phrases: Mapping[str, Sequence[str]] | None = None):
        self.sr = sr
        self.docs: dict[int, SRDoc] = {}
        for f in sr.foods.values():
            cat_pen = CATEGORY_PENALTY.get(f.category, 0.0) + (0.25 if BRAND_HINT.search(f.description) else 0.0)
            segs = [seg for seg in re.sub(r"\([^)]*\)", " ", f.description).split(",") if seg.strip()]
            ids = [frozenset(_id_tokens(s)) for s in segs]
            paren = frozenset(t for m in re.findall(r"\(([^)]*)\)", f.description) for t in _id_tokens(m))
            first = " ".join(tokens(segs[0])) if segs else ""
            if len(segs) > 1 and first in CATEGORY_PREFIX:
                ids = ids[1:]
            ids = list(ids) or [frozenset()]
            early = frozenset().union(*ids[:2])
            core = frozenset().union(*ids)
            if paren:
                ids.append(paren)          # parenthetical words (e.g. "(cilantro)") count as late-segment words
            allid = frozenset().union(*ids)
            self.docs[f.fdc_id] = SRDoc(f.fdc_id, f.description, f.category, tuple(ids), early, allid, core,
                                        frozenset(_facets_of(f.description)), cat_pen, ids[0])
        df: dict[str, int] = {}
        for d in self.docs.values():
            for t in d.allid:
                df[t] = df.get(t, 0) + 1
        n = len(self.docs)
        self.idf = {t: math.log((n - c + 0.5) / (c + 0.5) + 1.0) for t, c in df.items()}
        self.idf_unseen = math.log(n + 1.0)
        self.index: dict[str, set[int]] = {}
        for d in self.docs.values():
            for t in d.allid:
                self.index.setdefault(t, set()).add(d.fdc_id)
        merged: dict[str, list[str]] = {}
        try:
            from culinarystate.vocab.fdc import UK_US
            merged.update({_norm_name(k): list(v) for k, v in UK_US.items()})
        except ImportError:  # pragma: no cover
            pass
        for k, v in (phrases or EXTRA_PHRASES).items():
            merged[_norm_name(k)] = list(v)
        self.phrases = merged
        self.seg0_count: dict[str, int] = {}
        for d in self.docs.values():
            for t in d.seg0:
                self.seg0_count[t] = self.seg0_count.get(t, 0) + 1

    # ---------------------------------------------------------------- variants
    def variants(self, name: str) -> list[tuple[str, list[str], set[str], str, set[str]]]:
        """[(label, identity tokens, head candidates, kind, facets)] for the ING name and its synonym variants.
        A phrase variant is written in SR word order; facet words inside it (raw, cooked, ...) are its facets."""
        toks_all = tokens(name)
        out: list[tuple[str, list[str], set[str], str, set[str]]] = []
        ing_facets = {FACET_WORDS[t] for t in toks_all if t in FACET_WORDS}
        base = _id_tokens(name, ignore=True)
        if base:
            out.append(("name", base, {base[-1]}, "name", ing_facets))
        mapped = [TOKEN_MAP.get(t, t) for t in base]
        if mapped != base and mapped:
            out.append(("token_map", mapped, {mapped[-1]}, "name", ing_facets))
        key = " ".join(toks_all)
        for ph in self.phrases.get(key, []):
            pt = _strip_category(_id_tokens(ph))
            if pt:
                pf = {FACET_WORDS[t] for t in tokens(ph) if t in FACET_WORDS} | ing_facets
                out.append((f"phrase:{ph}", pt, {pt[0], pt[-1]}, "phrase", pf))
        if not out:
            out.append(("name", [], set(), "name", ing_facets))
        return out

    # ---------------------------------------------------------------- scoring
    def _w(self, t: str) -> float:
        return self.idf.get(t, self.idf_unseen)

    def score_doc(self, d: SRDoc, q: list[str], heads: set[str], ing_facets: set[str], ing_cat: str | None,
                  kind: str = "name"):
        qset = set(q)
        qw = sum(self._w(t) for t in qset)
        if not qset or qw <= 0:
            return None
        cov_early = sum(self._w(t) for t in qset & d.early) / qw
        cov_all = sum(self._w(t) for t in qset & d.allid) / qw
        cov = cov_early + 0.5 * (cov_all - cov_early)
        if cov <= 0:
            return None
        aw = sum(self._w(t) for t in d.core_all)
        prec_all = (sum(self._w(t) for t in qset & d.core_all) / aw) if aw > 0 else 0.0
        head_s, head_where = 0.0, "none"
        for i, seg in enumerate(d.seg_ids):
            if heads & seg:
                head_s, head_where = (1.0 if i == 0 else 0.8 if i == 1 else 0.4), f"seg{min(i, 2)}"
                break
        ew = sum(self._w(t) for t in d.early)
        prec = (sum(self._w(t) for t in qset & d.early) / ew) if ew > 0 else 0.0
        if ing_facets:
            hit = ing_facets & set(d.facets)
            doc_proc = set(d.facets) & PROCESSED_FACETS
            conflict = bool((ing_facets & PROCESSED_FACETS) and not hit and (doc_proc or "raw" in d.facets))
            if "salted" in ing_facets and "unsalted" in d.facets or "unsalted" in ing_facets and "salted" in d.facets:
                conflict = True
            if conflict:
                facet_s, facet_tag = 0.0, "facet_conflict"
            elif hit == ing_facets:
                extra = bool(doc_proc - ing_facets)
                facet_s, facet_tag = (0.8, "facet_match_extra_processing") if extra else (1.0, "facet_match")
            else:
                facet_s, facet_tag = (0.4, "facet_partial") if hit else (0.3, "facet_absent")
        else:
            proc = set(d.facets) & PROCESSED_FACETS
            facet_s, facet_tag = (1.0, "raw_default") if "raw" in d.facets and not proc else \
                (0.6, "no_facet") if not proc else (0.0, "processed_default_penalty")
        cat_s = 1.0 if ing_cat and d.category in ING_CATEGORY_TO_SR.get(ing_cat, ()) else 0.0
        score = 0.45 * cov + 0.25 * head_s + 0.20 * prec + 0.10 * facet_s + 0.05 * cat_s - d.penalty
        if facet_tag == "facet_conflict":
            score -= 0.10
        exact = kind == "phrase" and cov_all >= 0.999 and prec >= 0.999 and prec_all >= 0.75
        if exact:
            score += 0.12 + 0.45 * (1.0 - cov)  # a curated phrase variant that reproduces the SR entry: full coverage
            cov = 1.0
        reason = ("phrase_exact;" if exact else "") + f"cov={cov:.2f};head={head_where};prec={prec:.2f};{facet_tag}" + (";cat_ok" if cat_s else "") + \
                 (f";pen={d.penalty:.2f}" if d.penalty else "")
        return score, cov, head_where, prec, facet_tag, reason

    def _rank(self, name: str, ing_category: str | None = None) -> list[Candidate]:
        best: dict[int, Candidate] = {}
        for label, q, heads, kind, ing_facets in self.variants(name):
            pool: set[int] = set()
            for t in set(q):
                pool |= self.index.get(t, set())
            for fid in pool:
                d = self.docs[fid]
                res = self.score_doc(d, q, heads, ing_facets, ing_category, kind)
                if res is None:
                    continue
                score, cov, head_where, prec, facet_tag, reason = res
                cur = best.get(fid)
                if cur is None or score > cur.score:
                    best[fid] = Candidate(fid, d.description, d.category, round(score, 4), round(cov, 4), head_where,
                                          round(prec, 4), facet_tag, label, reason)
        return sorted(best.values(), key=lambda c: (-c.score, len(c.description), c.fdc_id))

    def candidates(self, name: str, ing_category: str | None = None, k: int = 3) -> list[Candidate]:
        return self._rank(name, ing_category)[:k + 1]

    def _query_heads(self, name: str) -> set[str]:
        base = _id_tokens(name, ignore=True)
        return {base[-1]} if len(base) == 1 else set()      # only a one-word ING name can be a bare head noun

    def match(self, name: str, ing_category: str | None = None, k: int = 3) -> list[dict]:
        """Top-k candidates with band and reason; element 0 is the proposal. Empty list = NO_CANDIDATE."""
        ranked = self._rank(name, ing_category)
        near = sum(1 for c in ranked if c.score >= ranked[0].score - 0.10) if ranked else 0
        cands = ranked[:k + 1]
        out = []
        for i, c in enumerate(cands[:k]):
            nxt = cands[i + 1].score if i + 1 < len(cands) else 0.0
            margin = (c.score - nxt) if i == 0 else 0.0     # only the proposal (rank 1) can be HIGH
            band = band_of(c, margin)
            reason = c.reason + f";margin={margin:.2f}"
            generic = max((self.seg0_count.get(t, 0) for t in self._query_heads(name)), default=0)
            if (i == 0 and band == "HIGH" and not c.reason.startswith("phrase_exact")
                    and (near >= GENERIC_NEAR_TIES or generic >= GENERIC_HEAD_DOCS)):
                band, reason = "MEDIUM", reason + f";GENERIC_HEAD near={near} seg0_docs={generic}"
            out.append({"rank": i + 1, "fdc_id": c.fdc_id, "description": c.description, "category": c.category,
                        "score": c.score, "band": band, "margin": round(margin, 4), "via": c.via, "reason": reason})
        return out


def band_of(c: Candidate, margin: float) -> str:
    head_ok = c.head in ("seg0", "seg1")
    if c.score >= 0.80 and c.coverage >= 0.99 and head_ok and c.precision >= 0.5 and margin >= 0.03:
        return "HIGH"
    if c.score >= 0.55 and c.coverage >= 0.70 and c.head != "none":
        return "MEDIUM"
    if c.score >= 0.30:
        return "LOW"
    return "LOW" if c.score > 0 else "NONE"


# ---------------------------------------------------------------- ING ledger (read-only)
def latest_ing(ing_jsonl: Path, *, active_only: bool = True) -> list[dict]:
    latest: dict[str, dict] = {}
    with open(ing_jsonl, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            prev = latest.get(r["id"])
            if prev is None or int(r.get("version") or 0) >= int(prev.get("version") or 0):
                latest[r["id"]] = r
    rows = list(latest.values())
    if active_only:
        rows = [r for r in rows if r.get("status") == "ACTIVE"]
    return sorted(rows, key=lambda r: r["id"])


def match_ing_rows(matcher: Matcher, ing_rows: Iterable[Mapping], k: int = 3) -> list[dict]:
    """Flat draft rows (one per ING x rank). status is always AI_DRAFTED; human_decision stays blank."""
    out: list[dict] = []
    for r in ing_rows:
        cands = matcher.match(r["canonical_name"], r.get("category"), k)
        base = {"ing_id": r["id"], "canonical_name": r["canonical_name"], "ing_status": r["status"],
                "ing_category": r.get("category") or "", "ledger_corpus_frequency": r.get("corpus_frequency") or 0}
        if not cands:
            out.append({**base, "rank": 0, "fdc_id": "", "sr_description": "", "sr_category": "", "score": "",
                        "confidence_band": "NONE", "via": "", "reason": "NO_CANDIDATE", "status": STATUS,
                        "human_decision": ""})
        for c in cands:
            out.append({**base, "rank": c["rank"], "fdc_id": c["fdc_id"], "sr_description": c["description"],
                        "sr_category": c["category"], "score": c["score"], "confidence_band": c["band"],
                        "via": c["via"], "reason": c["reason"], "status": STATUS, "human_decision": ""})
    return out


def top1_table(draft_rows: Iterable[Mapping]) -> dict[str, dict]:
    """ING id -> rank-1 row (fdc_id int, band) for the grams / composition layers."""
    out: dict[str, dict] = {}
    for r in draft_rows:
        if int(r["rank"] or 0) == 1 and r["fdc_id"] != "":
            out[r["ing_id"]] = {"fdc_id": int(r["fdc_id"]), "band": r["confidence_band"], "score": float(r["score"])}
    return out
