"""Layer 1 TEXT_STATED condition binding (S172, D-077): recipe text -> per-event simulator inputs, traced. DRAFT.

Reads the frozen Rung A graph and the raw text (Rung A is not modified). For each heat event it records each sim_aa_1
input with a value, status (MEASURED / RANGE / UNKNOWN), basis and span, and emits contract ``ConditionBinding``s
(source class STRUCTURAL_RECIPE) for the bound ones. Bases, all deterministic:
- TEXT_STATED: a duration (Rung A) or a temperature written in the event's sentence (°C, or °F converted exactly).
- CARRIED_SETPOINT: an oven temperature stated at "preheat", carried to later dry-heat events until restated.
- PHYSICAL_DEFINITION: the verb fixes the bath temperature (boil, steam: 100 °C at 1 atm), from
  registry/process_medium_map_v1.csv; PROCESS_DEFINITION: the medium the verb implies (same registry).
- CUE: lid and start-mode words in the sentence; CUT_HISTORY: the nearest upstream cut verb of a consumed lot;
  FOOD_GROUP: the consumed ingredients' ING food group when they all agree.
Nothing is defaulted: gas marks are kept as a code (GAS_n) with no number; water ratio stays UNKNOWN in v0.

S178 PHYS2 (version 0.2.0, SSOT v16 DRAFT 284.3 / 199.8, PROPOSED):
- Temperature OWNERSHIP (T4-C02 / S177 open item (a)). 0.1.0 bound to each heat event the temperature nearest to its verb among
  ALL temperatures of the sentence, so "Boil the potatoes ... then roast at 400 F" gave the boil an oven temperature (197
  FOODCOM / GUTENBERG / WIKIBOOKS boil, simmer and braise events stated more than 150 C, all of them oven or pan set-points
  attached to a liquid step). A temperature now belongs to ONE event: the last temperature-owning event (heat, heat control,
  cooling, preservation, ferment, resting, storage) whose verb precedes it in the sentence, else the first one that follows. A
  DRY_HEAT or HEAT_GENERAL event may also use a temperature owned by a HEAT_CONTROL event of its sentence ("preheat the oven to
  350 and bake"). A temperature with an oven cue next to it (oven, bake, roast, broil, grill, preheat, ...) is never the bath
  temperature of an aqueous (liquid-medium) step: it is kept as the separate input ``ambient_temperature`` (stated, not used as
  the liquid temperature). A temperature that follows an endpoint cue ("until a thermometer reads 165 F") is a TARGET of the food,
  not a medium temperature: it goes to the ``endpoint`` block (see ``endpoint_cues``), never to ``inputs``. ``temperature_note``
  records every event whose temperature differs from the 0.1.0 rule (audit trail).
- Member groups: ``matrix_groups`` lists the food groups of ALL lot members (so the solute-rich and all-dry rules of the cap act
  on multi-member lots); ``matrix_class`` stays the single group of single-group lots.
- Per-axis provenance (T4-C02): every bound axis carries ``span_id`` (``C:a-b`` characters of the joined step text, ``E:<event>``
  the event verb, ``L:<event>`` the lineage of the lots the event consumes) and ``row`` (registry row or code rule that fixed the
  value); every UNKNOWN axis carries a ``reason``. Records also carry the ``endpoint`` block (stopping criterion, QUALITATIVE,
  with spans), which is NOT part of ``inputs`` and so never part of a feature row.

S178 FIX-PHYS (version 0.3.0, SCI-A M1-M4 and m1-m3; SSOT v16 DRAFT 284.3 / 199.8, PROPOSED, AI_DRAFTED):
- M1 food targets: ``endpoint_cues.classify_temperatures`` (last strong cue, local syrup exemption, until-clause targets) decides
  which temperatures are targets; until-clause spans and roles are stored in the endpoint block.
- M2 medium compatibility. Every temperature gets a cue class from the nearest cue word of its clause window: OVEN (oven, bake,
  roast, broil, grill, preheat ...), OIL (oil, fat, fryer ...), APPLIANCE_PAN (electric skillet / frying pan, griddle),
  APPLIANCE_AMBIENT (slow cooker, crock pot) or HEAT_LEVEL (over medium heat, on high, setting, burner, reduce the heat to ...).
  A temperature is used only by a medium its cue allows: OVEN -> oven and radiant media; OIL -> oil and pan media; APPLIANCE_PAN ->
  pan and shallow-oil media; HEAT_LEVEL / APPLIANCE_AMBIENT -> no medium (an aqueous step keeps one at or below T_boil, the
  PHYSICAL_DEFINITION of the boil in process_medium_map_v1, flagged HEAT_LEVEL_OR_APPLIANCE_SETTING_AT_OR_BELOW_TBOIL). An
  incompatible own temperature is kept as ``ambient_temperature``; a shared one is not shared. A cue-less temperature of a general
  setter ("heat", "cook") is shared only when the receiving step consumes the setter's lot by lineage or cooks "in it".
- M3 the cue window after a temperature ends at the next clause break or event verb (symmetric with the window before it).
- M4 Layer 1 part: new CUE axes ``syrup_stage_cue`` (syrup, candy, jam word or a sugar stage in the event's own phrase) and
  ``pressure_cue`` (pressure cooker / canner, psi), with spans; Layer 2 decides the stated-liquid cap from them.
- m1 one temperature regex (``endpoint_cues.TEMP_RE``): ranges, spelled-out units, "c." as cups. m2 "200C/180C fan" is
  RANGE(fan, conventional) with flag FAN_VS_CONVENTIONAL_UNRESOLVED. m3 ``water_bath_cue`` on an oven step (water bath, bain-marie,
  pan of hot water): Layer 2 runs it as a water medium bounded by T_boil (flag WATER_BATH_IN_OVEN).
"""
from __future__ import annotations

