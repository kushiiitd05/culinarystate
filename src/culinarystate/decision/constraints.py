"""C5 goal/constraint parser: free text -> typed Constraints for the feasibility filter (SSOT §257B C5, §243.3).

Tools: "only have a pan and a microwave" -> closed-world available set; "no oven" / "don't have an oven" ->
unavailable; a plain "I have a pan" stays open-world (available_tools None). Time: first duration stated as a budget
(range -> lower end, conservative). Allergens: the eight FSSAI categories only (authority table); diet patterns
("vegan", "keto", "lactose") are returned UNRESOLVED, never mapped by guess. Ingredients: "no onion", "without
garlic", "out of coconut milk" -> longest phrase in the ingredient lexicon (feasibility also rejects descendants);
tools win over ingredients; unknown names are UNRESOLVED, function words ("no more than", "no time") ignored.
Raw text kept.
"""
from __future__ import annotations

import re

from culinarystate.evidence.conditions import extract_conditions
from culinarystate.process.tools import ALIAS_TO_TOOL, find_tools
from culinarystate.vocab.foodon import norm

from .feasibility import Constraints

VERSION = "constraints@0.2"
NEG_TOOL = re.compile(r"(?:\bno|\bwithout|\bdon'?t have|\bdo not have|\bhaven'?t got|\bnot have|\black|\bbroken)\s+"
                      r"(?:a|an|any|my|the)?\s*$", re.I)
TOOL_CTX = re.compile(r"(?:\bno|\bwithout|\bhave|\bhas|\bgot|\bown|\black|\bbroken|\bonly|\band|,)\s+"
                      r"(?:a\s+|an\s+|the\s+|my\s+|any\s+)?$", re.I)       # weak aliases ("microwave") as nouns
ONLY = re.compile(r"\bonly\s+(?:have|got|own)\b|\bjust\s+(?:have|a)\b|\ball i have is\b", re.I)
WORD_TIME = {"half an hour": 30.0, "an hour": 60.0, "a quarter of an hour": 15.0, "quarter of an hour": 15.0}
BUDGET_CUE = re.compile(r"\b(?:in|within|under|less than|max(?:imum)?|only have|have|got|done in|ready in)\b", re.I)
ALLERGEN_WORDS = {  # surface -> canonical allergen key in the authority table
    "gluten": "gluten", "wheat": "gluten", "milk": "milk", "dairy": "milk", "egg": "egg", "eggs": "egg",
    "nut": "nut", "nuts": "nut", "peanut": "nut", "peanuts": "nut", "tree nut": "nut", "tree nuts": "nut",
    "fish": "fish", "shellfish": "crustacean", "crustacean": "crustacean", "prawn": "crustacean",
    "prawns": "crustacean", "shrimp": "crustacean", "soy": "soy", "soya": "soy", "sulphite": "sulphite",
    "sulphites": "sulphite", "sulfite": "sulphite", "sulfites": "sulphite"}
ALLERGEN_CUE = (r"(?:(?P<w1>{w})[- ]free|\bno (?P<w2>{w})\b|\bwithout (?P<w3>{w})\b|allergic to (?P<w4>{w})\b|"
                r"\b(?:can'?t|cannot|don'?t) eat (?P<w5>{w})\b|\bavoid(?:ing)? (?P<w6>{w})\b)")
EXCL_CUE = re.compile(r"\b(?:no|without|don'?t have|do not have|(?:ran |run |i'?m )?out of|allergic to|can'?t eat|"
                      r"cannot eat|don'?t eat|avoid(?:ing)?|skip(?:ping)?|hold the)\s+(?:any |the |a |an |my )?"
                      r"(?=(?P<rest>[a-z][a-z' -]*))", re.I)      # lookahead: the phrase may hold the next cue
BOUNDARY = {"and", "or", "but", "please", "for", "in", "to", "because", "with", "at", "on", "so", "i", "i'm", "we", "if"}
FUNCTION = {"more", "less", "than", "time", "need", "longer", "way", "idea", "problem", "worries", "matter", "much",
            "one", "other", "extra", "added", "fancy", "special", "longer", "rush", "hurry", "thanks", "thank"}
