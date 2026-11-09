"""Evidence gates for the router demo (S176 lane L-ROUTER, revised S177 SCIFIX-ROUTER). NON_CITABLE, DEMO_ONLY, AI_DRAFTED,
PROPOSED_PILOT.

Two screens that run BEFORE the G0 evidence pre-check of the unchanged Step 23a engine. They only ever narrow the
route; neither can create or upgrade one (``DIRECT`` -> weaker, never the reverse). Scientific 23b stays BLOCKED.

1. Target-presence screen (nutrient targets only). Is the nutrient there at all in what the process acts on?
   - A lot member is the ING of an ingredient line. Its SR Legacy identity comes from ``mechanism/sr_identity.py`` (S177):
     the Mac's curated ``registry/ing_sr_defaults_v1.csv`` is the identity of record (kind -> band: DIRECT / UK_US /
     DEFAULT_FORM HIGH, APPROX MEDIUM, the unmappable kinds no identity), and the old lexical file
     ``registry/ing_sr_legacy_match_draft_v1.csv`` supplies alternates and a fallback capped at MEDIUM. A member without a
     usable (HIGH / MEDIUM) rank-1 identity has UNKNOWN identity. The identity is NOT taken as certain: every rank 2-3
     candidate whose score is within ``identity_score_margin`` of the rank-1 score is a plausible alternative (the
     matcher could not rule it out: "pepper" has black pepper at rank 1 and sweet red pepper 0.12 below). The SR values
     come from the derived table ``registry/ing_sr_target_content_draft_v1.csv`` (built by
     ``tools/build_target_content_table.py`` from the adapter and SR Legacy, public domain), so the demo needs no
     ``data/raw`` at run time; ``source="sr"`` builds the identity and reads SR Legacy directly.
   - PRESENT: every HIGH / MEDIUM plausible candidate has a known SR value >= the floor. (Unchanged since S176.)
   - ABSENT is a negative claim and needs ALL THREE (S177, FINAL-SCI #6): (a) the rank-1 band is HIGH (MEDIUM matches
     were only ~67 % plausible in the L-LOT audit); (b) every rank-1..3 candidate within the identity margin, of ANY
     band (LOW included), has a KNOWN SR value below the floor; (c) the ING category matches the SR food group of the
     rank-1 candidate under ``CATEGORY_CROSSWALK`` (AI_DRAFTED, strict; an ING with no category cannot be checked).
     Anything else that is not PRESENT is UNKNOWN (never 0). Found by the reviewers: "herb" -> chamomile tea,
     "coleslaw" -> coleslaw dressing, "lemongrass" -> a branded carrot soup, each a false TARGET_ABSENT before S177.
   - Lot state: PRESENT if >= 1 member is PRESENT; ABSENT only if EVERY member is ABSENT (no member of unknown
     identity); otherwise UNKNOWN. ABSENT -> the item routes NOT_APPLICABLE with reason ``TARGET_ABSENT``;
     UNKNOWN keeps routing and adds ``TARGET_PRESENCE_UNKNOWN``. A target with no floor row is NOT_SCREENED.
   - The floor is a PROPOSED_PILOT screening value in ``registry/target_presence_floor_v1_PROPOSED.csv`` (unsigned,
     a human decision). It is a screen on SR Legacy composition (public domain): analytical, imputed or assumed values,
     with the basis recorded (S178 FIX-ROUTER, R4: the SR derivation code and number of data points of every value are
     carried in the content table and in the gate's output). It is never emitted as a number about the user's food and
     it is not a chemistry threshold.
   - S178 (R4): ABSENT also needs every plausible value to be ANALYTICAL: SR derivation code A, AI or AR
     (``ANALYTICAL_DERIVATION_CODES``) with at least one data point. An SR zero (or sub-floor value) that is assumed
     (``Z``), imputed, calculated, taken from a formulation / recipe / label claim, or that has no derivation code and 0
     data points supports no negative claim: the member is UNKNOWN with blocker ``SR_ZERO_NOT_ANALYTICAL``. A screen
     built without any basis (``basis=None``, e.g. an older content table) is fail-closed: ``SR_BASIS_NOT_RECORDED``.
     A separate ``ABSENT_SR_ASSUMED`` state is a human decision (SCI-B Q2) and is not implemented.
2. Lot-context gate (SSOT 286.2 G0-C). Measured retention (EVD) is for a food cooked as itself, from raw. DIRECT /
   BRACKETING stands only when (i) the lot the process acts on has that food as its sole member AND (ii) the lot has
   not already been through a heat or leach (SEPARATION / SOAK) event. (i) fails -> reason ``MERGED_LOT_CONTEXT``;
   (ii) fails (S177, FINAL-SCI #7: boil then fry on the same food) -> reason ``PRIOR_PROCESS_CONTEXT``. Either way the
   pre-check is withheld, the engine applies its own order to the rest (in the demo, with no reviewed mechanism:
   UNKNOWN) and the EVD rows stay visible as ``evidence_not_applied``. A route is never upgraded.
   S178 (FIX-ROUTER, SCI-B R2 / R5 / R6), all in the narrowing direction:
   - R2 STATED_PRIOR_STATE (Layer 1 TEXT_STATED, never inferred): a processed-state word on the food itself ("the baked
     potatoes", "tinned tomatoes", "hard-boiled eggs", "leftover rice") or in its ingredient line ("1 can chopped
     tomatoes", "2 boiled potatoes") is a prior process of kind HEAT / LEACH / PRESERVED / PROCESSED from the registered
     word list ``STATE_WORDS`` (AI_DRAFTED). It withholds DIRECT with ``PRIOR_PROCESS_CONTEXT``; ``prior_basis`` says
     where it came from (``EVENT``, ``TEXT_STATED_STATE``, ``INGREDIENT_LINE``, ``EVENT_UNRESOLVED``).
   - R5 fail-closed: an ancestor event with no resolved process (or a process outside the hierarchy) is UNKNOWN context,
     never "no prior process": DIRECT is withheld with ``PRIOR_PROCESS_UNRESOLVED``. A NO_LOT item cannot keep a raw
     DIRECT (``LOT_CONTEXT_UNKNOWN``).
   - R6: freeze / defrost are a prior process (kind PRESERVED). The exemption for EVD rows that presuppose a prior cook
     (reheat; drain of a cooked food) would LOOSEN the S177 rule, so it is NOT applied: it is a human decision (SCI-B
     Q1, ``exempt_presupposed=False``); the census only counts the items it would release.
3. Event-role gate (S178, SCI-B R3, at the router, Rung A unchanged). Rung A turns some attributive participles ("add
   mashed potatoes", "over grilled shrimp", "fresh and canned peaches") and serving suggestions ("serve with roast beef")
   into events. ``event_roles`` reads the text around each ACTION: a participle (or a base form after a preposition)
   directly followed by its food is ``ATTRIBUTIVE_STATE``; an ACTION inside a "serve / garnish / top ... with" clause
   that takes a food directly is ``SERVING_SUGGESTION``. Such an event cannot get DIRECT (reasons
   ``ATTRIBUTIVE_STATE_NOT_EVENT`` / ``SERVING_SUGGESTION_NOT_EVENT``; the route is the engine's UNKNOWN), and an
   attributive heat / leach / state word feeds the food's prior state (R2).

Every gate output carries codes only (no recipe text). Lot membership and ancestry come from the Rung A event graph.
"""
from __future__ import annotations

import csv
import functools
import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

VERSION = "evidence-gates-0.3.0-draft"
STATUS = "AI_DRAFTED_PROPOSED_PILOT_UNSIGNED"
ROOT = Path(__file__).resolve().parents[3]
FLOOR_PATH = ROOT / "registry" / "target_presence_floor_v1_PROPOSED.csv"
MATCH_PATH = ROOT / "registry" / "ing_sr_legacy_match_draft_v1.csv"
TABLE_PATH = ROOT / "registry" / "ing_sr_target_content_draft_v1.csv"
SR_RELEASE = "USDA_SR_LEGACY_2018_04"
TABLE_COLUMNS = ("ing_id", "candidate_rank", "fdc_id", "confidence_band", "match_score", "nutrient_key", "unit",
                 "amount_per_100g", "source_release", "ing_category", "sr_category", "identity_source", "registry_kind",
                 "sr_derivation_code", "sr_data_points")
