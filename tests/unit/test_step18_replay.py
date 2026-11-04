"""Step 18b/18c deterministic replay, transactions, snapshot hashing and invariants (DRAFT_PENDING_16c).

Status: DRAFT_PENDING_16c (hard gate 16c open). Synthetic events only; nothing is
gold and no EVT / ENTITY / STATE ledger row is read or written.

Card (Plan Step 18, method 1-4): one append-only transaction per event = input
snapshot hash + event revision + output entity versions + quantity changes + issues
+ config hash; identical replay gives an identical snapshot hash; invariants are hard
validators with issue codes, never silent clamping; mass balance only when every term
is known, else UNKNOWN not FAIL; inferred events never feed explicit-only queries.
Negative controls: shuffled event order raises invariant issues; reuse of a
discarded entity fails.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from culinarystate.state_graph import replay as rp
from culinarystate.state_graph.event_log import (
    Allocation, EngineEvent, EventLog, EventLogError, QuantityTerm,
)
from culinarystate.state_graph.replay import Quantity, ReplayConfig, replay_events, replay_log

F = Fraction


def qt(entity: str, lo: int, hi: int | None = None, ref: str = "Q1", dim: str = "g") -> QuantityTerm:
    return QuantityTerm(entity, dim, F(lo), F(hi if hi is not None else lo), ref)


def intro(lot: str, k: int, q: QuantityTerm | None = None, route: str = "INFERRED_RULE") -> EngineEvent:
    return EngineEvent(f"INTRO/{lot}", (-1, k), kind="INTRODUCE_LOT", produces=(lot,),
                       produced_types=((lot, "INGREDIENT_LOT"),), quantities=(q,) if q else (), claim_route=route)


def step(eid: str, i: int, consumes=(), produces=(), discards=(), types=None, **kw) -> EngineEvent:
    types = types if types is not None else tuple((p, "INTERMEDIATE") for p in produces)
    return EngineEvent(eid, (i, 0), consumes=tuple(consumes), produces=tuple(produces), discards=tuple(discards),
                       produced_types=tuple(types), **kw)


def split(eid: str, i: int, parent: str, children: list[tuple[str, str, object]], basis: str = "MASS",
          quantities=()) -> EngineEvent:
    allocs = tuple(Allocation(f"{eid}/A{k}", kind, basis, parent, child, frac)
                   for k, (child, kind, frac) in enumerate(children))
    types = tuple((c, "RESERVED_PORTION" if kind == "RESERVE" else "INTERMEDIATE") for c, kind, _ in children)
    return EngineEvent(eid, (i, 0), consumes=(parent,), produces=tuple(c for c, _, _ in children),
                       produced_types=types, allocations=allocs, quantities=tuple(quantities))


def codes(result) -> set[str]:
    return {i.code for i in result.issues}


def unknown_codes(result) -> set[str]:
    return {i.code for i in result.unknown}


def pasta() -> list[EngineEvent]:
    return [intro("pasta", 0, qt("pasta", 300, ref="Q1")), intro("water", 1, qt("water", 2000, ref="Q2", dim="mL")),
            step("E1", 1, consumes=("pasta", "water"), produces=("pot",), types=(("pot", "MIXTURE"),)),
            step("E2", 2, consumes=("pot",), produces=("pot2",)),
            split("E3", 3, "pot2", [("drained", "SPLIT", None), ("liquid", "SPLIT", None)], basis="UNSPECIFIED"),
            split("E4", 4, "liquid", [("reserved", "RESERVE", None), ("rest", "REMAINDER", None)],
                  basis="UNSPECIFIED", quantities=(qt("reserved", 100, ref="Q3", dim="mL"),)),
            step("E5", 5, discards=("rest",)),
            step("E6", 6, consumes=("drained", "reserved"), produces=("dish",), types=(("dish", "MIXTURE"),))]


# ---------------------------------------------------------------- module
def test_module_is_draft_pending_16c_and_imports_no_pandas():
    assert rp.STATUS == "DRAFT_PENDING_16c"
    src = Path(rp.__file__).read_text(encoding="utf-8")
    assert "DRAFT_PENDING_16c" in src.splitlines()[0]
    assert "import pandas" not in src and "import numpy" not in src


# ---------------------------------------------------------------- transactions
def test_one_transaction_per_event_with_exactly_the_card_fields():
    r = replay_events(pasta())
    assert len(r.transactions) == len(pasta()) and r.issues == ()
    tx = r.transactions[0].to_canonical()
    card = {"input_snapshot_sha256", "event_revision", "output_entity_versions", "quantity_changes", "issues",
            "config_sha256"}
    ident = {"seq", "event_id", "event_sha256", "status", "unknown", "mass_balance", "output_snapshot_sha256"}
    assert set(tx) == card | ident


def test_snapshot_hashes_chain_through_the_transactions():
    r = replay_events(pasta())
    assert r.transactions[0].input_snapshot_sha256 == rp.empty_snapshot().sha256
    for a, b in zip(r.transactions, r.transactions[1:]):
        assert b.input_snapshot_sha256 == a.output_snapshot_sha256
    assert r.transactions[-1].output_snapshot_sha256 == r.snapshot.sha256 == r.snapshot_sha256
    assert all(t.config_sha256 == ReplayConfig().config_sha256 for t in r.transactions)


def test_identical_replay_is_byte_identical_and_config_is_hashed():
    a, b = replay_events(pasta()), replay_events(list(pasta()))
    assert a.to_jsonl() == b.to_jsonl() and a.sha256 == b.sha256
    c = replay_events(pasta(), ReplayConfig(scope="EXPLICIT_ONLY"))
    assert c.transactions[0].config_sha256 != a.transactions[0].config_sha256
    assert replay_events(pasta()[:-1]).snapshot_sha256 != a.snapshot_sha256


def test_versions_are_appended_and_lifecycles_follow_the_entity_draft():
    s = replay_events(pasta()).snapshot
    assert [v.lifecycle for v in s.versions("pasta")] == ["ACTIVE", "INCORPORATED"]
    assert [v.version for v in s.versions("pasta")] == [0, 1]
    assert s.current("rest").lifecycle == "DISCARDED"
    assert s.versions("reserved")[0].lifecycle == "RESERVED"
    assert s.current("dish").lifecycle == "ACTIVE" and s.current("dish").parents == ("drained", "reserved")
    assert s.current("drained").parents == ("pot2",)


def test_transaction_reports_output_versions_and_quantity_changes():
    tx = replay_events(pasta()).transactions[5]
    assert tx.event_id == "E4" and tx.status == "APPLIED"
    assert [(v["entity_id"], v["version"], v["lifecycle"]) for v in tx.to_canonical()["output_entity_versions"]] \
        == [("liquid", 1, "INCORPORATED"), ("reserved", 0, "RESERVED"), ("rest", 0, "ACTIVE")]
    changes = {c["entity_id"]: c for c in tx.to_canonical()["quantity_changes"]}
    assert changes["reserved"]["after"]["bounds"] == {"dim": "mL", "low": "100/1", "high": "100/1"}
    assert changes["rest"]["after"] is None and changes["rest"]["reason"] == "PARENT_QUANTITY_UNKNOWN"


# ---------------------------------------------------------------- quantities (no invention)
def test_transform_and_merge_never_invent_an_amount():
    s = replay_events(pasta()).snapshot
    assert s.current("pot").quantity is None and s.current("pot").quantity_reason == "NOT_PROPAGATED"
    assert s.current("pot2").quantity is None


def test_exact_split_propagation_and_remainder():
    r = replay_events([intro("d", 0, qt("d", 500)),
                       split("E1", 1, "d", [("ball", "SPLIT", F(1, 4)), ("rest", "REMAINDER", None)])])
    s = r.snapshot
    assert s.current("ball").quantity.bounds() == ("g", F(125), F(125))
    assert s.current("rest").quantity.bounds() == ("g", F(375), F(375))
    assert r.transactions[1].mass_balance[0]["status"] == "PASS" and r.issues == ()


def test_correlated_split_children_close_exactly_on_an_interval_parent():
    r = replay_events([intro("d", 0, qt("d", 100, 120)),
                       split("E1", 1, "d", [("a", "SPLIT", F(1, 2)), ("b", "SPLIT", F(1, 2))])])
    assert r.snapshot.current("a").quantity.bounds() == ("g", F(50), F(60))
    mb = r.transactions[1].mass_balance[0]
    assert mb == {"parent": "d", "status": "PASS", "reason": None}      # naive intervals would give [-20, 20]
    q = r.snapshot.current("a").quantity.plus(r.snapshot.current("b").quantity)
    assert q == Quantity.of(qt("d", 100, 120))


def test_unspecified_basis_or_interval_fraction_stays_unknown_not_fail():
    r = replay_events([intro("d", 0, qt("d", 500)),
                       split("E1", 1, "d", [("a", "SPLIT", F(1, 2)), ("b", "SPLIT", None)], basis="UNSPECIFIED")])
    assert r.issues == () and "FRACTION_BASIS_UNSPECIFIED" in unknown_codes(r)
    assert r.snapshot.current("a").quantity is None
    r2 = replay_events([intro("d", 0, qt("d", 500)),
                        split("E1", 1, "d", [("a", "SPLIT", (F(1, 4), F(1, 3)))])])
    assert r2.issues == () and r2.snapshot.current("a").quantity_reason == "FRACTION_INTERVAL_NOT_PROPAGATED"


def test_basis_must_match_the_parent_dimension():
    r = replay_events([intro("d", 0, qt("d", 500)), split("E1", 1, "d", [("a", "SPLIT", F(1, 2))], basis="VOLUME")])
    assert r.issues == () and r.snapshot.current("a").quantity_reason == "BASIS_DIMENSION_MISMATCH"


# ---------------------------------------------------------------- invariants (hard, never clamped)
def test_split_fractions_over_one_are_rejected_without_clamping():
    events = [intro("d", 0, qt("d", 500)), split("E1", 1, "d", [("a", "SPLIT", F(2, 3)), ("b", "SPLIT", F(2, 3))])]
    r = replay_events(events)
    assert "SPLIT_FRACTIONS_EXCEED_ONE" in codes(r) and r.transactions[1].status == "REJECTED"
    assert r.snapshot.current("d").lifecycle == "ACTIVE" and "a" not in r.snapshot.entity_ids()
    assert r.transactions[1].input_snapshot_sha256 == r.transactions[1].output_snapshot_sha256


def test_known_fractions_over_one_fail_even_with_an_unknown_sibling():
    r = replay_events([intro("d", 0), split("E1", 1, "d", [("a", "SPLIT", F(3, 4)), ("b", "SPLIT", F(1, 2)),
                                                           ("c", "SPLIT", None)])])
    assert "SPLIT_FRACTIONS_EXCEED_ONE" in codes(r)


def test_mass_balance_fails_when_outputs_exceed_the_input():
    r = replay_events([intro("d", 0, qt("d", 100)),
                       split("E1", 1, "d", [("res", "RESERVE", None), ("rest", "REMAINDER", None)],
                             quantities=(qt("res", 150, ref="Q2"),))])
    assert "MASS_BALANCE_FAIL" in codes(r) and r.transactions[1].status == "REJECTED"
    assert r.snapshot.current("d").lifecycle == "ACTIVE"                   # nothing clamped or half-applied


@pytest.mark.parametrize("child_q, reason", [(None, "TERM_UNKNOWN"), (qt("a", 50, ref="Q2", dim="mL"),
                                                                       "DIMENSION_MIXED")])
def test_mass_balance_is_unknown_not_fail_when_a_term_is_unknown(child_q, reason):
    r = replay_events([intro("d", 0, qt("d", 100)),
                       split("E1", 1, "d", [("a", "SPLIT", None), ("b", "SPLIT", None)],
                             quantities=(child_q,) if child_q else ())])
    assert r.issues == ()
    assert {"parent": "d", "status": "UNKNOWN", "reason": reason} in r.transactions[1].mass_balance


def test_incomplete_partition_is_unknown():
    r = replay_events([intro("d", 0, qt("d", 100)), split("E1", 1, "d", [("a", "SPLIT", F(1, 4))])])
    assert r.transactions[1].mass_balance == ({"parent": "d", "status": "UNKNOWN", "reason": "PARTITION_INCOMPLETE"},)


def test_consumed_before_produced_is_an_issue_even_with_equal_order_keys():
    events = [EngineEvent("E2", (0, 0), consumes=("N1",), produces=("N2",)),
              EngineEvent("E1", (0, 0), produces=("N1",))]
    r = replay_events(events)
    assert "ENTITY_UNKNOWN" in codes(r) and "ORDER_REGRESSION" not in codes(r)


def test_reuse_of_a_discarded_entity_fails():
    r = replay_events([intro("x", 0), step("E1", 1, discards=("x",)), step("E2", 2, consumes=("x",), produces=("y",))])
    assert "ENTITY_REUSED_AFTER_DISCARD" in codes(r) and r.transactions[2].status == "REJECTED"
    r2 = replay_events([intro("x", 0), step("E1", 1, discards=("x",)), step("E2", 2, discards=("x",))])
    assert "ENTITY_REUSED_AFTER_DISCARD" in codes(r2)


@pytest.mark.parametrize("events, code", [
    ([intro("x", 0), step("E1", 1, consumes=("x",), produces=("y",)), step("E2", 2, consumes=("x",), produces=("z",))],
     "ENTITY_ALREADY_CONSUMED"),
    ([intro("x", 0), step("E1", 1, consumes=("x",), produces=("x",))], "ENTITY_ID_REUSED"),
    ([intro("x", 0), intro("x2", 1), step("E1", 2, consumes=("x", "x"), produces=("y",))], "ENTITY_ROLE_CONFLICT"),
    ([intro("x", 0), step("E1", 1, consumes=("x",), discards=("x",))], "ENTITY_ROLE_CONFLICT"),
    ([intro("x", 0), intro("w", 1), EngineEvent("E1", (2, 0), consumes=("x",), produces=("y",),
                                                allocations=(Allocation("A", "SPLIT", "MASS", "w", "y"),))],
     "ALLOC_PARENT_NOT_CONSUMED"),
    ([intro("x", 0), EngineEvent("E1", (1, 0), consumes=("x",), produces=("y",),
                                 allocations=(Allocation("A", "SPLIT", "MASS", "x", "z"),))],
     "ALLOC_CHILD_NOT_PRODUCED"),
    ([intro("x", 0), step("E1", 1, consumes=("x",), produces=("y",), quantities=(qt("x", 5),))],
     "QUANTITY_FOR_UNPRODUCED_ENTITY"),
    ([intro("x", 0), step("E1", 1, consumes=("x",), produces=("y",),
                          quantities=(qt("y", 5), qt("y", 6, ref="Q2")))], "QUANTITY_CONFLICT"),
    ([intro("x", 0), step("E1", 1, consumes=("x",), produces=("y",), trajectory="PREDICTED")], "TRAJECTORY_MISMATCH"),
    ([intro("x", 0), step("E1", 1, consumes=("x",), produces=("y",), depends_on=("E9",))], "DEPENDENCY_NOT_APPLIED"),
    ([step("E1", 1, consumes=("ghost",), produces=("y",))], "ENTITY_UNKNOWN"),
])
def test_invariant_issue_codes(events, code):
    r = replay_events(events)
    assert code in codes(r) and r.transactions[-1].status == "REJECTED" and r.status == "FAIL"
    assert code in rp.ISSUE_CODES


def test_order_regression_is_reported():
    r = replay_events([intro("x", 0), step("E2", 2, consumes=("x",), produces=("y",)),
                       step("E1", 1, consumes=("y",), produces=("z",))])
    assert "ORDER_REGRESSION" in codes(r)


# ---------------------------------------------------------------- scope / trajectory / revisions
def test_explicit_only_scope_skips_inferred_events_and_refuses_their_products():
    events = [intro("x", 0, route="EXPLICIT"), step("E1", 1, consumes=("x",), produces=("y",)),
              step("E2", 2, consumes=("y",), produces=("z",), claim_route="EXPLICIT")]
    r = replay_events(events, ReplayConfig(scope="EXPLICIT_ONLY"))
    assert [t.status for t in r.transactions] == ["APPLIED", "SKIPPED_SCOPE", "REJECTED"]
    assert "INFERRED_DEPENDENCY_IN_EXPLICIT_SCOPE" in codes(r) and "y" not in r.snapshot.entity_ids()
    assert replay_events(events).issues == ()                              # ALL scope uses every event
    explicit = [intro("x", 0, route="EXPLICIT"), step("E1", 1, consumes=("x",), produces=("y",),
                                                     claim_route="EXPLICIT")]
    assert replay_events(explicit, ReplayConfig(scope="EXPLICIT_ONLY")).status == "PASS"


def test_trajectories_are_kept_apart():
    events = [intro("x", 0), step("E1", 1, consumes=("x",), produces=("y",), trajectory="OBSERVED_SESSION")]
    assert "TRAJECTORY_MISMATCH" in codes(replay_events(events))
    obs = [EngineEvent(e.event_id, e.order, produces=e.produces, consumes=e.consumes,
                       produced_types=e.produced_types, trajectory="OBSERVED_SESSION") for e in events]
    r = replay_events(obs, ReplayConfig(trajectory="OBSERVED_SESSION"))
    assert r.issues == () and r.snapshot.current("y").trajectory == "OBSERVED_SESSION"


def test_replay_log_uses_the_latest_revision_and_records_it():
    log = EventLog()
    for e in [intro("x", 0), step("E1", 1, consumes=("x",), produces=("y",))]:
        log.append(e)
    log.append(EngineEvent("E1", (1, 0), revision=1, consumes=("x",), produces=("y",),
                           produced_types=(("y", "MIXTURE"),)))
    r = replay_log(log)
    assert [t.event_revision for t in r.transactions] == [0, 1]
    assert r.snapshot.current("y").entity_type == "MIXTURE" and len(log) == 3


def test_bad_config_is_refused():
    with pytest.raises(EventLogError):
        ReplayConfig(scope="SOME")
    with pytest.raises(EventLogError):
        ReplayConfig(trajectory="GUESS")


# ---------------------------------------------------------------- lot accounting / output
def test_lot_accounting_must_agree_with_the_replayed_lifecycle():
    events = [intro("a", 0), intro("b", 1), step("E1", 2, consumes=("a",), produces=("y",))]
    ok = replay_events(events, lot_accounting={"a": "USED", "b": "APPARENTLY_UNUSED"})
    assert ok.issues == ()
    bad = replay_events(events, lot_accounting={"a": "DISCARDED", "b": "USED", "c": "OPTIONAL"})
    assert [(i.code, i.path) for i in bad.final_issues] == [("LOT_STATUS_CONTRADICTS_REPLAY", "a"),
                                                            ("LOT_STATUS_CONTRADICTS_REPLAY", "b"),
                                                            ("LOT_NOT_IN_REPLAY", "c")]


def test_result_names_what_it_does_not_check():
    r = replay_events(pasta())
    assert "INVENTED_VALUES_SEE_ADAPTER_AUDIT" in r.not_checked
    assert "SPAN_ROUNDTRIP_SEE_V1" in r.not_checked


def test_transactions_writer_uses_the_guarded_writer(tmp_path):
    r = replay_events(pasta())
    p = rp.write_replay_jsonl(r, tmp_path / "replay.jsonl")
    assert p.read_text(encoding="utf-8") == r.to_jsonl()
    with pytest.raises(EventLogError):
        rp.write_replay_jsonl(r, p)
    with pytest.raises(EventLogError):
        rp.write_replay_jsonl(r, tmp_path / "STATE.jsonl")


def test_jsonl_has_header_transactions_and_result_lines():
    r = replay_events(pasta())
    lines = r.to_jsonl().splitlines()
    assert len(lines) == len(pasta()) + 2
    assert '"record":"REPLAY_HEADER"' in lines[0]
    assert '"record":"REPLAY_RESULT"' in lines[-1] and r.snapshot_sha256 in lines[-1]
    assert r.sha256 == hashlib.sha256(r.to_jsonl().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- properties
@st.composite
def recipes(draw):
    """Valid synthetic event sequences with strictly increasing order keys."""
    events, live, discarded, nid = [], [], [], 0
    for k in range(draw(st.integers(1, 4))):
        q = draw(st.none() | st.integers(1, 500))
        events.append(intro(f"L{k}", k, qt(f"L{k}", q, q + draw(st.integers(0, 20)), ref=f"Q{k}") if q else None))
        live.append(f"L{k}")
    for i in range(draw(st.integers(1, 8))):
        if not live:
            break
        op = draw(st.sampled_from("TMSD"))
        op = "T" if op == "M" and len(live) < 2 else op
        if op == "M":
            ins = draw(st.lists(st.sampled_from(live), min_size=2, max_size=2, unique=True))
        else:
            ins = [draw(st.sampled_from(live))]
        for x in ins:
            live.remove(x)
        if op == "D":
            events.append(step(f"E{i}", i, discards=tuple(ins)))
            discarded.extend(ins)
        elif op == "S":
            a, b = f"N{nid}", f"N{nid + 1}"
            nid += 2
            frac = draw(st.fractions(min_value=0, max_value=1, max_denominator=12))
            events.append(split(f"E{i}", i, ins[0], [(a, "SPLIT", frac), (b, "REMAINDER", None)]))
            live += [a, b]
        else:
            out = f"N{nid}"
            nid += 1
            events.append(step(f"E{i}", i, consumes=tuple(ins), produces=(out,)))
            live.append(out)
    return events, discarded


@settings(max_examples=60, deadline=None)
@given(recipes())
def test_property_replay_twice_is_byte_identical_and_valid_input_has_no_issues(case):
    events, _ = case
    a, b = replay_events(events), replay_events(list(events))
    assert a.to_jsonl() == b.to_jsonl() and a.snapshot_sha256 == b.snapshot_sha256
    assert a.issues == ()


@settings(max_examples=60, deadline=None)
@given(recipes(), st.data())
def test_property_shuffled_order_raises_invariant_issues(case, data):
    events, _ = case
    perm = data.draw(st.permutations(range(len(events))))
    shuffled = [events[i] for i in perm]
    r = replay_events(shuffled)
    if list(perm) != sorted(perm):
        assert r.issues and "ORDER_REGRESSION" in codes(r)
    else:
        assert r.issues == ()


@settings(max_examples=60, deadline=None)
@given(recipes())
def test_property_reuse_of_any_discarded_entity_fails(case):
    events, discarded = case
    for k, x in enumerate(discarded):
        r = replay_events(events + [step("REUSE", 100 + k, consumes=(x,), produces=(f"R{k}",))])
        assert "ENTITY_REUSED_AFTER_DISCARD" in codes(r) and r.transactions[-1].status == "REJECTED"


@settings(max_examples=40, deadline=None)
@given(recipes(), st.integers(min_value=0, max_value=12))
def test_property_prefix_replay_is_a_prefix_of_the_full_replay(case, k):
    events, _ = case
    k = min(k, len(events))
    full, part = replay_events(events), replay_events(events[:k])
    assert [t.to_canonical() for t in part.transactions] == [t.to_canonical() for t in full.transactions[:k]]
