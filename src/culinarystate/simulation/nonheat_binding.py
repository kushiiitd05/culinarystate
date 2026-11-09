"""Layer 1 TEXT_STATED binding for the NON-heat process families (S176 L-NH, D-077 extension). DRAFT.

Heat families (WET/DRY/FAT/HEAT_GENERAL) are bound by ``condition_binding``; this module gives every other physical
event family the same layer, so that the formula router can later see it. It reuses the heat ``Binder`` (Rung A graph,
sentence split, setpoint tracking, ``_inputs`` for the prior heat step) and never modifies it.

Families (event family in the PROC ledger, plus STORAGE = the verb "store"): COOLING, SEPARATION, FERMENT_LEAVEN,
PRESERVATION, MECHANICAL_CUT, MECHANICAL_MIX, RESTING, STORAGE. Each record names its FORM candidate class (coverage
plan 2026-11-08); the 23a engine maps classes to FORM ids later and is not touched here.

Rules (all deterministic):
- An input is bound only from text in the event's own clause window (verb to the next physical verb in the same
  sentence) or from the recipe graph; every bound input carries its character span in the joined step text. No span
  means UNKNOWN (value None, status UNKNOWN, a reason code). Nothing is defaulted and no number is invented here.
- Basis vocabulary: TEXT_STATED (duration or temperature written in the clause), TEXT_CUE (a medium, environment,
  cut or state word written in the clause), PROCESS_DEFINITION (the verb itself fixes the class; span = the verb),
  PHYSICAL_DEFINITION (boiling water is 100 C at 1 atm; span = the phrase), LINEAGE / ORDER_ADJACENT (history link to
  a heat step or a cut step; span = that step's verb), LINEAGE_AND_STATED_DURATIONS (time until the next heat).
- Qualitative classes (FRIDGE, FREEZER, ROOM, OVERNIGHT ...) stay classes: fridge and freezer words are never turned
  into temperatures here (Layer 2 does that from the NH registry).
- Statuses: MEASURED, RANGE, BOUND_UPPER, BOUND_LOWER (up to / at least), QUALITATIVE (class, no number), UNKNOWN.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a_measure import code, seeded_sample
from culinarystate.mechanism.router_demo import _attr
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.recipes.ledgers import LOCALE
from culinarystate.simulation import condition_binding as CB

ROOT = Path(__file__).resolve().parents[3]
VERSION = "nonheat-binding-L1-0.2.0-draft"
VERSION_V01 = "nonheat-binding-L1-0.1.0-draft"  # SUPERSEDED: heat-step links used the 0.1.0 nearest-temperature rule; no span_id / row
CENSUS_VERSION = "nonheat-census-L1-0.1.0-draft"
NH_FAMILIES = ("COOLING", "SEPARATION", "FERMENT_LEAVEN", "PRESERVATION", "MECHANICAL_CUT", "MECHANICAL_MIX",
               "RESTING", "STORAGE")
STORE_PROC = "PROC-000113"
HEAT = CB.HEAT
# FORM candidate classes (coverage plan table); labels only, mapped to FORM ids by the router later.
FORM_CANDIDATE = {
    "COOLING": "TRANSIENT_CONDUCTION_COLD_BATH|PLANK_FREEZING_THAW_REVERSE",
    "SEPARATION": "LEACHING_COMPARTMENT_HANDOFF",
    "FERMENT_LEAVEN": "FICKIAN_SLAB_UPTAKE|PH_STATE_FLAG",
    "PRESERVATION": "DRYING_CONSTANT_PLUS_FALLING_RATE|F_VALUE_Z10_TREF121_1|FICKIAN_SLAB_UPTAKE",
    "MECHANICAL_CUT": "GEOMETRY_SIZE_CLASS_AND_ENZYME_ACTIVATION_FLAG",
    "MECHANICAL_MIX": "QUALITATIVE_STATE_FLAGS",
    "RESTING": "CARRYOVER_CONDUCTION_STILL_AIR",
    "STORAGE": "ARRHENIUS_AT_STORAGE_T_PARAM_PENDING",
}
INPUTS = {
    "COOLING": ("duration", "medium_temperature", "target_food_temperature", "environment", "target_state",
                "start_state", "piece_size_class"),
    "SEPARATION": ("duration", "removed_phase", "liquid_fate", "rinse_medium", "rinse_temperature_class",
                   "follows_soak_or_brine"),
    "FERMENT_LEAVEN": ("duration", "medium_temperature", "environment", "medium", "salt_concentration_pct",
                       "acid_concentration_pct", "piece_size_class"),
    "PRESERVATION": ("duration", "medium_temperature", "environment", "medium", "salt_concentration_pct",
                     "acid_concentration_pct", "piece_size_class"),
    "MECHANICAL_CUT": ("cut_class", "disruption_level", "enzyme_system", "time_until_next_heat"),
    "MECHANICAL_MIX": ("duration", "tool", "aerated", "emulsified", "developed"),
    "RESTING": ("duration", "environment", "cover_state", "prior_heat_link", "piece_size_class"),
    "STORAGE": ("duration", "medium_temperature", "environment", "container"),
}
TEXT_BASES = ("TEXT_STATED", "TEXT_CUE")
TIMED_FAMILIES = ("COOLING", "FERMENT_LEAVEN", "PRESERVATION", "RESTING", "STORAGE")
# surfaces that the lexicon maps to a verb but that are nouns or adjectives in recipe text (counted, never simulated)
NON_VERB_SURFACES = ("marinade", "marinades", "canned", "cans", "can", "pickles", "grates")
GEOMETRY_CLASSES = ("MINCED", "GRATED", "SHREDDED", "SLICED", "DICED", "CHOPPED", "JULIENNE")
DISRUPTION = {"MINCED": "HIGH", "CRUSHED": "HIGH", "GRATED": "HIGH", "SHREDDED": "HIGH", "GROUND": "HIGH",
              "CHOPPED": "MODERATE", "DICED": "MODERATE", "JULIENNE": "MODERATE", "SLICED": "MODERATE",
              "CRUMBLED": "MODERATE", "FLAKED": "MODERATE", "HALVED": "LOW", "TRIMMED": "LOW", "PEELED": "LOW",
              "TORN": "LOW", "SNIPPED": "LOW", "CARVED": "LOW", "SCORED": "LOW", "PIERCED": "LOW",
              "BUTTERFLIED": "LOW", "CRACKED": "LOW"}
CUT_CLASS_NH = {**CB.CUT_CLASS, "PROC-000062": "JULIENNE", "PROC-000061": "GROUND", "PROC-000046": "CUT_UNSPECIFIED",
                "PROC-000052": "TRIMMED", "PROC-000053": "PEELED", "PROC-000054": "TORN", "PROC-000055": "SNIPPED",
                "PROC-000056": "CARVED", "PROC-000057": "SCORED", "PROC-000058": "CRUMBLED", "PROC-000059": "FLAKED",
                "PROC-000060": "PIERCED", "PROC-000063": "BUTTERFLIED", "PROC-000148": "CRACKED"}
# sizes that a cut verb leaves on a lot are the same set the heat layer uses, plus JULIENNE (CUT_HISTORY basis)
SIZE_FROM_CUT = {**CB.CUT_CLASS, "PROC-000062": "JULIENNE"}

_UNIT_MIN = {"second": Fraction(1, 60), "seconds": Fraction(1, 60), "sec": Fraction(1, 60), "secs": Fraction(1, 60),
             "minute": 1, "minutes": 1, "min": 1, "mins": 1, "hour": 60, "hours": 60, "hr": 60, "hrs": 60, "h": 60,
             "day": 1440, "days": 1440, "week": 10080, "weeks": 10080}
_SENT2 = re.compile(r"[!?;\n]+|\.(?!\d)")
_UPPER = re.compile(r"(?:\bup to|\bupto|\bat most|\bmaximum of|\bmax\.?|\bno more than|\bnot more than|\bno longer than|"
                    r"\bwithin|\bfor a maximum of)\s*(?:about|around|approximately|roughly)?\s*$", re.I)
_LOWER = re.compile(r"(?:\bat least|\bminimum of|\ba minimum of|\bno less than|\bnot less than|\bmore than)"
                    r"\s*(?:about|around|approximately|roughly)?\s*$", re.I)
_APPROX = re.compile(r"(?:\babout|\baround|\bapproximately|\broughly|\bapprox\.?|\bca\.?|~)\s*$", re.I)
_LEFT_RANGE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*(?:-|–|—|&ndash;|&mdash;|&#8211;|to|or)\s*$", re.I)
_LONG = re.compile(r"(?P<a>\d+(?:\.\d+)?)(?:\s*(?:-|–|to)\s*(?P<b>\d+(?:\.\d+)?))?\s*(?P<u>months?|years?)\b", re.I)
_OVERNIGHT = re.compile(r"\bovernight\b|\bfor the night\b|\bthrough the night\b", re.I)
_GAP_SUM = re.compile(r"^\s*(?:,|and|&)?\s*$", re.I)
_GAP_RANGE = re.compile(r"^\s*(?:to|-|–|or)\s*$", re.I)
_TEMP = re.compile(
    r"(?<![\w.])(?P<a>[-−]?\d{1,3}(?:\.\d+)?)(?:\s*(?:-|–|to)\s*(?P<b>[-−]?\d{1,3}(?:\.\d+)?))?"
    r"(?:\s*(?:°|º|˚)\s*|\s+degrees?\s+|\s+deg\.?\s*|\s+(?=Celsius\b|Fahrenheit\b)|(?=[CF]\b))"
    r"(?P<u>C(?:elsius)?|F(?:ahrenheit)?)\b")
_TARGET_PREFIX = re.compile(r"(?:\bto|\buntil|\breach(?:es|ing)?|\bbelow|\bunder|\bdown to|\bless than|\blower than)"
                            r"\s*(?:about|around|approximately)?\s*(?:a |an |the )?(?:temperature of )?\s*$", re.I)
T_MIN_C, T_MAX_C = Fraction(-60), Fraction(260)

ENV_CUES = (
    ("FREEZER", r"\bfreezers?\b|\bdeep[- ]freeze\b|\bicebox\b"),
    ("FRIDGE", r"\bfridge\b|\brefrigerators?\b|\brefrigerated\b|\brefrigeration\b|\bchiller\b|\bcold room\b"),
    ("ICE_BATH", r"\bice[- ]?(?:bath|water)\b|\biced[- ]water\b|\bbowl of ice\b|\bover ice\b|\bice[- ]cold water\b|"
                 r"\bon ice\b"),
    ("COLD_WATER", r"\bcold (?:running |tap )?water\b|\brunning (?:cold )?water\b|\bunder (?:the )?(?:cold )?"
                   r"(?:tap|faucet)\b|\bcool(?:ing)? water\b"),
    ("ROOM", r"\broom[- ]temp(?:erature)?\b|\bambient\b|\bcounter(?:top)?\b|\bworktop\b|\bon the bench\b|"
             r"\bwire rack\b|\bcooling rack\b|\ba rack\b|\bthe rack\b|\bopen air\b"),
    ("COOL_DARK", r"\bcool,? (?:and )?(?:dry|dark)(?:,? (?:and )?(?:dry|dark))? (?:place|cupboard|pantry|spot|area)\b|"
                  r"\bcool place\b|\bpantry\b|\bcellar\b|\bdark place\b"),
    ("WARM_PLACE", r"\bwarm (?:place|spot|area|room|corner|location|kitchen|cupboard|environment)\b|"
                   r"\bairing cupboard\b|\bproof(?:ing)? (?:drawer|box|cabinet)\b"),
    ("DEHYDRATOR", r"\bdehydrators?\b"),
    ("OVEN", r"\boven\b"),
    ("MICROWAVE", r"\bmicrowave\b"),
    ("BOILING_WATER_BATH", r"\bboiling[- ]water(?:[- ]bath)?\b|\bwater[- ]bath canner\b"),
    ("PRESSURE_CANNER", r"\bpressure[- ]?(?:canner|cooker)\b|\bautoclave\b|\bretort\b"),
)
ENV_ALLOWED = {
    "COOLING": ("FREEZER", "FRIDGE", "ICE_BATH", "COLD_WATER", "ROOM", "MICROWAVE"),
    "RESTING": ("ROOM", "FRIDGE", "WARM_PLACE"),
    "STORAGE": ("FRIDGE", "FREEZER", "ROOM", "COOL_DARK"),
    "FERMENT_LEAVEN": ("FRIDGE", "ROOM", "WARM_PLACE", "COLD_WATER"),
    "PRESERVATION_DRY": ("DEHYDRATOR", "OVEN", "MICROWAVE"),
    # L1 keeps every environment cue the text gives. S177: Layer 2 computes F0 only for PROC-000132 + PRESSURE_CANNER; the other
    # cues (boiling-water bath, oven) get QUALITATIVE flags, and OVEN adds OVEN_CANNING_NOT_A_VALID_PROCESS (L1 is unchanged).
    "PRESERVATION_HEAT": ("BOILING_WATER_BATH", "PRESSURE_CANNER", "OVEN"),
    "PRESERVATION_SOAK": ("FRIDGE", "ROOM", "COOL_DARK", "WARM_PLACE"),
}
MEDIUM_CUES = (
    ("BRINE", r"\bbrine\b|\bbrining\b|\bsalt(?:ed)?[- ]water\b|\bsalt solution\b|\bsaline\b"),
    ("VINEGAR", r"\bvinegar\b|\bpickling (?:liquid|brine|solution)\b|\bacetic\b"),
    ("CITRUS_JUICE", r"\b(?:lemon|lime|citrus|orange|grapefruit)\s+juice\b|\bjuice of (?:a |an |one |two |\d+ )?"
                     r"(?:lemons?|limes?|oranges?)\b"),
    ("MARINADE_OTHER", r"\bmarinade\b|\bmarinating liquid\b|\bsoy sauce\b|\bbuttermilk\b|\byogh?urt\b|\bcurd\b|"
                       r"\bkefir\b|\bwine\b|\bbeer\b|\bsake\b|\bmirin\b|\bmilk\b|\bsyrup\b|\bolive oil\b"),
    ("WATER", r"\bwater\b"),
)
VERB_MEDIUM = {"PROC-000155": "BRINE", "PROC-000100": "MARINADE_OTHER"}  # brine, marinate
_SALT = re.compile(r"(?P<v>\d{1,2}(?:\.\d+)?)\s*(?:%|per ?cent|percent)\s*(?:salt|brine|salt(?:ed)?[- ]water|salinity|"
                   r"saline|solution)|(?:brine|salt solution|salt water|salted water)[^.;%]{0,25}?"
                   r"(?P<w>\d{1,2}(?:\.\d+)?)\s*(?:%|per ?cent|percent)", re.I)
_ACID = re.compile(r"(?P<v>\d{1,2}(?:\.\d+)?)\s*(?:%|per ?cent|percent)\s*(?:acetic|acidity|vinegar|acid)|"
                   r"(?:vinegar|acetic acid)[^.;%]{0,25}?(?P<w>\d{1,2}(?:\.\d+)?)\s*(?:%|per ?cent|percent)", re.I)
_DISCARD = re.compile(r"\b(?:discard|throw away|pour away|pour off|tip away|toss out)\w*\b", re.I)
_LIQ = re.compile(r"\b(?:liquid|liquids|water|marinade|brine|juices?|liquor|syrup|fat|oil|stock|"
                  r"(?:cooking|soaking|pasta|bean) (?:liquid|water))\b", re.I)
_SOLID = re.compile(r"\b(?:solids?|skins?|peel|seeds?|bones?|bay leaves|bay leaf|herbs?|stalks?|stems?|pips?|shells?|"
                    r"husks?|pulp|ends|leaves|cores?|stones?|pits?|bits)\b", re.I)
_RETAIN = re.compile(r"\b(?:reserv(?:e|ing|ed)|sav(?:e|ing)|keep(?:ing)?|set aside|retain(?:ing)?)\b[^.;]{0,40}?"
                     r"\b(?:liquid|water|stock|juices?|liquor|marinade|brine|"
                     r"(?:cooking|soaking|pasta|bean) (?:liquid|water))\b", re.I)
REMOVED_PHASE = {"PROC-000078": "LIQUID", "PROC-000079": "SOLID_LIQUID_SPLIT", "PROC-000080": "PARTICLE_FRACTION",
                 "PROC-000081": "SURFACE_LAYER", "PROC-000082": "COMPONENT_SPLIT", "PROC-000083": "OBJECT",
                 "PROC-000084": "SURFACE_FILM", "PROC-000085": "LIQUID", "PROC-000086": "SOLID_PIECES",
                 "PROC-000087": "SURFACE_WATER", "PROC-000156": "LIQUID"}
_RINSE_T = re.compile(r"\b(cold|cool|lukewarm|warm|hot|boiling)\b[^.;]{0,15}\bwater\b|\b(cold|cool) running\b", re.I)
_RINSE_CLASS = {"cold": "COLD", "cool": "COLD", "lukewarm": "WARM", "warm": "WARM", "hot": "HOT", "boiling": "HOT"}
SOAKLIKE = {"PROC-000129": "SOAK", "PROC-000155": "BRINE", "PROC-000100": "MARINATE", "PROC-000156": "DEGORGE"}
TOOL_CUES = (
    ("ELECTRIC_MIXER", r"\b(?:stand|hand|electric) mixer\b|\bmixer\b|\bdough hook\b|\bbeaters?\b"),
    ("BLENDER", r"\bblender\b|\bnutribullet\b"),
    ("FOOD_PROCESSOR", r"\bfood processor\b|\bprocessor\b|\bmagimix\b|\bthermomix\b"),
    ("WHISK", r"\b(?:with|using|use|by) (?:a |an |the |your )?(?:balloon |wire |hand )?whisk\b|"
              r"\b(?:balloon|wire) whisk\b"),
    ("HAND_TOOL", r"\bby hand\b|\bwith your (?:hands|fingers)\b|\bwooden spoon\b|\bspatula\b|\bfork\b|\bspoon\b"),
)
AERATED_TEXT = r"\b(?:stiff|soft|firm|medium|glossy) peaks?\b|\bfrothy\b|\bfoamy\b|\bfluffy\b|\blight and "\
               r"(?:fluffy|creamy|airy)\b|\bairy\b|\bribbon stage\b|\bpale and (?:thick|creamy|fluffy)\b|"\
               r"\bdoubled in (?:volume|size)\b"
EMULSIFIED_TEXT = r"\bemulsif\w*\b|\bemulsion\b|\bmayonnaise\b|\baioli\b|\bvinaigrette\b|\bhollandaise\b|\bb[eé]arnaise\b"
DEVELOPED_TEXT = r"\belastic\b|\bwindow[- ]?pane\b|\bstretchy\b|\bsmooth and (?:springy|supple|satiny|elastic)\b|"\
                 r"\bgluten\b|\bsprings back\b"
MIX_VERB_FLAG = {"PROC-000066": "aerated", "PROC-000073": "aerated", "PROC-000067": "aerated",
                 "PROC-000077": "emulsified", "PROC-000072": "developed"}
ENZYME_CUES = (
    ("ALLIINASE_FAMILY", r"\b(?:garlic|onions?|shallots?|leeks?|chives?|scallions?|spring onions?)\b"),
    ("MYROSINASE_FAMILY", r"\b(?:cabbage|broccoli|cauliflower|kale|mustard|radish(?:es)?|horseradish|wasabi|turnips?|"
                          r"brussels sprouts?|bok choy|rocket|arugula|watercress|collards?)\b"),
    ("PPO_FAMILY", r"\b(?:apples?|pears?|potato(?:es)?|avocados?|bananas?|mushrooms?|aubergines?|eggplants?|"
                   r"peach(?:es)?|artichokes?)\b"),
)
CONTAINER_CUES = (
    ("AIRTIGHT_OR_SEALED", r"\bair[- ]?tight\b|\bsealed\b|\bvacuum\b|\bsealable\b|\bzip[- ]?top\b|\bresealable\b|"
                           r"\bscrew[- ]?(?:top|cap)\b|\bkilner\b"),
    ("CONTAINER", r"\bjars?\b|\btins?\b|\bcontainers?\b|\bboxe?s?\b|\btubs?\b|\bbags?\b|\btupperware\b"),
    ("COVERED", r"\bcover(?:ed)?\b|\bfoil\b|\bwrap(?:ped)?\b|\bcling ?film\b|\bplastic wrap\b"),
)
COVER_CUES = (
    ("UNCOVERED", r"\buncover(?:ed)?\b|\bwithout (?:a |the )?(?:lid|cover|foil)\b"),
    ("FOIL_TENTED", r"\btent(?:ed)?\b|\bfoil\b"),
    ("COVERED", r"\bcover(?:ed)?\b|\bwrap(?:ped)?\b|\blid\b|\bclean (?:tea )?towel\b|\bcloth\b"),
)
EQUIPMENT = re.compile(r"\b(?:jars?|bottles?|lids?|containers?|utensils?|funnels?|equipment|tins?)\b", re.I)
_C = {k: [(c, re.compile(rx, re.I)) for c, rx in v] for k, v in (
    ("ENV", ENV_CUES), ("MEDIUM", MEDIUM_CUES), ("TOOL", TOOL_CUES), ("ENZ", ENZYME_CUES),
    ("CONT", CONTAINER_CUES), ("COVER", COVER_CUES))}
_AER, _EMU, _DEV = (re.compile(x, re.I) for x in (AERATED_TEXT, EMULSIFIED_TEXT, DEVELOPED_TEXT))


# ---------------------------------------------------------------------------------------------------- input helpers
def unknown(reason: str) -> dict:
    return {"value": None, "status": "UNKNOWN", "basis": None, "span": None, "reason": reason}


def known(value, status: str, basis: str, span: tuple[int, int], **extra) -> dict:
    return {"value": value, "status": status, "basis": basis, "span": [int(span[0]), int(span[1])], **extra}


def _s(v):
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, (tuple, list)):
        return [_s(x) for x in v]
    return v


def _latest(path: Path) -> dict:
    return CB._latest(path)


def _c_of(v: Fraction, unit: str) -> Fraction:
    return (v - 32) * Fraction(5, 9) if unit[0].upper() == "F" else v


class NonHeatBinder:
    def __init__(self, base: CB.Binder, names: Mapping[str, str]) -> None:
        self.base, self.names = base, names

    @classmethod
    def load(cls, root: Path = ROOT, base: CB.Binder | None = None) -> "NonHeatBinder":
        base = base or CB.Binder.load(root)
        procs = _latest(root / "ledgers/data/PROC.jsonl")
        return cls(base, {p: str(r.get("canonical_name") or "") for p, r in procs.items()})

    # ------------------------------------------------------------------------------------------ classification
    def nh_family(self, pid: str | None) -> str | None:
        if pid == STORE_PROC:
            return "STORAGE"
        fam = self.base.family.get(pid)
        return fam if fam in NH_FAMILIES else None

    # ------------------------------------------------------------------------------------------ text helpers
    @staticmethod
    def _cue(table, raw: str, win: tuple[int, int], anchor: int, allowed=None):
        """Nearest cue (class, span) to ``anchor`` in the window; ties go to the earlier table entry."""
        best = None
        for rank, (cls, rx) in enumerate(table):
            if allowed is not None and cls not in allowed:
                continue
            for m in rx.finditer(raw, win[0], win[1]):
                key = (abs(m.start() - anchor), rank)
                if best is None or key < best[0]:
                    best = (key, cls, (m.start(), m.end()), m)
        return None if best is None else (best[1], best[2])

    @staticmethod
    def _temperatures(raw: str, win: tuple[int, int], anchor: int) -> list[dict]:
        out = []
        for m in _TEMP.finditer(raw, win[0], win[1]):
            a = Fraction(m.group("a").replace("−", "-"))
            b = Fraction(m.group("b").replace("−", "-")) if m.group("b") else a
            lo, hi = sorted((_c_of(a, m.group("u")), _c_of(b, m.group("u"))))
            if not (T_MIN_C <= lo <= hi <= T_MAX_C):
                continue
            before = raw[max(0, m.start() - 40):m.start()]
            out.append({"value": (lo, hi), "span": (m.start(), m.end()),
                        "role": "TARGET_FOOD" if _TARGET_PREFIX.search(before) else "MEDIUM",
                        "dist": abs(m.start() - anchor)})
        return sorted(out, key=lambda d: d["dist"])

    def _temperature_inputs(self, raw, win, anchor, with_target: bool) -> dict:
        ts = self._temperatures(raw, win, anchor)
        res = {"medium_temperature": unknown("NO_TEMPERATURE_STATED")}
        if with_target:
            res["target_food_temperature"] = unknown("NO_TARGET_TEMPERATURE_STATED")
        for t in ts:
            name = "target_food_temperature" if t["role"] == "TARGET_FOOD" and with_target else "medium_temperature"
            if t["role"] == "TARGET_FOOD" and not with_target:
                continue
            if res[name]["status"] != "UNKNOWN":
                continue
            lo, hi = t["value"]
            res[name] = known(lo if lo == hi else (lo, hi), "MEASURED" if lo == hi else "RANGE", "TEXT_STATED", t["span"])
        return res

    @staticmethod
    def _sentence(raw: str, pos: int) -> tuple[int, int]:
        """Sentence bounds that do not split on a decimal point (the heat layer's splitter does)."""
        starts = [0] + [m.end() for m in _SENT2.finditer(raw, 0, pos)]
        nxt = _SENT2.search(raw, pos)
        return max(starts), (nxt.start() if nxt else len(raw))

    def _durations(self, ev, raw: str, win: tuple[int, int], timed: bool = True) -> dict:
        items: dict[int, dict] = {}
        for c in ev.attributes:
            m = re.fullmatch(r"duration(_min)?(?:_(\d+))?", c.field)
            if not m or c.span is None:
                continue
            idx = int(m.group(2) or 0)
            slot = items.setdefault(idx, {"span": (min(s[0] for s in c.span.segments),
                                                   max(s[1] for s in c.span.segments))})
            if m.group(1):
                slot["min"] = c.value
            else:
                slot["raw"], slot["unit"] = c.value, c.unit
                slot["f"] = _UNIT_MIN.get(c.unit)
        parsed = []
        for idx in sorted(items):
            it = items[idx]
            v = it.get("min")
            if v is None and "raw" in it and it.get("unit") in _UNIT_MIN:
                f = _UNIT_MIN[it["unit"]]
                r = it["raw"]
                v = tuple(Fraction(x) * f for x in r) if isinstance(r, tuple) else Fraction(r) * f
            if v is None:
                continue
            v = tuple(Fraction(x) for x in v) if isinstance(v, tuple) else Fraction(v)
            if (v[1] if isinstance(v, tuple) else v) > 0:
                parsed.append((it["span"], v, it.get("f")))
        parsed.sort(key=lambda p: p[0][0])
        if parsed:
            span, val, unit_f = parsed[0]
            extra: dict = {}
            if not isinstance(val, tuple) and unit_f is not None:
                # "6&ndash;12 hours", "4 or 5 hours": the unit follows the upper number only (Rung A keeps that one)
                a0 = max(0, span[0] - 24)
                left = _LEFT_RANGE.search(raw[a0:span[0]])
                if left and Fraction(left.group(1)) * Fraction(unit_f) < val:
                    val, span = (Fraction(left.group(1)) * Fraction(unit_f), val), (a0 + left.start(1), span[1])
                    extra = {"compound": "RANGE_LOW_FROM_TEXT"}
            for sp2, v2, _ in parsed[1:]:
                gap = raw[span[1]:sp2[0]]
                if not isinstance(val, tuple) and not isinstance(v2, tuple) and _GAP_SUM.match(gap):
                    val, span, extra = val + v2, (span[0], sp2[1]), {"compound": "SUM"}
                elif not isinstance(val, tuple) and not isinstance(v2, tuple) and _GAP_RANGE.match(gap):
                    val, span, extra = tuple(sorted((val, v2))), (span[0], sp2[1]), {"compound": "RANGE"}
                else:
                    extra = {"compound": "FIRST_OF_SEVERAL"}
                    break
            return self._finish_duration(raw, val, span, extra)
        # Rung A has no duration claim: months and years (not in its unit set), else the word "overnight"
        m = _LONG.search(raw, win[0], win[1])
        if m:
            f = Fraction(43200 if m.group("u").lower().startswith("month") else 525600)
            a = Fraction(m.group("a")) * f
            val = (a, Fraction(m.group("b")) * f) if m.group("b") else a
            return self._finish_duration(raw, val, (m.start(), m.end()),
                                         {"unit_convention": "MONTH_30D" if f == 43200 else "YEAR_365D"})
        m = _OVERNIGHT.search(raw, win[0], win[1]) if timed else None
        if m:
            return known("OVERNIGHT", "QUALITATIVE", "TEXT_CUE", (m.start(), m.end()))
        return unknown("NO_DURATION_STATED")

    @staticmethod
    def _finish_duration(raw: str, val, span: tuple[int, int], extra: dict) -> dict:
        before = raw[max(0, span[0] - 22):span[0]]
        if isinstance(val, tuple):
            return known(val, "RANGE" if val[0] != val[1] else "MEASURED", "TEXT_STATED", span, **extra)
        if _UPPER.search(before):
            return known(val, "BOUND_UPPER", "TEXT_STATED", span, **extra)
        if _LOWER.search(before):
            return known(val, "BOUND_LOWER", "TEXT_STATED", span, **extra)
        if _APPROX.search(before):
            extra = {**extra, "qualifier": "APPROX"}
        return known(val, "MEASURED", "TEXT_STATED", span, **extra)

    # ------------------------------------------------------------------------------------------ history
    def _size_class(self, g, ents, producers, lot_ids) -> dict:
        stack, seen = list(lot_ids), set()
        while stack:
            lid = stack.pop()
            if lid in seen:
                continue
            seen.add(lid)
            ev = producers.get(lid)
            if ev is not None and ev.span is not None:
                pid = _attr(ev.attributes, "proc_id")
                if pid in SIZE_FROM_CUT:
                    return known(SIZE_FROM_CUT[pid], "QUALITATIVE", "CUT_HISTORY",
                                 (ev.span.char_start, ev.span.char_end))
            if lid in ents:
                stack.extend(ents[lid].parent_entity_ids)
        return unknown("NO_CUT_HISTORY_FOR_LOT")

    def _prior_heat(self, ev, ctx) -> dict | None:
        """Nearest upstream heat step of the consumed lots (LINEAGE), else the immediately preceding physical step
        if it is a heat step in the same or previous recipe step (ORDER_ADJACENT)."""
        stack, seen = list(ev.consumes), set()
        found = None
        while stack:
            lid = stack.pop()
            if lid in seen:
                continue
            seen.add(lid)
            pev = ctx["producers"].get(lid)
            if pev is not None and pev.event_id in ctx["heat_inputs"]:
                if found is None or pev.span.char_start > found.span.char_start:
                    found = pev
                continue
            if lid in ctx["ents"]:
                stack.extend(ctx["ents"][lid].parent_entity_ids)
        basis = "LINEAGE"
        if found is None:
            rel = ctx["rel_order"]
            pos = rel.index(ev.event_id) if ev.event_id in rel else -1
            if pos > 0:
                prev = ctx["by_id"][rel[pos - 1]]
                if prev.event_id in ctx["heat_inputs"] and abs(prev.order[0] - ev.order[0]) <= 1:
                    found, basis = prev, "ORDER_ADJACENT"
        if found is None:
            return None
        inp, gas_code = ctx["heat_inputs"][found.event_id]
        return {"event_id": found.event_id, "process_id": _attr(found.attributes, "proc_id"), "basis": basis,
                "span": [found.span.char_start, found.span.char_end], "oven_setpoint_code": gas_code,
                "inputs": {k: {kk: (_s(vv) if kk == "value" else vv) for kk, vv in v.items()} for k, v in inp.items()}}

    def _next_heat(self, ev, ctx) -> dict | None:
        desc, stack = set(), list(ev.produces)
        while stack:
            lid = stack.pop()
            if lid in desc:
                continue
            desc.add(lid)
            stack.extend(ctx["children"].get(lid, ()))
        if not desc:
            return None
        nxt = None
        for oid in ctx["rel_order"]:
            other = ctx["by_id"][oid]
            if other.span.char_start <= ev.span.char_start or oid not in ctx["heat_inputs"]:
                continue
            if desc & set(other.consumes):
                nxt = other
                break
        if nxt is None:
            return None
        total, timed = Fraction(0), 0
        for oid in ctx["rel_order"]:
            other = ctx["by_id"][oid]
            if other.span.char_start < ev.span.char_start or other.span.char_start >= nxt.span.char_start:
                continue
            d = ctx["durations"].get(oid)
            if d and d["status"] in ("MEASURED", "RANGE"):
                total += d["value"][0] if isinstance(d["value"], tuple) else d["value"]
                timed += 1
        return {"event_id": nxt.event_id, "span": (nxt.span.char_start, nxt.span.char_end), "stated_minutes": total,
                "timed_steps": timed}

    # ------------------------------------------------------------------------------------------ main
    def bind_text(self, raw: str, locale: str | None = None) -> dict:
        base = self.base
        g = base.rung.run(SourceText.from_raw("BIND", raw), base.rung.config(locale=locale), schema=base.schema).graph
        events = sorted((e for e in g.events if e.span is not None), key=lambda e: e.span.char_start)
        ents = {e.entity_id: e for e in g.entities}
        producers = {p: ev for ev in g.events for p in ev.produces}
        children: dict[str, list[str]] = {}
        for e in g.entities:
            for p in e.parent_entity_ids:
                children.setdefault(p, []).append(e.entity_id)
        # heat inputs of every heat step, tracking the carried oven setpoint exactly as the heat binder does
        heat_inputs, setpoint, gas = {}, None, None
        plan = base.temperature_plan(raw, events)  # S178: the same temperature ownership as the heat binder (0.2.0)
        for ev in events:
            pid = _attr(ev.attributes, "proc_id")
            fam = base.family.get(pid)
            if fam == "HEAT_CONTROL" or fam in HEAT:
                a, b = base._sentence(raw, ev.span.char_start)
                tp = plan.get(ev.event_id)
                temps = tp.temps if tp else []
                gm = CB._GAS.search(raw, a, b)
                if fam == "HEAT_CONTROL":
                    setpoint = (temps[0], ev.event_id) if temps else setpoint
                    gas = f"GAS_{gm.group(1)}" if gm else (None if temps else gas)
                else:
                    heat_inputs[ev.event_id] = base._inputs(raw, g, ev, pid, fam, (a, b), temps, setpoint, gas, gm, plan=tp)
        # physical (relevant) events in text order and their clause windows
        rel = [ev for ev in events if ev.event_id in heat_inputs or self.nh_family(_attr(ev.attributes, "proc_id"))]
        windows: dict[str, tuple[int, int]] = {}
        groups: dict[tuple[int, int], list] = {}
        for ev in rel:
            groups.setdefault(self._sentence(raw, ev.span.char_start), []).append(ev)
        for (a, b), evs in groups.items():
            for i, ev in enumerate(evs):
                start = a if i == 0 else ev.span.char_start
                end = evs[i + 1].span.char_start if i + 1 < len(evs) else b
                windows[ev.event_id] = (start, end)
        ctx = {"raw": raw, "g": g, "ents": ents, "producers": producers, "children": children,
               "heat_inputs": heat_inputs, "rel_order": [e.event_id for e in rel], "by_id": {e.event_id: e for e in events},
               "windows": windows, "durations": {}}
        for ev in rel:  # durations first: the next-heat bound needs the durations of the steps in between
            ctx["durations"][ev.event_id] = self._durations(
                ev, raw, windows[ev.event_id],
                timed=self.nh_family(_attr(ev.attributes, "proc_id")) in TIMED_FAMILIES or ev.event_id in heat_inputs)
        out = []
        for ev in rel:
            pid = _attr(ev.attributes, "proc_id")
            fam = self.nh_family(pid)
            if fam is None:
                continue
            out.append(self._record(ev, pid, fam, ctx))
        return {"version": VERSION, "n_events": len(g.events), "events": out}

    def _record(self, ev, pid: str, fam: str, ctx: dict) -> dict:
        raw, win = ctx["raw"], ctx["windows"][ev.event_id]
        verb = (ev.span.char_start, ev.span.char_end)
        surface = ev.span.surface.lower()
        role = self.names.get(pid, "") or pid
        inp: dict[str, dict] = {k: unknown("NOT_BOUND") for k in INPUTS[fam]}
        cues: list[dict] = []
        dur = ctx["durations"][ev.event_id]
        if "duration" in inp:
            inp["duration"] = dur
        build = {"COOLING": self._cooling, "SEPARATION": self._separation, "FERMENT_LEAVEN": self._ferment,
                 "PRESERVATION": self._preservation, "MECHANICAL_CUT": self._cut, "MECHANICAL_MIX": self._mix,
                 "RESTING": self._rest, "STORAGE": self._storage}[fam]
        hist = build(ev, pid, role, surface, verb, win, ctx, inp, cues)
        self._stamp(inp, fam, pid)
        if surface in NON_VERB_SURFACES:
            cues.append({"name": "NON_VERB_SURFACE", "span": list(verb)})
        return {"event_id": ev.event_id, "process_id": pid, "family": self.base.family.get(pid), "nh_family": fam,
                "process_role": role, "form_candidate": FORM_CANDIDATE[fam], "layer": "TEXT_STATED",
                "version": VERSION, "verb_span": list(verb), "inputs": inp, "cues": cues, "history": hist or {}}

    @staticmethod
    def _stamp(inp: dict, fam: str, pid: str) -> None:
        """Per-axis provenance (S178, T4-C02): every bound axis gets ``span_id`` (``C:a-b`` of its span) and ``row`` (the code rule
        or table that fixed it: the verb's process id for a definition basis, else the family, axis and basis); unknown axes keep
        their ``reason``."""
        for axis, x in inp.items():
            if x["status"] == "UNKNOWN":
                continue
            x.setdefault("span_id", f"C:{x['span'][0]}-{x['span'][1]}" if x.get("span") else None)
            x.setdefault("row", f"nonheat_binding:{x['basis']}:{pid}" if x["basis"] in ("PROCESS_DEFINITION", "PHYSICAL_DEFINITION")
                         else f"nonheat_binding:{fam}.{axis}.{x['basis']}")

    # ------------------------------------------------------------------------------------------ families
    def _env(self, table_key: str, raw, win, verb, inp, fallback_reason="NO_ENVIRONMENT_CUE") -> None:
        cue = self._cue(_C["ENV"], raw, win, verb[0], ENV_ALLOWED[table_key])
        inp["environment"] = known(cue[0], "QUALITATIVE", "TEXT_CUE", cue[1]) if cue else unknown(fallback_reason)

    def _cooling(self, ev, pid, role, surface, verb, win, ctx, inp, cues):
        raw = ctx["raw"]
        inp.update(self._temperature_inputs(raw, win, verb[0], True))
        self._env("COOLING", raw, win, verb, inp)
        if inp["environment"]["status"] == "UNKNOWN":
            if surface.startswith("refrig"):
                inp["environment"] = known("FRIDGE", "QUALITATIVE", "PROCESS_DEFINITION", verb)
            elif pid == "PROC-000040":  # freeze
                inp["environment"] = known("FREEZER", "QUALITATIVE", "PROCESS_DEFINITION", verb)
        target = {"PROC-000038": "COOLED", "PROC-000039": "CHILLED", "PROC-000040": "FROZEN", "PROC-000041": "THAWED"}
        inp["target_state"] = known(target[pid], "QUALITATIVE", "PROCESS_DEFINITION", verb)
        prior = self._prior_heat(ev, ctx)
        if pid == "PROC-000041":
            inp["start_state"] = known("FROZEN", "QUALITATIVE", "PROCESS_DEFINITION", verb)
        elif prior:
            inp["start_state"] = known("POST_HEAT", "QUALITATIVE", prior["basis"], prior["span"])
        else:
            inp["start_state"] = unknown("NO_PRIOR_HEAT_LINK")
        inp["piece_size_class"] = self._size_class(ctx["g"], ctx["ents"], ctx["producers"], ev.consumes)
        return {"prior_heat": prior} if prior else {}

    def _separation(self, ev, pid, role, surface, verb, win, ctx, inp, cues):
        raw = ctx["raw"]
        inp["removed_phase"] = known(REMOVED_PHASE[pid], "QUALITATIVE", "PROCESS_DEFINITION", verb) \
            if pid in REMOVED_PHASE else unknown("VERB_NOT_IN_TABLE")
        win = self._extended_window(ev, pid, win, ctx)
        fate = unknown("NO_FATE_CUE")
        m = _DISCARD.search(raw, win[0], win[1])
        if m:
            tail = raw[m.end():min(win[1], m.end() + 60)]
            lq, sd = _LIQ.search(tail), _SOLID.search(tail)
            if lq and (not sd or lq.start() <= sd.start()):
                fate = known("DISCARDED", "QUALITATIVE", "TEXT_CUE", (m.start(), m.end() + lq.end()))
                inp["removed_phase"] = known("LIQUID", "QUALITATIVE", "TEXT_CUE", (m.start(), m.end() + lq.end())) \
                    if pid == "PROC-000083" else inp["removed_phase"]
            elif sd:
                inp["removed_phase"] = known("SOLID", "QUALITATIVE", "TEXT_CUE", (m.start(), m.end() + sd.end())) \
                    if pid == "PROC-000083" else inp["removed_phase"]
        r = _RETAIN.search(raw, win[0], win[1])
        if r and fate["status"] == "UNKNOWN":
            fate = known("RETAINED", "QUALITATIVE", "TEXT_CUE", (r.start(), r.end()))
        inp["liquid_fate"] = fate
        if surface.startswith(("rins", "wash")):
            inp["rinse_medium"] = known("WATER", "QUALITATIVE", "PROCESS_DEFINITION", verb)
            t = _RINSE_T.search(raw, win[0], win[1])
            inp["rinse_temperature_class"] = known(_RINSE_CLASS[(t.group(1) or t.group(2)).lower()], "QUALITATIVE",
                                                   "TEXT_CUE", (t.start(), t.end())) if t \
                else unknown("NO_RINSE_TEMPERATURE_CUE")
        else:
            inp["rinse_medium"] = unknown("NOT_A_RINSE")
            inp["rinse_temperature_class"] = unknown("NOT_A_RINSE")
        rel, hist = ctx["rel_order"], {}
        pos = rel.index(ev.event_id)
        inp["follows_soak_or_brine"] = unknown("NO_SOAK_OR_BRINE_JUST_BEFORE")
        for oid in reversed(rel[max(0, pos - 2):pos]):
            other = ctx["by_id"][oid]
            opid = _attr(other.attributes, "proc_id")
            if opid in SOAKLIKE and abs(other.order[0] - ev.order[0]) <= 1:
                inp["follows_soak_or_brine"] = known(SOAKLIKE[opid], "QUALITATIVE", "ORDER_ADJACENT",
                                                     (other.span.char_start, other.span.char_end))
                break
        return hist

    @staticmethod
    def _extended_window(ev, pid, win, ctx) -> tuple[int, int]:
        """"drain and discard the water": a separation verb also reads the clause of an immediately following
        discard verb in the same sentence (the discard verb owns its own clause as well)."""
        if pid == "PROC-000083":
            return win
        rel = ctx["rel_order"]
        pos = rel.index(ev.event_id)
        if pos + 1 < len(rel):
            nxt = ctx["by_id"][rel[pos + 1]]
            nxt_win = ctx["windows"][nxt.event_id]
            if _attr(nxt.attributes, "proc_id") == "PROC-000083" and nxt_win[0] == win[1] and \
                    nxt.span.char_start - win[1] <= 12:
                return (win[0], nxt_win[1])
        return win

    def _medium(self, pid, raw, win, verb, inp, cues) -> None:
        found = {}
        for cls, rx in _C["MEDIUM"]:
            ms = list(rx.finditer(raw, win[0], win[1]))
            if ms:
                m = min(ms, key=lambda x: abs(x.start() - verb[0]))
                found[cls] = (m.start(), m.end())
        if found:
            cls = next(c for c, _ in _C["MEDIUM"] if c in found)
            inp["medium"] = known(cls, "QUALITATIVE", "TEXT_CUE", found[cls])
            if len(found) > 1:
                cues.append({"name": "MULTIPLE_MEDIUM_CUES", "span": list(found[cls])})
        elif pid in VERB_MEDIUM:
            inp["medium"] = known(VERB_MEDIUM[pid], "QUALITATIVE", "PROCESS_DEFINITION", verb)
        elif pid == "PROC-000129":  # soak: a liquid is implied, which one is not
            inp["medium"] = known("LIQUID_UNSPECIFIED", "QUALITATIVE", "PROCESS_DEFINITION", verb)
        else:
            inp["medium"] = unknown("NO_MEDIUM_CUE")
        for name, rx in (("salt_concentration_pct", _SALT), ("acid_concentration_pct", _ACID)):
            inp[name] = unknown("NO_CONCENTRATION_STATED")
            for m in rx.finditer(raw, win[0], win[1]):
                v = Fraction(m.group("v") or m.group("w"))
                if 0 < v <= 40:
                    inp[name] = known(v, "MEASURED", "TEXT_STATED", (m.start(), m.end()))
                    break

    def _ferment(self, ev, pid, role, surface, verb, win, ctx, inp, cues):
        raw = ctx["raw"]
        inp.update({k: v for k, v in self._temperature_inputs(raw, win, verb[0], False).items()})
        self._env("FERMENT_LEAVEN", raw, win, verb, inp)
        self._medium(pid, raw, win, verb, inp, cues)
        inp["piece_size_class"] = self._size_class(ctx["g"], ctx["ents"], ctx["producers"], ev.consumes)
        return {}

    def _preservation(self, ev, pid, role, surface, verb, win, ctx, inp, cues):
        raw = ctx["raw"]
        inp.update(self._temperature_inputs(raw, win, verb[0], False))
        key = "PRESERVATION_DRY" if pid == "PROC-000133" else \
            "PRESERVATION_HEAT" if pid in ("PROC-000131", "PROC-000132", "PROC-000134") else "PRESERVATION_SOAK"
        self._env(key, raw, win, verb, inp)
        env = inp["environment"]
        if env["status"] != "UNKNOWN" and env["value"] == "BOILING_WATER_BATH" \
                and inp["medium_temperature"]["status"] == "UNKNOWN":
            inp["medium_temperature"] = known(Fraction(100), "MEASURED", "PHYSICAL_DEFINITION", env["span"])
        self._medium(pid, raw, win, verb, inp, cues)
        if pid == "PROC-000131" and EQUIPMENT.search(raw[verb[0]:min(win[1], verb[0] + 48)]):
            m = EQUIPMENT.search(raw, verb[0], min(win[1], verb[0] + 48))
            cues.append({"name": "EQUIPMENT_LIKELY", "span": [m.start(), m.end()]})
        inp["piece_size_class"] = self._size_class(ctx["g"], ctx["ents"], ctx["producers"], ev.consumes)
        return {}

    def _cut(self, ev, pid, role, surface, verb, win, ctx, inp, cues):
        raw = ctx["raw"]
        cls = CUT_CLASS_NH.get(pid)
        inp["cut_class"] = known(cls, "QUALITATIVE", "PROCESS_DEFINITION", verb) if cls else unknown("VERB_NOT_IN_TABLE")
        lvl = DISRUPTION.get(cls)
        inp["disruption_level"] = known(lvl, "QUALITATIVE", "PROCESS_DEFINITION", verb) if lvl \
            else unknown("NO_DISRUPTION_CLASS_FOR_CUT")
        cue = self._cue(_C["ENZ"], raw, win, verb[0])
        inp["enzyme_system"] = known(cue[0], "QUALITATIVE", "TEXT_CUE", cue[1]) if cue else unknown("NO_FOOD_WORD_CUE")
        nxt = self._next_heat(ev, ctx)
        own = ctx["durations"].get(ev.event_id) or {}
        hist: dict = {}
        if nxt is None:
            inp["time_until_next_heat"] = unknown("NO_HEAT_DOWNSTREAM_IN_LINEAGE")
        else:
            total = nxt["stated_minutes"]
            hist["next_heat"] = {"event_id": nxt["event_id"], "timed_steps": nxt["timed_steps"]}
            inp["time_until_next_heat"] = known(total, "BOUND_LOWER", "LINEAGE_AND_STATED_DURATIONS", nxt["span"]) \
                if total > 0 else known("NEXT_HEAT_NO_TIMED_STEP_BETWEEN", "QUALITATIVE", "LINEAGE", nxt["span"])
        if own.get("status") in ("MEASURED", "RANGE", "BOUND_UPPER", "BOUND_LOWER"):
            cues.append({"name": "HOLD_TIME_ATTACHED_TO_CUT", "span": own["span"]})
        return hist

    def _mix(self, ev, pid, role, surface, verb, win, ctx, inp, cues):
        raw = ctx["raw"]
        tool = self._cue(_C["TOOL"], raw, win, verb[0])
        inp["tool"] = known(tool[0], "QUALITATIVE", "TEXT_CUE", tool[1]) if tool else unknown("NO_TOOL_CUE")
        if surface == "process":  # the lexicon maps "process" to blend; with canning words it is likely a canning step
            canning = self._cue(_C["ENV"], raw, win, verb[0], ("BOILING_WATER_BATH", "PRESSURE_CANNER"))
            if canning:
                cues.append({"name": "BLEND_VERB_PROCESS_WITH_CANNING_CUE", "span": list(canning[1])})
        for name, rx in (("aerated", _AER), ("emulsified", _EMU), ("developed", _DEV)):
            m = rx.search(raw, win[0], win[1])
            if m:
                inp[name] = known(True, "QUALITATIVE", "TEXT_CUE", (m.start(), m.end()))
            elif MIX_VERB_FLAG.get(pid) == name:
                inp[name] = known(True, "QUALITATIVE", "PROCESS_DEFINITION", verb)
            else:
                inp[name] = unknown("NO_FLAG_CUE")
        return {}

    def _rest(self, ev, pid, role, surface, verb, win, ctx, inp, cues):
        raw = ctx["raw"]
        self._env("RESTING", raw, win, verb, inp)
        cue = self._cue(_C["COVER"], raw, win, verb[0])
        inp["cover_state"] = known(cue[0], "QUALITATIVE", "TEXT_CUE", cue[1]) if cue else unknown("NO_COVER_CUE")
        prior = self._prior_heat(ev, ctx)
        inp["prior_heat_link"] = known(prior["process_id"], "QUALITATIVE", prior["basis"], prior["span"]) if prior \
            else unknown("NO_PRIOR_HEAT_LINK")
        inp["piece_size_class"] = self._size_class(ctx["g"], ctx["ents"], ctx["producers"], ev.consumes)
        return {"prior_heat": prior} if prior else {}

    def _storage(self, ev, pid, role, surface, verb, win, ctx, inp, cues):
        raw = ctx["raw"]
        inp.update(self._temperature_inputs(raw, win, verb[0], False))
        self._env("STORAGE", raw, win, verb, inp)
        cue = self._cue(_C["CONT"], raw, win, verb[0])
        inp["container"] = known(cue[0], "QUALITATIVE", "TEXT_CUE", cue[1]) if cue else unknown("NO_CONTAINER_CUE")
        return {}


# ---------------------------------------------------------------------------------------------------- readiness
READY = {  # per (family, role-group): groups of any-of inputs, each group must be satisfied
    "COOLING_FREEZE": (("environment", "medium_temperature"), ("piece_size_class",)),
    "COOLING_DEFROST": (("environment", "medium_temperature"), ("piece_size_class",)),
    "COOLING_COOL": (("duration",), ("environment", "medium_temperature"), ("piece_size_class",)),
    "SEPARATION_LIQUID": (("removed_phase",), ("liquid_fate",)),
    "SEPARATION_OTHER": (("removed_phase",),),
    "FERMENT_UPTAKE": (("duration",), ("medium",), ("piece_size_class",)),
    "FERMENT_STATE": (("duration",),),
    "PRESERVATION_DRY": (("duration",), ("environment",), ("medium_temperature",), ("piece_size_class",)),
    "PRESERVATION_UPTAKE": (("duration",), ("medium",), ("piece_size_class",)),
    "PRESERVATION_F": (("duration",), ("medium_temperature",)),
    "MECHANICAL_CUT": (("cut_class",),),
    "MECHANICAL_MIX": (("aerated", "emulsified", "developed"),),
    "RESTING": (("duration",), ("prior_heat_link",), ("piece_size_class",)),
    "STORAGE": (("duration",), ("environment", "medium_temperature")),
}
DURATION_OK = ("MEASURED", "RANGE")
UPTAKE_MEDIA = ("BRINE", "VINEGAR", "CITRUS_JUICE", "WATER", "MARINADE_OTHER")


def driver_group(rec: Mapping) -> str:
    fam, pid = rec["nh_family"], rec["process_id"]
    if fam == "COOLING":
        return "COOLING_FREEZE" if pid == "PROC-000040" else "COOLING_DEFROST" if pid == "PROC-000041" else "COOLING_COOL"
    if fam == "SEPARATION":
        return "SEPARATION_LIQUID" if pid in ("PROC-000078", "PROC-000079") else "SEPARATION_OTHER"
    if fam == "FERMENT_LEAVEN":
        return "FERMENT_UPTAKE" if pid in ("PROC-000129", "PROC-000100") else "FERMENT_STATE"
    if fam == "PRESERVATION":
        return "PRESERVATION_DRY" if pid == "PROC-000133" else \
            "PRESERVATION_UPTAKE" if pid in ("PROC-000130", "PROC-000155") else "PRESERVATION_F"
    return fam


def missing_core(rec: Mapping) -> list[str]:
    """Names of the input groups that are not satisfied by text alone (empty list = full L1 driver inputs)."""
    inp, miss = rec["inputs"], []
    if any(c["name"] == "NON_VERB_SURFACE" for c in rec["cues"]):
        miss.append("verb_surface")
    for group in READY[driver_group(rec)]:
        ok = False
        for n in group:
            x = inp[n]
            if x["status"] == "UNKNOWN":
                continue
            if n == "duration" and x["status"] not in DURATION_OK and driver_group(rec) != "STORAGE":
                continue
            if n == "medium" and x["value"] not in UPTAKE_MEDIA:
                continue
            if n == "piece_size_class" and rec["nh_family"] != "MECHANICAL_CUT" and x["value"] not in GEOMETRY_CLASSES:
                continue
            if n == "cut_class" and x["value"] not in GEOMETRY_CLASSES:
                continue
            ok = True
        if not ok:
            miss.append("|".join(group))
    return miss


# ---------------------------------------------------------------------------------------------------- census
_CTX: dict = {}


def _steps(rec: Mapping) -> list[str]:
    return [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]


def row(rec: Mapping, src_family, recipe_id) -> dict:
    return {"recipe_id": recipe_id, "source_family": src_family, "event_id": rec["event_id"],
            "process_id": rec["process_id"], "family": rec["family"], "nh_family": rec["nh_family"],
            "process_role": rec["process_role"], "form_candidate": rec["form_candidate"], "layer": "TEXT_STATED",
            "version": VERSION, "verb_span": rec["verb_span"], "cues": rec["cues"], "history": rec["history"],
            "inputs": {k: {kk: _s(vv) for kk, vv in v.items()} for k, v in rec["inputs"].items()}}


def _chunk(args: tuple[int, list[Mapping]]) -> dict:
    idx, recs = args
    binder, out_dir = _CTX["binder"], _CTX["records_dir"]
    c = Counter()
    fh = open(Path(out_dir) / f"part-{idx:05d}.jsonl", "w", encoding="utf-8") if out_dir else None
    try:
        for rec in recs:
            steps = _steps(rec)
            if not steps:
                continue
            c[("tot", "texts_with_steps")] += 1
            try:
                res = binder.bind_text("\n".join(steps), LOCALE.get(rec.get("source_family")))
            except Exception as e:  # noqa: BLE001 - class name only
                c[("exc", code(type(e).__name__))] += 1
                continue
            c[("tot", "events")] += res["n_events"]
            for ev in res["events"]:
                fam = ev["nh_family"]
                c[("fam", fam)] += 1
                c[("role", fam, code(ev["process_role"]))] += 1
                any_val = any(x["status"] != "UNKNOWN" for x in ev["inputs"].values())
                any_text = any(x["status"] != "UNKNOWN" and x["basis"] in TEXT_BASES for x in ev["inputs"].values())
                c[("any_l1_value", fam, any_val)] += 1
                c[("any_text_value", fam, any_text)] += 1
                miss = missing_core(ev)
                if not miss:
                    c[("driver_ready", fam)] += 1
                for m in miss:
                    c[("missing_core", fam, code(m))] += 1
                core = {n for grp in READY[driver_group(ev)] for n in grp}
                for name, x in ev["inputs"].items():
                    c[("st", fam, name, x["status"])] += 1
                    if x["basis"]:
                        c[("ba", fam, name, x["basis"])] += 1
                    elif x["status"] == "UNKNOWN" and name in core:
                        c[("why", fam, name, code(x.get("reason") or "UNSPECIFIED"))] += 1
                for cue in ev["cues"]:
                    c[("cue", fam, code(cue["name"]))] += 1
                if "prior_heat" in ev["history"]:
                    c[("prior_heat", fam, ev["history"]["prior_heat"]["basis"])] += 1
                if fh:
                    fh.write(json.dumps(row(ev, rec.get("source_family"), rec["recipe_id"]),
                                        separators=(",", ":")) + "\n")
    finally:
        if fh:
            fh.close()
    return dict(c)


def _nest(counts: Mapping[tuple, int], prefix: str) -> dict:
    out: dict = {}
    for key, v in sorted(counts.items(), key=lambda kv: str(kv[0])):
        if key[0] != prefix:
            continue
        d = out
        for k in key[1:-1]:
            d = d.setdefault(str(k), {})
        d[str(key[-1])] = v
    return out


def census_from_records(records: Iterable[Mapping], *, seed: str, size: int, workers: int = 1,
                        binder: NonHeatBinder | None = None, records_dir: Path | None = None) -> dict:
    if workers < 1:
        raise ValueError("workers must be positive")
    seen = 0

    def counted(it: Iterable[Mapping]) -> Iterator[Mapping]:
        nonlocal seen
        for rec in it:
            seen += 1
            yield rec

    sample = seeded_sample(counted(records), seed, size)
    _CTX.clear()
    _CTX.update(binder=binder or NonHeatBinder.load(), records_dir=str(records_dir) if records_dir else None)
    n = workers * 8 if workers > 1 else 1
    chunks = [(i, sample[i::n]) for i in range(n)]
    try:
        if workers == 1:
            parts = [_chunk(c) for c in chunks]
        else:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(workers) as pool:
                parts = pool.map(_chunk, chunks)
    finally:
        _CTX.clear()
    acc: Counter = Counter()
    for p in parts:
        acc.update(p)
    fams = {f: acc[("fam", f)] for f in NH_FAMILIES}
    report = {"record": "NONHEAT_BINDING_CENSUS_L1", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
              "label": "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD", "census_version": CENSUS_VERSION, "binder_version": VERSION,
              "layer": "TEXT_STATED", "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
              "seed_sha256": hashlib.sha256(seed.encode()).hexdigest(), "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC",
              "sample_size_requested": int(size), "recipes_seen": seen, "recipes_sampled": len(sample),
              "texts_with_steps": acc[("tot", "texts_with_steps")], "events": acc[("tot", "events")],
              "nonheat_events": sum(fams.values()), "events_by_family": fams,
              "driver_ready_events_by_family": {f: acc[("driver_ready", f)] for f in NH_FAMILIES},
              "any_l1_value_by_family": {f: acc[("any_l1_value", f, True)] for f in NH_FAMILIES},
              "any_text_value_by_family": {f: acc[("any_text_value", f, True)] for f in NH_FAMILIES},
              "events_by_role": _nest(acc, "role"), "input_status": _nest(acc, "st"), "input_basis": _nest(acc, "ba"),
              "unknown_reasons": _nest(acc, "why"), "missing_core_inputs": _nest(acc, "missing_core"),
              "cues": _nest(acc, "cue"), "prior_heat_link_basis": _nest(acc, "prior_heat"),
              "exceptions_by_class": {k[1]: v for k, v in sorted(acc.items()) if k[0] == "exc"}}
    D.assert_counts_only(report)
    return report
