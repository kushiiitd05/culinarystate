"""S179 SCI re-review #3: the until-clause counter of the FIX-PHYS audit reads temperature roles (it never fired)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("_audit", ROOT / "tools/s178_phys_fixphys_audit.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def _rec(role):
    sp = [20, 26]
    return {"family": "FAT_HEAT", "inputs": {"temperature_profile": {"status": "MEASURED", "basis": "TEXT_STATED",
                                                                     "value": "74", "span": sp, "row": "X"}},
            "endpoint": {"cues": [], "until_clauses": [{"span": [10, 40], "temperatures": [{"span": sp, "role": role}]}]}}


def test_until_clause_counter_splits_exempt_target_and_unclassified(tmp_path):
    p = tmp_path / "part-00000.jsonl"
    p.write_text("\n".join(json.dumps(_rec(r)) for r in
                           ("EXEMPT_SYRUP_OR_CANDY", "TARGET_UNTIL_CLAUSE", "TARGET_STRONG_CUE", None)) + "\n")
    c = A.scan_l1(str(p))
    assert c["until_clause_bound_temperature_clause_spans_syrup_exempt"] == 1
    assert c["until_clause_bound_temperature_clause_spans_target_role"] == 2       # the invariant: must be 0 on real data
    assert c["until_clause_bound_temperature_clause_spans_unclassified"] == 1
    assert c["until_clause_bound_temperature_clause_spans"] == 3                   # non-exempt total, as before
