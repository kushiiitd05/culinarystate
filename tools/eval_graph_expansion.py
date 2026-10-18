#!/usr/bin/env python3
"""R4 graph expansion evaluation: leave-cell-out interpolation of retention factors (SSOT §241.1 R4, §242.6).

  /opt/anaconda3/bin/python tools/eval_graph_expansion.py [--n 1500]
A cell = (ingredient, process, target) with MEASURED retention rows. Its rows are hidden; each system predicts the
cell median from what is left:
  B0  global median of the same (process, target) over all other foods (no food knowledge)
  RP  retriever, ING parents only (the pre-R4 retriever)
  RG  retriever + R4 food graph (parents, children, OFF siblings, OFF ancestors)
  RGN RG without SIBLING relations (vertical hierarchy only)
  RGU RGN + rows whose matrix is UNKNOWN (unlinked food), i.e. the pre-v0.2 packet "near" rule
Retriever prediction = median of top-k hits whose process and target MATCH and whose matrix is NEAR (measured).
Reports coverage, MAE (fraction scale) on each system's covered cells and on the common subset, paired bootstrap
of |error| differences, and MAE by graph relation. Silver dev analysis; no gold labels involved.
Writes reports/del4/graph_expansion_v1.md/json.
"""
import argparse
import json
import random
import statistics as stats
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.generation.claims import row_value  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.retrieval.compatibility import Query  # noqa: E402
from culinarystate.retrieval.food_graph import FoodGraph  # noqa: E402
from culinarystate.retrieval.retriever import EvidenceRetriever  # noqa: E402
from culinarystate.scoring.metrics import grouped_bootstrap  # noqa: E402
from culinarystate.vocab.off import parse as parse_off  # noqa: E402

OFF = ROOT / "data" / "raw" / "off" / "ingredients_a1ce1d36.txt"


def measured(e: dict) -> float | None:
    rf = (e.get("derived") or {}).get("retention_factor") or {}
    return row_value(e) if rf.get("status") == "MEASURED" else None


def predict(R, q: Query, text: str, hide: set, k: int = 30, unknown_ok: bool = False) -> tuple[float | None, dict]:
    vals, kinds = [], defaultdict(list)
    for h in R.search(text, q, k=k, exclude=hide):
        v, c = measured(h.row), h.compat
        ok_matrix = ("NEAR", "UNKNOWN") if unknown_ok else ("NEAR",)
        if v is None or c["vector"]["process"] != "MATCH" or c["vector"]["target"] != "MATCH" or \
                c["vector"]["matrix"] not in ok_matrix:
            continue
        vals.append(v)
        kinds[c["match"]["matrix"]].append(v)
    return (stats.median(vals) if vals else None), {kd: stats.median(v) for kd, v in kinds.items()}


