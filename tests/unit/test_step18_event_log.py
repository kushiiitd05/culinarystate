"""Step 18a/18c append-only event log and canonical JSON (DRAFT_PENDING_16c).

Status: DRAFT_PENDING_16c (hard gate 16c open). Synthetic events only: no EVT /
ENTITY / STATE ledger row is read or written. Covers canonical JSON (no pandas),
engine event validation, the hash-chained append-only log with revisions, and the
JSONL writer that refuses protected areas, ledger file names and overwrites.
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from culinarystate.state_graph import event_log as el
from culinarystate.state_graph.event_log import (
    Allocation, EngineEvent, EventLog, EventLogError, QuantityTerm, canonical_json, sha256_canonical,
)

ROOT = Path(__file__).resolve().parents[2]


def ev(eid: str, order: tuple[int, int], **kw) -> EngineEvent:
    return EngineEvent(event_id=eid, order=order, **kw)


def chain(n: int) -> list[EngineEvent]:
    out = [ev("INTRO/L0", (-1, 0), produces=("L0",), produced_types=(("L0", "INGREDIENT_LOT"),))]
    for i in range(1, n):
        out.append(ev(f"E{i}", (i, 0), consumes=(f"N{i - 1}" if i > 1 else "L0",), produces=(f"N{i}",),
                      produced_types=((f"N{i}", "INTERMEDIATE"),)))
    return out


# ---------------------------------------------------------------- module
def test_module_is_draft_pending_16c_and_imports_no_pandas():
    assert el.STATUS == "DRAFT_PENDING_16c"
    src = Path(el.__file__).read_text(encoding="utf-8")
    assert "DRAFT_PENDING_16c" in src.splitlines()[0]
    assert "import pandas" not in src and "import numpy" not in src


def test_vocabularies_follow_the_step16_drafts():
    alloc = json.loads((ROOT / "reports/step16/schema_drafts/ALLOC.draft_v1.schema.json").read_text())
    evt = json.loads((ROOT / "reports/step16/schema_drafts/EVT.draft_v1.schema.json").read_text())
    assert set(el.ALLOC_KINDS) == set(alloc["properties"]["kind"]["enum"])
    assert set(el.ALLOC_BASES) == set(alloc["properties"]["basis"]["enum"])
    assert set(el.TRAJECTORIES) == set(evt["properties"]["trajectory"]["enum"])


# ---------------------------------------------------------------- canonical JSON
def test_canonical_json_is_sorted_compact_and_exact():
    a = canonical_json({"b": 1, "a": (Fraction(1, 3), "é"), "c": None})
    assert a == '{"a":["1/3","é"],"b":1,"c":null}'
    assert canonical_json({"c": None, "a": (Fraction(1, 3), "é"), "b": 1}) == a
    assert canonical_json(Fraction(4, 2)) == '"2/1"'


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), {1: "x"}, {"s": {1, 2}}, object(), b"raw"])
def test_canonical_json_rejects_ambiguous_values(bad):
    with pytest.raises(EventLogError):
        canonical_json(bad)


def test_sha256_canonical_ignores_insertion_order():
    assert sha256_canonical({"x": 1, "y": 2}) == sha256_canonical({"y": 2, "x": 1})
    assert len(sha256_canonical([])) == 64


# ---------------------------------------------------------------- event validation
@pytest.mark.parametrize("kw", [
    dict(event_id=" ", order=(0, 0)),
    dict(event_id="E", order=(0,)),
    dict(event_id="E", order=(0, 1.0)),
    dict(event_id="E", order=(0, 0), revision=-1),
    dict(event_id="E", order=(0, 0), revision=True),
    dict(event_id="E", order=(0, 0), trajectory="GUESSED"),
    dict(event_id="E", order=(0, 0), claim_route="HUMAN"),
    dict(event_id="E", order=(0, 0), consumes=["N1"]),
    dict(event_id="E", order=(0, 0), produces=("N1",), produced_types=(("N2", "INTERMEDIATE"),)),
    dict(event_id="E", order=(0, 0), attributes=(("proc_id", "P"), ("proc_id", "Q"))),
])
def test_engine_event_rejects_malformed_fields(kw):
    with pytest.raises(EventLogError):
        EngineEvent(**kw)


@pytest.mark.parametrize("kw", [
    dict(kind="SPLIT_EVENLY", basis="MASS"),
    dict(kind="SPLIT", basis="WEIGHT"),
    dict(kind="SPLIT", basis="MASS", fraction=0.5),
    dict(kind="SPLIT", basis="MASS", fraction=(Fraction(1, 2),)),
    dict(kind="SPLIT", basis="MASS", parent=""),
])
def test_allocation_rejects_malformed_fields(kw):
    base = dict(alloc_id="A1", kind="SPLIT", basis="MASS", parent="P", child="C", fraction=None)
    base.update(kw)
    with pytest.raises(EventLogError):
        Allocation(**base)


@pytest.mark.parametrize("kw", [
    dict(ref=""),
    dict(dim="kg"),
    dict(low=Fraction(2), high=Fraction(1)),
    dict(low=1.5, high=Fraction(2)),
    dict(low=Fraction(-1), high=Fraction(1)),
])
def test_quantity_term_needs_a_trace_ref_exact_bounds_and_no_unit_conversion(kw):
    base = dict(entity_id="N1", dim="g", low=Fraction(1), high=Fraction(2), ref="Q1")
    base.update(kw)
    with pytest.raises(EventLogError):
        QuantityTerm(**base)


def test_event_canonical_round_trip_and_hash():
    e = ev("E1", (1, 0), revision=2, kind="ACTION", consumes=("N0",), produces=("N1", "N2"),
           produced_types=(("N1", "RESERVED_PORTION"), ("N2", "INTERMEDIATE")),
           allocations=(Allocation("A1", "RESERVE", "MASS", "N0", "N1", Fraction(1, 4)),
                        Allocation("A2", "REMAINDER", "MASS", "N0", "N2", None),
                        Allocation("A3", "SPLIT", "COUNT", "N0", "N2", (Fraction(1, 4), Fraction(1, 3)))),
           quantities=(QuantityTerm("N1", "g", Fraction(25), Fraction(30), "Q1"),),
           attributes=(("proc_id", "PROC-1"),), claim_route="EXPLICIT", source_ref="SYN#E1")
    d = e.to_canonical()
    assert EngineEvent.from_canonical(json.loads(canonical_json(d))) == e
    assert e.sha256 == sha256_canonical(d)
    assert e.sha256 != ev("E1", (1, 0)).sha256


# ---------------------------------------------------------------- append-only log
def test_append_assigns_seq_and_hash_chain():
    log = EventLog()
    entries = [log.append(e) for e in chain(3)]
    assert [x.seq for x in entries] == [0, 1, 2]
    assert entries[0].prev_sha256 == el.GENESIS_SHA256
    assert entries[1].prev_sha256 == entries[0].entry_sha256
    assert log.head_sha256 == entries[-1].entry_sha256
    assert isinstance(log.entries, tuple) and len(log) == 3


def test_revisions_are_appended_never_rewritten():
    log = EventLog()
    for e in chain(3):
        log.append(e)
    fixed = ev("E1", (1, 0), revision=1, consumes=("L0",), produces=("N1",), produced_types=(("N1", "MIXTURE"),))
    log.append(fixed)
    assert len(log) == 4 and log.entries[1].event.revision == 0           # original kept
    eff = log.effective()
    assert [e.event_id for e in eff] == ["INTRO/L0", "E1", "E2"]           # position of first appearance
    assert eff[1] == fixed


@pytest.mark.parametrize("bad", [
    ev("E1", (1, 0)),                       # same id + revision again
    ev("E1", (1, 0), revision=2),           # revision gap
    ev("E9", (9, 0), revision=1),           # first revision must be 0
])
def test_append_refuses_duplicate_or_gapped_revisions(bad):
    log = EventLog()
    log.append(ev("E1", (1, 0)))
    with pytest.raises(EventLogError):
        log.append(bad)
    assert len(log) == 1


def test_log_exposes_no_rewrite_operations():
    log = EventLog()
    for name in ("remove", "pop", "insert", "replace", "clear", "__setitem__", "__delitem__", "truncate"):
        assert not hasattr(log, name)
    with pytest.raises((AttributeError, TypeError)):
        log.entries[0] = None  # type: ignore[index]


def test_jsonl_round_trip_is_byte_identical():
    log = EventLog()
    for e in chain(4):
        log.append(e)
    text = log.to_jsonl()
    assert text.endswith("\n") and text.count("\n") == 4
    again = EventLog.from_jsonl(text)
    assert again.to_jsonl() == text and again.head_sha256 == log.head_sha256


def test_from_jsonl_detects_tampering():
    log = EventLog()
    for e in chain(3):
        log.append(e)
    lines = log.to_jsonl().splitlines()
    rec = json.loads(lines[1])
    rec["event"]["produces"] = ["N_X"]
    tampered = "\n".join([lines[0], canonical_json(rec), lines[2]]) + "\n"
    with pytest.raises(EventLogError):
        EventLog.from_jsonl(tampered)
    with pytest.raises(EventLogError):                                    # non-canonical spacing
        EventLog.from_jsonl(lines[0].replace(":", ": ", 1) + "\n")
    with pytest.raises(EventLogError):                                    # dropped line breaks the chain
        EventLog.from_jsonl("\n".join([lines[0], lines[2]]) + "\n")


# ---------------------------------------------------------------- JSONL writer
def test_writer_creates_new_file_and_refuses_overwrite(tmp_path):
    log = EventLog()
    for e in chain(2):
        log.append(e)
    p = el.write_log_jsonl(log, tmp_path / "out" / "events.jsonl")
    assert p.read_text(encoding="utf-8") == log.to_jsonl()
    with pytest.raises(EventLogError):
        el.write_log_jsonl(log, p)


@pytest.mark.parametrize("rel", ["ledgers/data/x.jsonl", "ledgers/recipe_semantics/x.jsonl", "data/raw/x.jsonl",
                                 "data/x.jsonl", "exports/transition_tuples/x.jsonl", "annotation/gold/x.jsonl",
                                 "ledgers/../ledgers/data/y.jsonl"])
def test_writer_refuses_protected_areas(rel):
    log = EventLog()
    log.append(chain(1)[0])
    with pytest.raises(EventLogError):
        el.write_log_jsonl(log, ROOT / rel)
    assert not (ROOT / rel).exists()


@pytest.mark.parametrize("name", ["EVT.jsonl", "ENTITY.jsonl", "STATE.jsonl", "ALLOC.jsonl", "REF.jsonl",
                                  "GRAPH.jsonl", "INST.jsonl", "evt.jsonl"])
def test_writer_refuses_ledger_file_names_anywhere(tmp_path, name):
    log = EventLog()
    log.append(chain(1)[0])
    with pytest.raises(EventLogError):
        el.write_log_jsonl(log, tmp_path / name)


def test_extend_appends_only_new_lines_and_refuses_a_rewrite(tmp_path):
    log = EventLog()
    events = chain(4)
    for e in events[:2]:
        log.append(e)
    p = el.write_log_jsonl(log, tmp_path / "events.jsonl")
    first = p.read_bytes()
    for e in events[2:]:
        log.append(e)
    assert el.extend_log_jsonl(log, p) == 2
    assert p.read_bytes().startswith(first) and p.read_text(encoding="utf-8") == log.to_jsonl()
    other = EventLog()
    other.append(ev("INTRO/Z", (-1, 0), produces=("Z",)))
    with pytest.raises(EventLogError):                                    # file is not a prefix of `other`
        el.extend_log_jsonl(other, p)
    assert p.read_text(encoding="utf-8") == log.to_jsonl()
    with pytest.raises(EventLogError):
        el.extend_log_jsonl(log, tmp_path / "missing.jsonl")


def test_write_canonical_jsonl_shares_the_guards(tmp_path):
    p = el.write_canonical_jsonl([{"b": 1, "a": Fraction(1, 2)}], tmp_path / "tx.jsonl")
    assert p.read_text(encoding="utf-8") == '{"a":"1/2","b":1}\n'
    with pytest.raises(EventLogError):
        el.write_canonical_jsonl([{}], p)
    with pytest.raises(EventLogError):
        el.write_canonical_jsonl([{}], tmp_path / "STATE.jsonl")


# ---------------------------------------------------------------- properties
@settings(max_examples=40, deadline=None)
@given(n=st.integers(min_value=1, max_value=8), cut=st.integers(min_value=0, max_value=8))
def test_property_appending_never_changes_earlier_bytes(n, cut):
    events = chain(n)
    cut = min(cut, n)
    log = EventLog()
    for e in events[:cut]:
        log.append(e)
    before = log.to_jsonl()
    heads = [x.entry_sha256 for x in log.entries]
    for e in events[cut:]:
        log.append(e)
    assert log.to_jsonl().startswith(before)
    assert [x.entry_sha256 for x in log.entries[:cut]] == heads


@settings(max_examples=40, deadline=None)
@given(st.recursive(st.none() | st.booleans() | st.integers() | st.text(max_size=5)
                    | st.fractions(max_denominator=50),
                    lambda inner: st.lists(inner, max_size=3) | st.dictionaries(st.text(max_size=3), inner,
                                                                                max_size=3), max_leaves=10))
def test_property_canonical_json_is_deterministic(obj):
    assert canonical_json(obj) == canonical_json(obj)
    json.loads(canonical_json(obj))
