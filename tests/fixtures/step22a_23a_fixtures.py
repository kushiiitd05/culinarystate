"""SYNTHETIC fixtures for Step 22a process signatures and the Step 23a applicability engine (S158).

Built on tests/fixtures/mech_v1_1_fixtures.py. Every mechanism key, process id, state name, category and
bound here is a placeholder (SYNTH_*, PROC-SYN*, dummy numbers 1.0 / 10.0): structure only, never a real
mechanism, pathway, process-to-mechanism link or scientific value. Nothing here is a sealed case or a label.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from tests.fixtures.mech_v1_1_fixtures import (
    accepted,
    competes,
    evidence_ref,
    gate,
    open_,
    precondition,
    scope,
    state,
    stated,
    target,
)

MATRIX = "synthetic class"
TARGET_STATE = "synthetic_target"

# Synthetic hierarchy rows in the column layout of registry/processes/process_hierarchy_v1_DRAFT.csv.
HIERARCHY_ROWS: list[dict[str, str]] = [
    {"id": "FAM:SYNTH_FAMILY", "name": "SYNTH_FAMILY", "proposed_parent_id": "", "level": "1", "endpoint_flag": "false",
     "evidence": "synthetic"},
    {"id": "FAM:SYNTH_OTHER", "name": "SYNTH_OTHER", "proposed_parent_id": "", "level": "1", "endpoint_flag": "false",
     "evidence": "synthetic"},
    {"id": "PROC-SYN001", "name": "synth leaf one", "proposed_parent_id": "FAM:SYNTH_FAMILY", "level": "2",
     "endpoint_flag": "false", "evidence": "synthetic"},
    {"id": "PROC-SYN002", "name": "synth leaf two", "proposed_parent_id": "FAM:SYNTH_FAMILY", "level": "2",
     "endpoint_flag": "false", "evidence": "synthetic"},
    {"id": "ALIAS:PROC-SYN001:a", "name": "synth alias", "proposed_parent_id": "PROC-SYN001", "level": "3",
     "endpoint_flag": "false", "evidence": "synthetic"},
    {"id": "PROC-SYN003", "name": "synth other leaf", "proposed_parent_id": "FAM:SYNTH_OTHER", "level": "2",
     "endpoint_flag": "false", "evidence": "synthetic"},
    {"id": "PROC-SYN900", "name": "synth endpoint", "proposed_parent_id": "", "level": "", "endpoint_flag": "true",
     "evidence": "synthetic endpoint, outside hierarchy"},
]


def accepted_target(key: str = "TGT01", dirs: Iterable[str] = ("DECREASE",), state_key: str = TARGET_STATE,
                    **over: Any) -> dict[str, Any]:
    kw: dict[str, Any] = {"status": "ACCEPTED", "evidence_ids": ["SRC-000001"], "target": state(state_key)}
    kw.update(over)
    return target(dirs=dirs, key=key, **kw)


def mech(key: str = "SYNTH_FIXTURE_ONE", mid: str = "MECH-000001", *, dirs: Iterable[str] = ("DECREASE",),
         **over: Any) -> dict[str, Any]:
    """A fully specified ACCEPTED synthetic entry: one NECESSARY CV-013 TISSUE gate [1.0, open 10.0], one
    precondition synthetic_state IS SYNTH_A, matrix 'synthetic class', one ACCEPTED target synthetic_target."""
    base = {"mechanism_key": key, "id": mid, "affected_targets": [accepted_target(dirs=dirs)]}
    base.update(over)
    return accepted(**base)


def inhibiting_gate(key: str = "CG02", mn: float = 20.0, mx: float = 30.0) -> dict[str, Any]:
    """An ACCEPTED INHIBITING gate on CV-013 TISSUE (synthetic placeholder window)."""
    return gate(gtype="INHIBITING", key=key, mn=stated(mn), mx=stated(mx), evidence_ids=["SRC-000001"],
                status="ACCEPTED", matrix_scope=scope("FOOD_CLASS", inc=(MATRIX,)),
                rationale_raw="synthetic inhibiting window")


def necessary_gate(key: str = "CG01", cv: str = "CV-013", unit: str = "pH", mn: Any = None, mx: Any = None,
                   **over: Any) -> dict[str, Any]:
    kw: dict[str, Any] = {"evidence_ids": ["SRC-000001"], "status": "ACCEPTED",
                          "matrix_scope": scope("FOOD_CLASS", inc=(MATRIX,)),
                          "rationale_raw": "synthetic: a PRIMARY source states absence outside this window"}
    kw.update(over)
    return gate(cv=cv, key=key, unit=unit, mn=mn or stated(1.0), mx=mx or open_(10.0), **kw)


def accepted_competitor(key: str, relation: str = "PARALLEL_PATHWAY") -> dict[str, Any]:
    c = competes(relation=relation, key=key)
    c.update(status="ACCEPTED", evidence_ids=["SRC-000001"])
    return c


def accepted_precondition(**over: Any) -> dict[str, Any]:
    return precondition(status="ACCEPTED", evidence_ids=["SRC-000001"], **over)


def rule(rule_key: str = "SYNTH_RULE_ONE", process_ref: str = "PROC-SYN001", mechanism_keys: Iterable[str] =
         ("SYNTH_FIXTURE_ONE",), **over: Any) -> dict[str, Any]:
    """Keyword arguments for process_signatures.SignatureRule (synthetic rule, not a real process link)."""
    r: dict[str, Any] = {"rule_key": rule_key, "process_ref": process_ref, "include_descendants": True,
                         "modifier_predicates": (), "mechanism_keys": tuple(mechanism_keys),
                         "heat_transfer_mode_ids": (), "deterministic_change_refs": (),
                         "rationale_raw": "synthetic rule for structure tests", "authored_by": "synthetic-fixture"}
    r.update(over)
    return r


__all__ = ["HIERARCHY_ROWS", "MATRIX", "TARGET_STATE", "accepted_competitor", "accepted_precondition",
           "accepted_target", "evidence_ref", "inhibiting_gate", "mech", "necessary_gate", "rule"]