def mae(errs: list[float]) -> float | None:
    return round(sum(errs) / len(errs), 4) if errs else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1500)
    a = ap.parse_args()
    st = LedgerStore()
    cond = {c["id"]: c for c in st.all_latest("COND")}
    family = {p["id"]: p["family"] for p in st.all_latest("PROC")}
    pname = {p["id"]: p["canonical_name"] for p in st.all_latest("PROC")}
    ings = [i for i in st.all_latest("ING") if i["status"] == "ACTIVE"]
    iname = {i["id"]: i["canonical_name"] for i in ings}
    parents = {i["id"]: frozenset(i.get("parent_ids") or ()) for i in ings}
    graph = FoodGraph(ings, {k: e.parents for k, e in parse_off(OFF).items()})
    R = EvidenceRetriever(st.all_latest("EVD"), cond, family)
    cells, glob = defaultdict(list), defaultdict(list)
    for idx, e in enumerate(R.evd):
        v, ing, pid = measured(e), e["matrix"].get("ingredient_id"), e["process"].get("process_id")
        if v is None or not pid:
            continue
        tgt = e["target"]["raw_name"].lower()
        glob[(pid, tgt)].append((v, ing))
        if ing:
            cells[(ing, pid, tgt)].append((idx, v))
    keys = sorted(cells)
    random.seed(7)
    keys = random.sample(keys, min(a.n, len(keys)))
    rows = []
    for ing, pid, tgt in keys:
        hide = {i for i, _ in cells[(ing, pid, tgt)]}
        truth = stats.median(v for _, v in cells[(ing, pid, tgt)])
        others = [v for v, i2 in glob[(pid, tgt)] if i2 != ing]
        text = f"{iname.get(ing, '')} {pname.get(pid, '')} {tgt}"
        base = dict(ingredient_id=ing, ingredient_name=iname.get(ing), ingredient_parents=parents.get(ing, frozenset()),
                    process_id=pid, process_family=family.get(pid), target=tgt)
        rp, _ = predict(R, Query(**base), text, hide)
        rel = tuple(graph.related(ing, siblings=True).items())
        rg, by_kind = predict(R, Query(**base, ingredient_relations=rel), text, hide)
        rgn, _ = predict(R, Query(**base, ingredient_relations=tuple(x for x in rel if x[1] != "SIBLING")), text, hide)
        rgu, _ = predict(R, Query(**base, ingredient_relations=tuple(x for x in rel if x[1] != "SIBLING")), text, hide,
                         unknown_ok=True)
        rows.append({"cell": [ing, pid, tgt], "truth": truth, "B0": stats.median(others) if others else None,
                     "RP": rp, "RG": rg, "RGN": rgn, "RGU": rgu, "by_kind": by_kind, "n_related": len(rel)})
    systems = ("B0", "RP", "RG", "RGN", "RGU")
    common = [r for r in rows if all(r[s] is not None for s in systems)]
    lines = [f"# R4 graph expansion — leave-cell-out retention interpolation v1 ({len(rows)} cells, seed 7)", "",
             "Prediction of a hidden (ingredient, process, target) cell median from the remaining evidence; "
             "fraction scale. Silver dev analysis.", "",
             "| system | coverage | MAE (own covered) | MAE (common subset, n=%d) |" % len(common), "|---|---|---|---|"]
    out = {"n_cells": len(rows), "n_common": len(common), "systems": {}}
    for s in systems:
        cov = [r for r in rows if r[s] is not None]
        m1, m2 = mae([abs(r[s] - r["truth"]) for r in cov]), mae([abs(r[s] - r["truth"]) for r in common])
        out["systems"][s] = {"coverage": round(len(cov) / len(rows), 4), "mae": m1, "mae_common": m2}
        lines.append(f"| {s} | {len(cov) / len(rows):.3f} | {m1} | {m2} |")
    lines += ["", "Paired |error| differences on the common subset (negative = first system better):", "",
              "| pair | Δ MAE [95% CI] |", "|---|---|"]
    for x, y in (("RG", "B0"), ("RGN", "B0"), ("RP", "B0"), ("RG", "RP"), ("RGN", "RG")):
        ci = grouped_bootstrap({i: [abs(r[x] - r["truth"]) - abs(r[y] - r["truth"])] for i, r in enumerate(common)},
                               lambda xs: sum(xs) / len(xs), n_boot=1000)
        out[f"{x}-{y}"] = ci
        lines.append(f"| {x} − {y} | {ci['estimate']:+.4f} [{ci['low']:+.4f}, {ci['high']:+.4f}] |")
    lines.append("")
    for s in ("RG", "RGN", "RGU"):
        g = [r for r in rows if r[s] is not None and r["RP"] is None and r["B0"] is not None]
        ci = grouped_bootstrap({i: [abs(r[s] - r["truth"]) - abs(r["B0"] - r["truth"])] for i, r in enumerate(g)},
                               lambda xs: sum(xs) / len(xs), n_boot=1000) if g else {"estimate": 0, "low": 0, "high": 0}
        out[f"new_{s}-B0"] = ci
        lines.append(f"Cells newly covered by {s} (RP had nothing, B0 available): {len(g)}; MAE {s} "
                     f"{mae([abs(r[s] - r['truth']) for r in g])} vs B0 {mae([abs(r['B0'] - r['truth']) for r in g])}; "
                     f"paired Δ {ci['estimate']:+.4f} [{ci['low']:+.4f}, {ci['high']:+.4f}].")
    lines += ["", "| relation | cells | MAE of that relation's median | B0 MAE on the same cells | paired Δ [95% CI] |",
              "|---|---|---|---|---|"]
    for kd in ("PARENT", "CHILD", "SIBLING", "ANCESTOR", "GROUP_ROW", "FOOD_GROUP"):
        rs = [r for r in rows if kd in r["by_kind"] and r["B0"] is not None]
        if rs:
            m_k, m_b = mae([abs(r["by_kind"][kd] - r["truth"]) for r in rs]), mae([abs(r["B0"] - r["truth"]) for r in rs])
            ci = grouped_bootstrap({i: [abs(r["by_kind"][kd] - r["truth"]) - abs(r["B0"] - r["truth"])]
                                    for i, r in enumerate(rs)}, lambda xs: sum(xs) / len(xs), n_boot=1000)
            lines.append(f"| {kd} | {len(rs)} | {m_k} | {m_b} | {ci['estimate']:+.4f} [{ci['low']:+.4f}, {ci['high']:+.4f}] |")
            out.setdefault("by_relation", {})[kd] = {"n": len(rs), "mae": m_k, "b0_mae": m_b, "delta": ci}
    rep = ROOT / "reports" / "del4"
    (rep / "graph_expansion_v1.json").write_text(json.dumps(out, indent=1))
    (rep / "graph_expansion_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
