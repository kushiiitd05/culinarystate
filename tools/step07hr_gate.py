#!/usr/bin/env python3
"""STEP 07H-R automated gate: all tests + 4,414 scientific-condition regression + recipe-base validators + ledger integrity + TWO complete deterministic rebuilds.
Prereq: tools/build_gold_index.py, tools/build_recipe_base.py, tools/step07hr_finalize.py already run. -> reports/step07/step07hr_gate_result.json"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = "/opt/anaconda3/bin/python"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
GROUPS = {"condition_unit_schema_golden_bound_trajectory_property_dialect": ["tests/unit/test_condition_units.py", "tests/unit/test_condition_normalizer.py", "tests/unit/test_condition_dialect.py", "tests/unit/test_condition_schema.py",
                                                                         "tests/unit/test_condition_golden.py", "tests/unit/test_condition_open_bounds.py", "tests/unit/test_condition_trajectory.py", "tests/unit/test_condition_properties.py"],
          "recipe_probe": ["tests/unit/test_recipe_probe.py"], "recipe_base_integrity_gold_silver_family_reference": ["tests/unit/test_recipe_base_integrity.py"], "step07_other": ["tests/unit/test_step07_agreement.py", "tests/unit/test_evd_export.py", "tests/unit/test_es12_registries.py"]}
OUT = ["ledgers/recipe_base/recipe_base_v1{s}.parquet", "ledgers/recipe_base/recipe_simulation_readiness_v1{s}.parquet", "ledgers/recipe_semantics/recipe_expression_probe_v1{s}.parquet", "ledgers/recipe_semantics/recipe_condition_mentions_v1{s}.parquet",
       "ledgers/recipe_semantics/recipe_ingredient_mentions_v1{s}.parquet", "ledgers/recipe_semantics/recipe_quantity_mentions_v1{s}.parquet", "ledgers/recipe_semantics/recipe_process_mentions_v1{s}.parquet", "registry/recipe_condition_surface_forms_v1{s}.csv",
       "registry/recipe_quantity_surface_forms_v1{s}.csv", "registry/recipe_temporal_surface_forms_v1{s}.csv", "registry/recipe_process_surface_forms_v1{s}.csv"]


def pytest(files):
    p = subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", *files], cwd=ROOT, capture_output=True, text=True)
    c = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|error|skipped)", p.stdout)}
    return c | {"returncode": p.returncode}


def main():
    skip_det = "--skip-determinism" in sys.argv
    res = {k: pytest(v) for k, v in GROUPS.items()}
    reg = subprocess.run([PY, "tools/step07h_regression.py"], cwd=ROOT, capture_output=True, text=True)
    r = json.loads((ROOT / "reports/step07/step07h_regression_audit.json").read_text())
    a = json.loads((ROOT / "reports/step07/step07h_full_recipe_base_audit.json").read_text())
    det = {"ran": False}
    if not skip_det:
        subprocess.run([PY, "tools/build_recipe_base.py", "--procs", "4", "--suffix", "_det2"], cwd=ROOT, capture_output=True, text=True)
        same = {}
        for t in OUT:
            m, d = ROOT / t.format(s=""), ROOT / t.format(s="_det2")
            same[t.format(s="")] = bool(m.exists() and d.exists() and sha(m) == sha(d))
        det = {"ran": True, "byte_identical_per_artifact": same, "all_identical": all(same.values())}
        for t in OUT:
            (ROOT / t.format(s="_det2")).unlink(missing_ok=True)
        (ROOT / "reports/step07/_recipe_build_stats_det2.json").unlink(missing_ok=True)
    import csv
    ab = [x for x in csv.DictReader(open(ROOT / "registry/source_dialect_mapping_registry_v1.csv")) if x["field"] == "source_abbreviation"]
    promoted = [x["raw_pattern"] for x in ab if x["status"] != "UNVERIFIED" or x["canonical_target"]]
    gates = {"G1_tests_pass_no_unexplained_failures": all(v["returncode"] == 0 for v in res.values()), "G2_4414_condition_regression_0_unexplained": r["evd_coverage_ok"] and r["unexplained_field_changes"] == 0 and r["ledgers_byte_identical"],
             "G3_recipe_base_validators_all_pass": a["validators_all_pass"], "G4_scientific_and_vocab_ledgers_byte_identical": all(a["scientific_and_vocab_ledgers_byte_identical"].values()),
             "G5_two_complete_rebuilds_deterministic": det.get("all_identical", None) if det["ran"] else None, "G6_no_unsupported_abbreviation_promoted": not promoted,
             "G7_no_bulk_gold_promotion": a["totals"]["tier_totals"].get("DEEP_GOLD", 0) == 0 and a["totals"]["tier_totals"].get("GOLD_LIGHT", 0) == 0}
    out = {"gates": gates, "all_pass": all(v is True for v in gates.values()), "test_groups": res, "determinism": det, "regression": {k: r[k] for k in ("conditions_audited", "evd_references_covered", "fields_compared", "fields_changed", "unexplained_field_changes")}}
    (ROOT / "reports/step07/step07hr_gate_result.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1)[:2500])


if __name__ == "__main__":
    main()
