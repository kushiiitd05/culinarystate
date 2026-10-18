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
    T("oven", "HEAT_SOURCE", ("oven", "fan oven", "conventional oven")), T("hob", "HEAT_SOURCE", ("hob", "stovetop", "stove", "burner", "cooktop")),
    T("grill", "HEAT_SOURCE", ("grill", "grill pan")), T("barbecue", "HEAT_SOURCE", ("barbecue", "bbq")),
    T("microwave", "APPLIANCE", ("microwave", "microwave oven")), T("fridge", "APPLIANCE", ("fridge", "refrigerator")),
    T("freezer", "APPLIANCE", ("freezer",)), T("food processor", "APPLIANCE", ("food processor", "processor", "mini chopper")),
    T("blender", "APPLIANCE", ("blender", "liquidiser", "stick blender", "hand blender", "nutribullet")),
    T("electric whisk", "APPLIANCE", ("electric whisk", "hand mixer", "electric beaters")),
    T("stand mixer", "APPLIANCE", ("stand mixer", "tabletop mixer", "mixer")), T("slow cooker", "APPLIANCE", ("slow cooker",)),
    T("pressure cooker", "APPLIANCE", ("pressure cooker", "instant pot", "cooker", "multicooker")), T("air fryer", "APPLIANCE", ("air fryer", "air-fryer")),
    T("deep-fat fryer", "APPLIANCE", ("deep-fat fryer", "deep fryer", "deep fat fryer", "deep-fryer")), T("toaster", "APPLIANCE", ("toaster",)),
    T("ice cream maker", "APPLIANCE", ("ice cream maker", "ice cream machine")), T("spice grinder", "APPLIANCE", ("spice grinder", "coffee grinder")),
    # cookware
    T("frying pan", "COOKWARE", ("frying pan", "skillet", "non-stick pan", "non-stick frying pan")),
    T("saucepan", "COOKWARE", ("saucepan", "pan", "large pan", "small pan", "pot", "stockpot", "stock pot")),
    T("griddle pan", "COOKWARE", ("griddle pan", "griddle", "ridged griddle pan")),
    T("wok", "COOKWARE", ("wok",)), T("casserole", "COOKWARE", ("casserole", "casserole dish", "dutch oven", "flameproof casserole")),
    T("roasting tin", "COOKWARE", ("roasting tin", "roasting tray", "roasting pan")),
    T("baking tray", "COOKWARE", ("baking tray", "baking sheet", "oven tray", "cookie sheet", "sheet pan", "sheet")),
    T("baking dish", "COOKWARE", ("baking dish", "ovenproof dish", "gratin dish", "pie dish", "dish")),
    T("cake tin", "COOKWARE", ("cake tin", "cake pan", "sandwich tin", "springform tin", "springform pan", "loose-bottomed tin", "tin")),
    T("loaf tin", "COOKWARE", ("loaf tin", "loaf pan")), T("muffin tin", "COOKWARE", ("muffin tin", "cupcake tin", "bun tin", "muffin tray", "muffin pan", "cupcake pan")),
    T("tart tin", "COOKWARE", ("tart tin", "flan tin", "tart case", "tart pan", "quiche ring")), T("ramekin", "COOKWARE", ("ramekin", "ramekins")),
    T("pudding basin", "COOKWARE", ("pudding basin", "basin")), T("steamer", "COOKWARE", ("steamer", "steamer basket", "bamboo steamer")),
    T("tawa", "COOKWARE", ("tawa", "tava")), T("kadai", "COOKWARE", ("kadai", "kadhai", "karahi")),
    T("handi", "COOKWARE", ("handi",)), T("tadka pan", "COOKWARE", ("tadka pan", "tempering pan")),
    # vessels / containers
    T("bowl", "VESSEL", ("bowl", "mixing bowl", "large bowl", "small bowl", "heatproof bowl", "separate bowl")),
    T("jug", "VESSEL", ("jug", "measuring jug")), T("container", "VESSEL", ("container", "airtight container", "storage container", "tub", "jar")),
    T("plate", "VESSEL", ("plate", "serving plate", "platter", "serving platter", "serving dish")),
    T("glass", "VESSEL", ("glass", "tumbler", "cocktail shaker", "shaker")), T("bag", "VESSEL", ("food bag", "freezer bag", "sandwich bag", "bag")),
    # utensils
    T("wooden spoon", "UTENSIL", ("wooden spoon", "spoon")), T("slotted spoon", "UTENSIL", ("slotted spoon",)),
    T("ladle", "UTENSIL", ("ladle",)), T("spatula", "UTENSIL", ("spatula", "fish slice", "palette knife")),
    T("tongs", "UTENSIL", ("tongs",)), T("whisk", "UTENSIL", ("whisk", "balloon whisk")),
    T("knife", "UTENSIL", ("knife", "sharp knife", "serrated knife", "bread knife")), T("fork", "UTENSIL", ("fork",)),
    T("chopping board", "UTENSIL", ("chopping board", "cutting board", "board", "work surface", "surface")),
    T("rolling pin", "UTENSIL", ("rolling pin", "belan")), T("grater", "UTENSIL", ("grater", "microplane", "box grater", "zester")),
    T("peeler", "UTENSIL", ("peeler", "vegetable peeler")), T("masher", "UTENSIL", ("masher", "potato masher", "ricer")),
    T("sieve", "UTENSIL", ("sieve", "strainer", "tea strainer")), T("colander", "UTENSIL", ("colander",)),
    T("mortar and pestle", "UTENSIL", ("mortar and pestle", "pestle and mortar", "mortar", "pestle")),
    T("pastry brush", "UTENSIL", ("pastry brush", "brush")), T("cutter", "UTENSIL", ("cutter", "cookie cutter", "pastry cutter")),
    T("piping bag", "UTENSIL", ("piping bag", "pastry bag", "nozzle")), T("skewer", "UTENSIL", ("skewer", "cocktail stick", "toothpick")),
    T("mandoline", "UTENSIL", ("mandoline",)), T("wire rack", "UTENSIL", ("wire rack", "cooling rack", "rack")),
    T("lid", "UTENSIL", ("lid",)), T("scissors", "UTENSIL", ("scissors", "kitchen scissors")),
    # consumables
    T("baking parchment", "OTHER", ("baking parchment", "parchment", "parchment paper", "greaseproof paper", "baking paper")),
    T("foil", "OTHER", ("foil", "kitchen foil", "tin foil", "aluminium foil", "aluminum foil")), T("cling film", "OTHER", ("cling film", "clingfilm", "plastic wrap")),
    T("kitchen paper", "OTHER", ("kitchen paper", "paper towel", "paper towels")), T("tea towel", "OTHER", ("tea towel", "cloth", "muslin")),
    # measurement
    T("thermometer", "MEASURE", ("thermometer", "probe", "sugar thermometer", "meat thermometer")),
    T("scales", "MEASURE", ("scales", "digital scales")), T("measuring spoon", "MEASURE", ("measuring spoon", "measuring spoons")),
    T("timer", "MEASURE", ("timer",)),
    # added from Wikibooks Cookbook equipment pages (X3b, D-009)
    T("double boiler", "COOKWARE", ("double boiler", "bain-marie", "bain marie")),
    T("idli steamer", "COOKWARE", ("idli steamer", "idli pan", "idli stand", "idli maker")),
    T("tamagoyaki pan", "COOKWARE", ("tamagoyaki pan", "makiyakinabe")), T("fondue pot", "COOKWARE", ("fondue pot", "caquelon")),
    T("bundt tin", "COOKWARE", ("bundt tin", "bundt pan", "bundt mould")), T("pizza stone", "COOKWARE", ("pizza stone", "baking stone")),
    T("sauté pan", "COOKWARE", ("sauté pan", "saute pan")),
    T("tandoor", "HEAT_SOURCE", ("tandoor",)), T("blowtorch", "APPLIANCE", ("blowtorch", "blow torch", "kitchen torch")),
    T("rice cooker", "APPLIANCE", ("rice cooker",)), T("bread machine", "APPLIANCE", ("bread machine", "bread maker")),
    T("waffle iron", "APPLIANCE", ("waffle iron", "waffle maker")), T("juicer", "APPLIANCE", ("juicer", "juice extractor")),
    T("toaster oven", "APPLIANCE", ("toaster oven",)), T("pasta machine", "APPLIANCE", ("pasta machine", "pasta maker")),
    T("whipping siphon", "APPLIANCE", ("whipping siphon", "cream whipper")),
    T("funnel", "UTENSIL", ("funnel",)), T("garlic press", "UTENSIL", ("garlic press", "garlic crusher")),
    T("can opener", "UTENSIL", ("can opener", "tin opener")), T("egg separator", "UTENSIL", ("egg separator",)),
    T("baster", "UTENSIL", ("baster", "turkey baster")), T("food mill", "UTENSIL", ("food mill", "mouli")),
    T("citrus reamer", "UTENSIL", ("citrus reamer", "reamer", "citrus juicer", "lemon squeezer")),
    T("salad spinner", "UTENSIL", ("salad spinner",)), T("melon baller", "UTENSIL", ("melon baller",)),
    T("pastry blender", "UTENSIL", ("pastry blender",)),
    T("bench scraper", "UTENSIL", ("bench scraper", "dough scraper", "dough cutter")),
    T("pizza cutter", "UTENSIL", ("pizza cutter", "pizza wheel")), T("skimmer", "UTENSIL", ("skimmer", "spider strainer")),
    T("fat separator", "UTENSIL", ("fat separator", "gravy separator")), T("sifter", "UTENSIL", ("sifter", "flour sifter")),
    T("sushi mat", "UTENSIL", ("sushi mat", "bamboo mat", "makisu", "sushi roller")),
    T("chopsticks", "UTENSIL", ("chopsticks", "chopstick")), T("egg slicer", "UTENSIL", ("egg slicer",)),
    T("knife sharpener", "UTENSIL", ("knife sharpener", "sharpening steel", "whetstone")),
    T("proofing basket", "UTENSIL", ("proofing basket", "banneton", "proofer")),
    T("cheesecloth", "OTHER", ("cheesecloth", "muslin cloth")),
    T("silicone baking mat", "OTHER", ("silicone baking mat", "silpat")),
    T("paper case", "OTHER", ("paper case", "cupcake liner", "muffin case", "cupcake case")),
    T("measuring cup", "MEASURE", ("measuring cup", "measuring cups")),
)
# Wikibooks Cookbook equipment page per tool (external ref; CC BY-SA, X3b)
WIKIBOOKS_PAGE: dict[str, str] = {
    "baking dish": "Baking Dish",
    "baking parchment": "Parchment Paper",
    "baking tray": "Baking Sheet",
    "baster": "Baster",
    "bench scraper": "Dough cutter",
    "blender": "Blender",
    "blowtorch": "Blowtorch",
    "bowl": "Mixing Bowl",
    "bread machine": "Bread Machine",
    "bundt tin": "Bundt Cake Pan",
    "cake tin": "Cake Pan",
    "can opener": "Can Opener",
    "casserole": "Dutch Oven",
    "cheesecloth": "Cheesecloth",
    "chopping board": "Cutting Board",
    "chopsticks": "Chopstick",
    "citrus reamer": "Citrus reamer",
    "cling film": "Plastic Wrap",
    "colander": "Colander",
    "container": "Storage Containers",
    "cutter": "Cookie Cutter",
    "deep-fat fryer": "Deep Fryer",
    "double boiler": "Double Boiler",
    "egg separator": "Egg Separator",
    "egg slicer": "Egg Slicer",
    "fat separator": "Fat Separator",
    "foil": "Aluminium Foil",
    "fondue pot": "Caquelon",
    "food mill": "Food Mill",
    "food processor": "Food Processor",
    "fork": "Fork",
    "frying pan": "Frying Pan",
    "funnel": "Funnel",
    "garlic press": "Garlic Press",
    "grater": "Grater",
    "griddle pan": "Griddle",
    "grill": "Grill",
    "hob": "Cooktop",
    "ice cream maker": "Ice Cream Machine",
    "idli steamer": "Idli Pan",
    "juicer": "Juice Extractor",
    "kadai": "Kadai",
    "kitchen paper": "Paper Towel",
    "knife": "Knife",
    "knife sharpener": "Knife Sharpener",
    "ladle": "Ladle",
    "loaf tin": "Loaf Pan",
    "mandoline": "Mandoline",
    "masher": "Potato Masher",
    "measuring cup": "Measuring Cup",
    "measuring spoon": "Measuring Spoons",
    "melon baller": "Melon Baller",
    "microwave": "Microwave Oven",
    "mortar and pestle": "Mortar and Pestle",
    "muffin tin": "Cupcake Pan",
    "oven": "Oven",
    "paper case": "Cupcake Liner",
    "pasta machine": "Pasta Maker",
    "pastry blender": "Pastry Blender",
    "pastry brush": "Brush",
    "peeler": "Peeler",
    "piping bag": "Pastry Bag",
    "pizza cutter": "Pizza Cutter",
    "pizza stone": "Pizza Stone",
    "proofing basket": "Proofer",
    "ramekin": "Ramekin",
    "rice cooker": "Rice Cooker",
    "rolling pin": "Rolling Pin",
    "salad spinner": "Salad Spinner",
    "saucepan": "Saucepan",
    "sauté pan": "Sauté Pan",
    "scales": "Scale",
    "scissors": "Shears",
    "sieve": "Sieve",
    "sifter": "Sifter",
    "silicone baking mat": "Silpat",
    "skewer": "Skewer",
    "skimmer": "Spider",
    "slotted spoon": "Slotted Spoon",
    "slow cooker": "Slow Cooker",
    "spatula": "Spatula",
    "stand mixer": "Mixer",
    "sushi mat": "Sushi Roller",
    "tamagoyaki pan": "Makiyakinabe Pan",
    "tandoor": "Tandoor",
    "tart tin": "Quiche Ring",
    "tawa": "Tava",
    "thermometer": "Thermometer",
    "toaster": "Toaster",
    "toaster oven": "Toaster Oven",
    "tongs": "Tongs",
    "waffle iron": "Waffle Iron",
    "whipping siphon": "Whipping Siphon",
    "whisk": "Whisk",
    "wire rack": "Cooling Rack",
    "wok": "Wok",
    "wooden spoon": "Cooking Spoon",
}
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
