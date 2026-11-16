#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C12-R1: replay-invariant property tests at corpus scale (non-BBC), counts only.

For every instruction text of a family: Rung A -> engine events (`state_graph.event_adapter`) -> engine replay
(`state_graph.replay`, which REJECTS an event that violates an invariant). Two kinds of evidence are counted:

1. ENGINE violations per invariant by family: order regression, consumption before production / double consumption, use of a
   DISCARDED lot (no resurrection), reuse of an entity or event id, split fractions of one parent exceeding 1, plus every other
   replay issue and unknown code, adapter issues, replay status per text (PASS / UNKNOWN / FAIL) and lot-accounting issues.
2. A differential check: `independent_replay` re-implements the seven invariants above, and every other structural rejection rule
   of the replay, without importing the engine code or constants (local copies, pinned equal by a unit test). Since S178 FIX-EVAL
   (SCI-B CORP-4) it derives the APPLIED vector itself: an event is applied iff none of its rules fires. The one input it takes from the
   engine is MASS_BALANCE_FAIL (quantity arithmetic, not re-implemented; counted as `mass_balance_fail_events_taken_from_engine`). It
   compares event by event: violating events per invariant, the full issue-code set per event and the apply/reject decision. Any
   disagreement is "unexplained"; the acceptance is 0 unexplained. (v0.1 conditioned the checker on the engine's apply/reject vector
   and imported LIFECYCLE_BY_TYPE / PARTITION_KINDS from the engine; it said "six" invariants and checked seven.)
3. Power checks on a hash-selected 1-in-MUT_EVERY sample of texts: four mutations of the adapted events (swap two adjacent events with
   different order keys; consume a lot that was already consumed; consume a discarded lot; push one parent's split fractions above
   one). Since v0.2 the planted position is drawn by sha256(seed | text id | mutation) among every eligible position, and an inserted
   event goes at a drawn position after the lot's consumption / discard (mid-graph, not appended at the end). Both the engine and the
   independent checker must flag the planted violation AT the planted position; the detection rate shows the invariants have teeth.
4. Determinism on a 1-in-DET_EVERY sample: (a) replay twice in the same worker; (b) since v0.2, a second pass over the same sample in a
   fresh worker pool started with a different PYTHONHASHSEED (main pool DET_HASHSEED_MAIN, second pool DET_HASHSEED_OTHER), comparing
   per text the snapshot sha256 and the sha256 of the replay JSONL (in memory; nothing per text is written).

By construction (SCI-B CORP-5): ORDER_REGRESSION and EVENT_ID_REUSED cannot occur in adapted Rung A graphs. Rung A numbers events
`E{n}` in creation order and gives them (sentence, ordinal) order keys in loop order (`extraction/rung_a_binding.py:211-226`); the
adapter emits lot introductions `INTRO/<entity>` with order (-1, k), k increasing, before every graph event, in graph order
(`state_graph/event_adapter.py:180-213`). Their corpus-scale zeros are tautologies (`HOLDS_BY_CONSTRUCTION`), not validation; the
planted mutations show the checks would fire. Of the seven invariants, only ENTITY_UNKNOWN is non-zero on real graphs.

Counts only; no text, id, span or value is written. A violation count of zero says the rule-based extraction respects the structural
invariants of the replay, NOT that the events are correct (see `NOT_CHECKED` in the replay).

  nice -n 10 python tools/s178_corpus_replay_invariants.py --workers 16 --sample 1000 --seed 20261104   # smoke
  nice -n 10 python tools/s178_corpus_replay_invariants.py --workers 16                                 # full families
AI_DRAFTED / PROPOSED. Engineering check, not a gold score and not a human gate.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import re
import sys
import time
from collections import Counter, defaultdict
from fractions import Fraction
from multiprocessing import get_context
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-corpus-replay-invariants-0.2.0-draft"
OUT_DIR = "reports/s178/corpus"
FAMILIES = ("FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS")
MUT_EVERY = 20
DET_EVERY = 50
INVARIANTS = ("ORDER_REGRESSION", "ENTITY_UNKNOWN", "ENTITY_ALREADY_CONSUMED", "ENTITY_REUSED_AFTER_DISCARD", "ENTITY_ID_REUSED",
              "EVENT_ID_REUSED", "SPLIT_FRACTIONS_EXCEED_ONE")
MUTATIONS = {"M_ORDER_SWAP": "ORDER_REGRESSION", "M_DOUBLE_CONSUME": "ENTITY_ALREADY_CONSUMED",
             "M_RESURRECT_DISCARDED": "ENTITY_REUSED_AFTER_DISCARD", "M_SPLIT_OVER_ONE": "SPLIT_FRACTIONS_EXCEED_ONE"}
# Local copies of the engine's constants (state_graph/replay.py L48-L49, event_log.py ReplayConfig default trajectory). The checker
# must not read them from the engine (CORP-4); tests/unit/test_s178_fixeval_replay.py pins them equal to the engine's.
PARTITION_KINDS_LOCAL = frozenset({"SPLIT", "RESERVE", "REMAINDER", "DISCARD"})
LIFECYCLE_BY_TYPE_LOCAL = {"RESERVED_PORTION": "RESERVED", "DISCARDED_PORTION": "DISCARDED"}
DEFAULT_TRAJECTORY_LOCAL = "PLANNED"
# Structural rejection codes the independent replay re-derives (every engine issue code except MASS_BALANCE_FAIL, which needs the
# quantity arithmetic, and the scope / lot-accounting codes that do not arise under scope ALL per event).
STRUCTURAL_CODES = ("EVENT_ID_REUSED", "TRAJECTORY_MISMATCH", "ORDER_REGRESSION", "DEPENDENCY_NOT_APPLIED", "ENTITY_ROLE_CONFLICT",
                    "ENTITY_UNKNOWN", "ENTITY_REUSED_AFTER_DISCARD", "ENTITY_ALREADY_CONSUMED", "ENTITY_ID_REUSED",
                    "ALLOC_PARENT_NOT_CONSUMED", "ALLOC_CHILD_NOT_PRODUCED", "QUANTITY_FOR_UNPRODUCED_ENTITY", "QUANTITY_CONFLICT",
                    "SPLIT_FRACTIONS_EXCEED_ONE")