import csv
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence

from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.mechanism.router_demo import _attr
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.simulation import endpoint_cues as EC
from culinarystate.simulation import recipe_adapter as RA
from culinarystate.state_graph.source_class import SourceClass

ROOT = Path(__file__).resolve().parents[3]
VERSION = "condition-binding-L1-0.3.1-draft"
VERSION_V03 = "condition-binding-L1-0.3.0-draft"  # SUPERSEDED S179 (SCI re-review #1: endpoint-cues 0.3.0)
VERSION_V02 = "condition-binding-L1-0.2.0-draft"  # SUPERSEDED by 0.3.0 (SCI-A M1-M4, m1-m3: targets, medium compatibility, window cut)
VERSION_V01 = "condition-binding-L1-0.1.0-draft"  # SUPERSEDED: nearest-temperature rule, no provenance keys
HEAT = ("WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL")
INPUTS = ("duration", "temperature_profile", "medium", "lid_state", "start_mode", "piece_size_class", "water_ratio",
          "matrix_class")
_T = EC.TEMP_RE  # S178 FIX-PHYS m1: one regex for the binder and the endpoint cues
_GAS = re.compile(r"\bgas(?:\s*mark)?\s*(\d{1,2})\b", re.I)
_SENT = re.compile(r"[.!?;\n]+")
_UNCOV = re.compile(r"\buncover(?:ed)?\b|\bwithout (?:a |the )?lid\b|\blid off\b", re.I)
_PART = re.compile(r"\bpartially cover|\bhalf[- ]cover|\blid ajar\b", re.I)
_COV = re.compile(r"\bcover(?:ed)?\b|\blid on\b|\bwith (?:a|the) lid\b", re.I)
_HOT = re.compile(r"\b(?:into|to|in)\s+(?:a\s+)?(?:large\s+)?(?:(?:pan|pot|saucepan)\s+of\s+)?(?:salted\s+)?boiling\b",
                  re.I)
_COLD = re.compile(r"\bcold water\b", re.I)
CUT_CLASS = {"PROC-000045": "DICED", "PROC-000044": "SLICED", "PROC-000043": "CHOPPED", "PROC-000048": "GRATED",
             "PROC-000050": "MINCED", "PROC-000051": "SHREDDED", "PROC-000047": "HALVED", "PROC-000049": "CRUSHED"}
SETPOINT_FAMILIES = ("DRY_HEAT",)
T_MIN_C, T_MAX_C = Fraction(30), Fraction(320)
# S178 PHYS2 (0.2.0): temperature ownership
STORE_PROC = "PROC-000113"  # "store": ledger family TRANSFER, physical family STORAGE
TEMP_OWNER_FAMILIES = HEAT + ("HEAT_CONTROL", "COOLING", "PRESERVATION", "FERMENT_LEAVEN", "RESTING")
SETTER_PROCS = ("PROC-000028",)  # "reduce temperature to 350 and roast": the verb reduce (WET_HEAT by alias) also sets a temperature
SETTER_FAMILIES = ("HEAT_CONTROL", "HEAT_GENERAL")  # "preheat the oven to ...", "heat the oil to ...": the value is shared with later heat steps
LIQUID_MEDIA = ("WATER", "LIQUID", "LIQUID_PARTIAL", "WATER_PRESSURIZED", "WATER_BATH_SEALED")  # = phase_change.AQUEOUS_LIQUID_MEDIA
_OVEN_CUE = re.compile(r"\b(?:ovens?|bake[sd]?|baking|roast(?:s|ed|ing)?|broil(?:s|ed|ing|er)?|grill(?:s|ed|ing)?|bbq|"
                       r"barbecue[sd]?|preheat\w*|pre-heat\w*|convection|toaster)\b", re.I)
_OIL_CUE = re.compile(r"\b(?:oil|fat|lard|shortening|fryer|deep[- ]fry\w*|frying)\b", re.I)
_HEAT_LEVEL = re.compile(r"\b(?:low|medium|med|high|moderate|moderately)[- ]?(?:low|high)?[- ]+heat\s*(?:setting\s*)?(?:\(|of|to|at|:)?\s*$",
                         re.I)  # 0.2.0 (kept for reference)
# S178 FIX-PHYS M4 / M2: heat-level and appliance cues (the heater's setting, not a medium temperature)
_LEVEL_WORDS = (r"\b(?:low|medium|med|high|moderate|moderately)(?:[- ](?:low|high))?[- ]+(?:heat|flame|fire)\b|"
                r"\bon (?:high|low|medium)\b|\bsetting\b|\bburners?\b|\bhob\b|\bstove[- ]?top\b")