UNRESOLVED_DIET = re.compile(r"\b(vegan|vegetarian|keto|paleo|halal|kosher|jain|lactose|low[- ]fodmap|diabetic)\b", re.I)


def _time_budget(text: str) -> float | None:
    low = text.lower()
    for phrase, mins in WORD_TIME.items():
        if phrase in low:
            return mins
    for d in extract_conditions(text)["durations"]:
        raw = d.get("raw") or ""
        pos = low.find(raw.lower())
        if pos >= 0 and (BUDGET_CUE.search(low[max(0, pos - 25):pos]) or re.search(r"\bmax\b", low[pos:pos + len(raw) + 6])):
            return d["value"] if d["status"] == "MEASURED" else d["low"]
    return None


TOOL_NAMES = {norm(a) for a in ALIAS_TO_TOOL}


def _exclusions(text: str, names: dict) -> tuple[set, list]:
    found, unresolved = set(), []
    for m in EXCL_CUE.finditer(text):
        words = []
        for w in m["rest"].lower().split():
            if w in BOUNDARY or len(words) == 4:
                break
            words.append(w)
        is_tool = any(norm(" ".join(words[:n])) in TOOL_NAMES for n in range(1, len(words) + 1))
        if not words or words[0] in FUNCTION or is_tool:
            continue
        hit = next((names.get(p) or names.get(norm(p)) for n in range(len(words), 0, -1)
                    if (names.get(p := " ".join(words[:n])) or names.get(norm(p)))), None)
        if hit:
            found.add(hit)
        elif words[0] not in ALLERGEN_WORDS:
            unresolved.append(" ".join(words))
    return found, unresolved


def parse_constraints(text: str, tool_ids: dict, allergen_ids: dict,
                      ingredient_names: dict | None = None) -> tuple[Constraints, dict]:
    """tool_ids: canonical tool name -> TOOL id; allergen_ids: canonical allergen key -> ALLERGEN id;
    ingredient_names: normalised ingredient name/alias -> ING id (None: no ingredient exclusions parsed)."""
    text = text or ""
    affirmed, negated, unknown_tools = set(), set(), []
    for pos, tool, _ in find_tools(text, TOOL_CTX):
        tid = tool_ids.get(tool)
        if not tid:
            unknown_tools.append(tool)
            continue
        (negated if NEG_TOOL.search(text[max(0, pos - 22):pos]) else affirmed).add(tid)
    closed = bool(ONLY.search(text))
    words = "|".join(sorted((re.escape(w) for w in ALLERGEN_WORDS), key=len, reverse=True))
    excluded = set()
    for m in re.finditer(ALLERGEN_CUE.format(w=words), text, re.I):
        w = next(g for g in m.groups() if g)
        key = ALLERGEN_WORDS[w.lower()]
        if key in allergen_ids:
            excluded.add(allergen_ids[key])
    unresolved = sorted({m.group(1).lower().replace(" ", "-") for m in UNRESOLVED_DIET.finditer(text)})
    ings, unresolved_ings = _exclusions(text, ingredient_names) if ingredient_names else (set(), [])
    c = Constraints(available_tools=frozenset(affirmed - negated) if closed else None,
                    time_budget_min=_time_budget(text), excluded_allergens=frozenset(excluded),
                    unavailable_tools=frozenset(negated), excluded_ingredients=frozenset(ings))
    return c, {"version": VERSION, "raw": text, "closed_world_tools": closed, "unresolved": unresolved,
               "tools_not_in_registry": unknown_tools, "unresolved_exclusions": unresolved_ings}


def load_constraint_lexicons(store) -> tuple[dict, dict, dict]:
    tools = {t["canonical_name"]: t["id"] for t in store.all_latest("TOOL") if t["status"] == "ACTIVE"}
    keys = {"cereals containing gluten": "gluten", "crustacean": "crustacean", "milk": "milk", "egg": "egg",
            "fish": "fish", "nut": "nut", "soy": "soy", "sulphite": "sulphite"}
    allergens = {keys[a["allergen_name"].lower()]: a["id"] for a in store.all_latest("ALLERGEN")
                 if a["allergen_name"].lower() in keys}
    names = {norm(i["canonical_name"]): i["id"] for i in store.all_latest("ING") if i["status"] == "ACTIVE"}
    for a in store.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    return tools, allergens, names