BY_CONSTRUCTION = {      # counts-only code strings (assert_counts_only); the prose is in the module docstring and the md
    "ORDER_REGRESSION": "HOLDS_BY_CONSTRUCTION|extraction/rung_a_binding.py:211-226|state_graph/event_adapter.py:180-213",
    "EVENT_ID_REUSED": "HOLDS_BY_CONSTRUCTION|extraction/rung_a_binding.py:226|state_graph/event_adapter.py:187",
}
DET_HASHSEED_MAIN = "0"
DET_HASHSEED_OTHER = "1"
_CODE = re.compile(r"[^A-Za-z0-9_]")

_RUNG = None
_SCHEMA = None


def _init(schema):
    global _RUNG, _SCHEMA
    from culinarystate.extraction.rung_a import RungA
    _RUNG, _SCHEMA = RungA(), schema


def code(x) -> str:
    out = _CODE.sub("__", str(x))[:80]
    return out or "EMPTY"


def selected(seed: str, rid: str, every: int, salt: str) -> bool:
    return int(hashlib.sha256(f"{seed}|{salt}|{rid}".encode()).hexdigest()[:8], 16) % every == 0


# ----------------------------------------------------------------------------- independent re-implementation
def independent_replay(events, applied: list[bool] | None = None, *, mass_balance_fail=frozenset(),
                       trajectory: str = DEFAULT_TRAJECTORY_LOCAL):
    """Independent replay of the structural rules, without engine code or constants.

    Returns ``(violations, applied_vector, codes)``: per invariant the set of event positions that violate it; the apply decision
    per event; the structural issue codes per event. With ``applied`` given, the apply decisions are taken from it (v0.1 behaviour,
    kept for the hand-made unit cases); otherwise an event is applied iff no structural rule fires and its position is not in
    ``mass_balance_fail`` (the only engine-derived input: positions where the engine reported MASS_BALANCE_FAIL)."""
    life: dict[str, str] = {}
    viol: dict[str, set[int]] = defaultdict(set)
    codes: list[set[str]] = []
    out_applied: list[bool] = []
    applied_ids: set[str] = set()
    max_order = None
    seen_events: set[str] = set()
    for i, ev in enumerate(events):
        cs: set[str] = set()
        if ev.event_id in seen_events:
            cs.add("EVENT_ID_REUSED")
        seen_events.add(ev.event_id)
        if ev.trajectory != trajectory:
            cs.add("TRAJECTORY_MISMATCH")
        if max_order is not None and ev.order < max_order:
            cs.add("ORDER_REGRESSION")
        max_order = ev.order if max_order is None else max(max_order, ev.order)
        if any(d not in applied_ids for d in ev.depends_on):
            cs.add("DEPENDENCY_NOT_APPLIED")
        for role in ("consumes", "produces", "discards"):
            xs = list(getattr(ev, role))
            if len(xs) != len(set(xs)):
                cs.add("ENTITY_ROLE_CONFLICT")
        if set(ev.consumes) & set(ev.discards):
            cs.add("ENTITY_ROLE_CONFLICT")
        for role in ("consumes", "discards"):
            for x in dict.fromkeys(getattr(ev, role)):
                st = life.get(x)
                if st is None:
                    cs.add("ENTITY_UNKNOWN")
                elif st == "DISCARDED":
                    cs.add("ENTITY_REUSED_AFTER_DISCARD")
                elif st == "INCORPORATED":
                    cs.add("ENTITY_ALREADY_CONSUMED")
        if any(x in life for x in ev.produces):
            cs.add("ENTITY_ID_REUSED")
        consumed, produced = set(ev.consumes), set(ev.produces)
        for a in ev.allocations:
            if a.parent not in consumed:
                cs.add("ALLOC_PARENT_NOT_CONSUMED")
            if a.child not in produced:
                cs.add("ALLOC_CHILD_NOT_PRODUCED")
        q_by: Counter = Counter(q.entity_id for q in ev.quantities)
        if any(e not in produced for e in q_by):
            cs.add("QUANTITY_FOR_UNPRODUCED_ENTITY")
        if any(n > 1 for n in q_by.values()):
            cs.add("QUANTITY_CONFLICT")
        groups: dict[tuple[str, str], list] = defaultdict(list)
        for a in ev.allocations:
            if a.kind in PARTITION_KINDS_LOCAL:
                groups[(a.parent, a.basis)].append(a)
        for (_parent, basis), allocs in groups.items():
            if basis == "UNSPECIFIED":
                continue
            lo_sum = Fraction(0)
            negative = False
            for a in allocs:
                f = a.fraction
                if f is None:
                    continue
                lo, hi = f if isinstance(f, tuple) else (f, f)
                if lo > hi:
                    continue                                  # inverted: undecided, not summed
                if lo < 0:
                    negative = True
                    continue
                lo_sum += lo
            if not negative and lo_sum > 1:
                cs.add("SPLIT_FRACTIONS_EXCEED_ONE")
        for inv in INVARIANTS:
            if inv in cs:
                viol[inv].add(i)
        codes.append(cs)
        ok = (not cs and i not in mass_balance_fail) if applied is None else bool(applied[i])
        out_applied.append(ok)
        if ok:
            applied_ids.add(ev.event_id)
            for x in dict.fromkeys(ev.consumes):
                life[x] = "INCORPORATED"
            for x in dict.fromkeys(ev.discards):
                life[x] = "DISCARDED"
            types = dict(ev.produced_types)
            discard_children = {a.child for a in ev.allocations if a.kind == "DISCARD"}
            for c in dict.fromkeys(ev.produces):
                life[c] = "DISCARDED" if c in discard_children else LIFECYCLE_BY_TYPE_LOCAL.get(types.get(c, "UNSPECIFIED"), "ACTIVE")
    return viol, out_applied, codes


