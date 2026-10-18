#!/usr/bin/env python3
"""DEL-2 one-command runner: cells -> splits -> D0–D7 -> metrics + CIs + conformal + MNAR diagnostics.

  /opt/anaconda3/bin/python tools/run_del2.py --source USDA-RETN-R6 [--seed 7] [--n-boot 300]
Outputs reports/del2/<source>_results.json and .md. CPU only (seconds–minutes).
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.transition.baselines import all_models, log_models  # noqa: E402
from culinarystate.transition.dataset import build_cells  # noqa: E402
from culinarystate.transition.evaluate import evaluate, propensity_weights  # noqa: E402
from culinarystate.transition.splits import all_splits, leakage  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--source", default="USDA-RETN-R6")
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--n-boot", type=int, default=300)
ap.add_argument("--log-target", action="store_true", help="fit models on log(RF); report RF-scale + log errors")
a = ap.parse_args()

t0 = time.time()
cells = build_cells(LedgerStore(), a.source)
df = cells.df
splits, notes = all_splits(df, a.seed)
_, mnar = propensity_weights(df, df.head(5))
results = []
for s in splits:
    leak = leakage(df, s, ["matrix", "process", "target"])
    for m in (log_models() if a.log_target else all_models()):
        r = evaluate(df, s, m, n_boot=a.n_boot)
        r["leakage_test_seen_in_train"] = leak
        r["split_sha256"] = s.sha256()[:16]
        results.append(r)
        print(f"{s.name:16s} {m.name:32s} MAE={r['mae_censor_aware']:.4f} "
              f"[{r['mae_ci']['low']}, {r['mae_ci']['high']}] IPW={r['mae_ipw']:.4f} "
              f"MedAE={r['median_ae']:.4f} logMAE={r['mae_log_observed']} cov90={r['conformal_90']['coverage']}", flush=True)
tag = a.source + ("_log" if a.log_target else "")
summary = {"source_family": a.source, "log_target": a.log_target, "seed": a.seed, "rows": len(df), "censored": int(df["censored"].sum()),
           "matrices": df["matrix"].nunique(), "processes": df["process"].nunique(), "targets": df["target"].nunique(),
           "mnar": mnar, "notes": notes + ["D6 TabPFN: SKIPPED (not installed; GPU)",
                                           "censored rows trained at lower bound 0.975 (assumption)",
                                           "conformal coverage is empirical (AH4)"],
           "runtime_s": round(time.time() - t0, 1), "results": results}
out = ROOT / "reports" / "del2"
out.mkdir(parents=True, exist_ok=True)
(out / f"{tag}_results.json").write_text(json.dumps(summary, indent=1, default=str))
lines = [f"# DEL-2 baselines — {a.source} (seed {a.seed}){' — log-RF target' if a.log_target else ''}", "",
         f"rows {len(df):,} (censored {summary['censored']:,}); matrices {summary['matrices']}, process signatures "
         f"{summary['processes']}, targets {summary['targets']}; grid density {mnar.get('density')}, "
         f"propensity AUC {mnar.get('propensity_auc')}", "", *[f"- {n}" for n in summary["notes"]], "",
         "| split | model | MAE (censor-aware) | 95% CI (grouped) | median AE | MAE log (obs) | MAE IPW | conformal-90 cov / width |",
         "|---|---|---|---|---|---|---|---|"]
for r in results:
    c = r["conformal_90"]
    lines.append(f"| {r['split']} | {r['model']} | {r['mae_censor_aware']:.4f} | [{r['mae_ci']['low']}, "
                 f"{r['mae_ci']['high']}] | {r['median_ae']} | {r['mae_log_observed']} | {r['mae_ipw']:.4f} | "
                 f"{c['coverage']} / {c['width']} |")
(out / f"{tag}_results.md").write_text("\n".join(lines) + "\n")
print(f"done in {summary['runtime_s']} s -> reports/del2/{tag}_results.md")
