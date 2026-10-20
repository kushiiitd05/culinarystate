#!/usr/bin/env python3
"""S118 Part III: freeze the semantic NER benchmark v1 (splits, label views, metrics, seeds, selection/statistics/Pareto rules).

  /opt/anaconda3/bin/python tools/freeze_ner_benchmark.py          # writes benchmark/ner/*, refuses to overwrite a frozen benchmark
Splits are index lists (text-free). No model output is read. Re-running on the same data reproduces identical hashes.
"""
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ner import benchmark as B  # noqa: E402

OUT = ROOT / "benchmark" / "ner"
RDB3 = ROOT / "data" / "external" / "recipedb3_ner" / "Ingredient_Annotated_Dataset.csv"
TASTE = ROOT / "gpu" / "ner_tasteset" / "TASTEset.csv"
KNOWN = {"NAME", "QUANTITY", "UNIT", "STATE", "TEMP", "DF", "SIZE"}


def sha(path_or_bytes):
    b = path_or_bytes if isinstance(path_or_bytes, bytes) else Path(path_or_bytes).read_bytes()
    return hashlib.sha256(b).hexdigest()


def load_rdb3():
    df = pd.read_csv(RDB3).dropna()
    df = df[df.sentence.astype(str).str.strip() != ""].reset_index(drop=True)
    df["tags"] = df.tags.astype(str)
    ok = df.apply(lambda r: len(r.sentence.split()) == len(r.tags.split()), axis=1)
    return df[ok].reset_index(drop=True), int((~ok).sum())


def docs_rdb3(df, idx):
    out = []
    for i in idx:
        w = df.sentence[i].split()
        out.append(B.words_to_spans(w, B.tags_to_bio(df.tags[i].split(), KNOWN)))
    return out


def docs_taste(df, idx):
    return [(df.ingredients[i], [(e["start"], e["end"], e["type"]) for e in json.loads(df.ingredients_entities[i])]) for i in idx]


def diag(name, splits, docs_fn, view_labels, fam_fn):
    d = {k: docs_fn(v) for k, v in splits.items() if k in ("train", "calibration", "dev", "test")}
    counts = B.surface_counts(d["train"])
    fams = {k: {fam_fn(i) for i in splits[k]} for k in d}
    res = {"counts": {k: len(v) for k, v in splits.items()},
           "group_overlap_with_train": {k: len(fams[k] & fams["train"]) for k in ("calibration", "dev", "test")},
           "group_overlap_dev_test": len(fams["dev"] & fams["test"])}
    ts = Counter()
    for text, spans in d["test"]:
        for s, e, lab in spans:
            if lab in view_labels:
                ts[B.stratum(lab, text[s:e], counts)] += 1
    res["test_gold_strata"] = dict(ts)
    res["test_gold_entities"] = sum(ts.values())
    return res


