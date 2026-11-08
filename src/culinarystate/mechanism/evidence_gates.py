"""Evidence gates for the router demo (S176, lane L-ROUTER). NON_CITABLE, DEMO_ONLY, AI_DRAFTED, PROPOSED_PILOT.

Two screens that run BEFORE the G0 evidence pre-check of the unchanged Step 23a engine. They only ever narrow the
route; neither can create or upgrade one (``DIRECT`` -> weaker, never the reverse). Scientific 23b stays BLOCKED.

1. Target-presence screen (nutrient targets only). Is the nutrient there at all in what the process acts on?
   - A lot member is the ING of an ingredient line. It maps to its rank-1 SR Legacy proposal in
     ``registry/ing_sr_legacy_match_draft_v1.csv`` only when that proposal is band HIGH or MEDIUM (an unmatched / LOW
     member has UNKNOWN identity). The identity is NOT taken as certain: every HIGH / MEDIUM candidate of rank 2-3
     whose match score is within ``identity_score_margin`` of the rank-1 score is a plausible alternative (the
     matcher could not rule it out: "pepper" has black pepper at rank 1 and sweet red pepper 0.12 below). The SR
     values come from the derived table ``registry/ing_sr_target_content_draft_v1.csv`` (built by
     ``tools/build_target_content_table.py`` from SR Legacy, public domain), so the demo needs no ``data/raw`` at
     run time; ``source="sr"`` reads SR Legacy directly.
   - Member state over the plausible candidates: PRESENT if every one has an SR value >= the floor; ABSENT if every
     one has a known SR value < the floor; UNKNOWN if any value is missing (UNKNOWN is never 0), the candidates
     disagree (identity ambiguity), the member is unmatched, or its identity is unknown (a lot root with no linked
     ingredient). ABSENT is a negative claim, so it needs every plausible identity to agree.
   - Lot state: PRESENT if >= 1 member is PRESENT; ABSENT only if EVERY member is ABSENT (no member of unknown
     identity); otherwise UNKNOWN. ABSENT -> the item routes NOT_APPLICABLE with reason ``TARGET_ABSENT``;
     UNKNOWN keeps routing and adds ``TARGET_PRESENCE_UNKNOWN``. A target with no floor row is NOT_SCREENED.
   - The floor is a PROPOSED_PILOT screening value in ``registry/target_presence_floor_v1_PROPOSED.csv`` (unsigned,
     a human decision). It is a screen on MEASURED composition (SR Legacy, public domain). It is never emitted as
     a number about the user's food and it is not a chemistry threshold.
2. Lot-context gate. Measured retention (EVD) is for a food cooked as itself. DIRECT / BRACKETING stands only when
   the lot the process acts on has that food as its sole member. If the lot is merged (>= 2 members, or a member
   of unknown identity) the pre-check is withheld: reason ``MERGED_LOT_CONTEXT``, and the engine applies its own
   order to the rest (in the demo, with no reviewed mechanism: UNKNOWN). The EVD rows stay visible as
   ``evidence_not_applied``.

Every gate output carries codes only (no recipe text). Lot membership comes from the Rung A event graph lineage.
"""
from __future__ import annotations

import csv
import functools
import hashlib
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

VERSION = "evidence-gates-0.1.0-draft"
STATUS = "AI_DRAFTED_PROPOSED_PILOT_UNSIGNED"
ROOT = Path(__file__).resolve().parents[3]
FLOOR_PATH = ROOT / "registry" / "target_presence_floor_v1_PROPOSED.csv"
MATCH_PATH = ROOT / "registry" / "ing_sr_legacy_match_draft_v1.csv"
TABLE_PATH = ROOT / "registry" / "ing_sr_target_content_draft_v1.csv"
SR_RELEASE = "USDA_SR_LEGACY_2018_04"
TABLE_COLUMNS = ("ing_id", "candidate_rank", "fdc_id", "confidence_band", "match_score", "nutrient_key", "unit",
                 "amount_per_100g", "source_release")
USABLE_BANDS = ("HIGH", "MEDIUM")

