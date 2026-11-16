"""Private source evidence remains excluded regardless of CSV versus JSON format."""
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("path", [
    "annotation/aa_pilot/source_proof.json",
    "annotation/aa_pilot/source_rows.csv",
    "annotation/d5_review/d5_S_context_v1.jsonl",
    "data/raw/aa_pilot_simval_quarantine/AAK-12.pdf",
])
def test_private_evidence_paths_are_ignored(path):
    assert subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", "--", path]).returncode == 0
