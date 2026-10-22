#!/usr/bin/env python3
"""Step 07H automated hardening gate -> reports/step07/step07h_normalizer_hardening_report.md (+ gate json). Runs the test groups, the current-data regression, and the freeze checks."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = "/opt/anaconda3/bin/python"
GROUPS = [("1 unit tests (units, normalizer, dialect, agreement tool)", ["tests/unit/test_condition_units.py", "tests/unit/test_condition_normalizer.py", "tests/unit/test_condition_dialect.py", "tests/unit/test_step07_agreement.py"]),
          ("2 schema tests", ["tests/unit/test_condition_schema.py"]), ("3 golden syntax cases", ["tests/unit/test_condition_golden.py"]),
          ("4 inequality / open-bound tests", ["tests/unit/test_condition_open_bounds.py"]), ("5 trajectory tests", ["tests/unit/test_condition_trajectory.py"]), ("6 property-based tests (Hypothesis, 300 examples each)", ["tests/unit/test_condition_properties.py"])]


def run(files):
    p = subprocess.run([PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", *files], cwd=ROOT, capture_output=True, text=True)
    m = re.findall(r"(\d+) (passed|failed|error)", p.stdout)
    return {k: int(v) for v, k in m} | {"returncode": p.returncode}


def main():
    res = {name: run(f) for name, f in GROUPS}
    reg = subprocess.run([PY, "tools/step07h_regression.py"], cwd=ROOT, capture_output=True, text=True)
    r = json.loads((ROOT / "reports/step07/step07h_regression_audit.json").read_text())
    # two complete rebuilds of the human packet must be byte-identical
    hs = []
    for _ in range(2):
        subprocess.run([PY, "tools/step07_build_audit_packet.py"], cwd=ROOT, capture_output=True, text=True)
        hs.append(hashlib.sha256((ROOT / "annotation/condition_audit/condition_audit_packet_100_v3_Kush.csv").read_bytes()).hexdigest())
    d3 = json.loads((ROOT / "registry/source_dialect_mapping_registry_v1.csv").read_text()) if False else None
    import csv
    ab = [x for x in csv.DictReader(open(ROOT / "registry/source_dialect_mapping_registry_v1.csv")) if x["field"] == "source_abbreviation"]
    promoted = [x["raw_pattern"] for x in ab if x["status"] != "UNVERIFIED" or x["canonical_target"]]
    gates = {"G1_unit_tests_pass": res[GROUPS[0][0]]["returncode"] == 0, "G2_schema_tests_pass": res[GROUPS[1][0]]["returncode"] == 0, "G3_golden_pass": res[GROUPS[2][0]]["returncode"] == 0,
             "G4_open_bound_pass": res[GROUPS[3][0]]["returncode"] == 0, "G5_trajectory_pass": res[GROUPS[4][0]]["returncode"] == 0, "G6_property_pass": res[GROUPS[5][0]]["returncode"] == 0,
             "G7_current_data_regression_completed_4414_17978": r["evd_coverage_ok"] and reg.returncode == 0 and r["unexplained_field_changes"] == 0, "G8_source_ledgers_byte_identical": r["ledgers_byte_identical"],
             "G9_deterministic_two_rebuilds": r["audit_deterministic_over_two_rebuilds"] and hs[0] == hs[1], "G10_no_unsupported_abbreviation_promoted": not promoted}
    out = {"gates": gates, "all_pass": all(gates.values()), "test_groups": res, "packet_v3_sha256_two_rebuilds": hs, "fingerprint": r["normalizer_fingerprint"], "promoted_abbreviations": promoted}
    (ROOT / "reports/step07/step07h_gate_result.json").write_text(json.dumps(out, indent=1))
    L = ["# Step 07H -- normalizer production hardening: automated gate", "", f"**Overall: {'PASS' if out['all_pass'] else 'FAIL'}**  (normalizer `{r['normalizer_fingerprint']['normalizer_version']}`, combined hash `{r['normalizer_fingerprint']['combined_sha256']}`)", "", "| gate | result |", "|---|---|"]
    L += [f"| {k} | {'PASS' if v else 'FAIL'} |" for k, v in gates.items()]
    L += ["", "## Test counts", ""] + [f"- {k}: {v}" for k, v in res.items()]
    L += ["", "## Current-data regression (4,414 conditions / 17,978 EVD references)", "", f"- fields compared {r['fields_compared']}; unchanged {r['fields_unchanged']}; changed {r['fields_changed']}; **unexplained {r['unexplained_field_changes']}**",
          "- every change, by cause:"] + [f"  - {v['n']} x {k}" for k, v in r["transitions"].items()]
    L += [f"- audit count sections changed vs pre-07H: {list(r['count_section_differences']) or 'none'}; reason-count changes: {r['reason_count_differences'] or 'none'}", f"- ledgers byte-identical: {r['ledgers_byte_identical']}; audit deterministic over two rebuilds: {r['audit_deterministic_over_two_rebuilds']}"]
    (ROOT / "reports/step07/step07h_normalizer_hardening_report.md").write_text("\n".join(L) + "\n")
    print(json.dumps(gates, indent=1), out["all_pass"])
    print(res)


if __name__ == "__main__":
    main()