PRESENT, ABSENT, UNKNOWN, NOT_SCREENED = "PRESENT", "ABSENT", "UNKNOWN", "NOT_SCREENED"
SINGLE_MEMBER, MERGED, NO_LOT = "SINGLE_MEMBER", "MERGED", "NO_LOT"
NOT_APPLICABLE = "NOT_APPLICABLE"
R_TARGET_ABSENT = "TARGET_ABSENT"
R_PRESENCE_UNKNOWN = "TARGET_PRESENCE_UNKNOWN"
R_MERGED = "MERGED_LOT_CONTEXT"
GATE_REASONS = (R_TARGET_ABSENT, R_PRESENCE_UNKNOWN, R_MERGED)
# route strength used by the never-upgrade property (higher = stronger claim); NOT_APPLICABLE is outside the ladder
ROUTE_STRENGTH = {"DIRECT": 5, "INTERPOLATE": 4, "SIMULATE": 3, "QUALITATIVE": 2, "ASK": 1, "UNKNOWN": 0}


class GateError(ValueError):
    """A gate registry is malformed (never a verdict)."""


# ----------------------------------------------------------------------------- registries
@dataclass(frozen=True)
class Floor:
    svar_id: str
    name: str
    nutrient_key: str            # key of lotstate.sr_legacy.NUTRIENT_IDS
    unit: str
    value: Fraction              # per 100 g edible portion, SR Legacy
    status: str
    margin: Fraction = Fraction(0)   # identity_score_margin: rank 2-3 candidates this close to rank 1 are plausible


def read_floors(path: Path = FLOOR_PATH) -> dict[str, Floor]:
    from culinarystate.lotstate.sr_legacy import NUTRIENT_IDS, NUTRIENT_UNITS
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


# ING id -> ((fdc_id, band, match score), ...), rank 1 first; HIGH / MEDIUM candidates of rank 1-3 only
Candidates = Mapping[str, tuple[tuple[int, str, Fraction], ...]]


def read_candidates(path: Path = MATCH_PATH) -> dict[str, tuple[tuple[int, str, Fraction], ...]]:
    """Usable candidates per ING. An ING is present only when its rank-1 proposal is HIGH / MEDIUM; its entry then holds
    rank 1 and every HIGH / MEDIUM candidate of rank 2-3, in rank order."""
    rows: dict[str, list[tuple[int, int, str, Fraction]]] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["fdc_id"] != "" and r["rank"] in ("1", "2", "3") and r["confidence_band"] in USABLE_BANDS:
                rows.setdefault(r["ing_id"], []).append(
                    (int(r["rank"]), int(r["fdc_id"]), r["confidence_band"], Fraction(r["score"])))
    return {ing: tuple((f, band, sc) for _, f, band, sc in sorted(c)) for ing, c in rows.items()
            if min(c)[0] == 1}


def read_top1(path: Path = MATCH_PATH) -> dict[str, tuple[int, str]]:
    """ING id -> (fdc_id, band) of the usable rank-1 proposal."""
    return {ing: (c[0][0], c[0][1]) for ing, c in read_candidates(path).items()}


def read_sr_values(sr_dir: Path, fdc_ids: Iterable[int], keys: Iterable[str]) -> dict[tuple[int, str], Fraction]:
    """SR Legacy per-100 g values for the wanted foods and nutrient keys. A missing row is absent (UNKNOWN, not 0)."""
    from culinarystate.lotstate.intervals import frac
    from culinarystate.lotstate.sr_legacy import NUTRIENT_IDS
    wanted_f = set(fdc_ids)
    want: dict[int, list[tuple[str, int]]] = {}
    for key in set(keys):
        for rank, nid in enumerate(NUTRIENT_IDS[key][0]):
            want.setdefault(nid, []).append((key, rank))
    best: dict[tuple[int, str], tuple[int, Fraction]] = {}
    with (Path(sr_dir) / "food_nutrient.csv").open(newline="", encoding="utf-8") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        i_f, i_n, i_a = head.index("fdc_id"), head.index("nutrient_id"), head.index("amount")
        for row in rd:
            if not row[i_n].isdigit() or int(row[i_n]) not in want or not row[i_a]:
                continue
            f = int(row[i_f])
            if f not in wanted_f:
                continue
            for key, rank in want[int(row[i_n])]:
                cur = best.get((f, key))
                if cur is None or rank < cur[0]:
                    best[(f, key)] = (rank, frac(row[i_a]))
    return {k: v[1] for k, v in best.items()}


