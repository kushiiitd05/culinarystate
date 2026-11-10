"""S179: the D5 prereg v2 draft is exactly the mechanical build from v1 + S178 amendment with D-080/D-081 options."""
import hashlib
import os
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V1 = ROOT / "reports/del5/d5_benchmark_preregistration_DRAFT.md"
V2 = ROOT / "reports/del5/d5_benchmark_preregistration_v2_DRAFT.md"


def _build() -> str:
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        return runpy.run_path(str(ROOT / "tools/s179_build_d5_prereg_v2.py"))["build"]()
    finally:
        os.chdir(cwd)


def test_v1_untouched_and_v2_equals_the_build():
    assert hashlib.sha256(V1.read_bytes()).hexdigest() == "53ad89b7c13db57800e4546efb2ccfe29cdb2ef617b49c462c8b78f51415aa6b"
    assert V2.read_text(encoding="utf-8") == _build()


def test_chosen_options_present_alternatives_gone_sidedness_open():
    t = V2.read_text(encoding="utf-8")
    for must in ("e5-large-v2", "f169b11e22de13617baa190a028a32f3493550b6", "845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e",
                 "(uncalibrated)", "n = 30", "**Veto:**", "NOT_RUN", "OPEN, D-D5-6", "not a human sitting"):
        assert must in t, must
    for gone in ("[S60]", "[K2", "[G-B", "[BGE", "[F2", "9-10 Nov\nsitting chose", "Kush Tokas: ______"):
        assert gone not in t, gone
    assert "DRAFT_PENDING_SIGNATURES" in t
