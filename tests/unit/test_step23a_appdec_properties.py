"""Property tests for the Step 23a engine: UNKNOWN never routes to SIMULATE (S158, DRAFT_PENDING_21b_22a_H4).

Plan card output tests/property/test_appdec_unknown_never_simulates.py; kept under tests/unit so the full unit
suite runs it. Randomised SYNTHETIC queries over placeholder entries (hypothesis, plus a seeded loop of 10^4
queries for G23.2's ">= 10^4 randomised property-test queries"). Invariants:
- a required NECESSARY axis that is UNKNOWN (missing, None, wrong location or unit) never yields an APPLICABLE
  mechanism, APPLICABLE applicability or a SIMULATE route / cross-check;
- SIMULATE (route or cross-check) implies G1 and G4..G8 APPLICABLE, a validated domain and safety NO;
- a non-consumable MECH entry is never APPLICABLE;
- evaluation is deterministic (byte-identical records).
"""
from __future__ import annotations

import json
import random
from typing import Any

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from culinarystate.mechanism import applicability as AP
from culinarystate.mechanism import process_signatures as PS
from tests.fixtures.mech_v1_1_fixtures import entry, open_question
from tests.fixtures.step22a_23a_fixtures import HIERARCHY_ROWS, MATRIX, mech, rule

A, NA, U = "APPLICABLE", "NOT_APPLICABLE", "UNKNOWN"
H = PS.hierarchy_from_rows(HIERARCHY_ROWS)
ENTRIES = {
    "accepted": [mech()],
    "candidate": [entry()],
    "open_question": [mech(open_questions=[open_question()])],
}
SIGS = {k: PS.build_signatures([PS.SignatureRule(**rule(mechanism_keys=(v[0]["mechanism_key"],)))], v, H,
                               heat_transfer_mode_ids=frozenset()).signatures for k, v in ENTRIES.items()}
VERDICT_OR_NONE = [A, NA, U, None]
REASON = {"G6": {NA: ("ASSUMPTION_VIOLATED",), U: ("NO_FORM",)}, "G7": {NA: ("INPUT_UNOBSERVED",), U: ("INPUT_UNOBSERVED",)},
          "G8": {NA: ("NO_COMPATIBLE_PARAM",), U: ("PARAM_UNCONFIRMABLE",)}}


def case_gate(gate: str, v: str | None) -> AP.CaseGate | None:
    if v is None:
        return None
    return AP.CaseGate(A, (), f"SYNTH-{gate}") if v == A else AP.CaseGate(v, REASON[gate][v])


def axis(kind: str, value: float) -> tuple[AP.AxisValue, ...]:
    return {"missing": (), "none": (AP.AxisValue("CV-013", "TISSUE", None, "pH"),),
            "wrong_location": (AP.AxisValue("CV-013", "MEDIUM", value, "pH"),),
            "wrong_unit": (AP.AxisValue("CV-013", "TISSUE", value, "K"),),
            "stated": (AP.AxisValue("CV-013", "TISSUE", value, "pH"),),
            "interval": (AP.AxisValue("CV-013", "TISSUE", (value, value + 1.0), "pH"),)}[kind]


def query(p: dict[str, Any]) -> AP.ApplicabilityQuery:
    return AP.ApplicabilityQuery(
        case_id="SYNTH-PROP", entity_version_id="SYN-ENT@1", event_id="E1", target_svar_id=None,
        target_state_key="synthetic_target", process_id=p["process"], event_resolved=p["process"] is not None,
        matrix=p["matrix"], states=p["states"], axes=axis(p["axis"], p["value"]),
        formula=case_gate("G6", p["g6"]), observability=case_gate("G7", p["g7"]), parameters=case_gate("G8", p["g8"]),
        evidence_precheck=p["g0"], domain_flag=p["domain"], safety_critical=p["safety"],
        user_observable=p["observable"])


