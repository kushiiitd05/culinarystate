"""S178 / T9-C09-R2: pure helpers of the D5 leakage audit, cross-checked against the tools they mirror."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.evaluation import leakage_audit_d5 as LA
from culinarystate.extraction import rung_a_measure as M

ROOT = Path(__file__).resolve().parents[2]


def test_rank_and_seeded_set_match_the_rung_a_sampler():
    ids = {f"REC-{i:06d}": ("WIKIBOOKS" if i % 3 else "FOODCOM") for i in range(500)}
    assert LA.rank("seed-x", "REC-000007") == M.rank("seed-x", "REC-000007")
    recs = [{"recipe_id": i, "source_family": f} for i, f in ids.items()]
    want = {r["recipe_id"] for r in M.seeded_sample(recs, "seed-x", 40)}
    assert LA.seeded_set(ids, "seed-x", 40) == want
    wb = {r["recipe_id"] for r in M.seeded_sample([r for r in recs if r["source_family"] == "WIKIBOOKS"], "seed-x", 40)}
    assert LA.seeded_set(ids, "seed-x", 40, ["WIKIBOOKS"]) == wb


def test_overlap_and_expectation():
    assert LA.overlap(["a", "b"], ["b", "c"]) == {"n_target": 2, "n_other": 2, "n_overlap": 1}
    assert LA.expected_random_overlap(40, 1000, 600_000) == pytest.approx(0.0667, abs=1e-4)
    assert LA.expected_random_overlap(40, 10, 0) == 0.0


def test_linker_bucket_matches_build_linker_data():
    src = (ROOT / "tools/build_linker_data.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "bucket")
    ns = {"hashlib": __import__("hashlib")}
    exec(compile(ast.Module([fn], []), "bucket", "exec"), ns)                       # noqa: S102 - the repo's own function
    norm = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "norm")
    ns2 = {"re": __import__("re"), "unicodedata": __import__("unicodedata")}
    exec(compile(ast.Module([norm], []), "norm", "exec"), ns2)                      # noqa: S102
    for k in (f"ING-{i:06d}" for i in range(0, 4000, 37)):
        assert LA.linker_bucket(k) == ns["bucket"](k)
        b = ns["bucket"](k)
        assert LA.linker_split(k) == ("test" if b >= 0.8 else "dev" if b >= 0.7 else "train")
    for s in ("Crème fraîche, 200 g!", "  Olive   oil ", "1 gallon (3.75 L) fresh apple cider", ""):
        assert LA.norm_line(s) == ns2["norm"](s)


def test_exact_line_matches():
    corpus = {LA.norm_line("2 cups flour, sifted")}
    r = LA.exact_line_matches(["2 CUPS flour sifted", "1 egg", ""], corpus)
    assert r == {"n_lines": 2, "n_exact_match": 1}


def _evd(i, matrix, proc, target, fam, rf=True):
    return {"id": f"EVD-{i:06d}", "status": "ACTIVE", "source_family_id": fam,
            "matrix": {"raw_name": matrix}, "process": {"process_id": proc}, "target": {"raw_name": target},
            "derived": {"retention_factor": {"status": "MEASURED", "value": 0.5}} if rf else {}}


class FakeStore:
    rows: list = []

    def all_latest(self, name):
        if name == "EVD":
            return self.rows
        if name == "PROC":
            return [{"id": "PROC-1", "canonical_name": "boil"}, {"id": "PROC-2", "canonical_name": "fry"}]
        return []


def test_silver_queries_match_export_retrieval_set(tmp_path):
    rows = []
    n = 0
    for fam in ("A", "B", "C"):
        for m in range(12):
            for p in ("PROC-1", "PROC-2"):
                for _ in range(2 + m % 2):
                    n += 1
                    rows.append(_evd(n, f"Food{m}", p, "Vitamin C", fam))
    rows.append(_evd(999, "Lonely", "PROC-1", "Iron", "A"))                          # single-row cell: never a query
    rows.append(_evd(1000, "NoProc", "", "Iron", "A"))                               # no process id: not a cell
    spec = importlib.util.spec_from_file_location("_erss", ROOT / "tools/export_retrieval_set.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    FakeStore.rows = rows
    mod.LedgerStore, mod.OUT, mod.MAX_CELLS = FakeStore, tmp_path, 30
    mod.main()
    tool = [json.loads(x) for x in (tmp_path / "silver_queries.jsonl").read_text().splitlines()]
    mine = LA.silver_queries(rows, seed=mod.SEED, max_cells=30)
    assert len(tool) == len(mine) == 30
    assert [(q["matrix"], q["process_id"], q["target"]) for q in tool] == [x["cell"] for x in mine]
    assert [q["family"] for q in tool] == [x["family"] for x in mine]
    assert [q["relevant"] for q in tool] == [x["relevant"] for x in mine]
    assert LA.evd_cell(rows[0]) == ("food0", "PROC-1", "vitamin c")
