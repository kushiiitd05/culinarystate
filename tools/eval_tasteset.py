#!/usr/bin/env python3
"""X10: TASTEset (MIT, 700 recipes' ingredient lists, 9 entity types) as an external NER benchmark.
Scores the rule baseline (src/culinarystate/ner/rule_ner.py), exact + relaxed span F1 per label.

  /opt/anaconda3/bin/python tools/eval_tasteset.py
Writes reports/ner/tasteset_rule_baseline.md/json. The encoder NER (X8, A100) must beat this floor.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.ner.rule_ner import tag_text  # noqa: E402
from culinarystate.scoring.metrics import corpus_span_scores  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

COMMIT = "80bb783f521023db9193a90202fa9339afc8f678"
d = pd.read_csv(ROOT / "data" / "raw" / "tasteset" / "TASTEset.csv")
st = LedgerStore()
names = {norm(i["canonical_name"]) for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
names |= {norm(a["normalized"]) for a in st.all_latest("ALIAS") if a["status"] == "ACTIVE" and a["language"] == "en"}
docs = []
for r in d.itertuples():
    gold = [(e["start"], e["end"], e["type"]) for e in json.loads(r.ingredients_entities)]
    docs.append((gold, tag_text(r.ingredients, lambda t: norm(t) in names)))
res = {m: corpus_span_scores(docs, mode=m) for m in ("exact", "relaxed")}
out = ROOT / "reports" / "ner"
out.mkdir(parents=True, exist_ok=True)
(out / "tasteset_rule_baseline.json").write_text(json.dumps(res, indent=1, default=str))
labels = sorted({lab for g, _ in docs for *_, lab in g})
lines = [f"# TASTEset — rule baseline (X10)", "", f"TASTEset @ {COMMIT[:12]} (MIT): {len(d)} recipes, "
         f"{sum(len(g) for g, _ in docs):,} gold spans. Rule NER = quantity grammar + closed vocabularies + ING lexicon.",
         "", "| label | exact P | exact R | exact F1 | relaxed F1 |", "|---|---|---|---|---|"]
for lab in labels + ["micro"]:
    e = res["exact"]["micro"] if lab == "micro" else res["exact"]["per_label"].get(lab, {})
    x = res["relaxed"]["micro"] if lab == "micro" else res["relaxed"]["per_label"].get(lab, {})
    lines.append(f"| {lab} | {e.get('precision')} | {e.get('recall')} | {e.get('f1')} | {x.get('f1')} |")
lines.append(f"| macro F1 | | | {res['exact']['macro_f1']} | {res['relaxed']['macro_f1']} |")
(out / "tasteset_rule_baseline.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
