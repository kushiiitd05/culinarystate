#!/usr/bin/env python3
"""X3 ingest: Wikibooks Cookbook -> REC (source family 2), REC<->ING links, new ING concepts + aliases from
editor-linked ingredient pages, silver NER spans (local), cross-source near-duplicate check (D-009).

  /opt/anaconda3/bin/python tools/crawl_wikibooks.py && /opt/anaconda3/bin/python tools/ingest_wikibooks.py
Committed outputs hold IDs/counts only; CC BY-SA text stays in data/interim (attribution: page URL + revid).
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import sha256_file  # noqa: E402
from culinarystate.ingest.recipe_families import families  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402
from culinarystate.vocab.line_link import LineLinker  # noqa: E402

WB = ROOT / "data" / "interim" / "wikibooks"
A1 = ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "recipes_processed.jsonl"
CB, MIN_RECIPES = "Kush+Claude", 3
GENERIC_PAGES = {"sweeteners", "spirits", "juice", "dough", "zest", "cookie", "breakfast cereal", "liquid seasoning",
                 "dehydrated broth", "food coloring", "nondairy milk"}   # category-like pages, not concepts
load = lambda p: [json.loads(x) for x in (WB / p).open()]  # noqa: E731


def source(st: LedgerStore) -> str:
    sid = st.ids.mint("SRC", key="wikibooks:cookbook")
    st.upsert({"id": sid, "record_type": "SRC", "status": "ACTIVE", "created_by": CB,
               "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
               "kind": "WEBSITE", "title": "Wikibooks Cookbook (en.wikibooks.org, Cookbook namespace) via MediaWiki API",
               "url": "https://en.wikibooks.org/wiki/Cookbook:Table_of_Contents", "publisher": "Wikimedia Foundation",
               "licence": "CC BY-SA 4.0 (attribute page + revision; share-alike)", "licence_status": "VERIFIED",
               "storage_rule": "LOCAL_ONLY", "primary_or_secondary": "PRIMARY", "source_family_id": "WIKIBOOKS-COOKBOOK",
               "robots_terms_notes": "official API, 1 req/s, batches of 50 (D-009)"})
    snap = WB / "recipes.jsonl"
    sha = sha256_file(snap)
    st.upsert({"id": st.ids.mint("SNAP", key=f"sha256:{sha}"), "record_type": "SNAP", "status": "ACTIVE",
               "created_by": CB, "provenance": {"method": "SCRAPE", "source_ids": [sid]},
               "verification": {"status": "UNVERIFIED"}, "source_id": sid, "retrieved_at": "2026-10-18T13:10:00+05:30",
               "retrieval_url": "https://en.wikibooks.org/w/api.php", "sha256": sha, "bytes": snap.stat().st_size,
               "local_path": str(snap.relative_to(ROOT)), "http_status": 200, "source_version": "revids per page"})
    return sid


def names_map(st: LedgerStore) -> dict[str, str]:
    names = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en" and a["alias_type"] != "AMBIGUOUS":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    return names


def new_concepts(st: LedgerStore, sid: str, recipes: list, ing_pages: set, names: dict) -> tuple[Counter, Counter]:
    """Ingredient pages linked from ≥ MIN_RECIPES recipes -> ING (if new) + ALIAS for shown surfaces."""
    by_target, surfaces = defaultdict(set), defaultdict(Counter)
    for r in recipes:
        for ln in r["ingredients"]:
            for a, b, t in ln["links"]:
                if t in ing_pages:
                    by_target[t].add(r["pageid"])
                    surfaces[t][ln["text"][a:b].strip().lower()] += 1
    w_ing, w_al = Counter(), Counter()
    for t, recs in sorted(by_target.items()):
        if len(recs) < MIN_RECIPES or " and " in t.lower() or t.lower() in GENERIC_PAGES:
            continue
        key = norm(t)
        if key not in names:
            canon = t.lower()
            iid = st.ids.mint("ING", key=f"name:{canon}")
            w_ing[st.upsert({"id": iid, "record_type": "ING", "status": "ACTIVE", "created_by": CB,
                             "provenance": {"method": "IMPORT", "source_ids": [sid], "agent": "wikibooks_links@0.1",
                                            "locator": f"Cookbook:{t} (ingredient page linked from {len(recs)} recipes)"},
                             "verification": {"status": "UNVERIFIED"}, "canonical_name": canon,
                             "scientific_identity_status": "UNKNOWN", "parent_ids": [], "facets": {},
                             "corpus_frequency": None, "ambiguity": "MEDIUM",
                             "crosswalks": {k: {"status": "UNRESOLVED_EXTERNAL"} for k in
                                            ("foodon", "fdc", "flavordb", "recipedb")},
                             "external_refs": [f"WIKIBOOKS:Cookbook:{t}"],
                             "notes": f"from Wikibooks ingredient page; {len(recs)} Wikibooks recipes"})[0]] += 1
            names[key] = iid
        iid = names[key]
        for surf, n in surfaces[t].items():
            k = norm(surf)
            if n < 2 or not k or k in names:
                continue
            w_al[st.upsert({"id": st.ids.mint("ALIAS", key=f"wb:en:{k}"), "record_type": "ALIAS", "status": "ACTIVE",
                            "created_by": CB, "provenance": {"method": "IMPORT", "source_ids": [sid],
                                                             "agent": "wikibooks_links@0.1",
                                                             "locator": f"link text -> Cookbook:{t}"},
                            "verification": {"status": "UNVERIFIED"}, "surface": surf, "normalized": k,
                            "ingredient_id": iid, "candidate_ingredient_ids": [iid], "language": "en",
                            "region": None, "alias_type": "SYNONYM", "link_band": "HIGH", "corpus_frequency": n})[0]] += 1
            names[k] = iid
    return w_ing, w_al


def main() -> None:
    st = LedgerStore()
    sid = source(st)
    recipes = [r for r in load("recipes.jsonl") if r["ingredients"] and r["steps"]]
    tree = json.loads((WB / "category_tree.json").read_text())
    pages = {k: {p["title"] for p in load(f"{k}.jsonl")} for k in ("ingredients", "equipment", "techniques")}
    names = names_map(st)
    w_ing, w_al = new_concepts(st, sid, recipes, pages["ingredients"], names)
    units = {u["canonical_name"] for u in st.all_latest("UNIT")} | {a for u in st.all_latest("UNIT")
                                                                      for a in (u.get("aliases") or [])}
    linker = LineLinker(names, units)

    docs = {f"WB{r['pageid']}": " ".join(s["text"] for s in r["steps"]) for r in recipes}
    fam, _ = families(docs)
    a1_docs = {f"A1{x['recipe_id']}": " ".join(x.get("instruction_steps_raw") or []) for x in map(json.loads, A1.open())}
    _, cross = families({**docs, **a1_docs})
    cross = [(a, b, j) for a, b, j in cross if a[:2] != b[:2]]

    w_rec, links, ner, methods, cuisines, techs = Counter(), [], [], Counter(), Counter(), Counter()
    for r in recipes:
        cats = [c for c in r["categories"] if c in tree]
        cu = sorted(c.removesuffix(" recipes") for c in cats if tree[c]["tree"] == "cuisine")
        te = sorted(c.removesuffix(" recipes") for c in cats if tree[c]["tree"] == "technique")
        cuisines.update(cu)
        techs.update(te)
        content = json.dumps({"title": r["title"], "ingredients": [i["text"] for i in r["ingredients"]],
                              "steps": [s["text"] for s in r["steps"]]}, ensure_ascii=False, sort_keys=True)
        rid = st.ids.mint("REC", key=f"wikibooks:{r['pageid']}")
        w_rec[st.upsert({"id": rid, "record_type": "REC", "status": "ACTIVE", "created_by": CB,
                         "provenance": {"method": "SCRAPE", "source_ids": [sid], "agent": "wikibooks_api@0.1",
                                        "locator": f"{r['url']} (revid {r['revid']})"},
                         "verification": {"status": "UNVERIFIED"}, "title": r["title"], "source_url": r["url"],
                         "content_sha256": hashlib.sha256(content.encode()).hexdigest(),
                         "family_id": fam[f"WB{r['pageid']}"], "cuisine": "|".join(cu) or None,
                         "n_ingredient_lines": len(r["ingredients"]), "n_steps": len(r["steps"]),
                         "raw_location": f"data/interim/wikibooks/recipes.jsonl#pageid={r['pageid']}",
                         "external_refs": [f"WIKIBOOKS:{r['pageid']}:{r['revid']}"] + [f"TECHNIQUE:{t}" for t in te],
                         "notes": None})[0]] += 1
        for i, ln in enumerate(r["ingredients"]):
            iid, how = linker.link(ln["text"], ln["links"])
            methods[how] += 1
            links.append({"rec_id": rid, "line": i, "group": ln["group"], "ing_id": iid, "method": how})
        for kind, rows in (("ingredient_line", r["ingredients"]), ("step", r["steps"])):
            for ln in rows:
                spans = [{"start": a, "end": b, "target": t,
                          "label": "INGREDIENT" if t in pages["ingredients"] else "TOOL" if t in pages["equipment"]
                          else "PROCESS" if t in pages["techniques"] else "UNIT" if norm(t) in linker.unit_words
                          else "OTHER"} for a, b, t in ln["links"]]
                ner.append({"rec_id": rid, "kind": kind, "text": ln["text"], "spans": spans})
    out = ROOT / "registry" / "recipes"
    ldf = pd.DataFrame(links)
    ldf.to_csv(out / "wikibooks_ingredient_links_v1.csv", index=False)
    with (WB / "ner_silver.jsonl").open("w") as fh:
        for x in ner:
            fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    span_labels = Counter(s["label"] for x in ner for s in x["spans"])
    lines = ["# Wikibooks Cookbook ingest v1 (X3, D-009)", "",
             f"- recipes with ingredients+steps: {len(recipes):,} (REC writes {dict(w_rec)}); "
             f"ingredient lines {len(ldf):,}; steps {sum(len(r['steps']) for r in recipes):,}",
             f"- REC↔ING linked lines: {ldf.ing_id.notna().mean():.1%} ({dict(methods)})",
             f"- new ING concepts from editor-linked ingredient pages (≥{MIN_RECIPES} recipes): {dict(w_ing)}; "
             f"new aliases from link text: {dict(w_al)}",
             f"- near-duplicate families within Wikibooks: {len(docs) - len(set(fam.values())):,} recipes merged; "
             f"cross-source near-duplicates with BBC A1 (Jaccard ≥ 0.8): {len(cross)}",
             f"- silver NER spans (local, data/interim/wikibooks/ner_silver.jsonl): {dict(span_labels)}",
             f"- top cuisines: " + ", ".join(f"{k} {v}" for k, v in cuisines.most_common(15)),
             f"- technique labels: " + ", ".join(f"{k} {v}" for k, v in techs.most_common(15)),
             "- licence CC BY-SA 4.0: text stays local; ledgers carry URL + revid for attribution."]
    (ROOT / "reports" / "wikibooks_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[2:]))


if __name__ == "__main__":
    main()