def build_table_rows(cands: Candidates, values: Mapping[tuple[int, str], Fraction],
                     keys: Iterable[str]) -> list[dict[str, str]]:
    """Rows of the derived content table: one per (usable candidate of an ING) x nutrient key. An SR food with no value
    for the nutrient gets an EMPTY amount (UNKNOWN, never 0)."""
    from culinarystate.lotstate.sr_legacy import NUTRIENT_UNITS
    rows = []
    for ing in sorted(cands):
        for rank, (fdc, band, score) in enumerate(cands[ing], 1):
            for key in sorted(set(keys)):
                v = values.get((fdc, key))
                rows.append({"ing_id": ing, "candidate_rank": str(rank), "fdc_id": str(fdc), "confidence_band": band,
                             "match_score": _dec(score), "nutrient_key": key, "unit": NUTRIENT_UNITS[key],
                             "amount_per_100g": "" if v is None else _dec(v), "source_release": SR_RELEASE})
    return rows


def _dec(v: Fraction) -> str:
    """Exact decimal text of an SR amount; refuses an amount that is not a terminating decimal."""
    from decimal import Decimal
    text = format((Decimal(v.numerator) / Decimal(v.denominator)).normalize(), "f")
    if Fraction(text) != v:
        raise GateError("an SR amount is not a terminating decimal")
    return text


def read_table(path: Path = TABLE_PATH) -> tuple[dict[str, tuple[tuple[int, str, Fraction], ...]],
                                                 dict[tuple[int, str], Fraction]]:
    """(candidates per ING, SR values by (fdc_id, nutrient key)). An empty amount stays absent (UNKNOWN)."""
    rows: dict[str, dict[int, tuple[int, str, Fraction]]] = {}
    values: dict[tuple[int, str], Fraction] = {}
    with Path(path).open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["confidence_band"] not in USABLE_BANDS:
                raise GateError("the content table holds usable-band rows only")
            fdc = int(r["fdc_id"])
            rows.setdefault(r["ing_id"], {})[int(r["candidate_rank"])] = (fdc, r["confidence_band"],
                                                                          Fraction(r["match_score"]))
            if r["amount_per_100g"] != "":
                values[(fdc, r["nutrient_key"])] = Fraction(r["amount_per_100g"])
    cands = {ing: tuple(c[k] for k in sorted(c)) for ing, c in rows.items()}
    if any(1 not in rows[ing] for ing in rows):
        raise GateError("every ING in the content table needs its rank-1 row")
    return cands, values


def code_key(svar_id: str) -> str:
    """Report key for an SVAR id (counts-only reports allow [A-Za-z0-9_] keys)."""
    return svar_id.replace("-", "__")


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ----------------------------------------------------------------------------- presence screen
class TargetPresenceScreen:
    """Member and lot presence of a target nutrient, from measured SR Legacy composition."""

    def __init__(self, floors: Mapping[str, Floor], cands: Candidates,
                 values: Mapping[tuple[int, str], Fraction]) -> None:
        self.floors, self.cands, self.values = dict(floors), dict(cands), dict(values)

    def screened(self, svar_id: str | None) -> bool:
        return svar_id in self.floors

    def plausible(self, svar_id: str, ing_id: str | None) -> tuple[int, ...]:
        """SR foods the ING may be: rank 1 and the HIGH / MEDIUM candidates within the identity margin of its score."""
        cs = self.cands.get(ing_id) if ing_id else None
        if not cs:
            return ()
        return tuple(f for f, _, sc in cs if sc >= cs[0][2] - self.floors[svar_id].margin)

    def member_state(self, svar_id: str, ing_id: str | None) -> str:
        fl = self.floors[svar_id]
        foods = self.plausible(svar_id, ing_id)
        if not foods:
            return UNKNOWN                          # no usable (HIGH / MEDIUM) SR identity
        vals = [self.values.get((f, fl.nutrient_key)) for f in foods]
        if any(v is None for v in vals):
            return UNKNOWN                          # SR has no value: UNKNOWN is never 0
        if all(v >= fl.value for v in vals):
            return PRESENT
        if all(v < fl.value for v in vals):
            # S175 interim (FINAL-SCI #6): ABSENT is a negative claim; require a HIGH-band rank-1 identity.
            # MEDIUM-only identities (~67 % plausible in the L-LOT audit) stay UNKNOWN.
            cs = self.cands.get(ing_id) or ()
            return ABSENT if cs and cs[0][1] == "HIGH" else UNKNOWN
        return UNKNOWN                              # plausible identities disagree

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
        return TargetPresenceScreen({**self.floors, svar_id: new}, self.cands, self.values)

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
        cands, values = read_table(Path(table_path))
    else:
        cands = read_candidates(Path(match_path))
        values = read_sr_values(Path(sr_dir), {f for c in cands.values() for f, _, _ in c},
                                {f.nutrient_key for f in floors.values()})
    return TargetPresenceScreen(floors, cands, values)