def independent_check(events, applied: list[bool] | None = None, *, mass_balance_fail=frozenset()) -> dict[str, set[int]]:
    """Per invariant, the set of event positions that violate it (see ``independent_replay``)."""
    return independent_replay(events, applied, mass_balance_fail=mass_balance_fail)[0]


def engine_mass_balance_fail(result) -> frozenset:
    return frozenset(t.seq for t in result.transactions if any(i.code == "MASS_BALANCE_FAIL" for i in t.issues))


def engine_structural_codes(result) -> dict[int, set[str]]:
    return {t.seq: {i.code for i in t.issues if i.code in STRUCTURAL_CODES} for t in result.transactions}


def engine_violations(result) -> dict[str, set[int]]:
    out: dict[str, set[int]] = defaultdict(set)
    for t in result.transactions:
        for iss in t.issues:
            if iss.code in INVARIANTS:
                out[iss.code].add(t.seq)
    return out


def replay_with_flags(events, lot_accounting=None):
    from culinarystate.state_graph.replay import replay_events
    res = replay_events(events, lot_accounting=lot_accounting)
    return res, [t.status == "APPLIED" for t in res.transactions]


# ----------------------------------------------------------------------------- mutations
def _draw(key: str, n: int) -> int:
    return int(hashlib.sha256(key.encode()).hexdigest()[:12], 16) % n


def _insert(ev: list, pos: int, kind: str, eid: str):
    """Insert a mutation event consuming ``eid`` at position ``pos`` with an order key that does not regress."""
    from culinarystate.state_graph.event_log import EngineEvent
    if pos < len(ev):
        order = ev[pos - 1].order if pos > 0 else ev[0].order
    else:
        last = max((e.order for e in ev), default=(0, 0))
        order = (last[0] + 1, 0)
    ev.insert(pos, EngineEvent("MUT/" + kind, order, kind="MUTATION", consumes=(eid,)))


def mutate_at(events, kind: str, result, key: str = ""):
    """(mutated events, expected code, planted position) or None when the mutation does not apply to this text.

    The planted position is drawn by sha256(``key`` | kind) among all eligible positions (v0.2; v0.1 always took the first)."""
    ev = list(events)
    k = f"{key}|{kind}"
    if kind == "M_ORDER_SWAP":
        cand = [i for i in range(len(ev) - 1) if ev[i].order < ev[i + 1].order]
        if not cand:
            return None
        i = cand[_draw(k, len(cand))]
        ev[i], ev[i + 1] = ev[i + 1], ev[i]
        return ev, "ORDER_REGRESSION", i + 1
    if kind in ("M_DOUBLE_CONSUME", "M_RESURRECT_DISCARDED"):
        applied = {t.seq for t in result.transactions if t.status == "APPLIED"}
        cand: list[tuple[str, int]] = []
        for j, e in enumerate(ev):
            if j not in applied:
                continue
            if kind == "M_DOUBLE_CONSUME":
                cand += [(x, j) for x in dict.fromkeys(e.consumes)]
            else:
                types = dict(e.produced_types)
                dchild = {a.child for a in e.allocations if a.kind == "DISCARD"}
                cand += [(x, j) for x in dict.fromkeys(e.discards)]
                cand += [(c, j) for c in dict.fromkeys(e.produces)
                         if c in dchild or LIFECYCLE_BY_TYPE_LOCAL.get(types.get(c, "UNSPECIFIED")) == "DISCARDED"]
        if not cand:
            return None
        x, j = cand[_draw(k, len(cand))]
        pos = j + 1 + _draw(k + "|pos", len(ev) - j)            # anywhere after the lot's consumption / discard, end included
        _insert(ev, pos, kind, x)
        return ev, MUTATIONS[kind], pos
    if kind == "M_SPLIT_OVER_ONE":
        # the real graphs rarely carry a stated basis (it is UNSPECIFIED, so the engine treats the split as undecided): the planted
        # violation sets basis MASS and fraction 2/3 on every partition allocation of one parent that has at least two
        cand2: list[tuple[int, list[int]]] = []
        for i, e in enumerate(ev):
            groups: dict[str, list[int]] = defaultdict(list)
            for n, a in enumerate(e.allocations):
                if a.kind in PARTITION_KINDS_LOCAL:
                    groups[a.parent].append(n)
            cand2 += [(i, idxs) for idxs in groups.values() if len(idxs) >= 2]
        if not cand2:
            return None
        i, idxs = cand2[_draw(k, len(cand2))]
        allocs = list(ev[i].allocations)
        for n in idxs:
            allocs[n] = dataclasses.replace(allocs[n], basis="MASS", fraction=Fraction(2, 3))
        ev[i] = dataclasses.replace(ev[i], allocations=tuple(allocs))
        return ev, MUTATIONS[kind], i
    raise ValueError(kind)


def mutate(events, kind: str, result, key: str = ""):
    """Return (mutated events, code expected to fire) or None (``mutate_at`` without the position)."""
    m = mutate_at(events, kind, result, key)
    return None if m is None else (m[0], m[1])


