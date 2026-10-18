"""Unit catalogue v0 (data). Exact definitions are cited; conventions without a pinned authority are
marked NEEDS_SOURCE and must be checked by a human before any paper claim relies on them.

Three problems are never collapsed (SSOT §235.1):
  1. physical conversion (g<->kg, mL<->L)            -> `si` factor, EXACT_PHYSICAL
  2. culinary volume by locale (tbsp, cup, fl oz)     -> `conventions[locale]`, LOCALE_CONVENTION
  3. volume/count -> mass                             -> never here; needs a POR- record
"""
from __future__ import annotations

from dataclasses import dataclass, field

SOURCES = {
    "NIST_HB44_APPC": ("NIST Handbook 44, Appendix C — General Tables of Units of Measurement", "AUTHORITY", "VERIFIED_DEFINITION"),
    "UK_WMA_1985_SCH1": ("UK Weights and Measures Act 1985, Schedule 1 (imperial units)", "AUTHORITY", "VERIFIED_DEFINITION"),
    "CFR21_101_9": ("21 CFR 101.9(b)(5)(viii) — US nutrition-labeling household measures", "AUTHORITY", "VERIFIED_DEFINITION"),
    "SI_BROCHURE": ("BIPM SI Brochure (9th ed.) — SI prefixes; litre = 1 dm3", "AUTHORITY", "VERIFIED_DEFINITION"),
    "CONV_METRIC_SPOON": ("Metric culinary spoon convention (tsp 5 mL, tbsp 15 mL) — authority to cite", "CONVENTION", "NEEDS_SOURCE"),
    "CONV_AU_TBSP": ("Australian tablespoon 20 mL convention — authority to cite", "CONVENTION", "NEEDS_SOURCE"),
    "CONV_METRIC_CUP": ("Metric cup 250 mL convention (AU/NZ/CA/UK modern recipes) — authority to cite", "CONVENTION", "NEEDS_SOURCE"),
    "CONV_UK_DSP": ("UK dessertspoon 10 mL convention — authority to cite", "CONVENTION", "NEEDS_SOURCE"),
}


@dataclass(frozen=True)
class Unit:
    key: str
    unit_type: str          # PHYSICAL | CULINARY_VOLUME | COUNT_PORTION | PACKAGE | VERBAL_QUALITATIVE | REGIONAL | LENGTH
    dimension: str          # MASS | VOLUME | COUNT | LENGTH | NONE
    aliases: tuple[str, ...]
    si: float | None = None                     # exact factor to g / mL / cm
    si_source: str | None = None
    conventions: dict = field(default_factory=dict)   # locale -> (mL, source_key)
    note: str = ""


US_TSP, US_TBSP, US_CUP = 4.92892159375, 14.78676478125, 236.5882365
US_FLOZ, UK_FLOZ = 29.5735295625, 28.4130625

