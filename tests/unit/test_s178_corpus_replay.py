"""S178 T3-C12-R1: independent invariant checker, mutations and root-cause tracing of the corpus replay tool. Synthetic text and ids only."""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from types import SimpleNamespace

import pytest

from culinarystate.extraction import rung_a as ra
from culinarystate.extraction import rung_a_lexicon as lx
from culinarystate.quantity.rc2_dryrun import assert_counts_only
from culinarystate.state_graph.event_log import Allocation, EngineEvent
from tests.unit.test_s178_analysis_helpers import load_tool
from tests.unit.test_step17b_rung_a import SCHEMA, SYN, TEXT

T = load_tool("s178_corpus_replay_invariants")


def ev(eid, order, *, consumes=(), produces=(), discards=(), types=(), allocs=(), depends=()):
    return EngineEvent(eid, order, kind="ACTION", consumes=tuple(consumes), produces=tuple(produces), discards=tuple(discards),
                       depends_on=tuple(depends), produced_types=tuple(types), allocations=tuple(allocs))


def intro(x, k=0):
    return ev(f"INTRO/{x}", (-1, k), produces=(x,), types=((x, "INGREDIENT_LOT"),))


def both(events):
    """Engine and independent violations for the same events (independent conditioned on the engine's apply/reject)."""
    res, applied = T.replay_with_flags(events)
    return T.engine_violations(res), T.independent_check(events, applied), res


def same(events):
    eng, ind, res = both(events)
    for inv in T.INVARIANTS:
        assert eng.get(inv, set()) == ind.get(inv, set()), inv
    return eng, res


# ------------------------------------------------------------------ the checker agrees with the engine on hand-made cases
def test_clean_sequence_has_no_violations():
    eng, res = same([intro("A"), intro("B", 1), ev("E1", (0, 0), consumes=("A", "B"), produces=("M",), types=(("M", "MIXTURE"),)),
                     ev("E2", (1, 0), consumes=("M",), produces=("N",), types=(("N", "INTERMEDIATE"),))])
    assert not any(eng.values()) and res.status in ("PASS", "UNKNOWN")


def test_order_regression():
    eng, _ = same([intro("A"), ev("E1", (2, 0), consumes=("A",), produces=("M",)), ev("E2", (1, 0), consumes=("M",), produces=("N",))])
    assert eng["ORDER_REGRESSION"] == {2}


def test_double_consumption_and_resurrection():
    eng, _ = same([intro("A"), intro("B", 1), ev("E1", (0, 0), consumes=("A",), produces=("M",)),
                   ev("E2", (1, 0), consumes=("A",), produces=("N",)),                          # A already consumed
                   ev("E3", (2, 0), discards=("B",)), ev("E4", (3, 0), consumes=("B",), produces=("P",))])     # B used after discard
    assert eng["ENTITY_ALREADY_CONSUMED"] == {3} and eng["ENTITY_REUSED_AFTER_DISCARD"] == {5}


def test_unknown_entity_and_id_reuse_and_event_id_reuse():
    eng, _ = same([intro("A"), ev("E1", (0, 0), consumes=("GHOST",), produces=("M",)), ev("E1", (1, 0), consumes=("A",), produces=("A",))])
    assert eng["ENTITY_UNKNOWN"] == {1} and eng["EVENT_ID_REUSED"] == {2} and eng["ENTITY_ID_REUSED"] == {2}


def test_rejected_events_do_not_change_state():
    """E1 is rejected (unknown input), so its product M never exists and E2's use of M is unknown too (a cascade)."""
    eng, _ = same([ev("E1", (0, 0), consumes=("GHOST",), produces=("M",)), ev("E2", (1, 0), consumes=("M",), produces=("N",))])
    assert eng["ENTITY_UNKNOWN"] == {0, 1}


def _split(f1, f2, basis="MASS", k2="SPLIT"):
    return [intro("A"), ev("E1", (0, 0), consumes=("A",), produces=("X", "Y"), types=(("X", "INTERMEDIATE"), ("Y", "INTERMEDIATE")),
                           allocs=(Allocation("L1", "SPLIT", basis, "A", "X", f1), Allocation("L2", k2, basis, "A", "Y", f2)))]