# ----------------------------------------------------------------------------- root causes
def classify_causes(events, applied, result, adapted, cause: Counter) -> None:
    """Trace every engine issue to a known cause: an adapter issue, or a cascade from an event the engine rejected earlier."""
    produced_by: dict[str, int] = {}
    index: dict[str, int] = {}
    for i, ev in enumerate(events):
        index.setdefault(ev.event_id, i)
        for x in ev.produces:
            produced_by.setdefault(x, i)
    rejected = {i for i, a in enumerate(applied) if not a}
    no_producer = {i.path for i in adapted.issues if i.code == "ENTITY_WITHOUT_PRODUCER"}
    for t in result.transactions:
        for iss in t.issues:
            c = iss.code
            if c == "ENTITY_UNKNOWN":
                ent = iss.path.split("/", 1)[1] if "/" in iss.path else ""
                if ent in no_producer:
                    why = "ADAPTER_ENTITY_WITHOUT_PRODUCER"
                elif ent in produced_by and produced_by[ent] in rejected and produced_by[ent] < t.seq:
                    why = "CASCADE_PRODUCER_REJECTED"
                elif ent in produced_by and produced_by[ent] >= t.seq:
                    why = "CONSUMED_BEFORE_PRODUCED_IN_ORDER"
                else:
                    why = "UNTRACED"
            elif c == "DEPENDENCY_NOT_APPLIED":
                dep = iss.path.split("/", 1)[1] if "/" in iss.path else ""
                if dep in index and index[dep] in rejected and index[dep] < t.seq:
                    why = "CASCADE_DEPENDENCY_REJECTED"
                elif dep in index and index[dep] >= t.seq:
                    why = "DEPENDENCY_LATER_IN_ORDER"
                elif dep not in index:
                    why = "DEPENDENCY_NOT_IN_GRAPH"
                else:
                    why = "UNTRACED"
            else:
                why = "UNTRACED_OTHER_CODE"
            cause[f"{code(c)}__{why}"] += 1


def partition_stats(events, c: Counter) -> None:
    """How often the split-sum invariant has anything to check: partition groups (parent, basis) and their known fractions."""
    for ev in events:
        groups: dict[tuple[str, str], list] = defaultdict(list)
        for a in ev.allocations:
            if a.kind in PARTITION_KINDS_LOCAL:
                groups[(a.parent, a.basis)].append(a)
        for (_p, basis), allocs in groups.items():
            c["partition_groups"] += 1
            c["partition_groups_basis_unspecified"] += basis == "UNSPECIFIED"
            c["partition_groups_with_two_or_more_allocations"] += len(allocs) >= 2
            known = [a for a in allocs if a.fraction is not None]
            c["partition_groups_with_any_known_fraction"] += bool(known)
            c["partition_groups_checkable_basis_and_fraction"] += basis != "UNSPECIFIED" and bool(known)


# ----------------------------------------------------------------------------- per-text work
def new_counts() -> dict:
    return {"c": Counter(), "engine_issue": Counter(), "engine_unknown": Counter(), "adapter_issue": Counter(), "adapter_unknown": Counter(),
            "engine_inv_events": Counter(), "indep_inv_events": Counter(), "disagree": Counter(), "texts_with_inv": Counter(),
            "tx_status": Counter(), "replay_status": Counter(), "lot_issue": Counter(), "mut": Counter(), "exceptions": Counter(),
            "final_lifecycle": Counter(), "cause": Counter(), "code_disagree": Counter(), "det_digests": {}}


def _rid_key(rid: str) -> str:
    return hashlib.sha256(rid.encode()).hexdigest()[:20]                # in memory only; never written


def _digest(result) -> tuple[str, str]:
    return result.snapshot_sha256, hashlib.sha256(result.to_jsonl().encode()).hexdigest()


