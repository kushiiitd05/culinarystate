"""S176 / L-ROUTER: demo honesty. Evidence labels, TARGET_ABSENT answer, step gates in the summary, page contents.

No ledgers: packets are synthetic, the pipeline is replaced by a fake (the real one needs lxml, which this venv lacks).
"""
from __future__ import annotations

import sys
import types
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest

from culinarystate.decision import demo_context as DC
from culinarystate.decision import evidence_label as EL
from culinarystate.mechanism import evidence_gates as EG
from culinarystate.retrieval.retriever import EvidencePacket

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "src/culinarystate/app/static/index.html").read_text(encoding="utf-8")
VC = "SVAR-000009"


def _hit(evd, matrix="EXACT", process="EXACT"):
    return SimpleNamespace(evd_id=evd, compat={"match": {"matrix": matrix, "process": process}})


def _pk(cls, direct=(), near=()):
    return SimpleNamespace(evidence_class=cls, direct=list(direct), near=list(near))


def _dec(mode, precision="QUANTITATIVE", keys=("boil",)):
    return {"mode": mode, "precision": precision, "per_option": {k: {"precision": precision} for k in keys}}


# ------------------------------------------------------------------ evidence label
def test_measured_for_the_asked_food_is_the_only_from_data_label():
    lab = EL.label(_dec("ANSWER"), {"boil": _pk("DIRECT", direct=[_hit("EVD-1"), _hit("EVD-2")])})
    assert lab["code"] == EL.MEASURED and lab["badge"] == "Answered from data" and lab["from_data"] is True
    assert lab["evd_ids_asked_food"] == ["EVD-1", "EVD-2"] and lab["evd_ids_other"] == []
    near_exact = EL.label(_dec("ANSWER", "INTERVAL"), {"boil": _pk("INTERPOLATED", near=[_hit("EVD-3", "EXACT", "STEP")])})
    assert near_exact["from_data"] is True                     # interpolated, but every row is the asked food and process


@pytest.mark.parametrize("hits,code,badge", [
    ([_hit("E1", "EXACT", "SAME_FAMILY")], EL.OTHER_PROCESS, "Same food, different process"),
    ([_hit("E1", "PARENT", "EXACT"), _hit("E2", "SIBLING", "EXACT")], EL.SIMILAR, "Similar foods only"),
    ([_hit("E1", "GROUP_ROW", "EXACT")], EL.SIMILAR, "Similar foods only"),
    ([_hit("E1", "UNKNOWN", "EXACT")], EL.OTHER_FOODS, "Other foods only"),
    ([_hit("E1", "EXACT", "EXACT"), _hit("E2", "UNKNOWN", "EXACT")], EL.OTHER_FOODS, "Other foods only"),   # weakest wins
])
def test_near_evidence_never_gets_the_data_badge(hits, code, badge):
    lab = EL.label(_dec("ANSWER", "INTERVAL"), {"boil": _pk("INTERPOLATED", near=hits)})
    assert lab["code"] == code and lab["badge"] == badge and lab["from_data"] is False
    assert "E1" in lab["evd_ids_asked_food"] + lab["evd_ids_other"]


def test_qualitative_answers_say_direction_only_and_what_it_rests_on():
    lab = EL.label(_dec("ANSWER", "QUALITATIVE"), {"boil": _pk("QUALITATIVE", near=[_hit("E1", "UNKNOWN", "EXACT")])})
    assert lab["code"] == EL.DIRECTION and lab["badge"] == "Direction only (other foods)" and not lab["from_data"]
    exact = EL.label(_dec("ANSWER", "QUALITATIVE"), {"boil": _pk("QUALITATIVE", direct=[_hit("E1")])})
    assert exact["badge"] == "Direction only" and exact["from_data"] is False


def test_conflict_is_labelled_and_other_modes_get_no_label():
    c = EL.label(_dec("ANSWER", "REPORT_CONFLICT"), {"boil": _pk("CONFLICT", near=[_hit("E1"), _hit("E2")])})
    assert c["code"] == EL.CONFLICT and c["badge"] == "Sources disagree"
    for mode in ("ABSTAIN", "ASK", "RECOMMEND", "RECOVER", "DIAGNOSE"):
        assert EL.label(_dec(mode), {"boil": _pk("DIRECT", direct=[_hit("E1")])}) is None
    assert EL.label(_dec("ANSWER"), {"boil": _pk("UNSUPPORTED")}) is None          # no rows, no label


