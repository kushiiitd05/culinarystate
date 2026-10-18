"""Tool / utensil / appliance / material vocabulary v1 (TOOL- ledger input).

Curated from BBC corpus mining (heads after "in/into/on/with/using a …", 39,540 steps) plus Indian kitchen
equipment (tawa, kadai, pressure cooker…) that the BBC corpus under-represents. Material and safety
properties (reactivity, max temperature) are NOT asserted here — they need authority/evidence (WARN layer).
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Tool:
    canonical: str
    category: str              # COOKWARE APPLIANCE UTENSIL VESSEL HEAT_SOURCE MEASURE OTHER
    aliases: tuple[str, ...]
    material: str | None = None


T = Tool
TOOLS: tuple[Tool, ...] = (
    # heat sources / appliances
    T("oven", "HEAT_SOURCE", ("oven", "fan oven", "conventional oven")), T("hob", "HEAT_SOURCE", ("hob", "stovetop", "stove", "burner")),
    T("grill", "HEAT_SOURCE", ("grill", "grill pan")), T("barbecue", "HEAT_SOURCE", ("barbecue", "bbq")),
    T("microwave", "APPLIANCE", ("microwave",)), T("fridge", "APPLIANCE", ("fridge", "refrigerator")),
    T("freezer", "APPLIANCE", ("freezer",)), T("food processor", "APPLIANCE", ("food processor", "processor", "mini chopper")),
    T("blender", "APPLIANCE", ("blender", "liquidiser", "stick blender", "hand blender", "nutribullet")),
    T("electric whisk", "APPLIANCE", ("electric whisk", "hand mixer", "electric beaters")),
    T("stand mixer", "APPLIANCE", ("stand mixer", "tabletop mixer", "mixer")), T("slow cooker", "APPLIANCE", ("slow cooker",)),
    T("pressure cooker", "APPLIANCE", ("pressure cooker", "instant pot", "cooker")), T("air fryer", "APPLIANCE", ("air fryer", "air-fryer")),
    T("deep-fat fryer", "APPLIANCE", ("deep-fat fryer", "deep fryer", "deep fat fryer")), T("toaster", "APPLIANCE", ("toaster",)),
    T("ice cream maker", "APPLIANCE", ("ice cream maker",)), T("spice grinder", "APPLIANCE", ("spice grinder", "coffee grinder")),
    # cookware
    T("frying pan", "COOKWARE", ("frying pan", "skillet", "non-stick pan", "non-stick frying pan")),
    T("saucepan", "COOKWARE", ("saucepan", "pan", "large pan", "small pan", "pot", "stockpot", "stock pot")),
    T("griddle pan", "COOKWARE", ("griddle pan", "griddle", "ridged griddle pan")),
    T("wok", "COOKWARE", ("wok",)), T("casserole", "COOKWARE", ("casserole", "casserole dish", "dutch oven", "flameproof casserole")),
    T("roasting tin", "COOKWARE", ("roasting tin", "roasting tray", "roasting pan")),
    T("baking tray", "COOKWARE", ("baking tray", "baking sheet", "oven tray", "sheet")),
    T("baking dish", "COOKWARE", ("baking dish", "ovenproof dish", "gratin dish", "pie dish", "dish")),
    T("cake tin", "COOKWARE", ("cake tin", "sandwich tin", "springform tin", "loose-bottomed tin", "tin")),
    T("loaf tin", "COOKWARE", ("loaf tin",)), T("muffin tin", "COOKWARE", ("muffin tin", "cupcake tin", "bun tin", "muffin tray")),
    T("tart tin", "COOKWARE", ("tart tin", "flan tin", "tart case")), T("ramekin", "COOKWARE", ("ramekin", "ramekins")),
    T("pudding basin", "COOKWARE", ("pudding basin", "basin")), T("steamer", "COOKWARE", ("steamer", "steamer basket", "bamboo steamer")),
    T("tawa", "COOKWARE", ("tawa", "tava")), T("kadai", "COOKWARE", ("kadai", "kadhai", "karahi")),
    T("handi", "COOKWARE", ("handi",)), T("tadka pan", "COOKWARE", ("tadka pan", "tempering pan")),
    # vessels / containers
    T("bowl", "VESSEL", ("bowl", "mixing bowl", "large bowl", "small bowl", "heatproof bowl", "separate bowl")),
    T("jug", "VESSEL", ("jug", "measuring jug")), T("container", "VESSEL", ("container", "airtight container", "tub", "jar")),
    T("plate", "VESSEL", ("plate", "serving plate", "platter", "serving platter", "serving dish")),
    T("glass", "VESSEL", ("glass", "tumbler", "cocktail shaker", "shaker")), T("bag", "VESSEL", ("food bag", "freezer bag", "sandwich bag", "bag")),
    # utensils
    T("wooden spoon", "UTENSIL", ("wooden spoon", "spoon")), T("slotted spoon", "UTENSIL", ("slotted spoon",)),
    T("ladle", "UTENSIL", ("ladle",)), T("spatula", "UTENSIL", ("spatula", "fish slice", "palette knife")),
    T("tongs", "UTENSIL", ("tongs",)), T("whisk", "UTENSIL", ("whisk", "balloon whisk")),
    T("knife", "UTENSIL", ("knife", "sharp knife", "serrated knife", "bread knife")), T("fork", "UTENSIL", ("fork",)),
    T("chopping board", "UTENSIL", ("chopping board", "board", "work surface", "surface")),
    T("rolling pin", "UTENSIL", ("rolling pin", "belan")), T("grater", "UTENSIL", ("grater", "microplane", "box grater", "zester")),
    T("peeler", "UTENSIL", ("peeler", "vegetable peeler")), T("masher", "UTENSIL", ("masher", "potato masher", "ricer")),
    T("sieve", "UTENSIL", ("sieve", "strainer", "tea strainer")), T("colander", "UTENSIL", ("colander",)),
    T("mortar and pestle", "UTENSIL", ("mortar and pestle", "pestle and mortar", "mortar", "pestle")),
    T("pastry brush", "UTENSIL", ("pastry brush", "brush")), T("cutter", "UTENSIL", ("cutter", "cookie cutter", "pastry cutter")),
    T("piping bag", "UTENSIL", ("piping bag", "nozzle")), T("skewer", "UTENSIL", ("skewer", "cocktail stick", "toothpick")),
    T("mandoline", "UTENSIL", ("mandoline",)), T("wire rack", "UTENSIL", ("wire rack", "cooling rack", "rack")),
    T("lid", "UTENSIL", ("lid",)), T("scissors", "UTENSIL", ("scissors", "kitchen scissors")),
    # consumables
    T("baking parchment", "OTHER", ("baking parchment", "parchment", "greaseproof paper", "baking paper")),
    T("foil", "OTHER", ("foil", "kitchen foil", "tin foil")), T("cling film", "OTHER", ("cling film", "clingfilm")),
    T("kitchen paper", "OTHER", ("kitchen paper", "paper towel")), T("tea towel", "OTHER", ("tea towel", "cloth", "muslin")),
    # measurement
    T("thermometer", "MEASURE", ("thermometer", "probe", "sugar thermometer", "meat thermometer")),
    T("scales", "MEASURE", ("scales", "digital scales")), T("measuring spoon", "MEASURE", ("measuring spoon", "measuring spoons")),
    T("timer", "MEASURE", ("timer",)),
)
MATERIALS = ("non-stick", "cast-iron", "cast iron", "stainless steel", "aluminium", "copper", "enamelled", "glass",
             "ceramic", "wooden", "silicone", "carbon steel", "heatproof", "ovenproof", "flameproof")

ALIAS_TO_TOOL: dict[str, str] = {}
for _t in TOOLS:
    for _a in sorted((_t.canonical, *_t.aliases), key=len, reverse=True):
        ALIAS_TO_TOOL.setdefault(_a, _t.canonical)
_ALIAS_RE = re.compile(r"\b(" + "|".join(re.escape(a) for a in sorted(ALIAS_TO_TOOL, key=len, reverse=True))
                       + r")s?\b", re.IGNORECASE)
_MAT_RE = re.compile(r"\b(" + "|".join(re.escape(m) for m in MATERIALS) + r")\b", re.IGNORECASE)
# aliases that are too generic to count unless the context is clearly equipment
WEAK = {"sheet", "dish", "tin", "pan", "pot", "board", "surface", "spoon", "brush", "rack", "bag", "glass", "jar",
        "tub", "cloth", "probe", "cooker", "mixer", "processor", "basin", "mortar", "pestle", "nozzle", "shaker",
        "whisk", "grill", "microwave", "barbecue", "bbq", "sieve", "skewer", "ladle", "steamer", "strainer", "toaster"}
_ARTICLE = re.compile(r"\b(a|an|the|your|each|large|small|medium|deep|shallow|big|clean|lined|greased|"
                      r"non-stick|heavy|wide|separate|heatproof|ovenproof|flameproof|hot)\s+$", re.IGNORECASE)


def find_tools(text: str) -> list[tuple[int, str, str | None]]:
    """(position, canonical tool, material-or-None) — weak aliases count only after an article/adjective."""
    out = []
    for m in _ALIAS_RE.finditer(text):
        alias = m.group(1).lower()
        if alias in WEAK and not _ARTICLE.search(text[:m.start()]):
            continue
        mat = _MAT_RE.search(text[max(0, m.start() - 25):m.end()])   # material may sit inside the alias
        out.append((m.start(), ALIAS_TO_TOOL[alias], mat.group(1).lower() if mat else None))
    return out
