#!/usr/bin/env python3
"""Summarise X8 encoder NER runs (gpu/ner_tasteset/runs/*.json) against the rule floor on the same test split.

  /opt/anaconda3/bin/python tools/summarise_ner_runs.py
Model choice uses mean DEV micro exact F1 over seeds; test numbers are reported for every model but never used to
choose. "Beats the floor" = the selected model's 5-seed mean test F1 is above the floor's 95% CI upper bound.
Writes reports/ner/tasteset_encoders_v1.md/json.
"""
import json
import statistics as stats
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "gpu" / "ner_tasteset" / "runs"


def main() -> None:
    runs = [json.loads(p.read_text()) for p in sorted(RUNS.glob("*_seed*.json"))]
    if not runs:
        sys.exit(f"no runs in {RUNS}")
    floor = json.loads((ROOT / "reports" / "ner" / "tasteset_rule_baseline.json").read_text())
    f_ci = floor["test_split_micro_exact_f1_ci"]
    by = defaultdict(list)
    for r in runs:
        by[r["model"]].append(r)
    rows = {}
    for m, rs in by.items():
        ex = [r["test"]["exact"]["micro"]["f1"] for r in rs]
        rel = [r["test"]["relaxed"]["micro"]["f1"] for r in rs]
        devs = [r["best_dev_micro_exact_f1"] for r in rs]
        labels = sorted(rs[0]["test"]["exact"]["per_label"])
        rows[m] = {"seeds": len(rs), "dev_mean": round(stats.mean(devs), 4),
                   "test_exact_mean": round(stats.mean(ex), 4), "test_exact_sd": round(stats.pstdev(ex), 4),
                   "test_relaxed_mean": round(stats.mean(rel), 4),
                   "per_label_exact": {lab: round(stats.mean(r["test"]["exact"]["per_label"][lab]["f1"] for r in rs), 4)
                                       for lab in labels},
                   "minutes_per_run": round(stats.mean(r["minutes"] for r in rs), 1)}
    best = max(rows, key=lambda m: rows[m]["dev_mean"])
    verdict = "BEATS_FLOOR" if rows[best]["test_exact_mean"] > f_ci["high"] else "NOT_SEPARATED"
    res = {"selected_on_dev": best, "verdict": verdict, "floor_test_ci": f_ci, "models": rows}
    out = ROOT / "reports" / "ner"
    (out / "tasteset_encoders_v1.json").write_text(json.dumps(res, indent=1))
    labels = sorted(next(iter(rows.values()))["per_label_exact"])
    lines = ["# TASTEset encoder NER v1 (X8)", "",
             f"Same recipe split as the rule floor (test {runs[0]['n']['test']} recipes). Selected on DEV: **{best}**. "
             f"Rule floor test exact F1 {floor['test_split']['exact']['micro']['f1']} "
             f"(95% CI {f_ci['low']}–{f_ci['high']}). Verdict: **{verdict}**.", "",
             "| model | seeds | dev F1 | test exact F1 (mean ± sd) | test relaxed F1 | min/run |", "|---|---|---|---|---|---|"]
    lines += [f"| {m} | {r['seeds']} | {r['dev_mean']} | {r['test_exact_mean']} ± {r['test_exact_sd']} | "
              f"{r['test_relaxed_mean']} | {r['minutes_per_run']} |" for m, r in sorted(rows.items())]
    lines += ["", "| label | " + " | ".join(m.split("/")[-1] for m in sorted(rows)) + " | rule floor (all 700) |",
              "|---|" + "---|" * (len(rows) + 1)]
    lines += [f"| {lab} | " + " | ".join(str(rows[m]["per_label_exact"][lab]) for m in sorted(rows)) +
              f" | {floor['exact']['per_label'].get(lab, {}).get('f1')} |" for lab in labels]
    (out / "tasteset_encoders_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
