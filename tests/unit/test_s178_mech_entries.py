"""Draft MECH entries + G21.2 / G21.3 / G21.4 / G21.8 checkers (S178 lane MECH, T5-C01-R1 / R2).

The entries are AI_DRAFTED; passing says the draft file is well formed and honest about its evidence, not that any entry is
reviewed, sourced or true (G21.1 / G21.5-G21.7 are human gates)."""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from culinarystate.mechanism import mech_contract as MC
from culinarystate.mechanism import mech_entries as ME
from culinarystate.mechanism import mech_inputs as MI
from culinarystate.mechanism import mech_registry_check as RC

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def entries():
    return ME.load(ME.OUT_PATH)


def test_committed_file_is_a_fresh_deterministic_build():
    assert ME.OUT_PATH.read_text(encoding="utf-8") == ME.dumps(ME.build())
    assert ME.dumps(ME.build()) == ME.dumps(ME.build())


def test_every_entry_validates_v1_1_and_semantics(entries):
    cv, eff = MC.read_cv_rows(), MC.read_effect_rows()
    assert len(entries) == 32 == len({x["mech"]["mechanism_key"] for x in entries})
    roster = {r["mechanism_key"] for r in ME.read_roster()}
    assert {x["mech"]["mechanism_key"] for x in entries} == roster
    for x in entries:
        m = x["mech"]
        assert MC.schema_errors(m) == [], m["mechanism_key"]
        assert MC.semantic_problems(m, cv, effect_rows=eff) == [], m["mechanism_key"]
    mech = [x["mech"] for x in entries]
    assert MC.asymmetric_links(mech) == [] and MC.unresolved_links(mech) == []


def test_gate_report(entries):
    rep = RC.check(entries)
    assert rep["G21_2"]["pass"] and rep["G21_3"]["pass"] and rep["G21_8"]["pass"]
    assert rep["G21_4"] == {"pass": False, "entries_counted": 0, "entries": 32,
                            "rule": "ONLY_SOURCED_ENTRIES_COUNT_UNSOURCED_NEVER"}       # honest: no source was opened
    assert rep["envelope_problems"] == [] and rep["schema_invalid_entries"] == [] and rep["semantic_problem_entries"] == []
    assert rep["screen_subset_entries"] >= 14 and rep["xrefs_accepted"] == 0 and rep["consumable_for_applicability"] == 0


def test_honest_labels_and_zero_numbers(entries):
    for x in entries:
        m = x["mech"]
        assert x["provenance_class"] == "AI_DRAFTED" and x["evidence_status"] == "UNSOURCED"
        assert x["counts_toward_g21_4"] is False and m["evidence_refs"] == []
        assert m["provenance_class"] == "INFERRED_LLM" and m["ai_drafted"] is True
        assert m["review_status"] == "CANDIDATE" and m["verification"]["status"] == "UNVERIFIED"
        assert m["id"].startswith("MECH-9") and x["id_status"] == "DRAFT_BLOCK_NOT_MINTED"
        assert RC.numeric_leaves(m) == [] and RC.kinetic_keys(m) == []
        for g in m["condition_gates"]:
            if g["interval"]:
                assert g["interval"]["min"]["status"] == g["interval"]["max"]["status"] == "NOT_REPORTED"
        assert MC.consumable_for_applicability(m)[0] is False


def test_window_refs_exist_and_cited_windows_belong_to_the_key(entries):
    known, by_key = ME.window_ids(), ME.windows_by_key()
    for x in entries:
        assert set(x["window_refs"]) <= known
        assert set(x["window_refs_cited_in_rationale"]) <= set(by_key.get(x["mech"]["mechanism_key"], []))


