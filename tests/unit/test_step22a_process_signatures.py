"""Step 22a process-level signatures over PROC x modifiers x MECH (S158, DRAFT_PENDING_21b_H4).

SYNTHETIC fixtures only (tests/fixtures/step22a_23a_fixtures.py): placeholder processes, mechanisms and rules.
No real process-to-mechanism rule exists or is authored here; the shared case set is not sealed (human gate).
Plan Step 22 card: sign only, never a magnitude; is_evidence false; requires_gate_eval true; endpoint cues are
never a trigger or condition input; candidate generation is recall-oriented (Step 23 is the precision gate).
"""
from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

import pytest

from culinarystate.mechanism import mech_contract as MC
from culinarystate.mechanism import process_signatures as PS
from tests.fixtures.mech_v1_1_fixtures import entry
from tests.fixtures.step22a_23a_fixtures import HIERARCHY_ROWS, accepted_target, mech, rule


def hier() -> PS.ProcessHierarchy:
    return PS.hierarchy_from_rows(HIERARCHY_ROWS)


def build(rules: list[dict[str, Any]], entries: list[dict[str, Any]], **kw: Any) -> PS.SignatureBuild:
    return PS.build_signatures([PS.SignatureRule(**r) for r in rules], entries, hier(), **kw)


def walk_keys(x: Any) -> set[str]:
    if isinstance(x, dict):
        return set(x) | set().union(*(walk_keys(v) for v in x.values())) if x else set()
    if isinstance(x, (list, tuple)):
        return set().union(*(walk_keys(v) for v in x)) if x else set()
    return set()


# ----------------------------------------------------------------------------- constants and header
def test_header_and_contract_constants() -> None:
    assert PS.STATUS == "DRAFT_PENDING_21b_H4"
    assert PS.MODIFIER_AXES == ("INTENSITY", "GEOMETRY", "GRANULARITY", "MEDIUM")
    assert "ENDPOINT" in PS.REFUSED_MODIFIER_AXES and "ENDPOINT" not in PS.MODIFIER_AXES
    assert PS.PROVENANCE_CLASS == "MODEL_ESTIMATED" and PS.CANDIDATE_LABEL == "CANDIDATE"
    assert "DRAFT_PENDING_21b_H4" in (PS.__doc__ or "")


# ----------------------------------------------------------------------------- PROC hierarchy
def test_hierarchy_descendants_ancestors_and_endpoints() -> None:
    h = hier()
    assert h.process_ids_under("FAM:SYNTH_FAMILY") == ("PROC-SYN001", "PROC-SYN002")
    assert h.process_ids_under("PROC-SYN001") == ("PROC-SYN001",)
    assert h.ancestors("PROC-SYN001") == ("FAM:SYNTH_FAMILY",)
    assert h.is_endpoint("PROC-SYN900") and not h.is_endpoint("PROC-SYN001")
    assert h.contains("ALIAS:PROC-SYN001:a") and not h.contains("PROC-SYN777")


def test_hierarchy_problems_are_reported() -> None:
    assert PS.hierarchy_problems(HIERARCHY_ROWS) == []
    dup = HIERARCHY_ROWS + [dict(HIERARCHY_ROWS[2])]
    orphan = HIERARCHY_ROWS + [dict(HIERARCHY_ROWS[2], id="PROC-SYN004", proposed_parent_id="FAM:MISSING")]
    cyc = [dict(r) for r in HIERARCHY_ROWS]
    cyc[0]["proposed_parent_id"] = "PROC-SYN001"
    for rows in (dup, orphan, cyc):
        assert PS.hierarchy_problems(rows)
        with pytest.raises(PS.SignatureError):
            PS.hierarchy_from_rows(rows)


def test_real_process_hierarchy_draft_loads_without_structural_problems() -> None:
    h = PS.read_process_hierarchy()
    assert PS.HIERARCHY_PATH.name == "process_hierarchy_v1_DRAFT.csv"
    assert PS.hierarchy_problems(PS.read_hierarchy_rows()) == []
    fams = [n for n in h.node_ids if n.startswith("FAM:")]
    assert len(fams) == 17
    assert sum(h.is_endpoint(n) for n in h.node_ids) == 9


# ----------------------------------------------------------------------------- builder
def test_builder_emits_one_signature_per_rule_and_mechanism_from_the_mech_read_api() -> None:
    e = mech()
    out = build([rule(process_ref="FAM:SYNTH_FAMILY")], [e])
    assert out.problems == ()
    (s,) = out.signatures
    assert s.signature_key == "SYNTH_RULE_ONE:SYNTH_FIXTURE_ONE"
    assert s.process_ids_covered == ("PROC-SYN001", "PROC-SYN002")
    assert s.mechanism_id == "MECH-000001" and s.mech_consumable and s.mech_refusal_reasons == ()
    assert s.candidate_effects == MC.candidate_effects(e)
    assert s.required_condition_axes == MC.required_condition_axes(e)
    assert s.required_state_inputs == MC.required_state_inputs(e)
    assert s.requires_gate_eval is True and s.is_evidence is False
    assert s.provenance_class == "MODEL_ESTIMATED" and s.label == "CANDIDATE" and s.status == PS.STATUS


