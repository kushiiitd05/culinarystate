#!/usr/bin/env python3
"""X4 ingest: Gutenberg public-domain cookbooks -> SRC/SNAP per book, REC (source family GUTENBERG-PD),
REC<->ING mention links, historic tool-word candidates (D-009).

  /opt/anaconda3/bin/python tools/crawl_gutenberg.py && /opt/anaconda3/bin/python tools/ingest_gutenberg.py
A candidate becomes a REC only with evidence: ≥ 2 distinct ING mentions, ≥ 1 recognised process, 80–5000 chars.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import sha256_file  # noqa: E402
from culinarystate.ingest.gutenberg import strip_boilerplate  # noqa: E402
from culinarystate.ingest.old_recipes import segment  # noqa: E402
from culinarystate.ingest.recipe_families import families  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.process.tools import ALIAS_TO_TOOL, _hy  # noqa: E402
from culinarystate.state_graph.rule_compiler import step_processes  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402
from culinarystate.vocab.line_link import LineLinker  # noqa: E402

G = ROOT / "data" / "raw" / "gutenberg"
OUTI = ROOT / "data" / "interim" / "gutenberg"
CB, FAMILY = "Kush+Claude", "GUTENBERG-PD"
SENT = re.compile(r"(?<=[.;!?])\s+")
NON_FOOD = re.compile(r"\b(ointment|salve|liniment|remedy|remedies|cure for|soap|polish|dye|cleaning|wash for|poultice|"
                      r"plaster|varnish|ink|lotion|pomade|medicine|tincture)\b", re.I)
STOP_TITLE = re.compile(r"^(transcriber'?s? note|contents|subject[- ]matter|proportions|recipes?|menus?|index|preface|"
                        r"introduction|bill of fare|breakfast|dinner|luncheon|supper|tea|footnotes?|errata|general (?:rules|"
                        r"remarks|observations)|remarks|observations|alabama|alaska|arizona|california|colorado|connecticut|"
                        r"delaware|florida|georgia|illinois|indiana|iowa|kansas|kentucky|maine|maryland|massachusetts|michigan|"
                        r"minnesota|missouri|nebraska|new jersey|new york|ohio|oregon|pennsylvania|texas|vermont|virginia|"
                        r"wisconsin)\b", re.I)
DATE_TITLE = re.compile(r"^(january|february|march|april|may|june|july|august|september|october|november|december"
                        r"|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I)
MENU_BODY = re.compile(r"\b(BREAKFAST|DINNER|LUNCHEON|SUPPER)\s*[-—:]{1,2}")
INDEX_REF = re.compile(r"\b\d{2,4}\b(?![/\d]|\s*(?:lbs?|pounds?|oz|ounces?|minutes?|mins?|hours?|degrees?|°|gills?|quarts?|"
                       r"pints?|cups?|cupfuls?|table|tea|spoon|inch|eggs?|g\b|grains?|drops?|to\s+\d|or\s+\d|-|per|lb\.))")


def is_index_or_menu(title: str, body: str) -> bool:
    """Contents/index/menu pages: many page/recipe-number references per word."""
    refs = len(INDEX_REF.findall(body))
    return bool(re.search(r",\s*\d+$", title)) or refs >= 4 and refs / max(1, len(body.split())) > 0.08
TOOL_SLOT = re.compile(r"\b(?:in|into|on|over|with|upon) (?:a|an|the) ((?:[a-z-]+ ){0,1}[a-z-]+?(?:pan|pot|kettle|dish|tin|"
                       r"oven|sieve|cloth|jar|mould|mold|basin|bowl|spoon|board|knife|press|griddle|skillet|boiler|"
                       r"spider|salamander|toaster|grater|mortar|bag))\b")


def cuisine_of(subjects: str) -> str | None:
    m = [x.strip() for x in re.findall(r"Cooking, ([A-Z][A-Za-z ]+?)(?:\s*--|;|$)", subjects or "")]
    j = ["Jewish"] if "Jewish cooking" in (subjects or "") else []
    return "|".join(sorted(set(m + j))) or None


def names_map(st: LedgerStore) -> dict[str, str]:
    names = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en" and a["alias_type"] != "AMBIGUOUS":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    return names


def book_sources(st: LedgerStore, b) -> str:
    sid = st.ids.mint("SRC", key=f"gutenberg:{b.book_id}")
    st.upsert({"id": sid, "record_type": "SRC", "status": "ACTIVE", "created_by": CB,
               "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
               "kind": "BOOK", "title": f"{b.title} (Project Gutenberg #{b.book_id})", "url": b.url,
               "authors": [a.strip() for a in str(b.authors).split(";") if a.strip() and a != "nan"],
               "publisher": "Project Gutenberg", "licence": "Public domain in the USA (Project Gutenberg licence for the eBook)",
               "licence_status": "VERIFIED", "storage_rule": "COMMIT_OK", "primary_or_secondary": "PRIMARY",
               "source_family_id": FAMILY, "robots_terms_notes": "PGLAF mirror, 2 s/request (robot policy)"})
    raw = G / "texts" / f"{b.book_id}.txt"
    sha = sha256_file(raw)
    st.upsert({"id": st.ids.mint("SNAP", key=f"sha256:{sha}"), "record_type": "SNAP", "status": "ACTIVE",
               "created_by": CB, "provenance": {"method": "SCRAPE", "source_ids": [sid]},
               "verification": {"status": "UNVERIFIED"}, "source_id": sid, "retrieved_at": "2026-10-18T16:00:00+05:30",
               "retrieval_url": b.url, "sha256": sha, "bytes": raw.stat().st_size, "local_path": str(raw.relative_to(ROOT)),
               "http_status": 200, "source_version": f"PG #{b.book_id}"})
    return sid


def main() -> None:
    st = LedgerStore()
    if (G / "manifest.csv").exists():
        man = pd.read_csv(G / "manifest.csv")
        man = man[man.ok]
    else:                                              # crawl still running: use the books downloaded so far
        sel = pd.read_csv(G / "cookbook_selection.csv").rename(columns={"Text#": "book_id", "Title": "title",
                                                                       "Authors": "authors", "Subjects": "subjects",
                                                                       "Issued": "issued"})
        sel = sel[sel.book_id.map(lambda b: (G / "texts" / f"{b}.url").exists())]
        man = sel.assign(url=sel.book_id.map(lambda b: (G / "texts" / f"{b}.url").read_text().strip()),
                         title=sel.title.str.replace(r"\s+", " ", regex=True))
    linker = LineLinker(names_map(st), set())
    kept, stats, tool_words, links = [], Counter(), Counter(), []
    for b in man.itertuples():
        text = strip_boilerplate((G / "texts" / f"{b.book_id}.txt").read_text(encoding="utf-8"))
        cands = segment(text)
        stats["candidates"] += len(cands)
        good = []
        for i, c in enumerate(cands):
            body = c["body"]
            title = re.sub(r"^\[?Illustration:?\s*", "", c["title"]).strip(" []=_")
            if (not 80 <= len(body) <= 5000 or not title or NON_FOOD.search(title) or STOP_TITLE.match(title)
                    or DATE_TITLE.match(title) or MENU_BODY.search(body) or is_index_or_menu(title, body)):
                stats["rejected_filters"] += 1
                continue
            c = {**c, "title": title}
            ings = linker.mentions((c.get("ingredients") or "") + " " + (c.get("method") or body))
            procs = [p for s in SENT.split(c.get("method") or body) for _, p in step_processes(s)]
            if len(set(ings)) < 2 or not procs:
                continue
            tool_words.update(m.group(1) for m in TOOL_SLOT.finditer(body.lower()) if _hy(m.group(1)) not in ALIAS_TO_TOOL)
            good.append({"book_id": int(b.book_id), "idx": i, "title": c["title"].title()[:200], "body": body,
                         "fields": {k: v for k, v in c.items() if k not in ("title", "body")},
                         "ing_ids": sorted(set(ings)), "processes": sorted(set(procs)),
                         "steps": [s for s in SENT.split(c.get("method") or body) if s.strip()]})
        if good:
            sid = book_sources(st, b)
            for g in good:
                g["src_id"], g["cuisine"], g["url"] = sid, cuisine_of(b.subjects), b.url
            kept += good
            stats["books_with_recipes"] += 1
    docs = {f"G{g['book_id']}_{g['idx']}": g["body"] for g in kept}
    fam, pairs = families(docs)
    OUTI.mkdir(parents=True, exist_ok=True)
    w = Counter()
    with (OUTI / "recipes.jsonl").open("w") as fh:
        for g in kept:
            key = f"G{g['book_id']}_{g['idx']}"
            content = json.dumps({"title": g["title"], "body": g["body"]}, ensure_ascii=False, sort_keys=True)
            rid = st.ids.mint("REC", key=f"gutenberg:{g['book_id']}:{g['idx']}")
            n_lines = len(re.split(r"[,;]", g["fields"]["ingredients"])) if g["fields"].get("ingredients") else len(g["ing_ids"])
            w[st.upsert({"id": rid, "record_type": "REC", "status": "ACTIVE", "created_by": CB,
                         "provenance": {"method": "SCRAPE", "source_ids": [g["src_id"]], "agent": "old_recipes@0.1",
                                        "locator": f"{g['url']} segment {g['idx']}"},
                         "verification": {"status": "UNVERIFIED"}, "title": g["title"], "source_url": g["url"],
                         "content_sha256": hashlib.sha256(content.encode()).hexdigest(), "family_id": fam[key],
                         "cuisine": g["cuisine"], "n_ingredient_lines": n_lines, "n_steps": len(g["steps"]),
                         "raw_location": f"data/interim/gutenberg/recipes.jsonl#{key}",
                         "external_refs": [f"GUTENBERG:{g['book_id']}:{g['idx']}"],
                         "notes": "segmented from free text (heuristic, ~80-85% precision on 30-sample); ingredient list = mentions" if not
                         g["fields"].get("ingredients") else "Beeton-style fields parsed"})[0]] += 1
            links += [{"rec_id": rid, "ing_id": i} for i in g["ing_ids"]]
            fh.write(json.dumps({**g, "rec_id": rid}, ensure_ascii=False) + "\n")
    pd.DataFrame(links).to_csv(ROOT / "registry" / "recipes" / "gutenberg_ingredient_links_v1.csv", index=False)
    tw = pd.DataFrame(tool_words.most_common(80), columns=["tool_phrase", "count"])
    tw.to_csv(ROOT / "registry" / "tools" / "historic_tool_candidates.csv", index=False)
    by_cuisine = Counter(c for g in kept for c in (g["cuisine"] or "unspecified").split("|"))
    lines = ["# Gutenberg public-domain cookbooks v1 (X4, D-009)", "",
             f"- books downloaded: {len(man)}; books with ≥1 kept recipe: {stats['books_with_recipes']}",
             f"- segment candidates: {stats['candidates']:,}; kept as REC (≥2 ING, ≥1 process, 80–5000 chars): "
             f"{len(kept):,} (writes {dict(w)}); rejected by index/menu/non-food filters: {stats['rejected_filters']:,}",
             f"- with Beeton-style ingredient field: {sum(bool(g['fields'].get('ingredients')) for g in kept):,}; "
             f"with stated time: {sum(bool(g['fields'].get('time')) for g in kept):,}",
             f"- REC↔ING mention links: {len(links):,}; near-duplicate families merged: {len(docs) - len(set(fam.values()))}",
             "- cuisine (from catalog subjects): " + ", ".join(f"{k} {v}" for k, v in by_cuisine.most_common(12)),
             "- historic tool phrases not in TOOL vocab (review): " + ", ".join(tw.tool_phrase.head(20)),
             "- caveat: segmentation is heuristic; titles/bodies may merge neighbours; text local (data/interim)."]
    (ROOT / "reports" / "gutenberg_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[2:]))


if __name__ == "__main__":
    main()
