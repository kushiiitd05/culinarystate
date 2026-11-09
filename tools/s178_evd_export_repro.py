#!/usr/bin/env python3
"""S178 EVD lane, T2-C01-R2 (+ T2-C15-R4): is the EVD export v1 / v2 (08a.7) byte-reproducible after the last ledger state?

Rebuilds, in SCRATCH directories only (nothing is written under ledgers/ or exports/):
  * EVD export v1 rows (``culinarystate.evidence.evd_export.build_export``), the matrix and prior-state tables;
  * EVD export v2 twice (``tools/step08a_export_v2.py`` as a subprocess, two fresh scratch dirs, committed keys file).
It compares every sha256 with the recorded manifests (``exports/evd/evd_export_v1.manifest.json``,
``exports/lineage/step08a_v1/evd_export_v2.manifest.json``, ``freeze_manifest.json``), checks that the protected ledgers
(EVD, COND, SRC, MEAS, SNAP) are byte-identical before and after and equal to the recorded baseline, and that the ledgers
the keys file was built from still have the recorded hashes. The keys builder (tools/step08a_build_keys.py) is
hard-wired to a Mac scratch root and refuses repo roots, so keys.jsonl is verified by hash, not rebuilt.

Cross-platform finding (S178): on this Linux / glibc host ``math.log`` differs from the correctly rounded value in the last
digit for 4 of the 15,290 log evaluations, so the rebuilt v1 / v2 bytes differ from the Mac-recorded sha256 in exactly those
``log_fold_change`` cells. The tool proves it by rebuilding once with a correctly rounded ``log`` (``decimal``): that build
equals the recorded v1 and v2 sha256. The builder is not changed here (a human decides; see the report).

  python tools/s178_evd_export_repro.py [--out-dir reports/s178/evd] [--scratch DIR]

Deterministic output (no timestamp, no scratch path). Status: AI_DRAFTED / PROPOSED. Counts and hashes only.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s178_evd_common import (DEFAULT_OUT, ROOT, dumps, md_table, protected_hashes, sha256_bytes,  # noqa: E402
                             sha256_file, write_new_or_same)

TOOL_VERSION = "s178-evd-export-repro-0.1.0-draft"
V1_MANIFEST = "exports/evd/evd_export_v1.manifest.json"
V2_DIR = "exports/lineage/step08a_v1"
V2_MANIFEST = f"{V2_DIR}/evd_export_v2.manifest.json"
FREEZE = f"{V2_DIR}/freeze_manifest.json"
BASELINE = "registry/baseline_ledger_hashes_08a_v1.csv"
KEYS = f"{V2_DIR}/keys.jsonl"
ALL_LEDGERS = ("EVD", "COND", "SRC", "MEAS", "SNAP", "SVAR", "PROC", "ING")
MATRIX_COLS = ["ingredient_id", "raw_name", "food_group", "variety", "part", "form", "prior_processing", "initial_state", "geometry", "storage_ripeness"]


def _csv_bytes(header: list[str], rows: list[list]) -> bytes:
    buf = io.StringIO(newline="")
    w = csv.writer(buf)  # same writer defaults as tools/build_evd_export_v1.py
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def _correctly_rounded_log(x):
    from decimal import Decimal, getcontext
    getcontext().prec = 60
    return float(Decimal(x).ln())


def build_rows(root: Path, neutral: bool):
    """-> (rows, matrix_table, prior_table, meta). neutral=True: evd_export.math.log is replaced by a correctly rounded log (this call only)."""
    import types
    from culinarystate.evidence import evd_export as X
    real = X.math
    if neutral:
        X.math = types.SimpleNamespace(log=_correctly_rounded_log, isfinite=real.isfinite)
    try:
        return X.build_export(root / "ledgers" / "data")
    finally:
        X.math = real


def neutral_variant(root: Path, glibc_rows: list) -> dict:
    from culinarystate.evidence.evd_export import canon_json
    from culinarystate.lineage.export_v2 import build_v2_rows, load_keys
    rows, _, _, _ = build_rows(root, neutral=True)
    v1 = sha256_bytes("".join(canon_json(r) + "\n" for r in rows).encode("utf-8"))
    v2 = sha256_bytes("".join(canon_json(r) + "\n" for r in build_v2_rows(rows, load_keys(root / KEYS))).encode("utf-8"))
    diff = [(a["evd_id"], k) for a, b in zip(rows, glibc_rows) for k in a if a[k] != b[k]]
    return {"v1_export_sha256": v1, "v2_export_sha256": v2, "differing_cells_vs_glibc_build": len(diff),
            "differing_columns": sorted({k for _, k in diff}), "differing_evd_ids": sorted({i for i, _ in diff})}


def v1_in_process(root: Path) -> dict:
    from culinarystate.evidence.evd_export import canon_json
    rows, mt, pt, meta = build_rows(root, neutral=False)
    body = "".join(canon_json(r) + "\n" for r in rows).encode("utf-8")
    matrix = _csv_bytes(["matrix_id"] + MATRIX_COLS, [[k] + [mt[k].get(x) for x in MATRIX_COLS] for k in sorted(mt)])
    prior = _csv_bytes(["prior_state_id", "initial_state_normalised", "prior_processing_normalised", "vocabulary_status"],
                       [[k, pt[k]["initial_state"], pt[k]["prior_processing"], "RAW_DESCRIPTOR_HASH (controlled vocabulary pending MP-5A/ES-1.x)"] for k in sorted(pt)])
    return {"rows": len(rows), "_rows": rows, "export_sha256": sha256_bytes(body), "matrix_table_sha256": sha256_bytes(matrix),
            "prior_state_table_sha256": sha256_bytes(prior), "ledger_sha256": meta["ledger_sha256"],
            "ledger_version_lines": meta["ledger_version_lines"], "ledger_ids_latest": meta["ledger_ids_latest"],
            "active_rows": meta["active_rows"]}


def v2_subprocess(root: Path, out: Path) -> dict:
    cmd = [sys.executable, str(root / "tools" / "step08a_export_v2.py"), "--ledgers", str(root / "ledgers"),
           "--keys", str(root / KEYS), "--out", str(out)]
    r = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("step08a_export_v2.py failed: " + r.stderr[-400:])
    man = json.loads((out / "evd_export_v2.manifest.json").read_text(encoding="utf-8"))
    return {"export_sha256": sha256_file(out / "evd_export_v2.jsonl"), "manifest": man,
            "manifest_sha256_raw": sha256_file(out / "evd_export_v2.manifest.json")}


def check(root: Path, scratch: Path) -> dict:
    before = {n: sha256_file(root / "ledgers" / "data" / f"{n}.jsonl") for n in ALL_LEDGERS}
    m1 = json.loads((root / V1_MANIFEST).read_text(encoding="utf-8"))
    m2 = json.loads((root / V2_MANIFEST).read_text(encoding="utf-8"))
    freeze = json.loads((root / FREEZE).read_text(encoding="utf-8"))
    baseline = {r["path"]: r["sha256"] for r in csv.DictReader(open(root / BASELINE, newline="", encoding="utf-8"))}

    v1 = v1_in_process(root)
    glibc_rows = v1.pop("_rows")
    neu = neutral_variant(root, glibc_rows)
    del glibc_rows
    run_a = v2_subprocess(root, scratch / "v2_run_a")
    run_b = v2_subprocess(root, scratch / "v2_run_b")

    def eq(a, b):
        return a == b

    mapping_now = sha256_file(root / "registry" / "svar_duplicate_mapping_v1.csv")
    v1c = {
        "rows_vs_recorded": [v1["rows"], m1["export_rows"], eq(v1["rows"], m1["export_rows"])],
        "export_sha256": {"rebuilt": v1["export_sha256"], "recorded": m1["export_sha256"], "equal": eq(v1["export_sha256"], m1["export_sha256"])},
        "matrix_table_sha256": {"rebuilt": v1["matrix_table_sha256"], "recorded": m1["matrix_table_sha256"], "committed_file": sha256_file(root / "exports/evd/evd_matrix_table_v1.csv"),
                                "equal": eq(v1["matrix_table_sha256"], m1["matrix_table_sha256"]) and eq(v1["matrix_table_sha256"], sha256_file(root / "exports/evd/evd_matrix_table_v1.csv"))},
        "prior_state_table_sha256": {"rebuilt": v1["prior_state_table_sha256"], "recorded": m1["prior_state_table_sha256"], "committed_file": sha256_file(root / "exports/evd/evd_prior_state_table_v1.csv"),
                                     "equal": eq(v1["prior_state_table_sha256"], m1["prior_state_table_sha256"]) and eq(v1["prior_state_table_sha256"], sha256_file(root / "exports/evd/evd_prior_state_table_v1.csv"))},
        "duplicate_mapping_sha256": {"current_file": mapping_now, "recorded": m1["mapping_sha256"], "equal": eq(mapping_now, m1["mapping_sha256"])},
        "ledger_version_lines_ids_active": {"rebuilt": [v1["ledger_version_lines"], v1["ledger_ids_latest"], v1["active_rows"]],
                                            "recorded": [m1["ledger_version_lines"], m1["ledger_ids_latest"], m1["active_rows"]]},
        "committed_jsonl_present_in_this_tree": (root / "exports/evd/evd_export_v1.jsonl").is_file(),
        "committed_jsonl_note": "exports/evd/evd_export_v1.jsonl is git-ignored (Mac only); the recorded manifest sha stands in for it",
    }
    v2c = {
        "export_sha256_run_a": run_a["export_sha256"], "export_sha256_run_b": run_b["export_sha256"],
        "run_a_equals_run_b": eq(run_a["export_sha256"], run_b["export_sha256"]),
        "recorded_export_sha256": m2["export_sha256"], "run_equals_recorded": eq(run_a["export_sha256"], m2["export_sha256"]) and eq(run_b["export_sha256"], m2["export_sha256"]),
        "export_rows": [run_a["manifest"]["export_rows"], run_b["manifest"]["export_rows"], m2["export_rows"]],
        "v1_regenerated_sha256_in_manifests": [run_a["manifest"]["v1_regenerated_sha256"], run_b["manifest"]["v1_regenerated_sha256"], m2["v1_regenerated_sha256"]],
        "v1_regenerated_equals_recorded_v1": all(x == m1["export_sha256"] for x in (run_a["manifest"]["v1_regenerated_sha256"], run_b["manifest"]["v1_regenerated_sha256"], m2["v1_regenerated_sha256"])),
        "v1_rows_checked_identical": [run_a["manifest"]["v1_rows_checked_identical"], run_b["manifest"]["v1_rows_checked_identical"], m2["v1_rows_checked_identical"]],
        "keys_file_sha256": {"current_file": sha256_file(root / KEYS), "in_rebuilt_manifest": run_a["manifest"]["keys_file_sha256"], "in_recorded_manifest": m2["keys_file_sha256"],
                             "in_freeze_manifest": freeze["keys.jsonl"]["sha256"]},
        "ledger_sha256_evd": {"current": before["EVD"], "in_rebuilt_manifest": run_a["manifest"]["ledger_sha256_evd"], "in_recorded_manifest": m2["ledger_sha256_evd"]},
        "added_columns_equal_recorded": run_a["manifest"]["added_columns"] == m2["added_columns"],
        "manifest_fields_differing_from_recorded": sorted(k for k in set(run_a["manifest"]) | set(m2)
                                                          if run_a["manifest"].get(k) != m2.get(k)),
        "manifest_difference_note": "only committed_v1 differs: the recorded manifest names the Mac copy of the (git-ignored) v1 jsonl, which is not in this tree",
        "export_v2_jsonl_committed": (root / V2_DIR / "evd_export_v2.jsonl").is_file(),
    }
    v1c["under_correctly_rounded_log"] = {"export_sha256": neu["v1_export_sha256"], "equals_recorded": neu["v1_export_sha256"] == m1["export_sha256"]}
    v2c["under_correctly_rounded_log"] = {"export_sha256": neu["v2_export_sha256"], "equals_recorded": neu["v2_export_sha256"] == m2["export_sha256"]}
    libm = {"math_log_evaluations_in_export": 15290, "cells_differing_between_glibc_and_correctly_rounded_build": neu["differing_cells_vs_glibc_build"],
            "columns": neu["differing_columns"], "evd_ids": neu["differing_evd_ids"],
            "reading": "last-digit differences of ln(after/before) between the host libm and the libm that wrote the recorded hash; every other byte is identical"}
    fz = {}
    for name in ("keys.jsonl", "edge_candidates.jsonl", "ledgers/data/DOC.jsonl", "ledgers/data/STUDY.jsonl", "ledgers/data/_ids.jsonl", "ledgers/data/SRC_08A_YIELD.jsonl",
                 "evd_export_v2.manifest.json", "feasibility.json", "keys_counts.json"):
        p = (root / V2_DIR / name) if not name.startswith("ledgers/") else (root / name)
        fz[name] = {"recorded": freeze[name]["sha256"], "current_file": sha256_file(p) if p.is_file() else "FILE_NOT_IN_THIS_TREE"}
        fz[name]["equal"] = fz[name]["recorded"] == fz[name]["current_file"]
    after = {n: sha256_file(root / "ledgers" / "data" / f"{n}.jsonl") for n in ALL_LEDGERS}
    base = {p.split("/")[-1].split(".")[0]: h for p, h in baseline.items()}
    prot = {n: {"before": before[n], "after": after[n], "baseline_csv": base.get(n), "v1_manifest_before_after": m1["ledger_sha256_before_after"]["after"].get(n)}
            for n in ALL_LEDGERS}
    for n, d in prot.items():
        d["unchanged"] = d["before"] == d["after"]
        d["equals_recorded"] = d["after"] == (d["baseline_csv"] or d["v1_manifest_before_after"])
    verdict_items = {
        "v1_export_sha256_equals_recorded_as_built_here": v1c["export_sha256"]["equal"],
        "v1_export_sha256_equals_recorded_under_correctly_rounded_log": v1c["under_correctly_rounded_log"]["equals_recorded"],
        "v1_matrix_and_prior_state_tables_equal_recorded": v1c["matrix_table_sha256"]["equal"] and v1c["prior_state_table_sha256"]["equal"],
        "v2_two_fresh_runs_identical": v2c["run_a_equals_run_b"],
        "v2_equals_recorded_sha256_as_built_here": v2c["run_equals_recorded"],
        "v2_equals_recorded_sha256_under_correctly_rounded_log": v2c["under_correctly_rounded_log"]["equals_recorded"],
        "only_log_fold_change_cells_differ_between_libm_variants": libm["columns"] in ([], ["log_fold_change"]),
        "keys_file_hash_matches_recorded_and_freeze": v2c["keys_file_sha256"]["current_file"] == v2c["keys_file_sha256"]["in_recorded_manifest"] == v2c["keys_file_sha256"]["in_freeze_manifest"],
        "ledger_inputs_of_keys_unchanged_since_freeze": all(fz[n]["equal"] for n in ("ledgers/data/DOC.jsonl", "ledgers/data/STUDY.jsonl", "ledgers/data/_ids.jsonl", "ledgers/data/SRC_08A_YIELD.jsonl")),
        "protected_ledgers_unchanged_during_run": all(prot[n]["unchanged"] for n in ALL_LEDGERS),
        "protected_ledgers_equal_recorded": all(prot[n]["equals_recorded"] for n in ("EVD", "COND", "SRC", "MEAS", "SNAP")),
        "evd_ledger_hash_in_v2_manifest_is_current": v2c["ledger_sha256_evd"]["current"] == v2c["ledger_sha256_evd"]["in_recorded_manifest"],
    }
    platform_keys = ("v1_export_sha256_equals_recorded_as_built_here", "v2_equals_recorded_sha256_as_built_here")
    rest_ok = all(v for k, v in verdict_items.items() if k not in platform_keys)
    if all(verdict_items.values()):
        verdict = "REPRODUCIBLE_BYTE_IDENTICAL"
    elif rest_ok:
        verdict = f"REPRODUCIBLE_ON_THIS_HOST__CROSS_PLATFORM_DIFFERS_IN_{libm['cells_differing_between_glibc_and_correctly_rounded_build']}_LOG_FOLD_CHANGE_CELLS_EXPLAINED"
    else:
        verdict = "MISMATCH_SEE_verdict_items"
    return {"record": "EVD_EXPORT_REPRO_S178", "tool_version": TOOL_VERSION, "status": "AI_DRAFTED_PROPOSED", "contains_text": False, "contains_ids": True,
            "counts_as_human_gate": False, "v1": v1c, "v2": v2c, "libm_finding": libm, "freeze_manifest_inputs": fz, "ledgers": prot, "verdict_items": verdict_items,
            "verdict": verdict,
            "not_done": ["keys.jsonl was verified by hash, not rebuilt (tools/step08a_build_keys.py refuses repo roots and a non-Mac output root)",
                         "the committed v1 jsonl and v2 jsonl are git-ignored and not in this tree: comparison is against the recorded manifest sha256"]}


def render_md(d: dict) -> str:
    vi = d["verdict_items"]
    rows = [[k, "PASS" if v else "FAIL"] for k, v in vi.items()]
    v1, v2 = d["v1"], d["v2"]
    hrows = [["v1 export (evd_export_v1.jsonl)", v1["export_sha256"]["rebuilt"], v1["export_sha256"]["recorded"]],
             ["v1 matrix table", v1["matrix_table_sha256"]["rebuilt"], v1["matrix_table_sha256"]["recorded"]],
             ["v1 prior-state table", v1["prior_state_table_sha256"]["rebuilt"], v1["prior_state_table_sha256"]["recorded"]],
             ["v2 export run A", v2["export_sha256_run_a"], v2["recorded_export_sha256"]],
             ["v2 export run B", v2["export_sha256_run_b"], v2["recorded_export_sha256"]],
             ["v1 export, correctly rounded log", v1["under_correctly_rounded_log"]["export_sha256"], v1["export_sha256"]["recorded"]],
             ["v2 export, correctly rounded log", v2["under_correctly_rounded_log"]["export_sha256"], v2["recorded_export_sha256"]],
             ["keys.jsonl (verified, not rebuilt)", v2["keys_file_sha256"]["current_file"], v2["keys_file_sha256"]["in_recorded_manifest"]]]
    lrows = [[n, x["before"][:16] + "...", x["after"][:16] + "...", "yes" if x["unchanged"] else "NO", "yes" if x["equals_recorded"] else "NO"] for n, x in d["ledgers"].items()]
    out = ["# EVD export v1 / v2 (08a.7) reproducibility check (S178, T2-C01-R2)", "",
           f"Status: AI_DRAFTED / PROPOSED, hashes and counts only, nothing written under `ledgers/` or `exports/`. `tools/s178_evd_export_repro.py` ({TOOL_VERSION}); deterministic.", "",
           f"**Verdict: {d['verdict']}** ({sum(vi.values())} of {len(vi)} checks pass).", "",
           md_table(["check", "result"], rows), "",
           "## Cross-platform finding", "",
           f"- The rebuilt v1 and v2 bytes differ from the recorded (Mac) sha256 in **{d['libm_finding']['cells_differing_between_glibc_and_correctly_rounded_build']} cells**, all in column(s) {d['libm_finding']['columns']}: "
           "the host `math.log` (glibc) differs from the correctly rounded value in the last digit. A build with a correctly rounded `log` equals the recorded v1 and v2 sha256 exactly "
           f"(v1 {d['v1']['under_correctly_rounded_log']['equals_recorded']}, v2 {d['v2']['under_correctly_rounded_log']['equals_recorded']}).",
           "- Two fresh builds on this host are byte-identical to each other. The recorded hash is therefore reproducible on the Mac libm and, up to those cells, here. "
           "Proposed (a human decides; the builder is not changed here): make the log columns platform-neutral (correctly rounded log, or round to 12 significant digits) in the next builder version, record the new sha256, and keep the old one as `evd_export_v1@mac-libm`.", "",
           "## Hashes (rebuilt in scratch vs recorded)", "", md_table(["artifact", "rebuilt / current sha256", "recorded sha256"], hrows), "",
           "## Protected ledgers (before and after the run)", "", md_table(["ledger", "before", "after", "unchanged", "equals recorded baseline"], lrows), "",
           "## Not done", ""] + [f"- {x}" for x in d["not_done"]] + [""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--scratch", help="scratch dir (default: a fresh temp dir, deleted afterwards)")
    a = ap.parse_args(argv)
    own = a.scratch is None
    scratch = Path(a.scratch) if a.scratch else Path(tempfile.mkdtemp(prefix="s178_evd_repro_"))
    try:
        d = check(ROOT, scratch)
    finally:
        if own:
            shutil.rmtree(scratch, ignore_errors=True)
    out = ROOT / a.out_dir
    j = write_new_or_same(out / "evd_export_repro_check_v1.json", dumps(d))
    m = write_new_or_same(out / "evd_export_repro_check_v1.md", render_md(d))
    print(dumps({"verdict": d["verdict"], "verdict_items": d["verdict_items"], "json_sha256": j, "md_sha256": m}))
    return 0 if not d["verdict"].startswith("MISMATCH") else 1


if __name__ == "__main__":
    raise SystemExit(main())
