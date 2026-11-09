"""Kleene three-valued mechanism screen over lot state (S178 lane MECH, T5-C02-R2). AI_DRAFTED, NON_CITABLE, T6.

For every process event that has a physical-layer record (Layer 1 TEXT_STATED heat or non-heat binder record) and for every
lot the event consumes (an entity of the Rung A event graph; its members are the linked ING ids of its lineage), the screen
says POSSIBLE / NOT_POSSIBLE / UNKNOWN for each mechanism of the screen subset of ``registry/mech_entries_draft_v1.jsonl``,
separately in four layer views: L1 (Layer 1 + physical / process definitions + lineage + measured reference composition)
and L2:GENTLE / L2:TYPICAL / L2:INTENSE (the same plus that bracket of the Layer 2 SCENARIO record). Views are never mixed.

Rules (see ``mech_k3`` and ``mech_inputs``):
- conjuncts = the entry's preconditions, its NECESSARY gates (through a declared witness) and its inhibitors (as
  "inhibitor not acting"), in the entry's ``evaluation_order``; MODULATING gates never gate (rule M-1);
- Kleene AND: FALSE decides, all TRUE gives POSSIBLE, anything else UNKNOWN; an UNKNOWN input is never read as FALSE;
- NOT_POSSIBLE only from an admissible FALSE (measured SR zeros for every member), never from an L2 value;
- a member-scoped entry (cut-triggered enzymes) is evaluated per candidate member and the lot verdict is the K3 OR;
- every verdict carries its view, a reason code, the deciding item and whether L2 support was needed;
- interaction edges are created only between two DIFFERENT members of the SAME lot, only with a mechanism id, from the
  member facts the verdict used (never from co-occurrence, PMI or learned weights); tier T6, AI_DRAFTED.

While every entry is AI_DRAFTED / CANDIDATE the screen is an engineering diagnostic (SSOT v16 DRAFT 285.12): it never feeds a
route, a QUALITATIVE output or a number. Counts only leave this module; recipe text never does.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from culinarystate.mechanism import evidence_gates as EG
from culinarystate.mechanism import mech_entries as ME
from culinarystate.mechanism import mech_inputs as MI
from culinarystate.mechanism import mech_k3 as K

SCREEN_VERSION = "mech-screen-0.1.0-draft"
STATUS = "AI_DRAFTED_T6_DIAGNOSTIC_NON_CITABLE"
VIEW_DEPENDENT = frozenset({"tboil_surface", "denaturing_driver"})
VCHAR = {K.POSSIBLE: "P", K.NOT_POSSIBLE: "N", K.UNDECIDED: "U"}
NH_FAMILIES = ("COOLING", "SEPARATION", "FERMENT_LEAVEN", "PRESERVATION", "MECHANICAL_CUT", "MECHANICAL_MIX", "RESTING",
               "STORAGE")
STORE_PROC = "PROC-000113"


def view_key(view: str) -> str:
    return view.replace(":", "_")


# ----------------------------------------------------------------------------- edges
@dataclass(frozen=True)
class Edge:
    kind: str                    # REACTANT_PAIR | CONDITION_SUPPLIER
    mechanism_key: str
    supplier: str                # ING id (member of the lot)
    receiver: str                # ING id (another member of the same lot)
    phase: str
    direction: str               # ENABLES | INCREASES | INHIBITS
    view: str
    window: str
    created_from: tuple[str, ...]
    tier: str = "T6_AI_DRAFTED"
    review_status: str = "AI_DRAFTED"


# ----------------------------------------------------------------------------- screen
class MechScreen:
    def __init__(self, entries: Sequence[Mapping[str, Any]]) -> None:
        subset = ME.screen_entries(entries)
        if not subset:
            raise ValueError("no screen-subset entries")
        self.entries = sorted(((x["mech"]["mechanism_key"], x["mech"], x["screen_binding"]) for x in subset),
                              key=lambda t: t[0])
        self.keys = tuple(k for k, _, _ in self.entries)
        for k, _, b in self.entries:
            for ik in b["evaluation_order"]:
                if b["items"][ik]["evaluator"] not in MI.EVALUATORS:
                    raise ValueError(f"{k}: unknown evaluator {b['items'][ik]['evaluator']}")

    def _conjuncts(self, b: Mapping, lot: MI.LotCtx, member: MI.LotMember | None, ev: MI.EventCtx, view: str,
                   l1_cache: dict) -> list[K.Conjunct]:
        out = []
        for ik in b["evaluation_order"]:
            it = b["items"][ik]
            if view != "L1" and it["evaluator"] not in VIEW_DEPENDENT:
                out.append(l1_cache[(id(member), ik)])
                continue
            c = MI.evaluate(it["evaluator"], lot, member, ev, view, it["args"], ik, it["role"])
            if view == "L1":
                l1_cache[(id(member), ik)] = c
            out.append(c)
        return out

    def screen_lot(self, lot: MI.LotCtx, ev: MI.EventCtx) -> dict[str, dict[str, K.Verdict]]:
        """mechanism key -> view -> Verdict."""
        res: dict[str, dict[str, K.Verdict]] = {}
        for key, _, b in self.entries:
            scope = b["member_scope"]
            cands = ([m for m in lot.members if scope in m.info.classes] or [None]) if scope else [None]
            dependent = any(b["items"][ik]["evaluator"] in VIEW_DEPENDENT for ik in b["evaluation_order"])
            cache: dict = {}
            per_view: dict[str, K.Verdict] = {}
            for view in K.VIEWS:
                if view != "L1" and not dependent:
                    per_view[view] = dataclasses.replace(per_view["L1"], view=view)
                    continue
                per = [K.combine(self._conjuncts(b, lot, m, ev, view, cache), view, b["flags"]) for m in cands]
                per_view[view] = K.k_or_verdicts(per, view)
            res[key] = per_view
        return res

    @staticmethod
    def edges(lot: MI.LotCtx, verdicts: Mapping[str, Mapping[str, K.Verdict]]) -> list[Edge]:
        out: list[Edge] = []
        mem = sorted(lot.members, key=lambda m: m.info.ing_id)
        for view in K.VIEWS:
            v = verdicts.get("MAILLARD_STRECKER_LUMPED", {}).get(view)
            if v is not None and v.verdict == K.POSSIBLE:
                amino = [m for m in mem if m.info.presence["protein"][0] == EG.PRESENT]
                carb = [m for m in mem if m.info.presence["sugars"][0] == EG.PRESENT]
                out += [Edge("REACTANT_PAIR", "MAILLARD_STRECKER_LUMPED", a.info.ing_id, c.info.ing_id, "AQUEOUS",
                             "ENABLES", view, "NO_SWITCH_DOSE_NOT_ASSESSED", ("protein_PRESENT_SR", "sugars_PRESENT_SR"))
                        for a in amino for c in carb if a.info.ing_id != c.info.ing_id]
            v = verdicts.get("CHLOROPHYLL_TO_PHEOPHYTIN", {}).get(view)
            if v is not None and v.verdict == K.POSSIBLE:
                acid = [m for m in mem if m.info.acid_class == "ACID"]
                green = [m for m in mem if "CHLOROPHYLL_TISSUE" in m.info.classes]
                out += [Edge("CONDITION_SUPPLIER", "CHLOROPHYLL_TO_PHEOPHYTIN", a.info.ing_id, g.info.ing_id, "AQUEOUS",
                             "INCREASES", view, "CV-013_MODULATING_BOUNDS_NOT_REPORTED",
                             ("acid_class_ACID_FDA_TABLE_DIAGNOSTIC", "CHLOROPHYLL_TISSUE"))
                        for a in acid for g in green if a.info.ing_id != g.info.ing_id]
            v = verdicts.get("PPO_ENZYMATIC_BROWNING", {}).get(view)
            if v is not None and v.verdict == K.UNDECIDED and v.reason == "FOREIGN_MEMBER_MAY_INHIBIT":
                acid = [m for m in mem if m.info.acid_class == "ACID"]
                ppo = [m for m in mem if "PPO_FRESH" in m.info.classes]
                out += [Edge("CONDITION_SUPPLIER", "PPO_ENZYMATIC_BROWNING", a.info.ing_id, p.info.ing_id, "AQUEOUS",
                             "INHIBITS", view, "INH01_EXTENT_UNKNOWN", ("acid_class_ACID_FDA_TABLE_DIAGNOSTIC", "PPO_FRESH"))
                        for a in acid for p in ppo if a.info.ing_id != p.info.ing_id]
        ids = {m.info.ing_id for m in lot.members}
        for e in out:
            if e.supplier not in ids or e.receiver not in ids or e.supplier == e.receiver:
                raise K.K3Error("edge outside its lot")
        return out


# ----------------------------------------------------------------------------- lineage from the event graph
def _attr(claims, name: str):
    return next((c.value for c in claims if c.field == name), None)


def lineage(graph, families: Mapping[str, str], hierarchy=None) -> dict[str, tuple[dict[str, tuple[bool, bool]], int]]:
    """entity id -> ({ING id: (heated before, cut before)}, roots of unknown identity). A member is heated / cut when an
    event that PRODUCED the entity or one of its ancestors on that member's path is a heat (``evidence_gates.prior_kind``)
    or a cut / disruptive event."""
    ents = {e.entity_id: e for e in graph.entities}
    flags: dict[str, tuple[bool, bool]] = {}
    for ev in graph.events:
        pid = _attr(ev.attributes, "proc_id")
        heat = EG.prior_kind(pid, hierarchy) == "HEAT"
        cut = families.get(pid) == "MECHANICAL_CUT" or pid in MI.DISRUPTIVE_PROCS
        for eid in ev.produces:
            h, c = flags.get(eid, (False, False))
            flags[eid] = (h or heat, c or cut)
    memo: dict[str, tuple[dict[str, tuple[bool, bool]], int]] = {}

    def walk(eid: str, depth: int = 0):
        if eid in memo:
            return memo[eid]
        e = ents.get(eid)
        if e is None or depth > 500:
            return {}, 1
        h0, c0 = flags.get(eid, (False, False))
        out: dict[str, tuple[bool, bool]] = {}
        unknown = 0
        own = _attr(e.attributes, "ingredient_id")
        if own:
            out[own] = (h0, c0)
        for p in e.parent_entity_ids:
            sub, u = walk(p, depth + 1)
            unknown += u
            for ing, (h, c) in sub.items():
                ph, pc = out.get(ing, (False, False))
                out[ing] = (ph or h or h0, pc or c or c0)
        if not e.parent_entity_ids and not own:
            unknown += 1
        memo[eid] = (out, unknown)
        return memo[eid]

    return {eid: walk(eid) for eid in ents}


def physical_family(pid: str | None, families: Mapping[str, str]) -> str | None:
    return "STORAGE" if pid == STORE_PROC else families.get(pid)


def event_ctx(event_id: str, pid: str | None, fam: str | None, l1_rec: Mapping | None, l2_rec: Mapping | None) -> MI.EventCtx:
    l1 = dict((l1_rec or {}).get("inputs") or {})
    scen = dict((l2_rec or {}).get("scenarios") or {}) if fam in MI.HEAT_FAMILIES else {}
    return MI.EventCtx(event_id, pid, fam, l1, scen, (l2_rec or {}).get("medium") if scen else None)


# ----------------------------------------------------------------------------- one recipe
@dataclass
class RecipeResult:
    rows: list[dict[str, Any]]
    counts: Counter


def screen_graph(recipe_id: str, family: str, graph, *, screen: MechScreen, catalog: MI.MemberCatalog,
                 families: Mapping[str, str], records: Mapping[str, Mapping[str, Mapping]], hierarchy=None,
                 rows: bool = True) -> RecipeResult:
    """``records``: layer name (L1, L2, NH_L1, NH_L2) -> event id -> record of this recipe."""
    cnt: Counter = Counter()
    out_rows: list[dict[str, Any]] = []
    lin = lineage(graph, families, hierarchy)
    for ev in graph.events:
        pid = _attr(ev.attributes, "proc_id")
        fam = physical_family(pid, families)
        cnt[("events", "graph")] += 1
        heat = fam in MI.HEAT_FAMILIES
        nh = fam in NH_FAMILIES
        if not (heat or nh):
            cnt[("events_not_screened_family", fam or "NONE")] += 1
            continue
        l1 = records.get("L1" if heat else "NH_L1", {}).get(ev.event_id)
        l2 = records.get("L2" if heat else "NH_L2", {}).get(ev.event_id)
        if l1 is None:
            cnt[("events_physical_record_missing", "L1_HEAT" if heat else "L1_NONHEAT")] += 1
            continue
        if l1.get("process_id") != pid:
            cnt[("exceptions", "PROCESS_ID_MISMATCH")] += 1
            continue
        cnt[("events", "screened_heat" if heat else "screened_nonheat")] += 1
        cnt[("l2_status", (l2 or {}).get("status") or "NO_L2_RECORD")] += 1
        ctx = event_ctx(ev.event_id, pid, fam, l1, l2)
        lots = [eid for eid in dict.fromkeys(ev.consumes) if eid in lin]
        if not lots:
            cnt[("events", "screened_without_lot")] += 1
        for eid in lots:
            mem, unknown = lin[eid]
            lot = MI.LotCtx(eid, MI.members_from(catalog, ((i, h, c) for i, (h, c) in mem.items())), unknown)
            cnt[("lots", "screened")] += 1
            cnt[("lots", "members")] += len(lot.members)
            cnt[("lots", "with_unlinked_member")] += 1 if unknown else 0
            cnt[("lots", "no_linked_member")] += 1 if not lot.members else 0
            verdicts = screen.screen_lot(lot, ctx)
            _count(cnt, family, "HEAT" if heat else "NONHEAT", fam, verdicts)
            for e in screen.edges(lot, verdicts):
                cnt[("edge", family, e.mechanism_key, e.kind, e.direction, view_key(e.view))] += 1
            if rows:
                out_rows.append(_row(recipe_id, family, ev.event_id, eid, pid, fam, lot, verdicts, screen.keys))
    return RecipeResult(out_rows, cnt)


def _count(cnt: Counter, family: str, eclass: str, pfam: str | None, verdicts: Mapping[str, Mapping[str, K.Verdict]]) -> None:
    for key, per in verdicts.items():
        l1 = per["L1"]
        for view, v in per.items():
            vk = view_key(view)
            cnt[("verdict", family, key, vk, v.verdict)] += 1
            cnt[("verdict_by_event_class", family, key, vk, eclass, v.verdict)] += 1
            cnt[("reason", family, key, vk, v.verdict, v.reason)] += 1
            if v.verdict == K.POSSIBLE:
                cnt[("possible_support_layer", family, key, vk, v.support_layer)] += 1
            if v.verdict == K.NOT_POSSIBLE:
                cnt[("not_possible_item", family, key, vk, v.item_key or "NONE")] += 1
            # invariants (must stay 0): an L2 view never excludes what L1 did not, and never loses an L1 POSSIBLE
            if view != "L1" and v.verdict == K.NOT_POSSIBLE and l1.verdict != K.NOT_POSSIBLE:
                cnt[("invariant_violation", "L2_EXCLUDED_WITHOUT_L1")] += 1
            if view != "L1" and l1.verdict == K.POSSIBLE and v.verdict != K.POSSIBLE:
                cnt[("invariant_violation", "L2_LOST_L1_POSSIBLE")] += 1
            if v.verdict == K.POSSIBLE and v.reason != K.R_ALL_TRUE:
                cnt[("invariant_violation", "POSSIBLE_WITHOUT_ALL_TRUE")] += 1
            if view != "L1" and v.verdict != l1.verdict:
                cnt[("l1_to_l2_change", family, key, vk, f"{l1.verdict}__TO__{v.verdict}")] += 1
        trip = tuple(per[f"L2:{b}"].verdict for b in K.BRACKETS)
        if len(set(trip)) > 1:
            cnt[("bracket_disagreement", family, key, "__".join(VCHAR[t] for t in trip))] += 1
        cnt[("by_process_family", family, key, pfam or "NONE", l1.verdict)] += 1


def _row(recipe_id, family, event_id, lot_id, pid, fam, lot, verdicts, keys) -> dict[str, Any]:
    v = {view_key(view): "".join(VCHAR[verdicts[k][view].verdict] for k in keys) for view in K.VIEWS}
    np_reason = {k: verdicts[k]["L1"].reason for k in keys if verdicts[k]["L1"].verdict == K.NOT_POSSIBLE}
    row = {"r": recipe_id, "fam": family, "e": event_id, "lot": lot_id, "p": pid, "pf": fam, "nm": len(lot.members),
           "nu": lot.n_unknown, "v": v}
    if np_reason:
        row["np"] = np_reason
    return row


# ----------------------------------------------------------------------------- record files
def read_part(path: Path | None, want: set[str]) -> tuple[dict[str, dict[str, Mapping]], set[str]]:
    """recipe id -> event id -> record, for the wanted recipes; and the set of recipe ids seen in the file."""
    out: dict[str, dict[str, Mapping]] = {}
    seen: set[str] = set()
    if path is None or not Path(path).exists():
        return out, seen
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            rid = r["recipe_id"]
            seen.add(rid)
            if rid in want:
                out.setdefault(rid, {})[r["event_id"]] = r
    return out, seen


def n_parts(d: Path | None) -> int:
    return len(sorted(Path(d).glob("part-*.jsonl"))) if d else 0


def dir_manifest_sha256(d: Path | None) -> str:
    if not d:
        return "NOT_USED"
    h = hashlib.sha256()
    for p in sorted(Path(d).glob("part-*.jsonl")):
        h.update(p.name.encode())
        h.update(hashlib.sha256(p.read_bytes()).hexdigest().encode())
    return h.hexdigest()


def nest(counts: Counter, prefix: str) -> dict:
    """Counter keys (prefix, k1, ..., kn) -> nested dict of code keys (counts only)."""
    from culinarystate.extraction.rung_a_measure import code
    out: dict = {}
    for key, n in sorted(counts.items(), key=lambda t: tuple(str(x) for x in t[0])):
        if key[0] != prefix:
            continue
        d = out
        for part in key[1:-1]:
            d = d.setdefault(code(part), {})
        last = code(key[-1])
        d[last] = d.get(last, 0) + int(n)
    return out
