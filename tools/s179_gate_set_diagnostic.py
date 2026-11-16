#!/usr/bin/env python3
"""Evaluate a prehashed AI-authored gate set without changing gate or D5 code.

UNKNOWN is explicitly counted and operationally means no activation. Wilson
intervals summarize these authored cases, not independent population accuracy.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rate(k, n):
    if not n:
        return {"numerator": k, "denominator": n, "value": None, "wilson95": None}
    p, z = k / n, 1.959963984540054
    scale = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / scale
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / scale
    return {"numerator": k, "denominator": n, "value": p,
            "wilson95": [max(0., mid - half), min(1., mid + half)]}


def binary_metrics(gold, predicted):
    if len(gold) != len(predicted) or not all(type(v) is bool for v in gold):
        raise ValueError("equal lengths and boolean gold required")
    counts = Counter(TP=0, FN=0, FP=0, TN=0)
    unknown = Counter(all=0, gold_positive=0, gold_negative=0)
    for truth, prediction in zip(gold, predicted):
        if prediction not in (True, False, None):
            raise ValueError("predictions must be boolean or None")
        if prediction is None:
            unknown["all"] += 1
            unknown["gold_positive" if truth else "gold_negative"] += 1
        active = prediction is True
        counts[("TP" if active else "FN") if truth else ("FP" if active else "TN")] += 1
    tp, fn, fp, tn = (counts[k] for k in ("TP", "FN", "FP", "TN"))
    return {"counts": dict(counts), "unknown": dict(unknown), "n": len(gold),
            "precision": rate(tp, tp + fp), "recall": rate(tp, tp + fn),
            "false_negative_rate": rate(fn, tp + fn), "false_positive_rate": rate(fp, fp + tn),
            "unknown_rate": rate(unknown["all"], len(gold)),
            "prediction_rule": "Only literal True activates; False and None do not. UNKNOWN is also reported separately."}


def check_manifest(manifest):
    for path, digest in manifest["files"].items():
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        if sha(p) != digest:
            raise ValueError(f"Prehashed file changed: {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("refusing to overwrite")
    manifest = json.loads(args.manifest.read_text())
    check_manifest(manifest)
    rel_path = args.annotations.resolve().relative_to(ROOT).as_posix()
    if rel_path not in manifest["files"]:
        parser.error("annotations absent from prehash manifest")
    started = datetime.now(timezone.utc).isoformat()
    if datetime.fromisoformat(manifest["labels_prehashed_at_utc"]) >= datetime.fromisoformat(started):
        parser.error("prehash must precede predictions")
    from culinarystate.decision.relevance import relevance_gate
    from culinarystate.decision.query_router import route
    from culinarystate.decision.safety import is_safety
    rows = list(csv.DictReader(args.annotations.open(newline="")))
    if len({r["case_id"] for r in rows}) != len(rows):
        parser.error("duplicate case id")
    records, confusion = [], Counter()
    for row in rows:
        if row["needs_process_reasoning"] not in ("true", "false") or row["safety_question"] not in ("true", "false"):
            parser.error("labels must be literal true/false")
        q = row["query"]
        relevance, routing = relevance_gate(q), route(q)
        confusion[(row["expected_branch"], routing["branch"])] += 1
        records.append({"case_id": row["case_id"], "origin": row["origin"], "category": row["category"],
                        "query_sha256": hashlib.sha256(q.encode()).hexdigest(),
                        "gold_process": row["needs_process_reasoning"] == "true",
                        "gold_safety": row["safety_question"] == "true", "gold_branch": row["expected_branch"],
                        "gate_relevant": relevance["relevant"], "gate_reason": relevance["reason"],
                        "router_needs_process": routing["needs_process_model"], "router_branch": routing["branch"],
                        "safety_activation": is_safety(q)})
    results = {}
    for name, gold_key, pred_key in [("process_relevance_gate", "gold_process", "gate_relevant"),
                                     ("router_process_activation", "gold_process", "router_needs_process"),
                                     ("safety_gate", "gold_safety", "safety_activation")]:
        results[name] = binary_metrics([r[gold_key] for r in records], [r[pred_key] for r in records])
        results[name]["false_negative_case_ids"] = [r["case_id"] for r in records if r[gold_key] and r[pred_key] is not True]
        results[name]["false_positive_case_ids"] = [r["case_id"] for r in records if not r[gold_key] and r[pred_key] is True]
    check_manifest(manifest)
    report = {"record": "PREHASHED_AI_GATE_DIAGNOSTIC", "started_at_utc": started,
              "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "labels": ["AI_LABELLED_NOT_BLIND", "DIAGNOSTIC", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"],
              "scientific_gate_pass": False, "n_cases": len(records), "by_origin": dict(Counter(r["origin"] for r in records)),
              "input_sha256": {str(args.manifest): sha(args.manifest), **manifest["files"]},
              "metrics": results, "branch_accuracy": rate(sum(r["gold_branch"] == r["router_branch"] for r in records), len(records)),
              "branch_confusion": [{"gold": a, "predicted": b, "count": n} for (a, b), n in sorted(confusion.items())],
              "records": records, "no_runtime_or_d5_change": True,
              "limitations": ["AI-authored labels with knowledge of project/rules; prehash timing does not make labels blind or independent.",
                              "Five frozen D5 X controls are included post-hoc and reported as known controls, not a new D5 test or tune set.",
                              "Authored category counts are deliberate, not natural-query prevalence. Wilson intervals are conditional descriptive intervals.",
                              "Relevance means process-effect reasoning is needed; static metadata/lookup, retrieval, safety referral and navigation are negative.",
                              "No gate threshold, rule, scorer, frozen result or model has been altered. A new diagnostic cannot repair original scientific gates."]}
    with args.out.open("x") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v["counts"] for k, v in results.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
