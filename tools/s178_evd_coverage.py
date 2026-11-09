#!/usr/bin/env python3
"""S178 EVD lane, T2-C13-R1: counts-only coverage statement for the talk. EVD (ingredient, process) pair coverage against corpus demand,
per process family, tagged COND_UNAUDITED.

Three layers, each stated as what it is:

  1. EVD supply (ledger, ACTIVE rows): per PROC family, rows, PROC ids with any row, distinct (ING, PROC) pairs that hold a MEASURED or
     CENSORED retention value (the router's definition of a routable pair), and the vitamin-C (SVAR-000009) anchor: 115 pairs, 25 ING.
  2. Corpus demand at PROCESS level (committed census, full non-BBC corpora): process events per family and per PROC from
     reports/s178/analysis/corpus_can_say_v1.json (heat L1 + non-heat L1; TASTEset has no step lists). The share of events whose PROC has any EVD
     row is an UPPER bound on coverage: it ignores which ingredient the process acts on.
  3. Corpus demand at PAIR level (a seeded 1,000-recipe non-BBC sample, seed 20261104, the same sample as the committed S177 router census):
     distinct (ING, PROC) pairs the recipes ask about, and how many hold an EVD pair. The sample is re-run through the unchanged router machinery
     (Rung A -> route_text) and reconciled to ``reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json`` (items, events, distinct pairs,
     vitamin-C pairs seen). Full-corpus pair totals are read from the committed full non-BBC census (S177, router census 0.3.0), not recomputed.
     (Until the FIX-GOV repoint this read the S176 full census, which the S177 ABSENT rule superseded.)

Inputs are checked against ``registry/superseded_outputs_S176.csv`` before anything is read (culinarystate.governance_superseded): a
superseded input stops the tool. Status marker (GOV-8): the JSON carries a top-level ``status``; the CSV and SVG cannot carry one safely,
so their status is the one stated at the top of the sibling ``evd_coverage_vs_corpus_demand_v1.md`` (the SVG also says AI_DRAFTED in its <desc>).

One command: ``python tools/s178_evd_coverage.py [--sample-size 1000] [--workers 4] [--out-dir reports/s178/evd]`` writes the JSON, a markdown table with the
statement, a CSV and an SVG figure. ``--no-sample`` skips layer 3 (the table then says so). Counts only; no recipe text, id or span is written.
Status: AI_DRAFTED / PROPOSED, NON_CITABLE, COND_UNAUDITED. Deterministic apart from nothing (no timestamp); reruns are byte-identical.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s178_evd_common import (DEFAULT_OUT, ROOT, counter_dict, dumps, md_table, pct, protected_hashes, read_ledger,  # noqa: E402
                             sha256_file, write_new_or_same)

TOOL_VERSION = "s178-evd-coverage-0.2.0-draft"
CAN_SAY = "reports/s178/analysis/corpus_can_say_v1.json"
CENSUS_FULL = "reports/step23/router_demo_census_vitc_nonBBC_full_S177.json"
CENSUS_1000 = "reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json"
TARGET = "SVAR-000009"
SEED = "20261104"
SAMPLE_FAMILIES = ("WIKIBOOKS", "GUTENBERG_SEGMENT", "FOODCOM", "TASTESET")
EVIDENCE = ("MEASURED", "CENSORED")
FAMILY_ORDER = ("DRY_HEAT", "FAT_HEAT", "WET_HEAT", "HEAT_GENERAL", "COOLING", "PRESERVATION", "FERMENT_LEAVEN", "MECHANICAL_CUT", "MECHANICAL_MIX",
                "SEPARATION", "RESTING", "STORAGE")
UNMAPPED = "NO_PROC_FAMILY"


# ------------------------------------------------------------------------------------------------ pure helpers (unit-tested)
def routable_pairs(evd_rows: list[dict], target: str | None = None) -> set[tuple[str, str]]:
    """(ING, PROC) keys with a MEASURED or CENSORED retention value on an ACTIVE row (any target, or only ``target``)."""
    out = set()
    for e in evd_rows:
        if e.get("status") != "ACTIVE":
            continue
        ing, proc = (e.get("matrix") or {}).get("ingredient_id"), (e.get("process") or {}).get("process_id")
        rf = (e.get("derived") or {}).get("retention_factor") or {}
        if ing and proc and rf.get("status") in EVIDENCE and (target is None or e["target"]["state_variable_id"] == target):
            out.add((ing, proc))
    return out


def family_of(proc_id: str | None, proc_family: dict[str, str]) -> str:
    return proc_family.get(proc_id or "", UNMAPPED)


def events_by_family(events_by_proc: dict[str, int], proc_family: dict[str, str], evd_procs: set[str]) -> dict[str, dict]:
    out: dict[str, dict] = defaultdict(lambda: {"events": 0, "events_with_evd_proc": 0, "procs_with_events": 0, "procs_with_events_and_evd": 0})
    for p, n in events_by_proc.items():
        f = family_of(p, proc_family)
        o = out[f]
        o["events"] += n
        o["procs_with_events"] += 1
        if p in evd_procs:
            o["events_with_evd_proc"] += n
            o["procs_with_events_and_evd"] += 1
    return dict(out)


def pairs_by_family(sample_pairs: set[tuple[str, str]], evd_pairs: set[tuple[str, str]], proc_family: dict[str, str]) -> dict[str, dict]:
    out: dict[str, dict] = defaultdict(lambda: {"sample_distinct_pairs": 0, "sample_pairs_with_evd": 0})
    for ing, proc in sample_pairs:
        o = out[family_of(proc, proc_family)]
        o["sample_distinct_pairs"] += 1
        if (ing, proc) in evd_pairs:
            o["sample_pairs_with_evd"] += 1
    return dict(out)


def ordered(families) -> list[str]:
    return [f for f in FAMILY_ORDER if f in families] + sorted(f for f in families if f not in FAMILY_ORDER)


# ------------------------------------------------------------------------------------------------ layer 1 and 2
def evd_supply(root: Path) -> dict:
    led = root / "ledgers" / "data"
    evd, _ = read_ledger(led / "EVD.jsonl")
    proc, _ = read_ledger(led / "PROC.jsonl")
    proc_family = {i: p["family"] for i, p in proc.items()}
    rows = [e for e in evd.values() if e["status"] == "ACTIVE"]
    pairs_all = routable_pairs(rows)
    pairs_c = routable_pairs(rows, TARGET)
    by_fam: dict[str, dict] = defaultdict(lambda: {"evd_rows": 0, "evd_procs": set(), "pairs": set(), "ing": set(), "rows_with_ing": 0})
    for e in rows:
        pid = e["process"].get("process_id")
        o = by_fam[family_of(pid, proc_family)]
        o["evd_rows"] += 1
        if pid:
            o["evd_procs"].add(pid)
        if e["matrix"].get("ingredient_id"):
            o["rows_with_ing"] += 1
    for ing, pid in pairs_all:
        o = by_fam[family_of(pid, proc_family)]
        o["pairs"].add((ing, pid))
        o["ing"].add(ing)
    cell = Counter((e["matrix"].get("ingredient_id"), e["process"].get("process_id"), e["target"]["state_variable_id"]) for e in rows
                   if e["matrix"].get("ingredient_id") and e["process"].get("process_id"))
    return {"rows": rows, "proc_family": proc_family, "proc_names": {i: p["canonical_name"] for i, p in proc.items()}, "pairs_all": pairs_all,
            "pairs_target": pairs_c, "by_family": by_fam, "evd_procs": {e["process"].get("process_id") for e in rows if e["process"].get("process_id")},
            "ing_with_evd": {e["matrix"]["ingredient_id"] for e in rows if e["matrix"].get("ingredient_id")},
            "cells_ing_proc_svar": len(cell)}


def corpus_events(root: Path, proc_names: dict[str, str]) -> dict:
    d = json.loads((root / CAN_SAY).read_text(encoding="utf-8"))
    name_to_id: dict[str, list[str]] = defaultdict(list)
    for i, n in proc_names.items():
        name_to_id[n.lower()].append(i)
    heat: Counter = Counter()
    for k, v in d["heat"]["derived_by_process"].items():
        heat[k.split("|")[1]] += v["events"]
    nonheat: Counter = Counter()
    unmapped: Counter = Counter()
    for k, v in d["nonheat"]["derived_by_role"].items():
        role = k.split("|")[2].lower()
        ids = sorted(name_to_id.get(role, []))
        if len(ids) == 1:
            nonheat[ids[0]] += v["events"]
        else:
            unmapped[f"{'AMBIGUOUS' if ids else 'UNKNOWN_ROLE'}"] += v["events"]
    both = Counter(heat) + Counter(nonheat)
    return {"events_by_proc": dict(both), "heat_events": sum(heat.values()), "nonheat_events": sum(nonheat.values()), "unmapped_events": dict(unmapped),
            "census_heat_events_by_source": {k: v.get("heat_events") for k, v in d["heat"]["source_level_from_committed_census"].items()},
            "can_say_sha256": sha256_file(root / CAN_SAY)}


# ------------------------------------------------------------------------------------------------ layer 3 (re-runs the router machinery)
def sample_pairs(root: Path, size: int, workers: int) -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("_step17b_rung_a_dryrun", root / "tools/step17b_rung_a_dryrun.py")
    t17 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t17)
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.extraction.rung_a_measure import seeded_sample
    from culinarystate.mechanism import process_signatures as PS
    from culinarystate.mechanism import router_census as RC
    from culinarystate.mechanism import router_demo as RD
    from culinarystate.quantity import rc2_dryrun as D
    index = RD.EvidenceIndex.from_ledger(root / "ledgers" / "data" / "EVD.jsonl")
    status: dict = {}
    seen = 0

    def counted(it):
        nonlocal seen
        for r in it:
            seen += 1
            yield r
    sample = seeded_sample(counted(t17._stream(list(SAMPLE_FAMILIES), root, t17.corpus_records, status)), SEED, size)
    RC._CTX.clear()
    RC._CTX.update(index=index, target_svar=TARGET, rung=RungA(), schema=D.load_schema(), hierarchy=PS.read_process_hierarchy(), gates=None)
    try:
        acc = RC._run(sample, workers)
    finally:
        RC._CTX.clear()
    tot = acc["tot"]
    return {"pairs": acc["pairs"], "ingredients": acc["ingredients"], "recipes_seen": seen, "recipes_sampled": len(sample), "family_status": dict(sorted(status.items())),
            "items": tot["items"], "events": tot["events"], "items_linked": tot["items_linked"], "items_with_process": tot["items_with_process"],
            "texts_with_steps": tot["texts_with_steps"], "exceptions": sum(acc["exc"].values()), "evd_pairs_target_seen": len(index.pairs(TARGET) & acc["pairs"])}


# ------------------------------------------------------------------------------------------------ assemble
INPUT_FILES = ("ledgers/data/EVD.jsonl", "ledgers/data/PROC.jsonl", CAN_SAY, CENSUS_FULL, CENSUS_1000)


def check_inputs_not_superseded(root: Path) -> None:
    """Raise culinarystate.governance_superseded.SupersededInputError if any input is in registry/superseded_outputs_S176.csv."""
    from culinarystate.governance_superseded import assert_not_superseded
    assert_not_superseded(INPUT_FILES, root=root)


def build(root: Path, size: int, workers: int, with_sample: bool) -> dict:
    check_inputs_not_superseded(root)
    sup = evd_supply(root)
    ce = corpus_events(root, sup["proc_names"])
    census_full = json.loads((root / CENSUS_FULL).read_text(encoding="utf-8"))
    census_1000 = json.loads((root / CENSUS_1000).read_text(encoding="utf-8"))
    ev_fam = events_by_family(ce["events_by_proc"], sup["proc_family"], sup["evd_procs"])
    smp = sample_pairs(root, size, workers) if with_sample else None
    pf = pairs_by_family(smp["pairs"], sup["pairs_all"], sup["proc_family"]) if smp else {}
    fams = ordered(set(ev_fam) | set(sup["by_family"]) | set(pf))
    all_procs_by_family: Counter = Counter(f for f in sup["proc_family"].values())
    direct_full = defaultdict(int)
    direct_full_ungated = defaultdict(int)
    for k, v in census_full["direct_by_process"].items():
        direct_full[family_of(k.replace("__", "-"), sup["proc_family"])] += v
    for k, v in census_full["direct_ungated_by_process"].items():
        direct_full_ungated[family_of(k.replace("__", "-"), sup["proc_family"])] += v
    table = []
    for f in fams:
        s, e, p = sup["by_family"].get(f), ev_fam.get(f, {}), pf.get(f, {})
        row = {"process_family": f, "proc_ids_in_registry": all_procs_by_family.get(f, 0),
               "corpus_events": e.get("events", 0), "procs_with_corpus_events": e.get("procs_with_events", 0),
               "corpus_events_with_evd_proc": e.get("events_with_evd_proc", 0), "pct_events_with_evd_proc": pct(e.get("events_with_evd_proc", 0), e.get("events", 0)),
               "evd_rows": s["evd_rows"] if s else 0, "evd_procs": len(s["evd_procs"]) if s else 0, "evd_ing_proc_pairs_routable": len(s["pairs"]) if s else 0,
               "evd_ing_in_those_pairs": len(s["ing"]) if s else 0,
               "sample_distinct_pairs": p.get("sample_distinct_pairs") if smp else None, "sample_pairs_with_evd": p.get("sample_pairs_with_evd") if smp else None,
               "pct_sample_pairs_with_evd": pct(p.get("sample_pairs_with_evd", 0), p.get("sample_distinct_pairs", 0)) if smp else None,
               "router_vitc_direct_items_gated_full_nonBBC": direct_full.get(f, 0), "router_vitc_direct_items_ungated_full_nonBBC": direct_full_ungated.get(f, 0)}
        table.append(row)
    totals = {k: sum((r[k] or 0) for r in table) for k in ("proc_ids_in_registry", "corpus_events", "corpus_events_with_evd_proc", "evd_rows", "evd_ing_proc_pairs_routable",
                                                           "router_vitc_direct_items_gated_full_nonBBC", "router_vitc_direct_items_ungated_full_nonBBC")}
    if smp:
        totals["sample_distinct_pairs"] = sum(r["sample_distinct_pairs"] or 0 for r in table)
        totals["sample_pairs_with_evd"] = sum(r["sample_pairs_with_evd"] or 0 for r in table)
    totals["pct_events_with_evd_proc"] = pct(totals["corpus_events_with_evd_proc"], totals["corpus_events"])
    totals["pct_sample_pairs_with_evd"] = pct(totals.get("sample_pairs_with_evd", 0), totals.get("sample_distinct_pairs", 0)) if smp else None
    cf, c1 = census_full["evidence_coverage"], census_1000["evidence_coverage"]
    recon = {
        "evd_vitc_pairs_equal_router_census": [len(sup["pairs_target"]), cf["evd_pairs_for_target"], c1["evd_pairs_for_target"]],
        "evd_vitc_ingredients_equal_router_census": [len({i for i, _ in sup["pairs_target"]}), cf["evd_ingredients_for_target"], c1["evd_ingredients_for_target"]],
        "evd_pair_counts_equal_router_census": len(sup["pairs_target"]) == cf["evd_pairs_for_target"] == c1["evd_pairs_for_target"]
        and len({i for i, _ in sup["pairs_target"]}) == cf["evd_ingredients_for_target"] == c1["evd_ingredients_for_target"],
        "full_nonBBC_census": {"file": CENSUS_FULL, "recipes_sampled": census_full["recipes_sampled"], "items": census_full["items"], "sample_distinct_pairs": cf["sample_distinct_pairs"],
                               "evd_vitc_pairs_seen": cf["evd_pairs_seen_in_sample"], "pct_vitc_pairs_seen_of_distinct_pairs": pct(cf["evd_pairs_seen_in_sample"], cf["sample_distinct_pairs"]),
                               "sample_distinct_ingredients": cf["sample_distinct_ingredients"], "ingredients_with_vitc_evidence": cf["sample_ingredients_with_target_evidence"],
                               "route_ungated_DIRECT": census_full["route_ungated"].get("DIRECT"), "route_gated_DIRECT": census_full["route"].get("DIRECT"),
                               "census_version": census_full["census_version"]},
        "sha256": {CENSUS_FULL: sha256_file(root / CENSUS_FULL), CENSUS_1000: sha256_file(root / CENSUS_1000)},
        "can_say_events_total_vs_heat_sources": [ce["heat_events"], sum(v for k, v in ce["census_heat_events_by_source"].items() if k in ("FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS"))],
        "can_say_heat_events_equal_committed_census_non_BBC": ce["heat_events"] == sum(v for k, v in ce["census_heat_events_by_source"].items() if k in ("FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS")),
    }
    if smp:
        recon["sample_vs_committed_S177_1000_census"] = {k: [smp[k], c1v] for k, c1v in (("items", census_1000["items"]), ("events", census_1000["events"]),
                                                                                         ("recipes_seen", census_1000["recipes_seen"]), ("recipes_sampled", census_1000["recipes_sampled"]))}
        recon["sample_vs_committed_S177_1000_census"].update(distinct_pairs=[len(smp["pairs"]), c1["sample_distinct_pairs"]], distinct_ingredients=[len(smp["ingredients"]), c1["sample_distinct_ingredients"]],
                                                              vitc_pairs_seen=[smp["evd_pairs_target_seen"], c1["evd_pairs_seen_in_sample"]])
        recon["sample_reproduces_committed_S177_1000_census"] = all(v[0] == v[1] for v in recon["sample_vs_committed_S177_1000_census"].values())
    sample_block = None
    if smp:
        sample_block = {"seed_sha256": census_1000["seed_sha256"], "size": size, "recipes_seen": smp["recipes_seen"], "recipes_sampled": smp["recipes_sampled"],
                        "family_status": smp["family_status"], "items": smp["items"], "events": smp["events"], "items_linked": smp["items_linked"], "items_with_process": smp["items_with_process"],
                        "exceptions": smp["exceptions"], "distinct_pairs": len(smp["pairs"]), "distinct_ingredients": len(smp["ingredients"]),
                        "pairs_with_evd": len(smp["pairs"] & sup["pairs_all"]), "ingredients_with_any_evd_row": len(smp["ingredients"] & sup["ing_with_evd"]),
                        "pct_pairs_with_evd": pct(len(smp["pairs"] & sup["pairs_all"]), len(smp["pairs"])),
                        "pairs_with_no_process_family": sum(1 for _, p in smp["pairs"] if family_of(p, sup["proc_family"]) == UNMAPPED)}
    statement = (f"EVD holds {len(sup['pairs_all']):,} routable (ingredient, process) pairs over {len({i for i, _ in sup['pairs_all']}):,} ingredients and {len(sup['evd_procs'])} processes "
                 f"({len(sup['rows']):,} ACTIVE rows, all tier E3, UNVERIFIED, COND_UNAUDITED). ")
    if sample_block:
        statement += (f"A seeded 1,000-recipe non-BBC sample asks about {sample_block['distinct_pairs']:,} distinct (ingredient, process) pairs; {sample_block['pairs_with_evd']:,} "
                      f"({sample_block['pct_pairs_with_evd']} %) have any EVD pair. ")
    statement += (f"At process level {totals['pct_events_with_evd_proc']} % of {totals['corpus_events']:,} corpus process events (non-BBC, full) are for a process that has some EVD row: an upper bound that ignores the ingredient. "
                  f"For vitamin C the full non-BBC census saw {cf['evd_pairs_seen_in_sample']} of EVD's {cf['evd_pairs_for_target']} pairs among {cf['sample_distinct_pairs']:,} distinct pairs "
                  f"({pct(cf['evd_pairs_seen_in_sample'], cf['sample_distinct_pairs'])} %).")
    return {"record": "EVD_COVERAGE_VS_CORPUS_DEMAND_S178", "tool_version": TOOL_VERSION, "status": "AI_DRAFTED_PROPOSED", "label": "NON_CITABLE_COUNTS_ONLY",
            "tags": ["COND_UNAUDITED", "E3_UNVERIFIED", "BOOTSTRAP_UNVERIFIED", "NOT_07A_AUDITED"], "contains_text": False, "contains_ids": False, "counts_as_human_gate": False,
            "layers": {"1_evd_supply": "ledger ACTIVE rows", "2_corpus_events": CAN_SAY + " (committed census aggregate, non-BBC)",
                       "3_pair_demand": "seeded 1,000-recipe non-BBC sample through the unchanged router (Rung A + route_text)" if smp else "NOT_RUN (--no-sample)"},
            "statement": statement, "table": table, "totals": totals,
            "evd_supply": {"active_rows": len(sup["rows"]), "routable_pairs_any_target": len(sup["pairs_all"]), "routable_ingredients": len({i for i, _ in sup["pairs_all"]}),
                           "procs_with_evd_rows": len(sup["evd_procs"]), "proc_ids_in_registry": len(sup["proc_family"]),
                           "ing_ids_with_evd_rows": len(sup["ing_with_evd"]), "cells_ing_proc_svar": sup["cells_ing_proc_svar"],
                           "vitc_pairs": len(sup["pairs_target"]), "vitc_ingredients": len({i for i, _ in sup["pairs_target"]})},
            "corpus_events": {"heat": ce["heat_events"], "nonheat": ce["nonheat_events"], "unmapped_events": ce["unmapped_events"]},
            "sample": sample_block, "reconciliation": recon,
            "reading": ["process-level share is an upper bound on coverage (ingredient ignored)", "pair-level numbers are a 1,000-recipe sample, not the corpus",
                        "EVD rows are tier E3, UNVERIFIED and COND_UNAUDITED: coverage is not evidence quality", "TASTEset has no step lists: no process events"],
            "inputs": {"ledgers/data/EVD.jsonl": sha256_file(root / "ledgers/data/EVD.jsonl"), "ledgers/data/PROC.jsonl": sha256_file(root / "ledgers/data/PROC.jsonl"), CAN_SAY: ce["can_say_sha256"]}}


def render_csv(d: dict) -> str:
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\n")
    cols = list(d["table"][0].keys())
    w.writerow(cols)
    for r in d["table"]:
        w.writerow([r[c] for c in cols])
    return buf.getvalue()


def render_md(d: dict) -> str:
    T = d["table"]
    rows = [[r["process_family"], r["corpus_events"], r["pct_events_with_evd_proc"], r["evd_rows"], r["evd_procs"], r["evd_ing_proc_pairs_routable"],
             r["sample_distinct_pairs"], r["sample_pairs_with_evd"], r["pct_sample_pairs_with_evd"], r["router_vitc_direct_items_gated_full_nonBBC"]] for r in T]
    t = d["totals"]
    rows.append(["**all**", t["corpus_events"], t["pct_events_with_evd_proc"], t["evd_rows"], d["evd_supply"]["procs_with_evd_rows"], d["evd_supply"]["routable_pairs_any_target"],
                 t.get("sample_distinct_pairs"), t.get("sample_pairs_with_evd"), t["pct_sample_pairs_with_evd"], t["router_vitc_direct_items_gated_full_nonBBC"]])
    rc = d["reconciliation"]
    out = ["# EVD coverage against corpus demand, per process family (S178, T2-C13-R1)", "",
           "Status: AI_DRAFTED / PROPOSED, NON_CITABLE, counts only. **Tags: COND_UNAUDITED** (the 07.A condition-audit gate has not passed), E3_UNVERIFIED, BOOTSTRAP_UNVERIFIED. "
           f"Reproduce with one command: `python tools/s178_evd_coverage.py` ({TOOL_VERSION}).", "",
           "## Statement for the talk (counts only)", "", d["statement"], "",
           "## Table", "",
           "Columns: corpus events = process events in the full non-BBC corpora (committed census aggregate); % events with EVD PROC = share whose process has any EVD row (**upper bound**, ingredient ignored); "
           "EVD rows / PROC ids / routable pairs = ACTIVE EVD supply by PROC family (pair = (ING, PROC) with a MEASURED or CENSORED value, any target); sample pairs = distinct (ING, PROC) pairs asked in the seeded 1,000-recipe non-BBC sample, "
           "and how many hold an EVD pair; last column = vitamin-C DIRECT items in the committed full non-BBC router census (gated).", "",
           md_table(["process family", "corpus events", "% events with EVD PROC", "EVD rows", "EVD PROC ids", "EVD pairs", "sample pairs", "sample pairs with EVD", "% sample pairs with EVD", "vit-C DIRECT (router)"], rows,
                    align_right=tuple(range(1, 10))), "",
           "![coverage](fig_evd_coverage_by_family_v1.svg)", "",
           "## Reconciliation to the router census and the EVD ledger", "",
           f"- EVD vitamin-C (SVAR-000009) routable pairs: ledger {rc['evd_vitc_pairs_equal_router_census'][0]} = full non-BBC census {rc['evd_vitc_pairs_equal_router_census'][1]} = 1,000-sample census {rc['evd_vitc_pairs_equal_router_census'][2]}; "
           f"ingredients {rc['evd_vitc_ingredients_equal_router_census'][0]} = {rc['evd_vitc_ingredients_equal_router_census'][1]} = {rc['evd_vitc_ingredients_equal_router_census'][2]}. Equal: **{rc['evd_pair_counts_equal_router_census']}**.",
           f"- Heat events read from the can-say aggregate ({rc['can_say_events_total_vs_heat_sources'][0]:,}) equal the committed heat censuses of the three non-BBC sources ({rc['can_say_events_total_vs_heat_sources'][1]:,}): **{rc['can_say_heat_events_equal_committed_census_non_BBC']}**.",
           f"- Full non-BBC census ({rc['full_nonBBC_census']['file']}): {rc['full_nonBBC_census']['recipes_sampled']:,} recipes, {rc['full_nonBBC_census']['items']:,} items, {rc['full_nonBBC_census']['sample_distinct_pairs']:,} distinct pairs, "
           f"vitamin-C pairs seen {rc['full_nonBBC_census']['evd_vitc_pairs_seen']} ({rc['full_nonBBC_census']['pct_vitc_pairs_seen_of_distinct_pairs']} % of distinct pairs); census_version {rc['full_nonBBC_census']['census_version']}."]
    if d["sample"]:
        s = d["sample"]
        out += [f"- Sample re-run ({s['recipes_sampled']} of {s['recipes_seen']:,} recipes; {s['items']:,} items; {s['events']:,} events; {s['exceptions']} exceptions) vs the committed S177 1,000-recipe census "
                f"(items, events, recipes seen, distinct pairs, distinct ingredients, vitamin-C pairs seen): **reproduces: {rc['sample_reproduces_committed_S177_1000_census']}** {rc['sample_vs_committed_S177_1000_census']}.",
                f"- Sample ingredients with any EVD row: {s['ingredients_with_any_evd_row']} of {s['distinct_ingredients']}."]
    out += ["", "## How to read it", ""] + [f"- {x}" for x in d["reading"]] + [""]
    return "\n".join(out)


def render_svg(d: dict) -> str:
    import s178_analysis_corpus_can_say_render as R
    groups = [(r["process_family"], [r["pct_events_with_evd_proc"] or 0.0, r["pct_sample_pairs_with_evd"] or 0.0]) for r in d["table"] if r["corpus_events"] or r["sample_distinct_pairs"]]
    series = ["% of corpus process events whose PROC has any EVD row (upper bound)", "% of sampled (ingredient, process) pairs with an EVD pair"]
    return R.grouped_bars("EVD coverage of corpus demand, by process family (COND_UNAUDITED, E3 unverified)",
                          "Non-BBC corpora; pair level = seeded 1,000-recipe sample. Counts only; NON_CITABLE.", groups, series, [R.CAT[0], R.CAT[1]])


def run(out_dir: Path, size: int, workers: int, with_sample: bool, root: Path = ROOT) -> dict:
    before = protected_hashes(root)
    d = build(root, size, workers, with_sample)
    assert before == protected_hashes(root), "protected ledger changed during run"
    d["protected_ledgers_unchanged_during_run"] = True
    h = {"json": write_new_or_same(out_dir / "evd_coverage_vs_corpus_demand_v1.json", dumps(d)),
         "csv": write_new_or_same(out_dir / "evd_coverage_vs_corpus_demand_v1.csv", render_csv(d)),
         "md": write_new_or_same(out_dir / "evd_coverage_vs_corpus_demand_v1.md", render_md(d)),
         "svg": write_new_or_same(out_dir / "fig_evd_coverage_by_family_v1.svg", render_svg(d))}
    return {"sha256": h, "reconciled": d["reconciliation"].get("sample_reproduces_committed_S177_1000_census"), "evd_pair_counts_equal_router_census": d["reconciliation"]["evd_pair_counts_equal_router_census"],
            "statement": d["statement"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-sample", action="store_true", help="skip the pair-level layer (no corpus scan)")
    ap.add_argument("--selfcheck", action="store_true", help="run twice into scratch dirs and compare hashes")
    a = ap.parse_args(argv)
    if a.selfcheck:
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            r1, r2 = run(Path(t1), a.sample_size, a.workers, not a.no_sample), run(Path(t2), a.sample_size, a.workers, not a.no_sample)
        print(dumps({"selfcheck": "IDENTICAL" if r1 == r2 else "DIFFERENT", "run1": r1}))
        return 0 if r1 == r2 else 1
    print(dumps(run(ROOT / a.out_dir, a.sample_size, a.workers, not a.no_sample)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
