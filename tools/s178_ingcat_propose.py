#!/usr/bin/env python3
"""S178 INGCAT lane: AI-drafted category PROPOSALS for every ACTIVE ING that has no `category`, for one-sitting human confirmation.

AI_DRAFTED / PROPOSED / NON_CITABLE. Nothing here is a human decision, signature or approval; `human_decision` stays empty.
No ledger is written: ING.jsonl and every other `ledgers/data/*.jsonl` are READ ONLY. A proposed category is only ever a
value that already exists in the ING category vocabulary (the distinct non-empty `category` values of the ACTIVE ING). When no
existing value fits, the proposal is left empty or the closest value is flagged `NO_EXACT_FIT`, and a NEW value is suggested in
`new_category_suggestion` (suggested, never added).

Evidence, in this order of authority (each proposal records every basis it used and every conflict it found):
  REGISTRY_SR  the SR Legacy food group of the curated identity in registry/ing_sr_defaults_v1.csv (read through
               composition.ing_sr_match.load_registry / normalise, read only). Kinds DIRECT, UK_US, DEFAULT_FORM, APPROX map to a
               food; NO_SR_EQUIVALENT / NOT_A_FOOD / AMBIGUOUS give no identity (as in mechanism/sr_identity.py).
  LEGACY_SR    the legacy lexical match (registry/ing_sr_legacy_match_draft_v1.csv) rank-1 food group, only for terms the
               curated registry does not hold, and only when its band is HIGH or MEDIUM (a LOW band alone proposes nothing).
  LEXICAL      culinary-class rules over the name (head word scan, phrase overrides, special classes such as water, salt,
               leavening). The culinary class is checked AGAINST the SR group because SR food groups leak: salt is filed under
               "Spices and Herbs", water under "Beverages", baking powder under "Baked Products", mayonnaise under
               "Fats and Oils", soy sauce under "Legumes".
Resolution: when the bases agree the proposal is that category; when the culinary class and the SR group differ the culinary
class wins, the conflict is written down and confidence is capped at MEDIUM (LOW for a weak rule).

Confidence:
  HIGH    two bases agree on one existing value, the fit is exact and the lexical rule is unambiguous; or a curated registry
          identity (DIRECT / UK_US / DEFAULT_FORM) in a clean SR group with no lexical rule against it.
  MEDIUM  one decent basis, or the bases agree but the fit is approximate / the rule is ambiguous (dual-use words).
  LOW     weak or conflicting evidence, no existing value fits, or nothing to go on (proposed_category may be empty).

The impact order is the corpus mention count of the ING in the NON-BBC families (ledgers/recipe_base/vocab_corpus_frequency_v1.parquet:
FOODCOM, GUTENBERG_SEGMENT, WIKIBOOKS, TASTESET ingredient-line mentions). `mention_items` is the S177 full-census ITEM count
(reports/step23/router_demo_census_vitc_nonBBC_full_S177.json, `category_blocked_items`) where the S177 census has one.

    python tools/s178_ingcat_propose.py --overwrite                       # CSV + top-100 sheet + summary
    python tools/s178_ingcat_propose.py --overwrite --simulate            # + router-census overlay simulation (1,000 sample)
    python tools/s178_ingcat_propose.py --backtest-only                   # agreement of the engine with the ledger's own labels

Counts-only summaries; the CSV carries registry names, SR names (public domain) and counts, never recipe text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.composition import ing_sr_match as M  # noqa: E402  (read only: load_registry, normalise)

TOOL_VERSION = "s178-ingcat-propose-0.1.0-draft"
STATUS = "AI_DRAFTED_FOR_HUMAN_REVIEW"
OUT_CSV = "registry/ing_category_proposals_S178_DRAFT.csv"
OUT_SHEET = "reports/s178/ingcat/top100_for_human_confirmation.md"
OUT_SUMMARY = "reports/s178/ingcat/ingcat_summary_S178.json"
OUT_SIM = "reports/s178/ingcat/ingcat_router_simulation_1000_S178.json"
ING_LEDGER = "ledgers/data/ING.jsonl"
ALIAS_LEDGER = "ledgers/data/ALIAS.jsonl"
REGISTRY = "registry/ing_sr_defaults_v1.csv"
LEGACY = "registry/ing_sr_legacy_match_draft_v1.csv"
VOCAB_FREQ = "ledgers/recipe_base/vocab_corpus_frequency_v1.parquet"
S177_FULL = "reports/step23/router_demo_census_vitc_nonBBC_full_S177.json"
S177_1000 = "reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json"
BBC_FAMILY = "A1_BBC_GOOD_FOOD"
HIGH, MEDIUM, LOW = "HIGH", "MEDIUM", "LOW"
CURATED_KINDS = frozenset({"DIRECT", "UK_US", "DEFAULT_FORM"})
USABLE_LEGACY_BANDS = frozenset({HIGH, MEDIUM})
EXACT, APPROX, NONE = "EXACT", "APPROX", "NONE"
CSV_COLUMNS = ("ing_id", "name", "proposed_category", "basis", "confidence", "sr_food_group", "mention_items", "human_decision",
               "rank", "mention_nonbbc", "mention_all_families", "conflicts", "alt_category", "new_category_suggestion",
               "registry_kind", "sr_description", "legacy_band", "crosswalk_confirms", "unlocks_absent_vitc", "status")


# ============================================================================================ names and tokens
def fold(name: str) -> tuple[str, ...]:
    """Accent-folded, singularised tokens (the matcher's own `normalise` after NFKD, so 'gruyère' is one token)."""
    s = unicodedata.normalize("NFKD", name.lower())
    return M.normalise("".join(c for c in s if not unicodedata.combining(c)))


def _words(text: str) -> list[tuple[str, ...]]:
    return [fold(w) for w in text.split()]


def _single_map(text: str) -> dict[str, None]:
    return {t[0]: None for t in _words(text) if len(t) == 1}


# ============================================================================================ SR group -> vocabulary
# SR Legacy food group -> the existing ING category it files under. A group missing here has no vocabulary item (Snacks,
# Fast Foods, Meals/Entrees, Baby Foods, Restaurant Foods, American Indian/Alaska Native Foods): no SR-derived proposal.
GROUP_TO_CATEGORY: Mapping[str, str] = {
    "Beverages": "BEVERAGE", "Breakfast Cereals": "CEREAL", "Baked Products": "CEREAL", "Cereal Grains and Pasta": "CEREAL",
    "Soups, Sauces, and Gravies": "CONDIMENT", "Dairy and Egg Products": "DAIRY", "Fats and Oils": "FAT_OIL",
    "Fruits and Fruit Juices": "FRUIT", "Spices and Herbs": "HERB_SPICE", "Legumes and Legume Products": "LEGUME",
    "Beef Products": "MEAT", "Pork Products": "MEAT", "Poultry Products": "MEAT", "Lamb, Veal, and Game Products": "MEAT",
    "Sausages and Luncheon Meats": "MEAT", "Nut and Seed Products": "NUT_SEED", "Finfish and Shellfish Products": "SEAFOOD",
    "Sweets": "SWEETENER", "Vegetables and Vegetable Products": "VEGETABLE"}
# SR groups known to hold foods whose culinary class is another category (salt, water, baking powder, yeast, stock, soy sauce,
# mayonnaise, ketchup, fresh herbs, chocolate ...). An SR-only proposal from one of these is capped at MEDIUM.
LEAKY_GROUPS = frozenset({"Spices and Herbs", "Beverages", "Baked Products", "Sweets", "Soups, Sauces, and Gravies",
                          "Fats and Oils", "Legumes and Legume Products", "Vegetables and Vegetable Products",
                          "Fruits and Fruit Juices"})


def sr_category(group: str | None, description: str | None = None) -> str | None:
    """The existing ING category an SR food group files under; Dairy-and-Egg splits on the SR description, fruit juice is a
    BEVERAGE (the ledger files lemon / orange juice there)."""
    if not group:
        return None
    first = fold((description or "").split(",")[0])
    if group == "Dairy and Egg Products":
        return "EGG" if first[:1] == ("egg",) else "DAIRY"
    if group == "Fruits and Fruit Juices" and "juice" in first:
        return "BEVERAGE"
    return GROUP_TO_CATEGORY.get(group)


# ============================================================================================ lexical culinary class
CATEGORY_WORDS: Mapping[str, str] = {
    "FAT_OIL": "oil fat lard dripping shortening suet tallow schmaltz margarine",
    "DAIRY": ("milk cheese cream yogurt yoghurt butter buttermilk curd whey custard kefir ghee paneer mascarpone ricotta mozzarella "
              "parmesan parmigiano cheddar feta brie camembert gouda edam emmental emmenthal gruyere halloumi stilton "
              "gorgonzola roquefort manchego fontina pecorino bocconcini boursin taleggio comte dolcelatte quark provolone "
              "asiago havarti jarlsberg cotija burrata labneh leicester cheshire lancashire wensleydale gloucester "
              "creme fraiche mozarella fromage"),
    "EGG": "egg yolk albumen meringue",
    "MEAT": ("beef pork chicken turkey lamb duck goose veal venison ham bacon sausage mince steak rib chop cutlet liver kidney "
             "rabbit goat mutton gammon salami chorizo pepperoni prosciutto pancetta lardon brisket tenderloin sirloin rump "
             "oxtail tripe shank hock drumstick thigh wing breast meat quail pheasant partridge poussin pig jerky meatball "
             "frankfurter mortadella bresaola haggis pigeon game fowl brawn guanciale nduja sausagemeat gravadlax"),
    "SEAFOOD": ("fish salmon tuna cod haddock trout mackerel sardine anchovy herring prawn shrimp crab lobster mussel clam oyster "
                "squid octopus scallop halibut bream snapper tilapia sole plaice eel swordfish crayfish crawfish cockle whelk "
                "caviar roe seafood kipper pollock monkfish mullet crabmeat langoustine calamari skate turbot whitebait bonito "
                "dryfish haddock pilchard sprat carp perch pike catfish"),
    "VEGETABLE": ("onion garlic carrot potato tomato cabbage lettuce spinach kale broccoli cauliflower cucumber courgette zucchini "
                  "aubergine eggplant pumpkin squash beet beetroot turnip swede radish celery leek mushroom corn sweetcorn "
                  "asparagus artichoke shallot scallion okra parsnip yam cassava fennel chard rocket arugula watercress cress "
                  "radicchio endive chicory kohlrabi mangetout salad samphire seaweed nori olive avocado pimento romaine "
                  "cos savoy sprout rutabaga celeriac beansprout pak choi bok choy marrow gherkin pickle "
                  "sorrel kimchi sauerkraut coleslaw chilli chili chile jalapeno capsicum porcini cep cornichon mooli frisee"),
    "FRUIT": ("apple pear peach plum cherry berry strawberry raspberry blueberry blackberry cranberry currant gooseberry grape "
              "raisin sultana orange lemon lime grapefruit mandarin clementine tangerine banana mango pineapple papaya kiwi "
              "melon cantaloupe watermelon fig date apricot nectarine pomegranate rhubarb damson lychee tamarind plantain "
              "quince persimmon guava fruit zest peel rind jam marmalade prune barberry kumquat satsuma physalis"),
    "BEVERAGE": ("wine beer ale lager stout cider rum vodka gin whisky whiskey bourbon brandy cognac tequila liqueur sherry port "
                 "vermouth champagne prosecco sake juice tea coffee espresso soda cola lemonade tonic amaretto kirsch marnier "
                 "pernod bailey marsala madeira pisco kahlua schnapps cointreau campari aperol absinthe mead cocktail "
                 "smoothie cordial perry grappa calvados cassis limoncello guinness malibu disaronno matcha"),
    "CEREAL": ("flour bread rice pasta noodle spaghetti penne fusilli linguine fettuccine tagliatelle pappardelle rigatoni macaroni "
               "orzo lasagne lasagna cannelloni ravioli gnocchi couscous bulgur quinoa oat oatmeal barley wheat rye cornflour "
               "cornstarch cornmeal polenta semolina millet sorghum buckwheat spelt cereal cornflake granola muesli porridge "
               "tortilla pitta pita naan bagel baguette brioche croissant biscuit cracker crouton breadcrumb panko pastry cake "
               "muffin scone crumpet pancake waffle cookie wrapper filo phyllo dough stuffing matzo matzoh hominy grain "
               "wheatgerm bran malt popcorn chip cone ciabatta focaccia sourdough bun roll teacake shortbread flapjack "
                "rusk toast farina grits vermicelli udon soba ramen pie tart crust taco oatcake grissini basmati bucatini farfalle orecchiette conchiglie tortellini"),
    "LEGUME": ("bean pea lentil chickpea tofu tempeh edamame hummus soy soya miso natto flageolet cannellini borlotti haricot "
               "pinto mung peanut dal dhal gram lupin"),
    "NUT_SEED": ("nut almond walnut pecan pistachio cashew hazelnut macadamia chestnut seed sesame sunflower poppy chia flax "
                 "linseed coconut cocoa cacao marzipan praline pinenut"),
    "SWEETENER": ("sugar honey syrup molasses treacle caramel jaggery agave stevia sweetener icing fondant fudge marshmallow "
                  "candy chocolate sprinkle grenadine jelly honeycomb glucose toffee nougat"),
    "CONDIMENT": ("sauce ketchup catsup vinegar mustard mayonnaise dressing vinaigrette chutney relish piccalilli salsa pesto "
                  "gravy stock broth bouillon soup wasabi harissa tabasco tamari worcestershire marmite sriracha gochujang "
                  "hoisin tahini aioli ponzu mirin mayo tzatziki raita dashi"),
    "HERB_SPICE": ("basil thyme rosemary oregano sage parsley coriander mint dill chive tarragon marjoram bay chervil savory "
                   "lavender cumin paprika nutmeg mace cinnamon clove cardamom turmeric cayenne saffron allspice anise caraway "
                   "fenugreek nigella sumac masala curry vanilla extract essence seasoning spice herb peppercorn "
                   "ginger galangal asafoetida annatto juniper zaatar ajwain kalonji lemongrass tikka korma tandoori chipotle hanout"),
}
WEAK_WORDS = frozenset(fold(w)[0] for w in (
    "ginger chilli chili chile mushroom olive marrow salad pickle chip cone game jelly chocolate squash gin port bay "
    "savory clove roll date seed sprout corn grain mustard soda").split())
# the dictionary is built once: word -> (category, strength)
WORD_CAT: dict[str, tuple[str, str]] = {}
for _cat, _text in CATEGORY_WORDS.items():
    for _w in _text.split():
        _t = fold(_w)
        if len(_t) == 1:
            WORD_CAT.setdefault(_t[0], (_cat, "W" if _t[0] in WEAK_WORDS else "S"))

# exact culinary phrases that beat the head-word scan: (tokens, category | None, special | None, rule id, strength, fit)
_PH = [
    # waters that are drinks (ledger precedent: mineral water, soda water, tonic water are BEVERAGE)
    ("sparkling water", "BEVERAGE", None, "water_drink", "S", EXACT), ("soda water", "BEVERAGE", None, "water_drink", "S", EXACT),
    ("mineral water", "BEVERAGE", None, "water_drink", "S", EXACT), ("tonic water", "BEVERAGE", None, "water_drink", "S", EXACT),
    ("coconut water", "BEVERAGE", None, "water_drink", "S", EXACT),
    ("rose water", "HERB_SPICE", None, "flavouring_water", "W", APPROX), ("rosewater", "HERB_SPICE", None, "flavouring_water", "W", APPROX),
    ("orange flower water", "HERB_SPICE", None, "flavouring_water", "W", APPROX),
    ("orange blossom water", "HERB_SPICE", None, "flavouring_water", "W", APPROX),
    # leavening and raising agents have no vocabulary value
    ("cream of tartar", None, "LEAVENING_AGENT", "leavening", "S", NONE), ("baking powder", None, "LEAVENING_AGENT", "leavening", "S", NONE),
    ("baking soda", None, "LEAVENING_AGENT", "leavening", "S", NONE), ("bicarbonate of soda", None, "LEAVENING_AGENT", "leavening", "S", NONE),
    ("bicarbonate", None, "LEAVENING_AGENT", "leavening", "S", NONE), ("sodium bicarbonate", None, "LEAVENING_AGENT", "leavening", "S", NONE),
    ("yeast", None, "LEAVENING_AGENT", "leavening", "S", NONE),
    # not butter / not cream / not milk of the dairy head
    ("peanut butter", "NUT_SEED", None, "nut_butter", "S", EXACT), ("almond butter", "NUT_SEED", None, "nut_butter", "S", EXACT),
    ("cashew butter", "NUT_SEED", None, "nut_butter", "S", EXACT), ("nut butter", "NUT_SEED", None, "nut_butter", "S", EXACT),
    ("cocoa butter", "NUT_SEED", None, "nut_butter", "S", EXACT), ("shea butter", "FAT_OIL", None, "fat", "S", EXACT),
    ("butter bean", "LEGUME", None, "bean", "S", EXACT), ("water chestnut", "VEGETABLE", None, "water_chestnut", "S", EXACT),
    ("vegan butter", "FAT_OIL", None, "plant_fat", "S", EXACT), ("vegan margarine", "FAT_OIL", None, "plant_fat", "S", EXACT),
    ("vegetable suet", "FAT_OIL", None, "plant_fat", "S", EXACT), ("cooking spray", "FAT_OIL", None, "fat", "S", EXACT),
    ("icing sugar", "SWEETENER", None, "sugar", "S", EXACT), ("ice cream", "DAIRY", None, "dairy", "S", EXACT),
    ("salt cod", "SEAFOOD", None, "salt_fish", "S", EXACT), ("salt beef", "MEAT", None, "salt_meat", "S", EXACT),
    ("salt pork", "MEAT", None, "salt_meat", "S", EXACT),
    ("egg noodle", "CEREAL", None, "noodle", "S", EXACT), ("cream cheese", "DAIRY", None, "dairy", "S", EXACT),
    ("coconut milk", "DAIRY", None, "milk_analogue", "S", EXACT), ("rice milk", "DAIRY", None, "milk_analogue", "S", EXACT),
    ("milk powder", "DAIRY", None, "dairy", "S", EXACT), ("custard powder", "DAIRY", None, "dairy", "S", EXACT),
    ("sweet potato", "VEGETABLE", None, "veg", "S", EXACT), ("pepper sauce", "CONDIMENT", None, "sauce", "S", EXACT),
    ("hot sauce", "CONDIMENT", None, "sauce", "S", EXACT), ("liquid smoke", "HERB_SPICE", None, "flavouring", "W", APPROX),
    ("tomato ketchup", "CONDIMENT", None, "sauce", "S", EXACT), ("mushroom ketchup", "CONDIMENT", None, "sauce", "S", EXACT),
    ("curry paste", "HERB_SPICE", None, "spice_paste", "S", EXACT), ("curry powder", "HERB_SPICE", None, "spice", "S", EXACT),
    ("curry leaf", "HERB_SPICE", None, "spice", "S", EXACT), ("garam masala", "HERB_SPICE", None, "spice", "S", EXACT),
    ("bouquet garni", "HERB_SPICE", None, "spice", "S", EXACT), ("bay leaf", "HERB_SPICE", None, "herb", "S", EXACT),
    ("baby spinach", "VEGETABLE", None, "veg", "S", EXACT), ("corn tortilla", "CEREAL", None, "tortilla", "S", EXACT),
    ("tortilla chip", "CEREAL", None, "tortilla", "S", EXACT), ("corn tortilla chip", "CEREAL", None, "tortilla", "S", EXACT),
    ("french fry", "VEGETABLE", None, "potato", "S", EXACT), ("hash brown", "VEGETABLE", None, "potato", "S", EXACT),
    ("star anise", "HERB_SPICE", None, "spice", "S", EXACT), ("pine nut", "NUT_SEED", None, "nut", "S", EXACT),
    ("brazil nut", "NUT_SEED", None, "nut", "S", EXACT), ("onion seed", "HERB_SPICE", None, "spice", "S", EXACT),
    ("cocktail stick", None, "NON_FOOD", "utensil", "S", NONE), ("scallop shell", None, "NON_FOOD", "utensil", "S", NONE),
    ("baking paper", None, "NON_FOOD", "utensil", "S", NONE), ("kitchen paper", None, "NON_FOOD", "utensil", "S", NONE),
    ("greaseproof paper", None, "NON_FOOD", "utensil", "S", NONE), ("baking parchment", None, "NON_FOOD", "utensil", "S", NONE), ("sponge finger", "CEREAL", None, "biscuit", "S", EXACT),
    ("wonton wrapper", "CEREAL", None, "pastry", "S", EXACT), ("rice vinegar", "CONDIMENT", None, "vinegar", "S", EXACT),
    ("rice wine", "BEVERAGE", None, "drink", "S", EXACT), ("wild rice", "CEREAL", None, "rice", "S", EXACT),
    ("wild rabbit", "MEAT", None, "meat", "S", EXACT), ("water cress", "VEGETABLE", None, "veg", "S", EXACT),
    ("tea leaf", "BEVERAGE", None, "drink", "S", EXACT), ("petit pois", "LEGUME", None, "pea", "S", EXACT),
    ("ras el hanout", "HERB_SPICE", None, "spice", "S", EXACT), ("za atar", "HERB_SPICE", None, "spice", "S", EXACT),
    ("mange tout", "VEGETABLE", None, "veg", "S", EXACT), ("spring green", "VEGETABLE", None, "veg", "S", EXACT),
    ("food colouring", None, "ADDITIVE", "additive", "S", NONE), ("balsamic glaze", "CONDIMENT", None, "sauce", "S", EXACT), ("coffee bean", "BEVERAGE", None, "drink", "S", EXACT),
    ("cocoa bean", "NUT_SEED", None, "cocoa", "S", EXACT), ("vanilla bean", "HERB_SPICE", None, "spice", "S", EXACT),
    ("vanilla pod", "HERB_SPICE", None, "spice", "S", EXACT), ("lemon verbena", "HERB_SPICE", None, "herb", "S", EXACT),
    ("kaffir lime", "HERB_SPICE", None, "herb", "S", EXACT), ("lime leaf", "HERB_SPICE", None, "herb", "S", EXACT),
    ("juniper berry", "HERB_SPICE", None, "spice", "S", EXACT), ("allspice berry", "HERB_SPICE", None, "spice", "S", EXACT), ("salad cream", "CONDIMENT", None, "sauce", "S", EXACT),
    ("lemon curd", "FRUIT", None, "preserve", "S", EXACT), ("coconut cream", "NUT_SEED", None, "coconut", "S", EXACT),
    ("creamed coconut", "NUT_SEED", None, "coconut", "S", EXACT), ("mince pie", "CEREAL", None, "pie", "S", EXACT), ("nutritional yeast", None, "LEAVENING_AGENT", "leavening", "S", NONE),
]
_PH += [(f"{w} seed", "HERB_SPICE", None, "spice_seed", "S", EXACT) for w in (
    "celery caraway fennel dill anise coriander cumin mustard nigella fenugreek kalonji ajwain onion cardamom").split()]
PHRASES: list[tuple[tuple[str, ...], str | None, str | None, str, str, str]] = sorted(
    ((fold(p), c, sp, rid, st, fit) for p, c, sp, rid, st, fit in _PH), key=lambda r: -len(r[0]))

CUT_WORDS = frozenset(fold(w)[0] for w in "steak chop cutlet rib breast thigh wing mince tenderloin sirloin rump shank hock liver "
                      "meat".split())
SPICE_PEPPER_MODS = frozenset(fold(w)[0] for w in "black white pink lemon cayenne sichuan szechuan ground cracked".split())
SPICE_FORM = frozenset({"powder", "granule", "flake", "paste"})
SPICE_FORM_BASES = frozenset(fold(w)[0] for w in "onion garlic chilli chili chile ginger pepper mustard".split())
SALT_PLAIN_MODS = frozenset(fold(w)[0] for w in "sea rock kosher table flaky fine coarse pink himalayan maldon iodized iodised "
                            "cooking curing".split())
SALT_SEASONED_MODS = frozenset(fold(w)[0] for w in "celery garlic onion seasoned".split())
WATER_TOKENS = frozenset(fold(w)[0] for w in "water ice cube hot cold boiling warm tap iced crushed filtered lukewarm".split())
ADDITIVE_WORDS = frozenset(fold(w)[0] for w in "gelatine gelatin agar pectin xanthan citric msg potash rennet glycerine lye "
                           "glycerin colouring coloring xylitol glitter lustre".split())
NON_FOOD_HEADS = frozenset(fold(w)[0] for w in (
    "saucepan colander bowl spoon knife muslin brush sieve whisk skewer tin foil film string pot dish tray board "
    "cutter mould mold thermometer grater peeler processor blender mixer oven hob pin ramekin jar bottle lid spatula tongs "
    "scissors label card scale piping").split())
NEW_VALUE_NOTES: Mapping[str, str] = {
    "WATER": "water and ice are a cooking medium, not a beverage; BEVERAGE is the closest existing value",
    "SALT_MINERAL": "salt is a mineral seasoning, not a spice or herb; HERB_SPICE is the closest existing value",
    "LEAVENING_AGENT": "chemical or biological raising agents fit no existing value",
    "ADDITIVE": "gelling, thickening and flavour-enhancing additives fit no existing value",
    "STOCK_BROTH": "stock and bouillon are cooking liquids, not condiments; CONDIMENT is the closest existing value",
    "NON_FOOD": "not a food (utensil or lexicon artefact): no category; consider deprecating the ING instead",
}
APPROX_WORDS: Mapping[str, str] = {w: "STOCK_BROTH" for w in ("stock", "broth", "bouillon", "soup")}
DUAL_USE_NOTES: Mapping[str, str] = {
    "ginger": "spice or fresh vegetable", "chilli": "fresh vegetable or dried spice", "chili": "fresh vegetable or dried spice",
    "chile": "fresh vegetable or dried spice", "mushroom": "fungus, no fungus value, the ledger files other mushrooms under FRUIT",
    "olive": "fruit botanically, the ledger files olives under VEGETABLE", "mustard": "prepared condiment or spice seed",
    "marrow": "bone marrow or vegetable marrow", "chocolate": "confection or cocoa product (the ledger files chocolate under NUT_SEED)",
    "jelly": "set fruit preserve or gelatine dessert", "soda": "club soda or bicarbonate of soda", "coriander": "herb leaf or spice seed", "clove": "spice or garlic clove",
    "salad": "dish, not an ingredient", "pickle": "preserved vegetable or relish", "curry": "spice blend or dish",
    "game": "generic meat word", "gin": "spirit (the ledger files gin under CEREAL)", "port": "wine or harbour word",
    "squash": "vegetable or cordial", "date": "fruit or calendar word", "bay": "herb or place word", "roll": "bread or verb",
    "seed": "generic word", "peel": "fruit rind or verb", "zest": "fruit rind or verb", "wheat": "grain or flour",
    "grain": "generic word", "corn": "vegetable or cereal grain", "cream": "dairy cream or cream-like product",
    "essence": "flavouring", "extract": "flavouring", "chip": "fried potato or crisp or chocolate chip", "cone": "edible cone or other",
    "sprout": "sprouted vegetable or seed", "savory": "herb or adjective", "gram": "unit or pulse"}


@dataclass(frozen=True)
class Lex:
    category: str | None
    rule: str
    strength: str = "S"          # S unambiguous word / W ambiguous (dual-use) word
    fit: str = EXACT             # EXACT / APPROX (closest existing value) / NONE (no existing value fits)
    special: str | None = None   # a suggested NEW value (WATER, SALT_MINERAL, LEAVENING_AGENT, ADDITIVE, STOCK_BROTH, NON_FOOD)
    alt: str | None = None
    note: str = ""


def _contains(tokens: tuple[str, ...], phrase: tuple[str, ...]) -> bool:
    n = len(phrase)
    return n > 0 and any(tokens[i:i + n] == phrase for i in range(len(tokens) - n + 1))


def lexical(tokens: tuple[str, ...]) -> Lex | None:
    """Culinary class of an ingredient name from its folded tokens, or None when no rule applies."""
    if not tokens:
        return None
    last = tokens[-1]
    for ph, cat, special, rid, st, fit in PHRASES:
        if _contains(tokens, ph):
            return Lex(cat, rid, st, fit, special, note="")
    tset = set(tokens)
    if last in NON_FOOD_HEADS:
        return Lex(None, "non_food_head", "S", NONE, "NON_FOOD")
    if tset <= WATER_TOKENS and ("water" in tset or "ice" in tset):
        return Lex("BEVERAGE", "water", "S", APPROX, "WATER")
    if last == "salt":
        mods = set(tokens[:-1])
        if not mods or mods <= SALT_PLAIN_MODS:
            return Lex("HERB_SPICE", "salt", "S", APPROX, "SALT_MINERAL", "CONDIMENT")
        if mods <= SALT_SEASONED_MODS:
            return Lex("HERB_SPICE", "seasoned_salt", "S", EXACT)
    if tset & ADDITIVE_WORDS:
        return Lex(None, "additive", "S", NONE, "ADDITIVE")
    if tset & SPICE_FORM and tset & SPICE_FORM_BASES:
        return Lex("HERB_SPICE", "spice_form", "S", EXACT)
    if "pepper" in tset:
        if tset & SPICE_PEPPER_MODS:
            return Lex("HERB_SPICE", "pepper_spice", "S", EXACT)
        if last == "pepper":
            return Lex("VEGETABLE", "pepper_veg", "W", EXACT, alt="HERB_SPICE", note="vegetable pepper or spice pepper")
    for pos in range(len(tokens) - 1, -1, -1):
        tok = tokens[pos]
        hit = WORD_CAT.get(tok)
        if hit is None:
            continue
        if tok in CUT_WORDS:                                         # 'tuna steak', 'salmon fillet': the animal word decides
            animal = next(((t, WORD_CAT[t]) for t in reversed(tokens[:pos]) if t in WORD_CAT and WORD_CAT[t][0] in ("SEAFOOD", "MEAT")), None)
            if animal:
                tok, hit = animal
        cat, st = hit
        if tok in APPROX_WORDS:
            return Lex(cat, f"word:{tok}", st, APPROX, APPROX_WORDS[tok])
        note = DUAL_USE_NOTES.get(tok, "")
        alt = {"ginger": "VEGETABLE", "chilli": "HERB_SPICE", "chili": "HERB_SPICE", "chile": "HERB_SPICE",
               "olive": "FRUIT", "mustard": "HERB_SPICE", "chocolate": "NUT_SEED"}.get(tok)
        return Lex(cat, f"word:{tok}", st, EXACT, None, alt, note)
    return None


# ============================================================================================ proposal
@dataclass(frozen=True)
class Evidence:
    """Everything known about one ING that the proposal may use. `registry_group` is the SR group of the curated identity."""
    name: str
    registry_kind: str | None = None          # DIRECT / UK_US / DEFAULT_FORM / APPROX / NO_SR_EQUIVALENT / NOT_A_FOOD / AMBIGUOUS
    registry_group: str | None = None
    registry_description: str | None = None
    legacy_group: str | None = None
    legacy_description: str | None = None
    legacy_band: str | None = None
    precedent: Mapping[str, int] = field(default_factory=dict)     # labelled ING with the same head word: category -> n


@dataclass(frozen=True)
class Proposal:
    category: str
    basis: str
    confidence: str
    sr_food_group: str
    sr_description: str
    conflicts: str
    alt_category: str
    new_category_suggestion: str
    registry_kind: str
    legacy_band: str


def _precedent_flag(cat: str, prec: Mapping[str, int], head: str) -> str:
    total = sum(prec.values())
    if total >= 2 and cat:
        top, n = max(prec.items(), key=lambda kv: (kv[1], kv[0]))
        if top != cat and n / total >= 0.6:
            return f"PRECEDENT_DISAGREES(head={head}: ledger has {n}/{total} as {top})"
    return ""


def propose(ev: Evidence, vocabulary: Iterable[str]) -> Proposal:
    """One proposal from the evidence. A returned category is always in `vocabulary` or empty (checked)."""
    vocab = frozenset(vocabulary)
    toks = fold(ev.name)
    lex = lexical(toks)
    flags: list[str] = []
    bases: list[str] = []
    sr_info = ("", "", "")             # (group, description, source tag)
    sr_cat: str | None = None
    quality = ""
    if ev.registry_kind in CURATED_KINDS | {"APPROX"} and ev.registry_group:
        sr_info = (ev.registry_group, ev.registry_description or "", "REGISTRY_SR")
        sr_cat = sr_category(ev.registry_group, ev.registry_description)
        quality = "curated" if ev.registry_kind in CURATED_KINDS else "approx"
    elif ev.registry_kind is not None and ev.registry_kind not in CURATED_KINDS | {"APPROX"}:
        flags.append(f"REGISTRY_UNMAPPABLE({ev.registry_kind})")
    elif ev.legacy_group and ev.legacy_band in USABLE_LEGACY_BANDS:
        sr_info = (ev.legacy_group, ev.legacy_description or "", "LEGACY_SR")
        sr_cat = sr_category(ev.legacy_group, ev.legacy_description)
        quality = "legacy_" + ev.legacy_band.lower()
    group, desc, src_tag = sr_info
    if group and sr_cat is None:
        flags.append(f"SR_GROUP_HAS_NO_VOCABULARY_ITEM({group})")
    lex_cat = lex.category if lex else None
    suggestion = lex.special if lex and lex.special else ""
    alt = (lex.alt or "") if lex else ""
    cat, conf = "", LOW
    head = toks[-1] if toks else ""

    if lex and lex.fit == NONE and lex_cat is None:
        # the culinary class has no existing value: propose nothing, say which value would fit
        cat, conf = "", LOW
        bases.append(f"LEXICAL({lex.rule})")
        flags.append("NO_VOCABULARY_FIT")
        if sr_cat:
            bases.append(f"{src_tag}({quality}:{group})")
            flags.append(f"SR_GROUP_WOULD_MAP_TO({sr_cat})_BUT_CULINARY_CLASS_DIFFERS")
    elif lex_cat and sr_cat and lex_cat == sr_cat:
        cat = lex_cat
        bases += [f"LEXICAL({lex.rule})", f"{src_tag}({quality}:{group})"]
        exact = lex.fit == EXACT and lex.strength == "S"
        strong_src = quality in ("curated", "approx", "legacy_high")
        conf = HIGH if exact and strong_src else MEDIUM
        if lex.fit == APPROX:
            flags.append("NO_EXACT_FIT")
        if lex.strength == "W":
            flags.append("DUAL_USE")
    elif lex_cat and sr_cat:
        cat, conf = lex_cat, MEDIUM if lex.strength == "S" else LOW
        bases += [f"LEXICAL({lex.rule})", f"{src_tag}({quality}:{group})"]
        flags.append(f"SR_GROUP_DISAGREES(SR group '{group}' files under {sr_cat}, culinary class is {lex_cat})")
        alt = alt or sr_cat
        if lex.fit == APPROX:
            flags.append("NO_EXACT_FIT")
    elif lex_cat:
        cat = lex_cat
        bases.append(f"LEXICAL({lex.rule})")
        conf = MEDIUM if lex.strength == "S" and lex.fit == EXACT else LOW
        if lex.fit == APPROX:
            flags.append("NO_EXACT_FIT")
        if lex.strength == "W":
            flags.append("DUAL_USE")
    elif sr_cat:
        cat = sr_cat
        bases.append(f"{src_tag}({quality}:{group})")
        if quality == "curated" and group not in LEAKY_GROUPS:
            conf = HIGH
        elif quality in ("curated", "approx", "legacy_high") and group not in LEAKY_GROUPS:
            conf = MEDIUM
        elif quality == "curated":
            conf = MEDIUM
            flags.append(f"LEAKY_SR_GROUP({group})")
        else:
            conf = LOW
            if group in LEAKY_GROUPS:
                flags.append(f"LEAKY_SR_GROUP({group})")
        if quality.startswith("legacy"):
            conf = LOW                          # a name the curated registry does not hold and no culinary rule covers
            flags.append("LEGACY_MATCH_ONLY")  # (backtest: 11 of 16 legacy-only HIGH-band matches agree with the ledger)
    else:
        bases.append("NONE")
        flags.append("NO_BASIS")

    if lex and lex.special == "NON_FOOD":
        flags.append("NOT_A_FOOD_SUSPECT")
    if suggestion and suggestion != "NON_FOOD":
        flags.append(f"NEW_VALUE_SUGGESTED({suggestion})")
    if suggestion == "NON_FOOD":
        flags.append("NOT_A_FOOD_CONSIDER_DEPRECATING")
        suggestion = ""
    if lex and lex.note and cat and lex.strength == "W":
        flags.append(f"DUAL_USE_NOTE({lex.note})")
    if cat:
        pf = _precedent_flag(cat, ev.precedent, head)
        if pf:
            flags.append(pf)
    if cat and cat not in vocab:                                     # the vocabulary guard: never invent a value
        flags.append(f"VALUE_NOT_IN_VOCABULARY({cat})")
        cat, conf = "", LOW
    if alt and alt not in vocab:
        alt = ""
    if alt == cat:
        alt = ""
    return Proposal(cat, "|".join(bases), conf, group, desc, "; ".join(f for f in flags if f), alt, suggestion,
                    ev.registry_kind or ("LEGACY_FALLBACK" if src_tag == "LEGACY_SR" else ""), ev.legacy_band or "")


# ============================================================================================ inputs (read only)
def read_ing_ledger(path: Path) -> dict[str, dict]:
    """Latest version of every ING id (ACTIVE only): name and category ('' when none)."""
    latest: dict[str, dict] = {}
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                if r["id"] not in latest or r["version"] > latest[r["id"]]["version"]:
                    latest[r["id"]] = r
    return {i: {"name": r["canonical_name"], "category": r.get("category") or ""}
            for i, r in latest.items() if r.get("status") == "ACTIVE"}


def read_aliases(path: Path) -> dict[str, tuple[str, ...]]:
    out: dict[str, set] = defaultdict(set)
    latest: dict[str, dict] = {}
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                if r["id"] not in latest or r["version"] > latest[r["id"]]["version"]:
                    latest[r["id"]] = r
    for r in latest.values():
        if r.get("status") == "ACTIVE" and r.get("language") == "en" and r.get("ingredient_id"):
            out[r["ingredient_id"]].add(r.get("normalized") or r.get("surface") or "")
    return {k: tuple(sorted(v)) for k, v in out.items()}


def registry_entry(registry: Mapping, name: str, aliases: Iterable[str]):
    """Canonical name first; else ACTIVE aliases, only when every alias that hits gives one entry (as sr_identity does)."""
    e = registry.get(M.normalise(name))
    if e is not None:
        return e
    hits = {registry[k] for a in aliases if (k := M.normalise(a)) in registry}
    return next(iter(hits)) if len(hits) == 1 else None


def read_legacy_rank1(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["rank"] == "1" and r["fdc_id"] != "":
                out[r["ing_id"]] = r
    return out


def read_mentions(path: Path) -> dict[str, tuple[int, int]]:
    """ING id -> (non-BBC ingredient-line mentions, all-family mentions) from vocab_corpus_frequency_v1.parquet."""
    import pandas as pd
    df = pd.read_parquet(path)
    df = df[df["vocab_type"] == "ING"]
    allm = df.groupby("vocab_id")["mention_count"].sum()
    nb = df[df["source_family"] != BBC_FAMILY].groupby("vocab_id")["mention_count"].sum()
    return {i: (int(nb.get(i, 0)), int(allm[i])) for i in allm.index}


def read_s177_items(path: Path) -> dict[str, int]:
    """ING id -> S177 census item count, from the category-blocked counter (the ING that only a category blocks from ABSENT)."""
    rep = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k.replace("__", "-", 1): int(v) for k, v in rep.get("category_blocked_items", {}).items()}


def head_precedent(ing: Mapping[str, dict], exclude: str | None = None) -> dict[str, Counter]:
    """head word -> Counter of the categories of the labelled ACTIVE ING that end in that word (information and flags only)."""
    out: dict[str, Counter] = defaultdict(Counter)
    for i, r in ing.items():
        if r["category"] and i != exclude:
            t = fold(r["name"])
            if t:
                out[t[-1]][r["category"]] += 1
    return out


@dataclass(frozen=True)
class Inputs:
    ing: Mapping[str, dict]
    registry: Mapping
    aliases: Mapping[str, tuple[str, ...]]
    legacy: Mapping[str, dict]
    groups: Mapping[int, str]            # fdc_id -> SR food group (registry foods)
    descriptions: Mapping[int, str]
    mentions: Mapping[str, tuple[int, int]]
    s177_items: Mapping[str, int]
    router_groups: Mapping[str, str]     # ING -> SR group of the router's rank-1 identity (shipped content table)
    vocabulary: tuple[str, ...]


def build_evidence(i: str, inp: Inputs, precedent: Mapping[str, Counter], *, exclude_self: bool = False) -> Evidence:
    name = inp.ing[i]["name"]
    e = registry_entry(inp.registry, name, inp.aliases.get(i, ()))
    leg = inp.legacy.get(i)
    prec = dict(precedent.get(fold(name)[-1] if fold(name) else "", {}))
    if exclude_self and inp.ing[i]["category"]:
        h = fold(name)[-1] if fold(name) else ""
        if h and prec.get(inp.ing[i]["category"]):
            prec[inp.ing[i]["category"]] -= 1
            prec = {k: v for k, v in prec.items() if v > 0}
    return Evidence(
        name=name, registry_kind=e.kind if e else None,
        registry_group=inp.groups.get(e.fdc_id) if e and e.fdc_id else None,
        registry_description=inp.descriptions.get(e.fdc_id) if e and e.fdc_id else None,
        legacy_group=(leg or {}).get("sr_category") or None, legacy_description=(leg or {}).get("sr_description") or None,
        legacy_band=(leg or {}).get("confidence_band") or None, precedent=prec)


def load_inputs(root: Path, *, sr_dir: Path | None = None, paths: Mapping[str, str] | None = None) -> Inputs:
    from culinarystate.mechanism import evidence_gates as EG
    from culinarystate.mechanism import sr_identity as SI
    p = {"ing": ING_LEDGER, "alias": ALIAS_LEDGER, "registry": REGISTRY, "legacy": LEGACY, "vocab": VOCAB_FREQ,
         "s177": S177_FULL, **(paths or {})}
    root = Path(root)
    ing = read_ing_ledger(root / p["ing"])
    registry = M.load_registry(root / p["registry"])
    sr = Path(sr_dir) if sr_dir else SI.default_dir(root)
    fdcs = {e.fdc_id for e in registry.values() if e.fdc_id}
    groups, descs = SI.sr_food_groups(sr, fdcs), SI.sr_descriptions(sr, fdcs)
    table = root / "registry" / "ing_sr_target_content_draft_v1.csv"
    router = {k: v[1] for k, v in EG.read_table_full(table)[2].items()} if table.exists() else {}
    vocabulary = tuple(sorted({r["category"] for r in ing.values() if r["category"]}))
    return Inputs(ing, registry, read_aliases(root / p["alias"]), read_legacy_rank1(root / p["legacy"]), groups, descs,
                  read_mentions(root / p["vocab"]), read_s177_items(root / p["s177"]), router, vocabulary)


# ============================================================================================ build and render
def crosswalk_confirms(category: str, router_group: str | None) -> bool | None:
    """Would the S177 ABSENT crosswalk accept this ING category against the SR group of the router's rank-1 identity?"""
    from culinarystate.mechanism import evidence_gates as EG
    if not category or not router_group:
        return None
    return EG.category_matches(category, router_group)


def build_rows(inp: Inputs) -> list[dict]:
    """One row per ACTIVE ING without a category, ordered by non-BBC corpus mentions (then all-family mentions, then id)."""
    precedent = head_precedent(inp.ing)
    todo = [i for i, r in inp.ing.items() if not r["category"]]
    todo.sort(key=lambda i: (-inp.mentions.get(i, (0, 0))[0], -inp.mentions.get(i, (0, 0))[1], i))
    rows = []
    for rank, i in enumerate(todo, 1):
        pr = propose(build_evidence(i, inp, precedent), inp.vocabulary)
        nb, allm = inp.mentions.get(i, (0, 0))
        rg = inp.router_groups.get(i)
        cw = crosswalk_confirms(pr.category, rg)
        s177 = inp.s177_items.get(i)
        conflicts = pr.conflicts
        if pr.category and cw is False and rg:
            conflicts = "; ".join(x for x in (conflicts, f"CROSSWALK_WOULD_NOT_CONFIRM({pr.category} vs SR group '{rg}')") if x)
        rows.append({
            "ing_id": i, "name": inp.ing[i]["name"], "proposed_category": pr.category, "basis": pr.basis,
            "confidence": pr.confidence, "sr_food_group": rg or pr.sr_food_group,
            "mention_items": "" if s177 is None else str(s177), "human_decision": "", "rank": str(rank),
            "mention_nonbbc": str(nb), "mention_all_families": str(allm), "conflicts": conflicts,
            "alt_category": pr.alt_category, "new_category_suggestion": pr.new_category_suggestion,
            "registry_kind": pr.registry_kind, "sr_description": pr.sr_description, "legacy_band": pr.legacy_band,
            "crosswalk_confirms": "" if cw is None else ("YES" if cw else "NO"),
            "unlocks_absent_vitc": "YES" if (s177 is not None and cw) else ("NO" if s177 is not None else ""),
            "status": STATUS})
    return rows


PROTECTED_OUTPUT_DIRS = ("ledgers", "data", "exports", "annotation/gold", "src/culinarystate/composition")


def checked_output(root: Path, rel: str | Path) -> Path:
    """The output path, refusing anywhere a ledger, raw data or the Mac's composition layer lives (this lane writes no ledger)."""
    root = Path(root).resolve()
    target = (root / rel).resolve()
    try:
        parts = target.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(f"output {target} is outside the repository root") from exc
    for d in PROTECTED_OUTPUT_DIRS:
        if parts == d or parts.startswith(d + "/"):
            raise ValueError(f"refusing to write inside {d}/ (this lane edits no ledger and no composition code)")
    return target


def write_csv(path: Path, rows: Sequence[Mapping], *, overwrite: bool) -> str:
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite {path} (pass --overwrite)")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def top_sheet(rows: Sequence[Mapping], n: int = 100) -> str:
    """The one-sitting confirmation sheet: one tickable line per ING, the first `n` by impact."""
    lines = [
        "# ING category proposals: top 100 for human confirmation (S178 INGCAT)", "",
        "Status: **AI_DRAFTED / PROPOSED / NON_CITABLE.** Nothing below is a decision. No ledger was edited. A category here is a "
        "PROPOSAL for an ACTIVE ING that has none; it comes from the existing ING category vocabulary only.", "",
        "How to use: tick `[x]` to ACCEPT the proposal; write `CHANGE:<CATEGORY>` or `REJECT` after the line otherwise. "
        "Order is the ING's non-BBC corpus mention count (ingredient lines). `S177 items` is the S177 full-census item count for "
        "ING that only a missing category keeps out of the vitamin-C ABSENT rule. `unlocks` = confirming it would clear that "
        "block under the current S177 crosswalk.", "",
        "Confidence: HIGH = two bases agree on one existing value; MEDIUM = one decent basis or approximate fit; LOW = weak, "
        "conflicting or no existing value fits (proposal may be empty). Flags: NO_EXACT_FIT (closest existing value, a NEW value "
        "is suggested, not added), SR_GROUP_DISAGREES (the SR food group files it elsewhere), DUAL_USE, PRECEDENT_DISAGREES.", ""]
    for r in rows[:n]:
        bits = [f"- [ ] {r['rank']}. `{r['ing_id']}` **{r['name']}** -> **{r['proposed_category'] or '(none fits)'}** [{r['confidence']}]"]
        if r["alt_category"]:
            bits.append(f"alt {r['alt_category']}")
        bits.append(f"SR: {r['sr_food_group'] or 'none'}")
        bits.append(f"{int(r['mention_nonbbc']):,} mentions")
        if r["mention_items"]:
            bits.append(f"S177 items {int(r['mention_items']):,}")
        if r["unlocks_absent_vitc"] == "YES":
            bits.append("unlocks ABSENT")
        elif r["unlocks_absent_vitc"] == "NO":
            bits.append("does NOT unlock (crosswalk)")
        if r["new_category_suggestion"]:
            bits.append(f"suggest NEW value {r['new_category_suggestion']}")
        short = [c.split("(")[0] for c in r["conflicts"].split("; ") if c and not c.startswith("NEW_VALUE_SUGGESTED")]
        if short:
            bits.append("flags: " + ", ".join(dict.fromkeys(short)))
        lines.append(" | ".join(bits))
    lines += ["", "## Suggested NEW category values (not added; a human decides)", ""]
    used = sorted({r["new_category_suggestion"] for r in rows if r["new_category_suggestion"]})
    lines += [f"- `{v}`: {NEW_VALUE_NOTES[v]}." for v in used]
    lines += ["- Adopting any of these also needs a row in `CATEGORY_CROSSWALK` (mechanism/evidence_gates.py), or the ING stays "
              "UNKNOWN under the S177 ABSENT rule. This sheet does not touch the crosswalk.", ""]
    return "\n".join(lines)


def full_member_projection(rows: Sequence[Mapping]) -> dict:
    """Exact member-level projection on the S177 FULL census (35,256,601 items): for each scenario, how many ING and how many
    S177 items would have their OWN member state move from UNKNOWN (CATEGORY_EMPTY) to ABSENT, i.e. the ING that the S177 census
    counted as blocked only by the category and that the proposed value clears under the current crosswalk. This is not a route
    count (lot-level and route changes need a census run); it is the exact count of items whose ING stops being blocked."""
    out = {}
    for name, ov in scenarios(rows).items():
        hit = [r for r in rows if r["ing_id"] in ov and r["unlocks_absent_vitc"] == "YES"]
        out[name] = {"ing_confirmed": len(ov), "ing_clearing_the_s177_category_block": len(hit),
                     "s177_full_items_member_unknown_to_absent": sum(int(r["mention_items"]) for r in hit)}
    return out


def summarise(rows: Sequence[Mapping], vocabulary: Sequence[str], n_labelled: int, backtest: Mapping | None) -> dict:
    conf = Counter(r["confidence"] for r in rows)
    cat = Counter(r["proposed_category"] or "NONE" for r in rows)
    nb_total = sum(int(r["mention_nonbbc"]) for r in rows)
    by_conf_mentions = Counter()
    for r in rows:
        by_conf_mentions[r["confidence"]] += int(r["mention_nonbbc"])
    flags = Counter()
    for r in rows:
        for c in r["conflicts"].split("; "):
            if c:
                flags[c.split("(")[0]] += 1
    new_vals = Counter(r["new_category_suggestion"] for r in rows if r["new_category_suggestion"])
    new_vals_mentions = Counter()
    for r in rows:
        if r["new_category_suggestion"]:
            new_vals_mentions[r["new_category_suggestion"]] += int(r["mention_nonbbc"])
    top100 = rows[:100]
    return {
        "tool_version": TOOL_VERSION, "status": STATUS, "counts_only": True,
        "active_ing_without_category": len(rows), "active_ing_with_category": n_labelled,
        "vocabulary": list(vocabulary),
        "by_confidence": dict(sorted(conf.items())), "by_proposed_category": dict(sorted(cat.items())),
        "nonbbc_mentions_total_of_uncategorised": nb_total,
        "nonbbc_mentions_by_confidence": dict(sorted(by_conf_mentions.items())),
        "top100_by_confidence": dict(sorted(Counter(r["confidence"] for r in top100).items())),
        "top100_nonbbc_mentions_share": round(sum(int(r["mention_nonbbc"]) for r in top100) / max(1, nb_total), 4),
        "flag_counts": dict(sorted(flags.items())),
        "new_value_suggestions_ing": dict(sorted(new_vals.items())),
        "new_value_suggestions_nonbbc_mentions": dict(sorted(new_vals_mentions.items())),
        "no_proposal": sum(1 for r in rows if not r["proposed_category"]),
        "s177_full_census_member_projection": full_member_projection(rows),
        "s177_category_blocked_ing": sum(1 for r in rows if r["mention_items"]),
        "s177_category_blocked_ing_proposed_and_confirmed_by_crosswalk": sum(1 for r in rows if r["unlocks_absent_vitc"] == "YES"),
        "backtest_vs_ledger_labels": backtest}


# ============================================================================================ backtest
def backtest(inp: Inputs) -> dict:
    """Run the engine on the ACTIVE ING that DO have a category (label hidden, its own label removed from the precedent) and count
    agreement with the ledger label by confidence. The ledger labels are FoodOn-derived and visibly noisy (gin under CEREAL,
    mushrooms under FRUIT), so this measures agreement, not truth, and covers the easier ING that FoodOn could classify."""
    precedent = head_precedent(inp.ing)
    res: dict[str, Counter] = defaultdict(Counter)
    for i, r in inp.ing.items():
        if not r["category"]:
            continue
        pr = propose(build_evidence(i, inp, precedent, exclude_self=True), inp.vocabulary)
        key = pr.confidence
        res[key]["n"] += 1
        if not pr.category:
            res[key]["no_proposal"] += 1
        elif pr.category == r["category"]:
            res[key]["agree"] += 1
        else:
            res[key]["disagree"] += 1
    out = {}
    for k in (HIGH, MEDIUM, LOW):
        c = res.get(k, Counter())
        made = c["agree"] + c["disagree"]
        out[k] = {"n": c["n"], "proposed": made, "agree": c["agree"], "disagree": c["disagree"], "no_proposal": c["no_proposal"],
                  "agreement_rate_of_proposed": round(c["agree"] / made, 3) if made else None}
    return out


# ============================================================================================ router-census overlay simulation
def _load_step17b():
    spec = importlib.util.spec_from_file_location("_step17b_rung_a_dryrun_ingcat", ROOT / "tools/step17b_rung_a_dryrun.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def overlay_gates(base, overlay: Mapping[str, str]):
    """EvidenceGates identical to `base` except that the ING category of each overlaid ING is the proposed one. Runtime only:
    the shipped table, the registry and every ledger are untouched. Returns (gates, number of overlaid ING that have a router
    identity). An overlaid ING with no identity cannot change any verdict (NO_USABLE_IDENTITY is tested first)."""
    from culinarystate.mechanism import evidence_gates as EG
    s = base.screen
    cats = dict(s.categories)
    applied = 0
    for ing, cat in overlay.items():
        if ing in cats:
            cats[ing] = (cat, cats[ing][1])
            applied += 1
    screen = EG.TargetPresenceScreen(s.floors, s.cands, s.values, cats, s.kinds)
    return EG.EvidenceGates(screen, presence=base.presence_on, context=base.context_on, provenance=base.provenance), applied


def _slice(rep: Mapping) -> dict:
    keep = ("items", "recipes_sampled", "texts_with_steps", "recipes_with_any_direct", "route", "route_ungated", "member_presence",
            "member_blocker", "member_absent_items", "category_blocked_items", "reason_counts", "gate_cross", "exceptions_by_class",
            "direct_ungated_cross", "prior_process_withheld", "direct_by_process")
    return {k: rep[k] for k in keep if k in rep}


def _delta(a: Mapping, b: Mapping) -> dict:
    out = {}
    for k in sorted(set(a) | set(b)):
        d = int(b.get(k, 0)) - int(a.get(k, 0))
        if d:
            out[k] = d
    return out


def scenarios(rows: Sequence[Mapping]) -> dict[str, dict[str, str]]:
    """Named overlays: ING -> proposed category. HIGH-only scenarios are the ones the brief asks for."""
    prop = [r for r in rows if r["proposed_category"]]
    high = [r for r in prop if r["confidence"] == HIGH]
    top100 = rows[:100]
    return {
        "A_top100_sheet_HIGH_only": {r["ing_id"]: r["proposed_category"] for r in top100 if r["confidence"] == HIGH and r["proposed_category"]},
        "B_first100_HIGH_proposals": {r["ing_id"]: r["proposed_category"] for r in high[:100]},
        "C_all_HIGH": {r["ing_id"]: r["proposed_category"] for r in high},
        "D_top100_sheet_HIGH_and_MEDIUM": {r["ing_id"]: r["proposed_category"] for r in top100
                                           if r["confidence"] in (HIGH, MEDIUM) and r["proposed_category"]},
        "E_all_HIGH_and_MEDIUM": {r["ing_id"]: r["proposed_category"] for r in prop if r["confidence"] in (HIGH, MEDIUM)}}


def simulate(rows: Sequence[Mapping], *, seed: str, size: int, workers: int, root: Path = ROOT) -> dict:
    """Router census over the seeded sample, once without and once per scenario with a runtime category overlay. Counts only."""
    from culinarystate.extraction.rung_a_measure import seeded_sample
    from culinarystate.mechanism import evidence_gates as EG
    from culinarystate.mechanism import router_census as RC
    from culinarystate.mechanism import router_demo as RD
    T17 = _load_step17b()
    families = ["FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS", "TASTESET"]      # the non-BBC families of the S177 runs
    ing_path = Path(root) / ING_LEDGER
    sha_before = hashlib.sha256(ing_path.read_bytes()).hexdigest()
    try:
        T17._baseline(root)
        baseline_before = "PASS"
    except Exception:  # noqa: BLE001
        baseline_before = "FAILED"
    status: dict = {}
    sample = seeded_sample(T17._stream(families, root, T17.corpus_records, status), seed, size)
    index = RD.EvidenceIndex.from_ledger(Path(RD.EVD_PATH))
    base = EG.EvidenceGates.load()
    target = "SVAR-000009"

    def run(gates) -> dict:
        return RC.census_from_records(sample, seed=seed, size=size, index=index, target_svar=target, workers=workers, gates=gates)

    base_rep = run(base)
    out_s: dict = {}
    for name, ov in scenarios(rows).items():
        gates, applied = overlay_gates(base, ov)
        rep = run(gates)
        out_s[name] = {
            "overlay_ing": len(ov), "overlay_ing_with_router_identity": applied,
            "census": _slice(rep),
            "delta_route": _delta(base_rep["route"], rep["route"]),
            "delta_reason_counts": _delta(base_rep["reason_counts"], rep["reason_counts"]),
            "delta_member_presence": _delta(base_rep["member_presence"], rep["member_presence"]),
            "delta_member_blocker": _delta(base_rep["member_blocker"], rep["member_blocker"]),
            "delta_member_absent_items": _delta(base_rep["member_absent_items"], rep["member_absent_items"]),
            "delta_recipes_with_any_direct": int(rep["recipes_with_any_direct"]) - int(base_rep["recipes_with_any_direct"]),
            "newly_absent_ing": sorted(k for k in rep["member_absent_items"] if k not in base_rep["member_absent_items"])}
    try:
        T17._baseline(root)
        baseline_after = "PASS"
    except Exception:  # noqa: BLE001
        baseline_after = "FAILED"
    sha_after = hashlib.sha256(ing_path.read_bytes()).hexdigest()
    s177 = json.loads((Path(root) / S177_1000).read_text(encoding="utf-8"))
    same = all(base_rep[k] == s177[k] for k in ("route", "reason_counts", "member_presence", "member_blocker", "member_absent_items",
                                                  "category_blocked_items", "gate_cross"))
    result = {
        "record": "INGCAT_ROUTER_OVERLAY_SIMULATION", "status": "AI_DRAFTED_SIMULATION_COUNTS_ONLY", "counts_only": True,
        "tool_version": TOOL_VERSION, "target_svar": target, "seed_sha256": hashlib.sha256(seed.encode()).hexdigest(),
        "sample_size_requested": size, "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC", "families": families,
        "family_status": dict(sorted(status.items())),
        "overlay_is_runtime_only": True, "ledger_written": False,
        "ing_ledger_sha256_before": sha_before, "ing_ledger_sha256_after": sha_after, "ing_ledger_unchanged": sha_before == sha_after,
        "protected_ledger_baseline_before": baseline_before, "protected_ledger_baseline_after": baseline_after,
        "baseline_reproduces_s177_1000": same, "baseline": _slice(base_rep), "scenarios": out_s}
    from culinarystate.quantity import rc2_dryrun as D
    D.assert_counts_only(result)
    return result


# ============================================================================================ CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", default=OUT_CSV)
    ap.add_argument("--sheet", default=OUT_SHEET)
    ap.add_argument("--summary", default=OUT_SUMMARY)
    ap.add_argument("--overwrite", action="store_true", help="replace the DRAFT outputs of an earlier run")
    ap.add_argument("--backtest-only", action="store_true", help="print the agreement with the ledger labels and stop")
    ap.add_argument("--simulate", action="store_true", help="also run the router-census overlay simulation")
    ap.add_argument("--sim-out", default=OUT_SIM)
    ap.add_argument("--seed", default="20261104")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--sr-dir", default=None, help="SR Legacy CSV directory (default: the repository's data/raw/fdc/sr_legacy)")
    a = ap.parse_args(argv)
    root = Path(a.root)
    inp = load_inputs(root, sr_dir=Path(a.sr_dir) if a.sr_dir else None)
    bt = backtest(inp)
    if a.backtest_only:
        print(json.dumps(bt, indent=1, sort_keys=True))
        return 0
    out_csv, sheet = checked_output(root, a.out), checked_output(root, a.sheet)
    sp, simp = checked_output(root, a.summary), checked_output(root, a.sim_out)
    rows = build_rows(inp)
    n_labelled = sum(1 for r in inp.ing.values() if r["category"])
    sha = write_csv(out_csv, rows, overwrite=a.overwrite)
    if sheet.exists() and not a.overwrite:
        raise FileExistsError(f"refusing to overwrite {sheet} (pass --overwrite)")
    sheet.parent.mkdir(parents=True, exist_ok=True)
    sheet.write_text(top_sheet(rows), encoding="utf-8")
    summ = summarise(rows, inp.vocabulary, n_labelled, bt)
    summ["csv_sha256"] = sha
    if sp.exists() and not a.overwrite:
        raise FileExistsError(f"refusing to overwrite {sp} (pass --overwrite)")
    sp.write_text(json.dumps(summ, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: summ[k] for k in ("active_ing_without_category", "by_confidence", "top100_by_confidence", "csv_sha256")}))
    if a.simulate:
        sim = simulate(rows, seed=a.seed, size=a.sample_size, workers=a.workers, root=root)
        if simp.exists() and not a.overwrite:
            raise FileExistsError(f"refusing to overwrite {simp} (pass --overwrite)")
        simp.write_text(json.dumps(sim, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"simulation": str(simp), "ing_ledger_unchanged": sim["ing_ledger_unchanged"],
                          "baseline_reproduces_s177_1000": sim["baseline_reproduces_s177_1000"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
