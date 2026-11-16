"""S178 H1H3H: one-at-a-time ablation driver on a tiny SYNTHETIC system (hand-computed error changes)."""
from __future__ import annotations

import pytest

from culinarystate.evaluation import ablation as AB

EVD = {"EVD-990001": {"id": "EVD-990001", "matrix": {"ingredient_id": "ING-990001", "raw_name": "fixturefruit"},
                      "process": {"process_id": "PROC-990001", "steps": ["boil"], "raw_name": "boil"},
                      "target": {"state_variable_id": "SVAR-990001", "raw_name": "Vitamin C"},
                      "derived": {"retention_factor": {"status": "MEASURED", "value": 0.65, "unit": "fraction"}}}}
CELL = dict(ingredient_id="ING-990001", food="fixturefruit", process="boil", process_id="PROC-990001", target_svars="SVAR-990001")
ROWS = [{"qid": "SYN-P1-001", "block": "P1", "gold_mode": "ANSWER", **CELL},
        {"qid": "SYN-P3-001", "block": "P3", "gold_mode": "ABSTAIN", **CELL},
        {"qid": "SYN-S1-001", "block": "S1"}]
NOPE = "There is no measured evidence, so I can't give a number."


def system(row, off):
    if row["qid"] == "SYN-P1-001":
        txt = "It keeps 90 % [EVD-990001]." if "claim_enforcement" in off else (
            NOPE if "state_conditioning" in off else "It keeps 65 % [EVD-990001].")
    else:
        txt = "About 50 % is kept." if "ood_gate" in off else NOPE
    return {"answer": txt, "rung": "B7"}


def test_driver_and_table():
    recs = AB.run_ablations(ROWS, system)
    assert set(recs) == {"FULL", *AB.CHEAP} and set(recs["FULL"]) == {"SYN-P1-001", "SYN-P3-001"}   # S rows excluded
    assert recs["ood_gate"]["SYN-P3-001"]["config"] == "ood_gate"
    t = AB.table_from_records(ROWS, recs, EVD)
    assert t["full"]["error_rate_E1"]["x"] == 0 and t["full"]["ucr"] == 0.0
    by = {r["toggle"]: r for r in t["table"] if r["toggle"]}
    assert by["ood_gate"]["paired_E1"] == {"n": 2, "errors_added": 1, "errors_removed": 0,
                                           "p_exact_two_sided_descriptive": 1.0}
    assert by["ood_gate"]["metrics"]["abstention_on_abstain_gold"]["x"] == 0
    assert by["claim_enforcement"]["paired_E1"]["errors_added"] == 1 and by["claim_enforcement"]["delta_vs_full"]["ucr"] == 1.0
    sc = by["state_conditioning"]
    assert sc["paired_E1"]["errors_added"] == 0 and sc["metrics"]["false_abstention_answerable"]["x"] == 1
    assert sc["metrics"]["ucr"] is None and sc["delta_vs_full"]["ucr"] is None       # no claim: UCR undefined, not 0
    assert by["evidence_compatibility"]["delta_vs_full"]["error_rate_E1"] == 0.0
    not_run = [r for r in t["table"] if r["status"] == "NOT_RUN"]
    assert len(t["table"]) == 9 and len(not_run) == 5 and all(r["reason"] for r in not_run)
    assert t["prereg_status"].startswith("EXPLORATORY")


def test_missing_config_and_validation():
    recs = AB.run_ablations(ROWS, system, components=("ood_gate",))
    t = AB.table_from_records(ROWS, recs, EVD)
    by = {r["ssot_245_13"]: r for r in t["table"]}
    assert by["evidence compatibility"]["status"] == "NOT_RUN" and by["uncertainty/OOD gate"]["status"] == "RUN"
    with pytest.raises(ValueError):
        AB.configs(("feasibility_filtering",))
    with pytest.raises(ValueError):
        AB.table_from_records(ROWS, {"ood_gate": {}}, EVD)
