"""S178 FIX-EVAL: SCI-B CORP-4 / CORP-5 / CORP-6 on the corpus replay-invariant and verb-census tools. Synthetic inputs only.

Each test is built from the reviewer's failure scenario:
- CORP-4: the "independent" replay inherited the engine's apply/reject vector and imported its constants, so a wrong engine rejection
  or lifecycle mapping still showed 0 disagreements; every mutation was planted at a trivial position.
- CORP-5: ORDER_REGRESSION and EVENT_ID_REUSED hold by construction.
- CORP-6: determinism was checked in one process; the verb-census denominator depended on the outcome.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from fractions import Fraction

import pytest

from culinarystate.extraction import rung_a as ra
from culinarystate.extraction import rung_a_lexicon as lx
from culinarystate.extraction.rung_a import RungA
from culinarystate.extraction.rung_a_lexicon import build_lexicon
from culinarystate.state_graph import replay as RP
from culinarystate.state_graph.event_log import Allocation, EngineEvent, QuantityTerm
from tests.unit.test_s178_analysis_helpers import ROOT, load_tool
from tests.unit.test_step17b_rung_a import SCHEMA, SYN, TEXT

T = load_tool("s178_corpus_replay_invariants")
V = load_tool("s178_corpus_verb_census")


def ev(eid, order, *, consumes=(), produces=(), discards=(), types=(), allocs=(), depends=(), quantities=()):
    return EngineEvent(eid, order, kind="ACTION", consumes=tuple(consumes), produces=tuple(produces), discards=tuple(discards),
                       depends_on=tuple(depends), produced_types=tuple(types), allocations=tuple(allocs), quantities=tuple(quantities))


def intro(x, k=0):
    return ev(f"INTRO/{x}", (-1, k), produces=(x,), types=((x, "INGREDIENT_LOT"),))


def engine(events):
    res, applied = T.replay_with_flags(events)
    return res, applied


# ------------------------------------------------------------------ CORP-4: no engine constants, own apply vector
def test_local_constants_equal_the_engine_and_are_not_imported_from_it():
    assert T.PARTITION_KINDS_LOCAL == RP.PARTITION_KINDS
    assert T.LIFECYCLE_BY_TYPE_LOCAL == RP.LIFECYCLE_BY_TYPE
    assert T.DEFAULT_TRAJECTORY_LOCAL == RP.ReplayConfig().trajectory
    assert set(T.STRUCTURAL_CODES) <= RP.ISSUE_CODES
    assert RP.ISSUE_CODES - set(T.STRUCTURAL_CODES) == {"MASS_BALANCE_FAIL", "INFERRED_DEPENDENCY_IN_EXPLICIT_SCOPE",
                                                         "LOT_STATUS_CONTRADICTS_REPLAY", "LOT_NOT_IN_REPLAY"}
    src = (ROOT / "tools/s178_corpus_replay_invariants.py").read_text(encoding="utf-8")
    assert "import LIFECYCLE_BY_TYPE" not in src and "import PARTITION_KINDS" not in src
    assert "replay import ENGINE_VERSION, NOT_CHECKED" in src                  # metadata only


HAND_CASES = [
    [intro("A"), intro("B", 1), ev("E1", (0, 0), consumes=("A", "B"), produces=("M",), types=(("M", "MIXTURE"),)),
     ev("E2", (1, 0), consumes=("M",), produces=("N",))],
    [intro("A"), ev("E1", (2, 0), consumes=("A",), produces=("M",)), ev("E2", (1, 0), consumes=("M",), produces=("N",))],
    [intro("A"), intro("B", 1), ev("E1", (0, 0), consumes=("A",), produces=("M",)), ev("E2", (1, 0), consumes=("A",), produces=("N",)),
     ev("E3", (2, 0), discards=("B",)), ev("E4", (3, 0), consumes=("B",), produces=("P",))],
    [ev("E1", (0, 0), consumes=("GHOST",), produces=("M",)), ev("E2", (1, 0), consumes=("M",), produces=("N",), depends=("E1",))],
    [intro("A"), ev("E1", (0, 0), consumes=("A", "A"), produces=("M",))],                              # role conflict
    [intro("A"), ev("E1", (0, 0), consumes=("A",), produces=("X",),
                    allocs=(Allocation("L1", "SPLIT", "MASS", "Z", "X", Fraction(1, 2)),))],              # alloc parent not consumed
    [intro("A"), ev("E1", (0, 0), consumes=("A",), produces=("X",),
                    quantities=(QuantityTerm("Y", "g", Fraction(1), Fraction(1), "QNT-1"),))],        # quantity for unproduced
    [intro("A"), ev("E1", (0, 0), consumes=("A",), produces=("X", "Y"), types=(("X", "INTERMEDIATE"), ("Y", "INTERMEDIATE")),
                    allocs=(Allocation("L1", "SPLIT", "MASS", "A", "X", Fraction(2, 3)),
                            Allocation("L2", "SPLIT", "MASS", "A", "Y", Fraction(2, 3))))],
]


@pytest.mark.parametrize("events", HAND_CASES)
def test_independent_apply_vector_and_codes_equal_the_engine_on_hand_cases(events):
    res, applied = engine(events)
    viol, ind_applied, codes = T.independent_replay(events, mass_balance_fail=T.engine_mass_balance_fail(res))
    assert ind_applied == applied
    eng_codes = T.engine_structural_codes(res)
    assert [eng_codes.get(i, set()) for i in range(len(events))] == codes
    eng = T.engine_violations(res)
    assert {k: v for k, v in eng.items() if v} == {k: v for k, v in viol.items() if v}


def test_wrong_engine_lifecycle_mapping_is_now_a_disagreement(monkeypatch):
    """Reviewer: 'a wrong engine ... lifecycle mapping still shows 0 disagreements'. The engine is patched to map a
    DISCARDED_PORTION to ACTIVE; v0.1 imported the same (wrong) constant and agreed; the independent replay does not."""
    events = [intro("A"), ev("E1", (0, 0), consumes=("A",), produces=("X",), types=(("X", "DISCARDED_PORTION"),)),
              ev("E2", (1, 0), consumes=("X",), produces=("Y",))]
    monkeypatch.setattr(RP, "LIFECYCLE_BY_TYPE", {"RESERVED_PORTION": "RESERVED", "DISCARDED_PORTION": "ACTIVE"})
    res, applied = engine(events)
    assert applied == [True, True, True] and not T.engine_violations(res)          # the wrong engine accepts the reuse
    viol, ind_applied, _ = T.independent_replay(events, mass_balance_fail=T.engine_mass_balance_fail(res))
    assert viol["ENTITY_REUSED_AFTER_DISCARD"] == {2} and ind_applied[2] is False


def test_wrong_engine_rejection_is_now_a_disagreement(monkeypatch):
    """Reviewer: 'a wrong engine rejection ... still shows 0 disagreements'. The engine is patched to reject E1 spuriously;
    conditioned on the engine's vector (v0.1) the checker reproduces the cascade and agrees; the own vector disagrees."""
    events = [intro("A"), ev("E1", (0, 0), consumes=("A",), produces=("M",)), ev("E2", (1, 0), consumes=("M",), produces=("N",))]
    orig = RP._Run._quantity_terms

    def spurious(self, e, fail):
        if e.event_id == "E1":
            fail("QUANTITY_CONFLICT", "quantities/M")
        return orig(self, e, fail)

    monkeypatch.setattr(RP._Run, "_quantity_terms", spurious)
    res, applied = engine(events)
    assert applied == [True, False, False]
    eng = T.engine_violations(res)
    conditioned = T.independent_check(events, applied)                              # the v0.1 mode
    assert {k: v for k, v in conditioned.items() if v} == {k: v for k, v in eng.items() if v}     # v0.1 saw no disagreement
    viol, ind_applied, codes = T.independent_replay(events, mass_balance_fail=T.engine_mass_balance_fail(res))
    assert ind_applied == [True, True, True] and ind_applied != applied
    assert eng.get("ENTITY_UNKNOWN") == {2} and not viol.get("ENTITY_UNKNOWN")
    assert codes[1] != T.engine_structural_codes(res)[1]