# "reduce / lower / raise the heat (temperature) to N": the setting of whatever heats the step (oven, fryer or burner)
_CHANGE_WORDS = r"\b(?:reduce|lower|increase|raise|turn|adjust|drop)\w*\s+(?:the\s+)?(?:heat|flame|burner|temperature|temp)\b(?:\s+(?:down|up|back))?"
_LEVEL_TAIL = r"(?:\s|,|\(|:|-|\bto\b|\bat\b|\bof\b|\babout\b|\baround\b|\bapproximately\b|\bapprox\.?|\bsetting\b|\bset\b)*$"
_HEAT_LEVEL_ANCHORED = re.compile(rf"(?:{_LEVEL_WORDS}){_LEVEL_TAIL}", re.I)
_HEAT_CHANGE_ANCHORED = re.compile(rf"(?:{_CHANGE_WORDS}){_LEVEL_TAIL}", re.I)
_APPLIANCE_PAN = re.compile(r"\belectric (?:skillet|frying[- ]pan|fry[- ]?pan|griddle|wok)\b|\bgriddle\b", re.I)
_APPLIANCE_AMBIENT = re.compile(r"\bslow[- ]?cookers?\b|\bcrock[- ]?pots?\b|\bcrockpots?\b", re.I)
_SYRUP_STAGE = re.compile(rf"\b(?:{EC._SYRUP_WORDS})\b|\bsoft[- ]ball\b|\bfirm[- ]ball\b|\bhard[- ]ball\b|\bsoft[- ]crack\b|"
                          r"\bhard[- ]crack\b|\bthread stage\b|\bjelly stage\b|\bsetting point\b|\bgel(?:ling)? point\b", re.I)
_PRESSURE = re.compile(r"\bpressure[- ]?(?:cook\w*|canners?)\b|\b\d{1,2}\s*(?:psi|psig|lbs?\.?\s+(?:of\s+)?pressure|pounds?\s+"
                       r"(?:of\s+)?pressure)\b|\binstant ?pot\b|\bautoclave\b", re.I)
_WATER_BATH = re.compile(r"\b(?:hot[- ]|warm[- ]|boiling[- ])?water[- ]bath\b|\bbain[- ]?marie\b|\bba[ñn]o[- ]mar[íi]a\b|"
                         r"\b(?:roasting )?(?:pan|tin|dish|tray) (?:half[- ]filled )?(?:of|with) (?:hot|boiling|warm) water\b", re.I)
_ANAPHORA = re.compile(r"\b(?:in|into|to|with)\s+(?:it|them|this|that|the (?:hot |warm |same |heated |scalded )?"
                       r"(?:milk|liquid|mixture|water|stock|broth|syrup|cream|oil|fat|butter|pan|pot|saucepan))\b", re.I)
_FAN = re.compile(r"\s*(?:/|\(|,|or)\s*$")
_FAN_AFTER = re.compile(r"\s*(?:fan(?:[- ]assisted| oven| forced)?|fan-forced|convection)\b", re.I)
OVEN_MEDIA = ("OVEN_AIR", "OVEN_AIR_FORCED", "RADIANT")
OIL_MEDIA = ("OIL_IMMERSION", "OIL_SHALLOW", "PAN_CONTACT_OIL")
PAN_MEDIA = ("PAN_CONTACT_OIL", "OIL_SHALLOW")
CUE_CLASSES = ("OVEN", "OIL", "APPLIANCE_PAN", "APPLIANCE_AMBIENT", "HEAT_LEVEL", "HEAT_CHANGE")
SETTING_CLASSES = ("HEAT_LEVEL", "HEAT_CHANGE", "APPLIANCE_PAN", "APPLIANCE_AMBIENT")  # a heater setting, not a liquid temperature
HEAT_LEVEL_LE_TBOIL = "HEAT_LEVEL_OR_APPLIANCE_SETTING_AT_OR_BELOW_TBOIL"
FAN_FLAG = "FAN_VS_CONVENTIONAL_UNRESOLVED"
_CLAUSE_CUT = re.compile(r"[,;]|\b(?:then|and|while|before|after|until)\b", re.I)
_LEADING_GAP = re.compile(r"\s*(?:,|and|then|&)?\s*(?:and\s+|then\s+)?(?:\w+\s+){0,1}")
OVEN_WINDOW_BEFORE, OVEN_WINDOW_AFTER = 40, 25
INPUT_REASONS = {"duration": "NO_DURATION_STATED", "temperature_profile": "NO_TEMPERATURE_STATED", "medium": "NO_MEDIUM_IN_PROCESS_MAP",
                 "lid_state": "NO_LID_CUE", "start_mode": "NO_START_CUE", "piece_size_class": "NO_CUT_HISTORY",
                 "water_ratio": "NOT_BOUND_V0", "matrix_class": "NO_FOOD_GROUP"}


def _latest(path: Path) -> dict:
    out: dict = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                if r["id"] not in out or r.get("version", 0) >= out[r["id"]].get("version", 0):
                    out[r["id"]] = r
    return out




def _c(v: Fraction, unit: str) -> Fraction:
    return (v - 32) * Fraction(5, 9) if unit.upper() == "F" else v


def _unknown(reason: str | None = None) -> dict:
    d = {"value": None, "status": "UNKNOWN", "basis": None, "span": None}
    if reason:
        d["reason"] = reason
    return d


def _known(value, basis: str, span=None, *, sid: str | None = None, row: str | None = None) -> dict:
    """A bound axis. ``span`` = characters in the joined step text (or None); ``span_id`` always names the evidence: ``C:a-b``
    characters, ``E:<event>`` an event verb, ``L:<event>`` the lots the event consumes; ``row`` the registry row or code rule
    that fixed the value (T4-C02)."""
    status = "RANGE" if isinstance(value, tuple) and value[0] != value[1] else "MEASURED"
    out = {"value": value[0] if isinstance(value, tuple) and value[0] == value[1] else value, "status": status,
           "basis": basis, "span": list(span) if span is not None else None}
    out["span_id"] = sid or (EC.span_id(span) if span is not None else None)
    out["row"] = row
    return out


def _claim_span(claims, *fields) -> tuple[int, int] | None:
    for c in claims:
        sp = getattr(c, "span", None)
        if c.field in fields and sp is not None and getattr(sp, "segments", None):
            return (min(s[0] for s in sp.segments), max(s[1] for s in sp.segments))
    return None


