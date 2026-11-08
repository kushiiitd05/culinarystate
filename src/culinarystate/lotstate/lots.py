"""Lot assembly: ingredient lines + state-graph lineage -> per-lot records (Step 3 inputs, Step 4 flags).

A lot is a state-graph entity (INGREDIENT_LOT, MIXTURE or INTERMEDIATE; Step 18 / Rung A graph, replay-checked) or the
recipe-level ``RECIPE_POOL`` (all ingredient lines together, a bookkeeping lot, not a physical one).

Members of a graph lot are the INGREDIENT_LOT ancestors of the entity (lineage through parents). Each member carries
a SHARE interval of its root lot (1 through transforms and merges; [0, 1] through SPLIT / RESERVE / REMAINDER /
DISCARD / RECOMBINE unless the allocation states an exact mass fraction). The member mass is the ingredient-line mass
of the root's ING (summed over lines of that ING) times the share; when the graph holds more than one lot of the same
ING the line mass is shared as [0, total]. No line for the ING, or any unusable line, makes the mass UNKNOWN.
Quantities in the instruction text are not used (the replay already carries them); only ingredient lines give masses.

Composition is of the members AS LISTED (see composition.py). Records carry codes, ids and numbers only: no recipe
text. Everything is MODEL_DERIVED / NON_CITABLE.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Mapping, Sequence

from culinarystate.extraction.interfaces import SourceText
from culinarystate.quantity.rc2_grounding import GroundingContext
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.recipes.ledgers import LOCALE
from culinarystate.state_graph.event_adapter import adapt_event_graph

from . import values as V
from .composition import (AwConfig, CompositionConfig, Member, composition, solute_load, water_activity)
from .intervals import frac
from .line_grams import LineResult, resolve_line
from .linker import LineLinker
from .ph import PhRegistry, ph_record
from .sr_legacy import SRLegacy

LAYER_NOTE = "REFERENCE_DATA_MODEL_DERIVED"
ALLOC_PARTIAL = frozenset({"SPLIT", "RESERVE", "REMAINDER", "DISCARD", "RECOMBINE"})
ZERO_ONE = (Fraction(0), Fraction(1))


@dataclass(frozen=True)
class BuilderConfig:
    min_band: str = "MEDIUM"
    aw: AwConfig = AwConfig()


@dataclass
class LineInfo:
    idx: int
    ing_id: str | None
    fdc_id: int | None
    band: str
    result: LineResult

    def to_json(self, recipe_id: str, family: str) -> dict:
        return {**self.result.to_json(), "recipe_id": recipe_id, "source_family": family, "line": self.idx,
                "ing_id": self.ing_id, "link": "LINKED" if self.ing_id else "UNLINKED", "sr_band": self.band,
                **({"fdc_id": self.fdc_id} if self.fdc_id is not None else {})}


def _share_mul(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    return a[0] * b[0], a[1] * b[1]


def _known_fraction(alloc) -> tuple[Fraction, Fraction]:
    c = getattr(alloc, "fraction", None)
    if alloc.kind in ("SPLIT", "RESERVE", "REMAINDER", "DISCARD") and alloc.basis == "MASS" and c is not None \
            and getattr(c, "status", "") == "KNOWN" and c.value is not None:
        v = c.value
        try:
            lo, hi = (frac(v[0]), frac(v[1])) if isinstance(v, tuple) else (frac(v), frac(v))
        except (ValueError, TypeError):
            return ZERO_ONE
        if 0 <= lo <= hi <= 1:
            return lo, hi
    return ZERO_ONE


class LotStateBuilder:
    def __init__(self, *, sr: SRLegacy, top1: Mapping[str, Mapping], ing_names: Mapping[str, str], linker: LineLinker,
                 schema: Mapping, rung, ph_registry: PhRegistry | None = None, cfg: BuilderConfig = BuilderConfig()):
        self.sr, self.top1, self.ing_names, self.linker = sr, top1, ing_names, linker
        self.schema, self.rung, self.ph, self.cfg = schema, rung, ph_registry, cfg
        self.ccfg = CompositionConfig(min_band=cfg.min_band)
        self._memo: dict[tuple, tuple[dict, dict, dict]] = {}

    # ------------------------------------------------------------ lines
    def lines(self, rec: Mapping) -> list[LineInfo]:
        fam = rec.get("source_family")
        loc = LOCALE.get(fam)
        ctx = GroundingContext(source_metadata=D.SOURCE_META, locale=loc, locale_metadata=D.LOCALE_META if loc else None)
        out: list[LineInfo] = []
        if fam == "FOODCOM":
            ex = rec.get("extra") or {}
            parts = list(ex.get("ingredient_parts") or [])
            q = list(ex.get("q_raw") or [])
            aligned = ex.get("q_len") == ex.get("p_len")
            for i, part in enumerate(parts):
                ing = self.linker.link_part(part)
                t = self.top1.get(ing) if ing else None
                qt = q[i] if aligned and i < len(q) and q[i] else ""
                text = f"{qt} {part}".strip() if aligned else part
                res = resolve_line(text, schema=self.schema, context=ctx, sr=self.sr, fdc_id=t["fdc_id"] if t else None,
                                   band=t["band"] if t else "NONE", unit_stripped_source=True, qp_mismatch=not aligned)
                out.append(LineInfo(i, ing, t["fdc_id"] if t else None, t["band"] if t else "NONE", res))
            return out
        for i, line in enumerate(rec.get("ingredient_lines") or []):
            if not isinstance(line, str) or not line.strip():
                continue
            ing = self.linker.link_line(line)
            t = self.top1.get(ing) if ing else None
            res = resolve_line(line, schema=self.schema, context=ctx, sr=self.sr, fdc_id=t["fdc_id"] if t else None,
                               band=t["band"] if t else "NONE")
            out.append(LineInfo(i, ing, t["fdc_id"] if t else None, t["band"] if t else "NONE", res))
        return out

    def _ing_mass(self, lines: Sequence[LineInfo]) -> dict[str, tuple[tuple[Fraction, Fraction] | None, str]]:
        """ING id -> (summed usable grams or None, basis string) over the recipe's lines of that ING."""
        acc: dict[str, list[LineInfo]] = {}
        for li in lines:
            if li.ing_id:
                acc.setdefault(li.ing_id, []).append(li)
        out = {}
        for ing, lis in acc.items():
            gs = [li.result.usable_grams(self.cfg.min_band) for li in lis]
            bases = sorted({li.result.basis for li in lis if li.result.basis != V.BASIS_UNKNOWN})
            if any(g is None for g in gs):
                out[ing] = (None, V.BASIS_UNKNOWN)
            else:
                out[ing] = ((sum((g[0] for g in gs), Fraction(0)), sum((g[1] for g in gs), Fraction(0))), "+".join(bases))
        return out

    # ------------------------------------------------------------ lots
    def _member(self, ing: str | None, mass, basis: str) -> Member:
        t = self.top1.get(ing) if ing else None
        return Member(ing, t["fdc_id"] if t else None, t["band"] if t else "NONE", mass,
                      basis if mass is not None else V.BASIS_UNKNOWN)

    def _lot_values(self, members: Sequence[Member]) -> tuple[dict, dict, dict]:
        key = tuple((m.ing_id, m.fdc_id, m.band, m.mass, m.mass_basis) for m in members)
        hit = self._memo.get(key)
        if hit is None:
            comp = composition(members, self.sr, self.ccfg)
            sol = solute_load(members, self.sr, self.ccfg)
            aw = water_activity(sol, self.cfg.aw)
            hit = (comp, sol, aw)
            if len(self._memo) < 200000:
                self._memo[key] = hit
        return hit

    def _lot_record(self, recipe_id: str, family: str, lot_id: str, kind: str, lifecycle: str, is_leaf: bool,
                    members: Sequence[Member], extra_members: Sequence[dict], replay_status: str = "NONE") -> dict:
        comp, sol, aw = self._lot_values(members)
        ph = ph_record([(m.ing_id, self.ing_names.get(m.ing_id or "")) for m in members], self.ph)
        c = {k: comp[k] for k in ("kind", "members_total", "members_usable", "match_floor")}
        c["nutrients"] = {k: V.compact(v) for k, v in comp["nutrients"].items()}
        c["total_mass_g"] = V.compact(comp["total_mass_g"])
        c["provenance"] = next((v["provenance"] for v in comp["nutrients"].values()), None)
        return {"recipe_id": recipe_id, "source_family": family, "lot_id": lot_id, "kind": kind, "lifecycle": lifecycle,
                "is_leaf": is_leaf, "replay_status": replay_status, "layer": LAYER_NOTE, "labels": list(V.LABELS), "members": list(extra_members),
                "composition": c, "solute_load": {k: V.compact(v) for k, v in sol.items()},
                "water_activity": V.compact(aw), "ph": {k: ph[k] for k in ("type", "mask", "unit", "basis", "flags",
                                                                           "member_ranges")}}

    def _graph_lots(self, rec: Mapping, lines: Sequence[LineInfo]) -> tuple[list[dict], dict]:
        fam, rid = rec.get("source_family"), rec["recipe_id"]
        steps = [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]
        stats = {"graph_attempted": 0, "graph_failed": 0, "replay_status": "NONE"}
        if not steps:
            return [], stats
        stats["graph_attempted"] = 1
        try:
            source = SourceText.from_raw("LOT", "\n".join(steps))
            res = self.rung.run(source, self.rung.config(locale=LOCALE.get(fam)), schema=self.schema)
            adapted = adapt_event_graph(source, res.graph, groundings=res.quantities, recomputers=self.rung.recomputers())
            replay = adapted.replay()
            stats["replay_status"] = replay.status
            g = res.graph
        except Exception:  # noqa: BLE001 - counted, never message
            stats["graph_failed"] = 1
            return [], stats
        ents = {e.entity_id: e for e in g.entities}
        order = [e.entity_id for e in g.entities]
        allocs: dict[tuple[str, str], Any] = {}
        for a in g.allocations:
            allocs.setdefault((a.parent_entity_id, a.child_entity_id), a)
        is_parent = {p for e in g.entities for p in e.parent_entity_ids}
        ing_of = {e.entity_id: next((c.value for c in e.attributes if c.field == "ingredient_id"), None)
                  for e in g.entities}
        roots_of_ing: dict[str, int] = {}
        for eid, e in ents.items():
            if not e.parent_entity_ids and e.entity_type == "INGREDIENT_LOT" and ing_of[eid]:
                roots_of_ing[ing_of[eid]] = roots_of_ing.get(ing_of[eid], 0) + 1
        ing_mass = self._ing_mass(lines)
        memo: dict[str, dict[str, tuple[Fraction, Fraction]]] = {}

        def shares(eid: str, depth: int = 0) -> dict[str, tuple[Fraction, Fraction]]:
            if eid in memo:
                return memo[eid]
            e = ents[eid]
            if not e.parent_entity_ids or depth > 400:
                memo[eid] = {eid: (Fraction(1), Fraction(1))}
                return memo[eid]
            acc: dict[str, tuple[Fraction, Fraction]] = {}
            for p in e.parent_entity_ids:
                if p not in ents:
                    continue
                a = allocs.get((p, eid))
                f = _known_fraction(a) if a is not None and a.kind in ALLOC_PARTIAL else (Fraction(1), Fraction(1))
                for root, s in shares(p, depth + 1).items():
                    s2 = _share_mul(s, f)
                    prev = acc.get(root)
                    acc[root] = s2 if prev is None else (prev[0] + s2[0], prev[1] + s2[1])
            memo[eid] = acc
            return acc

        lots = []
        for eid in order:
            e = ents[eid]
            members, extra = [], []
            for root, (s_lo, s_hi) in sorted(shares(eid).items()):
                ing = ing_of.get(root) if ents[root].entity_type == "INGREDIENT_LOT" else None
                mass, basis = (None, V.BASIS_UNKNOWN)
                if ing and ing in ing_mass and ing_mass[ing][0] is not None:
                    (m_lo, m_hi), basis = ing_mass[ing]
                    if roots_of_ing.get(ing, 1) > 1:
                        m_lo = Fraction(0)
                    mass = (m_lo * min(s_lo, Fraction(1)), m_hi * min(s_hi, Fraction(1)))
                mem = self._member(ing, mass, basis)
                members.append(mem)
                extra.append({"root": root, "ing_id": ing, "share": [float(s_lo), float(s_hi)], "sr_band": mem.band,
                              "fdc_id": mem.fdc_id, "mass_basis": mem.mass_basis,
                              **({"mass_g": [float(mass[0]), float(mass[1])]} if mass else {})})
            lots.append(self._lot_record(rid, fam, f"{rid}#{eid}", e.entity_type, e.lifecycle, eid not in is_parent,
                                         members, extra, stats["replay_status"]))
        return lots, stats

    def _pool_lot(self, rec: Mapping, lines: Sequence[LineInfo]) -> dict | None:
        if not lines:
            return None
        ing_mass = self._ing_mass(lines)
        members, extra = [], []
        for ing, (mass, basis) in sorted(ing_mass.items()):
            mem = self._member(ing, mass, basis)
            members.append(mem)
            extra.append({"ing_id": ing, "sr_band": mem.band, "fdc_id": mem.fdc_id, "mass_basis": mem.mass_basis,
                          **({"mass_g": [float(mass[0]), float(mass[1])]} if mass else {})})
        for li in lines:
            if not li.ing_id:                                   # an unlinked line is a member of unknown identity
                members.append(Member(None, None, "NONE", None, V.BASIS_UNKNOWN))
                extra.append({"ing_id": None, "unlinked_line": li.idx})
        return self._lot_record(rec["recipe_id"], rec.get("source_family"), f"{rec['recipe_id']}#POOL", "RECIPE_POOL",
                                "POOL", True, members, extra)

    def build_recipe(self, rec: Mapping) -> dict:
        """{"lines": [...], "lots": [...], "stats": {...}} for one recipe record (no text, ids and numbers only)."""
        fam, rid = rec.get("source_family"), rec["recipe_id"]
        lines = self.lines(rec)
        lots, stats = self._graph_lots(rec, lines)
        pool = self._pool_lot(rec, lines)
        if pool:
            lots.append(pool)
        ex = rec.get("extra") or {}
        stats["foodcom_qp_mismatch"] = int(fam == "FOODCOM" and ex.get("q_len") != ex.get("p_len"))
        return {"lines": [li.to_json(rid, fam) for li in lines], "lots": lots, "stats": stats}