USABLE_BANDS = ("HIGH", "MEDIUM")
ABSENT_RANK1_BAND = "HIGH"          # S177: ABSENT needs a HIGH-band rank-1 identity
# S178 (R4): SR Legacy derivation codes that count as analytical (food_nutrient_derivation.csv: A "Analytical", AI
# "Analytical data; from the literature or government; incomplete documentation", AR "Analytical data; derived by linear
# regression"). Strict on purpose (D-071): a human may widen it (e.g. JA, MA, DA, PAK); an AI does not.
ANALYTICAL_DERIVATION_CODES = frozenset({"A", "AI", "AR"})
NO_DERIVATION_CODE = "NONE"         # the SR row has an amount but a blank derivation_id
NOT_RECORDED_CODE = "NOT_RECORDED"  # the SR files at hand carry no derivation (column or table missing): never analytical
BASIS_STATUS = "AI_DRAFTED_UNSIGNED_STRICT"

PRESENT, ABSENT, UNKNOWN, NOT_SCREENED = "PRESENT", "ABSENT", "UNKNOWN", "NOT_SCREENED"
SINGLE_MEMBER, MERGED, NO_LOT = "SINGLE_MEMBER", "MERGED", "NO_LOT"
NOT_APPLICABLE = "NOT_APPLICABLE"
R_TARGET_ABSENT = "TARGET_ABSENT"
R_PRESENCE_UNKNOWN = "TARGET_PRESENCE_UNKNOWN"
R_MERGED = "MERGED_LOT_CONTEXT"
R_PRIOR_PROCESS = "PRIOR_PROCESS_CONTEXT"
R_PRIOR_UNRESOLVED = "PRIOR_PROCESS_UNRESOLVED"        # S178 R5(a)
R_LOT_UNKNOWN = "LOT_CONTEXT_UNKNOWN"                  # S178 R5(b)
R_ATTRIBUTIVE = "ATTRIBUTIVE_STATE_NOT_EVENT"          # S178 R3
R_SERVING = "SERVING_SUGGESTION_NOT_EVENT"             # S178 R3
GATE_REASONS = (R_TARGET_ABSENT, R_PRESENCE_UNKNOWN, R_MERGED, R_PRIOR_PROCESS, R_PRIOR_UNRESOLVED, R_LOT_UNKNOWN,
                R_ATTRIBUTIVE, R_SERVING)
B_NOT_ANALYTICAL = "SR_ZERO_NOT_ANALYTICAL"            # S178 R4 member blocker
B_BASIS_NOT_RECORDED = "SR_BASIS_NOT_RECORDED"         # S178 R4: screen built without any derivation basis
# S178 R3 event roles
PROCESS_STEP, ATTRIBUTIVE_STATE, SERVING_SUGGESTION = "PROCESS_STEP", "ATTRIBUTIVE_STATE", "SERVING_SUGGESTION"
ROLE_REASON = {ATTRIBUTIVE_STATE: R_ATTRIBUTIVE, SERVING_SUGGESTION: R_SERVING}
# S178 prior-process bases (where a prior kind came from)
PB_EVENT, PB_UNRESOLVED, PB_TEXT, PB_LINE = "EVENT", "EVENT_UNRESOLVED", "TEXT_STATED_STATE", "INGREDIENT_LINE"
# route strength used by the never-upgrade property (higher = stronger claim); NOT_APPLICABLE is outside the ladder
ROUTE_STRENGTH = {"DIRECT": 5, "INTERPOLATE": 4, "SIMULATE": 3, "QUALITATIVE": 2, "ASK": 1, "UNKNOWN": 0}

# ING category (registry ing_category of the match file) -> SR Legacy food groups it may legitimately be matched to.
# AI_DRAFTED (S177, FINAL-SCI #6), strict on purpose: a pair that is not listed means "category not confirmed", and an
# unconfirmed category can never support an ABSENT claim (it stays UNKNOWN). Fresh herbs that SR files under
# "Vegetables and Vegetable Products", juices filed under "Fruits and Fruit Juices" and the like are therefore UNKNOWN,
# not ABSENT. A human may widen it (decision, not an AI act). An ING with an empty category is never confirmed.
CATEGORY_CROSSWALK_STATUS = "AI_DRAFTED_UNSIGNED"
CATEGORY_CROSSWALK: Mapping[str, frozenset] = {
    "BEVERAGE": frozenset({"Beverages"}),
    "CEREAL": frozenset({"Cereal Grains and Pasta", "Breakfast Cereals", "Baked Products"}),
    "CONDIMENT": frozenset({"Soups, Sauces, and Gravies", "Spices and Herbs"}),
    "DAIRY": frozenset({"Dairy and Egg Products"}),
    "EGG": frozenset({"Dairy and Egg Products"}),
    "FAT_OIL": frozenset({"Fats and Oils"}),
    "FRUIT": frozenset({"Fruits and Fruit Juices"}),
    "HERB_SPICE": frozenset({"Spices and Herbs"}),
    "LEGUME": frozenset({"Legumes and Legume Products"}),
    "MEAT": frozenset({"Beef Products", "Pork Products", "Poultry Products", "Lamb, Veal, and Game Products",
                       "Sausages and Luncheon Meats"}),
    "NUT_SEED": frozenset({"Nut and Seed Products"}),
    "SEAFOOD": frozenset({"Finfish and Shellfish Products"}),
    "SWEETENER": frozenset({"Sweets"}),
    "VEGETABLE": frozenset({"Vegetables and Vegetable Products"}),
}


def category_matches(ing_category: str | None, sr_category: str | None) -> bool:
    """True when the ING category is confirmed against the SR food group by ``CATEGORY_CROSSWALK`` (empty never is)."""
    return bool(ing_category and sr_category and sr_category in CATEGORY_CROSSWALK.get(ing_category, frozenset()))


# Prior-process classes for the lot-context gate (S177, FINAL-SCI #7). An event of one of these classes that produced
# the lot (or an ancestor of it) means the lot is no longer the raw food a measured raw-to-cooked retention row is
# about. Heat = the PROC heat families + the heat preservation processes; leach = SEPARATION family (drain, strain,
# rinse, squeeze, ...) and the soak-like processes (the SEPARATION / SOAK wording of the finding). Taken from the PROC
# hierarchy and nonheat_binding's SOAKLIKE / PRESERVATION_HEAT sets. Withholding is the safe direction; a human may narrow.
PRIOR_HEAT_FAMILIES = frozenset({"WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL"})
PRIOR_LEACH_FAMILIES = frozenset({"SEPARATION"})
PRIOR_HEAT_PROCS = frozenset({"PROC-000131", "PROC-000132", "PROC-000134", "PROC-000133"})   # sterilise can pasteurise dry
PRIOR_LEACH_PROCS = frozenset({"PROC-000129", "PROC-000100", "PROC-000155", "PROC-000130"})  # soak marinate brine pickle
PRIOR_PRESERVED_PROCS = frozenset({"PROC-000040", "PROC-000041"})                             # S178 R6: freeze defrost
# PRESERVED (S178): frozen / thawed / cured state; PROCESSED: an earlier process the text states without its class
# (leftover, mashed, puréed, instant); UNRESOLVED (S178 R5): an ancestor event whose process is unknown.
PRIOR_KINDS = ("HEAT", "LEACH", "PRESERVED", "PROCESSED", "UNRESOLVED")
KNOWN_PRIOR_KINDS = PRIOR_KINDS[:4]
PRIOR_REHEAT_PROC, PRIOR_DRAIN_PROC = "PROC-000033", "PROC-000078"
_COOKED_ROW = re.compile(r"\b(?:COOKED|CKD|BOILED|BLD)\b", re.IGNORECASE)

# S178 R2: registered processed-state words (Layer 1 TEXT_STATED; AI_DRAFTED, a human may narrow or widen). Each word
# maps to the prior kind of the PROC class it names (canned / dried follow PROC can / dry, which the S177 classes count as
# heat). Matched on word boundaries ("uncooked" never matches "cooked"); a word inside the food's own surface ("smoked
# salmon" as an alias) belongs to the food's identity and is not counted; "non-" / "not " / "un-" before it cancels it.
STATE_WORDS_STATUS = "AI_DRAFTED_UNSIGNED"
STATE_WORDS: Mapping[str, str] = {
    **{w: "HEAT" for w in ("baked", "boiled", "parboiled", "cooked", "precooked", "roasted", "fried", "grilled",
                           "broiled", "steamed", "poached", "toasted", "braised", "stewed", "sauteed", "sautéed",
                           "microwaved", "blanched", "scalded", "scrambled", "charred", "seared", "barbecued",
                           "barbequed", "caramelized", "caramelised", "canned", "tinned", "jarred", "dried",
                           "dehydrated", "smoked", "evaporated", "condensed")},
    **{w: "LEACH" for w in ("drained", "rinsed", "soaked", "strained", "marinated", "brined", "pickled")},
    **{w: "PRESERVED" for w in ("frozen", "thawed", "defrosted", "cured", "corned", "candied")},
    **{w: "PROCESSED" for w in ("leftover", "leftovers", "mashed", "pureed", "puréed", "instant", "reconstituted")},
}
STATE_WORD_RE = re.compile(r"(?<![A-Za-z])(?:left[- ]over|" + "|".join(sorted(map(re.escape, STATE_WORDS), key=len,
                                                                             reverse=True)) + r")(?![A-Za-z])",
                           re.IGNORECASE)
