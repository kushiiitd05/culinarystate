"""D5 benchmark v1 built from the ksh+prv (AI, D-085) review (S179): deterministic, labelled, no recipe text."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
from collections import Counter
from pathlib import Path

import pytest

from culinarystate.evaluation import d5_scoring as DS
from culinarystate.evaluation import h1_independence as HI

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("d5rev", ROOT / "tools/s179_d085_d5_review.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


@pytest.fixture(scope="module")
def built():
    return {k: list(csv.DictReader(io.StringIO(b.decode()))) for k, b in R.build().items()}


def test_committed_files_equal_a_fresh_build():
    assert R.main(["--check"]) == 0


def test_block_sizes_and_rank_entry(built):
    n = Counter(r["block"] for k in ("S", "PC", "UX") for r in built[k])
    assert n == {"S1": 12, "S2": 12, "P1": 10, "P2": 10, "P3": 10, "C": 10, "U": 5, "X": 5}
    rev = built["REVIEW"]
    assert len(rev) == 110 and {r["reviewer"] for r in rev} == {R.REVIEWER}
    for b in n:
        ranks = [int(r["rank_in_block"]) for r in rev if r["block"] == b]
        kept = [int(r["rank_in_block"]) for r in rev if r["block"] == b and r["verdict"] == "KEEP"]
        entered = [int(r["rank_in_block"]) for r in rev if r["block"] == b and r["entered"] == "true"]
        assert entered == sorted(kept)[:len(entered)] and len(ranks) >= len(entered)


def test_benchmark_loads_and_gold_is_ai_labelled(built):
    rows = DS.load_benchmark([R.OUT["S"], R.OUT["PC"], R.OUT["UX"]])
    assert len(rows) == 74
    assert {r["gold_origin"] for r in rows} == {"AI_DRAFTED_GOLD"} and {r["label"] for r in rows} == {R.LABEL}
    rep = HI.gold_independence_report(rows)
    assert rep["n_independent"] == 0 and rep["n_refused"] == 0 and rep["label"] == "CIRCULAR_SELF_CONSISTENCY_ONLY"


def test_no_recipe_step_text_in_committed_files():
    ctx = ROOT / "annotation/d5_review/d5_S_context_v1.jsonl"
    if not ctx.is_file():
        pytest.skip("recipe context is Mac-only (git-ignored)")
    steps = [s for line in ctx.open(encoding="utf-8") for s in json.loads(line)["steps"] if len(s) > 30]
    text = "".join(R.OUT[k].read_text(encoding="utf-8") for k in R.OUT)
    assert not [s for s in steps if s in text]
