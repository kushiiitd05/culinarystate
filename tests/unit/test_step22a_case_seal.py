"""Case-set sealing helper for the shared Step 22c / 23 case set (S158, DRAFT_PENDING_21b_H4).

The spine makes "shared case set sealed before rule coding" a HUMAN gate. This test exercises the hash-commit
helper on SYNTHETIC placeholder cases only; it seals nothing real, authors no case and writes no file.
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest

from culinarystate.mechanism import case_seal as CS

NONCE = "00" * 32


def cases() -> list[dict[str, object]]:
    return [{"case_id": "SYNTH-CASE-002", "split": "TEST", "payload": {"x": "SYNTH_A"}},
            {"case_id": "SYNTH-CASE-001", "split": "DEV", "payload": {"x": "SYNTH_B"}}]


def test_status_says_the_human_gate_is_open() -> None:
    assert CS.STATUS == "DRAFT_PENDING_21b_H4"
    assert CS.CASE_SET_STATUS == "NOT_SEALED_HUMAN_GATE_OPEN"
    assert CS.HUMAN_SEALERS == ("Kush Tokas", "Parv Goyal")


def test_commitment_is_order_independent_and_changes_with_any_byte() -> None:
    a = CS.case_set_commitment(cases(), nonce_hex=NONCE)
    b = CS.case_set_commitment(list(reversed(cases())), nonce_hex=NONCE)
    assert a == b
    assert a["n_cases"] == 2 and a["n_by_split"] == {"DEV": 1, "TEST": 1} and a["algorithm"] == "sha256"
    assert re.fullmatch(r"[0-9a-f]{64}", a["commitment"])
    changed = cases()
    changed[0]["payload"] = {"x": "SYNTH_C"}
    assert CS.case_set_commitment(changed, nonce_hex=NONCE)["commitment"] != a["commitment"]
    assert CS.case_set_commitment(cases(), nonce_hex="11" * 32)["commitment"] != a["commitment"]


def test_case_shape_is_checked() -> None:
    dup = cases() + [copy.deepcopy(cases()[0])]
    no_split = [{"case_id": "SYNTH-CASE-003"}]
    bad_split = [{"case_id": "SYNTH-CASE-003", "split": "TRAIN"}]
    for bad in (dup, no_split, bad_split, []):
        with pytest.raises(CS.CaseSealError):
            CS.case_set_commitment(bad, nonce_hex=NONCE)
    for nonce in ("", "zz" * 32, "00" * 8):
        with pytest.raises(CS.CaseSealError):
            CS.case_set_commitment(cases(), nonce_hex=nonce)


def test_manifest_needs_named_humans_and_no_rule_set_at_seal_time() -> None:
    m = CS.seal_manifest(cases(), nonce_hex=NONCE, sealed_by=("Kush Tokas",), sealed_at="2026-11-03T00:00:00+00:00")
    assert m["sealed_by"] == ["Kush Tokas"] and m["rules_present_at_seal"] is False
    assert m["case_set_status"] == "SEALED_BY_HUMAN" and m["nonce_disclosed"] is False
    assert "nonce" not in m and NONCE not in str(m)
    for who in ((), ("prv",), ("ksh",), ("Kush Tokas", "AI agent")):
        with pytest.raises(CS.CaseSealError):
            CS.seal_manifest(cases(), nonce_hex=NONCE, sealed_by=who, sealed_at="2026-11-03T00:00:00+00:00")
    with pytest.raises(CS.CaseSealError, match="rule"):
        CS.seal_manifest(cases(), nonce_hex=NONCE, sealed_by=("Parv Goyal",), sealed_at="2026-11-03T00:00:00+00:00",
                         rules_present=True)
    with pytest.raises(CS.CaseSealError):
        CS.seal_manifest(cases(), nonce_hex=NONCE, sealed_by=("Parv Goyal",), sealed_at="not a time")


def test_verify_against_manifest() -> None:
    m = CS.seal_manifest(cases(), nonce_hex=NONCE, sealed_by=("Parv Goyal",), sealed_at="2026-11-03T00:00:00+00:00")
    assert CS.verify_case_set(cases(), m, nonce_hex=NONCE) is True
    changed = cases()
    changed[1]["split"] = "TEST"
    assert CS.verify_case_set(changed, m, nonce_hex=NONCE) is False
    assert CS.verify_case_set(cases(), m, nonce_hex="11" * 32) is False


def test_rules_citing_test_case_ids_are_reported() -> None:
    texts = {"SYNTH_RULE_ONE": "derived from SYNTH-CASE-002 by inspection", "SYNTH_RULE_TWO": "no case cited",
             "SYNTH_RULE_THREE": "dev case SYNTH-CASE-001 only"}
    assert CS.rules_citing_test_cases(texts, cases()) == [("SYNTH_RULE_ONE", "SYNTH-CASE-002")]


def test_module_writes_nothing() -> None:
    src = Path(CS.__file__).read_text(encoding="utf-8")
    for banned in ("write_text", "write_bytes", "open(", "ledgers/data", "subprocess"):
        assert banned not in src, banned
