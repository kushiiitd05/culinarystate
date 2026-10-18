#!/usr/bin/env python3
"""X4 crawl: public-domain English cookbooks from the Gutenberg catalog via the PGLAF mirror (2 s/request, cached).

  /opt/anaconda3/bin/python tools/crawl_gutenberg.py
Selection: catalog Subjects in a cookery list (Cooking, Cookbooks, Confectionery, Baking, Canning ...), not fiction /
Captain Cook. Writes data/raw/gutenberg/texts/<id>.txt and data/raw/gutenberg/manifest.csv.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.gutenberg import Fetcher  # noqa: E402

G = ROOT / "data" / "raw" / "gutenberg"
CAT = pd.read_csv(G / "pg_catalog.csv")
S = CAT.Subjects.fillna("")
PAT = (r"(?:^|; )(?:Cooking|Cookbooks|Cookery|Vegetarian cooking|Jewish cooking|Confectionery|Baking|Bread|"
       r"Canning and preserving|Desserts|Pastry|Soups|Salads|Sauces|Beverages|Ice cream)")
sel = CAT[(CAT.Language == "en") & (CAT.Type == "Text") & S.str.contains(PAT) & ~S.str.contains("Cook, James|Fiction")]
f = Fetcher(G / "texts")
rows = []
for r in sel.itertuples():
    got = f.book(int(r[1]))
    rows.append({"book_id": int(r[1]), "title": str(r.Title).replace("\r\n", " ").replace("\n", " "), "authors": r.Authors,
                 "subjects": r.Subjects, "issued": r.Issued, "ok": bool(got), "url": got[1] if got else None,
                 "chars": len(got[0]) if got else 0})
    if len(rows) % 25 == 0:
        print(len(rows), "books", sum(x["ok"] for x in rows), "ok", flush=True)
pd.DataFrame(rows).to_csv(G / "manifest.csv", index=False)
print("done", len(rows), "ok", sum(x["ok"] for x in rows))
