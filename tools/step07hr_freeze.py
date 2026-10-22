#!/usr/bin/env python3
"""STEP 07H-R freeze manifest: commit SHA + code/schema/registry/ledger hashes. Run AFTER the gate passes and the code/registries are committed.
Any later change to a listed file invalidates the human audit (verify with --verify)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
sha = lambda p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
CODE = ["src/culinarystate/evidence/condition_parser.py", "src/culinarystate/evidence/condition_normalizer.py", "src/culinarystate/evidence/condition_units.py", "src/culinarystate/evidence/source_dialect.py", "src/culinarystate/recipes/corpus.py",
        "src/culinarystate/recipes/probe.py", "src/culinarystate/recipes/ledgers.py", "tools/build_recipe_base.py", "tools/build_gold_index.py", "tools/step07hr_finalize.py"]
SCHEMA = ["registry/schemas/condition_value_v1.schema.json"]
REGS = ["registry/condition_variable_registry_v1.csv", "registry/condition_variable_bounds_registry_v1.csv", "registry/notation_rule_registry_v1.csv", "registry/source_dialect_mapping_registry_v1.csv", "registry/recipe_location_cues_v1.csv",
        "registry/recipe_quality_tier_registry_v1.csv", "registry/recipe_condition_surface_forms_v1.csv", "registry/recipe_quantity_surface_forms_v1.csv", "registry/recipe_temporal_surface_forms_v1.csv", "registry/recipe_process_surface_forms_v1.csv"]
PARQ = ["ledgers/recipe_base/recipe_base_v1.parquet", "ledgers/recipe_base/gold_recipe_index_v1.parquet", "ledgers/recipe_base/recipe_simulation_readiness_v1.parquet", "ledgers/recipe_base/vocab_corpus_frequency_v1.parquet", "ledgers/recipe_semantics/recipe_expression_probe_v1.parquet",
        "ledgers/recipe_semantics/recipe_condition_mentions_v1.parquet", "ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet", "ledgers/recipe_semantics/recipe_quantity_mentions_v1.parquet", "ledgers/recipe_semantics/recipe_process_mentions_v1.parquet"]
TESTS = ["tests/golden/condition_syntax_golden_v1.json"]


def build():
    from culinarystate.evidence import condition_normalizer as N
    import build_recipe_base as B
    schema_hash = hashlib.sha256(json.dumps({k: [(n, str(t)) for n, t in getattr(B, k)] for k in ("BASE_SCHEMA", "EXPR_SCHEMA", "ING_SCHEMA", "QTY_SCHEMA", "PROC_SCHEMA", "READY_SCHEMA")}, sort_keys=True).encode()).hexdigest()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *CODE, *SCHEMA, *REGS, *TESTS], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    import pyarrow.parquet as pq
    art = {p: {"bytes": (ROOT / p).stat().st_size, "rows": (pq.ParquetFile(ROOT / p).metadata.num_rows if p.endswith(".parquet") else None)} for p in PARQ + REGS if (ROOT / p).exists()}
    return {"artifact_manifest": art, "frozen": True, "freeze_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "uncommitted_among_frozen_files": dirty or None, "condition_normalizer_fingerprint": N.fingerprint(),
            "code_sha256": {p: sha(p) for p in CODE}, "condition_schema_sha256": {p: sha(p) for p in SCHEMA}, "registry_sha256": {p: sha(p) for p in REGS}, "recipe_base_schema_sha256": schema_hash, "golden_suite_sha256": {p: sha(p) for p in TESTS},
            "ledger_parquet_sha256": {p: sha(p) for p in PARQ}, "rule": "any change to these files after reviewers start invalidates the human audit; python tools/step07hr_freeze.py --verify"}


if __name__ == "__main__":
    cur = build()
    f = ROOT / "reports/step07/step07hr_freeze_manifest.json"
    if "--verify" in sys.argv:
        old = json.loads(f.read_text())
        bad = [k for k in ("code_sha256", "condition_schema_sha256", "registry_sha256", "recipe_base_schema_sha256", "golden_suite_sha256", "ledger_parquet_sha256") if old[k] != cur[k]]
        print("FREEZE INTACT" if not bad and old["condition_normalizer_fingerprint"]["combined_sha256"] == cur["condition_normalizer_fingerprint"]["combined_sha256"] else f"FREEZE BROKEN: {bad}")
    else:
        f.write_text(json.dumps(cur, indent=1))
        print(cur["freeze_commit"], cur["condition_normalizer_fingerprint"]["combined_sha256"], cur["uncommitted_among_frozen_files"])
