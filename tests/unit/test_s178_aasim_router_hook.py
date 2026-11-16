"""S178 aa-fit-sim, T5-C11-R4: the minimal ``simulate=`` hook in ``router_demo.route_text`` (synthetic TEST_ONLY fixtures).

Fixtures come from tests/unit/test_s178_aasim_branch.py (SYNTHETIC, TEST_ONLY). Real-data behaviour: SIMULATE never fires.
"""
from __future__ import annotations

import copy
import functools

import pytest

from culinarystate.mechanism import evidence_gates as EG
from culinarystate.mechanism import router_demo as RD
from culinarystate.mechanism import simulate_branch as SB
from tests.unit import test_s178_aasim_branch as T

VC = "SVAR-000009"
INDEX = RD.EvidenceIndex.from_rows([])


@functools.lru_cache(maxsize=1)
def _gates() -> EG.EvidenceGates:
    return EG.EvidenceGates.load()


def route(text: str, *, simulate=None, gates=True) -> dict:
    return RD.route_text(text, index=INDEX, target_svar=VC, gates=_gates() if gates else None, simulate=simulate)


def test_orange_juice_ing_is_the_one_the_fixtures_use() -> None:
    assert route("Steam the orange juice for 10 minutes.")["items"][0]["ingredient_id"] == T.ING


# ----------------------------------------------------------------------------- default behaviour unchanged
@pytest.mark.parametrize("text", ["Steam the orange juice for 10 minutes.", "Boil the potatoes for 20 minutes.",
                                  "Simmer the orange juice at 90 C for 20 minutes. Drain."])
def test_no_simulate_argument_is_byte_identical(text: str) -> None:
    a = RD.route_text(text, index=INDEX, target_svar=VC, gates=_gates())
    b = RD.route_text(text, index=INDEX, target_svar=VC, gates=_gates(), simulate=None)
    assert a == b and "simulate" not in a and all("simulate" not in it for it in a["items"])
    assert RD.route_text(text, index=INDEX, target_svar=VC) == RD.route_text(text, index=INDEX, target_svar=VC,
                                                                            simulate=None)


# ----------------------------------------------------------------------------- real data: nothing reaches SIMULATE
def test_real_branch_on_real_router_gives_no_simulate_and_says_why() -> None:
    br = SB.SimulateBranch.from_repo()
    out = route("Steam the orange juice for 10 minutes. Steam the broccoli for 5 minutes. Simmer the tomatoes for "
                "20 minutes at 90 C.", simulate=br)
    assert out["simulate"]["mode"] == "REAL" and out["simulate"]["guard_allowed"] is False
    assert {"PARAM_ROWS_ABSENT", "FROZEN_FIT_ABSENT", "STEP27_HELDOUT_ABSENT"} <= set(out["simulate"]["guard_reasons"])
    assert out["citable"] is False and "NON_CITABLE" in out["labels"]
    assert out["items"] and all(it["route"] != "SIMULATE" for it in out["items"])
    for it in out["items"]:
        s = it["simulate"]
        assert s["simulated"] is False and s["status"] in ("NOT_SIMULATED", "NOT_EVALUATED_PREEMPTED")
        assert s["section141_class"] == "unsupported" and "retention_interval" not in s
        assert "TEST_ONLY" not in s["labels"] and s["mode"] == "REAL"
    counts = SB.summarize(out["items"])
    assert counts["simulate_routes"] == 0 and counts["status"]["NOT_SIMULATED"] == len(out["items"])


def test_real_branch_leaves_every_route_as_it_was() -> None:
    text = "Steam the orange juice for 10 minutes. Boil the potatoes for 20 minutes. Fry the onions."
    base, withsim = route(text), route(text, simulate=SB.SimulateBranch.from_repo())
    assert [(i["route"], i["reasons"]) for i in base["items"]] == [(i["route"], i["reasons"]) for i in withsim["items"]]


