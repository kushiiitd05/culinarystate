#!/usr/bin/env python3
"""X6: TOOL -> Wikidata QIDs (CC0). Exact English label/alias match, kept only if the item's superclass chain
(P279+ / P31) reaches a kitchen root (kitchenware, cookware, kitchen utensil, home/kitchen appliance, container).

  /opt/anaconda3/bin/python tools/build_tool_wikidata.py
Writes TOOL.external_refs WIKIDATA:Q…, registry/tools/tool_wikidata_v1.csv (all candidates + chosen), report.
"""
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import USER_AGENT  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

ENDPOINT = "https://query.wikidata.org/sparql"
ROOTS = "wd:Q1521410 wd:Q3773693 wd:Q154038 wd:Q212920 wd:Q1066288 wd:Q987767 wd:Q1357761 wd:Q39546"
# kitchenware, kitchen utensil, cookware, home appliance, kitchen appliance (approx), container, tool-ish, tool
CACHE = ROOT / "data" / "raw" / "wikidata" / "tool_lookup.json"


def query(labels: list[str]) -> list[dict]:
    vals = " ".join(json.dumps(x) + "@en" for x in labels)
    q = f"""SELECT DISTINCT ?item ?l ?itemLabel WHERE {{
      VALUES ?l {{ {vals} }} {{ ?item rdfs:label ?l }} UNION {{ ?item skos:altLabel ?l }}
      VALUES ?root {{ {ROOTS} }} ?item (wdt:P279|wdt:P31)/wdt:P279* ?root .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} }}"""
    for attempt in range(4):
        r = requests.get(ENDPOINT, params={"query": q}, headers={"User-Agent": USER_AGENT,
                                                                 "Accept": "application/sparql-results+json"}, timeout=90)
        if r.status_code == 200:
            return r.json()["results"]["bindings"]
        time.sleep(5 * (attempt + 1))
    r.raise_for_status()
    return []


def main() -> None:
    st = LedgerStore()
    tools = [t for t in st.all_latest("TOOL") if t["status"] == "ACTIVE"]
    surface = {t["canonical_name"]: [t["canonical_name"], *(t.get("aliases") or [])] for t in tools}
    if CACHE.exists():
        hits = json.loads(CACHE.read_text())
    else:
        labels = sorted({s for v in surface.values() for s in v})
        hits = []
        for i in range(0, len(labels), 40):
            hits += query(labels[i:i + 40])
            time.sleep(1.5)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(hits))
    by_label = defaultdict(set)
    for h in hits:
        by_label[h["l"]["value"].lower()].add((h["item"]["value"].rsplit("/", 1)[1], h["itemLabel"]["value"]))
    rows, writes = [], defaultdict(int)
    for t in tools:
        canon_hits = by_label.get(t["canonical_name"].lower(), set())
        alias_hits = set().union(*[by_label.get(a.lower(), set()) for a in surface[t["canonical_name"]][1:]] or [set()])
        cands = canon_hits or alias_hits
        chosen = sorted(cands, key=lambda x: (x[1].lower() != t["canonical_name"].lower(), int(x[0][1:])))[0] if cands else None
        label_ok = bool(chosen) and (bool(canon_hits) or chosen[1].lower() in {x.lower() for x in surface[t["canonical_name"]]})
        status = "LINKED" if chosen and len(cands) == 1 and label_ok else ("CANDIDATE" if chosen else "NO_MATCH")
        rows.append({"tool_id": t["id"], "tool": t["canonical_name"], "status": status,
                     "qid": chosen[0] if chosen else None, "wikidata_label": chosen[1] if chosen else None,
                     "candidates": " | ".join(f"{q}:{l}" for q, l in sorted(cands)), "human_decision": ""})
        refs = [r for r in (t.get("external_refs") or []) if not r.startswith("WIKIDATA:")]
        if status == "LINKED":
            refs.append(f"WIKIDATA:{chosen[0]}")
        writes[st.upsert({**t, "external_refs": sorted(refs)})[0]] += 1
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "registry" / "tools" / "tool_wikidata_v1.csv", index=False)
    vc = df.status.value_counts().to_dict()
    lines = ["# TOOL ↔ Wikidata v1 (X6, CC0)", "", f"- tools: {len(df)}; {vc}",
             "- LINKED = exactly one kitchen-rooted item for the canonical name (or its aliases); CANDIDATE = several "
             "(see CSV, human_decision); NO_MATCH = none under the kitchen roots.",
             "- unmatched: " + ", ".join(df[df.status == "NO_MATCH"].tool), f"- TOOL writes: {dict(writes)}"]
    (ROOT / "reports" / "tool_wikidata_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