STATE_CONTAINER_RE = re.compile(r"(?:\d|\))[ \t]*(?:cans?|tins?|jars?)(?![A-Za-z])", re.IGNORECASE)   # "1 can", "(15 oz) can"
_STATE_CANCEL = re.compile(r"(?:\bnon-?|\bnot[ \t]+|\bun-)$", re.IGNORECASE)
# S179 (SCI re-review #4): a state stated right AFTER the food also describes it: "potatoes (already boiled)",
# "potatoes that you boiled yesterday", "potatoes, previously boiled, ...", "potatoes left over from dinner". Text order
# is not time order. Only these anchored forms count; a negation ("that are not cooked") never matches.
_POST_STATE_WORDS = "|".join(sorted(map(re.escape, STATE_WORDS), key=len, reverse=True))
POST_STATE_RE = re.compile(
    r"^[ \t]*(?:\([ \t]*(?:(?:already|previously|pre-?)[ \t]*)?"
    r"|,?[ \t]*(?:that|which)[ \t]+(?:(?:you|we|i|they|have|has|had|were|was|been|are|is|already|previously|just)[ \t]+)*"
    r"|,?[ \t]*(?:already|previously)[ \t]+)"
    r"(?P<w>" + _POST_STATE_WORDS + r")(?![A-Za-z])"
    r"|^[ \t]*(?P<lo>left[- ]over)(?![A-Za-z])", re.IGNORECASE)


def post_state_cue(text_after: str) -> str | None:
    """Prior kind stated immediately after a food mention (anchored at its end), else None."""
    m = POST_STATE_RE.match(text_after or "")
    if m is None:
        return None
    return "PROCESSED" if m.group("lo") else STATE_WORDS[m.group("w").lower()]


def state_cues(text: str) -> list[tuple[int, int, str]]:
    """(start, end, prior kind) of every registered processed-state cue in ``text`` (words and "N can / tin / jar")."""
    out = []
    for m in STATE_WORD_RE.finditer(text or ""):
        if _STATE_CANCEL.search(text[max(0, m.start() - 6):m.start()]):
            continue
        w = m.group(0).lower()
        out.append((m.start(), m.end(), "PROCESSED" if w.replace(" ", "-") == "left-over" else STATE_WORDS[w]))
    for m in STATE_CONTAINER_RE.finditer(text or ""):
        out.append((m.start(), m.end(), "HEAT"))
    return sorted(out)


def presupposes_prior_heat(process_id: str | None, raw_name: str | None) -> bool:
    """An EVD row about a food that was already cooked: reheat, or drain of a food the row names as cooked (SCI-B R6)."""
    if process_id == PRIOR_REHEAT_PROC:
        return True
    return process_id == PRIOR_DRAIN_PROC and bool(_COOKED_ROW.search(raw_name or ""))


class GateError(ValueError):
    """A gate registry is malformed (never a verdict)."""


# ----------------------------------------------------------------------------- registries
@dataclass(frozen=True)
class Floor:
    svar_id: str
    name: str
    nutrient_key: str            # key of sr_identity.NUTRIENT_IDS (the composition roster without its unit suffix)
    unit: str
    value: Fraction              # per 100 g edible portion, SR Legacy
    status: str
    margin: Fraction = Fraction(0)   # identity_score_margin: rank 2-3 candidates this close to rank 1 are plausible


def read_floors(path: Path = FLOOR_PATH) -> dict[str, Floor]:
    from culinarystate.mechanism.sr_identity import NUTRIENT_IDS, NUTRIENT_UNITS
    out: dict[str, Floor] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            key, svar = r["sr_nutrient_key"], r["target_svar_id"]
            if key not in NUTRIENT_IDS:
                raise GateError(f"{svar}: sr_nutrient_key {key!r} is not an SR nutrient the lot-state layer reads")
            if r["unit"] != NUTRIENT_UNITS[key]:
                raise GateError(f"{svar}: unit {r['unit']!r} != SR unit {NUTRIENT_UNITS[key]!r}")
            try:
                value = Fraction(r["floor_value"])
            except (ValueError, ZeroDivisionError) as exc:
                raise GateError(f"{svar}: floor_value is not a decimal number") from exc
            if value <= 0:
                raise GateError(f"{svar}: a floor must be > 0 (0 would make every member PRESENT)")
            try:
                margin = Fraction(r["identity_score_margin"])
            except (KeyError, ValueError, ZeroDivisionError) as exc:
                raise GateError(f"{svar}: identity_score_margin is not a decimal number") from exc
            if margin < 0:
                raise GateError(f"{svar}: identity_score_margin must be >= 0")
            out[svar] = Floor(svar, r["target_name"], key, r["unit"], value, r["status"], margin)
    return out


# ING id -> ((fdc_id, band, match score), ...), rank 1 first; rank 1-3 candidates of ANY band (S177: LOW included so the
# margin test sees every alternative). An ING is present only when its rank-1 proposal is HIGH / MEDIUM.
Candidates = Mapping[str, tuple[tuple[int, str, Fraction], ...]]
# ING id -> (ING category, SR food group of its rank-1 candidate), both as written in the match registry
Categories = Mapping[str, tuple[str, str]]


def _read_match_rows(path: Path) -> dict[str, list[dict]]:
    rows: dict[str, list[dict]] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["fdc_id"] != "" and r["rank"] in ("1", "2", "3"):
                rows.setdefault(r["ing_id"], []).append(r)
    return rows


def read_candidates(path: Path = MATCH_PATH) -> dict[str, tuple[tuple[int, str, Fraction], ...]]:
    """Candidates per ING: rank 1-3 of ANY band, in rank order. An ING is present only when its rank-1 proposal is HIGH /
    MEDIUM (a LOW / missing rank 1 means unknown identity). LOW rank 2-3 rows are kept: they are plausible alternative
    identities the ABSENT screen must see (S177, FINAL-SCI #6)."""
    out = {}
    for ing, rs in _read_match_rows(path).items():
        rs = sorted(rs, key=lambda r: int(r["rank"]))
        if rs[0]["rank"] == "1" and rs[0]["confidence_band"] in USABLE_BANDS:
            out[ing] = tuple((int(r["fdc_id"]), r["confidence_band"], Fraction(r["score"])) for r in rs)
    return out


def read_categories(path: Path = MATCH_PATH) -> dict[str, tuple[str, str]]:
    """ING id -> (ing_category, sr_category of its rank-1 candidate) for the ING that ``read_candidates`` keeps."""
    out = {}
    for ing, rs in _read_match_rows(path).items():
        top = min(rs, key=lambda r: int(r["rank"]))
        if top["rank"] == "1" and top["confidence_band"] in USABLE_BANDS:
            out[ing] = (top.get("ing_category", ""), top.get("sr_category", ""))
    return out


def read_top1(path: Path = MATCH_PATH) -> dict[str, tuple[int, str]]:
    """ING id -> (fdc_id, band) of the usable rank-1 proposal."""
    return {ing: (c[0][0], c[0][1]) for ing, c in read_candidates(path).items()}


Basis = Mapping[tuple[int, str], tuple[str, int]]     # (fdc_id, nutrient key) -> (SR derivation code, data points)


def is_analytical(code: str | None, data_points: int | None) -> bool:
    """S178 R4: an SR value counts as analytical only with code A / AI / AR and at least one data point."""
    return code in ANALYTICAL_DERIVATION_CODES and (data_points or 0) >= 1


def _derivation_codes(sr_dir: Path) -> dict[str, str] | None:
    p = Path(sr_dir) / "food_nutrient_derivation.csv"
    if not p.exists():
        return None
    with p.open(newline="", encoding="utf-8") as fh:
        return {r["id"]: r["code"] for r in csv.DictReader(fh)}


