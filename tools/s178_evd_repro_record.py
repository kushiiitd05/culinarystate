#!/usr/bin/env python3
"""S178 EVD lane, T2-C15-R4: reproducibility record for the evidence-plane runs (G15-R): seeds, versions, hashes, splits, run list,
and a rerun that reproduces the dataset-card hash.

What it does (read-only on ledgers; nothing is written outside --out-dir and a scratch dir):
  * reruns ``tools/s178_analysis_evd_card.py`` (unchanged) into a scratch dir and compares its JSON and markdown sha256 with the committed
    ``reports/s178/analysis/evd_dataset_card_v1.{json,md}`` (acceptance: "a rerun that reproduces dataset card hash");
  * records the interpreter, platform and package versions, the sha256 of every code file the evidence-plane runs use, the sha256 of every
    input ledger / registry / census file, the sampling seed rule, the split position (this lane builds no split), and the sha256 of every
    committed output of this lane that exists at the time of the run (the record does not hash itself);
  * lists the evidence-plane runs with their one-line commands, so the orchestrator can match them to compute_runs rows.

  python tools/s178_evd_repro_record.py [--out-dir reports/s178/evd]

Deterministic on one host and tree state. Status: AI_DRAFTED / PROPOSED. No personal path, host name or credential is written.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s178_evd_common import DEFAULT_OUT, ROOT, dumps, md_table, protected_hashes, sha256_file, write_new_or_same  # noqa: E402

TOOL_VERSION = "s178-evd-repro-record-0.2.0-draft"   # 0.2.0 (S179): router census S177 -> S179b, can_say + coverage v2; 0.1.1 (FIX-GOV): S176 -> S177
CARD_TOOL = "tools/s178_analysis_evd_card.py"
CARD_FILES = ("evd_dataset_card_v1.json", "evd_dataset_card_v1.md")
RECORD_NAMES = ("evd_reproducibility_record_v2.json", "evd_reproducibility_record_v2.md")   # S179: v1 kept on record
CARD_DIR = "reports/s178/analysis"
CODE = ("tools/s178_evd_common.py", "tools/s178_evd_conformance.py", "tools/s178_evd_export_repro.py", "tools/s178_evd_svar_reconcile.py", "tools/s178_evd_coverage.py",
        "tools/s178_evd_transition_audit.py", "tools/s178_evd_d5_ux_draft.py", "tools/s178_evd_repro_record.py", CARD_TOOL, "tools/step08a_export_v2.py",
        "src/culinarystate/evidence/evd_export.py", "src/culinarystate/lineage/export_v2.py", "src/culinarystate/transition/dataset.py",
        "src/culinarystate/transition/baselines.py", "src/culinarystate/transition/cross_source.py", "src/culinarystate/mechanism/router_demo.py",
        "src/culinarystate/mechanism/router_census.py", "tests/unit/test_s178_evd_no_imputation.py")
INPUTS = ("ledgers/data/EVD.jsonl", "ledgers/data/COND.jsonl", "ledgers/data/SRC.jsonl", "ledgers/data/MEAS.jsonl", "ledgers/data/SNAP.jsonl", "ledgers/data/SVAR.jsonl",
          "ledgers/data/PROC.jsonl", "ledgers/data/ING.jsonl", "registry/svar_duplicate_mapping_v1.csv", "registry/state_variable_registry_v1.csv", "registry/baseline_ledger_hashes_08a_v1.csv",
          "exports/lineage/step08a_v1/keys.jsonl", "exports/evd/evd_export_v1.manifest.json", "exports/lineage/step08a_v1/evd_export_v2.manifest.json",
          "reports/step15/15a_R_seal_commitment_v1.json", "reports/step23/router_demo_census_vitc_nonBBC_full_S179b.json", "reports/step23/router_demo_census_vitc_nonBBC_1000_S179b.json",
          "reports/s178/analysis/corpus_can_say_v2.json")
OUTPUTS = ("evd_field_conformance_203_2_v1.json", "evd_field_conformance_203_2_v1.csv", "evd_field_conformance_203_2_v1.md", "evd_export_repro_check_v1.json", "evd_export_repro_check_v1.md",
           "svar_reconciliation_v1.json", "svar_reconciliation_v1.md", "evd_coverage_vs_corpus_demand_v2.json", "evd_coverage_vs_corpus_demand_v2.csv", "evd_coverage_vs_corpus_demand_v2.md",
           "fig_evd_coverage_by_family_v2.svg", "transition_no_imputation_audit_v1.json", "d5_UX_blocks_S178_DRAFT.csv", "d5_UX_blocks_S178_DRAFT.md")
RUNS = [
    ("EVD-1", "T2-C01-R2", "python tools/s178_evd_export_repro.py", "evd_export_repro_check_v1.{json,md}", "rebuild EVD export v1 and v2 (08a.7) in scratch dirs, compare with recorded sha256; two fresh v2 builds + a correctly-rounded-log variant"),
    ("EVD-2", "T2-C01-R1", "python tools/s178_evd_conformance.py [--selfcheck]", "evd_field_conformance_203_2_v1.{json,csv,md}", "203.2 field-by-field conformance of the 17,978 ACTIVE rows"),
    ("EVD-3", "T2-C03-R3", "python tools/s178_evd_svar_reconcile.py [--selfcheck]", "svar_reconciliation_v1.{json,md}", "SVAR lines / distinct ids / registry rows / EVD usage"),
    ("EVD-4", "T2-C13-R1", "python tools/s178_evd_coverage.py --sample-size 1000 --workers 4 [--selfcheck]", "evd_coverage_vs_corpus_demand_v2.{json,csv,md}, fig_evd_coverage_by_family_v2.svg",
     "EVD pair coverage vs corpus demand; seeded 1,000-recipe non-BBC sample through the unchanged router"),
    ("EVD-5", "T6-C09-R2", "python tools/s178_evd_transition_audit.py [--selfcheck]", "transition_no_imputation_audit_v1.json", "real cell tables built with the unmodified transition.dataset; imputation violations counted"),
    ("EVD-6", "T8-C20-R4", "python tools/s178_evd_d5_ux_draft.py", "d5_UX_blocks_S178_DRAFT.{csv,md}", "draft U and X blocks (ledger facts re-read and asserted)"),
    ("EVD-7", "T2-C15-R4", "python tools/s178_evd_repro_record.py", "evd_reproducibility_record_v2.{json,md}", "this record; reruns the dataset-card tool and compares its hash"),
]


def versions() -> dict:
    out = {}
    for p in ("numpy", "pandas", "scipy", "pytest", "pyarrow"):
        try:
            out[p] = md.version(p)
        except md.PackageNotFoundError:
            out[p] = "NOT_INSTALLED"
    return out


def git_head(root: Path) -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True, timeout=20)
        return r.stdout.strip() or "UNKNOWN"
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def hashes(root: Path, rels) -> dict:
    return {r: (sha256_file(root / r) if (root / r).is_file() else "FILE_NOT_PRESENT") for r in rels}


def card_rerun(root: Path, scratch: Path) -> dict:
    r = subprocess.run([sys.executable, str(root / CARD_TOOL), "--out-dir", str(scratch)], cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("card tool failed: " + r.stderr[-300:])
    files = {}
    for f in CARD_FILES:
        committed, rerun = sha256_file(root / CARD_DIR / f), sha256_file(scratch / f)
        files[f] = {"committed_sha256": committed, "rerun_sha256": rerun, "equal": committed == rerun}
    return {"tool": CARD_TOOL, "files": files, "all_equal": all(v["equal"] for v in files.values())}


def build(root: Path, scratch: Path, out_dir: Path) -> dict:
    before = protected_hashes(root)
    card = card_rerun(root, scratch)
    assert before == protected_hashes(root)
    return {"record": "EVD_PLANE_REPRODUCIBILITY_S178", "tool_version": TOOL_VERSION, "status": "AI_DRAFTED_PROPOSED", "contains_text": False, "counts_as_human_gate": False,
            "environment": {"python": platform.python_version(), "implementation": platform.python_implementation(), "platform": platform.platform(), "packages": versions(),
                            "libm_note": "math.log on this glibc differs from the correctly rounded value in the last digit for 4 log_fold_change cells of the export (see evd_export_repro_check_v1)",
                            "git_head": git_head(root), "tree_state": "uncommitted changes present (worktree)"},
            "seeds": {"coverage_sample": {"seed_sha256": hashlib.sha256(b"20261104").hexdigest(), "rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC", "sample_size": 1000,
                                          "families": ["WIKIBOOKS", "GUTENBERG_SEGMENT", "FOODCOM", "TASTESET"], "same_sample_as": "reports/step23/router_demo_census_vitc_nonBBC_1000_S179b.json"},
                      "other_runs": "none: the other evidence-plane runs are deterministic functions of the ledgers (no random draw)",
                      "tests": "property tests use random.Random(seed) for seeds 0..39 (fixed in the test file)"},
            "splits": {"built_by_this_lane": 0, "note": "no train / test split is built or read here; split registry: registry/split_registry_v1.csv (EVAL lane)"},
            "code_sha256": hashes(root, CODE), "input_sha256": hashes(root, INPUTS),
            "output_sha256": {f: (sha256_file(out_dir / f) if (out_dir / f).is_file() else "FILE_NOT_PRESENT") for f in OUTPUTS},
            "dataset_card_rerun": card,
            "protected_ledgers_unchanged_during_run": True, "protected_ledger_sha256": before,
            "runs": [{"id": f"RUN-S178-{r[0]}", "item": r[1], "command": r[2], "outputs": r[3], "what": r[4]} for r in RUNS],
            "compute_runs_note": "rows for compute_runs_v1.csv are written by the orchestrator; start / end times and wall seconds are in reports/orchestration/S178_EVD_report.md"}


def render_md(d: dict) -> str:
    card = d["dataset_card_rerun"]
    crow = [[f, v["committed_sha256"], v["rerun_sha256"], "yes" if v["equal"] else "NO"] for f, v in card["files"].items()]
    runs = [[r["id"], r["item"], f"`{r['command']}`", r["outputs"]] for r in d["runs"]]
    env = d["environment"]
    return "\n".join([
        "# Evidence-plane reproducibility record (S178, T2-C15-R4)", "",
        f"Status: AI_DRAFTED / PROPOSED. `tools/s178_evd_repro_record.py` ({TOOL_VERSION}). Hashes, versions and commands only.", "",
        f"**Dataset card: rerun reproduces the committed hash: {card['all_equal']}.**", "",
        md_table(["card file", "committed sha256", "rerun sha256", "equal"], crow), "",
        "## Environment", "", f"- python {env['python']} ({env['implementation']}), {env['platform']}; packages {env['packages']}; git HEAD {env['git_head']} (+ uncommitted worktree changes).",
        f"- {env['libm_note']}.", "",
        "## Seeds and splits", "", f"- Coverage sample: seed sha256 `{d['seeds']['coverage_sample']['seed_sha256']}`, rule {d['seeds']['coverage_sample']['rule']}, n = 1,000, non-BBC families; same sample as the committed S179b router census.",
        f"- {d['seeds']['other_runs']}.", f"- {d['seeds']['tests']}.", f"- Splits: {d['splits']['note']}.", "",
        "## Runs", "", md_table(["run", "item", "command", "outputs"], runs), "",
        "## Hashes", "", f"Code, input and output sha256 are in `{RECORD_NAMES[0]}` (`code_sha256`, `input_sha256`, `output_sha256`). The record does not hash itself.", ""])


def run(out_dir: Path, scratch: Path, root: Path = ROOT) -> dict:
    d = build(root, scratch, out_dir)
    return {"json_sha256": write_new_or_same(out_dir / RECORD_NAMES[0], dumps(d)),
            "md_sha256": write_new_or_same(out_dir / RECORD_NAMES[1], render_md(d)), "card_reproduced": d["dataset_card_rerun"]["all_equal"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--scratch", help="scratch dir for the card rerun (default: a temp dir, deleted afterwards)")
    a = ap.parse_args(argv)
    own = a.scratch is None
    scratch = Path(a.scratch) if a.scratch else Path(tempfile.mkdtemp(prefix="s178_evd_record_"))
    try:
        r = run(ROOT / a.out_dir, scratch)
    finally:
        if own:
            shutil.rmtree(scratch, ignore_errors=True)
    print(dumps(r))
    return 0 if r["card_reproduced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
