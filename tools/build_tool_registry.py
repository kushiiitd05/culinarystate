#!/usr/bin/env python3
"""TOOL- ledger v1 + process↔tool links from corpus co-occurrence (sentence level, lift ≥ 2, count ≥ 20).

  /opt/anaconda3/bin/python tools/build_tool_registry.py
Outputs: ledgers/data/TOOL.jsonl, PROC revisions (tool_ids), registry/tools/*.csv, reports/tool_registry_v1.md
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.process.tools import TOOLS, WIKIBOOKS_PAGE, find_tools  # noqa: E402
from culinarystate.state_graph.rule_compiler import step_processes  # noqa: E402

MIN_COUNT, MIN_LIFT = 20, 2.0
steps = []
with (ROOT.parent / "a1" / "A1 3" / "data" / "raw" / "recipes_raw.jsonl").open() as fh:
    for line in fh:
        steps += json.loads(line).get("instruction_steps_raw") or []
n_bbc = len(steps)
WB = ROOT / "data" / "interim" / "wikibooks" / "recipes.jsonl"          # X3 corpus (local, CC BY-SA)
if WB.exists():
    steps += [s["text"] for line in WB.open() for s in json.loads(line)["steps"]]
sents = [s for st in steps for s in re.split(r"(?<=[.!?])\s+", st) if s.strip()]

tool_freq, proc_freq, pair, mat = Counter(), Counter(), Counter(), Counter()
steps_with_tool = 0
for st in steps:
    steps_with_tool += bool(find_tools(st))
for s in sents:
    tools = {t for _, t, _ in find_tools(s)}
    for _, t, m in find_tools(s):
        if m:
            mat[(t, m)] += 1
    procs = {p for _, p in step_processes(s)}
    tool_freq.update(tools)
    proc_freq.update(procs)
    pair.update((p, t) for p in procs for t in tools)
N = len(sents)
links = []
for (p, t), c in pair.items():
    lift = (c / N) / ((proc_freq[p] / N) * (tool_freq[t] / N))
    if c >= MIN_COUNT and lift >= MIN_LIFT:
        links.append({"process": p, "tool": t, "count": c, "lift": round(lift, 2)})
links_df = pd.DataFrame(links).sort_values(["process", "lift"], ascending=[True, False])

st = LedgerStore()
src_id = st.ids.mint("SRC", key="a1:bbcgoodfood:ingredient_mentions")
wb_src = st.ids.lookup("SRC", "wikibooks:cookbook")
tool_ids = {}
counts = Counter()
for t in TOOLS:
    rid = st.ids.mint("TOOL", key=f"name:{t.canonical}")
    tool_ids[t.canonical] = rid
    rec = {"id": rid, "record_type": "TOOL", "status": "ACTIVE", "created_by": "Kush+Claude",
           "provenance": {"method": "MANUAL", "agent": "tool_vocab@1.1",
                          "source_ids": [src_id] + ([wb_src] if wb_src and t.canonical in WIKIBOOKS_PAGE else []),
                          "notes": f"corpus sentence mentions: {tool_freq.get(t.canonical, 0)}"},
           "verification": {"status": "UNVERIFIED"}, "canonical_name": t.canonical,
           "aliases": [a for a in t.aliases if a != t.canonical], "category": t.category,
           "material": None, "reactive_with": [], "max_safe_temperature_c": {"status": "UNKNOWN"},
           "external_refs": [f"WIKIBOOKS:Cookbook:{WIKIBOOKS_PAGE[t.canonical]}"] if t.canonical in WIKIBOOKS_PAGE else []}
    counts[("TOOL", st.upsert(rec)[0])] += 1
by_proc = links_df.groupby("process")["tool"].apply(list).to_dict() if len(links_df) else {}
for proc in st.all_latest("PROC"):
    tids = [tool_ids[t] for t in by_proc.get(proc["canonical_name"], []) if t in tool_ids]
    if tids != proc.get("tool_ids", []):
        counts[("PROC", st.upsert({**proc, "tool_ids": tids})[0])] += 1

out = ROOT / "registry" / "tools"
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame([{"tool_id": tool_ids[t.canonical], "canonical": t.canonical, "category": t.category,
               "sentence_mentions": tool_freq.get(t.canonical, 0), "aliases": "|".join(t.aliases)} for t in TOOLS]) \
    .sort_values("sentence_mentions", ascending=False).to_csv(out / "tool_registry_v1.csv", index=False)
links_df.to_csv(out / "process_tool_links_v1.csv", index=False)
pd.DataFrame([{"tool": t, "material": m, "count": c} for (t, m), c in mat.most_common()]) \
    .to_csv(out / "tool_material_mentions.csv", index=False)
zero = [t.canonical for t in TOOLS if not tool_freq.get(t.canonical)]
lines = ["# Tool registry v1", "", f"- tools: {len(TOOLS)}; categories: {dict(Counter(t.category for t in TOOLS))}",
         f"- corpus steps (BBC {n_bbc:,} + Wikibooks {len(steps) - n_bbc:,}) with ≥1 tool mention: "
         f"{steps_with_tool:,}/{len(steps):,} ({steps_with_tool/len(steps):.1%})",
         f"- tools with a Wikibooks equipment page: {sum(t.canonical in WIKIBOOKS_PAGE for t in TOOLS)}",
         f"- tools never mentioned in the corpus (kept: curated/Indian/evidence equipment): {zero}",
         f"- process↔tool links (sentence co-occurrence, count ≥ {MIN_COUNT}, lift ≥ {MIN_LIFT}): {len(links_df)} "
         f"over {links_df['process'].nunique() if len(links_df) else 0} processes",
         "- examples: " + "; ".join(f"{r.process}→{r.tool} (lift {r.lift})" for r in links_df.sort_values("count",
                                                                                                    ascending=False).head(12).itertuples()),
         f"- material mentions (top): " + ", ".join(f"{t}/{m}={c}" for (t, m), c in mat.most_common(8)),
         "- material/reactivity/max temperature NOT asserted (needs authority evidence → WARN layer)",
         f"- ledger writes: {dict(counts)}"]
(ROOT / "reports" / "tool_registry_v1.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