@pytest.mark.parametrize("f1,f2,basis,exceeds", [
    (Fraction(2, 3), Fraction(2, 3), "MASS", True), (Fraction(1, 2), Fraction(1, 2), "MASS", False), (Fraction(1, 2), None, "MASS", False),
    (Fraction(2, 3), Fraction(2, 3), "UNSPECIFIED", False),                       # undecided, not a violation
    ((Fraction(1, 2), Fraction(3, 4)), Fraction(1, 2), "MASS", False),            # lower bounds sum to 1
    ((Fraction(3, 5), Fraction(3, 4)), Fraction(1, 2), "COUNT", True),            # lower bounds sum above 1
    (Fraction(-1, 2), Fraction(2, 3), "MASS", False),                             # negative: rule open, excluded
    ((Fraction(3, 4), Fraction(1, 2)), Fraction(2, 3), "MASS", False),            # inverted interval: undecided
])
def test_split_sum(f1, f2, basis, exceeds):
    eng, _ = same(_split(f1, f2, basis))
    assert bool(eng.get("SPLIT_FRACTIONS_EXCEED_ONE")) is exceeds


def test_remainder_without_fraction_is_not_a_violation():
    eng, _ = same(_split(Fraction(3, 4), None, "MASS", k2="REMAINDER"))
    assert not eng.get("SPLIT_FRACTIONS_EXCEED_ONE")


# ------------------------------------------------------------------ mutations
@pytest.fixture(scope="module")
def rung():
    return ra.RungA(lx.build_lexicon(**SYN))


def _events(rung, raw):
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.state_graph.event_adapter import adapt_event_graph
    s = SourceText.from_raw("SYN", raw)
    out = rung.run(s, rung.config(), schema=SCHEMA)
    a = adapt_event_graph(s, out.graph, groundings=out.quantities, recomputers=rung.recomputers())
    res, applied = T.replay_with_flags(a.events, a.lot_accounting)
    return a, res, applied


def test_every_mutation_is_detected_by_both_checkers(rung):
    a, res, applied = _events(rung, TEXT + " Reserve half of the liquid. Discard the dough. Divide the water into two parts.")
    assert res.status in ("PASS", "UNKNOWN") and not T.engine_violations(res)
    for kind, want in T.MUTATIONS.items():
        m = T.mutate(a.events, kind, res)
        if m is None:
            assert kind == "M_SPLIT_OVER_ONE" or kind == "M_RESURRECT_DISCARDED", kind
            continue
        ev2, expected = m
        assert expected == want
        r2, ap2 = T.replay_with_flags(ev2, a.lot_accounting)
        e2, i2 = T.engine_violations(r2), T.independent_check(ev2, ap2)
        assert e2.get(want) and i2.get(want) and e2[want] == i2[want], kind


def test_resurrection_and_split_mutations_on_a_discard_and_divide_text(rung):
    a, res, _ = _events(rung, "Discard the liquid. Divide the dough into 4 balls. Mix the dough with the oil. Add the leaf.")
    kinds = {k: T.mutate(a.events, k, res) for k in ("M_RESURRECT_DISCARDED", "M_SPLIT_OVER_ONE")}
    assert kinds["M_RESURRECT_DISCARDED"] is not None
    for kind, m in kinds.items():
        if m is None:
            continue
        ev2, want = m
        r2, ap2 = T.replay_with_flags(ev2, a.lot_accounting)
        assert T.engine_violations(r2).get(want) and T.independent_check(ev2, ap2).get(want), kind


def test_mutations_do_not_apply_to_trivial_inputs():
    events = [intro("A")]
    res, _ = T.replay_with_flags(events)
    for kind in T.MUTATIONS:
        assert T.mutate(events, kind, res) is None


