"""S178 FIX-PHYS, SCI-B R1 (D-003): public mode must not serve BBC-derived typical durations through the scenario layer.

``ScenarioLayer.load(public=True)`` drops every PROC_TYPICAL_DURATION edge that ``public_mode.is_bbc_derived`` names; the
default load is unchanged (the census tools use it). ``DemoContext.load`` passes the mode in force. Synthetic recipe text only.
"""
from __future__ import annotations

import ast
import json
import re
import sys
import types
from pathlib import Path

import pytest

from culinarystate.decision import demo_context as DC
from culinarystate.decision import public_mode as PM
from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import scenario_layer as SL

ROOT = Path(__file__).resolve().parents[2]
TEXT = "Boil the potatoes. Drain and fry the potatoes in oil."
KGE_ID = re.compile(r"KGE-\d+")


def _kge_edges() -> dict[str, dict]:
    out = {}
    with open(ROOT / "ledgers/data/KGE.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                e = json.loads(line)
                out[e["id"]] = e
    return out


def _legacy_durations() -> dict:
    """The S172..S178 v04 reader, re-implemented here: every ACTIVE PROC_TYPICAL_DURATION edge in minutes."""
    out = {}
    for e in _kge_edges().values():
        q = e.get("quantiles") or {}
        if e.get("predicate") == "PROC_TYPICAL_DURATION" and e.get("status") == "ACTIVE" and q.get("p50") is not None \
                and q.get("unit") == "min":
            out[e["subject_id"]] = (q["p10"], q["p50"], q["p90"], e["id"])
    return out


@pytest.fixture(scope="module")
def layers():
    return SL.ScenarioLayer.load(), SL.ScenarioLayer.load(public=False), SL.ScenarioLayer.load(public=True)


@pytest.fixture(scope="module")
def binder():
    return CB.Binder.load()


def test_default_load_is_unchanged_and_byte_identical_to_public_false(layers, binder):
    default, local, _ = layers
    assert default.durations == local.durations == _legacy_durations() and len(default.durations) > 0
    assert default.public is False and default.dropped_bbc_duration_edges == 0
    recs = [{**e, "inputs": {k: {**v, "value": DC._str(v["value"])} for k, v in e["inputs"].items()}}
            for e in binder.bind_text(TEXT + " Simmer the sauce. Bake at 350 F.")["events"] if e["heat"]]
    assert recs
    for r in recs:
        assert json.dumps(default.run(r), sort_keys=True) == json.dumps(local.run(r), sort_keys=True)


def test_public_load_drops_every_bbc_derived_duration_edge(layers):
    default, _, public = layers
    edges = _kge_edges()
    bbc = {sid for sid, row in default.durations.items() if PM.is_bbc_derived(edges[row[3]])}
    assert public.public is True and public.dropped_bbc_duration_edges == len(bbc)
    assert set(public.durations) == set(default.durations) - bbc
    assert not any(PM.is_bbc_derived(edges[row[3]]) for row in public.durations.values())


def _walk_ids(obj) -> set[str]:
    return set(KGE_ID.findall(json.dumps(obj, default=str)))


def test_public_physics_summary_has_no_bbc_duration_and_says_unknown(layers, binder):
    default, _, public = layers
    edges = _kge_edges()
    local_out = DC.physics_summary(TEXT, binder, default)
    pub_out = DC.physics_summary(TEXT, binder, public)
    # local mode: unchanged (a corpus duration basis is still served there)
    assert any(KGE_ID.fullmatch(str((s["scenario"]["bases"] or {}).get("duration_min"))) for s in local_out["steps"])
    for kid in _walk_ids(pub_out):
        assert not PM.is_bbc_derived(edges[kid]) and edges[kid].get("predicate") != PM.CARBON_PREDICATE, kid
    for s in pub_out["steps"]:
        if s["stated"]["duration_min"] is None:  # no duration in the text: no BBC typical duration, so UNKNOWN
            assert s["scenario"]["typical_duration_min"] is None and s["scenario"]["status"] == "SCENARIO_UNKNOWN"
    assert any(s["scenario"]["status"] == "SCENARIO_UNKNOWN" for s in pub_out["steps"])
    raw = public.run({"process_id": "PROC-000019", "oven_setpoint_code": None,
                      "inputs": CB.Binder.load().bind_text("Boil the potatoes.")["events"][0]["inputs"]})
    if not public.durations.get("PROC-000019"):
        assert raw["status"] == "SCENARIO_UNKNOWN" and "duration_min" in raw["missing"]


def test_a_stated_duration_still_computes_in_public_mode(layers, binder):
    _, _, public = layers
    out = DC.physics_summary("Boil the potatoes for 20 minutes.", binder, public)
    boil = out["steps"][0]
    assert boil["scenario"]["status"] == "SCENARIO_COMPUTED" and boil["scenario"]["bases"]["duration_min"] == "L1:TEXT_STATED"
    assert not _walk_ids(out)


def test_demo_context_passes_the_mode_to_the_scenario_layer():
    src = (ROOT / "src/culinarystate/decision/demo_context.py").read_text(encoding="utf-8")
    calls = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "load" and isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "ScenarioLayer"]
    assert len(calls) == 1
    kw = {k.arg: ast.unparse(k.value) for k in calls[0].keywords}
    assert kw == {"public": "mode.public"}


@pytest.fixture
def lxml_shim(monkeypatch):
    try:
        import lxml  # noqa: F401
    except ImportError:
        pkg = types.ModuleType("lxml")
        pkg.etree = types.ModuleType("lxml.etree")
        monkeypatch.setitem(sys.modules, "lxml", pkg)
        monkeypatch.setitem(sys.modules, "lxml.etree", pkg.etree)


def test_public_demo_answer_with_a_recipe_carries_no_bbc_derived_kge_id(lxml_shim):
    """End to end through DemoContext.load(public=True): every KGE id in the whole response is non-BBC and non-carbon."""
    edges = _kge_edges()
    ctx = DC.DemoContext.load(public=True)
    assert ctx.layer.public is True and ctx.layer.dropped_bbc_duration_edges > 0
    out = ctx.respond("How much vitamin C is left after boiling potatoes?", recipe_text=TEXT)
    bad = sorted(k for k in _walk_ids(out) if k in edges and (PM.is_bbc_derived(edges[k])
                                                            or edges[k].get("predicate") == PM.CARBON_PREDICATE))
    assert bad == []
    phys = ((out.get("recipe") or {}).get("physics") or {}).get("steps") or []
    for s in phys:
        if s["stated"]["duration_min"] is None:
            assert s["scenario"]["typical_duration_min"] is None
