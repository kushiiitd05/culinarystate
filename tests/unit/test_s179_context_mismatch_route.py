"""A2 (D-084 item 7): CONTEXT_MISMATCH route value, test-first (S179).

When the gates withhold a DIRECT / BRACKETING pre-check for a context reason (merged lot, prior process, unresolved
prior process, no lot) and the engine has nothing weaker than UNKNOWN, the router says CONTEXT_MISMATCH: "a table row
exists for this pair, but not for this food in this context". It is opt-in (``context_mismatch_route=True``) so the
S176-S178 records stay reproducible; it has the strength of UNKNOWN, so it never upgrades a route.
"""
from __future__ import annotations

import random

from culinarystate.mechanism import evidence_gates as EG
from tests.unit import test_s176_evidence_gates as S6
from tests.unit import test_s177_router_gates as S7


def _gates6(values, **kw):
    return EG.EvidenceGates(S6._screen(values), context_mismatch_route=True, **kw)


def _merged_item(gates):
    proc = S6.IDS["potato_simmer"][1]
    _, items = S6._items(S6.MERGED_TEXT, gates, [S6._row("EVD-3", S6.POTATO, proc)])
    return next(i for i in items if i["action"].lower() == "simmer" and i["ingredient_id"] == S6.POTATO)


def test_route_value_and_reasons_are_registered():
    assert EG.CONTEXT_MISMATCH == "CONTEXT_MISMATCH"
    assert set(EG.CONTEXT_REASONS) == {EG.R_MERGED, EG.R_PRIOR_PROCESS, EG.R_PRIOR_UNRESOLVED, EG.R_LOT_UNKNOWN}
    assert EG.ROUTE_STRENGTH[EG.CONTEXT_MISMATCH] == EG.ROUTE_STRENGTH["UNKNOWN"]


def test_merged_lot_routes_context_mismatch_when_enabled():
    it = _merged_item(_gates6({S6.POTATO: "19.7", S6.CARROT: "5.9"}))
    assert it["route_ungated"] == "DIRECT" and it["route"] == "CONTEXT_MISMATCH"
    assert it["reasons"][0] == "MERGED_LOT_CONTEXT"
    assert it["evidence"] == [] and len(it["evidence_not_applied"]) == 1


def test_default_off_keeps_the_s176_route():
    it = _merged_item(S6._gates({S6.POTATO: "19.7", S6.CARROT: "5.9"}))
    assert it["route"] == "UNKNOWN"
    assert S6._gates({S6.POTATO: "1"}).describe()["context_mismatch_route"] is False


def test_prior_process_routes_context_mismatch_and_first_process_stays_direct():
    rows = [S7._row("EVD-1", S7.POTATO, S7.BOIL), S7._row("EVD-2", S7.POTATO, S7.FRY)]
    gates = EG.EvidenceGates(S7._screen({S7.POTATO: "19.7"}), context_mismatch_route=True)
    items = S7._items(S7.TEXT_BOIL_FRY, gates, rows)
    boil, = S7._by_action(items, "boil", S7.POTATO)
    fry, = S7._by_action(items, "fry", S7.POTATO)
    assert boil["route"] == "DIRECT"
    assert fry["route"] == "CONTEXT_MISMATCH" and fry["reasons"][0] == "PRIOR_PROCESS_CONTEXT"


def test_absent_target_stays_not_applicable_not_context_mismatch():
    it = _merged_item(_gates6({S6.POTATO: "0", S6.CARROT: "0"}))
    assert it["route"] == "NOT_APPLICABLE" and it["reasons"][0] == "TARGET_ABSENT"


def test_no_evidence_row_is_never_context_mismatch():
    _, items = S6._items(S6.MERGED_TEXT, _gates6({S6.POTATO: "19.7", S6.CARROT: "5.9"}), [])
    assert all(i["route"] != "CONTEXT_MISMATCH" for i in items)


def test_context_mismatch_never_upgrades_and_only_replaces_unknown():
    texts = ["Boil the potatoes for 20 minutes. Roast the carrots in the oven. Bake the eggs.", S6.MERGED_TEXT,
             "Bake the eggs for 10 minutes. Mix the eggs and the potatoes together into a batter. Bake the mixture.",
             "Boil the potatoes for 20 minutes. Fry the potatoes for 5 minutes."]
    keys = [S6.IDS["potato"], S6.IDS["carrot"], S6.IDS["egg"], S6.IDS["potato_simmer"]]
    rng = random.Random(179)
    for _ in range(30):
        rows = [S6._row(f"E{n}", i, p) for n, (i, p) in enumerate(rng.sample(keys, rng.randint(0, len(keys))))]
        vals = {i: rng.choice(["0", "1", "5", None]) for i in (S6.POTATO, S6.CARROT, S6.EGG)}
        on = EG.EvidenceGates(S6._screen(vals), context_mismatch_route=True)
        off = EG.EvidenceGates(S6._screen(vals))
        for text in texts:
            _, a = S6._items(text, on, rows)
            _, b = S6._items(text, off, rows)
            assert len(a) == len(b)
            for x, y in zip(a, b):
                if x["route"] == "CONTEXT_MISMATCH":
                    assert y["route"] == "UNKNOWN" and x["reasons"][0] in EG.CONTEXT_REASONS
                    assert x["route_ungated"] in ("DIRECT", "INTERPOLATE")
                else:
                    assert x["route"] == y["route"]
                if x["route"] != EG.NOT_APPLICABLE:
                    assert EG.ROUTE_STRENGTH[x["route"]] <= EG.ROUTE_STRENGTH[x["route_ungated"]]


def _census_tool():
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("router_demo_census", root / "tools/router_demo_census.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_census_cli_flag_is_recorded_and_needs_gates(tmp_path):
    import json
    import pytest
    from tests.unit import test_s171_router_census as S1
    tool = _census_tool()
    (tmp_path / "missing.jsonl").write_text("")
    src = lambda families, root: iter(S1.records())  # noqa: E731
    base = ["--seed", "7", "--sample-size", "6", "--root", str(tmp_path), "--no-baseline-check",
            "--evd", str(tmp_path / "missing.jsonl"), "--context-mismatch-route"]
    out = tmp_path / "on.json"
    assert tool.main([*base, "--out", str(out)], record_source=src) in (0, 3)
    assert json.loads(out.read_text())["gates"]["context_mismatch_route"] is True
    with pytest.raises(SystemExit):
        tool.main([*base, "--out", str(tmp_path / "off.json"), "--gates", "off"], record_source=src)
