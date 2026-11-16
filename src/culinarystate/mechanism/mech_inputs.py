"""Inputs and K3 evaluators of the mechanism screen (S178 lane MECH, T5-C02-R2). AI_DRAFTED, NON_CITABLE.

Three kinds of input, read-only:

1. **Members** of a lot (ING ids from the Rung A event graph). Identity of record = ``mechanism.sr_identity`` (the Mac's
   curated ``registry/ing_sr_defaults_v1.csv`` through ``composition.ing_sr_match``); SR values = the composition layer's
   loader ``composition.sr_legacy.load_sr`` (USDA SR Legacy 2018-04, measured, public domain). Presence of a nutrient uses
   the router's ``evidence_gates.TargetPresenceScreen`` semantics unchanged (PRESENT: every HIGH / MEDIUM plausible identity
   holds it; ABSENT is a negative claim needing a HIGH rank-1 identity, every plausible identity of any band KNOWN and below
   the floor, the ING category confirmed against the SR food group and, since S178 FIX-ROUTER R4, every such zero ANALYTICAL
   (SR derivation A / AI / AR with >= 1 data point; an assumed or imputed zero is UNKNOWN); anything else UNKNOWN, never 0;
   a lot is ABSENT only
   if every member is and no member is of unknown identity). The floor here is the PROPOSED screening convention
   ``SR value > 0`` (``ZERO_FLOOR``): a reaction can act on any non-zero amount, so the router's 1 mg vitamin C routing floor
   would turn trace presence into a false NOT_POSSIBLE. Taxon classes (Allium, Brassicaceae, PPO-browning foods, green
   tissue, ascorbate-oxidase foods, animal connective tissue) are read from the SR description / food group of the identity
   of record and need a raw form (an enzyme in a cooked, dried or canned identity is not assumed active); they can make a
   reactant PRESENT, never ABSENT (no SR nutrient measures alliin, glucosinolates, PPO, chlorophyll or collagen).
2. **Event inputs**: Layer 1 TEXT_STATED axes (heat binder or non-heat binder record) and, for the L2 views, the Layer 2
   SCENARIO bracket record of the same event.
3. **Lineage** of each member (graph ancestry): was it heated (``evidence_gates.prior_kind`` HEAT) or cut / crushed / blended
   (MECHANICAL_CUT family or a disruptive mix / squeeze) by an EARLIER event.

Every evaluator returns a ``mech_k3.Conjunct``; a missing input is UNKNOWN with a reason code, never FALSE. Only the
evaluators marked *may exclude* below can return FALSE, and only from measured SR zeros (``REFERENCE_SR``).
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from culinarystate.mechanism import evidence_gates as EG
from culinarystate.mechanism import mech_k3 as K
from culinarystate.mechanism.mech_k3 import FALSE, TRUE, UNKNOWN, Conjunct

ROOT = Path(__file__).resolve().parents[3]
VERSION = "mech-inputs-0.2.0-draft"   # 0.2.0: SR derivation basis passed to the router presence screen
NUTRIENT_KEYS = ("protein", "sugars", "starch", "fat", "water", "vitamin_c")
ZERO_FLOOR = Fraction(1, 10 ** 6)          # PROPOSED: "SR value > 0" (SR amounts have <= 3 decimals); not a chemistry value
MARGIN = Fraction(15, 100)                 # the router's PROPOSED identity margin (registry/target_presence_floor_v1_PROPOSED.csv)
FLOOR_STATUS = "PROPOSED_SCREEN_CONVENTION_SR_NONZERO"
PH_REGISTRY = ROOT / "registry" / "food_ph_fda2003_v1.csv"
PROC_FAMILY_REGISTRY = ROOT / "registry" / "proc_family_registry_v1.csv"

HEAT_FAMILIES = ("WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL")
DISRUPTIVE_PROCS = frozenset({"PROC-000070", "PROC-000071", "PROC-000085"})     # blend, mash, squeeze
SOAK_PROC = "PROC-000129"
AIR_EXPOSED_MEDIA = frozenset({"OVEN_AIR", "OVEN_AIR_FORCED", "RADIANT", "PAN_CONTACT_OIL", "OIL_SHALLOW"})
IMMERSION_MEDIA = frozenset({"WATER", "LIQUID", "LIQUID_PARTIAL", "WATER_PRESSURIZED"})
STEAM_MEDIA = frozenset({"STEAM"})
NH_AQUEOUS_MEDIA = frozenset({"WATER", "BRINE", "VINEGAR", "CITRUS_JUICE"})
T_BOIL_C = Fraction(100)                   # physical definition: water boils at 100 C at 1 atm (no chemistry value)
L2_SURFACE_AT_TBOIL = frozenset({"SURFACE_WET_AT_TBOIL", "SURFACE_DRYING_POSSIBLE"})
L2_IMMERSED = "SURFACE_IMMERSED_WET"

# ----------------------------------------------------------------------------- taxon classes (AI_DRAFTED, for review)
# SR description head = text before the first comma, lower case. A class member needs every HIGH / MEDIUM plausible
# identity of the ING to be in the class and in a raw form (chlorophyll: raw, fresh or frozen).
CLASS_HEADS: Mapping[str, frozenset] = {
    "ALLIUM_FRESH": frozenset({"garlic", "onions", "leeks", "shallots", "chives"}),
    "ONION_FRESH": frozenset({"onions", "shallots"}),
    "BRASSICA_FRESH": frozenset({"broccoli", "brussels sprouts", "cabbage", "cauliflower", "kale", "kohlrabi", "radishes",
                                 "rutabagas", "turnips", "turnip greens", "watercress", "arugula", "mustard greens", "cress",
                                 "collards", "broccoli raab", "wasabi", "horseradish"}),
    "PPO_FRESH": frozenset({"apples", "pears", "potatoes", "bananas", "avocados", "mushrooms", "eggplant", "peaches",
                            "apricots", "nectarines", "quinces", "artichokes", "sweet potato", "lettuce"}),
    "AAO_FRESH": frozenset({"broccoli", "carrots"}),
    "CHLOROPHYLL_TISSUE": frozenset({"spinach", "kale", "broccoli", "brussels sprouts", "lettuce", "arugula", "watercress",
                                     "cress", "chard", "mustard greens", "collards", "chicory greens", "turnip greens",
                                     "asparagus", "okra", "celery", "leeks", "chives", "parsley", "basil", "spearmint",
                                     "peppermint", "dill weed", "rosemary", "thyme", "edamame", "broadbeans", "jute",
                                     "drumstick pods", "tomatillos", "coriander (cilantro) leaves", "seaweed",
                                     "cabbage", "peas", "beans", "peppers", "squash", "cucumber", "onions", "tomatoes"}),
}
# heads above that are green only in some forms: the description must also contain one of these words
CLASS_QUALIFIER: Mapping[tuple[str, str], tuple[str, ...]] = {
    ("CHLOROPHYLL_TISSUE", "cabbage"): ("savoy", "chinese"),
    ("CHLOROPHYLL_TISSUE", "peas"): ("green", "edible-podded"),
    ("CHLOROPHYLL_TISSUE", "beans"): ("snap, green",),
    ("CHLOROPHYLL_TISSUE", "peppers"): ("green",),
    ("CHLOROPHYLL_TISSUE", "squash"): ("zucchini",),
    ("CHLOROPHYLL_TISSUE", "cucumber"): ("with peel",),
    ("CHLOROPHYLL_TISSUE", "onions"): ("spring", "scallions"),
    ("CHLOROPHYLL_TISSUE", "tomatoes"): ("green",),
}
CLASS_ALLOW_FROZEN = frozenset({"CHLOROPHYLL_TISSUE"})
RAW_WORDS = re.compile(r"\b(?:raw|fresh)\b")
NOT_RAW_WORDS = re.compile(r"\b(?:cooked|boiled|canned|dried|dehydrated|pickled|pickles|fried|roasted|baked|powder|juice|"
                           r"prepared|sauce|stewed|kimchi|sauerkraut|flakes|puree|paste|frozen|microwaved|steamed|"
                           r"blanched|drained)\b")
COLLAGEN_GROUPS = frozenset({"Beef Products", "Pork Products", "Poultry Products", "Lamb, Veal, and Game Products",
                             "Finfish and Shellfish Products"})
# members that are neither reactants nor plausible inhibitors of the cut-triggered enzymes (pure fats and plain water);
# AI_DRAFTED, by canonical ING name; flavoured oils and salted butter are deliberately left out
INERT_CARRIER_NAMES = frozenset({
    "water", "butter", "unsalted butter", "butter room temperature", "butter cold", "olive oil", "extra virgin olive oil",
    "light olive oil", "vegetable oil", "sunflower oil", "rapeseed oil", "oil", "sesame oil", "groundnut oil",
    "peanut oil", "coconut oil", "ghee", "lard", "walnut oil", "goose fat", "duck fat", "chicken fat", "flavourless oil",
    "cooking oil", "hazelnut oil", "spray oil", "neutral-tasting oil", "corn oil", "rice bran oil", "clarified butter",
    "avocado oil", "canola oil"})


def sr_head(desc: str) -> str:
    return desc.split(",")[0].strip().lower()


def in_class(cls: str, desc: str | None) -> bool:
    if not desc:
        return False
    d = desc.lower()
    head = sr_head(desc)
    if head not in CLASS_HEADS[cls]:
        return False
    q = CLASS_QUALIFIER.get((cls, head))
    if q and not any(w in d for w in q):
        return False
    if "frozen" in d and cls in CLASS_ALLOW_FROZEN and not re.search(r"\b(?:cooked|boiled|canned|dried)\b", d):
        return True
    return bool(RAW_WORDS.search(d)) and not NOT_RAW_WORDS.search(d)


# ----------------------------------------------------------------------------- members
@dataclass(frozen=True)
class MemberInfo:
    ing_id: str
    presence: Mapping[str, tuple[str, str]]          # nutrient key -> (PRESENT / ABSENT / UNKNOWN, blocker)
    classes: frozenset                               # taxon classes the member belongs to (identity of record)
    inert: bool
    acid_class: str                                  # FDA 2003 table class (diagnostic for edges only; never a gate)


@dataclass(frozen=True)
class LotMember:
    info: MemberInfo
    heated_before: bool
    cut_before: bool


@dataclass(frozen=True)
class LotCtx:
    lot_id: str
    members: tuple[LotMember, ...]
    n_unknown: int                                   # roots of the lot with no linked ING (unknown identity)


@dataclass(frozen=True)
class EventCtx:
    event_id: str
    process_id: str | None
    family: str | None                               # physical family (proc_family_registry primary family)
    l1: Mapping[str, Mapping[str, Any]]              # Layer 1 inputs (heat or non-heat binder record)
    l2: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)   # bracket -> heat L2 scenario dict
    l2_medium: str | None = None

    @property
    def heat(self) -> bool:
        return self.family in HEAT_FAMILIES or self.process_id in EG.PRIOR_HEAT_PROCS

    @property
    def disruptive(self) -> bool:
        return self.family == "MECHANICAL_CUT" or self.process_id in DISRUPTIVE_PROCS


def read_proc_families(path: Path = PROC_FAMILY_REGISTRY) -> dict[str, str]:
    with Path(path).open(newline="", encoding="utf-8") as fh:
        return {r["proc_id"]: r["primary_family"] for r in csv.DictReader(fh)}


class MemberCatalog:
    """Per-ING member facts, cached. Built once per run (before workers fork)."""

    def __init__(self, cands: Mapping, categories: Mapping, kinds: Mapping, values: Mapping[tuple[int, str], Fraction],
                 descriptions: Mapping[int, str], groups: Mapping[int, str], names: Mapping[str, str],
                 ph_lookup: Callable[[str], str] | None = None,
                 basis: Mapping[tuple[int, str], tuple[str, int]] | None = None) -> None:
        """``basis``: (fdc, key) -> (SR derivation code, data points). When the router's presence screen takes a basis
        (S178 FIX-ROUTER R4), an SR zero supports ABSENT only if it is analytical; with no basis ABSENT is never
        confirmed (fail-closed). The rule in force is recorded in ``basis_rule``."""
        floors = {f"NUT__{k}": EG.Floor(f"NUT__{k}", k, k, _unit(k), ZERO_FLOOR, FLOOR_STATUS, MARGIN)
                  for k in NUTRIENT_KEYS}
        if basis_supported():
            self.screen = EG.TargetPresenceScreen(floors, cands, values, categories, kinds, basis=basis)
            self.basis_rule = "ABSENT_NEEDS_ANALYTICAL_SR_ZERO" if basis is not None else "NO_BASIS_ABSENT_FAIL_CLOSED"
        else:
            self.screen = EG.TargetPresenceScreen(floors, cands, values, categories, kinds)
            self.basis_rule = "ROUTER_SCREEN_WITHOUT_BASIS_RULE"
        self.descriptions, self.groups, self.names = dict(descriptions), dict(groups), dict(names)
        self.ph_lookup = ph_lookup
        self._cache: dict[str, MemberInfo] = {}

    def member(self, ing_id: str) -> MemberInfo:
        m = self._cache.get(ing_id)
        if m is None:
            m = self._cache[ing_id] = self._build(ing_id)
        return m

    def _build(self, ing: str) -> MemberInfo:
        pres = {k: self.screen.member_verdict(f"NUT__{k}", ing) for k in NUTRIENT_KEYS}
        plaus = self.screen.plausible(f"NUT__{NUTRIENT_KEYS[0]}", ing)       # HIGH / MEDIUM plausible identities
        classes = set()
        for cls in CLASS_HEADS:
            if plaus and all(in_class(cls, self.descriptions.get(f)) for f in plaus):
                classes.add(cls)
        if plaus and all(self.groups.get(f) in COLLAGEN_GROUPS for f in plaus):
            classes.add("COLLAGEN_TISSUE")
        name = self.names.get(ing, "")
        acid = self.ph_lookup(name) if (self.ph_lookup and name) else "UNKNOWN"
        return MemberInfo(ing, pres, frozenset(classes), name in INERT_CARRIER_NAMES, acid)

    @classmethod
    def load(cls, root: Path = ROOT, sr_dir: Path | None = None) -> "MemberCatalog":
        from culinarystate.composition import food_ph as PH
        from culinarystate.composition import sr_legacy as SR
        from culinarystate.mechanism import sr_identity as SI
        sr = Path(sr_dir) if sr_dir else SI.default_dir(root)
        idn = SI.build_identity(root=root, sr_dir=sr)
        fdc = {f for cs in idn.cands.values() for f, _, _ in cs}
        foods = SR.load_sr(sr)
        values = {}
        for f in fdc:
            food = foods.get(f)
            if food is None:
                continue
            for name, v in food.nutrients.items():
                key = name.rpartition("_")[0]
                if key in NUTRIENT_KEYS:
                    values[(f, key)] = Fraction(repr(v))
        basis = EG.read_sr_basis(sr, fdc, NUTRIENT_KEYS) if hasattr(EG, "read_sr_basis") else None
        table = PH.PHTable(PH.load_registry(PH_REGISTRY))
        memo: dict[str, str] = {}

        def ph(name: str) -> str:
            if name not in memo:
                memo[name] = PH.acid_class(table.lookup(name))
            return memo[name]
        names = {i: n for i, (n, _) in SI.read_ing().items()}
        return cls(idn.cands, idn.categories, idn.kinds, values, SI.sr_descriptions(sr, fdc), SI.sr_food_groups(sr, fdc),
                   names, ph, basis)

    def describe(self) -> dict[str, Any]:
        return {"inputs_version": VERSION, "floor_rule": FLOOR_STATUS, "identity_margin": str(MARGIN),
                "evidence_gates_version": EG.VERSION, "absent_basis_rule": self.basis_rule,
                "nutrient_keys": list(NUTRIENT_KEYS), "presence_semantics": "evidence_gates.TargetPresenceScreen",
                "values_source": "composition.sr_legacy.load_sr", "identity_source": "mechanism.sr_identity",
                "taxon_classes": sorted(list(CLASS_HEADS) + ["COLLAGEN_TISSUE"]),
                "ings_with_identity": len(self.screen.cands)}


def basis_supported() -> bool:
    """True when ``evidence_gates.TargetPresenceScreen`` takes the SR derivation basis (S178 FIX-ROUTER R4)."""
    import inspect
    return "basis" in inspect.signature(EG.TargetPresenceScreen.__init__).parameters


def _unit(key: str) -> str:
    from culinarystate.mechanism.sr_identity import NUTRIENT_UNITS
    return NUTRIENT_UNITS[key]


# ----------------------------------------------------------------------------- helpers
def _c(value: str, reason: str, basis: str = K.NO_BASIS) -> Conjunct:
    return Conjunct("_", "_", value, reason, basis if value != UNKNOWN else K.NO_BASIS)


def _l1_value(ev: EventCtx, axis: str) -> tuple[Any, str | None]:
    x = ev.l1.get(axis) or {}
    if x.get("status") in (None, "UNKNOWN"):
        return None, None
    return x.get("value"), x.get("basis")


def _frac_lo(v: Any) -> Fraction | None:
    """Lower end of a Layer 1 value (``"100"``, ``"1715/9"`` or a two-item range)."""
    try:
        if isinstance(v, (list, tuple)):
            return min(Fraction(str(x)) for x in v)
        return Fraction(str(v))
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def _basis(b: str | None) -> str:
    """The Layer 1 basis of a bound axis, unchanged; an unrecognised basis is an error (counted, never guessed)."""
    if b in K.L1_BASES:
        return b
    raise K.K3Error(f"unrecognised Layer 1 basis {b!r}")


def _l1_medium(ev: EventCtx) -> tuple[str | None, str | None]:
    v, b = _l1_value(ev, "medium")
    return (v, b) if isinstance(v, str) else (None, None)


def _lot_presence(lot: LotCtx, key: str, trace_exempt_class: str | None = None) -> tuple[str, str]:
    """Router lot rule. A member of ``trace_exempt_class`` never counts as ABSENT for ``key`` (its SR zero is below the
    reporting level of a reactant that is known to occur there in traces): it is UNKNOWN with blocker TRACE_EXEMPT."""
    states = []
    for m in sorted(lot.members, key=lambda m: m.info.ing_id):
        s, b = m.info.presence[key]
        if s == EG.ABSENT and trace_exempt_class and trace_exempt_class in m.info.classes:
            s, b = EG.UNKNOWN, "TRACE_EXEMPT_CLASS"
        states.append((s, b))
    if any(s == EG.PRESENT for s, _ in states):
        return EG.PRESENT, ""
    if states and lot.n_unknown == 0 and all(s == EG.ABSENT for s, _ in states):
        return EG.ABSENT, ""
    if lot.n_unknown:
        return EG.UNKNOWN, "UNLINKED_MEMBER"
    if not states:
        return EG.UNKNOWN, "NO_MEMBERS"
    return EG.UNKNOWN, next(b for s, b in states if s != EG.ABSENT) or "MEMBER_UNKNOWN"


# ----------------------------------------------------------------------------- evaluators
# signature: (lot, member or None, event, view, **args) -> Conjunct (item_key / role filled in by the screen)
def nutrient_present(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str, *, key: str,
                     trace_exempt_class: str | None = None) -> Conjunct:
    """May exclude: FALSE only when every member is ABSENT under the router semantics (measured SR zeros)."""
    s, blocker = _lot_presence(lot, key, trace_exempt_class)
    if s == EG.PRESENT:
        return _c(TRUE, f"{key.upper()}_PRESENT_SR", "REFERENCE_SR")
    if s == EG.ABSENT:
        return _c(FALSE, f"{key.upper()}_ABSENT_SR_ZERO_ALL_MEMBERS", "REFERENCE_SR")
    return _c(UNKNOWN, f"{key.upper()}_PRESENCE_UNKNOWN__{blocker}")


def carbonyl_source(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    """Never FALSE: trace reducing sugars below SR reporting (meat, fish) still react."""
    s, _ = _lot_presence(lot, "sugars")
    if s == EG.PRESENT:
        return _c(TRUE, "CARBONYL_SOURCE_SUGARS_PRESENT_SR", "REFERENCE_SR")
    return _c(UNKNOWN, "CARBONYL_SOURCE_NOT_ESTABLISHED")


def taxon_present(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str, *, cls: str) -> Conjunct:
    """Never FALSE (no SR nutrient measures the class reactant)."""
    pool = [member] if member is not None else list(lot.members)
    if any(cls in m.info.classes for m in pool if m is not None):
        return _c(TRUE, f"TAXON_{cls}_IN_LOT", "REFERENCE_SR")
    return _c(UNKNOWN, f"TAXON_{cls}_NOT_IDENTIFIED")


def collagen_present(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    """May exclude: FALSE only when SR protein is zero for every member (collagen is a protein)."""
    if any("COLLAGEN_TISSUE" in m.info.classes for m in lot.members):
        return _c(TRUE, "COLLAGEN_TISSUE_IN_LOT", "REFERENCE_SR")
    s, _ = _lot_presence(lot, "protein")
    if s == EG.ABSENT:
        return _c(FALSE, "COLLAGEN_ABSENT_PROTEIN_SR_ZERO_ALL_MEMBERS", "REFERENCE_SR")
    return _c(UNKNOWN, "COLLAGEN_TISSUE_NOT_IDENTIFIED")


def cell_disrupted(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    if ev.disruptive:
        return _c(TRUE, "DISRUPTED_BY_THIS_EVENT", "PROCESS_DEFINITION")
    pool = [member] if member is not None else list(lot.members)
    if any(m.cut_before for m in pool if m is not None):
        return _c(TRUE, "DISRUPTED_IN_LINEAGE", "LINEAGE")
    return _c(UNKNOWN, "HEAT_DISRUPTION_NOT_ASSESSED" if ev.heat else "NO_DISRUPTION_EVIDENCE")


ENZYME_CLASSES = frozenset({"ALLIUM_FRESH", "ONION_FRESH", "BRASSICA_FRESH", "PPO_FRESH", "AAO_FRESH"})


def enzyme_active(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    """TRUE only for a member whose identity of record is raw enzyme-bearing tissue and that no earlier event heated."""
    if member is None:
        return _c(UNKNOWN, "ENZYME_MEMBER_NOT_IDENTIFIED")
    if not (member.info.classes & ENZYME_CLASSES):
        return _c(UNKNOWN, "MEMBER_NOT_RAW_ENZYME_TISSUE")
    if member.heated_before:
        return _c(UNKNOWN, "PRIOR_HEAT_INACTIVATION_EXTENT_UNKNOWN")
    return _c(TRUE, "RAW_IDENTITY_NO_HEAT_IN_LINEAGE", "LINEAGE")


def oxygen_contact(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    """Never FALSE: no cooking condition is shown to be oxygen-free."""
    med, b = _l1_medium(ev)
    if med in AIR_EXPOSED_MEDIA:
        return _c(TRUE, "AIR_EXPOSED_MEDIUM", _basis(b))
    lid, lb = _l1_value(ev, "lid_state")
    if lid == "UNCOVERED":
        return _c(TRUE, "UNCOVERED_CUE", _basis(lb))
    aer, ab = _l1_value(ev, "aerated")
    if aer is True:
        return _c(TRUE, "AERATED_BY_MIXING", _basis(ab))
    return _c(UNKNOWN, "OXYGEN_CONTACT_NOT_STATED")


def aqueous_contact(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    """Never FALSE: a lot may hold its own liquid whatever the heating medium."""
    med, b = _l1_medium(ev)
    if med in IMMERSION_MEDIA:
        return _c(TRUE, "IMMERSED_IN_AQUEOUS_MEDIUM", _basis(b))
    if med in STEAM_MEDIA:
        return _c(TRUE, "STEAM_CONDENSATE_CONTACT", _basis(b))
    if med in NH_AQUEOUS_MEDIA and ev.family in ("FERMENT_LEAVEN", "PRESERVATION"):
        return _c(TRUE, "SOAK_OR_BRINE_IN_AQUEOUS_LIQUID", _basis(b))
    rinse, rb = _l1_value(ev, "rinse_medium")
    if rinse == "WATER":
        return _c(TRUE, "RINSED_IN_WATER", _basis(rb))
    return _c(UNKNOWN, "AQUEOUS_CONTACT_NOT_ESTABLISHED")


def excess_water(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    """Never FALSE (the food's own water and limited-water gelatinisation are not assessed)."""
    med, b = _l1_medium(ev)
    if med in IMMERSION_MEDIA:
        return _c(TRUE, "IMMERSED_IN_AQUEOUS_MEDIUM", _basis(b))
    if ev.process_id == SOAK_PROC and med in NH_AQUEOUS_MEDIA:
        return _c(TRUE, "SOAKED_IN_AQUEOUS_LIQUID", _basis(b))
    return _c(UNKNOWN, "EXCESS_WATER_NOT_ESTABLISHED")


def tboil_surface(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str, *, excess_water: bool) -> Conjunct:
    """Gate witness: the surface is held at the boiling point of water. Never FALSE (no window bound is reported).
    L1: an aqueous immersion (or steam, when excess water is not required) at a stated or defined T >= T_boil.
    L2 view: the bracket's surface state, used only when L1 does not already decide TRUE (basis SCENARIO)."""
    media = IMMERSION_MEDIA if excess_water else IMMERSION_MEDIA | STEAM_MEDIA
    med, _ = _l1_medium(ev)
    tv, tb = _l1_value(ev, "temperature_profile")
    lo = _frac_lo(tv) if tv is not None else None
    if med in media and lo is not None and lo >= T_BOIL_C:
        return _c(TRUE, "SURFACE_AT_TBOIL_L1", _basis(tb))
    if view != "L1":
        s = ev.l2.get(view.split(":", 1)[1]) or {}
        state, bath = s.get("surface_state"), s.get("bath_c")
        l2_med = ev.l2_medium or med
        if not excess_water and state in L2_SURFACE_AT_TBOIL:
            return _c(TRUE, "SURFACE_AT_TBOIL_L2", "SCENARIO")
        if state == L2_IMMERSED and l2_med in media and isinstance(bath, (int, float)) and bath >= T_BOIL_C:
            return _c(TRUE, "IMMERSED_AT_TBOIL_L2", "SCENARIO")
        return _c(UNKNOWN, "L2_SURFACE_NOT_AT_TBOIL_OR_NOT_COMPUTED")
    if med not in media:
        return _c(UNKNOWN, "NO_AQUEOUS_TBOIL_MEDIUM_L1")
    if lo is None:
        return _c(UNKNOWN, "TEMPERATURE_UNKNOWN_L1")
    return _c(UNKNOWN, "BELOW_TBOIL_WINDOW_BOUND_NOT_REPORTED")


def heat_applied(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    if ev.heat:
        return _c(TRUE, "HEAT_EVENT", "PROCESS_DEFINITION")
    return _c(UNKNOWN, "NOT_A_HEAT_EVENT_FOOD_T_UNKNOWN")


def denaturing_driver(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str) -> Conjunct:
    """Disjunction: heat at T_boil (surface) OR foaming / whipping. TRUE if any part is TRUE; never FALSE."""
    parts = [tboil_surface(lot, member, ev, view, excess_water=False)]
    aer, ab = _l1_value(ev, "aerated")
    parts.append(_c(TRUE, "AERATED_FOAM_INTERFACE", _basis(ab)) if aer is True else _c(UNKNOWN, "NOT_AERATED"))
    v = K.k_or_or_unknown([p.value for p in parts])
    if v == TRUE:
        p = next(p for p in parts if p.value == TRUE)
        return _c(TRUE, f"DENATURING_DRIVER__{p.reason}", p.basis)
    return _c(UNKNOWN, f"NO_DENATURING_DRIVER__{parts[0].reason}")


def inhibiting_agent_absent(lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str, *, cls: str) -> Conjunct:
    """TRUE only when every member is reactant tissue of the class or an inert carrier and no member is unlinked; else
    UNKNOWN (an inhibitor of unknown extent may act). Never FALSE (no inhibitor here is COMPLETE)."""
    if lot.n_unknown == 0 and lot.members and all(cls in m.info.classes or m.info.inert for m in lot.members):
        return _c(TRUE, "ONLY_REACTANT_OR_INERT_MEMBERS", "MECH_DEFINITION")
    return _c(UNKNOWN, "UNLINKED_MEMBER_MAY_INHIBIT" if lot.n_unknown else "FOREIGN_MEMBER_MAY_INHIBIT")


EVALUATORS: Mapping[str, Callable[..., Conjunct]] = {
    "nutrient_present": nutrient_present, "carbonyl_source": carbonyl_source, "taxon_present": taxon_present,
    "collagen_present": collagen_present, "cell_disrupted": cell_disrupted, "enzyme_active": enzyme_active,
    "oxygen_contact": oxygen_contact, "aqueous_contact": aqueous_contact, "excess_water": excess_water,
    "tboil_surface": tboil_surface, "heat_applied": heat_applied, "denaturing_driver": denaturing_driver,
    "inhibiting_agent_absent": inhibiting_agent_absent,
}
# the only evaluators that can return FALSE (and then only with basis REFERENCE_SR)
MAY_EXCLUDE = frozenset({"nutrient_present", "collagen_present"})


def evaluate(name: str, lot: LotCtx, member: LotMember | None, ev: EventCtx, view: str, args: Mapping[str, Any],
             item_key: str, role: str) -> Conjunct:
    c = EVALUATORS[name](lot, member, ev, view, **dict(args))
    if c.value == FALSE and name not in MAY_EXCLUDE:
        raise K.K3Error(f"evaluator {name} returned FALSE but may not exclude")
    if view == "L1" and c.basis in K.L2_BASES:
        raise K.K3Error(f"evaluator {name} used a Layer 2 value in the L1 view")
    return Conjunct(item_key, role, c.value, c.reason, c.basis, c.flags)


def members_from(catalog: MemberCatalog, rows: Iterable[tuple[str, bool, bool]]) -> tuple[LotMember, ...]:
    return tuple(LotMember(catalog.member(i), h, c) for i, h, c in sorted(rows))


def is_l1_basis(basis: str) -> bool:
    return basis in K.L1_BASES


__all__ = ["MemberCatalog", "MemberInfo", "LotMember", "LotCtx", "EventCtx", "EVALUATORS", "MAY_EXCLUDE", "evaluate",
           "read_proc_families", "in_class", "members_from", "Sequence"]
