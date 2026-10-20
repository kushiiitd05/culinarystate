#!/usr/bin/env python3
"""S116: evidence-first recipe search. Which recipes contain an INSTRUCTION-level ingredient x process match to an ACTIVE EVD
retention cell?  (ingredient-list co-occurrence is not enough: the process event must act on an entity whose ancestry
contains the base ingredient, via the rule compiler's events.)

  /opt/anaconda3/bin/python tools/evidence_first_candidates.py [--pool bbc|wikibooks|foodcom|all] [--limit N]
Pools: bbc (local only, third-party text: spans are NOT written), wikibooks (CC BY-SA), foodcom (data/external/foodcom/RAW_recipes.csv,
only if the user has downloaded it; not present now). Matches are COMPILER-PROPOSED (rule compiler, weak on step structure);
every row needs annotation before use as Gold. No B3/B4 output is read. Writes reports/h_state/evidence_first_recipe_candidates.csv
and reports/h_state/evidence_first_pool_stats.json.
"""
import argparse
import csv
import json
import re
import signal
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.state_graph.prefix_state import prefix_state  # noqa: E402
from culinarystate.state_graph.engine import Add  # noqa: E402
from culinarystate.state_graph.rule_compiler import compile_recipe  # noqa: E402
from culinarystate.state_graph.rule_compiler import step_processes  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402


OUT = ROOT / "reports" / "h_state"
BBC = ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "recipes_processed.jsonl"
WB = ROOT / "data" / "interim" / "wikibooks" / "recipes.jsonl"
FC = ROOT / "data" / "external" / "foodcom" / "recipes.parquet"
FC_CAP = 20000                                                             # deterministic cap on prefilter survivors that get compiled
TIME_RE = re.compile(r"\b\d+\s*(?:-\s*\d+\s*)?(?:min|minutes?|hours?|hrs?|seconds?)\b", re.I)
TEMP_RE = re.compile(r"\b\d{2,3}\s*°?\s*[CF]\b|gas mark|degrees|boiling|simmer", re.I)
FIELDS = ["pool", "recipe_id", "recipe_name", "canonical_ingredient", "ingredient_id", "process", "instruction_span", "step_index",
          "matched_evidence_ids", "evidence_tier", "conditions_available", "recipe_family", "duplicate_family", "candidate_cut_count",
          "licence", "selection_score"]
LICENCE = {"bbc": "THIRD_PARTY_LOCAL_ONLY", "wikibooks": "CC-BY-SA-4.0", "foodcom": "CC0 (Kaggle metadata; UNVERIFIED by us)"}


FC_STATS = {}
SLICE = ""


def pools(which, prefilter=None):
    if which in ("bbc", "all") and BBC.exists():
        for line in BBC.open():
            d = json.loads(line)
            yield "bbc", d["recipe_id"], d["title"], d["ingredient_phrases_raw"], d["instruction_steps_raw"]
    if which in ("wikibooks", "all") and WB.exists():
        for line in WB.open():
            d = json.loads(line)
            steps = d.get("steps") or d.get("instructions") or []
            steps = [s["text"] if isinstance(s, dict) else s for s in steps]
            yield "wikibooks", f"WB{d['pageid']}", d["title"], [i["text"] for i in d.get("ingredients", [])], steps
    if which in ("foodcom", "all") and FC.exists():
        yield from foodcom_pool(prefilter)
    if which == "foodcom_slice":
        import gzip
        for line in gzip.open(SLICE, "rt"):
            d = json.loads(line)
            yield "foodcom", d["id"], d["name"], d["lines"], d["steps"]


