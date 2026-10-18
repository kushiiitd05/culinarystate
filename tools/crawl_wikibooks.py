#!/usr/bin/env python3
"""X3 crawl: Wikibooks Cookbook recipes + equipment + ingredient + technique pages (MediaWiki API, cached).

  /opt/anaconda3/bin/python tools/crawl_wikibooks.py
Writes data/interim/wikibooks/{recipes,equipment,ingredients,techniques}.jsonl (local; CC BY-SA attribution kept per page).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.wikibooks import WikiClient, parse_recipe, to_plain  # noqa: E402

CATS = {"recipes": ["Category:Recipes"], "equipment": ["Category:Cookbook equipment"],
        "ingredients": ["Category:Ingredients"], "techniques": ["Category:Cooking techniques"]}
OUT = ROOT / "data" / "interim" / "wikibooks"

TREES = {"cuisine": "Category:Recipes by origin", "technique": "Category:Recipes by preparation technique"}

cli = WikiClient(ROOT / "data" / "raw" / "wikibooks" / "api")
OUT.mkdir(parents=True, exist_ok=True)
tree = {}                                                  # category -> {"tree": cuisine|technique, "path": [...root]}
for name, root in TREES.items():
    frontier = [(root, [])]
    while frontier:
        cat, path = frontier.pop(0)
        for sub in cli.members(cat, ns=14):
            key = sub.removeprefix("Category:")
            if key not in tree and len(path) < 4:
                tree[key] = {"tree": name, "path": [cat.removeprefix("Category:")] + path}
                frontier.append((sub, tree[key]["path"]))
(OUT / "category_tree.json").write_text(json.dumps(tree, indent=1, ensure_ascii=False))
print("category tree:", {n: sum(v["tree"] == n for v in tree.values()) for n in TREES})
for kind, cats in CATS.items():
    titles = []
    for c in cats:
        titles += cli.members(c)
        if kind == "ingredients":                          # one level of subcategories (spices, herbs, ...)
            for sub in cli.members(c, ns=14):
                titles += cli.members(sub)
    titles = sorted(set(titles))
    pages = cli.pages(titles)
    with (OUT / f"{kind}.jsonl").open("w") as fh:
        for p in pages:
            if kind == "recipes":
                rec = parse_recipe(p)
            else:
                lead = p["content"].split("\n==")[0]
                rec = {"title": p["title"].removeprefix("Cookbook:"), "pageid": p["pageid"], "revid": p["revid"],
                       "categories": p["categories"], "lead": to_plain(lead).text[:1500],
                       "url": "https://en.wikibooks.org/wiki/" + p["title"].replace(" ", "_")}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{kind}: {len(titles)} titles -> {len(pages)} pages")