def read_sr_records(sr_dir: Path, fdc_ids: Iterable[int], keys: Iterable[str]) -> dict[tuple[int, str], tuple[Fraction, str, int]]:
    """SR Legacy per-100 g value, derivation code and data-point count for the wanted foods and nutrient keys. A missing
    row is absent (UNKNOWN, not 0); a row with a blank derivation is ``NO_DERIVATION_CODE``; blank data points are 0."""
    from culinarystate.mechanism.sr_identity import NUTRIENT_IDS
    codes = _derivation_codes(sr_dir)
    wanted_f = set(fdc_ids)
    want: dict[int, list[tuple[str, int]]] = {}
    for key in set(keys):
        for rank, nid in enumerate(NUTRIENT_IDS[key][0]):
            want.setdefault(nid, []).append((key, rank))
    best: dict[tuple[int, str], tuple[int, Fraction, str, int]] = {}
    with (Path(sr_dir) / "food_nutrient.csv").open(newline="", encoding="utf-8") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        i_f, i_n, i_a = head.index("fdc_id"), head.index("nutrient_id"), head.index("amount")
        i_d = head.index("derivation_id") if "derivation_id" in head else None
        i_p = head.index("data_points") if "data_points" in head else None
        for row in rd:
            if not row[i_n].isdigit() or int(row[i_n]) not in want or not row[i_a]:
                continue
            f = int(row[i_f])
            if f not in wanted_f:
                continue
            d = row[i_d].strip() if i_d is not None else None
            if d is None or codes is None:
                code = NOT_RECORDED_CODE
            else:
                code = (codes.get(d, NOT_RECORDED_CODE) if d else NO_DERIVATION_CODE)
            n = int(row[i_p]) if i_p is not None and row[i_p].strip().isdigit() else 0
            for key, rank in want[int(row[i_n])]:
                cur = best.get((f, key))
                if cur is None or rank < cur[0]:
                    best[(f, key)] = (rank, Fraction(row[i_a].strip()), code, n)
    return {k: v[1:] for k, v in best.items()}


def read_sr_values(sr_dir: Path, fdc_ids: Iterable[int], keys: Iterable[str]) -> dict[tuple[int, str], Fraction]:
    """SR Legacy per-100 g values for the wanted foods and nutrient keys. A missing row is absent (UNKNOWN, not 0)."""
    return {k: v[0] for k, v in read_sr_records(sr_dir, fdc_ids, keys).items()}


def read_sr_basis(sr_dir: Path, fdc_ids: Iterable[int], keys: Iterable[str]) -> dict[tuple[int, str], tuple[str, int]]:
    """(SR derivation code, data points) of every value ``read_sr_values`` returns (S178 R4)."""
    return {k: (v[1], v[2]) for k, v in read_sr_records(sr_dir, fdc_ids, keys).items()}


def build_table_rows(cands: Candidates, values: Mapping[tuple[int, str], Fraction], keys: Iterable[str],
                     categories: Categories | None = None, basis: Basis | None = None) -> list[dict[str, str]]:
    """Rows of the derived content table: one per (candidate of an ING, rank 1-3, any band) x nutrient key. An SR food
    with no value for the nutrient gets an EMPTY amount (UNKNOWN, never 0). ``ing_category`` / ``sr_category`` carry the
    category pair used by the ABSENT crosswalk check (the SR group is the rank-1 candidate's, repeated on its rows).
    ``identity_source`` / ``registry_kind`` are filled by ``sr_identity.table_rows`` (blank here). S178 (R4):
    ``sr_derivation_code`` / ``sr_data_points`` carry the SR basis of the value (blank when no value or no basis given)."""
    from culinarystate.mechanism.sr_identity import NUTRIENT_UNITS
    cats = categories or {}
    bas = basis or {}
    rows = []
    for ing in sorted(cands):
        ing_cat, sr_cat = cats.get(ing, ("", ""))
        for rank, (fdc, band, score) in enumerate(cands[ing], 1):
            for key in sorted(set(keys)):
                v = values.get((fdc, key))
                b = bas.get((fdc, key)) if v is not None else None
                rows.append({"ing_id": ing, "candidate_rank": str(rank), "fdc_id": str(fdc), "confidence_band": band,
                             "match_score": _dec(score), "nutrient_key": key, "unit": NUTRIENT_UNITS[key],
                             "amount_per_100g": "" if v is None else _dec(v), "source_release": SR_RELEASE,
                             "ing_category": ing_cat, "sr_category": sr_cat, "identity_source": "", "registry_kind": "",
                             "sr_derivation_code": "" if b is None else b[0],
                             "sr_data_points": "" if b is None else str(b[1])})
    return rows


def _dec(v: Fraction) -> str:
    """Exact decimal text of an SR amount; refuses an amount that is not a terminating decimal."""
    from decimal import Decimal
    text = format((Decimal(v.numerator) / Decimal(v.denominator)).normalize(), "f")
    if Fraction(text) != v:
        raise GateError("an SR amount is not a terminating decimal")
    return text


def read_table_full(path: Path = TABLE_PATH) -> tuple[dict[str, tuple[tuple[int, str, Fraction], ...]],
                                                      dict[tuple[int, str], Fraction], dict[str, tuple[str, str]]]:
    """(candidates per ING, SR values by (fdc_id, nutrient key), (ING category, SR group) per ING). An empty amount stays
    absent (UNKNOWN). Rank-2/3 rows may be of any band; every ING needs a usable (HIGH / MEDIUM) rank-1 row."""
    rows: dict[str, dict[int, tuple[int, str, Fraction]]] = {}
    values: dict[tuple[int, str], Fraction] = {}
    cats: dict[str, tuple[str, str]] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            fdc = int(r["fdc_id"])
            rank = int(r["candidate_rank"])
            rows.setdefault(r["ing_id"], {})[rank] = (fdc, r["confidence_band"], Fraction(r["match_score"]))
            if rank == 1:
                cats[r["ing_id"]] = (r.get("ing_category", ""), r.get("sr_category", ""))
            if r["amount_per_100g"] != "":
                values[(fdc, r["nutrient_key"])] = Fraction(r["amount_per_100g"])
    cands = {ing: tuple(c[k] for k in sorted(c)) for ing, c in rows.items()}
    if any(1 not in rows[ing] for ing in rows):
        raise GateError("every ING in the content table needs its rank-1 row")
    if any(c[0][1] not in USABLE_BANDS for c in cands.values()):
        raise GateError("the content table holds ING with a usable (HIGH / MEDIUM) rank-1 candidate only")
    return cands, values, cats


def read_table_basis(path: Path = TABLE_PATH) -> dict[tuple[int, str], tuple[str, int]] | None:
    """(SR derivation code, data points) per (fdc_id, nutrient key) from the content table (S178 R4). A table without the
    basis columns gives None (the screen is then fail-closed for ABSENT)."""
    out: dict[tuple[int, str], tuple[str, int]] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        if "sr_derivation_code" not in (rd.fieldnames or ()):
            return None
        for r in rd:
            if r["amount_per_100g"] != "" and r.get("sr_derivation_code"):
                n = r.get("sr_data_points") or "0"
                out[(int(r["fdc_id"]), r["nutrient_key"])] = (r["sr_derivation_code"], int(n) if n.isdigit() else 0)
    return out


def read_table_meta(path: Path = TABLE_PATH) -> tuple[dict[str, str], set]:
    """(registry kind per ING, identity sources named in the table). An older table without the columns gives ({}, set())."""
    kinds: dict[str, str] = {}
    sources: set = set()
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("registry_kind"):
                kinds[r["ing_id"]] = r["registry_kind"]
            if r.get("identity_source"):
                sources.add(r["identity_source"])
    return kinds, sources


def read_table(path: Path = TABLE_PATH) -> tuple[dict[str, tuple[tuple[int, str, Fraction], ...]],
                                                 dict[tuple[int, str], Fraction]]:
    """(candidates per ING, SR values by (fdc_id, nutrient key)); see ``read_table_full`` for the categories too."""
    cands, values, _ = read_table_full(path)
    return cands, values