def test_signature_holds_signs_only_and_never_a_magnitude() -> None:
    (s,) = build([rule()], [mech()]).signatures
    keys = walk_keys(s.to_canonical())
    assert not keys & PS.MAGNITUDE_KEYS
    assert {d for c in s.candidate_effects for d in c.allowed_directions} <= {"INCREASE", "DECREASE", "UNKNOWN"}


def test_non_consumable_entries_are_kept_for_recall_with_their_refusal_reasons() -> None:
    (s,) = build([rule()], [entry()]).signatures
    assert s.mech_consumable is False
    assert "NOT_ACCEPTED" in s.mech_refusal_reasons and "GATES_UNKNOWN" in s.mech_refusal_reasons


def test_rule_problems_block_the_rule_and_never_invent_a_link() -> None:
    bad = {
        "unknown mechanism": rule(mechanism_keys=("SYNTH_NOT_IN_REGISTRY",)),
        "no mechanism": rule(mechanism_keys=()),
        "unknown process": rule(process_ref="PROC-SYN777"),
        "endpoint process": rule(process_ref="PROC-SYN900"),
        "alias process": rule(process_ref="ALIAS:PROC-SYN001:a"),
        "endpoint modifier": rule(modifier_predicates=(PS.ModifierPredicate("ENDPOINT", "IS", ("GOLDEN",)),)),
        "unknown modifier axis": rule(modifier_predicates=(PS.ModifierPredicate("COLOUR", "IS", ("X",)),)),
        "bad operator": rule(modifier_predicates=(PS.ModifierPredicate("INTENSITY", "GT", ("X",)),)),
        "IN with one value": rule(modifier_predicates=(PS.ModifierPredicate("INTENSITY", "IN", ("X",)),)),
        "lower-case value": rule(modifier_predicates=(PS.ModifierPredicate("INTENSITY", "IS", ("gentle",)),)),
        "UNKNOWN as value": rule(modifier_predicates=(PS.ModifierPredicate("INTENSITY", "IS", ("UNKNOWN",)),)),
        "heat-transfer id": rule(heat_transfer_mode_ids=("HT-999",)),
        "deterministic change": rule(deterministic_change_refs=("BOIL_OFF",)),
        "bad rule key": rule(rule_key="lower case"),
    }
    for name, r in bad.items():
        out = build([r], [mech()], heat_transfer_mode_ids=frozenset({"HT-001"}))
        assert out.signatures == () and out.problems, name


def test_schema_invalid_entries_and_duplicate_rule_keys_are_problems() -> None:
    broken = mech()
    broken["is_evidence"] = True
    out = build([rule()], [broken])
    assert out.signatures == () and any("schema" in p for p in out.problems)
    out = build([rule(), rule()], [mech()])
    assert any("duplicate rule_key" in p for p in out.problems)
    out = build([rule()], [mech(), mech()])
    assert any("duplicate mechanism_key" in p for p in out.problems)


def test_valid_heat_transfer_and_deterministic_refs_are_carried() -> None:
    r = rule(heat_transfer_mode_ids=("HT-001",), deterministic_change_refs=("SPLIT",),
             modifier_predicates=(PS.ModifierPredicate("INTENSITY", "IN", ("SYNTH_LOW", "SYNTH_HIGH")),))
    out = build([r], [mech()], heat_transfer_mode_ids=frozenset({"HT-001"}))
    assert out.problems == ()
    (s,) = out.signatures
    assert s.heat_transfer_mode_ids == ("HT-001",) and s.deterministic_change_refs == ("SPLIT",)


def test_default_heat_transfer_ids_are_read_from_the_registry() -> None:
    ids = PS.read_heat_transfer_mode_ids()
    assert "HT-001" in ids
    assert build([rule(heat_transfer_mode_ids=("HT-001",))], [mech()]).problems == ()


def test_build_is_deterministic_and_order_independent() -> None:
    rules = [rule(), rule(rule_key="SYNTH_RULE_TWO", process_ref="PROC-SYN003")]
    a = build(rules, [mech()])
    b = build(list(reversed(rules)), [mech()])
    assert [s.sha256() for s in a.signatures] == [s.sha256() for s in b.signatures]
    assert [s.signature_key for s in a.signatures] == sorted(s.signature_key for s in a.signatures)