def check(rec: dict[str, Any], p: dict[str, Any], kind: str) -> None:
    g = {k: v["verdict"] for k, v in rec["gates"].items()}
    sim = rec["route"] == "SIMULATE" or rec["cross_check"] == "SIMULATE"
    if sim:
        assert all(g[x] == A for x in ("G1", "G4", "G5", "G6", "G7", "G8")), rec
        assert rec["domain_flag"] == "IN_VALIDATION_DOMAIN" and rec["safety_critical"] == "NO"
        assert rec["applicability"] == A
    if any(g[x] in (U, NA) for x in ("G1", "G4", "G5", "G6", "G7", "G8")):
        assert not sim and rec["applicability"] != A
    if p["axis"] in ("missing", "none", "wrong_location", "wrong_unit"):
        assert all(m["verdict"] != A for m in rec["mechanisms"])
        assert rec["applicability"] != A and not sim
    if kind != "accepted":
        assert all(m["verdict"] == U and not m["consumable"] for m in rec["mechanisms"])
        assert not sim
    if rec["applicability"] == U:
        assert rec["route"] != "SIMULATE"


PARAMS = st.fixed_dictionaries({
    "kind": st.sampled_from(sorted(ENTRIES)), "process": st.sampled_from(["PROC-SYN001", "PROC-SYN003", None]),
    "matrix": st.sampled_from([MATRIX, "synthetic other", None]),
    "states": st.sampled_from([{"synthetic_state": "SYNTH_A"}, {"synthetic_state": "SYNTH_B"},
                               {"synthetic_state": "UNKNOWN"}, {}]),
    "axis": st.sampled_from(["missing", "none", "wrong_location", "wrong_unit", "stated", "interval"]),
    "value": st.floats(min_value=-1.0, max_value=13.0, allow_nan=False),
    "g6": st.sampled_from(VERDICT_OR_NONE), "g7": st.sampled_from(VERDICT_OR_NONE),
    "g8": st.sampled_from(VERDICT_OR_NONE), "g0": st.sampled_from(sorted(AP.EVIDENCE_PRECHECK)),
    "domain": st.sampled_from(sorted(AP.DOMAIN_FLAGS)), "safety": st.sampled_from(sorted(AP.SAFETY)),
    "observable": st.sampled_from([(), ("axis:CV-013@TISSUE",), ("state:synthetic_state",)]),
})


@settings(max_examples=400, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(PARAMS)
def test_property_unknown_never_reaches_simulate(p: dict[str, Any]) -> None:
    kind = p["kind"]
    rec = AP.evaluate(query(p), SIGS[kind], ENTRIES[kind], H)
    check(rec, p, kind)


@settings(max_examples=100, deadline=None)
@given(PARAMS)
def test_property_evaluation_is_deterministic(p: dict[str, Any]) -> None:
    kind = p["kind"]
    a = AP.evaluate(query(p), SIGS[kind], ENTRIES[kind], H)
    b = AP.evaluate(query(p), SIGS[kind], ENTRIES[kind], H)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_seeded_ten_thousand_queries_never_simulate_from_unknown() -> None:
    rng = random.Random(23)
    choices: dict[str, list[Any]] = {
        "kind": sorted(ENTRIES), "process": ["PROC-SYN001", "PROC-SYN003", None], "matrix": [MATRIX, "x", None],
        "states": [{"synthetic_state": "SYNTH_A"}, {"synthetic_state": "SYNTH_B"}, {}],
        "axis": ["missing", "none", "wrong_location", "wrong_unit", "stated", "interval"],
        "g6": VERDICT_OR_NONE, "g7": VERDICT_OR_NONE, "g8": VERDICT_OR_NONE, "g0": sorted(AP.EVIDENCE_PRECHECK),
        "domain": sorted(AP.DOMAIN_FLAGS), "safety": sorted(AP.SAFETY),
        "observable": [(), ("axis:CV-013@TISSUE",)]}
    simulate = 0
    for _ in range(10_000):
        p = {k: rng.choice(v) for k, v in choices.items()}
        p["value"] = rng.uniform(-1.0, 13.0)
        rec = AP.evaluate(query(p), SIGS[p["kind"]], ENTRIES[p["kind"]], H)
        check(rec, p, p["kind"])
        simulate += rec["route"] == "SIMULATE"
    assert simulate > 0, "anti-triviality: the complete-input branch is reachable"