def test_mass_balance_fail_is_the_only_engine_input():
    events = [intro("A"), ev("E1", (0, 0), consumes=("A",), produces=("M",)), ev("E2", (1, 0), consumes=("M",), produces=("N",))]
    _, ind_applied, _ = T.independent_replay(events, mass_balance_fail=frozenset({1}))
    assert ind_applied == [True, False, False]                                      # E1 rejected by mass balance, E2 cascades


# ------------------------------------------------------------------ CORP-4: mutations at drawn, non-trivial positions
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


LONG = TEXT + " Mix the onion with the oil. Add the leaf. Stir the dough. Add the grain. Discard the liquid. Mix the paste with the syrup."


def test_mutations_are_planted_at_drawn_positions_and_detected_there(rung):
    a, res, _ = _events(rung, LONG)
    positions = {k: set() for k in T.MUTATIONS}
    for n in range(40):
        for kind, want in T.MUTATIONS.items():
            m = T.mutate_at(a.events, kind, res, key=f"k{n}")
            if m is None:
                continue
            ev2, code_, pos = m
            assert code_ == want
            positions[kind].add((pos, len(ev2)))
            r2, _ = T.replay_with_flags(ev2, a.lot_accounting)
            ind2, _, _ = T.independent_replay(ev2, mass_balance_fail=T.engine_mass_balance_fail(r2))
            assert pos in T.engine_violations(r2).get(want, set()), (kind, pos)
            assert pos in ind2.get(want, set()), (kind, pos)
    for kind in ("M_ORDER_SWAP", "M_DOUBLE_CONSUME"):
        assert len(positions[kind]) >= 3, kind                                       # not always the same position
        assert any(0 < p < n - 1 for p, n in positions[kind]), kind                  # at least one interior position
    # v0.1 always swapped the first eligible pair and appended inserted events at the end
    old_like = {(p, n) for p, n in positions["M_DOUBLE_CONSUME"] if p == n - 1}
    assert old_like != positions["M_DOUBLE_CONSUME"]