# ------------------------------------------------------------------ per-text counting, causes and determinism
def test_process_text_counts_and_no_disagreement(rung, monkeypatch):
    monkeypatch.setattr(T, "_RUNG", rung)
    monkeypatch.setattr(T, "_SCHEMA", SCHEMA)
    monkeypatch.setattr(T, "MUT_EVERY", 1)
    monkeypatch.setattr(T, "DET_EVERY", 1)
    out = T.new_counts()
    for i, raw in enumerate([TEXT, "Reserve half of the liquid. Add the liquid to the onion.", "", "Discard the liquid. Add the liquid."]):
        T.process_text(f"id{i}", raw, None, "seed", out)
    c = out["c"]
    assert c["texts"] == 4 and c["texts_empty"] == 1 and c["texts_with_events"] == 3
    assert sum(out["disagree"].values()) == 0
    assert out["cause"] == Counter() or all("UNTRACED" not in k for k in out["cause"])
    assert c["determinism_checked"] == 3 == c["determinism_identical"]
    assert c["mutation_texts"] == 3
    assert out["mut"]["M_ORDER_SWAP__engine_detected"] == out["mut"]["M_ORDER_SWAP__applicable"] > 0
    assert out["mut"]["M_DOUBLE_CONSUME__both_detected"] == out["mut"]["M_DOUBLE_CONSUME__applicable"] > 0
    assert out["engine_inv_events"]["ENTITY_REUSED_AFTER_DISCARD"] == 0                 # Rung A opens a NEW lot after a discard: no resurrection
    assert sum(out["replay_status"].values()) == 3
    blk = T.family_block(out)
    assert blk["unexplained_total"] == 0 and blk["mutation_power"]["M_ORDER_SWAP"]["engine_detection_pct"] == 100.0
    assert_counts_only(T.plain(blk))


def test_classify_causes_traces_cascades_and_adapter_issues():
    events = [ev("E1", (0, 0), consumes=("NOPROD",), produces=("M",)),          # rejected: consumes an entity with no producer
              ev("E2", (1, 0), consumes=("M",), produces=("N",), depends=("E1",)),   # cascade: M never produced, E1 not applied
              ev("E3", (2, 0), consumes=("LATER",), produces=("Q",)),
              ev("E4", (3, 0), produces=("LATER",)),
              ev("E5", (4, 0), consumes=("Z",), depends=("MISSING",))]
    res, applied = T.replay_with_flags(events)
    adapted = SimpleNamespace(issues=[SimpleNamespace(code="ENTITY_WITHOUT_PRODUCER", path="NOPROD")])
    cause = Counter()
    T.classify_causes(events, applied, res, adapted, cause)
    assert cause["ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER"] == 1
    assert cause["ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED"] == 1
    assert cause["DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED"] == 1
    assert cause["ENTITY_UNKNOWN__CONSUMED_BEFORE_PRODUCED_IN_ORDER"] == 1
    assert cause["DEPENDENCY_NOT_APPLIED__DEPENDENCY_NOT_IN_GRAPH"] == 1
    assert cause["ENTITY_UNKNOWN__UNTRACED"] == 1                                  # Z: no producer anywhere and no adapter issue
    assert {k for k in cause if "UNTRACED" in k} == {"ENTITY_UNKNOWN__UNTRACED"}


def test_selection_is_deterministic_and_proportional():
    hits = sum(T.selected("s", f"r{i}", 20, "mut") for i in range(20000))
    assert 700 < hits < 1300
    assert T.selected("s", "r1", 20, "mut") == T.selected("s", "r1", 20, "mut")
    assert T.selected("s", "r1", 1, "x") is True


def test_partition_stats():
    c = Counter()
    T.partition_stats(_split(Fraction(1, 2), Fraction(1, 2)) + _split(None, None, "UNSPECIFIED"), c)
    assert c["partition_groups"] == 2 and c["partition_groups_basis_unspecified"] == 1
    assert c["partition_groups_with_two_or_more_allocations"] == 2 and c["partition_groups_checkable_basis_and_fraction"] == 1