def test_compare_takes_the_weakest_option():
    per = _dec("COMPARE", "INTERVAL", keys=("boil", "steam"))
    packets = {"boil": _pk("DIRECT", direct=[_hit("E1")]),
               "steam": _pk("INTERPOLATED", near=[_hit("E2", "PARENT", "EXACT")])}
    lab = EL.label(per, packets)
    assert lab["code"] == EL.SIMILAR and lab["badge"] == "Compared: similar foods only"
    assert lab["options"] == {"boil": EL.MEASURED, "steam": EL.SIMILAR}
    both = EL.label(per, {"boil": _pk("DIRECT", direct=[_hit("E1")]), "steam": _pk("DIRECT", direct=[_hit("E2")])})
    assert both["badge"] == "Compared from data"


def test_label_works_on_real_packet_objects_and_is_deterministic():
    p = EvidencePacket("q", None, "UNSUPPORTED")
    assert EL.label(_dec("ANSWER"), {"boil": p}) is None
    a = EL.label(_dec("ANSWER"), {"boil": _pk("DIRECT", direct=[_hit("E1")])})
    assert a == EL.label(_dec("ANSWER"), {"boil": _pk("DIRECT", direct=[_hit("E1")])})


# ------------------------------------------------------------------ TARGET_ABSENT answer through the demo context
def _gates(values):
    cands = {ing: ((1000 + n, "HIGH", Fraction(1)),) for n, ing in enumerate(values)}
    vals = {(1000 + n, "vitamin_c"): Fraction(v) for n, (_, v) in enumerate(values.items()) if v is not None}
    fl = {VC: EG.Floor(VC, "Vitamin C", "vitamin_c", "mg", Fraction(1), "PROPOSED_PILOT")}
    # S177 (FINAL-SCI #6 encoded): ABSENT now needs a confirmed ING category, so the synthetic ING carry a matching pair
    cats = {ing: ("VEGETABLE", "Vegetables and Vegetable Products") for ing in values}
    return EG.EvidenceGates(EG.TargetPresenceScreen(fl, cands, vals, cats, basis={k: ("A", 1) for k in vals}),  # S178 R4: synthetic SR values are analytical
                            provenance={"version": EG.VERSION})


REG = [{"state_variable_id": VC, "name": "Vitamin C, total ascorbic acid content", "current_row_count": "270"}]


def _ctx(monkeypatch, gates, *, ingredient="ING-EGG", mode="ANSWER", packets=None):
    packets = packets or {"bake": _pk("DIRECT", direct=[_hit("EVD-9")])}
    real_packet = EvidencePacket("q", None, "UNSUPPORTED")
    slots = SimpleNamespace(target="vitamin c", ingredient_id=ingredient, ingredient_name="egg",
                            processes=[("bake", "PROC-1")])

    def answer(q, *a, **k):
        d = {"mode": mode, "precision": "QUANTITATIVE", "reason": "DIRECT", "intent": "ANSWER",
             "per_option": {"bake": {"precision": "QUANTITATIVE"}}}
        return {"decision": d, "slots": slots, "packets": {"bake": real_packet} if mode != "ANSWER" else packets}

    fake = types.ModuleType("culinarystate.decision.pipeline")
    fake.answer = answer
    monkeypatch.setitem(sys.modules, "culinarystate.decision.pipeline", fake)
    import culinarystate.generation.verbalize as VZ
    real_verbalize = VZ.verbalize
    # the synthetic packet has no EVD rows to print: ANSWER text is a stub, ABSTAIN text is the real verbaliser's
    monkeypatch.setattr(VZ, "verbalize", lambda q, d, p: real_verbalize(q, d, p) if d["mode"] == "ABSTAIN" else
                        "stub answer [EVD-9]")
    return DC.DemoContext(registry=REG, gates=gates, lex=None, retriever=None, req=None, family=None, sup=None, ts=None)


