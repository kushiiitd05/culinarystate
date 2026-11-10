"""D5 rung runner (S179): record shape on real benchmark rows with a fake LLM and embedder (no GPU, no network)."""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

from culinarystate.evaluation import d5_scoring as DS

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("d5run", ROOT / "tools/s179_d5_run_rungs.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)


@pytest.fixture(scope="module")
def ctx():
    import run_ladder as RL
    st = RL.LedgerStore()
    lex, fam = RL.load_lexicon(st)
    cond = {c["id"]: c for c in st.all_latest("COND")}
    evd = st.all_latest("EVD")
    return (lex, RL.EvidenceRetriever(evd, cond, fam), RL.load_requirements(st), fam, RL.SupportIndex(evd),
            RL.TroubleshootIndex.from_registry(ROOT))


def _row(path, block):
    with (ROOT / path).open(encoding="utf-8") as fh:
        return next(r for r in csv.DictReader(fh) if r["block"] == block)


def test_s_records_have_outcomes_and_config(ctx):
    row = _row(T.BENCH[0], "S2")
    steps = [f"Step text {i} boil the water." for i in range(1, int(row["cut_after_step"]) + 2)]
    recs = T.s_records(row, steps, embed=lambda xs: [[1.0, float(i)] for i in range(len(xs))],
                       generate=lambda p: "stir", lex=ctx[0])
    assert [r["rung"] for r in recs] == list(T.S_RUNGS)
    assert all(r["s_outcome"] in (True, False, "UNRESOLVED") for r in recs)
    assert all(set(r) <= set(DS.RUN_RECORD_FIELDS) for r in recs)


def test_pc_records_map_ladder_rungs(ctx, monkeypatch):
    import run_ladder as RL
    monkeypatch.setattr(RL, "generate", lambda prompt, model: "It keeps some folate.")
    row = _row(T.BENCH[1], "P1")
    recs = T.pc_records(row, ctx, model="fake", branch="TRANSFORMATION")
    assert [r["rung"] for r in recs] == ["B0", "B2", "B5", "B7", "B5T"]
    assert all(set(r) <= set(DS.RUN_RECORD_FIELDS) for r in recs)
    b7 = next(r for r in recs if r["rung"] == "B7")
    assert b7["decision"]["mode"] and "enforce" in b7 and b7["packet_ids"]


def test_refuses_without_valid_freeze(tmp_path):
    with pytest.raises(SystemExit):
        T.main(["--freeze-record", str(tmp_path / "none.json"), "--s-context", str(tmp_path / "x"),
                "--out", str(tmp_path / "o.jsonl")])
