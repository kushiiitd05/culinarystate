"""S178 EVD lane, T2-C01-R2: helpers of the export reproducibility check (tiny synthetic ledgers; the real build is run by the tool)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
_spec = importlib.util.spec_from_file_location("s178_evd_export_repro", ROOT / "tools/s178_evd_export_repro.py")
RP = importlib.util.module_from_spec(_spec)
sys.modules["s178_evd_export_repro"] = RP
_spec.loader.exec_module(RP)

# inputs where glibc math.log is one ulp off the correctly rounded value (found by the S178 repro check on the real export)
GLIBC_GAP = ((1.1079265562024183, 0.10249030111227536), (1.1954397394136809, 0.17851410046737318), (0.1522633744855967, -1.882143530696324))


def test_correctly_rounded_log_matches_known_values():
    assert RP._correctly_rounded_log(1.0) == 0.0
    assert RP._correctly_rounded_log(math.e) == pytest.approx(1.0, rel=1e-15)
    for x, cr in GLIBC_GAP:
        assert RP._correctly_rounded_log(x) == cr


def test_csv_bytes_uses_the_builders_writer_defaults():
    b = RP._csv_bytes(["a", "b"], [[1, None], ["x,y", "z"]])
    assert b == b'a,b\r\n1,\r\n"x,y",z\r\n'
    assert hashlib.sha256(b).hexdigest() == RP.sha256_bytes(b)


def tiny_ledgers(tmp_path, before, after):
    led = tmp_path / "ledgers" / "data"
    led.mkdir(parents=True)
    evd = {"id": "EVD-000001", "version": 1, "status": "ACTIVE", "record_type": "EVD", "source_id": "SRC-000001", "source_family_id": "F", "study_ids": [], "study_id_status": "NOT_IDENTIFIABLE",
           "matrix": {"ingredient_id": None, "raw_name": "X", "food_group": "G"}, "process": {"process_id": None, "raw_name": "P", "steps": ["boil"], "condition_id": "COND-000001"},
           "target": {"state_variable_id": "SVAR-000001", "raw_name": "T", "basis": "FRESH_WEIGHT"},
           "before": {"status": "MEASURED", "value": before, "unit": "mg"}, "after": {"status": "MEASURED", "value": after, "unit": "mg"},
           "derived": {"direction": "INCREASE"}, "tier": "E3", "verification": {"status": "UNVERIFIED"}, "provenance": {"method": "IMPORT", "source_ids": ["SRC-000001"]}, "censored": False}
    (led / "EVD.jsonl").write_text(json.dumps(evd) + "\n", encoding="utf-8")
    (led / "COND.jsonl").write_text(json.dumps({"id": "COND-000001", "version": 1, "completeness_mask": {}}) + "\n", encoding="utf-8")
    (led / "PROC.jsonl").write_text("", encoding="utf-8")
    return tmp_path


def test_neutral_build_uses_the_correctly_rounded_log_and_restores_math(tmp_path):
    from culinarystate.evidence import evd_export as X
    real = X.math
    root = tiny_ledgers(tmp_path, 1.0, 1.1079265562024183)
    rows, _, _, _ = RP.build_rows(root, neutral=True)
    assert X.math is real                                                   # patch is undone
    assert rows[0]["log_fold_change"] == 0.10249030111227536                # correctly rounded ln(1.1079265562024183)
    plain, _, _, _ = RP.build_rows(root, neutral=False)
    assert plain[0]["log_fold_change"] == pytest.approx(0.10249030111227536, abs=3e-16)   # host libm may differ in the last digit only
    assert {k for k in rows[0] if rows[0][k] != plain[0][k]} <= {"log_fold_change"}


def test_build_rows_restores_math_even_when_the_build_fails(tmp_path):
    from culinarystate.evidence import evd_export as X
    real = X.math
    with pytest.raises(Exception):
        RP.build_rows(tmp_path / "missing", neutral=True)
    assert X.math is real