class TempPlan:
    """Temperatures one temperature-owning event may use (S178 PHYS2, FIX-PHYS 0.3.0). ``temps`` = own first, then those shared from
    earlier setter steps (medium-compatible only); ``legacy`` = every temperature of the sentence (the 0.1.0 candidates); ``target``
    = spans that are targets of the food; ``oven`` = spans with an oven, grill, appliance or heat-level cue (never a liquid
    temperature above T_boil); ``oil`` = spans with an oil or fat cue; ``owner_of`` = the events that own each span; ``cue`` = span ->
    (nearest cue class or None, all cue classes of its window); ``fan`` = merged UK fan / conventional spans; ``roles`` = the
    endpoint role of every span; ``level_ok`` = spans shared under the heat-level-at-or-below-T_boil rule; ``window`` = the event's
    own phrase (verb to the next owner verb) and ``lead`` = the start of the text before it that belongs to no other owner."""
    __slots__ = ("temps", "own", "legacy", "target", "oven", "owner_of", "oil", "cue", "fan", "roles", "level_ok", "window", "lead",
                 "amb_shared")

    def __init__(self, temps, own, legacy, target, oven, owner_of, oil=frozenset(), cue=None, fan=frozenset(), roles=None,
                 level_ok=frozenset(), window=None, lead=None, amb_shared=()):
        self.temps, self.own, self.legacy, self.target, self.oven, self.owner_of = temps, own, legacy, target, oven, owner_of
        self.oil, self.cue, self.fan, self.roles, self.level_ok = oil, cue or {}, fan, roles or {}, level_ok
        self.window, self.lead = window, lead
        self.amb_shared = list(amb_shared)  # heater settings of an earlier setter that this step may not use ("reduce heat to 325 F")


def _lineage(g, receiver, setter) -> bool:
    """True when ``receiver`` consumes a lot that descends from a lot ``setter`` produced (Rung A lineage)."""
    if g is None:
        return False
    made = set(setter.produces)
    ents = {e.entity_id: e for e in g.entities}
    stack, seen = list(receiver.consumes), set()
    while stack:
        lid = stack.pop()
        if lid in seen:
            continue
        seen.add(lid)
        if lid in made:
            return True
        if lid in ents:
            stack.extend(ents[lid].parent_entity_ids)
    return False


