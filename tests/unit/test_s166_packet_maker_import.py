"""S166 review block L2 (ksh KA8, prv PA8): importing the Step 19 packet maker must not run it.

Reviewers needed the maker's records() helper and importing the module ran argparse (main() was unguarded).
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_importing_the_packet_maker_does_not_run_it(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["step19_packet_maker.py"])  # no --letter: running main() would SystemExit
    spec = importlib.util.spec_from_file_location("maker_import_check", ROOT / "tools/step19_packet_maker.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert callable(mod.main) and callable(mod.records)
