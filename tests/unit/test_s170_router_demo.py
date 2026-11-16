"""S170 / D-075 M1: router demo mode on real recipe text (NON_CITABLE; 23a engine unchanged; no COND consumed)."""
import pytest

from culinarystate.mechanism import router_demo as RD

VC = "SVAR-000009"


def _row(evd_id, ing, proc, svar=VC, status="MEASURED", value=65.0, active="ACTIVE", version=1):
    return {"id": evd_id, "version": version, "status": active, "tier": "E3", "source_id": "SRC-1",
            "matrix": {"ingredient_id": ing, "raw_name": "X"}, "process": {"process_id": proc},
            "target": {"state_variable_id": svar, "raw_name": "Vitamin C"},
            "derived": {"retention_factor": {"status": status, "value": value, "unit": "%", "raw": str(value)}},
            "verification": {"status": "UNVERIFIED"}}


def test_index_keeps_latest_active_version_only():
    idx = RD.EvidenceIndex.from_rows([_row("E1", "ING-1", "PROC-1", value=50.0),
                                      _row("E1", "ING-1", "PROC-1", value=60.0, version=2),
                                      _row("E2", "ING-1", "PROC-1", active="RETRACTED")])
    hits = idx.lookup("ING-1", "PROC-1", VC)
    assert [(h["evd_id"], h["value"]) for h in hits] == [("E1", 60.0)]


def test_precheck_direct_only_for_measured_or_censored():
    assert RD.precheck([{"status": "MEASURED"}]) == "DIRECT"
    assert RD.precheck([{"status": "CENSORED"}]) == "DIRECT"
    assert RD.precheck([{"status": "UNKNOWN"}]) == "NONE"
    assert RD.precheck([]) == "NONE"


def test_route_text_direct_with_evidence_unknown_without(monkeypatch):
    text = "Boil the potatoes for 20 minutes. Roast the carrots in the oven."
    out0 = RD.route_text(text, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    items = out0["items"]
    assert [i["action"] for i in items] == ["Boil", "Roast"]
    ing_boil, proc_boil = items[0]["ingredient_id"], items[0]["process_id"]
    assert ing_boil and proc_boil == "PROC-000019"
    assert all(i["route"] == "UNKNOWN" for i in items)
    out = RD.route_text(text, index=RD.EvidenceIndex.from_rows([_row("EVD-9", ing_boil, proc_boil)]), target_svar=VC)
    boil, roast = out["items"]
    assert boil["route"] == "DIRECT" and [e["evd_id"] for e in boil["evidence"]] == ["EVD-9"]
    assert roast["route"] == "UNKNOWN" and "NO_CANDIDATE_MECHANISM" in roast["reasons"]


def test_envelope_is_non_citable_and_engine_unchanged():
    out = RD.route_text("Boil the potatoes.", index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    assert out["citable"] is False and "NON_CITABLE" in out["labels"] and "DEMO_ONLY" in out["labels"]
    assert out["engine_mode"] == "23a" and out["conditions_consumed"] is False
    with pytest.raises(RD.DemoRefused):
        RD.assert_citable(out)


def test_unresolved_or_unlinked_events_route_unknown_with_reason():
    out = RD.route_text("Stir well.", index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    assert out["items"] and all(i["route"] == "UNKNOWN" for i in out["items"])
    assert all(i["ingredient_id"] is None for i in out["items"])
    assert all("NO_LINKED_INGREDIENT" in i["reasons"] for i in out["items"])


def test_target_required():
    with pytest.raises(ValueError):
        RD.route_text("Boil the potatoes.", index=RD.EvidenceIndex.from_rows([]), target_svar="")