UNITS: tuple[Unit, ...] = (
    # ---- physical mass ----
    Unit("g", "PHYSICAL", "MASS", ("g", "gram", "grams", "gm", "gms", "gr", "grammes"), 1.0, "SI_BROCHURE"),
    Unit("kg", "PHYSICAL", "MASS", ("kg", "kilo", "kilos", "kilogram", "kilograms", "kgs"), 1000.0, "SI_BROCHURE"),
    Unit("mg", "PHYSICAL", "MASS", ("mg", "milligram", "milligrams"), 0.001, "SI_BROCHURE"),
    Unit("oz", "PHYSICAL", "MASS", ("oz", "ounce", "ounces", "ozs"), 28.349523125, "NIST_HB44_APPC",
         note="avoirdupois ounce; 'fl oz' is a different unit"),
    Unit("lb", "PHYSICAL", "MASS", ("lb", "lbs", "pound", "pounds"), 453.59237, "NIST_HB44_APPC"),
    # ---- physical volume ----
    Unit("ml", "PHYSICAL", "VOLUME", ("ml", "mls", "millilitre", "millilitres", "milliliter", "milliliters", "cc"),
         1.0, "SI_BROCHURE"),
    Unit("cl", "PHYSICAL", "VOLUME", ("cl", "centilitre", "centilitres"), 10.0, "SI_BROCHURE"),
    Unit("dl", "PHYSICAL", "VOLUME", ("dl", "decilitre", "decilitres"), 100.0, "SI_BROCHURE"),
    Unit("l", "PHYSICAL", "VOLUME", ("l", "litre", "litres", "liter", "liters", "ltr", "ltrs"), 1000.0, "SI_BROCHURE"),
    # ---- locale-dependent volume ----
    Unit("fl_oz", "CULINARY_VOLUME", "VOLUME", ("fl oz", "floz", "fl. oz", "fl.oz", "fluid ounce", "fluid ounces"),
         conventions={"US": (US_FLOZ, "NIST_HB44_APPC"), "UK": (UK_FLOZ, "UK_WMA_1985_SCH1"),
                      "US_LABEL": (30.0, "CFR21_101_9")}),
    Unit("pint", "CULINARY_VOLUME", "VOLUME", ("pint", "pints", "pt"),
         conventions={"US": (473.176473, "NIST_HB44_APPC"), "UK": (568.26125, "UK_WMA_1985_SCH1")}),
    Unit("quart", "CULINARY_VOLUME", "VOLUME", ("quart", "quarts", "qt"),
         conventions={"US": (946.352946, "NIST_HB44_APPC"), "UK": (1136.5225, "UK_WMA_1985_SCH1")}),
    Unit("gallon", "CULINARY_VOLUME", "VOLUME", ("gallon", "gallons", "gal"),
         conventions={"US": (3785.411784, "NIST_HB44_APPC"), "UK": (4546.09, "UK_WMA_1985_SCH1")}),
    Unit("tsp", "CULINARY_VOLUME", "VOLUME", ("tsp", "tsps", "teaspoon", "teaspoons", "tspn", "t"),
         conventions={"US": (US_TSP, "NIST_HB44_APPC"), "US_LABEL": (5.0, "CFR21_101_9"),
                      "UK": (5.0, "CONV_METRIC_SPOON"), "METRIC": (5.0, "CONV_METRIC_SPOON"),
                      "AU": (5.0, "CONV_METRIC_SPOON"), "IN": (5.0, "CONV_METRIC_SPOON")}),
    Unit("tbsp", "CULINARY_VOLUME", "VOLUME", ("tbsp", "tbsps", "tablespoon", "tablespoons", "tbs", "tbl", "tbls",
                                                "tblsp", "T"),
         conventions={"US": (US_TBSP, "NIST_HB44_APPC"), "US_LABEL": (15.0, "CFR21_101_9"),
                      "UK": (15.0, "CONV_METRIC_SPOON"), "METRIC": (15.0, "CONV_METRIC_SPOON"),
                      "AU": (20.0, "CONV_AU_TBSP"), "IN": (15.0, "CONV_METRIC_SPOON")}),
    Unit("dsp", "CULINARY_VOLUME", "VOLUME", ("dsp", "dessertspoon", "dessertspoons", "dstspn"),
         conventions={"UK": (10.0, "CONV_UK_DSP")}),
    Unit("cup", "CULINARY_VOLUME", "VOLUME", ("cup", "cups", "c"),
         conventions={"US": (US_CUP, "NIST_HB44_APPC"), "US_LABEL": (240.0, "CFR21_101_9"),
                      "METRIC": (250.0, "CONV_METRIC_CUP"), "AU": (250.0, "CONV_METRIC_CUP")},
         note="UK recipes mix US and metric cups -> AMBIGUOUS range when locale is UK"),
    # ---- regional / non-standard vessels: no number without evidence ----
    Unit("katori", "REGIONAL", "VOLUME", ("katori", "katoris", "katori-ful", "vati", "bowl", "bowls"),
         note="no standard volume; only an evidenced empirical distribution (Q4) may be attached"),
    Unit("glass", "REGIONAL", "VOLUME", ("glass", "glasses"), note="no standard volume"),
    Unit("mug", "REGIONAL", "VOLUME", ("mug", "mugs", "mugful"), note="no standard volume"),
    # ---- count / portion (ingredient-specific mass, never universal) ----
    *[Unit(k, "COUNT_PORTION", "COUNT", a) for k, a in (
        ("clove", ("clove", "cloves")), ("slice", ("slice", "slices")), ("fillet", ("fillet", "fillets")),
        ("head", ("head", "heads")), ("bunch", ("bunch", "bunches")), ("sprig", ("sprig", "sprigs")),
        ("stick", ("stick", "sticks")), ("rasher", ("rasher", "rashers")), ("sheet", ("sheet", "sheets")),
        ("piece", ("piece", "pieces", "pc", "pcs")), ("leaf", ("leaf", "leaves")), ("stalk", ("stalk", "stalks")),
        ("wedge", ("wedge", "wedges")), ("strip", ("strip", "strips")), ("cube", ("cube", "cubes")),
        ("ball", ("ball", "balls")), ("pod", ("pod", "pods")), ("ear", ("ear", "ears")),
        ("loaf", ("loaf", "loaves")), ("joint", ("joint", "joints")),
        ("bulb", ("bulb", "bulbs")))],
    # ---- packages (mass/volume only if the line states the package size) ----
    *[Unit(k, "PACKAGE", "COUNT", a) for k, a in (
        ("can", ("can", "cans", "tin", "tins")), ("jar", ("jar", "jars")), ("pack", ("pack", "packs", "packet",
                                                                                     "packets", "pkt")),
        ("bag", ("bag", "bags")), ("carton", ("carton", "cartons")), ("bottle", ("bottle", "bottles")),
        ("tub", ("tub", "tubs")), ("box", ("box", "boxes")), ("sachet", ("sachet", "sachets")),
        ("punnet", ("punnet", "punnets")), ("bar", ("bar", "bars")), ("block", ("block", "blocks")),
        ("pot", ("pot", "pots")), ("tray", ("tray", "trays")), ("pouch", ("pouch", "pouches")))],
    # ---- verbal / qualitative (SSOT §235.5: no grams by common sense) ----
    *[Unit(k, "VERBAL_QUALITATIVE", "NONE", a) for k, a in (
        ("pinch", ("pinch", "pinches")), ("dash", ("dash", "dashes")), ("splash", ("splash", "splashes")),
        ("handful", ("handful", "handfuls")), ("drizzle", ("drizzle",)), ("knob", ("knob", "knobs")),
        ("sprinkle", ("sprinkle", "sprinkling")), ("glug", ("glug", "glugs")), ("smidgen", ("smidgen",)),
        ("drop", ("drop", "drops")), ("squeeze", ("squeeze",)), ("dollop", ("dollop", "dollops")),
        ("grating", ("grating", "gratings")), ("shaving", ("shaving", "shavings")),
        ("scattering", ("scattering",)))],
    # ---- length (size of a piece, not an amount) ----
    Unit("cm", "LENGTH", "LENGTH", ("cm", "centimetre", "centimetres"), 1.0, "SI_BROCHURE"),
    Unit("mm", "LENGTH", "LENGTH", ("mm",), 0.1, "SI_BROCHURE"),
    Unit("inch", "LENGTH", "LENGTH", ("in", "inch", "inches"), 2.54, "NIST_HB44_APPC"),
)

BY_KEY = {u.key: u for u in UNITS}
ALIAS: dict[str, Unit] = {}
for _u in UNITS:
    for _a in _u.aliases:
        ALIAS.setdefault(_a.lower() if _a not in ("T", "t", "c") else _a, _u)

PHRASE_QUALITATIVE = ("to taste", "as needed", "as required", "enough to cover", "for frying", "for greasing",
                      "for dusting", "to serve", "to garnish", "for drizzling", "for brushing", "optional")


def lookup(token: str) -> Unit | None:
    if token in ("T", "t", "c"):          # case-sensitive legacy spoon/cup abbreviations
        return ALIAS.get(token)
    return ALIAS.get(token.lower().rstrip("."))
