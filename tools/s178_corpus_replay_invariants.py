#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C12-R1: replay-invariant property tests at corpus scale (non-BBC), counts only.

For every instruction text of a family: Rung A -> engine events (`state_graph.event_adapter`) -> engine replay
(`state_graph.replay`, which REJECTS an event that violates an invariant). Two kinds of evidence are counted:

1. ENGINE violations per invariant by family: order regression, consumption before production / double consumption, use of a
   DISCARDED lot (no resurrection), reuse of an entity or event id, split fractions of one parent exceeding 1, plus every other
   replay issue and unknown code, adapter issues, replay status per text (PASS / UNKNOWN / FAIL) and lot-accounting issues.
2. A differential check: `independent_check` re-implements the six invariants above without the engine code, conditioned only on which
   events the engine APPLIED (the state before an event depends on them), and compares event by event. A disagreement (an invariant the
   engine flags and the checker does not, or the reverse) is "unexplained"; the acceptance is 0 unexplained.
3. Power checks on a hash-selected 1-in-MUT_EVERY sample of texts: four mutations of the adapted events (swap two events with
   different order keys; consume a lot that was already consumed; consume a discarded lot; push one parent's split fractions above
   one). Both the engine and the independent checker must flag the planted violation; the detection rate shows the invariants have teeth.
   Also a determinism check on a 1-in-DET_EVERY sample (replay twice, identical snapshot hash and JSONL bytes).

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

TOOL_VERSION = "s178-corpus-replay-invariants-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
FAMILIES = ("FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS")
MUT_EVERY = 20
DET_EVERY = 50
INVARIANTS = ("ORDER_REGRESSION", "ENTITY_UNKNOWN", "ENTITY_ALREADY_CONSUMED", "ENTITY_REUSED_AFTER_DISCARD", "ENTITY_ID_REUSED",
              "EVENT_ID_REUSED", "SPLIT_FRACTIONS_EXCEED_ONE")