# ----------------------------------------------------------------------------- validator
def test_signature_validator_accepts_built_signatures_and_finds_tampering() -> None:
    e = mech(affected_targets=[accepted_target(), accepted_target("TGT02", ("INCREASE",), "synthetic_other", effect="FORMED")])
    (s,) = build([rule()], [e]).signatures
    good = s.to_canonical()
    assert PS.signature_problems(good, [e], hier()) == []

    def tamper(fn: Any) -> dict[str, Any]:
        x = copy.deepcopy(good)
        fn(x)
        return x

    bad = {
        "evidence": tamper(lambda x: x.update(is_evidence=True)),
        "gate eval": tamper(lambda x: x.update(requires_gate_eval=False)),
        "provenance": tamper(lambda x: x.update(provenance_class="MEASURED")),
        "dropped target": tamper(lambda x: x["candidate_effects"].pop()),
        "dropped axis": tamper(lambda x: x["required_condition_axes"].pop()),
        "dropped state input": tamper(lambda x: x["required_state_inputs"].pop()),
        "widened sign": tamper(lambda x: x["candidate_effects"][0].update(allowed_directions=["DECREASE", "INCREASE"])),
        "magnitude": tamper(lambda x: x["candidate_effects"][0].update(magnitude=0.5)),
        "status": tamper(lambda x: x.update(status="APPROVED")),
        "unknown mechanism": tamper(lambda x: x["mechanism"].update(mechanism_key="SYNTH_OTHER_KEY")),
        "covered process": tamper(lambda x: x["trigger"].update(process_ids_covered=["PROC-SYN003"])),
        "consumable flag": tamper(lambda x: x["mechanism"].update(consumable=False)),
    }
    for name, inst in bad.items():
        assert PS.signature_problems(inst, [e], hier()), name


# ----------------------------------------------------------------------------- matching an event's process
def test_match_signatures_by_process_and_modifiers() -> None:
    pred = PS.ModifierPredicate("INTENSITY", "IS", ("SYNTH_LOW",))
    sigs = build([rule(process_ref="FAM:SYNTH_FAMILY", modifier_predicates=(pred,)),
                  rule(rule_key="SYNTH_RULE_TWO", process_ref="PROC-SYN003")], [mech()]).signatures
    (m,) = PS.match_signatures(sigs, "PROC-SYN002", {"INTENSITY": "SYNTH_LOW"})
    assert m.signature.rule_key == "SYNTH_RULE_ONE" and m.modifier_status == "MATCHED" and m.missing_modifiers == ()
    (m,) = PS.match_signatures(sigs, "PROC-SYN001", {})
    assert m.modifier_status == "MODIFIER_UNKNOWN" and m.missing_modifiers == ("INTENSITY",)
    (m,) = PS.match_signatures(sigs, "PROC-SYN001", {"INTENSITY": None})
    assert m.modifier_status == "MODIFIER_UNKNOWN"
    assert PS.match_signatures(sigs, "PROC-SYN001", {"INTENSITY": "SYNTH_HIGH"}) == ()
    assert [x.signature.rule_key for x in PS.match_signatures(sigs, "PROC-SYN003", {})] == ["SYNTH_RULE_TWO"]
    assert PS.match_signatures(sigs, "PROC-SYN777", {}) == ()


def test_an_endpoint_cue_is_never_accepted_as_a_modifier_input() -> None:
    sigs = build([rule()], [mech()]).signatures
    with pytest.raises(PS.SignatureError, match="ENDPOINT"):
        PS.match_signatures(sigs, "PROC-SYN001", {"ENDPOINT": "GOLDEN"})


def test_negated_predicates() -> None:
    pred = PS.ModifierPredicate("GRANULARITY", "NOT_IN", ("SYNTH_A", "SYNTH_B"))
    sigs = build([rule(modifier_predicates=(pred,))], [mech()]).signatures
    assert len(PS.match_signatures(sigs, "PROC-SYN001", {"GRANULARITY": "SYNTH_C"})) == 1
    assert PS.match_signatures(sigs, "PROC-SYN001", {"GRANULARITY": "SYNTH_A"}) == ()


# ----------------------------------------------------------------------------- firewall counters and purity
def test_firewall_counters_are_zero_on_built_signatures_and_count_tampering() -> None:
    sigs = build([rule()], [mech()]).signatures
    c = PS.firewall_counters([s.to_canonical() for s in sigs])
    assert c == {"magnitudes_emitted": 0, "is_evidence_true": 0, "endpoint_as_condition": 0, "gate_eval_skipped": 0}
    bad = sigs[0].to_canonical()
    bad["candidate_effects"][0]["rate"] = 1.0
    bad["trigger"]["modifier_predicates"].append({"axis": "ENDPOINT", "operator": "IS", "values": ["X"]})
    c = PS.firewall_counters([bad])
    assert c["magnitudes_emitted"] == 1 and c["endpoint_as_condition"] == 1


def test_module_is_pure_and_holds_no_chemistry_or_rules() -> None:
    src = Path(PS.__file__).read_text(encoding="utf-8")
    assert not re.search(r"ascorb|chlorophyll|pheoph|vitamin|alliin|maillard|starch|sim_aa|sim_chl", src, re.IGNORECASE)
    for banned in ("write_text", "write_bytes", "ledgers/data", "subprocess", "requests", "open("):
        assert banned not in src, banned
