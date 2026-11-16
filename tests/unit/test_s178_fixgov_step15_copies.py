"""S178 FIX-GOV, board T2-C15-R1 / T2-C01-R1: the reports/step15/ copies of the EVD dataset card and the 203.2 field
conformance table are byte-identical to their S178 sources, and README_S178_copies.md names each source with its sha256.

If a source is regenerated, the copy must be refreshed (and the README hash with it); this test then fails until that is done.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COPIES = {
    "reports/step15/dataset_card_15a_v1.md": "reports/s178/analysis/evd_dataset_card_v1.md",
    "reports/step15/dataset_card_15a_v1.json": "reports/s178/analysis/evd_dataset_card_v1.json",
    "reports/step15/evd_field_conformance_203_2_v1.csv": "reports/s178/evd/evd_field_conformance_203_2_v1.csv",
    "reports/step15/evd_field_conformance_203_2_v1.md": "reports/s178/evd/evd_field_conformance_203_2_v1.md",
    "reports/step15/evd_field_conformance_203_2_v1.json": "reports/s178/evd/evd_field_conformance_203_2_v1.json",
}
README = ROOT / "reports/step15/README_S178_copies.md"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.mark.parametrize("copy,source", sorted(COPIES.items()))
def test_copy_is_byte_identical_to_its_source(copy, source):
    assert (ROOT / copy).read_bytes() == (ROOT / source).read_bytes(), f"{copy} differs from {source}: re-copy it"


def test_readme_lists_every_copy_with_the_source_path_and_sha256():
    text = README.read_text(encoding="utf-8")
    for copy, source in COPIES.items():
        line = next((x for x in text.splitlines() if f"`{copy}`" in x), None)
        assert line is not None, copy
        assert f"`{source}`" in line and _sha(ROOT / source) in line, copy
    assert re.search(r"AI_DRAFTED", text) and "not a freeze" in text.lower()