MUTATIONS = {"M_ORDER_SWAP": "ORDER_REGRESSION", "M_DOUBLE_CONSUME": "ENTITY_ALREADY_CONSUMED",
             "M_RESURRECT_DISCARDED": "ENTITY_REUSED_AFTER_DISCARD", "M_SPLIT_OVER_ONE": "SPLIT_FRACTIONS_EXCEED_ONE"}
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
def independent_check(events, applied: list[bool]) -> dict[str, set[int]]:
    """Per invariant, the set of event positions that violate it. Conditioned on `applied[i]` (the engine's apply/reject of event i)."""
    from culinarystate.state_graph.replay import LIFECYCLE_BY_TYPE, PARTITION_KINDS
    life: dict[str, str] = {}
    viol: dict[str, set[int]] = defaultdict(set)
    max_order = None
    seen_events: set[str] = set()
    for i, ev in enumerate(events):
        if max_order is not None and ev.order < max_order:
            viol["ORDER_REGRESSION"].add(i)
        max_order = ev.order if max_order is None else max(max_order, ev.order)
        if ev.event_id in seen_events:
            viol["EVENT_ID_REUSED"].add(i)
        seen_events.add(ev.event_id)
        for role in ("consumes", "discards"):
            for x in dict.fromkeys(getattr(ev, role)):
                st = life.get(x)
                if st is None:
                    viol["ENTITY_UNKNOWN"].add(i)
                elif st == "DISCARDED":
                    viol["ENTITY_REUSED_AFTER_DISCARD"].add(i)
                elif st == "INCORPORATED":
                    viol["ENTITY_ALREADY_CONSUMED"].add(i)
        for x in dict.fromkeys(ev.produces):
            if x in life:
                viol["ENTITY_ID_REUSED"].add(i)
        groups: dict[tuple[str, str], list] = defaultdict(list)
        for a in ev.allocations:
            if a.kind in PARTITION_KINDS:
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
                viol["SPLIT_FRACTIONS_EXCEED_ONE"].add(i)
        if applied[i]:
            for x in dict.fromkeys(ev.consumes):
                life[x] = "INCORPORATED"
            for x in dict.fromkeys(ev.discards):
                life[x] = "DISCARDED"
            types = dict(ev.produced_types)
            discard_children = {a.child for a in ev.allocations if a.kind == "DISCARD"}
            for c in dict.fromkeys(ev.produces):
                life[c] = "DISCARDED" if c in discard_children else LIFECYCLE_BY_TYPE.get(types.get(c, "UNSPECIFIED"), "ACTIVE")
    return viol


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
def mutate(events, kind: str, result):
    """Return (mutated events, positions expected to violate) or None when the mutation does not apply to this text."""
    from culinarystate.state_graph.event_log import EngineEvent
    ev = list(events)
    if kind == "M_ORDER_SWAP":
        for i in range(len(ev) - 1):
            if ev[i].order < ev[i + 1].order:
                ev[i], ev[i + 1] = ev[i + 1], ev[i]
                return ev, "ORDER_REGRESSION"
        return None
    snap = result.snapshot
    last_order = max((e.order for e in ev), default=(0, 0))
    new_order = (last_order[0] + 1, 0)
    if kind in ("M_DOUBLE_CONSUME", "M_RESURRECT_DISCARDED"):
        want = "INCORPORATED" if kind == "M_DOUBLE_CONSUME" else "DISCARDED"
        for eid in snap.entity_ids():
            if snap.current(eid).lifecycle == want:
                ev.append(EngineEvent("MUT/" + kind, new_order, kind="MUTATION", consumes=(eid,)))
                return ev, MUTATIONS[kind]
        return None
    if kind == "M_SPLIT_OVER_ONE":
        # the real graphs rarely carry a stated basis (it is UNSPECIFIED, so the engine treats the split as undecided): the planted
        # violation sets basis MASS and fraction 2/3 on every partition allocation of one parent that has at least two
        from culinarystate.state_graph.replay import PARTITION_KINDS
        for i, e in enumerate(ev):
            groups: dict[str, list[int]] = defaultdict(list)
            for k, a in enumerate(e.allocations):
                if a.kind in PARTITION_KINDS:
                    groups[a.parent].append(k)
            for idxs in groups.values():
                if len(idxs) >= 2:
                    allocs = list(e.allocations)
                    for k in idxs:
                        allocs[k] = dataclasses.replace(allocs[k], basis="MASS", fraction=Fraction(2, 3))
                    ev[i] = dataclasses.replace(e, allocations=tuple(allocs))
                    return ev, MUTATIONS[kind]
        return None
    raise ValueError(kind)


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
    from culinarystate.state_graph.replay import PARTITION_KINDS
    for ev in events:
        groups: dict[tuple[str, str], list] = defaultdict(list)
        for a in ev.allocations:
            if a.kind in PARTITION_KINDS:
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
            "final_lifecycle": Counter(), "cause": Counter()}


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
    # differential check
    eng, ind = engine_violations(result), independent_check(events, applied)
    for inv in INVARIANTS:
        e, i = eng.get(inv, set()), ind.get(inv, set())
        out["engine_inv_events"][inv] += len(e)
        out["indep_inv_events"][inv] += len(i)
        out["disagree"][inv] += len(e ^ i)
        out["texts_with_inv"][inv] += bool(e)
    c["texts_with_any_disagreement"] += any(eng.get(inv, set()) != ind.get(inv, set()) for inv in INVARIANTS)
    # determinism (sampled)
    if selected(seed, rid, DET_EVERY, "det"):
        r2, _ = replay_with_flags(events, adapted.lot_accounting)
        c["determinism_checked"] += 1
        c["determinism_identical"] += int(r2.snapshot_sha256 == result.snapshot_sha256 and r2.to_jsonl() == result.to_jsonl())
    # power checks (sampled)
    if selected(seed, rid, MUT_EVERY, "mut"):
        c["mutation_texts"] += 1
        for kind in MUTATIONS:
            m = mutate(events, kind, result)
            if m is None:
                out["mut"][f"{kind}__not_applicable"] += 1
                continue
            ev2, want = m
            try:
                r2, ap2 = replay_with_flags(ev2, adapted.lot_accounting)
                ind2 = independent_check(ev2, ap2)
            except Exception as exc:  # noqa: BLE001
                out["mut"][f"{kind}__exception_{code(type(exc).__name__)}"] += 1
                continue
            e2 = engine_violations(r2)
            out["mut"][f"{kind}__applicable"] += 1
            out["mut"][f"{kind}__engine_detected"] += bool(e2.get(want))
            out["mut"][f"{kind}__independent_detected"] += bool(ind2.get(want))
            out["mut"][f"{kind}__both_detected"] += bool(e2.get(want)) and bool(ind2.get(want))
            out["mut"][f"{kind}__sets_agree"] += e2.get(want, set()) == ind2.get(want, set())


def work(args):
    family, items, locale, seed = args
    out = new_counts()
    for rid, raw in items:
        process_text(rid, raw, locale, seed, out)
    return family, out


def merge(into: dict, part: dict) -> None:
    for k, v in part.items():
        into[k].update(v)


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
               "disagreements": agg["disagree"][k], "texts_with_violation": agg["texts_with_inv"][k]} for k in INVARIANTS}
    nonmut = {k: v for k, v in agg["mut"].items() if "exception" in k}
    return {"status": "READ", "texts": c["texts"], "texts_empty": c["texts_empty"], "texts_with_events": c["texts_with_events"],
            "rung_a_graph_events": c["events_rung_a_graph"], "engine_events_incl_lot_introductions": c["engine_events"],
            "transactions_by_status": plain(agg["tx_status"]), "replay_status_by_text": plain(agg["replay_status"]),
            "texts_with_replay_fail": c["texts_replay_fail"], "invariants": inv,
            "unexplained_total": sum(agg["disagree"].values()) + sum(v for k, v in agg["cause"].items() if "UNTRACED" in k),
            "disagreements_engine_vs_independent": sum(agg["disagree"].values()),
            "engine_issues_untraced": sum(v for k, v in agg["cause"].items() if "UNTRACED" in k),
            "engine_issue_causes": plain(agg["cause"]), "texts_with_any_disagreement": c["texts_with_any_disagreement"],
            "engine_issues_all_codes": plain(agg["engine_issue"]), "engine_unknown_codes": plain(agg["engine_unknown"]),
            "adapter_issue_codes": plain(agg["adapter_issue"]), "adapter_unknown_codes": plain(agg["adapter_unknown"]),
            "lot_accounting_issue_codes": plain(agg["lot_issue"]), "invented_values_excluded_by_adapter": c["invented_values"],
            "final_entity_lifecycle": plain(agg["final_lifecycle"]), "exceptions": plain(agg["exceptions"]),
            "determinism": {"checked_texts": c["determinism_checked"], "identical": c["determinism_identical"]},
            "split_sum_invariant_coverage": {k: c[k] for k in ("partition_groups", "partition_groups_basis_unspecified", "partition_groups_with_two_or_more_allocations",
                                                               "partition_groups_with_any_known_fraction", "partition_groups_checkable_basis_and_fraction")},
            "mutation_power": mut, "mutation_exceptions": plain(Counter(nonmut))}


