"""Tests for tools/step35_foodcom_tag_census.py (D-036 draft, unsigned)."""
import csv
import hashlib
import importlib.util
from pathlib import Path

import pyarrow.parquet as pq
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("census", ROOT / "tools/step35_foodcom_tag_census.py")
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)

pytestmark = pytest.mark.skipif(not census.SRC.exists(), reason="local Food.com parquet absent")
TEXT_COLS = {"Name", "Description", "RecipeInstructions", "RecipeIngredientParts",
             "RecipeIngredientQuantities", "AuthorName", "Images"}


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_clean_tags_robust():
    assert census.clean_tags(None) == frozenset()
    assert census.clean_tags([" a ", "", "a", None, "b"]) == frozenset({"a", "b"})
    assert census.clean_tags("Dessert") == frozenset({"Dessert"})


def test_deterministic_and_sorted():
    c1, n1 = census.count_tags()
    c2, n2 = census.count_tags()
    assert c1 == c2 and n1 == n2
    r = census.rows(c1)
    assert r == sorted(r, key=lambda x: (-x[1], x[0], x[2]))
    assert all(x[1] >= census.MIN_RECIPES for x in r)


def test_only_tag_columns_read_and_written(monkeypatch):
    seen = []
    orig = pq.ParquetFile.iter_batches

    def spy(self, *a, **k):
        seen.append(tuple(k.get("columns") or ()))
        return orig(self, *a, **k)

    monkeypatch.setattr(pq.ParquetFile, "iter_batches", spy)
    census.count_tags()
    census.derive()
    assert seen and all(set(s) == {"Keywords", "RecipeCategory"} for s in seen)
    assert not TEXT_COLS & set(census.COLUMNS)
    for out in (census.OUT, census.MAP_OUT, census.EXPL_OUT):
        header = [l for l in out.read_text().splitlines() if not l.startswith("#")][0].split(",")
        assert not TEXT_COLS & set(header) and "recipe_id" not in header and "RecipeId" not in header


def test_counts_reconcile_to_parquet_rows():
    tag_n, st = census.derive()
    n = pq.ParquetFile(census.SRC).metadata.num_rows
    assert st["n_rows"] == n
    assert st["n_ge1_mapped"] + st["n_unknown"] == n
    assert st["n_conflicting"] <= st["n_ge1_mapped"]
    assert max(tag_n.values()) <= n


def test_lookup_unique_terms_and_valid_values():
    rows = list(csv.DictReader(census.LOOKUP.open()))
    terms = [r["term"].casefold() for r in rows]
    assert len(terms) == len(set(terms))
    assert all(r["cuisine"] and r["continent"] and r["basis"] for r in rows)
    ok = {"Africa", "Americas", "Asia", "Europe", "Oceania", "MIXED", "NEEDS_HUMAN"}
    assert {r["continent"] for r in rows} <= ok
    assert "UNKNOWN" not in {r["cuisine"] for r in rows}


def test_unknown_tags_never_mapped_and_status_draft():
    lk = census.load_lookup()
    rows = list(csv.DictReader(census.MAP_OUT.open()))
    for r in rows:
        assert r["status"] == "DRAFT_PENDING_SIGN"
        if r["proposed_cuisine"] == "UNKNOWN":
            assert r["proposed_continent"] == "UNKNOWN" and r["tag"].casefold() not in lk
        else:
            assert r["tag"].casefold() in lk


def test_map_does_not_modify_source():
    before = _sha(census.SRC) if census.SRC.stat().st_size < 10**9 else None
    census.derive()
    assert before is None or before == _sha(census.SRC)