def foodcom_pool(prefilter):
    """Food.com (Kaggle irkaal, CC0 declared). `prefilter(ingredient_parts, steps)` is a cheap string test applied to all rows; survivors are
    ordered by a hash of the recipe id (deterministic, not by any score) and capped at FC_CAP."""
    import hashlib

    import pandas as pd
    d = pd.read_parquet(FC, columns=["RecipeId", "Name", "RecipeIngredientQuantities", "RecipeIngredientParts", "RecipeInstructions"])
    keep = []
    for rid, name, q, parts, steps in zip(d.RecipeId, d.Name, d.RecipeIngredientQuantities, d.RecipeIngredientParts, d.RecipeInstructions):
        parts, steps = [str(x) for x in (parts if parts is not None else [])], [str(x) for x in (steps if steps is not None else [])]
        if parts and steps and prefilter(parts, steps):
            q = [str(x) for x in (q if q is not None else [])]
            lines = [f"{(q[i] if i < len(q) and q[i] != 'None' else '')} {p}".strip() for i, p in enumerate(parts)]
            keep.append((hashlib.sha1(str(int(rid)).encode()).hexdigest(), f"FC{int(rid)}", name, lines, steps))
    print(f"foodcom prefilter survivors: {len(keep)} of {len(d)}", file=sys.stderr, flush=True)
    FC_STATS["survivors"], FC_STATS["rows"] = len(keep), len(d)
    for _, rid, name, lines, steps in sorted(keep)[:FC_CAP]:
        yield "foodcom", rid, name, lines, steps


G: dict = {}


def independent_families(rows) -> int:
    """Independent coverage = distinct recipe families, never raw row or recipe counts (duplicate/lineage recipes collapse)."""
    return len({(r["pool"], r["recipe_family"]) for r in rows})