def main():
    if (OUT / "semantic_benchmark_v1.json").exists():
        sys.exit("benchmark v1 is frozen; create v2 instead of overwriting")
    df, skipped = load_rdb3()
    rs = B.split_recipedb3(df.sentence.tolist())
    td = pd.read_csv(TASTE)
    ts = B.split_tasteset(td.ingredients.tolist())
    spl = OUT / "splits"
    spl.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, s, data in (("recipedb3", rs, df.sentence.tolist()), ("tasteset", ts, td.ingredients.tolist())):
        body = {"split_version": B.SALT, "groups": "masked-sentence family" if name == "recipedb3" else "recipe (+ identical-text quarantine)",
                "indices": s, "row_hash": {k: hashlib.sha256("\n".join(data[i] for i in v).encode()).hexdigest() for k, v in s.items()}}
        p = spl / f"{name}_split_v1.json"
        p.write_text(json.dumps(body, indent=1) + "\n")
        files[name] = p
    d_r = diag("recipedb3", rs, lambda idx: docs_rdb3(df, idx), B.VIEWS["recipedb3_published"], lambda i: B.family(df.sentence[i]))
    d_t = diag("tasteset", ts, lambda idx: docs_taste(td, idx), B.VIEWS["tasteset_native"], lambda i: td.ingredients[i].lower().strip())
    d_r["skipped_len_mismatch"], d_t["quarantined_identical_recipes"] = skipped, len(ts["quarantined_duplicates"])
    spec = {
        "benchmark": "semantic_ner_v1", "frozen": "2026-10-20", "no_model_output_read": True,
        "datasets": {"recipedb3": {"file": str(RDB3.relative_to(ROOT)), "sha256": sha(RDB3), "licence": "CoSyLab/RecipeDB3 public notebook data; use per D-015 (ASSUMED / DERIVED_ONLY); text not redistributed here",
                                   "diagnostics": d_r},
                     "tasteset": {"file": str(TASTE.relative_to(ROOT)), "sha256": sha(TASTE), "licence": "MIT", "diagnostics": d_t}},
        "split_rules": {"recipedb3": "sha256 bucket of the masked-sentence family: test <0.10, dev <0.20, CALIBRATION <0.30, train rest",
                        "tasteset": "legacy recipe split (seed 7, 70/15/15); train recipes byte-identical to a dev/test recipe quarantined; 12.5% grouped CALIBRATION carved from train"},
        "calibration_split_rule": "never used to fit encoder, calibrator, aliases, gazetteer or linker; thresholds are set on CALIBRATION only; calibrators are fit out-of-fold on train (5-fold)",
        "dev_rule": "model/checkpoint selection only; " + B.CHECKPOINT_RULE,
        "train_only_statistics": "alias hits, surface frequencies, strata, gazetteers and linker indices are built from train; train-time features are 5-fold out-of-fold; test uses the full-train build; candidate spans (all n-grams <= 6 tokens) are generated before NER",
        "label_views": {k: sorted(v) for k, v in B.VIEWS.items()}, "label_adapter_to_core": B.ADAPTER_TO_CORE,
        "primary_views": {"recipedb3": "recipedb3_published", "tasteset": "tasteset_native"},
        "metrics": {"implementation": ["src/culinarystate/ner/benchmark.py", "src/culinarystate/scoring/metrics.py", "src/culinarystate/scoring/calibration.py"],
                    "list": ["exact micro F1", "exact macro F1", "per-label F1", "relaxed span F1", "boundary error rate", "type error rate", "FOOD/NAME F1",
                             "SIZE", "QUANTITY", "UNIT", "FORM/STATE (STATE, DF)", "head/mid/tail/unseen surface F1 (train counts; head>=20, tail<=4)",
                             "seen/unseen alias F1", "ECE/Brier/AURC/selective risk", "runtime", "peak GPU memory"],
                    "hash_of_code": {f: sha(ROOT / f) for f in ("src/culinarystate/ner/benchmark.py", "src/culinarystate/scoring/metrics.py", "src/culinarystate/scoring/calibration.py")}},
        "seeds": list(B.SEEDS), "seed_semantics": "model-initialisation/shuffle seeds only; the split never changes",
        "training_budget": {"epochs": 15, "batch_size": 16, "max_len": 128, "lr_base": 5e-5, "lr_large": 2e-5, "optimizer": "AdamW", "note": "same budget for every encoder"},
        "checkpoint_selection": B.CHECKPOINT_RULE, "statistics": B.STATS_RULE, "pareto_promotion_rule": B.PARETO_RULE,
        "router": {"scores": ["entity", "link"], "outputs": ["ACCEPT", "REVIEW", "NOVEL(NIL)", "REJECT"],
                   "thresholds": "set by risk control on CALIBRATION so ACCEPT-set error <= epsilon, stratified by label and line type; epsilon declared before the first run: 0.02"},
        "fusion_guards": {"metadata_dropout": 0.3, "gate_bias_init": "g ~ 1", "warm_start": "encoder+CRF checkpoint", "feature_roles": "encoder confidence/entropy are calibrator-only (excluded from fusion inputs)"},
        "claims_policy": "no SOTA / superiority claim before H6; no test-set model selection; benchmark is not modified after any candidate sees test"}
    sp = OUT / "semantic_benchmark_v1.json"
    sp.write_text(json.dumps(spec, indent=1) + "\n")
    rows = [("semantic_benchmark_v1.json", sp), ("recipedb3_split_v1.json", files["recipedb3"]), ("tasteset_split_v1.json", files["tasteset"]),
            ("benchmark.py", ROOT / "src/culinarystate/ner/benchmark.py"), ("metrics.py", ROOT / "src/culinarystate/scoring/metrics.py"),
            ("calibration.py", ROOT / "src/culinarystate/scoring/calibration.py"), ("recipedb3_data", RDB3), ("tasteset_data", TASTE)]
    with (OUT / "semantic_benchmark_manifest.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["artifact", "path", "sha256", "bytes"])
        for n, p in rows:
            w.writerow([n, str(p.relative_to(ROOT)), sha(p), p.stat().st_size])
    print(json.dumps({"recipedb3": d_r, "tasteset": d_t}, indent=1))


if __name__ == "__main__":
    main()
