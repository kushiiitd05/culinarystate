#!/usr/bin/env python3
"""Step 08a.8 scoring of the returned edge-audit and unlinked-pair packets (G08-3, G08-H, THR-08A-18).

Reviewer code synonyms are mapped to the packet codes (SCRIBE MAPPING, approved by Kush 2026-10-27); originals are never
edited, mapped copies go to <out-dir>/mapped/. The sealed key is read only here, to attach strata.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lineage import audit_packet as ap  # noqa: E402
from culinarystate.lineage.wilson import wilson_interval  # noqa: E402

EDGE_MAP = {"CORRECT": "CORRECT_EDGE", "SUPPORTED": "CORRECT_EDGE", "INCORRECT": "WRONG_EDGE",
            "NOT_SUPPORTED": "WRONG_EDGE", "UNCERTAIN": "UNCERTAIN"}
# ASSUMPTION (Kush: "same thing"): on the unlinked-pair question CORRECT = "correctly not linked" = NOT_DUPLICATE.
PAIR_MAP = {"CORRECT": "NOT_DUPLICATE", "DISTINCT_EVIDENCE": "NOT_DUPLICATE", "INCORRECT": "TRUE_DUPLICATE",
            "UNCERTAIN": "UNCERTAIN"}


def _read(p: Path) -> tuple[list[str], list[dict]]:
    with p.open(newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames), list(r)


def _mapped(src: Path, dst: Path, col: str, mp: dict) -> None:
    head, rows = _read(src)
    for r in rows:
        r[col] = mp[r[col].strip()]
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, head)
        w.writeheader()
        w.writerows(rows)


def _prec(correct: int, n: int) -> dict:
    lo, hi = wilson_interval(correct, n) if n else (None, None)
    return {"correct": correct, "n": n, "precision": correct / n if n else None, "wilson_lower": lo, "wilson_upper": hi}


def main() -> int:
    ap_ = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap_.add_argument("--dir", type=Path, default=ROOT / "annotation" / "lineage_audit")
    ap_.add_argument("--out", type=Path, default=ROOT / "reports" / "step08" / "step08a_audit_result_v1.json")
    ap_.add_argument("--parv-edge", default="edge_audit_v1_Parv_1.csv")
    ap_.add_argument("--parv-pair", default="parv_miss.csv")
    a = ap_.parse_args()
    d = a.dir
    m = d / "mapped"
    _mapped(d / "edge_audit_v1_Kush_1.csv", m / "edge_audit_v1_Kush.csv", ap.EDGE_JUDGEMENT_COL, EDGE_MAP)
    _mapped(d / a.parv_edge, m / "edge_audit_v1_Parv.csv", ap.EDGE_JUDGEMENT_COL, EDGE_MAP)
    _mapped(d / "missed_pair_v1_Kush_1.csv", m / "missed_pair_v1_Kush.csv", ap.PAIR_JUDGEMENT_COL, PAIR_MAP)
    _mapped(d / a.parv_pair, m / "missed_pair_v1_Parv.csv", ap.PAIR_JUDGEMENT_COL, PAIR_MAP)
    ev = ap.validate_returned_edge_packets(d / "edge_audit_v1_Kush.csv", m / "edge_audit_v1_Kush.csv", m / "edge_audit_v1_Parv.csv")
    pv = ap.validate_returned_pair_packets(d / "missed_pair_v1_Kush.csv", m / "missed_pair_v1_Kush.csv", m / "missed_pair_v1_Parv.csv")

    _, key = _read(d / "edge_audit_v1_KEY_SEALED.csv")
    strat = {r["audit_id"]: r["stratum"] for r in key}
    lab = {n: {r["audit_id"]: r[ap.EDGE_JUDGEMENT_COL] for r in _read(m / f"edge_audit_v1_{n}.csv")[1]} for n in ("Kush", "Parv")}
    out: dict = {"mapping_note": "scribe mapping of reviewer code synonyms, approved by Kush; originals untouched",
                 "edge_map": EDGE_MAP, "pair_map": PAIR_MAP, "pair_map_assumption": "CORRECT/DISTINCT_EVIDENCE read as NOT_DUPLICATE",
                 "provenance": {"edge": ev["status"], "pairs": pv["status"], "problems": ev["problems"] + pv["problems"]},
                 "edge_precision": {}, "agreement": {}}
    for who in ("Kush", "Parv", "both_correct", "either_wrong_or_uncertain_is_error"):
        out["edge_precision"][who] = {}
    ids = sorted(strat)
    for s in ("ALL", "B2", "B3", "STRONG"):
        sel = [i for i in ids if s == "ALL" or strat[i] == s]
        for who in ("Kush", "Parv"):
            out["edge_precision"][who][s] = _prec(sum(lab[who][i] == "CORRECT_EDGE" for i in sel), len(sel))
        both = sum(lab["Kush"][i] == lab["Parv"][i] == "CORRECT_EDGE" for i in sel)
        out["edge_precision"]["both_correct"][s] = _prec(both, len(sel))
        out["edge_precision"]["either_wrong_or_uncertain_is_error"][s] = out["edge_precision"]["both_correct"][s]
        out["agreement"][s] = {"raw": sum(lab["Kush"][i] == lab["Parv"][i] for i in sel) / len(sel),
                               "crosstab": dict(Counter((lab["Kush"][i], lab["Parv"][i]) for i in sel).most_common()) and
                               {f"{k[0]}|{k[1]}": v for k, v in Counter((lab["Kush"][i], lab["Parv"][i]) for i in sel).items()}}
    thr = 0.90
    out["G08-3"] = {"threshold_wilson_lower": thr, "per_reviewer_pass": {w: out["edge_precision"][w]["ALL"]["wilson_lower"] >= thr for w in ("Kush", "Parv")},
                    "strata_n_ok": all(out["edge_precision"]["Kush"][s]["n"] >= 50 for s in ("B2", "B3", "STRONG")),
                    "status": "PASS" if all(out["edge_precision"][w]["ALL"]["wilson_lower"] >= thr for w in ("Kush", "Parv")) else "FAIL"}
    pairs = {n: [r[ap.PAIR_JUDGEMENT_COL] for r in _read(m / f"missed_pair_v1_{n}.csv")[1]] for n in ("Kush", "Parv")}
    out["THR-08A-18_miss_rate"] = {n: ap.miss_rate_report(sum(v == "TRUE_DUPLICATE" for v in pairs[n]), len(pairs[n]))
                                   for n in pairs} | {"uncertain": {n: sum(v == "UNCERTAIN" for v in pairs[n]) for n in pairs}}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"provenance": out["provenance"], "G08-3": out["G08-3"],
                      "precision": {w: {s: (round(v["precision"], 3), round(v["wilson_lower"], 3)) for s, v in out["edge_precision"][w].items()}
                                    for w in ("Kush", "Parv", "both_correct")},
                      "raw_agreement": {s: round(v["raw"], 3) for s, v in out["agreement"].items()},
                      "miss": out["THR-08A-18_miss_rate"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