def test_process_text_reports_planted_positions_and_zero_unexplained(rung, monkeypatch):
    monkeypatch.setattr(T, "_RUNG", rung)
    monkeypatch.setattr(T, "_SCHEMA", SCHEMA)
    monkeypatch.setattr(T, "MUT_EVERY", 1)
    monkeypatch.setattr(T, "DET_EVERY", 1)
    out = T.new_counts()
    for i, raw in enumerate([TEXT, LONG, "Reserve half of the liquid. Add the liquid to the onion."]):
        T.process_text(f"id{i}", raw, None, "seed", out)
    digests = out.pop("det_digests")
    assert len(digests) == 3
    blk = T.family_block(out)
    assert blk["unexplained_total"] == 0
    iv = blk["independent_applied_vector"]
    assert iv["apply_decision_disagreements"] == 0 and iv["issue_code_set_disagreements"] == 0
    for kind in ("M_ORDER_SWAP", "M_DOUBLE_CONSUME"):
        m = blk["mutation_power"][kind]
        assert m["applicable"] > 0 and m["independent_detected_at_planted_position"] == m["applicable"] == m["engine_detected_at_planted_position"]
    assert blk["invariants"]["ORDER_REGRESSION"]["by_construction"].startswith("HOLDS_BY_CONSTRUCTION")
    assert blk["invariants"]["EVENT_ID_REUSED"]["by_construction"].startswith("HOLDS_BY_CONSTRUCTION")
    assert blk["invariants"]["ENTITY_UNKNOWN"]["by_construction"] == "NOT_BY_CONSTRUCTION"
    from culinarystate.quantity.rc2_dryrun import assert_counts_only
    assert_counts_only(T.plain(blk))


def test_docstring_counts_seven_invariants_and_labels_the_tautologies():
    doc = T.__doc__
    assert "six invariants" not in doc.split("(v0.1")[0]
    assert len(T.INVARIANTS) == 7 and set(T.BY_CONSTRUCTION) == {"ORDER_REGRESSION", "EVENT_ID_REUSED"}
    assert "HOLDS_BY_CONSTRUCTION" in doc