def code_key(svar_id: str) -> str:
    """Report key for an SVAR id (counts-only reports allow [A-Za-z0-9_] keys)."""
    return svar_id.replace("-", "__")


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- presence screen
class TargetPresenceScreen:
    """Member and lot presence of a target nutrient, from SR Legacy composition with its basis recorded (S178 R4: SR
    values may be analytical, imputed or assumed; only analytical ones can support ABSENT)."""

    def __init__(self, floors: Mapping[str, Floor], cands: Candidates,
                 values: Mapping[tuple[int, str], Fraction], categories: Categories | None = None,
                 kinds: Mapping[str, str] | None = None, basis: Basis | None = None) -> None:
        self.floors, self.cands, self.values = dict(floors), dict(cands), dict(values)
        self.categories = dict(categories or {})     # no category info = no ABSENT claim can be confirmed
        self.kinds = dict(kinds or {})               # ING -> registry kind (DIRECT, DEFAULT_FORM, ..., LEGACY_FALLBACK)
        # S178 R4: (fdc, key) -> (SR derivation code, data points). None = no basis known: ABSENT is never confirmed.
        self.basis = None if basis is None else dict(basis)
        self._verdicts: dict[tuple[str, str | None], tuple[str, str]] = {}

    def analytical(self, fdc: int, key: str) -> bool:
        b = (self.basis or {}).get((fdc, key))
        return b is not None and is_analytical(*b)

    def member_basis(self, svar_id: str, ing_id: str | None) -> list[dict[str, Any]]:
        """SR basis of every plausible candidate (any band) of one ING: fdc id, band, value, derivation code, data points,
        analytical flag (S178 R4: kept in the gate's output). Codes and SR numbers only."""
        if not ing_id or svar_id not in self.floors:
            return []
        key = self.floors[svar_id].nutrient_key
        out = []
        for f, band in self.plausible_all(svar_id, ing_id):
            v = self.values.get((f, key))
            b = (self.basis or {}).get((f, key)) if v is not None else None
            out.append({"fdc_id": f, "band": band, "value": None if v is None else _dec(v),
                        "sr_derivation_code": None if b is None else b[0], "sr_data_points": None if b is None else b[1],
                        "analytical": bool(b is not None and is_analytical(*b))})
        return out

    def screened(self, svar_id: str | None) -> bool:
        return svar_id in self.floors

    def plausible_all(self, svar_id: str, ing_id: str | None) -> tuple[tuple[int, str], ...]:
        """(SR food, band) the ING may be, ANY band: rank 1 and every rank 2-3 candidate within the identity margin of
        its score. This is the set the ABSENT claim must hold for (S177)."""
        cs = self.cands.get(ing_id) if ing_id else None
        if not cs:
            return ()
        return tuple((f, band) for f, band, sc in cs if sc >= cs[0][2] - self.floors[svar_id].margin)

    def plausible(self, svar_id: str, ing_id: str | None) -> tuple[int, ...]:
        """The HIGH / MEDIUM subset of ``plausible_all`` (the identities PRESENT must hold for)."""
        return tuple(f for f, band in self.plausible_all(svar_id, ing_id) if band in USABLE_BANDS)

    def category_ok(self, ing_id: str | None) -> bool:
        """The ING category is confirmed against the SR food group of its rank-1 candidate (``CATEGORY_CROSSWALK``)."""
        ing_cat, sr_cat = self.categories.get(ing_id, ("", "")) if ing_id else ("", "")
        return category_matches(ing_cat, sr_cat)

    def member_verdict(self, svar_id: str, ing_id: str | None) -> tuple[str, str]:
        """(state, blocker) of one ING taken alone. ``blocker`` says why a non-ABSENT, non-PRESENT member is UNKNOWN, in the
        order the ABSENT conditions are tested; the category check is LAST, so CATEGORY_EMPTY / CATEGORY_MISMATCH mean every
        other condition held (the member would be ABSENT if its category were confirmed). S178 R4: the analytical-basis
        check (``SR_ZERO_NOT_ANALYTICAL`` / ``SR_BASIS_NOT_RECORDED``) comes just before the category check."""
        k = (svar_id, ing_id)
        got = self._verdicts.get(k)
        if got is None:
            got = self._verdicts[k] = self._member_verdict(svar_id, ing_id)
        return got

    def _member_verdict(self, svar_id: str, ing_id: str | None) -> tuple[str, str]:
        fl = self.floors[svar_id]
        cs = self.cands.get(ing_id) if ing_id else None
        if not cs or cs[0][1] not in USABLE_BANDS:
            return UNKNOWN, "NO_USABLE_IDENTITY"    # no usable (HIGH / MEDIUM) rank-1 SR identity
        usable = [self.values.get((f, fl.nutrient_key)) for f in self.plausible(svar_id, ing_id)]
        if usable and all(v is not None and v >= fl.value for v in usable):
            return PRESENT, ""
        # ABSENT is a negative claim; all three conditions of S177 (FINAL-SCI #6) or it stays UNKNOWN
        if cs[0][1] != ABSENT_RANK1_BAND:
            return UNKNOWN, "RANK1_NOT_HIGH"        # MEDIUM identities (~67 % plausible) support no negative claim
        vals = [self.values.get((f, fl.nutrient_key)) for f, _ in self.plausible_all(svar_id, ing_id)]
        if any(v is None for v in vals):
            return UNKNOWN, "SR_VALUE_MISSING"      # SR has no value for a plausible identity: UNKNOWN is never 0
        if not all(v < fl.value for v in vals):
            return UNKNOWN, "IDENTITIES_DISAGREE"   # a plausible identity (any band) holds the nutrient: ambiguous
        if self.basis is None:
            return UNKNOWN, B_BASIS_NOT_RECORDED    # S178 R4: no derivation basis known -> no negative claim
        if not all(self.analytical(f, fl.nutrient_key) for f, _ in self.plausible_all(svar_id, ing_id)):
            return UNKNOWN, B_NOT_ANALYTICAL        # S178 R4: an assumed / imputed / undocumented zero is not a measurement
        if not self.category_ok(ing_id):
            ing_cat = (self.categories.get(ing_id) or ("", ""))[0]
            return UNKNOWN, "CATEGORY_MISMATCH" if ing_cat else "CATEGORY_EMPTY"
        return ABSENT, ""

    def member_state(self, svar_id: str, ing_id: str | None) -> str:
        return self.member_verdict(svar_id, ing_id)[0]

    def lot_state(self, svar_id: str | None, ings: Iterable[str], n_unknown: int = 0) -> str:
        if not self.screened(svar_id):
            return NOT_SCREENED
        states = [self.member_state(svar_id, i) for i in sorted(set(ings))]
        if PRESENT in states:
            return PRESENT
        if states and n_unknown == 0 and all(s == ABSENT for s in states):
            return ABSENT
        return UNKNOWN

    def _replace(self, svar_id: str, **kw) -> "TargetPresenceScreen":
        fl = self.floors[svar_id]
        new = Floor(fl.svar_id, fl.name, fl.nutrient_key, fl.unit, kw.get("value", fl.value), fl.status,
                    kw.get("margin", fl.margin))
        return TargetPresenceScreen({**self.floors, svar_id: new}, self.cands, self.values, self.categories, self.kinds,
                                    self.basis)

    def with_floor(self, svar_id: str, value: Fraction | str | float) -> "TargetPresenceScreen":
        """Same screen with another floor for one target (sensitivity analysis only)."""
        return self._replace(svar_id, value=Fraction(str(value)))

    def with_margin(self, svar_id: str, margin: Fraction | str | float) -> "TargetPresenceScreen":
        """Same screen with another identity margin for one target (sensitivity analysis only)."""
        return self._replace(svar_id, margin=Fraction(str(margin)))


@functools.lru_cache(maxsize=4)
def _screen(floor_path: str, source: str, table_path: str, match_path: str, sr_dir: str) -> TargetPresenceScreen:
    floors = read_floors(Path(floor_path))
    if source == "table":
        cands, values, cats = read_table_full(Path(table_path))
        kinds = read_table_meta(Path(table_path))[0]
        basis = read_table_basis(Path(table_path))
    else:
        from culinarystate.mechanism import sr_identity as SI
        idn = SI.build_identity(sr_dir=Path(sr_dir), match_path=Path(match_path))
        cands, cats, kinds = idn.cands, idn.categories, idn.kinds
        recs = read_sr_records(Path(sr_dir), {f for c in cands.values() for f, _, _ in c},
                               {f.nutrient_key for f in floors.values()})
        values, basis = {k: v[0] for k, v in recs.items()}, {k: (v[1], v[2]) for k, v in recs.items()}
    return TargetPresenceScreen(floors, cands, values, cats, kinds, basis)


# ----------------------------------------------------------------------------- human-review lists (S177)
REVIEW_COLUMNS = ("rank", "ing_id", "ing_canonical_name", "ing_category", "registry_kind", "rank1_fdc_id",
                  "rank1_sr_description", "rank1_sr_food_group", "rank1_band", "rank1_match_score",
                  "plausible_candidates_any_band", "rank1_sr_value_mg_per_100g",
                  "max_sr_value_among_plausible_mg_per_100g", "plausible_sr_derivation_codes", "plausible_sr_data_points",
                  "all_plausible_analytical", "floor_mg_per_100g", "member_verdict", "blocker", "items",
                  "status", "human_verdict", "human_note")


