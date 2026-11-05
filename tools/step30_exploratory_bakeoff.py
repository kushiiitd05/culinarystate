"""Step 30 EXPLORATORY bake-off on the 17,978 ES-1.1 evidence rows. DIAGNOSTIC_ONLY, not a gate.

Runs the S160 bake-off scaffold (culinarystate.evaluation) on measured retention values with three simple
rungs, an 80/20 group-aware split on independence_group and a paired cluster bootstrap. The split seed,
margin and resample settings were chosen by the agent for an exploratory look at Parv's request (2026-11-04);
they are NOT pre-registered, so nothing here is a result for a claim. Counts, medians and errors only; no
row ids or text are written. Refuses to overwrite its output.
"""
import json, statistics, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evaluation import bakeoff as B  # noqa: E402
from culinarystate.evaluation.splits import group_aware_split  # noqa: E402

OUT = ROOT / "reports/step30/exploratory_bakeoff_counts.json"
SPLIT_SEED, BOOT_SEED = "exploratory-split-2026-11-04", "exploratory-boot-2026-11-04"
MARGIN, N_RES, CONF = 0.0, 2000, 0.95


def load_rows():
    latest = {}
    with open(ROOT / "ledgers/data/EVD.jsonl") as f:
        for line in f:
            r = json.loads(line)
            if r["id"] not in latest or r["version"] > latest[r["id"]]["version"]:
                latest[r["id"]] = r
    rows = []
    for r in latest.values():
        if r.get("status") != "ACTIVE":
            continue
        rf = (r.get("derived") or {}).get("retention_factor") or {}
        if rf.get("status") != "MEASURED" or not isinstance(rf.get("value"), (int, float)):
            continue
        y = rf["value"] / 100.0 if rf.get("unit") == "%" else float(rf["value"])
        steps = (r.get("process") or {}).get("steps") or []
        rows.append({"id": r["id"], "grp": r["independence_group"], "y": y,
                     "nutrient": (r.get("target") or {}).get("raw_name") or "?",
                     "process": steps[0] if steps else "?"})
    return len(latest), rows


def med_fit(keyf, fallback_fit=None):
    def fit(train):
        by = defaultdict(list)
        for r in train:
            by[keyf(r)].append(r["y"])
        glob = statistics.median(r["y"] for r in train)
        fb = fallback_fit(train) if fallback_fit else None
        m = {k: statistics.median(v) for k, v in by.items()}
        return lambda r: m.get(keyf(r), fb(r) if fb else glob)
    return fit


def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    n_latest, rows = load_rows()
    d0 = med_fit(lambda r: "ALL")
    d1 = med_fit(lambda r: r["nutrient"], d0)
    d2 = med_fit(lambda r: (r["nutrient"], r["process"]), d1)
    reg = B.ModelRegistry()
    for mid, rung, desc, fit in (("D0", "D0", "global median", d0), ("D1", "D1", "median by nutrient", d1),
                                 ("D2", "D2", "median by nutrient x first process step", d2)):
        reg.register(B.ModelSpec(mid, rung, desc, fit))
    manifest = reg.freeze()
    split = group_aware_split(rows, id_column="id", group_columns=["grp"],
                              role_fractions={"TRAIN": "4/5", "TEST": "1/5"}, seed=SPLIT_SEED, remainder_role="TRAIN")
    losses = B.evaluate(reg, split, rows, id_column="id", target=lambda r: r["y"],
                        loss=lambda t, p: abs(t - p), train_role="TRAIN", test_role="TEST")
    by_grp = {r["id"]: r["grp"] for r in rows}
    clusters = {i: by_grp[i] for i in losses["D0"]}
    comps = {}
    for base, chal in (("D0", "D1"), ("D1", "D2"), ("D0", "D2")):
        c = B.paired_cluster_bootstrap(losses[base], losses[chal], clusters, margin=MARGIN, n_resamples=N_RES,
                                       confidence=CONF, seed=BOOT_SEED, weighting="CLUSTER")
        comps[f"{base}->{chal}"] = c.as_record()
    test_groups = sorted({g.split(":")[0] if g.startswith("pe_pub") else g for g in clusters.values()})
    out = {"label": "EXPLORATORY_DIAGNOSTIC_ONLY", "not_preregistered": True, "evd_latest_rows": n_latest,
           "measured_rows_used": len(rows), "loss": "absolute error on retention fraction",
           "registry_manifest_sha256": manifest["sha256"], "split": split.manifest(),
           "test_source_families": sorted({"PE" if g.startswith("pe_pub") else g for g in clusters.values()}),
           "mae_test": {m: sum(v.values()) / len(v) for m, v in losses.items()},
           "paired_comparisons": comps, "contains_ids": False, "contains_text": False}
    OUT.parent.mkdir(exist_ok=True)
    json.dump(out, open(OUT, "x"), indent=1, sort_keys=True)
    print(json.dumps({"rows": len(rows), "n_rows": split.n_rows, "n_components": split.n_components,
                      "families": out["test_source_families"], "mae": out["mae_test"],
                      "cmp": {k: [round(v["estimate"], 4), round(v["lower"], 4), round(v["upper"], 4), v["verdict"]]
                              for k, v in comps.items()}}))


main()
