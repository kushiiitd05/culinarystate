#!/usr/bin/env python3
"""Process registry v1: corpus coverage (spaCy lemmas over all BBC steps) + evidence coverage (EVD steps)
-> PROC- ledger records + registry/processes/*.csv + reports/process_registry_v1.md.

  /opt/anaconda3/bin/python tools/build_process_registry.py [--sample 0]   (0 = all steps, ~3 min)
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import spacy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.process.vocab import (AXES, BY_CANON, IGNORE, LEMMA_TO_PROC, MECHANISMS, PROCESSES,  # noqa: E402
                                         map_step_name, phrase_processes)

ap = argparse.ArgumentParser()
ap.add_argument("--sample", type=int, default=0)
a = ap.parse_args()

steps = []
with (ROOT.parent / "a1" / "A1 3" / "data" / "raw" / "recipes_raw.jsonl").open() as fh:
    for line in fh:
        steps += json.loads(line).get("instruction_steps_raw") or []
if a.sample:
    steps = steps[: a.sample]

nlp = spacy.load("en_core_web_sm", disable=["ner"])
freq, unknown = Counter(), Counter()
steps_with_proc = 0
for text, doc in zip(steps, nlp.pipe(steps, batch_size=256)):
    found = set(phrase_processes(text))
    for t in doc:
        if t.pos_ != "VERB":
            continue
        lem = t.lemma_.lower()
        if lem in LEMMA_TO_PROC:
            found.add(LEMMA_TO_PROC[lem])
        elif lem not in IGNORE and lem.isalpha():
            unknown[lem] += 1
    for p in found:
        freq[p] += 1
    steps_with_proc += bool(found)

st = LedgerStore()
evd_steps = Counter()
unmapped_evd = Counter()
for e in st.all_latest("EVD"):
    for s in e["process"].get("steps", []):
        c = map_step_name(s)
        if c:
            evd_steps[c] += 1
        else:
            unmapped_evd[s] += 1

src = {"id": st.ids.mint("SRC", key="a1:bbcgoodfood:ingredient_mentions"), "record_type": "SRC"}
counts = Counter()
rows = []
for p in PROCESSES:
    rid = st.ids.mint("PROC", key=f"name:{p.canonical}")
    rec = {"id": rid, "record_type": "PROC", "status": "ACTIVE", "created_by": "Kush+Claude",
           "provenance": {"method": "MANUAL", "source_ids": [src["id"]], "agent": "process_vocab@1.0",
                          "notes": "curated from corpus verb discovery; mechanism families AI-drafted (verify vs R3)"},
           "verification": {"status": "UNVERIFIED"}, "canonical_name": p.canonical,
           "aliases": [x for x in p.aliases if x != p.canonical], "family": p.family, "kind": p.kind,
           "required_condition_axes": list(AXES.get(p.family, ())),
           "mechanism_families": list(MECHANISMS.get(p.family, ())),
           "corpus_frequency": freq.get(p.canonical, 0), "evidence_coverage": evd_steps.get(p.canonical, 0)}
    counts[st.upsert(rec)[0]] += 1
    rows.append({"proc_id": rid, "canonical": p.canonical, "family": p.family, "kind": p.kind,
                 "steps_with_process": freq.get(p.canonical, 0), "evd_rows": evd_steps.get(p.canonical, 0),
                 "aliases": "|".join(p.aliases)})

out = ROOT / "registry" / "processes"
out.mkdir(parents=True, exist_ok=True)
reg = pd.DataFrame(rows).sort_values("steps_with_process", ascending=False)
reg.to_csv(out / "process_registry_v1.csv", index=False)
pd.DataFrame(unknown.most_common(200), columns=["lemma", "verb_count"]).to_csv(out / "unmapped_verbs.csv", index=False)
pd.DataFrame(unmapped_evd.most_common(), columns=["evidence_step", "rows"]).to_csv(out / "unmapped_evidence_steps.csv",
                                                                                 index=False)
fam = reg.groupby("family")[["steps_with_process", "evd_rows"]].sum().sort_values("steps_with_process", ascending=False)
no_evd = reg[(reg.evd_rows == 0) & (reg.kind == "ACTION") & (reg.steps_with_process > 0)]
lines = [f"# Process registry v1", "",
         f"- processes: {len(PROCESSES)} ({sum(p.kind == 'ENDPOINT' for p in PROCESSES)} endpoints); families: "
         f"{reg.family.nunique()}",
         f"- BBC steps scanned: {len(steps):,}; steps with ≥1 recognised process: {steps_with_proc:,} "
         f"({steps_with_proc/len(steps):.1%})",
         f"- unmapped verb lemmas (non-ignored): {len(unknown):,}; top: "
         + ", ".join(f"{k}({v})" for k, v in unknown.most_common(15)),
         f"- evidence (EVD) step mentions mapped: {sum(evd_steps.values()):,}; unmapped: {sum(unmapped_evd.values()):,}",
         f"- corpus processes with ZERO state-change evidence: {len(no_evd)} — e.g. "
         + ", ".join(no_evd.canonical.head(20)),
         f"- ledger PROC writes: {dict(counts)}", "", "## Family coverage", "", fam.to_markdown()]
(ROOT / "reports" / "process_registry_v1.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines[:9]))
