#!/usr/bin/env python3
"""Mine cause / prevention / recovery statements (kg/troubleshoot.py) from Gutenberg (PD) and Wikibooks (CC BY-SA).

  /opt/anaconda3/bin/python tools/mine_troubleshooting.py
Writes data/interim/troubleshooting/statements.jsonl (all, local) and registry/kg/troubleshooting_candidates_v1.csv
(Gutenberg public-domain statements only, with book/REC locator; Wikibooks counted, text kept local for licence
hygiene). Support = number of distinct books/pages stating the same (relation, failure, normalised text).
Candidates for the RQ16-18 proposer; not verified causal facts.
"""
import ast
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.kg.troubleshoot import mine_sentence, sentences  # noqa: E402

OUT = ROOT / "data" / "interim" / "troubleshooting"


def norm(t: str) -> str:
    t = re.sub(r"\b(a|an|the|it|them|some|little|very|well|at once|immediately|quickly)\b", " ", t.lower())
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", t)).strip()


def docs():
    for line in (ROOT / "data" / "interim" / "gutenberg" / "recipes.jsonl").open():
        d = json.loads(line)
        yield "GUTENBERG-PD", f"GUTENBERG:{d['book_id']}", d.get("rec_id"), d.get("body") or ""
    wb = ROOT / "data" / "interim" / "wikibooks"
    for line in (wb / "recipes.jsonl").open():
        d = json.loads(line)
        steps = d["steps"] if isinstance(d["steps"], list) else ast.literal_eval(d["steps"] or "[]")
        yield "WIKIBOOKS-COOKBOOK", d["url"], None, " ".join(s.get("text", "") if isinstance(s, dict) else str(s) for s in steps)
    for f in ("techniques.jsonl", "ingredients.jsonl", "equipment.jsonl"):
        for line in (wb / f).open():
            d = json.loads(line)
            yield "WIKIBOOKS-COOKBOOK", d["url"], None, " ".join(str(d.get(k) or "") for k in ("lead", "text", "body"))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, n_docs = [], Counter()
    with (OUT / "statements.jsonl").open("w") as fh:
        for fam, src, rec, text in docs():
            n_docs[fam] += 1
            for s in sentences(text):
                for st in mine_sentence(s):
                    r = {"family": fam, "source": src, "rec_id": rec, "relation": st.relation, "failure": st.failure,
                         "text": st.text, "key": norm(st.text), "sentence": st.sentence[:400]}
                    rows.append(r)
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    df = pd.DataFrame(rows)
    sup = df.groupby(["relation", "failure", "key"]).agg(support_sources=("source", "nunique"), mentions=("source", "size"),
                                                        families=("family", lambda x: "|".join(sorted(set(x))))).reset_index()
    pd_rows = df[df.family == "GUTENBERG-PD"].drop_duplicates(["relation", "failure", "key"])[
        ["relation", "failure", "key", "text", "source", "rec_id"]]
    reg = sup.merge(pd_rows, on=["relation", "failure", "key"], how="left").sort_values(
        ["support_sources", "mentions"], ascending=False)
    reg.to_csv(ROOT / "registry" / "kg" / "troubleshooting_candidates_v1.csv", index=False)
    random.seed(20261018)
    sample = random.sample(rows, min(40, len(rows)))
    (OUT / "precision_sample.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in sample) + "\n")
    by = df.groupby(["relation", "failure"]).size().unstack(0).fillna(0).astype(int)
    lines = ["# Troubleshooting candidates v1 (RQ16-18/19 proposer evidence)", "",
             f"- documents scanned: {dict(n_docs)}; statements: {len(df):,} (CAUSE {sum(df.relation == 'CAUSE'):,}, "
             f"PREVENTION {sum(df.relation == 'PREVENTION'):,}, RECOVERY {sum(df.relation == 'RECOVERY'):,})",
             f"- distinct (relation, failure, text) keys: {len(sup):,}; with support ≥ 2 sources: {sum(sup.support_sources >= 2):,}",
             "- registry CSV carries Gutenberg (public domain) text only; Wikibooks text stays local (CC BY-SA).",
             "- candidates, not verified causes; precision sample in data/interim/troubleshooting/precision_sample.jsonl",
             "- AI-judged precision on fresh random samples (not human verification): 37/40 (mixed, seed 7); "
             "17/20 RECOVERY before noise filter; 26/30 strict / 28/30 lenient (mixed, seed 23). Known noise: "
             "condition spans from unrelated if-clauses, vague actions.", "",
             by.to_markdown()]
    (ROOT / "reports" / "troubleshooting_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:5]))


if __name__ == "__main__":
    main()
