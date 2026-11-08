"""S172 / D-077: Layer 1 binding census (counts only) + per-event dataset records (data plane). Synthetic."""
from __future__ import annotations

import json

from culinarystate.quantity import rc2_dryrun as D
from culinarystate.simulation import binding_census as BC

SENTINEL = "ZQXSENTINEL"


def records(n=6):
    return [{"recipe_id": f"SYN-{SENTINEL}-{i}", "source_family": "WIKIBOOKS",
             "steps": [f"Dice the potatoes {SENTINEL}.", "Boil the potatoes for 20 minutes.",
                       "Preheat the oven to 200C.", "Bake for 25 mins."] if i != 2 else []} for i in range(n)]


def test_counts_only_and_add_up():
    rep = BC.census_from_records(records(), seed="7", size=6)
    D.assert_counts_only(rep)
    assert SENTINEL not in json.dumps(rep) and rep["contains_ids"] is False
    assert rep["texts_with_steps"] == 5 and rep["heat_events"] > 0
    for name, st in rep["input_status"].items():
        assert sum(st.values()) == rep["heat_events"], name
    assert rep["driver_ready_events"] <= rep["driver_bounded_events"] <= rep["heat_events"]
    assert rep["input_basis"]["temperature_profile"]["PHYSICAL_DEFINITION"] == 5
    assert rep["input_basis"]["temperature_profile"]["CARRIED_SETPOINT"] == 5


def test_workers_identical():
    assert BC.census_from_records(records(9), seed="7", size=9) == \
        BC.census_from_records(records(9), seed="7", size=9, workers=2)


def test_records_out_writes_per_event_rows(tmp_path):
    rep = BC.census_from_records(records(), seed="7", size=6, records_dir=tmp_path)
    rows = [json.loads(l) for f in sorted(tmp_path.glob("*.jsonl")) for l in f.read_text().splitlines()]
    assert len(rows) == rep["heat_events"]
    r = rows[0]
    assert {"recipe_id", "event_id", "process_id", "inputs", "layer"} <= set(r) and r["layer"] == "TEXT_STATED"
    assert all(v["status"] in ("MEASURED", "RANGE", "UNKNOWN") for v in r["inputs"].values())