def test_food_without_the_nutrient_gets_an_explicit_abstention_and_no_figure(monkeypatch):
    ctx = _ctx(monkeypatch, _gates({"ING-EGG": "0"}))
    out = ctx._transform("How much vitamin C does baked egg keep?")
    assert out["mode"] == "ABSTAIN" and out["reason"] == "TARGET_ABSENT" and out["cited"] == []
    assert out["evidence"] is None and out["target_presence"]["state"] == "ABSENT"
    assert "no meaningful amount" in out["answer"] and not any(ch.isdigit() for ch in out["answer"])
    assert "EVD-" not in out["answer"]


def test_food_with_the_nutrient_keeps_its_answer_and_gets_a_label(monkeypatch):
    ctx = _ctx(monkeypatch, _gates({"ING-EGG": "19.7"}))
    out = ctx._transform("How much vitamin C does baked egg keep?")
    assert out["mode"] == "ANSWER" and out["target_presence"] is None
    assert out["evidence"]["badge"] == "Answered from data" and out["evidence"]["evd_ids_asked_food"] == ["EVD-9"]


def test_unknown_presence_or_no_gates_changes_nothing_but_still_labels(monkeypatch):
    for gates in (None, _gates({}), _gates({"ING-EGG": None})):
        out = _ctx(monkeypatch, gates)._transform("How much vitamin C does baked egg keep?")
        assert out["mode"] == "ANSWER" and out["target_presence"] is None and out["evidence"]["from_data"] is True


def test_target_absent_helper_requires_a_screened_target_and_a_known_food():
    g = _gates({"ING-EGG": "0", "ING-POT": "19.7"})
    assert DC.target_absent(g, VC, "ING-EGG") is True
    assert DC.target_absent(g, VC, "ING-POT") is False
    assert DC.target_absent(g, "SVAR-NOFLOOR", "ING-EGG") is False and DC.target_absent(g, None, "ING-EGG") is False
    assert DC.target_absent(g, VC, None) is False and DC.target_absent(None, VC, "ING-EGG") is False
    assert DC.target_absent(EG.EvidenceGates(g.screen, presence=False), VC, "ING-EGG") is False


# ------------------------------------------------------------------ recipe summary carries the gates
def test_recipe_summary_exposes_gate_codes_and_withheld_rows():
    items = [{"event_id": "E1", "action": "Bake", "process_id": "P", "ingredient_id": "ING-EGG", "route": "NOT_APPLICABLE",
              "reasons": ["TARGET_ABSENT", "NO_FORM"], "evidence": [], "evidence_not_applied": [{"evd_id": "EVD-9"}],
              "gates": {"presence": "ABSENT", "lot_context": "SINGLE_MEMBER"}},
             {"event_id": "E2", "action": "Boil", "process_id": "P", "ingredient_id": "ING-POT", "route": "DIRECT",
              "reasons": ["EVIDENCE_PREEMPTS"], "evidence": [{"evd_id": "EVD-1"}]}]
    s = DC.recipe_summary({"items": items, "target_svar": VC, "gates": {"enabled": True, "version": "v", "floors": {"X": 1}}})
    assert s["routes"] == {"DIRECT": 1, "NOT_APPLICABLE": 1}
    assert s["steps"][0]["evidence_not_applied"] == ["EVD-9"] and s["steps"][0]["gates"]["presence"] == "ABSENT"
    assert s["steps"][1]["evidence_not_applied"] == [] and s["steps"][1]["gates"] is None
    assert s["gates"] == {"enabled": True, "version": "v"}       # no thresholds leak into the page payload


# ------------------------------------------------------------------ the page
def test_page_has_no_blanket_data_badge_and_no_bbc_derived_example():
    assert "Answered from data" not in HTML                       # the text now comes from the server's evidence label
    assert "buttermilk" not in HTML.lower()                       # BBC-derived example removed (D-003)
    assert "evidence.from_data" in HTML or "ev.from_data" in HTML
    assert "b-data" in HTML and "b-near" in HTML and "b-pattern" in HTML and "b-safety" in HTML
    assert "ABSTAIN_SAFETY" in HTML and "TARGET_ABSENT" in HTML and "MERGED_LOT_CONTEXT" in HTML
    assert "instead of ricotta" in HTML and "still pink" in HTML and "fried potatoes" in HTML.lower()


def test_page_green_class_is_assigned_only_through_from_data():
    import re
    assigns = re.findall(r'cls: ([^,}]+)', HTML)
    assert any("from_data" in a for a in assigns)
    assert sum('"b-data"' in a for a in assigns) == 1             # b-data appears once, in the from_data conditional