def process_text(rid: str, raw: str, locale: str | None, seed: str, out: dict) -> None:
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.state_graph.event_adapter import adapt_event_graph
    c = out["c"]
    c["texts"] += 1
    if not raw.strip():
        c["texts_empty"] += 1
        return
    try:
        source = SourceText.from_raw("T", raw)
        res = _RUNG.run(source, _RUNG.config(locale=locale), schema=_SCHEMA)
        adapted = adapt_event_graph(source, res.graph, groundings=res.quantities, recomputers=_RUNG.recomputers())
        events = adapted.events
        result, applied = replay_with_flags(events, adapted.lot_accounting)
    except Exception as exc:  # noqa: BLE001 - class name only
        out["exceptions"][code(type(exc).__name__)] += 1
        return
    c["texts_with_events"] += bool(events)
    c["engine_events"] += len(events)
    c["events_rung_a_graph"] += len(res.graph.events)
    for t in result.transactions:
        out["tx_status"][t.status] += 1
        for i in t.issues:
            out["engine_issue"][code(i.code)] += 1
        for i in t.unknown:
            out["engine_unknown"][code(i.code)] += 1
    for i in result.final_issues:
        out["lot_issue"][code(i.code)] += 1
    for i in adapted.issues:
        out["adapter_issue"][code(i.code)] += 1
    for i in adapted.unknown:
        out["adapter_unknown"][code(i.code)] += 1
    out["replay_status"][result.status] += 1
    c["texts_replay_fail"] += result.status == "FAIL"
    c["invented_values"] += adapted.invented_count
    for eid in result.snapshot.entity_ids():
        out["final_lifecycle"][result.snapshot.current(eid).lifecycle] += 1
    classify_causes(events, applied, result, adapted, out["cause"])
    partition_stats(events, c)
    # differential check: the independent replay derives its own apply/reject vector (only MASS_BALANCE_FAIL comes from the engine)
    mbf = engine_mass_balance_fail(result)
    c["mass_balance_fail_events_taken_from_engine"] += len(mbf)
    eng = engine_violations(result)
    ind, ind_applied, ind_codes = independent_replay(events, mass_balance_fail=mbf)
    for inv in INVARIANTS:
        e, i = eng.get(inv, set()), ind.get(inv, set())
        out["engine_inv_events"][inv] += len(e)
        out["indep_inv_events"][inv] += len(i)
        out["disagree"][inv] += len(e ^ i)
        out["texts_with_inv"][inv] += bool(e)
    apply_dis = sum(a != b for a, b in zip(applied, ind_applied)) + abs(len(applied) - len(ind_applied))
    c["apply_decision_disagreements"] += apply_dis
    c["engine_rejected_events"] += sum(not a for a in applied)
    c["independent_rejected_events"] += sum(not a for a in ind_applied)
    eng_codes = engine_structural_codes(result)
    code_dis = 0
    for pos, cs in enumerate(ind_codes):
        ec = eng_codes.get(pos, set())
        if ec != cs:
            code_dis += 1
            for x in sorted(ec ^ cs):
                out["code_disagree"][code(x)] += 1
    c["issue_code_set_disagreements"] += code_dis
    c["texts_with_any_disagreement"] += bool(any(eng.get(inv, set()) != ind.get(inv, set()) for inv in INVARIANTS) or apply_dis or code_dis)
    # determinism (sampled): same worker twice, and a digest for the cross-process pass
    if selected(seed, rid, DET_EVERY, "det"):
        r2, _ = replay_with_flags(events, adapted.lot_accounting)
        c["determinism_checked"] += 1
        c["determinism_identical"] += int(r2.snapshot_sha256 == result.snapshot_sha256 and r2.to_jsonl() == result.to_jsonl())
        out["det_digests"][_rid_key(rid)] = _digest(result)
    # power checks (sampled), planted at a drawn position
    if selected(seed, rid, MUT_EVERY, "mut"):
        c["mutation_texts"] += 1
        for kind in MUTATIONS:
            m = mutate_at(events, kind, result, key=f"{seed}|{rid}")
            if m is None:
                out["mut"][f"{kind}__not_applicable"] += 1
                continue
            ev2, want, pos = m
            try:
                r2, ap2 = replay_with_flags(ev2, adapted.lot_accounting)
                ind2, ind_ap2, _ = independent_replay(ev2, mass_balance_fail=engine_mass_balance_fail(r2))
            except Exception as exc:  # noqa: BLE001
                out["mut"][f"{kind}__exception_{code(type(exc).__name__)}"] += 1
                continue
            e2 = engine_violations(r2)
            out["mut"][f"{kind}__applicable"] += 1
            out["mut"][f"{kind}__engine_detected"] += bool(e2.get(want))
            out["mut"][f"{kind}__independent_detected"] += bool(ind2.get(want))
            out["mut"][f"{kind}__both_detected"] += bool(e2.get(want)) and bool(ind2.get(want))
            out["mut"][f"{kind}__sets_agree"] += e2.get(want, set()) == ind2.get(want, set())
            out["mut"][f"{kind}__engine_detected_at_planted"] += pos in e2.get(want, set())
            out["mut"][f"{kind}__independent_detected_at_planted"] += pos in ind2.get(want, set())
            out["mut"][f"{kind}__apply_vectors_agree"] += ap2 == ind_ap2
            n = len(ev2)
            out["mut"][f"{kind}__planted_first"] += pos == 0
            out["mut"][f"{kind}__planted_last"] += pos == n - 1
            out["mut"][f"{kind}__planted_interior"] += 0 < pos < n - 1


def work(args):
    family, items, locale, seed = args
    out = new_counts()
    for rid, raw in items:
        process_text(rid, raw, locale, seed, out)
    return family, out


def merge(into: dict, part: dict) -> None:
    for k, v in part.items():
        into[k].update(v)


def det_work(args):
    """Cross-process determinism pass: digests of the sampled texts, computed in a pool started with another PYTHONHASHSEED."""
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.state_graph.event_adapter import adapt_event_graph
    family, items, locale, seed = args
    out: dict[str, tuple[str, str]] = {}
    exc_n = 0
    for rid, raw in items:
        try:
            source = SourceText.from_raw("T", raw)
            res = _RUNG.run(source, _RUNG.config(locale=locale), schema=_SCHEMA)
            adapted = adapt_event_graph(source, res.graph, groundings=res.quantities, recomputers=_RUNG.recomputers())
            result, _ = replay_with_flags(adapted.events, adapted.lot_accounting)
        except Exception:  # noqa: BLE001 - counted only
            exc_n += 1
            continue
        out[_rid_key(rid)] = _digest(result)
    return out, exc_n, hash("culinarystate-hashseed-probe")


def _probe(_):
    import os as _os
    return hash("culinarystate-hashseed-probe"), _os.environ.get("PYTHONHASHSEED")


def _pool(ctx, workers: int, schema, hashseed: str):
    """A spawn pool whose workers start with PYTHONHASHSEED = ``hashseed`` (the environment is read at spawn time)."""
    import os
    old = os.environ.get("PYTHONHASHSEED")
    os.environ["PYTHONHASHSEED"] = hashseed
    try:
        pool = ctx.Pool(workers, initializer=_init, initargs=(schema,))
        probes = pool.map(_probe, range(workers))
    finally:
        if old is None:
            os.environ.pop("PYTHONHASHSEED", None)
        else:
            os.environ["PYTHONHASHSEED"] = old
    return pool, probes


