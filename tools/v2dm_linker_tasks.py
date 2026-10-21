#!/usr/bin/env python3
"""V2-DM Track C (linker verification) tasks from the frozen BGE v2 tables: mention + top-5 ledger candidates (+ NONE). Sets: dev_alias (n=61), unseen_alias (96, report only), dev NIL (252, gold NONE), unseen_concept NIL (543, report only).
Ledger names/aliases are project vocabulary (no benchmark recipe text). -> features/v2dm/linker_tasks.jsonl"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from collections import defaultdict  # noqa: E402

from culinarystate.ledgers.store import LedgerStore  # noqa: E402

st = LedgerStore()
name, alias = {}, defaultdict(list)
for i in st.all_latest("ING"):
    if i["status"] == "ACTIVE":
        name[i["id"]] = i["canonical_name"]
for a in st.all_latest("ALIAS"):
    if a["status"] == "ACTIVE" and a.get("ingredient_id") in name:
        alias[a["ingredient_id"]].append(a["normalized"])
t = json.load(open(ROOT / "reports/ner/_raw_v2/linker__bge-large-en-v1.5_v2final__seed1.tables.json"))
D = json.load(open(ROOT / "features/linker_data_v2.json"))
rows = []
for part in ("dev_alias", "unseen_alias", "dev", "unseen_concept"):
    qs = D["queries"][part]
    for k, (q, r) in enumerate(zip(qs, t[part])):
        cands = [{"id": c, "score": round(s, 4), "name": name.get(c, c), "aliases": [a for a in alias[c] if a != name.get(c)][:3]} for c, s in r["top"]]
        rows.append({"id": f"{part}-{k}", "set": part, "mention": q["s"], "gold": q["gold"], "cands": cands})
(ROOT / "features/v2dm").mkdir(exist_ok=True)
open(ROOT / "features/v2dm/linker_tasks.jsonl", "w").write("\n".join(json.dumps(r) for r in rows) + "\n")
print(len(rows), {p: sum(1 for r in rows if r["set"] == p) for p in ("dev_alias", "unseen_alias", "dev", "unseen_concept")})