def basis_summary(basis_rows: Sequence[Mapping[str, Any]]) -> tuple[str, str, str]:
    """('A|NONE|Z', '3|0|0', 'YES' / 'NO' / '') for the plausible candidates' SR basis (``member_basis``), in rank order;
    a value SR does not have is ``MISSING``. 'YES' only when every candidate is analytical."""
    if not basis_rows:
        return "", "", ""
    codes = "|".join("MISSING" if b["value"] is None else (b["sr_derivation_code"] or "NOT_RECORDED") for b in basis_rows)
    pts = "|".join("" if b["sr_data_points"] is None else str(b["sr_data_points"]) for b in basis_rows)
    return codes, pts, "YES" if all(b["analytical"] for b in basis_rows) else "NO"


def review_rows(screen: TargetPresenceScreen, svar_id: str, counts: Mapping[str, int], *,
                names: Mapping[str, str] | None = None, descriptions: Mapping[int, str] | None = None,
                top: int = 50) -> list[dict[str, str]]:
    """The ``top`` ING by item count, for a human to check (counts only: registry names, SR descriptions, SR values; no
    recipe text). ``counts`` maps a report key (``ING__000123``) to its item count; ``names`` (ING id -> canonical name,
    from the ING ledger) and ``descriptions`` (fdc id -> SR description) are optional and left blank when missing.
    Ties break on the ING id."""
    fl = screen.floors[svar_id]
    names, descriptions = names or {}, descriptions or {}
    rows = []
    ranked = sorted(((n, k.replace("__", "-", 1)) for k, n in counts.items()), key=lambda t: (-t[0], t[1]))
    for rank, (n, ing) in enumerate(ranked[:top], 1):
        cs = screen.cands.get(ing, ())
        ing_cat, sr_group = screen.categories.get(ing, ("", ""))
        plaus = screen.plausible_all(svar_id, ing)
        vals = [screen.values.get((f, fl.nutrient_key)) for f, _ in plaus]
        top_v = screen.values.get((cs[0][0], fl.nutrient_key)) if cs else None
        known = [v for v in vals if v is not None]
        state, blocker = screen.member_verdict(svar_id, ing)
        codes, pts, anal = basis_summary(screen.member_basis(svar_id, ing))
        rows.append({"rank": str(rank), "ing_id": ing, "ing_canonical_name": names.get(ing, ""), "ing_category": ing_cat,
                     "registry_kind": screen.kinds.get(ing, ""), "rank1_fdc_id": str(cs[0][0]) if cs else "",
                     "rank1_sr_description": descriptions.get(cs[0][0], "") if cs else "", "rank1_sr_food_group": sr_group,
                     "rank1_band": cs[0][1] if cs else "", "rank1_match_score": _dec(cs[0][2]) if cs else "",
                     "plausible_candidates_any_band": str(len(plaus)),
                     "rank1_sr_value_mg_per_100g": "" if top_v is None else _dec(top_v),
                     "max_sr_value_among_plausible_mg_per_100g": "" if not known else _dec(max(known)),
                     "plausible_sr_derivation_codes": codes, "plausible_sr_data_points": pts,
                     "all_plausible_analytical": anal,
                     "floor_mg_per_100g": _dec(fl.value), "member_verdict": state, "blocker": blocker, "items": str(n),
                     "status": "AI_DRAFTED_FOR_HUMAN_REVIEW", "human_verdict": "", "human_note": ""})
    return rows


# ----------------------------------------------------------------------------- lot membership from the event graph
@dataclass(frozen=True)
class LotMembers:
    """Members of one lot: distinct linked ING ids, the number of roots of unknown identity, the prior-process kinds
    (``PRIOR_KINDS``) found on the lot or any of its ancestors, and where they came from (``prior_basis``: S177 heat /
    leach events; S178 also freeze / defrost events, unresolved events, states stated on the food and ingredient lines)."""

    ings: frozenset
    unknown: int = 0
    prior: frozenset = frozenset()
    prior_basis: frozenset = frozenset()

    @property
    def sole(self) -> str | None:
        return next(iter(self.ings)) if len(self.ings) == 1 and self.unknown == 0 else None

    @property
    def prior_process(self) -> bool:
        return bool(self.prior)


def _attr(claims, name: str):
    return next((c.value for c in claims if c.field == name), None)


@functools.lru_cache(maxsize=1)
def _default_hierarchy():
    from culinarystate.mechanism import process_signatures as PS
    return PS.read_process_hierarchy()


def prior_kind(proc_id: str | None, hierarchy=None) -> str | None:
    """``HEAT`` / ``LEACH`` / ``PRESERVED`` (S178: freeze, defrost) when an event of this process changes the food away
    from its raw form (see the ``PRIOR_*`` constants), else None (an unresolved process is None here; the gate uses the
    fail-closed ``event_prior_kind``)."""
    if not proc_id:
        return None
    if proc_id in PRIOR_HEAT_PROCS:
        return "HEAT"
    if proc_id in PRIOR_LEACH_PROCS:
        return "LEACH"
    if proc_id in PRIOR_PRESERVED_PROCS:
        return "PRESERVED"
    h = hierarchy or _default_hierarchy()
    if not h.contains(proc_id):
        return None
    fams = {a[4:] for a in h.ancestors(proc_id) if a.startswith("FAM:")}
    if fams & PRIOR_HEAT_FAMILIES:
        return "HEAT"
    if fams & PRIOR_LEACH_FAMILIES:
        return "LEACH"
    return None


def event_prior_kind(proc_id: str | None, hierarchy=None) -> str | None:
    """S178 R5 (fail-closed): ``prior_kind``, except that an event with no process id, or with one the PROC hierarchy does
    not hold, is ``UNRESOLVED`` (unknown context, never "no prior process")."""
    if not proc_id:
        return "UNRESOLVED"
    k = prior_kind(proc_id, hierarchy)
    if k:
        return k
    h = hierarchy or _default_hierarchy()
    return None if h.contains(proc_id) else "UNRESOLVED"


# ----------------------------------------------------------------------------- what the text states (S178 R2 / R3)
SERVE_CUE = re.compile(
    r"\b(?:serve[ds]?|serving|garnish(?:ed|es)?|top(?:ped|s)?|accompan(?:y|ied|ies))\b"
    r"(?:[ \t]+(?:it|them|this|each|everything|immediately|hot|warm|cold|chilled|at[ \t]+once|right[ \t]+away))*"
    r"[ \t]+(?:with|over|on|alongside|atop|beside|by)\b", re.IGNORECASE)
PREPOSITIONS = frozenset({"with", "over", "on", "onto", "alongside", "atop", "beside", "of", "for", "like", "plus"})
ED_BASE_FORMS = frozenset({"shred", "seed", "deseed", "feed", "bleed", "speed", "need", "embed", "weed", "wed", "bed",
                           "shed", "sled", "breed", "heed", "proceed", "exceed", "succeed", "red", "bred", "reseed"})
IRREGULAR_PARTICIPLES = frozenset({"frozen", "beaten", "broken", "ground", "shaken", "risen", "hidden", "sown", "torn",
                                   "chosen", "spun", "stricken"})
ADJECTIVAL_BASE = frozenset({"roast"})        # base form used as an adjective ("roast beef"); needs a non-clause context
_CLAUSE_BREAK = re.compile(r"(?:[,;:(]|\b(?:and|or|then|now|first|next|finally)\b)[ \t]*$", re.IGNORECASE)
_WORD = re.compile(r"[A-Za-zÀ-ÿ']+")
REFERRING_WORDS = frozenset({"it", "them", "everything"})
EVENT_ROLE_RULES_STATUS = "AI_DRAFTED_UNSIGNED"


def is_participle(surface: str) -> bool:
    """Past-participle form of an ACTION surface (last word): regular -ed (not a base form such as "shred" / "seed") or
    an irregular participle ("frozen", "beaten")."""
    words = re.split(r"[\s\-]+", (surface or "").lower().strip())
    w = words[-1] if words else ""
    if w in IRREGULAR_PARTICIPLES:
        return True
    return len(w) >= 5 and w.endswith("ed") and w not in ED_BASE_FORMS


def _prev_word(prefix: str) -> str | None:
    ws = _WORD.findall(prefix)
    return ws[-1].lower() if ws else None


def is_attributive(surface: str, prefix: str) -> bool:
    """An ACTION that directly precedes its food is attributive (a state of the food, not an event) when it is a
    participle ("add mashed potatoes", "fresh and canned peaches"), when a preposition comes right before it ("serve with
    roast beef"), or when it is an adjectival base form ("roast") that does not open a clause. ``prefix`` is the sentence
    text before the ACTION; the caller checks the "directly followed by a food mention" condition."""
    w = (re.split(r"[\s\-]+", (surface or "").lower().strip()) or [""])[-1]
    if is_participle(surface):
        return True
    pw = _prev_word(prefix)
    if pw in PREPOSITIONS:
        return True
    return w in ADJECTIVAL_BASE and pw is not None and not _CLAUSE_BREAK.search(prefix)


