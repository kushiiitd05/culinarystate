"""S173: ingredient-line export for corpus NER (D-003 guard, data plane only)."""
from __future__ import annotations

import importlib.util
import json
import platform
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _tool():
    spec = importlib.util.spec_from_file_location("eil", ROOT / "tools/export_ingredient_lines.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def src(families, root):
    for fam in families:
        yield {"recipe_id": f"{fam}-1", "ingredient_lines": ["2 carrots", "  ", "1 tbsp oil"]}
        yield {"recipe_id": f"{fam}-2", "ingredient_lines": []}


def test_exports_lines_and_skips_empty(tmp_path):
    out = tmp_path / "lines"
    assert _tool().main(["--families", "WIKIBOOKS", "--out", str(out)], record_source=src) == 0
    rows = [json.loads(l) for l in (out / "WIKIBOOKS.jsonl").read_text().splitlines()]
    assert rows == [{"recipe_id": "WIKIBOOKS-1", "source_family": "WIKIBOOKS", "lines": ["2 carrots", "1 tbsp oil"]}]


def test_bbc_refused_without_flag_and_off_mac(tmp_path, monkeypatch):
    t = _tool()
    with pytest.raises(SystemExit):
        t.main(["--families", "A1_BBC_GOOD_FOOD", "--out", str(tmp_path / "a")], record_source=src)
    monkeypatch.setattr(platform, "system", lambda: "Linux")
    with pytest.raises(SystemExit):
        t.main(["--families", "A1_BBC_GOOD_FOOD", "--allow-bbc", "--out", str(tmp_path / "b")], record_source=src)


def test_refuses_tracked_locations_and_non_empty(tmp_path):
    t = _tool()
    with pytest.raises(SystemExit):
        t.main(["--families", "WIKIBOOKS", "--out", str(ROOT / "reports" / "x")], record_source=src)
    (tmp_path / "c").mkdir()
    (tmp_path / "c" / "f").write_text("x")
    with pytest.raises(SystemExit):
        t.main(["--families", "WIKIBOOKS", "--out", str(tmp_path / "c")], record_source=src)