def _one(item):
    """Compile one recipe and return (pool, id, title, stat counter, rows). Pure w.r.t. globals G (set in main before the fork)."""
    pool, rid, title, lines, steps = item
    ing, proc, cells, names = G["ing"], G["proc"], G["cells"], G["names"]
    stat, rows = Counter(recipes=1), []
    fam = norm(title)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(10)                                                       # a pathological recipe must not stall the scan
    try:
        ev = compile_recipe(lines, steps, names)
    except TimeoutError:
        stat["compile_timeouts"] += 1
        return pool, rid, title, stat, rows
    except Exception:                                                      # compiler is rule-based; count failures, never hide
        stat["compile_errors"] += 1
        return pool, rid, title, stat, rows
    finally:
        signal.alarm(0)
    concept = {e.label: (e.concept_id or "") for e in ev if isinstance(e, Add)}
    anc, procs, _, _ = prefix_state(ev, len(ev), concept)
    acting = [e for e in ev if not isinstance(e, Add)]
    found = {}
    for j, e in enumerate(acting):
        nm = type(e).__name__
        pr = getattr(e, "process", None)
        ent = getattr(e, "target", None) or getattr(e, "output", None)
        if nm not in ("Transform", "Merge") or not pr or ent is None:
            continue
        for b in anc.get(ent, {ent}):
            iid = ing.get(norm(concept.get(b, "")))
            pid = proc.get(pr)
            if iid and pid and cells.get((iid, pid)) and (iid, pid) not in found:
                step = getattr(e, "step", None)
                txt = steps[step] if step is not None and step < len(steps) else ""
                found[(iid, pid)] = (b, pr, step, txt, len(acting) - j - 1)
    if found:
        stat["recipes_with_match"] += 1
    stat["matched_cells"] += len(found)
    for (iid, pid), (b, pr, step, txt, after) in found.items():
        cond = "|".join(c for c, rx in (("TIME", TIME_RE), ("TEMPERATURE", TEMP_RE)) if rx.search(txt))
        rows.append({"pool": pool, "recipe_id": rid, "recipe_name": title if pool != "bbc" else "", "canonical_ingredient": iid,
                     "ingredient_id": iid, "process": pid, "instruction_span": txt[:240] if pool != "bbc" else "",
                     "step_index": step, "matched_evidence_ids": "|".join(cells[(iid, pid)][:5]), "evidence_tier": "E3",
                     "conditions_available": cond, "recipe_family": f"FAM-{fam[:40]}", "duplicate_family": "",
                     "candidate_cut_count": after, "licence": LICENCE[pool],
                     "selection_score": round(len(cells[(iid, pid)]) ** 0.5 + 0.5 * bool(cond) + 0.1 * min(after, 5), 3)})
    return pool, rid, title, stat, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="all")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--start", type=int, default=0, help="skip first N recipes of the pool (chunked runs under macOS background throttling)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--context", default="", help="JSON {ing, proc, cells} instead of reading the ledgers (server runs)")
    ap.add_argument("--export-context", default="", help="write the context JSON and exit")
    ap.add_argument("--export-foodcom", default="", help="write the hash-ordered prefilter survivors (<= --fc-cap) as .jsonl.gz and exit")
    ap.add_argument("--slice", default="", help="pool foodcom_slice: read recipes from this .jsonl.gz")
    ap.add_argument("--fc-cap", type=int, default=0, help="override FC_CAP (survivors compiled)")
    ap.add_argument("--tag", default="", help="write evidence_first_recipe_candidates_<tag>.csv / stats_<tag>.json instead")
    a = ap.parse_args()
    global FC_CAP, SLICE
    SLICE = a.slice
    FC_CAP = a.fc_cap or FC_CAP
    if a.context:
        c = json.load(open(a.context))
        ing, proc = c["ing"], c["proc"]
        cells = defaultdict(list, {tuple(k.split("|")): v for k, v in c["cells"].items()})
    else:
        from culinarystate.ledgers.store import LedgerStore
        st = LedgerStore()
        ing = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
        proc = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC") if p["status"] == "ACTIVE"}
        cells = defaultdict(list)
        for e in st.all_latest("EVD"):
            i, p = e["matrix"].get("ingredient_id"), e["process"].get("process_id")
            if e["status"] == "ACTIVE" and (e.get("derived") or {}).get("retention_factor") and i and p:
                cells[(i, p)].append(e["id"])
    if a.export_context:
        json.dump({"ing": ing, "proc": proc, "cells": {"|".join(k): v for k, v in cells.items()}}, open(a.export_context, "w"))
        print("context written", len(ing), len(proc), len(cells))
        return
    names = set(ing)
    iname_by_id = {v: k for k, v in ing.items()}
    pname_by_id = {v: k for k, v in proc.items()}
    rows, stats, seen_titles = [], defaultdict(Counter), Counter()
    cell_ing = {iname for (i, _p) in cells for iname in [iname_by_id.get(i)] if iname}
    cell_proc = {pname_by_id[p] for (_i, p) in cells if p in pname_by_id}

    ing_rx = re.compile(r"\b(?:" + "|".join(re.escape(n) for n in sorted(cell_ing, key=len, reverse=True)) + ")")

    def prefilter(parts, steps):
        if not ing_rx.search(" ".join(parts).lower()):
            return False
        return any(name in cell_proc for st_ in steps for _, name in step_processes(st_))

    if a.export_foodcom:
        import gzip
        with gzip.open(a.export_foodcom, "wt") as fh:
            for _p, rid, name, lines, steps in foodcom_pool(prefilter):
                fh.write(json.dumps({"id": rid, "name": name, "lines": lines, "steps": steps}) + "\n")
        print("foodcom slice written", a.export_foodcom)
        return
    global G
    G = {"ing": ing, "proc": proc, "cells": cells, "names": names}
    items = []
    for n, item in enumerate(pools(a.pool, prefilter)):
        if n < a.start:
            continue
        if a.limit and n >= a.start + a.limit:
            break
        items.append(item)
    if a.workers > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(a.workers) as pool_:
            results = pool_.map(_one, items, chunksize=50)
    else:
        results = []
        for n, it in enumerate(items):
            results.append(_one(it))
            if n % 500 == 0:
                print(f"[{time.strftime('%H:%M:%S')}] {it[0]} {n} recipes", file=sys.stderr, flush=True)
    for (pool, rid, title, stat, rws) in results:
        for k, v in stat.items():
            stats[pool][k] += v
        seen_titles[(pool, norm(title))] += 1
        rows.extend(rws)
    for r in rows:
        r["duplicate_family"] = int(seen_titles[(r["pool"], r["recipe_family"][4:])] > 1)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"evidence_first_recipe_candidates{'_' + a.tag if a.tag else ''}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    by_cell = defaultdict(set)
    for r in rows:
        by_cell[(r["ingredient_id"], r["process"])].add(r["recipe_family"])
    out = {"pools": {k: dict(v) for k, v in stats.items()}, "distinct_cells_matched": len(by_cell), "ledger_cells_total": len(cells),
           "rows": len(rows), "foodcom_prefilter": FC_STATS, "families_per_cell_top": Counter({f"{k[0]}+{k[1]}": len(v) for k, v in by_cell.items()}).most_common(25)}
    (OUT / f"evidence_first_pool_stats{'_' + a.tag if a.tag else ''}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