class Binder:
    def __init__(self, *, rung: RungA, schema: Any, medium_map: Mapping[str, Mapping], family: Mapping[str, str],
                 food_group: Mapping[str, str]) -> None:
        self.rung, self.schema, self.medium_map, self.family, self.food_group = rung, schema, medium_map, family, \
            food_group
        self.lexicon = EC.load_lexicon()
        tb = (medium_map.get("PROC-000019") or {}).get("physical_definition_degC")
        self.t_boil_def = Fraction(tb) if tb else None  # PHYSICAL_DEFINITION of the boil (process_medium_map_v1)

    @classmethod
    def load(cls, root: Path = ROOT) -> "Binder":
        with open(root / "registry/process_medium_map_v1.csv", newline="", encoding="utf-8") as fh:
            mm = {r["process_id"]: r for r in csv.DictReader(fh)}
        procs = _latest(root / "ledgers/data/PROC.jsonl")
        ings = _latest(root / "ledgers/data/ING.jsonl")
        groups = {i: (r.get("category") or r.get("food_group")) for i, r in ings.items() if r.get("status") == "ACTIVE"}
        return cls(rung=RungA(), schema=D.load_schema(root), medium_map=mm,
                   family={p: r.get("family") for p, r in procs.items()},
                   food_group={i: g for i, g in groups.items() if g})

    # ---------------------------------------------------------------- helpers
    @staticmethod
    def _sentence(raw: str, pos: int) -> tuple[int, int]:
        starts = [0] + [m.end() for m in _SENT.finditer(raw)]
        start = max(s for s in starts if s <= pos)
        nxt = _SENT.search(raw, pos)
        return start, (nxt.start() if nxt else len(raw))

    @staticmethod
    def _temps_fan(raw: str, a: int, b: int) -> tuple[list[tuple[Any, tuple[int, int]]], set[tuple[int, int]]]:
        """Temperatures of ``raw[a:b]`` (``endpoint_cues.parse_temperatures``, within T_MIN_C..T_MAX_C) and the spans that merge a
        UK fan / conventional pair ("200C/180C fan", "180C fan / 200C") into RANGE(fan, conventional) (S178 FIX-PHYS m2)."""
        got = [t for t in EC.parse_temperatures(raw, a, b) if T_MIN_C <= t[0][0] <= t[0][1] <= T_MAX_C]
        out, fan, i = [], set(), 0
        while i < len(got):
            (v, (s, e)) = got[i]
            if i + 1 < len(got) and v[0] == v[1] and got[i + 1][0][0] == got[i + 1][0][1]:
                (v2, (s2, e2)) = got[i + 1]
                gap = raw[e:s2]
                second_fan = re.fullmatch(r"\s*(?:/|\(|,|or)\s*", gap, re.I) and _FAN_AFTER.match(raw, e2)
                first_fan = re.fullmatch(r"\s*(?:fan(?:[- ]assisted| oven| forced)?|fan-forced|convection)\s*(?:/|\(|,|or)\s*", gap,
                                         re.I)
                if second_fan or first_fan:
                    lo, hi = sorted((v[0], v2[0]))
                    out.append(((lo, hi), (s, e2)))
                    fan.add((s, e2))
                    i += 2
                    continue
            out.append((v, (s, e)))
            i += 1
        return out, fan

    @classmethod
    def _temperatures(cls, raw: str, a: int, b: int) -> list[tuple[Any, tuple[int, int]]]:
        return cls._temps_fan(raw, a, b)[0]

    @staticmethod
    def _cue_class(raw: str, a: int, b: int, s: int, e: int, verbs: Sequence[int]) -> tuple[str | None, frozenset]:
        """(nearest cue class, all cue classes) of the clause window of the temperature ``[s, e)`` (S178 FIX-PHYS M2 / M3 / M4).
        The window runs 40 characters before (cut at the last clause break) and 25 after, cut at the first clause break and at the
        next event verb after the temperature (M3). A heat-level phrase directly before the temperature (commas and fillers
        allowed: "over medium heat, about 300 F") counts at distance 0."""
        lo = max(a, s - OVEN_WINDOW_BEFORE)
        cuts = list(_CLAUSE_CUT.finditer(raw, lo, s))
        if cuts:
            lo = cuts[-1].end()
        hi = min(b, e + OVEN_WINDOW_AFTER)
        c = _CLAUSE_CUT.search(raw, e, hi)
        if c:
            hi = c.start()
        nv = [v for v in verbs if v >= e]
        if nv:
            hi = min(hi, nv[0])
        found = []
        for rank, (cls, rx) in enumerate((("OVEN", _OVEN_CUE), ("OIL", _OIL_CUE), ("APPLIANCE_PAN", _APPLIANCE_PAN),
                                          ("APPLIANCE_AMBIENT", _APPLIANCE_AMBIENT))):
            for m in rx.finditer(raw, lo, hi):
                d = s - m.end() if m.end() <= s else m.start() - e
                found.append((max(d, 0), rank, cls))
        if _HEAT_LEVEL_ANCHORED.search(raw, max(a, s - 40), s):
            found.append((0, -2, "HEAT_LEVEL"))
        elif _HEAT_CHANGE_ANCHORED.search(raw, max(a, s - 40), s):
            found.append((0, -1, "HEAT_CHANGE"))
        return (min(found)[2] if found else None), frozenset(c for _, _, c in found)

    def _share_ok(self, t, cue: tuple[str | None, frozenset], setter_fam: str | None, setter_pid: str | None,
                  medium: str | None, linked: bool) -> tuple[bool, bool]:
        """(may the receiving medium use this shared temperature, was it taken under the heat-level-at-or-below-T_boil rule)."""
        cls = cue[0]
        liquid_ok = medium in LIQUID_MEDIA and self.t_boil_def is not None and t[0][1] <= self.t_boil_def
        unknown = medium is None  # a generic "cook" / "heat" step: no medium to contradict (Layer 2 cannot run it without one)
        if cls == "OVEN":
            return medium in OVEN_MEDIA or unknown, False
        if cls == "OIL":
            return medium in OIL_MEDIA or unknown, False
        if cls == "APPLIANCE_PAN":
            return medium in PAN_MEDIA or unknown, False
        if cls == "HEAT_CHANGE":  # "reduce the heat to 350 F and bake": the oven's (or fryer's) setting; a liquid only <= T_boil
            if medium in OVEN_MEDIA or medium in OIL_MEDIA or unknown:
                return True, False
            return liquid_ok, liquid_ok
        if cls in ("HEAT_LEVEL", "APPLIANCE_AMBIENT"):
            return liquid_ok, liquid_ok
        if setter_fam == "HEAT_CONTROL" or setter_pid in SETTER_PROCS or setter_fam == "DRY_HEAT":
            return medium in OVEN_MEDIA or unknown, False
        return linked, False  # a cue-less general setter ("heat the milk to 180 F"): lineage or "in it" only

    def temperature_plan(self, raw: str, events: Sequence, g=None) -> dict[str, TempPlan]:
        """Who owns each temperature (S178 PHYS2 0.2.0, FIX-PHYS 0.3.0). ``events`` = graph events with spans, in text order;
        ``g`` = the Rung A graph (lineage for the general-setter rule; optional). A temperature belongs to the last
        temperature-owning event whose verb precedes it in the sentence, else the first that follows. A heat event may also use a
        temperature owned by an EARLIER setter when its medium is compatible with the temperature's cue (``_share_ok``).
        Targets of the food (``endpoint_cues.classify_temperatures``) are nobody's bath temperature."""
        groups: dict[tuple[int, int], list] = {}
        all_verbs: dict[tuple[int, int], list[int]] = {}
        for ev in events:
            sent = self._sentence(raw, ev.span.char_start)
            all_verbs.setdefault(sent, []).append(ev.span.char_start)
            pid = _attr(ev.attributes, "proc_id")
            fam = "STORAGE" if pid == STORE_PROC else self.family.get(pid)
            if fam in TEMP_OWNER_FAMILIES or fam == "STORAGE":
                groups.setdefault(sent, []).append((ev, fam))
        plan: dict[str, TempPlan] = {}
        for (a, b), evs in groups.items():
            temps, fan = self._temps_fan(raw, a, b)
            starts = [ev.span.char_start for ev, _ in evs]
            verbs = sorted(all_verbs.get((a, b), starts))
            roles = EC.classify_temperatures(raw, a, b, temps, starts)
            target = {sp for sp, r in roles.items() if r in EC.TARGET_ROLES}
            owned: dict[str, list] = {ev.event_id: [] for ev, _ in evs}
            owner_of: dict[tuple[int, int], str] = {}
            oven: set[tuple[int, int]] = set()
            oil: set[tuple[int, int]] = set()
            cue: dict[tuple[int, int], tuple] = {}
            for t in temps:
                s, e = t[1]
                if (s, e) in target:
                    continue
                prec = [i for i, st in enumerate(starts) if st <= s]
                oi = prec[-1] if prec else 0
                owners = [oi]
                for j in range(oi - 1, -1, -1):  # coordinated verbs ("bake (braise) at 350", "bake or roast at 200") share it
                    if starts[oi] - starts[j] > 40 or _CLAUSE_CUT.search(raw, starts[j], starts[oi]) or \
                            any(starts[j] <= ts[0] < starts[oi] for _, ts in temps):
                        break
                    owners.append(j)
                for j in owners:
                    owned[evs[j][0].event_id].append(t)
                owner_of[(s, e)] = frozenset(evs[j][0].event_id for j in owners)
                cue[(s, e)] = self._cue_class(raw, a, b, s, e, verbs)
                if cue[(s, e)][1] & {"OVEN", *SETTING_CLASSES}:
                    oven.add((s, e))
                if "OIL" in cue[(s, e)][1]:
                    oil.add((s, e))
            # a second temperature of one owner that leads the next owner-less verb ("bake at 450 ..., turn the oven down to 350 and
            # bake 10 more minutes") belongs to that verb
            for i in range(len(evs) - 1):
                mine, nxt = owned[evs[i][0].event_id], owned[evs[i + 1][0].event_id]
                if len(mine) >= 2 and not nxt:
                    t = mine[-1]
                    if t[1][0] < starts[i + 1] and _LEADING_GAP.fullmatch(raw[t[1][1]:starts[i + 1]]):
                        mine.remove(t)
                        nxt.append(t)
                        owner_of[t[1]] = frozenset({evs[i + 1][0].event_id})
            for i, (ev, fam) in enumerate(evs):
                w1 = starts[i + 1] if i + 1 < len(evs) else b
                lead = starts[i - 1] if i > 0 else a
                shared: list = []
                amb_shared: list = []
                level_ok: set = set()
                if fam in HEAT:
                    medium = (self.medium_map.get(_attr(ev.attributes, "proc_id")) or {}).get("medium_code")
                    anaphora = bool(_ANAPHORA.search(raw, starts[i], w1))
                    for j in range(i):
                        sev, sfam = evs[j]
                        spid = _attr(sev.attributes, "proc_id")
                        setter = sfam in SETTER_FAMILIES or spid in SETTER_PROCS
                        oven_step = sfam == "DRY_HEAT" and fam in ("DRY_HEAT", "HEAT_GENERAL")
                        if not (setter or oven_step):
                            continue
                        linked = anaphora or _lineage(g, ev, sev)
                        for t in owned[sev.event_id]:
                            ok, lv = self._share_ok(t, cue.get(t[1], (None, frozenset())), sfam, spid, medium, linked)
                            if ok:
                                shared.append(t)
                                if lv:
                                    level_ok.add(t[1])
                            elif setter and (cue.get(t[1], (None,))[0] in SETTING_CLASSES or (
                                    cue.get(t[1], (None,))[0] == "OVEN" and (fam == "WET_HEAT" or medium in LIQUID_MEDIA))):
                                amb_shared.append(t)  # a heater setting (or an oven value next to a liquid step): stated, not used
                shared.sort(key=lambda t: -t[1][0])
                own = owned[ev.event_id]
                plan[ev.event_id] = TempPlan(own + shared, own, temps, target, oven, owner_of, oil, cue, fan, roles,
                                             frozenset(level_ok), (starts[i], w1), lead, amb_shared)
        return plan

    def _cut_class(self, g, lot_ids) -> tuple[str | None, Any]:
        """(cut class, the cut event) of the nearest upstream cut verb of a consumed lot."""
        producers = {p: ev for ev in g.events for p in ev.produces}
        ents = {e.entity_id: e for e in g.entities}
        stack, seen = list(lot_ids), set()
        while stack:
            lid = stack.pop()
            if lid in seen:
                continue
            seen.add(lid)
            ev = producers.get(lid)
            if ev is not None and _attr(ev.attributes, "proc_id") in CUT_CLASS:
                return CUT_CLASS[_attr(ev.attributes, "proc_id")], ev
            if lid in ents:
                stack.extend(ents[lid].parent_entity_ids)
        return None, None

    def _groups(self, g, lot_ids) -> set[str]:
        from culinarystate.mechanism.router_demo import _lot_ingredients
        return {self.food_group[i] for i in _lot_ingredients(g, lot_ids) if i in self.food_group}

    # ---------------------------------------------------------------- main
    def bind_text(self, raw: str, locale: str | None = None) -> dict:
        g = self.rung.run(SourceText.from_raw("BIND", raw), self.rung.config(locale=locale), schema=self.schema).graph
        events, bindings = [], []
        setpoint, gas = None, None
        evs = sorted((e for e in g.events if e.span is not None), key=lambda e: e.span.char_start)
        plan = self.temperature_plan(raw, evs, g)
        heat_by_sentence: dict[tuple[int, int], list[tuple[str, int]]] = {}
        for ev in evs:
            if self.family.get(_attr(ev.attributes, "proc_id")) in HEAT:
                heat_by_sentence.setdefault(self._sentence(raw, ev.span.char_start), []).append(
                    (ev.event_id, ev.span.char_start))
        cues: dict[str, list[dict]] = {}
        clauses: dict[str, list[dict]] = {}
        for (a, b), hs in heat_by_sentence.items():
            roles = plan[hs[0][0]].roles if hs[0][0] in plan else None
            owners = sorted(ev.span.char_start for ev in evs if ev.event_id in plan and self._sentence(raw, ev.span.char_start) == (a, b))
            cues.update(EC.extract_sentence(raw, a, b, hs, lex=self.lexicon, temps=self._temperatures(raw, a, b), roles=roles,
                                            verbs=owners))
            clauses.update(EC.until_clauses_by_event(raw, a, b, hs, roles or {}, owners))
        for ev in evs:
            pid = _attr(ev.attributes, "proc_id")
            fam = self.family.get(pid)
            a, b = self._sentence(raw, ev.span.char_start)
            tp = plan.get(ev.event_id)
            temps = tp.temps if tp else []
            gm = _GAS.search(raw, a, b)
            if fam == "HEAT_CONTROL":
                setpoint = (temps[0], ev.event_id) if temps else setpoint
                gas = f"GAS_{gm.group(1)}" if gm else (None if temps else gas)
            rec = {"event_id": ev.event_id, "action": ev.span.surface, "process_id": pid, "family": fam,
                   "heat": fam in HEAT, "inputs": {}, "oven_setpoint_code": None}
            if fam in HEAT:
                notes: list[dict] = []
                rec["inputs"], rec["oven_setpoint_code"] = self._inputs(raw, g, ev, pid, fam, (a, b), temps, setpoint, gas,
                                                                         gm, plan=tp, notes=notes)
                rec[EC.BLOCK_KEY] = EC.block(cues.get(ev.event_id, []), clauses.get(ev.event_id, []))
                if notes:
                    rec["temperature_note"] = notes
                bindings += self._bindings(ev.event_id, rec["inputs"])
            events.append(rec)
        return {"version": VERSION, "events": events, "bindings": tuple(bindings)}

    def _inputs(self, raw, g, ev, pid, fam, sent, temps, setpoint, gas, gm, plan: TempPlan | None = None,
                notes: list | None = None):
        a, b = sent
        text = raw[a:b]
        eid = ev.event_id
        inp = {k: _unknown(INPUT_REASONS[k]) for k in INPUTS}
        dur = _attr(ev.attributes, "duration_min")
        if dur is not None:
            sp = _claim_span(ev.attributes, "duration_min", "duration")
            inp["duration"] = _known(tuple(Fraction(x) for x in dur) if isinstance(dur, tuple) else
                                     (Fraction(dur), Fraction(dur)), "TEXT_STATED", sp, sid=None if sp else f"E:{eid}",
                                     row="RUNG_A:duration_min")
        mm = self.medium_map.get(pid) or {}
        medium = mm.get("medium_code")
        # S178 FIX-PHYS M2 / M4: a temperature is used only by a medium its cue allows; the rest is kept as ambient_temperature
        liquid = fam == "WET_HEAT" or medium in LIQUID_MEDIA
        cand = list(temps)
        level_kept: set = set()
        if plan is not None:
            def _reject(t) -> str | None:
                near, classes = plan.cue.get(t[1], (None, frozenset()))
                if liquid:
                    if "OVEN" in classes:
                        return "OVEN_OR_HEAT_LEVEL_CUE"
                    if classes & set(SETTING_CLASSES):
                        if self.t_boil_def is not None and t[0][1] <= self.t_boil_def:
                            level_kept.add(t[1])
                            return None
                        return "HEAT_LEVEL_OR_APPLIANCE_CUE"
                    if t[1] in plan.oil and t not in plan.own:  # an oil temperature shared from an earlier "heat the oil to ..."
                        return "OIL_CUE_SHARED_FROM_SETTER"
                    return None
                if medium in OVEN_MEDIA and near in ("HEAT_LEVEL", "APPLIANCE_AMBIENT", "APPLIANCE_PAN"):
                    return "HEAT_LEVEL_OR_APPLIANCE_CUE_NOT_OVEN_AIR"
                if medium in OIL_MEDIA and near in ("OVEN", "HEAT_LEVEL", "APPLIANCE_AMBIENT"):
                    return "OVEN_OR_HEAT_LEVEL_CUE_NOT_OIL_OR_PAN"
                return None
            amb = [(t, _reject(t)) for t in cand]
            amb = [(t, why) for t, why in amb if why]
            bad = {t[1] for t, _ in amb}
            cand = [t for t in cand if t[1] not in bad]
            if amb:
                t, why = min(amb, key=lambda x: abs(x[0][1][0] - ev.span.char_start))
                inp["ambient_temperature"] = _known(t[0], "TEXT_STATED", t[1], row=f"CB_RULE:AMBIENT_{why}")
            elif plan.amb_shared:
                t = max(plan.amb_shared, key=lambda x: x[1][0])
                inp["ambient_temperature"] = _known(t[0], "TEXT_STATED", t[1], row="CB_RULE:AMBIENT_SETTER_VALUE_NOT_COMPATIBLE")
        code = None
        chosen = None
        if cand:
            pool = [t for t in cand if plan is None or t in plan.own] or cand
            near = min(pool, key=lambda t: abs(t[1][0] - ev.span.char_start))
            chosen = near[1]
            own = plan is None or near in plan.own
            inp["temperature_profile"] = _known(near[0], "TEXT_STATED", near[1],
                                                row="CB_RULE:TEMPERATURE_OWN_CLAUSE" if own else
                                                "CB_RULE:TEMPERATURE_FROM_SETTER_STEP")
            tflags = []
            if plan is not None and near[1] in plan.fan:
                tflags.append(FAN_FLAG)
            if plan is not None and (near[1] in level_kept or near[1] in plan.level_ok):
                tflags.append(HEAT_LEVEL_LE_TBOIL)
            if tflags:
                inp["temperature_profile"]["flags"] = tflags
        elif fam in SETPOINT_FAMILIES and setpoint is not None:
            inp["temperature_profile"] = _known(setpoint[0][0], "CARRIED_SETPOINT", setpoint[0][1],
                                                row="CB_RULE:CARRIED_SETPOINT")
        elif mm.get("physical_definition_degC"):
            v = Fraction(mm["physical_definition_degC"])
            inp["temperature_profile"] = _known((v, v), "PHYSICAL_DEFINITION", None, sid=f"E:{eid}",
                                                row=f"process_medium_map_v1:{pid}")
        elif fam in SETPOINT_FAMILIES and (gm or gas):
            code = f"GAS_{gm.group(1)}" if gm else gas
            inp["temperature_profile"] = _unknown("GAS_MARK_CODE_ONLY")
        # S178 FIX-PHYS M4 / m3: CUE axes from the event's own phrase (spans; Layer 2 decides what they allow)
        if plan is not None and plan.window is not None:
            w0, w1 = plan.window
            lead = plan.lead if plan.lead is not None else a
            m = _SYRUP_STAGE.search(raw, w0, w1)
            if m:
                inp["syrup_stage_cue"] = _known("SYRUP_OR_CANDY_STAGE", "CUE", (m.start(), m.end()), row="CB_RULE:SYRUP_STAGE_CUE")
            m = _PRESSURE.search(raw, lead, w1)
            if m:
                inp["pressure_cue"] = _known("PRESSURE_STATED", "CUE", (m.start(), m.end()), row="CB_RULE:PRESSURE_CUE")
            if medium in ("OVEN_AIR", "OVEN_AIR_FORCED"):
                m = _WATER_BATH.search(raw, lead, w1)
                if m:
                    inp["water_bath_cue"] = _known("WATER_BATH_IN_OVEN", "CUE", (m.start(), m.end()), row="CB_RULE:WATER_BATH_IN_OVEN")
        if plan is not None and notes is not None and plan.legacy:
            leg = min(plan.legacy, key=lambda t: abs(t[1][0] - ev.span.char_start))[1]
            if chosen != leg:
                if leg in plan.target:
                    why = "TARGET_FOOD_TEMPERATURE"
                elif leg in plan.owner_of and eid not in plan.owner_of[leg]:
                    why = "OWNED_BY_OTHER_EVENT"
                elif liquid and (leg in plan.oven or leg in plan.oil):
                    why = "OVEN_OIL_OR_HEAT_LEVEL_CUE_TEMPERATURE_OF_LIQUID_STEP"
                elif leg in plan.oven or leg in plan.oil:
                    why = "CUE_NOT_COMPATIBLE_WITH_MEDIUM"
                else:
                    why = "OTHER_TEMPERATURE_SELECTED"
                notes.append({"legacy_span": list(leg), "now": why})
        if mm.get("medium_code"):
            inp["medium"] = _known(mm["medium_code"], "PROCESS_DEFINITION", None, sid=f"E:{eid}",
                                   row=f"process_medium_map_v1:{pid}")
        lid, m = None, None
        for label, rx in (("UNCOVERED", _UNCOV), ("PARTIAL", _PART), ("COVERED", _COV)):
            m = rx.search(text)
            if m:
                lid = label
                break
        if lid:
            inp["lid_state"] = _known(lid, "CUE", (a + m.start(), a + m.end()), row=f"CB_RULE:LID_{lid}")
        start, m = None, None
        for label, rx in (("HOT_START", _HOT), ("COLD_START", _COLD)):
            m = rx.search(text)
            if m:
                start = label
                break
        if start:
            inp["start_mode"] = _known(start, "CUE", (a + m.start(), a + m.end()), row=f"CB_RULE:{start}")
        cut, cut_ev = self._cut_class(g, ev.consumes)
        if cut:
            inp["piece_size_class"] = _known(cut, "CUT_HISTORY", None, sid=f"E:{cut_ev.event_id}",
                                             row=f"CB_RULE:CUT_CLASS:{_attr(cut_ev.attributes, 'proc_id')}")
        groups = self._groups(g, ev.consumes)
        if len(groups) == 1:
            inp["matrix_class"] = _known(next(iter(groups)), "FOOD_GROUP", None, sid=f"L:{eid}", row="ING_LEDGER:category")
        elif len(groups) > 1:
            inp["matrix_class"] = _unknown("MULTIPLE_FOOD_GROUPS")
        if groups:  # S178: all members, so the solute-rich and all-dry rules of the cap act on multi-member lots
            inp["matrix_groups"] = _known(sorted(groups), "FOOD_GROUP", None, sid=f"L:{eid}", row="ING_LEDGER:category")
        return inp, code

    @staticmethod
    def _bindings(event_id: str, inp: Mapping[str, dict]) -> list[RA.ConditionBinding]:
        out = []
        sc = SourceClass.STRUCTURAL_RECIPE
        for name in ("duration", "medium", "lid_state", "start_mode", "piece_size_class", "matrix_class"):
            x = inp[name]
            if x["status"] == "UNKNOWN":
                continue
            unit = RA.INPUT_SPECS[name].unit
            out.append(RA.ConditionBinding(event_id, name, x["value"], "EVT", event_id, sc, unit))
        d, t = inp["duration"], inp["temperature_profile"]
        if t["status"] != "UNKNOWN" and d["status"] == "MEASURED" and d["value"] > 0:
            lo, hi = t["value"] if isinstance(t["value"], tuple) else (t["value"], t["value"])
            seg = RA.ProfileSegment(Fraction(0), d["value"], lo, hi)
            out.append(RA.ConditionBinding(event_id, "temperature_profile", (seg,), "EVT", event_id, sc, "min|degC"))
        return out