@dataclass(frozen=True)
class TextContext:
    """What one recipe text states around its mentions (codes and spans only). Spans are (char_start, char_end)."""

    roles: Mapping[tuple[int, int], str]                       # ACTION span -> PROCESS_STEP | ATTRIBUTIVE_STATE | SERVING_SUGGESTION
    action_kinds: Mapping[tuple[int, int], frozenset]          # ACTION span -> state-word kinds of its own surface
    windows: Mapping[tuple[int, int], tuple[int, int]]         # ACTION span -> argument window
    food_states: Mapping[tuple[int, int], frozenset]           # FOOD_MENTION span -> stated prior kinds
    food_ing: Mapping[tuple[int, int], str]                    # FOOD_MENTION span -> uniquely linked ING id

    def role(self, span: tuple[int, int] | None) -> str:
        return self.roles.get(span, PROCESS_STEP) if span else PROCESS_STEP

    def window_states(self, span: tuple[int, int] | None, ing: str | None) -> frozenset:
        """Stated kinds of the food mentions inside the event's argument window that link to ``ing`` (a food named
        again with a state word, e.g. "Fry the baked potatoes", whatever lot coreference chose)."""
        w = self.windows.get(span) if span else None
        if not w or not ing:
            return frozenset()
        out: set = set()
        for fs, kinds in self.food_states.items():
            if w[0] <= fs[0] < w[1] and self.food_ing.get(fs) == ing:
                out |= kinds
        return frozenset(out)


def _span(m) -> tuple[int, int]:
    return (m.span.char_start, m.span.char_end)


def text_context(raw: str, mentions: Iterable, links: Iterable = ()) -> TextContext:
    """Build the S178 R2 / R3 text context from Rung A's mentions and links (Rung A itself is not changed)."""
    from culinarystate.extraction.rung_a import sentences
    ms = sorted(mentions, key=lambda m: (m.span.char_start, -m.span.char_end))
    link_by = {lr.mention_id: lr.selected_id for lr in links if getattr(lr, "selected_id", None)}
    roles: dict = {}
    akinds: dict = {}
    windows: dict = {}
    fstates: dict = {}
    fing: dict = {}
    for ss, se in sentences(raw):
        sm = [m for m in ms if ss <= m.span.char_start < se]
        acts = [m for m in sm if m.label == "ACTION"]
        for k, a in enumerate(acts):
            windows[_span(a)] = (a.span.char_end, acts[k + 1].span.char_start if k + 1 < len(acts) else se)
        cue = SERVE_CUE.search(raw, ss, se)
        in_scope = cue is not None
        for a in acts:
            nxt = next((m for m in sm if m.span.char_start >= a.span.char_end), None)
            direct_food = (nxt is not None and nxt.label == "FOOD_MENTION"
                           and nxt.span.surface.lower() not in REFERRING_WORDS
                           and raw[a.span.char_end:nxt.span.char_start].strip(" \t") == ""
                           and nxt.span.char_start > a.span.char_end)
            prefix = raw[ss:a.span.char_start]
            role = PROCESS_STEP
            if direct_food and is_attributive(a.span.surface, prefix):
                role = ATTRIBUTIVE_STATE
            elif in_scope and a.span.char_start >= cue.end():
                if direct_food or _prev_word(prefix) in PREPOSITIONS:
                    role = SERVING_SUGGESTION
                else:
                    in_scope = False                  # a new verb phrase ("... and bake for 10 minutes") ends the clause
            if role != PROCESS_STEP:
                roles[_span(a)] = role
                ks = frozenset(k for _, _, k in state_cues(a.span.surface))
                if ks:
                    akinds[_span(a)] = ks
        for i, m in enumerate(sm):
            if m.label != "FOOD_MENTION" or m.span.surface.lower() in REFERRING_WORDS:
                continue
            if m.mention_id in link_by:
                fing[_span(m)] = link_by[m.mention_id]
            start, j = ss, i - 1
            while j >= 0:
                p = sm[j]
                # the noun phrase in front of the food: quantities ("1 can"), state words Rung A tagged as foods
                # ("dried") and attributive ACTIONs ("1 can chopped tomatoes") belong to it
                if p.label == "QUANTITY_IN_STEP" or (p.label == "FOOD_MENTION" and STATE_WORD_RE.fullmatch(p.span.surface.strip())) \
                        or (p.label == "ACTION" and roles.get(_span(p)) == ATTRIBUTIVE_STATE):
                    j -= 1
                    continue
                start = p.span.char_end
                break
            ks = set()
            if start < m.span.char_start:
                ks |= {k for _, _, k in state_cues(raw[start:m.span.char_start])}
            if (post := post_state_cue(raw[m.span.char_end:se])) is not None:
                ks.add(post)
            if ks:
                fstates[_span(m)] = frozenset(ks)
    return TextContext(roles, akinds, windows, fstates, fing)


def lot_members(graph, hierarchy=None, *, text: TextContext | None = None,
                ingredient_states: Mapping[str, Iterable[str]] | None = None) -> dict[str, LotMembers]:
    """Entity id -> members (lineage through parents) and prior-process kinds. A root without a linked ingredient is a
    member of unknown identity (e.g. a named mixture that no earlier step produces). An entity listed in the
    ``produces`` of a heat / leach / freeze event carries that kind, and every descendant inherits it (replay-graph
    ancestry). S178: an event with an unresolved process gives ``UNRESOLVED`` (R5); with ``text`` a root lot opened by a
    food mention with a stated state, and the products of an attributive / serving event with a state word, carry the
    stated kind (R2 / R3); ``ingredient_states`` (ING -> kinds from the ingredient lines) marks every root of that ING."""
    ents = {e.entity_id: e for e in graph.entities}
    made_by: dict[str, dict[str, set]] = {}
    for ev in getattr(graph, "events", ()):
        add: dict[str, str] = {}
        k = event_prior_kind(_attr(ev.attributes, "proc_id"), hierarchy)
        if k:
            add[k] = PB_UNRESOLVED if k == "UNRESOLVED" else PB_EVENT
        span = (ev.span.char_start, ev.span.char_end) if getattr(ev, "span", None) is not None else None
        if text is not None and text.role(span) != PROCESS_STEP:
            for kk in text.action_kinds.get(span, ()):
                add.setdefault(kk, PB_TEXT)
        for eid in ev.produces:
            for kk, b in add.items():
                made_by.setdefault(eid, {}).setdefault(kk, set()).add(b)
    stated_root: dict[str, frozenset] = {}
    if text is not None:
        for e in graph.entities:
            if e.span is not None and not e.parent_entity_ids:
                ks = text.food_states.get((e.span.char_start, e.span.char_end))
                if ks:
                    stated_root[e.entity_id] = ks
    line_states = {i: frozenset(v) for i, v in (ingredient_states or {}).items()}
    memo: dict[str, LotMembers] = {}

    def walk(eid: str, depth: int = 0) -> LotMembers:
        if eid in memo:
            return memo[eid]
        e = ents.get(eid)
        if e is None or depth > 500:
            return LotMembers(frozenset(), 1)
        own = _attr(e.attributes, "ingredient_id")
        ings = {own} if own else set()
        unknown = 0
        kinds: set = set()
        bases: set = set()
        for kk, bs in made_by.get(eid, {}).items():
            kinds.add(kk)
            bases |= bs
        if eid in stated_root:
            kinds |= stated_root[eid]
            bases.add(PB_TEXT)
        if own and own in line_states:
            kinds |= line_states[own]
            bases.add(PB_LINE)
        for p in e.parent_entity_ids:
            m = walk(p, depth + 1)
            ings |= m.ings
            unknown += m.unknown
            kinds |= m.prior
            bases |= m.prior_basis
        if not e.parent_entity_ids and not own:
            unknown += 1
        memo[eid] = LotMembers(frozenset(ings), unknown, frozenset(kinds), frozenset(bases))
        return memo[eid]

    return {eid: walk(eid) for eid in ents}


def lots_of(members: Mapping[str, LotMembers], consumed: Iterable[str], ing: str | None) -> list[LotMembers]:
    """The consumed lots the item (event, ing) belongs to: those holding ``ing`` (ing None: those with no linked ING)."""
    out = []
    for eid in dict.fromkeys(consumed):
        m = members.get(eid)
        if m is None:
            continue
        if (ing is not None and ing in m.ings) or (ing is None and not m.ings):
            out.append(m)
    return out