def test_screen_binding_covers_every_evaluable_item(entries):
    subset = ME.screen_entries(entries)
    assert len(subset) >= 14
    for x in subset:
        m, b = x["mech"], x["screen_binding"]
        assert not m["gates_unknown"] and m["preconditions"]
        need = {p["precondition_key"] for p in m["preconditions"]} \
            | {g["gate_key"] for g in m["condition_gates"] if g["gate_type"] == "NECESSARY"} \
            | {i["inhibitor_key"] for i in m["inhibitors_mitigators"]}
        assert set(b["items"]) == need == set(b["evaluation_order"])
        assert all(it["evaluator"] in MI.EVALUATORS for it in b["items"].values())
        assert set(b["modulating_gates_not_evaluated"]) == {g["gate_key"] for g in m["condition_gates"]
                                                            if g["gate_type"] == "MODULATING"}
        # a CHEMICAL_REACTION never carries a NECESSARY temperature gate (no switch; E-7)
        if m["kind"] == "CHEMICAL_REACTION":
            assert not [g for g in m["condition_gates"] if g["gate_type"] == "NECESSARY"]
    for x in entries:
        if not x["screen_subset"]:
            assert x["screen_binding"] is None and x["mech"]["gates_unknown"] is True


# ----------------------------------------------------------------------------- negative controls of the checkers
def _mut(entries, key, fn):
    out = copy.deepcopy(entries)
    fn(next(x for x in out if x["mech"]["mechanism_key"] == key))
    return out


def test_g21_8_catches_a_number_and_a_kinetic_key(entries):
    bad = _mut(entries, "LEACHING", lambda x: x["mech"]["condition_gates"].append(
        {**copy.deepcopy(next(e for e in entries if e["mech"]["mechanism_key"] == "STARCH_GELATINISATION")
                         ["mech"]["condition_gates"][0]), "gate_key": "CG09"}))
    bad[0]["mech"]["notes"] = None
    leach = next(x for x in bad if x["mech"]["mechanism_key"] == "LEACHING")
    leach["mech"]["condition_gates"][-1]["interval"]["min"] = {"status": "STATED", "value": 330.0, "inclusive": True}
    assert not RC.check(bad)["G21_8"]["pass"]
    assert RC.kinetic_keys({"x": {"Ea": 80.0}}) == ["/x/Ea"]
    assert RC.kinetic_keys({"consecutive_with": [{"order": "THIS_PRECEDES_OTHER"}]}) == []


def test_g21_2_and_g21_3_negative_controls(entries):
    rep = RC.check([x for x in entries if x["mech"]["mechanism_key"] != "LEACHING"])
    assert not rep["G21_2"]["pass"] and "LEACHING" in rep["G21_2"]["missing"]
    m = copy.deepcopy(entries[0]["mech"])
    m.update(preconditions=[], condition_gates=[], inhibitors_mitigators=[], gates_unknown=False)
    assert not RC.g21_3_ok(m)
    assert MC.schema_errors(m)                                   # the schema refuses it too


def test_evidence_envelope_negative_controls(entries):
    known, ev = ME.window_ids(), set(MI.EVALUATORS)
    ref = {"evidence_id": "DOC-000001", "doc_type": "PRIMARY", "supports": ["GATE"], "locator": "p. 3",
           "lineage_root_id": None, "lineage_status": "UNKNOWN"}
    x = copy.deepcopy(entries[0])
    x["mech"]["evidence_refs"] = [ref]
    assert any("UNSOURCED but evidence_refs" in p for p in RC.envelope_problems(x, known, ev))
    x["evidence_status"] = "SOURCED"
    x["counts_toward_g21_4"] = True
    assert RC.sourced(x) and RC.envelope_problems(x, known, ev) == []
    x["mech"]["evidence_refs"] = [{**ref, "locator": None}]
    assert not RC.sourced(x) and RC.envelope_problems(x, known, ev)
    y = copy.deepcopy(next(e for e in entries if e["screen_subset"]))
    y["screen_binding"]["items"].pop(next(iter(y["screen_binding"]["items"])))
    assert any("binding items" in p for p in RC.envelope_problems(y, known, ev))
    z = copy.deepcopy(entries[0])
    z["provenance_class"] = "HUMAN"
    assert RC.envelope_problems(z, known, ev)