# ----------------------------------------------------------------------------- lot membership from the event graph
@dataclass(frozen=True)
class LotMembers:
    """Members of one lot: distinct linked ING ids and the number of roots of unknown identity."""

    ings: frozenset
    unknown: int = 0

    @property
    def sole(self) -> str | None:
        return next(iter(self.ings)) if len(self.ings) == 1 and self.unknown == 0 else None


def _attr(claims, name: str):
    return next((c.value for c in claims if c.field == name), None)


def lot_members(graph) -> dict[str, LotMembers]:
    """Entity id -> members (lineage through parents). A root without a linked ingredient is a member of unknown
    identity (e.g. a named mixture that no earlier step produces)."""
    ents = {e.entity_id: e for e in graph.entities}
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
        for p in e.parent_entity_ids:
            m = walk(p, depth + 1)
            ings |= m.ings
            unknown += m.unknown
        if not e.parent_entity_ids and not own:
            unknown += 1
        memo[eid] = LotMembers(frozenset(ings), unknown)
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

    def as_item(self) -> dict[str, Any]:
        return {"presence": self.presence, "lot_context": self.lot_context}


class EvidenceGates:
    def __init__(self, screen: TargetPresenceScreen, *, presence: bool = True, context: bool = True,
                 provenance: Mapping[str, Any] | None = None) -> None:
        self.screen, self.presence_on, self.context_on = screen, presence, context
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
            from culinarystate.lotstate.sr_legacy import default_dir
            sr = str(Path(sr_dir) if sr_dir else default_dir(ROOT))
        screen = _screen(str(floor_path), source, str(table_path), str(match_path), sr)
        prov = {"version": VERSION, "status": STATUS, "floor_file_sha256": _sha(floor_path), "content_source": source,
                "content_table_sha256": _sha(table_path) if source == "table" else "NOT_USED",
                "match_registry_sha256": _sha(match_path), "sr_source": SR_RELEASE,
                "floors": {code_key(k): {"value": float(f.value), "identity_score_margin": float(f.margin), "unit": f.unit,
                                         "status": f.status}
                           for k, f in screen.floors.items()}}
        return cls(screen, presence=presence, context=context, provenance=prov)

    def describe(self) -> dict[str, Any]:
        return {**self.provenance, "enabled": True, "presence_gate": self.presence_on, "context_gate": self.context_on}

    def evaluate(self, *, svar_id: str, ing: str | None, raw_precheck: str, lots: Sequence[LotMembers]) -> GateResult:
        ings = {i for lm in lots for i in lm.ings}
        unknown = sum(lm.unknown for lm in lots)
        presence = self.screen.lot_state(svar_id, ings, unknown) if self.presence_on else NOT_SCREENED
        if ing is None or not lots:
            context = NO_LOT
        else:
            context = SINGLE_MEMBER if all(lm.sole == ing for lm in lots) else MERGED
        reasons: list[str] = []
        if presence == ABSENT:
            return GateResult(presence, context, (R_TARGET_ABSENT,), "NONE", True, raw_precheck != "NONE")
        if presence == UNKNOWN:
            reasons.append(R_PRESENCE_UNKNOWN)
        final, withheld = raw_precheck, False
        if self.context_on and raw_precheck != "NONE" and context == MERGED:
            reasons.insert(0, R_MERGED)
            final, withheld = "NONE", True
        return GateResult(presence, context, tuple(reasons), final, False, withheld)