# ----------------------------------------------------------------------------- driver
def stream_items(family: str, sample: int | None, seed: str):
    from culinarystate.extraction import rung_a_measure as M
    from culinarystate.recipes import corpus
    if family == "FOODCOM":
        it = corpus.iter_foodcom()
    elif family == "WIKIBOOKS":
        it = corpus.iter_rec_corpora(families=("WIKIBOOKS",))
    elif family == "GUTENBERG_SEGMENT":
        it = (r for r in corpus.iter_rec_corpora(families=("GUTENBERG_SEGMENT",)) if not r["extra"].get("raw_segment_missing"))
    else:
        raise ValueError(family)
    if sample:
        it = M.seeded_sample(it, seed, sample)
    for rec in it:
        steps = [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]
        yield rec["recipe_id"], "\n".join(steps)


def batches(it, n, family, locale, seed):
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) >= n:
            yield family, buf, locale, seed
            buf = []
    if buf:
        yield family, buf, locale, seed


def plain(o):
    if isinstance(o, Counter):
        return {k: int(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
    if isinstance(o, dict):
        return {k: plain(v) for k, v in o.items()}
    return o


def family_block(agg: dict) -> dict:
    c = agg["c"]
    mut = {}
    for kind, want in MUTATIONS.items():
        app = agg["mut"][f"{kind}__applicable"]
        mut[kind] = {"expected_code": want, "texts_sampled": c["mutation_texts"], "applicable": app,
                     "not_applicable": agg["mut"][f"{kind}__not_applicable"],
                     "engine_detected": agg["mut"][f"{kind}__engine_detected"],
                     "independent_detected": agg["mut"][f"{kind}__independent_detected"],
                     "both_detected": agg["mut"][f"{kind}__both_detected"],
                     "violating_event_sets_agree": agg["mut"][f"{kind}__sets_agree"],
                     "engine_detection_pct": round(100.0 * agg["mut"][f"{kind}__engine_detected"] / app, 3) if app else None,
                     "independent_detection_pct": round(100.0 * agg["mut"][f"{kind}__independent_detected"] / app, 3) if app else None}
    inv = {k: {"engine_violating_events": agg["engine_inv_events"][k], "independent_violating_events": agg["indep_inv_events"][k],
               "disagreements": agg["disagree"][k], "texts_with_violation": agg["texts_with_inv"][k],
               "by_construction": BY_CONSTRUCTION.get(k, "NOT_BY_CONSTRUCTION")} for k in INVARIANTS}
    for kind in MUTATIONS:
        app = agg["mut"][f"{kind}__applicable"]
        mut[kind].update({
            "engine_detected_at_planted_position": agg["mut"][f"{kind}__engine_detected_at_planted"],
            "independent_detected_at_planted_position": agg["mut"][f"{kind}__independent_detected_at_planted"],
            "apply_vectors_agree": agg["mut"][f"{kind}__apply_vectors_agree"],
            "planted_first_position": agg["mut"][f"{kind}__planted_first"], "planted_last_position": agg["mut"][f"{kind}__planted_last"],
            "planted_interior_position": agg["mut"][f"{kind}__planted_interior"],
            "independent_detection_at_planted_pct": round(100.0 * agg["mut"][f"{kind}__independent_detected_at_planted"] / app, 3) if app else None})
    nonmut = {k: v for k, v in agg["mut"].items() if "exception" in k}
    return {"status": "READ", "texts": c["texts"], "texts_empty": c["texts_empty"], "texts_with_events": c["texts_with_events"],
            "rung_a_graph_events": c["events_rung_a_graph"], "engine_events_incl_lot_introductions": c["engine_events"],
            "transactions_by_status": plain(agg["tx_status"]), "replay_status_by_text": plain(agg["replay_status"]),
            "texts_with_replay_fail": c["texts_replay_fail"], "invariants": inv,
            "unexplained_total": (sum(agg["disagree"].values()) + sum(v for k, v in agg["cause"].items() if "UNTRACED" in k)
                                  + c["apply_decision_disagreements"] + c["issue_code_set_disagreements"]),
            "disagreements_engine_vs_independent": sum(agg["disagree"].values()),
            "independent_applied_vector": {"apply_decision_disagreements": c["apply_decision_disagreements"],
                                           "issue_code_set_disagreements": c["issue_code_set_disagreements"],
                                           "issue_codes_in_disagreement": plain(agg["code_disagree"]),
                                           "engine_rejected_events": c["engine_rejected_events"],
                                           "independent_rejected_events": c["independent_rejected_events"],
                                           "mass_balance_fail_events_taken_from_engine": c["mass_balance_fail_events_taken_from_engine"]},
            "engine_issues_untraced": sum(v for k, v in agg["cause"].items() if "UNTRACED" in k),
            "engine_issue_causes": plain(agg["cause"]), "texts_with_any_disagreement": c["texts_with_any_disagreement"],
            "engine_issues_all_codes": plain(agg["engine_issue"]), "engine_unknown_codes": plain(agg["engine_unknown"]),
            "adapter_issue_codes": plain(agg["adapter_issue"]), "adapter_unknown_codes": plain(agg["adapter_unknown"]),
            "lot_accounting_issue_codes": plain(agg["lot_issue"]), "invented_values_excluded_by_adapter": c["invented_values"],
            "final_entity_lifecycle": plain(agg["final_lifecycle"]), "exceptions": plain(agg["exceptions"]),
            "determinism": {"checked_texts": c["determinism_checked"], "identical": c["determinism_identical"], "scope": "SAME_WORKER_REPLAYED_TWICE"},
            "split_sum_invariant_coverage": {k: c[k] for k in ("partition_groups", "partition_groups_basis_unspecified", "partition_groups_with_two_or_more_allocations",
                                                               "partition_groups_with_any_known_fraction", "partition_groups_checkable_basis_and_fraction")},
            "mutation_power": mut, "mutation_exceptions": plain(Counter(nonmut))}


def run(root: Path, families, workers: int, sample: int | None, seed: str, batch: int, out_dir: Path, name: str,
        det_cross_process: bool = True) -> dict:
    from culinarystate.extraction.rung_a import RULES_VERSION, RungA
    from culinarystate.extraction.rung_a_lexicon import LEXICON_VERSION
    from culinarystate.quantity.rc2_dryrun import assert_counts_only, load_schema
    from culinarystate.recipes.ledgers import LOCALE
    from culinarystate.state_graph.event_adapter import ADAPTER_VERSION
    from culinarystate.state_graph.replay import ENGINE_VERSION, NOT_CHECKED
    t0 = time.time()
    schema = load_schema(root)
    ref = RungA()
    res = {"record": "REPLAY_INVARIANTS_CORPUS_S178", "tool_version": TOOL_VERSION, "item": "T3-C12-R1",
           "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY", "contains_recipe_text": False, "contains_recipe_ids": False,
           "counts_as_human_gate": False, "sample_texts_per_family": sample,
           "sample_seed_sha256": hashlib.sha256(seed.encode()).hexdigest() if sample else None, "selection_seed_sha256": hashlib.sha256(seed.encode()).hexdigest(),
           "rung_a_rules_version": RULES_VERSION, "lexicon_version": LEXICON_VERSION, "lexicon_fingerprint": ref.lexicon.fingerprint,
           "adapter_version": ADAPTER_VERSION, "engine_version": ENGINE_VERSION, "not_checked_by_replay": list(NOT_CHECKED),
           "invariants": list(INVARIANTS), "invariants_by_construction": BY_CONSTRUCTION, "structural_codes_re_derived": list(STRUCTURAL_CODES),
           "engine_inputs_to_independent_replay": ["MASS_BALANCE_FAIL_POSITIONS"],
           "mutation_every_n_texts": MUT_EVERY, "determinism_every_n_texts": DET_EVERY,
           "locale_source": "LEGACY_SOURCE_FAMILY_LOCALE_MAP", "workers": workers, "families": {}}
    ctx = get_context("spawn")
    res["determinism_cross_process"] = {"main_pool_pythonhashseed": DET_HASHSEED_MAIN, "second_pool_pythonhashseed": DET_HASHSEED_OTHER}
    for fam in families:
        t1 = time.time()
        agg = new_counts()
        pool, probes_main = _pool(ctx, workers, schema, DET_HASHSEED_MAIN)
        with pool:
            for _f, part in pool.imap_unordered(work, batches(stream_items(fam, sample, seed), batch, fam, LOCALE.get(fam), seed)):
                merge(agg, part)
        digests_main = agg.pop("det_digests")
        blk = family_block(agg)
        blk["seconds"] = round(time.time() - t1, 1)
        if det_cross_process:
            t2 = time.time()
            other: dict = {}
            det_exc = 0
            hashes_other = set()
            pool, probes_other = _pool(ctx, max(1, min(workers, 8)), schema, DET_HASHSEED_OTHER)
            det_items = ((r, x) for r, x in stream_items(fam, sample, seed) if x.strip() and selected(seed, r, DET_EVERY, "det"))
            with pool:
                for part, n_exc, hv in pool.imap_unordered(det_work, batches(det_items, max(1, batch // 4), fam, LOCALE.get(fam), seed)):
                    other.update(part)
                    det_exc += n_exc
                    hashes_other.add(hv)
            keys = set(digests_main) | set(other)
            blk["determinism_cross_process"] = {
                "texts_main": len(digests_main), "texts_second_pool": len(other), "texts_compared": len(set(digests_main) & set(other)),
                "identical_snapshot_and_jsonl": sum(digests_main.get(k) == other.get(k) for k in keys if k in digests_main and k in other),
                "only_in_one_pass": len(keys) - len(set(digests_main) & set(other)), "second_pool_exceptions": det_exc,
                "hash_seeds_differ_in_fact": bool({p[0] for p in probes_main}.isdisjoint({p[0] for p in probes_other})),
                "worker_pythonhashseed_main": sorted({str(p[1]) for p in probes_main}),
                "worker_pythonhashseed_second": sorted({str(p[1]) for p in probes_other}),
                "seconds": round(time.time() - t2, 1)}
        res["families"][fam] = blk
    res["families"]["TASTESET"] = {"status": "NOT_AVAILABLE", "reason": "NO_INSTRUCTION_TEXT"}
    res["families"]["A1_BBC_GOOD_FOOD"] = {"status": "NOT_ON_THIS_SERVER", "reason": "D_003_BBC_DATA_NOT_PRESENT"}
    res["seconds_total"] = round(time.time() - t0, 1)
    assert_counts_only(res)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{name}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / f"{name}.md").write_text(md(res), encoding="utf-8")
    return res


def md(res: dict) -> str:
    L = ["# Replay-invariant property tests at corpus scale (S178, T3-C12-R1)", "",
         "Status: AI_DRAFTED / PROPOSED. Counts only; no text, id or value. Engineering check, not a gold score. "
         f"Tool `{res['tool_version']}`; Rung A `{res['rung_a_rules_version']}`, lexicon `{res['lexicon_fingerprint'][:16]}`, adapter `{res['adapter_version']}`, engine `{res['engine_version']}`.",
         f"Sample: {res['sample_texts_per_family'] or 'full families'}. Pipeline per text: Rung A -> adapter -> engine replay (which rejects an event violating an invariant) + an independent replay that re-derives the seven invariants, every other structural rejection rule and its own apply/reject vector (only MASS_BALANCE_FAIL positions come from the engine), compared event by event.", "",
         "## Violations per invariant (events), engine vs independent checker", "",
         "ORDER_REGRESSION and EVENT_ID_REUSED are marked BY CONSTRUCTION: Rung A and the adapter cannot produce them (ids `E{n}` and order keys in loop order, `extraction/rung_a_binding.py:211-226`; introductions first, `state_graph/event_adapter.py:180-213`). Their zeros are not validation.", ""]
    fams = [f for f, b in res["families"].items() if b.get("status") == "READ"]
    L += ["| invariant | " + " | ".join(f"{f} engine / independent / disagree" for f in fams) + " |", "|---|" + "---:|" * len(fams)]
    for inv in res["invariants"]:
        cells = []
        for f in fams:
            v = res["families"][f]["invariants"][inv]
            cells.append(f"{v['engine_violating_events']:,} / {v['independent_violating_events']:,} / {v['disagreements']:,}")
        tag = " (BY CONSTRUCTION)" if inv in res.get("invariants_by_construction", {}) else ""
        L.append(f"| {inv}{tag} | " + " | ".join(cells) + " |")
    L += ["", "## Per family", ""]
    L += ["| family | texts | with events | Rung A graph events | engine events (incl. lot intros) | replay PASS | UNKNOWN | FAIL | unexplained (untraced + disagreements) | apply-decision disagreements | determinism same worker | determinism other pool (hash seed differs) |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|"]
    for f in fams:
        b = res["families"][f]
        s = b["replay_status_by_text"]
        d = b["determinism"]
        x = b.get("determinism_cross_process") or {}
        xs = f"{x.get('identical_snapshot_and_jsonl', 0)}/{x.get('texts_compared', 0)} ({x.get('hash_seeds_differ_in_fact')})" if x else "not run"
        L.append(f"| {f} | {b['texts']:,} | {b['texts_with_events']:,} | {b['rung_a_graph_events']:,} | {b['engine_events_incl_lot_introductions']:,} | {s.get('PASS', 0):,} | "
                 f"{s.get('UNKNOWN', 0):,} | {s.get('FAIL', 0):,} | **{b['unexplained_total']:,}** | {b['independent_applied_vector']['apply_decision_disagreements']:,} | "
                 f"{d['identical']}/{d['checked_texts']} | {xs} |")
    for f in fams:
        b = res["families"][f]
        L += ["", f"### {f}", "",
              f"- Transactions: {b['transactions_by_status']}.",
              f"- All engine issue codes (events): {b['engine_issues_all_codes'] or 'none'}.",
              f"- Traced causes of every engine issue: {b['engine_issue_causes'] or 'none'}; untraced: {b['engine_issues_untraced']}; engine-vs-independent disagreements: {b['disagreements_engine_vs_independent']}.",
              f"- Engine unknown codes: {b['engine_unknown_codes'] or 'none'}.",
              f"- Adapter issue codes: {b['adapter_issue_codes'] or 'none'}; adapter unknown codes: {b['adapter_unknown_codes'] or 'none'}.",
              f"- Lot-accounting issues (final): {b['lot_accounting_issue_codes'] or 'none'}; invented values excluded by the adapter: {b['invented_values_excluded_by_adapter']}.",
              f"- Final entity lifecycles: {b['final_entity_lifecycle']}. Exceptions: {b['exceptions'] or 'none'}.",
              f"- Split-sum invariant coverage (what it had to check): {b['split_sum_invariant_coverage']}.",
              f"- Independent replay: {b['independent_applied_vector']}.",
              "- Power check (planted violations on the sampled texts, at a hash-drawn position):", "",
              "| mutation | expected code | applicable | engine detected | independent detected | independent at the planted position | same violating events | planted first / interior / last |", "|---|---|---:|---:|---:|---:|---:|---|"]
        for k, m in b["mutation_power"].items():
            L.append(f"| {k} | {m['expected_code']} | {m['applicable']:,} | {m['engine_detected']:,} ({m['engine_detection_pct']} %) | "
                     f"{m['independent_detected']:,} ({m['independent_detection_pct']} %) | {m['independent_detected_at_planted_position']:,} | {m['violating_event_sets_agree']:,} | "
                     f"{m['planted_first_position']:,} / {m['planted_interior_position']:,} / {m['planted_last_position']:,} |")
    L += ["", "## Reading and limits", "",
          "- A violation is a structural breach (order, consumption, resurrection, id reuse, split sum). Zero says the rule-based extraction respects the replay's structural invariants; it does not say the events are right.",
          "- The independent replay shares the engine's SEMANTICS (what counts as a violation) but not its code or constants; it derives its own apply/reject vector. The only engine input is the MASS_BALANCE_FAIL positions (quantity arithmetic is not re-implemented).",
          "- Determinism: same-worker double replay, and a second worker pool started with a different PYTHONHASHSEED over the same sample.",
          f"- Not checked by the replay at all: {', '.join(res['not_checked_by_replay'])}.",
          "- TASTEset has no instruction text; BBC is not on this server (D-003)."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--seed", default="20261104")
    ap.add_argument("--batch", type=int, default=200)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--name", default=None)
    ap.add_argument("--no-cross-process-determinism", action="store_true")
    a = ap.parse_args(argv)
    if a.workers > 24:
        ap.error("at most 24 workers (shared server)")
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    name = a.name or ("replay_invariants_corpus_v2" if not a.sample else f"replay_invariants_corpus_sample{a.sample}_v2")
    res = run(root, [f for f in a.families.split(",") if f], a.workers, a.sample, a.seed, a.batch, out, name,
              det_cross_process=not a.no_cross_process_determinism)
    print(json.dumps({f: {k: b.get(k) for k in ("texts", "engine_events_incl_lot_introductions", "texts_with_replay_fail", "unexplained_total", "seconds")}
                      for f, b in res["families"].items() if b.get("status") == "READ"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
