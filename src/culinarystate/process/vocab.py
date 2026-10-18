"""Process vocabulary v1 — curated from BBC corpus verb discovery (spaCy lemmas, 15k-step sample)
plus USDA R6 / Phenol-Explorer step names. Corpus-supported; not padded to a target count.

Each entry: canonical, family, kind (ACTION | ENDPOINT), lemma aliases, required condition axes.
`MECHANISMS` are AI-drafted candidate mechanism families per process family — verify against
research/R3 cooking-chemistry notes before citing (verification status UNVERIFIED in the ledger).
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Proc:
    canonical: str
    family: str
    kind: str
    aliases: tuple[str, ...]


HEAT_AXES = ("duration", "temperature")
AXES = {
    "DRY_HEAT": HEAT_AXES, "FAT_HEAT": HEAT_AXES, "WET_HEAT": HEAT_AXES, "HEAT_GENERAL": HEAT_AXES,
    "COOLING": HEAT_AXES, "MECHANICAL_CUT": ("particle_size", "geometry"), "MECHANICAL_MIX": ("agitation", "duration"),
    "FERMENT_LEAVEN": ("duration", "temperature", "humidity"), "PRESERVATION": ("duration", "temperature", "ph", "salt",
                                                                                  "sugar"),
    "SEPARATION": (), "COMBINATION": (), "TRANSFER": (), "SHAPING": ("geometry",), "RESERVATION": (),
    "RESTING": ("duration", "temperature"), "SERVING": (), "HEAT_CONTROL": ("temperature",), "ENDPOINT": (),
}
MECHANISMS = {
    "DRY_HEAT": ("maillard", "caramelisation", "moisture_loss", "lipid_oxidation"),
    "FAT_HEAT": ("maillard", "moisture_loss", "lipid_oxidation", "oil_uptake", "acrylamide_formation_starchy"),
    "WET_HEAT": ("leaching", "starch_gelatinisation", "protein_denaturation", "cell_wall_softening"),
    "HEAT_GENERAL": ("protein_denaturation", "phase_change"),
    "MECHANICAL_CUT": ("cell_rupture_enzymatic_reactions",),
    "MECHANICAL_MIX": ("emulsification", "aeration", "gluten_development"),
    "FERMENT_LEAVEN": ("microbial_fermentation", "co2_leavening"),
    "COOLING": ("crystallisation", "starch_retrogradation", "gelation"),
    "PRESERVATION": ("water_activity_reduction", "acidification", "microbial_inactivation"),
}

P = Proc
PROCESSES: tuple[Proc, ...] = (
    # added from Wikibooks Cookbook technique pages (X3b, D-009); "temper" split from tadka, "brine" from pickle
    P("sous-vide", "WET_HEAT", "ACTION", ("sous-vide", "sous vide")), P("scald", "WET_HEAT", "ACTION", ("scald",)),
    P("render", "FAT_HEAT", "ACTION", ("render",)), P("baste", "FAT_HEAT", "ACTION", ("baste",)),
    P("blind-bake", "DRY_HEAT", "ACTION", ("blind-bake", "bake blind")),
    P("temper", "HEAT_GENERAL", "ACTION", ("temper",)), P("brine", "PRESERVATION", "ACTION", ("brine",)),
    P("degorge", "SEPARATION", "ACTION", ("degorge", "disgorge")),
    # dry heat
    P("bake", "DRY_HEAT", "ACTION", ("bake", "shirr")), P("roast", "DRY_HEAT", "ACTION", ("roast",)),
    P("grill", "DRY_HEAT", "ACTION", ("grill", "broil", "barbecue", "griddle")),
    P("toast", "DRY_HEAT", "ACTION", ("toast",)), P("char", "DRY_HEAT", "ACTION", ("char", "blacken", "scorch")),
    P("smoke", "DRY_HEAT", "ACTION", ("smoke",)), P("microwave", "HEAT_GENERAL", "ACTION", ("microwave", "nuke")),
    P("air-fry", "DRY_HEAT", "ACTION", ("air-fry", "airfry")),
    # fat heat
    P("fry", "FAT_HEAT", "ACTION", ("fry",)), P("stir-fry", "FAT_HEAT", "ACTION", ("stir-fry", "stirfry")),
    P("deep-fry", "FAT_HEAT", "ACTION", ("deep-fry",)), P("shallow-fry", "FAT_HEAT", "ACTION", ("shallow-fry",)),
    P("pan-fry", "FAT_HEAT", "ACTION", ("pan-fry",)), P("saute", "FAT_HEAT", "ACTION", ("sauté", "saute")),
    P("sear", "FAT_HEAT", "ACTION", ("sear", "reverse-sear", "pan-broil")), P("brown", "FAT_HEAT", "ACTION", ("brown",)),
    P("sweat", "FAT_HEAT", "ACTION", ("sweat",)), P("temper-spices", "FAT_HEAT", "ACTION", ("tadka", "chhonk", "baghar")),
    # wet heat
    P("boil", "WET_HEAT", "ACTION", ("boil",)), P("simmer", "WET_HEAT", "ACTION", ("simmer",)),
    P("poach", "WET_HEAT", "ACTION", ("poach",)), P("steam", "WET_HEAT", "ACTION", ("steam",)),
    P("blanch", "WET_HEAT", "ACTION", ("blanch",)), P("braise", "WET_HEAT", "ACTION", ("braise",)),
    P("stew", "WET_HEAT", "ACTION", ("stew",)), P("parboil", "WET_HEAT", "ACTION", ("parboil",)),
    P("pressure-cook", "WET_HEAT", "ACTION", ("pressure-cook", "pressure-boil", "pressure-steam")),
    P("reduce", "WET_HEAT", "ACTION", ("reduce",)), P("infuse", "WET_HEAT", "ACTION", ("infuse", "steep")),
    P("deglaze", "WET_HEAT", "ACTION", ("deglaze",)),
    # general heat
    P("cook", "HEAT_GENERAL", "ACTION", ("cook",)), P("heat", "HEAT_GENERAL", "ACTION", ("heat", "warm")),
    P("reheat", "HEAT_GENERAL", "ACTION", ("reheat",)), P("melt", "HEAT_GENERAL", "ACTION", ("melt",)),
    P("preheat", "HEAT_CONTROL", "ACTION", ("preheat",)), P("flame", "HEAT_GENERAL", "ACTION", ("flambé", "flame")),
    P("caramelise", "DRY_HEAT", "ACTION", ("caramelise", "caramelize")),
    # cooling / resting
    P("cool", "COOLING", "ACTION", ("cool",)), P("chill", "COOLING", "ACTION", ("chill", "refrigerate")),
    P("freeze", "COOLING", "ACTION", ("freeze",)), P("defrost", "COOLING", "ACTION", ("defrost", "thaw")),
    P("rest", "RESTING", "ACTION", ("rest", "stand", "sit")),
    # mechanical cut
    P("chop", "MECHANICAL_CUT", "ACTION", ("chop",)), P("slice", "MECHANICAL_CUT", "ACTION", ("slice",)),
    P("dice", "MECHANICAL_CUT", "ACTION", ("dice", "cube")), P("cut", "MECHANICAL_CUT", "ACTION", ("cut",)),
    P("halve", "MECHANICAL_CUT", "ACTION", ("halve", "quarter")), P("grate", "MECHANICAL_CUT", "ACTION", ("grate", "zest")),
    P("crush", "MECHANICAL_CUT", "ACTION", ("crush", "bash", "pound", "squash")),
    P("mince", "MECHANICAL_CUT", "ACTION", ("mince",)), P("shred", "MECHANICAL_CUT", "ACTION", ("shred", "shre")),
    P("crack", "MECHANICAL_CUT", "ACTION", ("crack", "break")),
    P("trim", "MECHANICAL_CUT", "ACTION", ("trim", "core", "deseed", "stone", "hull", "top")),
    P("peel", "MECHANICAL_CUT", "ACTION", ("peel", "skin")), P("tear", "MECHANICAL_CUT", "ACTION", ("tear", "rip")),
    P("snip", "MECHANICAL_CUT", "ACTION", ("snip",)), P("carve", "MECHANICAL_CUT", "ACTION", ("carve",)),
    P("score", "MECHANICAL_CUT", "ACTION", ("score", "slash")), P("crumble", "MECHANICAL_CUT", "ACTION", ("crumble",)),
    P("flake", "MECHANICAL_CUT", "ACTION", ("flake",)), P("pierce", "MECHANICAL_CUT", "ACTION", ("pierce", "prick", "poke")),
    P("grind", "MECHANICAL_CUT", "ACTION", ("grind", "mill")), P("julienne", "MECHANICAL_CUT", "ACTION", ("julienne",)),
    P("butterfly", "MECHANICAL_CUT", "ACTION", ("butterfly", "spatchcock", "spatchcock")),
    # mechanical mix
    P("stir", "MECHANICAL_MIX", "ACTION", ("stir",)), P("mix", "MECHANICAL_MIX", "ACTION", ("mix", "combine", "incorporate", "loosen")),
    P("whisk", "MECHANICAL_MIX", "ACTION", ("whisk",)), P("beat", "MECHANICAL_MIX", "ACTION", ("beat", "cream")),
    P("fold", "MECHANICAL_MIX", "ACTION", ("fold",)), P("toss", "MECHANICAL_MIX", "ACTION", ("toss",)),
    P("blend", "MECHANICAL_MIX", "ACTION", ("blend", "whizz", "blitz", "purée", "puree", "liquidise", "process")),
    P("mash", "MECHANICAL_MIX", "ACTION", ("mash",)), P("knead", "MECHANICAL_MIX", "ACTION", ("knead",)),
    P("whip", "MECHANICAL_MIX", "ACTION", ("whip",)), P("rub-in", "MECHANICAL_MIX", "ACTION", ("rub",)),
    P("shake", "MECHANICAL_MIX", "ACTION", ("shake",)), P("swirl", "MECHANICAL_MIX", "ACTION", ("swirl", "ripple")),
    P("emulsify", "MECHANICAL_MIX", "ACTION", ("emulsify",)),
    # separation
    P("drain", "SEPARATION", "ACTION", ("drain",)), P("strain", "SEPARATION", "ACTION", ("strain", "sieve")),
    P("sift", "SEPARATION", "ACTION", ("sift",)), P("skim", "SEPARATION", "ACTION", ("skim",)),
    P("separate", "SEPARATION", "ACTION", ("separate",)), P("discard", "SEPARATION", "ACTION", ("discard",)),
    P("rinse", "SEPARATION", "ACTION", ("rinse", "wash", "wipe", "clean")), P("squeeze", "SEPARATION", "ACTION", ("squeeze", "juice")),
    P("pick", "SEPARATION", "ACTION", ("pick", "pluck")), P("pat-dry", "SEPARATION", "ACTION", ("pat",)),
    # combination / application
    P("add", "COMBINATION", "ACTION", ("add",)), P("pour", "COMBINATION", "ACTION", ("pour",)),
    P("sprinkle", "COMBINATION", "ACTION", ("sprinkle", "scatter", "dust", "dot")),
    P("drizzle", "COMBINATION", "ACTION", ("drizzle",)), P("spoon", "COMBINATION", "ACTION", ("spoon", "ladle", "dollop", "scoop")),
    P("spread", "COMBINATION", "ACTION", ("spread", "smear", "smooth", "level")), P("top", "COMBINATION", "ACTION", ("layer", "pile")),
    P("coat", "COMBINATION", "ACTION", ("coat", "dredge", "dip", "roll-in")),
    P("brush", "COMBINATION", "ACTION", ("brush", "glaze", "baste", "grease", "oil", "butter")),
    P("season", "COMBINATION", "ACTION", ("season", "salt", "taste")), P("fill", "COMBINATION", "ACTION", ("fill", "stuff")),
    P("dress", "COMBINATION", "ACTION", ("dress",)), P("marinate", "FERMENT_LEAVEN", "ACTION", ("marinate", "marinade")),
    P("dissolve", "COMBINATION", "ACTION", ("dissolve",)),
    # transfer / containment
    P("put", "TRANSFER", "ACTION", ("put", "place", "set", "pop")), P("transfer", "TRANSFER", "ACTION", ("transfer", "move")),
    P("tip", "TRANSFER", "ACTION", ("tip", "turn-out", "empty")), P("return", "TRANSFER", "ACTION", ("return",)),
    P("remove", "TRANSFER", "ACTION", ("remove", "lift", "take", "scrape")), P("arrange", "TRANSFER", "ACTION", ("arrange", "lay")),
    P("line", "TRANSFER", "ACTION", ("line",)), P("wrap", "TRANSFER", "ACTION", ("wrap",)),
    P("cover", "TRANSFER", "ACTION", ("cover",)), P("uncover", "TRANSFER", "ACTION", ("uncover",)),
    P("seal", "TRANSFER", "ACTION", ("seal",)), P("store", "TRANSFER", "ACTION", ("store",)),
    P("thread", "TRANSFER", "ACTION", ("thread", "skewer")), P("flip", "TRANSFER", "ACTION", ("flip", "turn")),
    P("insert", "TRANSFER", "ACTION", ("insert", "tuck", "push")),
    # shaping / assembly
    P("roll", "SHAPING", "ACTION", ("roll",)), P("shape", "SHAPING", "ACTION", ("shape", "form", "mould", "quenelle")),
    P("divide", "SHAPING", "ACTION", ("divide", "split", "portion")), P("pipe", "SHAPING", "ACTION", ("pipe",)),
    P("flatten", "SHAPING", "ACTION", ("flatten", "press")), P("stamp-out", "SHAPING", "ACTION", ("stamp",)),
    P("assemble", "SHAPING", "ACTION", ("assemble", "sandwich", "build")), P("tie", "SHAPING", "ACTION", ("tie", "truss")),
    P("decorate", "SHAPING", "ACTION", ("decorate", "garnish")), P("pack", "SHAPING", "ACTION", ("pack",)),
    # biological / preservation
    P("prove", "FERMENT_LEAVEN", "ACTION", ("prove", "proof")), P("ferment", "FERMENT_LEAVEN", "ACTION", ("ferment",)),
    P("soak", "FERMENT_LEAVEN", "ACTION", ("soak",)), P("pickle", "PRESERVATION", "ACTION", ("pickle", "cure")),
    P("sterilise", "PRESERVATION", "ACTION", ("sterilise", "sterilize")), P("can", "PRESERVATION", "ACTION", ()),
    P("dry", "PRESERVATION", "ACTION", ("dry", "dehydrate")), P("pasteurise", "PRESERVATION", "ACTION", ("pasteurise",)),
    P("germinate", "FERMENT_LEAVEN", "ACTION", ("germinate", "sprout", "sprout")),
    # reservation / serving / heat control
    P("reserve", "RESERVATION", "ACTION", ("reserve", "save", "keep")), P("serve", "SERVING", "ACTION", ("serve",)),
    P("adjust-heat", "HEAT_CONTROL", "ACTION", ("lower", "increase")),
    # endpoints (usually "until …")
    P("soften", "ENDPOINT", "ENDPOINT", ("soften", "tender")), P("thicken", "ENDPOINT", "ENDPOINT", ("thicken",)),
    P("wilt", "ENDPOINT", "ENDPOINT", ("wilt",)), P("colour", "ENDPOINT", "ENDPOINT", ("colour", "color", "golden")),
    P("bubble", "ENDPOINT", "ENDPOINT", ("bubble", "sizzle")), P("crisp", "ENDPOINT", "ENDPOINT", ("crisp",)),
    P("evaporate", "ENDPOINT", "ENDPOINT", ("evaporate", "absorb")), P("set", "ENDPOINT", "ENDPOINT", ("firm",)),
    P("puff", "ENDPOINT", "ENDPOINT", ("puff", "rise")),
)

# phrases resolved before single lemmas (text is lowercased)
PHRASES: tuple[tuple[str, str], ...] = (
    (r"\bbring\b[^.]{0,40}\bto (?:the |a )?(?:boil|simmer)\b", "boil"),
    (r"\bset (?:\w+ ){0,3}aside\b|\bput (?:\w+ ){0,3}aside\b", "reserve"),
    (r"\bleave (?:\w+ ){0,3}to (?:cool)\b", "cool"),
    (r"\bleave (?:\w+ ){0,3}to (?:rest|stand|infuse|marinate|soak|prove|rise)\b", "rest"),
    (r"\b(?:turn|reduce|lower) (?:down )?the heat\b|\bturn the heat (?:down|up)\b", "adjust-heat"),
    (r"\bstir[- ]fry", "stir-fry"), (r"\bdeep[- ]fry", "deep-fry"), (r"\bpan[- ]fry", "pan-fry"),
    (r"\bshallow[- ]fry", "shallow-fry"), (r"\brub (?:\w+ ){0,3}in\b", "rub-in"), (r"\bturn out\b", "tip"),
    (r"\bstamp out\b|\bcut out\b", "stamp-out"), (r"\bpat (?:\w+ ){0,3}dry\b", "pat-dry"),
    (r"\bheat (?:the )?oven\b|\bpreheat\b", "preheat"),
)
IGNORE = {"use", "make", "leave", "have", "like", "need", "start", "take", "come", "follow", "do", "go", "give", "get",
          "see", "want", "eat", "help", "run", "look", "feel", "become", "depend", "ensure", "prevent", "worry", "try",
          "reach", "be", "check", "allow", "let", "continue", "begin", "finish", "create", "repeat", "stop", "accord",
          "prefer", "handle", "catch", "end", "open", "test", "adjust", "enjoy", "wait", "fall", "remain", "bring",
          "work", "prepare", "hold", "fit", "release", "drop", "pull", "slide", "throw", "measure", "weigh", "touch",
          "resemble", "overlap", "space", "low", "room", "re", "double", "base", "ice", "flour", "oven", "chilli",
          "stick", "lie", "burn", "cle"}

# Wikibooks Cookbook technique page -> canonical process (curated; pages without a single process are omitted)
WIKIBOOKS_TECHNIQUE: dict[str, str] = {
    "Baking": "bake", "Deep Fat Frying": "deep-fry", "Grilling": "grill", "Boiling": "boil", "Braising": "braise",
    "Frying": "fry", "Broiling": "grill", "Blanching": "blanch", "Dredging": "coat", "Marinating": "marinate",
    "Barbecuing": "grill", "Pickling": "pickle", "Parboiling": "parboil", "Boiling Rice": "boil", "Cooking Sugar": "boil",
    "Brining": "brine", "Boiling Pasta": "boil", "Basting": "baste", "Caramelization": "caramelise",
    "Microwaving": "microwave", "Melting chocolate": "melt", "Fermentation": "ferment", "Al Dente": "boil",
    "Knife Skills": "cut", "Browning": "brown", "Mixing": "mix", "Deglazing": "deglaze", "Pan Broiling": "sear",
    "Degorging": "degorge", "Canning": "can", "Freezing": "freeze", "Microwave Cooking": "microwave",
    "Blind-baking": "blind-bake", "Roasting": "roast", "Roasting Nuts": "toast", "Simmering": "simmer",
    "Steaming": "steam", "Sautéing": "saute", "Salting": "season", "Poaching": "poach", "Stir-frying": "stir-fry",
    "Smoking": "smoke", "Stewing": "stew", "Rolling Boil": "boil", "Puréeing": "blend", "Soaking Beans": "soak",
    "Toasting": "toast", "Tempering": "temper", "Tempering Chocolate": "temper", "Scalding": "scald",
    "Pressure Cooking": "pressure-cook", "Separating Eggs": "separate", "Sous-vide": "sous-vide", "Shirring": "bake",
    "Thermal Cooking": "cook", "Sprouting": "germinate", "Spatchcocking": "butterfly", "Quenelle": "shape",
    "Rendering": "render", "Reverse-searing": "sear", "Outdoor Cooking": "cook", "Camp Cooking": "cook",
    "Clay Pot Cooking": "cook"}

BY_CANON = {p.canonical: p for p in PROCESSES}
LEMMA_TO_PROC: dict[str, str] = {}
for _p in PROCESSES:
    for _a in (_p.canonical, *_p.aliases):
        LEMMA_TO_PROC.setdefault(_a, _p.canonical)
_PHRASE_RE = [(re.compile(p), c) for p, c in PHRASES]


def phrase_processes(text: str) -> list[str]:
    t = text.lower()
    return [c for rx, c in _PHRASE_RE if rx.search(t)]


def map_step_name(name: str) -> str | None:
    """Map evidence step names (USDA/PE: 'boil', 'pressure-boil', 'store-frozen') to a canonical process."""
    n = name.strip().lower()
    if n in BY_CANON:
        return n
    if n in LEMMA_TO_PROC:
        return LEMMA_TO_PROC[n]
    special = {"hard-boil": "boil", "scramble": "fry", "make-jam": "boil", "make-puree": "blend", "juice": "squeeze",
               "store-ambient": "store", "store-frozen": "freeze", "store-refrigerated": "chill", "dehull": "trim",
               "extrude": "shape", "high-pressure-process": "pasteurise", "pulsed-electric-field": "pasteurise",
               "nixtamalize": "soak", "freeze-dry": "dry", "boil|bake": "boil", "bake|simmer": "bake",
               "fry|broil": "fry", "broil|fry": "grill", "heat": "heat"}
    return special.get(n)
