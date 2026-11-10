"""S179 (D-080..D-082): the three pre-registration DRAFT files equal the mechanical build from their git base text and
the S178 amendments; chosen options present, alternatives gone, open human choices still visibly open, nothing signed."""
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = runpy.run_path(str(ROOT / "tools/s179_apply_prereg_amendments.py"), run_name="lib")


def _text(name):
    return (ROOT / M["DOCS"][name]["draft"]).read_text(encoding="utf-8")


def test_each_draft_equals_its_build():
    for name in M["DOCS"]:
        assert _text(name) == M["build"](name), name


def test_d5_options_and_open_sidedness():
    t = _text("D5")
    for must in ("intfloat/e5-large-v2", "f169b11e22de13617baa190a028a32f3493550b6",
                 "845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e", "(uncalibrated)", "n = 30",
                 "**Veto:**", "OPEN, D-D5-6", "not a human sitting", "DRAFT_PENDING_SIGNATURES"):
        assert must in t, must
    assert "Kush Tokas: ______" not in t


def test_29diag_and_aa_options():
    d = _text("D29")
    assert "D3 = B-2" not in d and "B2 = TB-V0 B-2 ingredient-conditioned mean" in d and "food_group_disjoint" in d
    a = _text("AA")
    for must in ("## 7. Where a SIMULATE number may be used", "(a) Kush moves the SIM-VAL PDFs", "and (b) SIM-VAL rows",
                 "BASIS_MISMATCH_TOTAL_VITC", "RESEARCH_ONLY"):
        assert must in a, must


def test_no_signature_files_created():
    for p in ("reports/del5/d5_prereg_signature_Kush.json", "reports/del5/d5_prereg_signature_Parv.json",
              "reports/step29/29diag_prereg_signature.json", "reports/step10/aa_pilot_prereg_signature_Kush.json",
              "reports/step10/aa_pilot_prereg_signature_Parv.json"):
        assert not (ROOT / p).exists(), p
