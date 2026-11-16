"""tools/aa_pilot_fit.py --delegate (S179, D-085): one AI_PRECHECKED verification file, labelled, never human."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("aafit", ROOT / "tools/aa_pilot_fit.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)
COLS = ["row_id", "candidate_id", "row_type", "T_C", "order", "value", "verdict", "corrected_value", "verified_by"]


def _sheet(tmp_path, who="ksh+prv (AI, D-085)"):
    rows = []
    for i, (paper, T_C, k) in enumerate([("SYN-A", 70, 0.01), ("SYN-A", 80, 0.02), ("SYN-A", 90, 0.04),
                                         ("SYN-B", 70, 0.012), ("SYN-B", 80, 0.025), ("SYN-B", 90, 0.05)]):
        rows.append({"row_id": f"R{i}", "candidate_id": paper, "row_type": "K_AT_T", "T_C": T_C, "order": "first",
                     "value": k, "verdict": "VERIFIED", "corrected_value": "", "verified_by": who})
    p = tmp_path / "verify.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    return p


def test_delegate_fit_is_labelled_ai_prechecked(tmp_path):
    out = tmp_path / "fit.json"
    assert T.main(["--delegate", str(_sheet(tmp_path)), "--out", str(out)]) == 0
    rep = json.loads(out.read_text())
    assert rep["signoff"] == "AI_DELEGATED_D085" and rep["label"] == "NO_HUMAN_SIGNOFF_D085"
    assert rep["verification"] == "AI_PRECHECKED" and rep["fit"]["n_papers"] == 2
    assert "Kush" not in json.dumps(rep["returned_sha256"])


def test_delegate_sheet_must_name_only_the_delegate(tmp_path):
    with pytest.raises(SystemExit):
        T.main(["--delegate", str(_sheet(tmp_path, who="Kush Tokas")), "--out", str(tmp_path / "f.json")])


def test_human_and_delegate_modes_are_exclusive(tmp_path):
    p = _sheet(tmp_path)
    with pytest.raises(SystemExit):
        T.main(["--delegate", str(p), "--kush", str(p), "--parv", str(p), "--out", str(tmp_path / "f.json")])
