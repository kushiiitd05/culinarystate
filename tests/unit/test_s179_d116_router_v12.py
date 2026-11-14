"""D-116 item 4: composition-aware routing over the frozen router; tomato A-D acceptance + unstated-context scenario."""
from __future__ import annotations

from pathlib import Path

import pytest

from culinarystate.composition import context_v12 as CV
from culinarystate.composition import router_v12 as RV
from culinarystate.composition import state as CS
from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.ledgers.store import LedgerStore
from culinarystate.mechanism import evidence_gates as EG
from culinarystate.mechanism import process_signatures as PS
from culinarystate.mechanism import router_demo as RD
from culinarystate.quantity.rc2_dryrun import load_schema

ROOT = Path(__file__).resolve().parents[2]
MARKS, ROLES = CS.load_markers_v2(ROOT / "registry" / "composition_markers_v2.csv")
SR = CV.load_sr_composition(ROOT / "registry" / "ing_sr_composition_v1.csv")
RUNG, SCHEMA = RungA(coord_food_guard=True), load_schema()
TOMATO, BOIL, VITC = "ING-000010", "PROC-000019", "SVAR-000009"


@pytest.fixture(scope="module")
def env():
    return dict(index=RD.EvidenceIndex.from_rows(LedgerStore().all_latest("EVD")), gates=EG.EvidenceGates.load(),
                hierarchy=PS.read_process_hierarchy())


def _routed(env, text):
    parsed = RUNG.run(SourceText.from_raw("T", text), RUNG.config(), schema=SCHEMA)
    mem = CS.lot_members_v11(parsed.graph.entities)
    events = {e.event_id: e for e in parsed.graph.events}
    r = RD.route_text(text, target_svar=VITC, rung=RUNG, schema=SCHEMA, **env)
    item = next(i for i in r["items"] if i["ingredient_id"] == TOMATO and i["process_id"] == BOIL)
    ctx = CV.context_v12(TOMATO, list(events[item["event_id"]].consumes), mem, MARKS, ROLES, SR, medium_type=None)
    return item, ctx, RV.composition_route(item, ctx)


CASES = {
    "A": ("Boil the tomatoes in water for 20 minutes.", "DIRECT", None),
    "W": ("Mix the tomatoes and water.\nBoil the mixture for 20 minutes.", "DIRECT", None),
    "B": ("Mix the tomatoes, water and salt.\nBoil the mixture for 20 minutes.", "CONTEXT_MISMATCH", "SALT"),
    "C": ("Mix the tomatoes, water, salt and vinegar.\nBoil the mixture for 20 minutes.", "CONTEXT_MISMATCH", "SALT+ACID"),
    "D": ("Mix the tomatoes, water, salt, vinegar and oil.\nBoil the mixture for 20 minutes.", "CONTEXT_MISMATCH",
          "SALT+ACID+LIPID"),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_tomato_variants(env, name):
    text, route, axes = CASES[name]
    _, _, out = _routed(env, text)
    assert out["route"] == route
    if axes:
        assert out["composition_reasons"][0] == "COMPOSITION_CONTEXT_DIFFERS:" + axes
        assert [e["evd_id"] for e in out["near_evidence"]] == ["EVD-002765"] and out["evidence"] == []
    else:
        assert [e["evd_id"] for e in out["evidence"]] == ["EVD-002765"]


def test_input_item_not_mutated(env):
    item, _, out = _routed(env, CASES["B"][0])
    assert item["route"] == "UNKNOWN" and out is not item


def test_unknown_axis_is_never_direct():
    ctx = {"salt_present": {"v": None, "u": "MEMBER_UNLINKED"}, "acid_present": {"v": "NOT_DETECTED"},
           "lipid_present": {"v": "NOT_DETECTED"}, "context_members": {"v": []}}
    out = RV.composition_route({"route": "DIRECT", "route_ungated": "DIRECT", "evidence": [{"evd_id": "X"}]}, ctx)
    assert out["route"] == "UNKNOWN" and out["composition_reasons"] == ["COMPOSITION_UNKNOWN:SALT"]


def test_unplaced_listed_salt_gives_scenario(env):
    item, ctx, out = _routed(env, CASES["A"][0])
    unplaced = RV.unplaced_from_list(["ING-000010", "ING-000044"], ["ING-000010", "ING-000109"], MARKS)
    sug = RV.suggest_context(ctx, unplaced, prior=None)
    assert sug["salt"] == {"label": "SUGGESTED", "basis": "INGREDIENT_LIST_UNPLACED", "members": ["ING-000044"]}
    sc = RV.scenario_route(out, sug)
    assert sc["route"] == "SCENARIO" and "NOT_STATED_IN_TEXT" in sc["composition_reasons"]
    assert out["route"] == "DIRECT"                          # the stated-text route is unchanged


@pytest.mark.parametrize("n,k,label", [(100, 60, "PROBABLE"), (100, 25, "POSSIBLE"), (100, 10, None), (10, 9, None)])
def test_corpus_prior_labels(n, k, label):
    assert RV.prior_label(n, k) == label