# ----------------------------------------------------------------------------- gate decision
@dataclass(frozen=True)
class GateResult:
    presence: str                       # PRESENT | ABSENT | UNKNOWN | NOT_SCREENED
    lot_context: str                    # SINGLE_MEMBER | MERGED | NO_LOT (no linked ingredient / consumed lot)
    reasons: tuple[str, ...]            # gate reason codes, in precedence order
    final_precheck: str                 # the pre-check handed to G0 (NONE when withheld)
    not_applicable: bool
    withheld: bool                      # evidence rows exist but the gates do not let them stand
    prior_kinds: tuple[str, ...] = ()   # prior-process kinds found for the consumed lot(s) (incl. UNRESOLVED)
    event_role: str = PROCESS_STEP      # S178 R3
    prior_basis: tuple[str, ...] = ()   # S178: EVENT / EVENT_UNRESOLVED / TEXT_STATED_STATE / INGREDIENT_LINE
    presupposed: bool = False           # S178 R6: every hit presupposes a prior cook and the only prior kind is HEAT

    def as_item(self) -> dict[str, Any]:
        return {"presence": self.presence, "lot_context": self.lot_context}


_EVIDENCE_STATUSES = ("MEASURED", "CENSORED")


class EvidenceGates:
    def __init__(self, screen: TargetPresenceScreen, *, presence: bool = True, context: bool = True,
                 provenance: Mapping[str, Any] | None = None, exempt_presupposed: bool = False) -> None:
        self.screen, self.presence_on, self.context_on = screen, presence, context
        self.exempt_presupposed = bool(exempt_presupposed)     # S178 R6: a HUMAN decision (SCI-B Q1); OFF by default
        self.provenance = dict(provenance or {})

    @classmethod
    def load(cls, *, floor_path: Path = FLOOR_PATH, source: str = "table", table_path: Path = TABLE_PATH,
             match_path: Path = MATCH_PATH, sr_dir: Path | None = None, presence: bool = True,
             context: bool = True) -> "EvidenceGates":
        """``source="table"`` (default, the shipped derived table) or ``"sr"`` (SR Legacy read directly)."""
        if source not in ("table", "sr"):
            raise GateError("source is 'table' or 'sr'")
        sr = ""
        if source == "sr":
            from culinarystate.mechanism.sr_identity import default_dir
            sr = str(Path(sr_dir) if sr_dir else default_dir(ROOT))
        screen = _screen(str(floor_path), source, str(table_path), str(match_path), sr)
        from culinarystate.mechanism import sr_identity as SI
        id_src = ", ".join(sorted(read_table_meta(Path(table_path))[1])) if source == "table" else SI.IDENTITY_SOURCE
        words = "\n".join(f"{w}={k}" for w, k in sorted(STATE_WORDS.items()))
        prov = {"version": VERSION, "status": STATUS, "floor_file_sha256": _sha(floor_path), "content_source": source,
                "content_table_sha256": _sha(table_path) if source == "table" else "NOT_USED",
                "match_registry_sha256": _sha(match_path), "sr_source": SR_RELEASE,
                "identity_source": id_src or "LEGACY_TABLE_NO_IDENTITY_COLUMNS",
                "identity_registry_sha256": _sha(SI.REGISTRY_PATH) if SI.REGISTRY_PATH.exists() else "MISSING",
                "identity_kinds": dict(sorted(Counter(screen.kinds.values()).items())),
                "absent_rule": "RANK1_HIGH_AND_ALL_PLAUSIBLE_ANY_BAND_KNOWN_BELOW_FLOOR_AND_ANALYTICAL_AND_CATEGORY_CONFIRMED",
                "analytical_derivation_codes": sorted(ANALYTICAL_DERIVATION_CODES), "analytical_min_data_points": 1,
                "basis_status": BASIS_STATUS if screen.basis is not None else "BASIS_NOT_RECORDED_FAIL_CLOSED",
                "category_crosswalk_status": CATEGORY_CROSSWALK_STATUS,
                "prior_process_kinds": list(PRIOR_KINDS),
                "state_words_status": STATE_WORDS_STATUS,
                "state_words_sha256": hashlib.sha256(words.encode("utf-8")).hexdigest(),
                "event_role_rules_status": EVENT_ROLE_RULES_STATUS,
                "presupposed_prior_heat_exemption": "OFF_PENDING_HUMAN_DECISION_SCI_B_Q1",
                "floors": {code_key(k): {"value": float(f.value), "identity_score_margin": float(f.margin), "unit": f.unit,
                                         "status": f.status}
                           for k, f in screen.floors.items()}}
        return cls(screen, presence=presence, context=context, provenance=prov)

    def describe(self) -> dict[str, Any]:
        return {**self.provenance, "enabled": True, "presence_gate": self.presence_on, "context_gate": self.context_on,
                "presupposed_prior_heat_exemption_applied": self.exempt_presupposed}

    def member_presence(self, svar_id: str | None, ing: str | None) -> str | None:
        """Presence state of one ING taken alone (None when the presence gate is off or nothing is linked)."""
        if not self.presence_on or not ing or not self.screen.screened(svar_id):
            return None
        return self.screen.member_state(svar_id, ing)

    def member_blocker(self, svar_id: str | None, ing: str | None) -> str | None:
        """Why an UNKNOWN member is not ABSENT (``TargetPresenceScreen.member_verdict``); None when not applicable."""
        if not self.presence_on or not ing or not self.screen.screened(svar_id):
            return None
        return self.screen.member_verdict(svar_id, ing)[1] or None

    def member_basis(self, svar_id: str | None, ing: str | None) -> list[dict[str, Any]]:
        """SR basis (derivation code, data points) of the member's plausible candidates (S178 R4); [] when not screened."""
        if not self.presence_on or not ing or not self.screen.screened(svar_id):
            return []
        return self.screen.member_basis(svar_id, ing)

    def evaluate(self, *, svar_id: str, ing: str | None, raw_precheck: str, lots: Sequence[LotMembers],
                 event_role: str = PROCESS_STEP, stated: Iterable[str] = (),
                 hits: Sequence[Mapping[str, Any]] = ()) -> GateResult:
        """The gate decision for one item. ``event_role`` (S178 R3) and ``stated`` (S178 R2: kinds stated on the food
        mention inside this event's own window) only ever narrow; ``hits`` are the EVD rows of the raw pre-check."""
        ings = {i for lm in lots for i in lm.ings}
        unknown = sum(lm.unknown for lm in lots)
        presence = self.screen.lot_state(svar_id, ings, unknown) if self.presence_on else NOT_SCREENED
        if ing is None or not lots:
            context = NO_LOT
        else:
            context = SINGLE_MEMBER if all(lm.sole == ing for lm in lots) else MERGED
        stated = frozenset(stated)
        prior = set(stated).union(*(lm.prior for lm in lots))
        bases = ({PB_TEXT} if stated else set()).union(*(lm.prior_basis for lm in lots))
        kinds = tuple(k for k in PRIOR_KINDS if k in prior)
        pbasis = tuple(sorted(bases)) if kinds else ()
        has_raw = raw_precheck != "NONE"
        if event_role != PROCESS_STEP:                 # S178 R3: not a performed process -> never DIRECT, no claim
            reasons = (ROLE_REASON[event_role],) + ((R_PRESENCE_UNKNOWN,) if presence == UNKNOWN else ())
            return GateResult(presence, context, reasons, "NONE", False, has_raw, kinds, event_role, pbasis)
        if presence == ABSENT:
            return GateResult(presence, context, (R_TARGET_ABSENT,), "NONE", True, has_raw, kinds, event_role, pbasis)
        reasons: list[str] = []
        if presence == UNKNOWN:
            reasons.append(R_PRESENCE_UNKNOWN)
        final, withheld, presupposed = raw_precheck, False, False
        if self.context_on and has_raw:
            if context == NO_LOT:
                reasons.insert(0, R_LOT_UNKNOWN)          # S178 R5(b): no lot context -> no raw DIRECT
                final, withheld = "NONE", True
            elif context == MERGED:
                reasons.insert(0, R_MERGED)
                final, withheld = "NONE", True
            elif kinds:
                ev_rows = [h for h in hits if h.get("status") in _EVIDENCE_STATUSES]
                presupposed = (kinds == ("HEAT",) and bool(ev_rows)
                               and all(h.get("presupposes_prior_heat") for h in ev_rows))
                if not (presupposed and self.exempt_presupposed):
                    if "UNRESOLVED" in kinds:
                        reasons.insert(0, R_PRIOR_UNRESOLVED)    # S178 R5(a)
                    if any(k != "UNRESOLVED" for k in kinds):
                        reasons.insert(0, R_PRIOR_PROCESS)       # S177 #7 + S178 R2 / R6
                    final, withheld = "NONE", True
        return GateResult(presence, context, tuple(reasons), final, False, withheld, kinds, event_role, pbasis,
                          presupposed)