# ----------------------------------------------------------------------------- synthetic TEST_ONLY end to end
def test_end_to_end_demo_case_with_full_provenance_chain() -> None:
    out = route("Steam the orange juice for 10 minutes.", simulate=T.make_branch())
    assert out["simulate"] == {"enabled": True, "mode": "TEST_ONLY", "guard_allowed": True, "guard_reasons": [],
                               "layer1_text_inputs_used": True}
    it = out["items"][0]
    assert it["route"] == "SIMULATE" and it["reasons"] == ["SIMULATE_RESEARCH_ONLY_PILOT"]
    assert it["reasons_demo_engine"] and "SIMULATE" not in it["reasons_demo_engine"]
    s = it["simulate"]
    assert s["status"] == "COMPLETED" and s["engine_route"] == "SIMULATE" and s["section141_class"] == "physically_possible"
    assert set(s["labels"]) >= {"NOT_VALIDATED", "RESEARCH_ONLY", "NON_CITABLE", "TEST_ONLY"}
    iv = s["retention_interval"]
    assert 0 < iv["low"] < iv["high"] < 1 and iv["unit"] == "FRACTION_OF_INITIAL_REDUCED_AA" and not iv["coverage_claimed"]
    # provenance chain: text span -> input basis -> domain gate -> FORM -> PARAM ids -> frozen fit hash -> VAL -> APPDEC -> run
    inputs = {i["name"]: i for i in s["inputs"]}
    assert inputs["duration"]["basis"] == "TEXT_STATED" and inputs["duration"]["ref"].startswith("C:")
    assert inputs["temperature"]["basis"] == "PHYSICAL_DEFINITION" and inputs["temperature"]["value"] == 100.0
    assert inputs["medium"]["value"] == "STEAM" and inputs["matrix_class"]["value"] == T.CLASS
    assert s["domain_gate"]["verdict"] == "IN" and s["domain_gate"]["medium_contact"] == "NO_WATER_CONTACT"
    assert s["form_id"] == SB.FORM_ID and len(s["param_ids"]) == 4 and len(s["val_ids"]) == 1
    assert len(s["frozen_fit_sha256"]) == 64 and s["appdec_id"] == it["appdec_id"]
    assert s["derived_param_ids"] and all(p.startswith("DERIVED-") for p in s["derived_param_ids"]) and s["run_sha256"]
    assert s["analyte_basis"] == "REDUCED_L_ASCORBIC_ACID" and s["basis_flags"] == ["BASIS_MISMATCH_TOTAL_VITC"]
    assert "T_P_BATH_EQUALS_PRODUCT_ASSUMED" in s["flags"] and "INTERVAL_COVERAGE_NOT_CLAIMED" in s["flags"]
    # the envelope stays NON_CITABLE: a SIMULATE item can never be cited
    assert out["citable"] is False
    with pytest.raises(RD.DemoRefused):
        RD.assert_citable(out)


@pytest.mark.parametrize("text, code", [
    ("Steam the broccoli for 5 minutes.", "MATRIX_UNLISTED"),                       # vegetable: not on the list
    ("Boil the orange juice for 10 minutes.", "LEACHING_UNIDENTIFIED_WATER_IMMERSION"),
    ("Steam the orange juice until soft.", "DURATION_UNKNOWN"),
    ("Cook the orange juice sous vide for 30 minutes.", "TEMPERATURE_UNKNOWN"),
    ("Boil the orange juice for 5 minutes. Steam the orange juice for 10 minutes.", "PRIOR_PROCESS_CONTEXT"),
])
def test_unknown_or_out_of_domain_events_stay_unknown_in_the_router(text: str, code: str) -> None:
    base = route(text)
    out = route(text, simulate=T.make_branch())
    hit = [it for it in out["items"] if code in it["simulate"]["reasons"]]
    assert hit, [it["simulate"]["reasons"] for it in out["items"]]
    for it in hit:
        assert it["simulate"]["simulated"] is False and it["route"] != "SIMULATE"
        assert "retention_interval" not in it["simulate"]
    assert [i["route"] for i in base["items"]] == [i["route"] for i in out["items"]] or any(
        i["route"] == "SIMULATE" for i in out["items"])                      # never downgraded


def test_without_evidence_gates_the_lot_context_is_unconfirmed_so_no_simulate() -> None:
    out = route("Steam the orange juice for 10 minutes.", simulate=T.make_branch(), gates=False)
    s = out["items"][0]["simulate"]
    assert not s["simulated"] and "EVIDENCE_GATES_NOT_RUN" in s["reasons"] and out["items"][0]["route"] != "SIMULATE"


def test_a_merged_lot_never_simulates() -> None:
    out = route("Stir the orange juice with the sugar. Steam the mixture for 10 minutes.", simulate=T.make_branch())
    for it in out["items"]:
        g = it.get("gates") or {}
        if it["route"] == "SIMULATE":
            assert g.get("lot_context") == "SINGLE_MEMBER" and not it["prior_process"]
    steam = [it for it in out["items"] if it["process_id"] == T.STEAM]
    assert steam and all(it["route"] != "SIMULATE" for it in steam)


def test_simulate_only_ever_upgrades_unknown_never_replaces_stronger_routes() -> None:
    """A measured-evidence route (DIRECT) is pre-empting: the branch does not evaluate it and does not touch the route."""
    rows = [{"id": "EVD-T1", "version": 1, "status": "ACTIVE", "tier": "E3", "source_id": "SRC-1",
             "matrix": {"ingredient_id": T.ING}, "process": {"process_id": T.STEAM},
             "target": {"state_variable_id": VC, "raw_name": "Vitamin C"},
             "derived": {"retention_factor": {"status": "MEASURED", "value": 60.0, "unit": "%", "raw": "60"}},
             "verification": {"status": "UNVERIFIED"}}]
    idx = RD.EvidenceIndex.from_rows(rows)
    out = RD.route_text("Steam the orange juice for 10 minutes.", index=idx, target_svar=VC, gates=_gates(),
                        simulate=T.make_branch())
    it = out["items"][0]
    assert it["route"] == "DIRECT" and it["simulate"]["status"] == "NOT_EVALUATED_PREEMPTED"
    assert it["simulate"]["simulated"] is False


def test_hook_does_not_mutate_the_branch_or_inputs() -> None:
    br = T.make_branch()
    guard_before = copy.deepcopy(br.guard)
    route("Steam the orange juice for 10 minutes.", simulate=br)
    route("Steam the orange juice for 10 minutes.", simulate=br)
    assert br.guard == guard_before