def run(root: Path, families, workers: int, sample: int | None, seed: str, batch: int, out_dir: Path, name: str) -> dict:
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
           "invariants": list(INVARIANTS), "mutation_every_n_texts": MUT_EVERY, "determinism_every_n_texts": DET_EVERY,
           "locale_source": "LEGACY_SOURCE_FAMILY_LOCALE_MAP", "workers": workers, "families": {}}
    ctx = get_context("spawn")
    for fam in families:
        t1 = time.time()
        agg = new_counts()
        with ctx.Pool(workers, initializer=_init, initargs=(schema,)) as pool:
            for _f, part in pool.imap_unordered(work, batches(stream_items(fam, sample, seed), batch, fam, LOCALE.get(fam), seed)):
                merge(agg, part)
        blk = family_block(agg)
        blk["seconds"] = round(time.time() - t1, 1)
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
         f"Sample: {res['sample_texts_per_family'] or 'full families'}. Pipeline per text: Rung A -> adapter -> engine replay (which rejects an event violating an invariant) + an independent re-implementation of the seven invariants, compared event by event.", "",
         "## Violations per invariant (events), engine vs independent checker", ""]
    fams = [f for f, b in res["families"].items() if b.get("status") == "READ"]
    L += ["| invariant | " + " | ".join(f"{f} engine / independent / disagree" for f in fams) + " |", "|---|" + "---:|" * len(fams)]
    for inv in res["invariants"]:
        cells = []
        for f in fams:
            v = res["families"][f]["invariants"][inv]
            cells.append(f"{v['engine_violating_events']:,} / {v['independent_violating_events']:,} / {v['disagreements']:,}")
        L.append(f"| {inv} | " + " | ".join(cells) + " |")
    L += ["", "## Per family", ""]
    L += ["| family | texts | with events | Rung A graph events | engine events (incl. lot intros) | replay PASS | UNKNOWN | FAIL | unexplained (untraced + disagreements) | determinism identical |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for f in fams:
        b = res["families"][f]
        s = b["replay_status_by_text"]
        d = b["determinism"]
        L.append(f"| {f} | {b['texts']:,} | {b['texts_with_events']:,} | {b['rung_a_graph_events']:,} | {b['engine_events_incl_lot_introductions']:,} | {s.get('PASS', 0):,} | "
                 f"{s.get('UNKNOWN', 0):,} | {s.get('FAIL', 0):,} | **{b['unexplained_total']:,}** | {d['identical']}/{d['checked_texts']} |")
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
              "- Power check (planted violations on the sampled texts):", "",
              "| mutation | expected code | applicable | engine detected | independent detected | both | same violating events |", "|---|---|---:|---:|---:|---:|---:|"]
        for k, m in b["mutation_power"].items():
            L.append(f"| {k} | {m['expected_code']} | {m['applicable']:,} | {m['engine_detected']:,} ({m['engine_detection_pct']} %) | "
                     f"{m['independent_detected']:,} ({m['independent_detection_pct']} %) | {m['both_detected']:,} | {m['violating_event_sets_agree']:,} |")
    L += ["", "## Reading and limits", "",
          "- A violation is a structural breach (order, consumption, resurrection, id reuse, split sum). Zero says the rule-based extraction respects the replay's structural invariants; it does not say the events are right.",
          "- The independent checker shares the engine's SEMANTICS (what counts as a violation) but not its code; it is conditioned on the engine's apply/reject decisions because the state before an event depends on them.",
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
    a = ap.parse_args(argv)
    if a.workers > 24:
        ap.error("at most 24 workers (shared server)")
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    name = a.name or ("replay_invariants_corpus_v1" if not a.sample else f"replay_invariants_corpus_sample{a.sample}")
    res = run(root, [f for f in a.families.split(",") if f], a.workers, a.sample, a.seed, a.batch, out, name)
    print(json.dumps({f: {k: b.get(k) for k in ("texts", "engine_events_incl_lot_introductions", "texts_with_replay_fail", "unexplained_total", "seconds")}
                      for f, b in res["families"].items() if b.get("status") == "READ"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