# ------------------------------------------------------------------ CORP-6: determinism across processes
_DIGEST_SCRIPT = r"""
import hashlib, json, sys
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, sys.argv[1] + "/src")
from tests.unit.test_step17b_rung_a import SCHEMA, SYN, TEXT
from culinarystate.extraction import rung_a as ra, rung_a_lexicon as lx
from culinarystate.extraction.interfaces import SourceText
from culinarystate.state_graph.event_adapter import adapt_event_graph
from culinarystate.state_graph.replay import replay_events
rung = ra.RungA(lx.build_lexicon(**SYN))
out = {}
for i, raw in enumerate([TEXT, sys.argv[2]]):
    s = SourceText.from_raw("SYN", raw)
    r = rung.run(s, rung.config(), schema=SCHEMA)
    a = adapt_event_graph(s, r.graph, groundings=r.quantities, recomputers=rung.recomputers())
    res = replay_events(a.events, lot_accounting=a.lot_accounting)
    out[i] = [res.snapshot_sha256, hashlib.sha256(res.to_jsonl().encode()).hexdigest()]
print(json.dumps({"digests": out, "hash_probe": hash("culinarystate-hashseed-probe")}))
"""


def test_replay_digests_identical_across_processes_with_different_hash_seeds():
    got = []
    for seed in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        p = subprocess.run([sys.executable, "-c", _DIGEST_SCRIPT, str(ROOT), LONG], env=env, capture_output=True, text=True,
                           timeout=300, cwd=str(ROOT))
        assert p.returncode == 0, p.stderr[-2000:]
        got.append(json.loads(p.stdout.strip().splitlines()[-1]))
    assert got[0]["hash_probe"] != got[1]["hash_probe"]                              # the hash seeds really differ
    assert got[0]["digests"] == got[1]["digests"]


# ------------------------------------------------------------------ CORP-6: verb-census denominator fixed before the outcome
@pytest.fixture()
def food_verb_rung(monkeypatch):
    lex = build_lexicon(foods={"salt": ["ING-1"], "flour": ["ING-2"]},
                        procs={"salt": ["PROC-1"], "stir": ["PROC-2"], "quarter": ["PROC-3"]},
                        proc_info={"PROC-1": ("salt", "SEASONING", "ACTION"), "PROC-2": ("stir", "MECHANICAL_MIX", "ACTION"),
                                   "PROC-3": ("quarter", "CUTTING", "ACTION")},
                        tools={"bowl": ["TOOL-1"]}, tool_classes={}, units=[])
    monkeypatch.setattr(V, "_RUNG", RungA(lex))
    return lex


def test_mapped_food_or_closed_class_word_is_not_a_candidate(food_verb_rung):
    """v0.1: a word that is a food (or closed-class) word and maps to a PROC counted as a mapped candidate, but the same word
    unmapped was excluded, so the mapped share depended on the outcome. v0.2 filters first."""
    got = V.count_texts(["Salt the flour. Stir the flour. Quarter the flour."])          # "quarter" is closed-class and a cutting verb
    c = got["c"]
    assert c["action_events"] == 3
    assert c["cand_slot"] == 1 and c["cand_slot_mapped"] == 1                        # only "Stir"
    assert c["cand_init"] == 1 and c["cand_init_mapped"] == 1
    assert c["action_excluded_by_filter"] == 2
    assert c["action_excluded_food_or_tool"] == 1 and c["action_excluded_closed_class"] == 1
    assert c["slot_food_or_tool_word"] == 1 and c["slot_closed_class"] == 1


def test_denominator_is_the_same_whether_or_not_the_word_maps(monkeypatch):
    def census(procs):
        lex = build_lexicon(foods={"salt": ["ING-1"], "flour": ["ING-2"]}, procs=procs,
                            proc_info={v[0]: (k, "SEASONING", "ACTION") for k, v in procs.items()}, tools={}, tool_classes={}, units=[])
        monkeypatch.setattr(V, "_RUNG", RungA(lex))
        return V.count_texts(["Salt the flour. Fumble the flour."])["c"]
    mapped, unmapped = census({"salt": ["PROC-1"]}), census({"stir": ["PROC-9"]})
    assert mapped["cand_slot"] == unmapped["cand_slot"] == 1                         # "Fumble" only, in both worlds
    assert mapped["cand_init"] == unmapped["cand_init"] == 1


def test_verb_census_writes_versioned_names():
    assert V.TOOL_VERSION.endswith("0.2.0-draft") and V.CSV_TAG == "_v2"
    import inspect
    assert 'default="verb_coverage_census_v2"' in inspect.getsource(V.main)
