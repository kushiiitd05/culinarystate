#!/usr/bin/env python3
"""CulinaryState-specific layer (proposed, not promoted): EVIDENCE-KEY EXTRACTION baseline. Local only; reads the Food.com v1.1 joint Gold (recipe text stays local), writes counts only.

  /opt/anaconda3/bin/python tools/evidence_key_baseline.py
Question: from RAW recipe text, with the CURRENT rule stack (LineLinker for ingredients, step_processes for processes) and no gold events, how many of the (ING x PROC) cells that the
Gold marks as evidence-supported can be recovered? Extraction: ingredient lines -> ING ids; for each step, ING mentions in the step text x processes detected in that step, kept only when the
EVD ledger holds a retention cell for (ING, PROC). Target = recipe-evidence pairs from tools/hstate_coverage_foodcom.py (Gold lineage). Misses are attributed:
ING_NEVER_MENTIONED / PROC_NEVER_DETECTED / NO_COOCCURRENCE (both present but never in the same step = implicit reference / coreference / state carry-over)."""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.state_graph.rule_compiler import step_processes  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402
from culinarystate.vocab.line_link import LineLinker  # noqa: E402
import hstate_coverage_foodcom as H  # noqa: E402


def main():
    st = LedgerStore()
    ing = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    proc = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC") if p["status"] == "ACTIVE"}
    names = dict(ing)
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en" and a["alias_type"] != "AMBIGUOUS":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    linker = LineLinker(names, set())
    cells = defaultdict(list)
    for e in st.all_latest("EVD"):
        i, p = e["matrix"].get("ingredient_id"), e["process"].get("process_id")
        if e["status"] == "ACTIVE" and (e.get("derived") or {}).get("retention_factor") and i and p:
            cells[(i, p)].append(e["id"])
    docs = H.load_docs("foodcom_ai_assisted_v1_1")
    gold, _ = H.pairs_for(docs, ing, proc, cells)
    extracted, seen_ing, seen_proc, cooc = set(), defaultdict(set), defaultdict(set), defaultdict(set)
    for d in docs:
        rid = d["recipe_id"]
        line_ing = {linker.link(l["text"])[0] for l in d["ingredient_lines"] if not l.get("notes", "").startswith("STEP_ONLY")} - {None}
        for s in d["steps"]:
            mi = set(linker.mentions(s["text"]))
            pr = {proc.get(p) for _, p in step_processes(s["text"])} - {None}
            seen_ing[rid] |= mi
            seen_proc[rid] |= pr
            for i in mi:
                for p in pr:
                    cooc[rid].add((i, p))
                    if cells.get((i, p)):
                        extracted.add((rid, i, p))
    hit = gold & extracted
    miss = Counter()
    for rid, i, p in gold - extracted:
        miss["ING_NEVER_MENTIONED" if i not in seen_ing[rid] else "PROC_NEVER_DETECTED" if p not in seen_proc[rid] else "NO_COOCCURRENCE"] += 1
    out = {"gold_supported_pairs": len(gold), "extracted_evidence_bearing_cells": len(extracted), "recovered": len(hit),
           "recall": round(len(hit) / max(len(gold), 1), 3), "precision_vs_gold_lineage": round(len(hit) / max(len(extracted), 1), 3),
           "miss_attribution": dict(miss), "note": "precision here is vs Gold *lineage* pairs only; an extracted cell absent from Gold may still be textually valid, so precision is a LOWER bound",
           "recipes": len(docs)}
    (ROOT / "reports/ner/evidence_key_baseline.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
