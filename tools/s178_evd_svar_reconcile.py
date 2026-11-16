#!/usr/bin/env python3
"""S178 EVD lane, T2-C03-R3: reconcile the SVAR counts (ledger lines vs distinct ids vs registry rows vs EVD usage).

Reads ledgers/data/SVAR.jsonl, ledgers/data/EVD.jsonl, registry/state_variable_registry_v1.csv and
registry/svar_duplicate_mapping_v1.csv READ-ONLY and writes one counts-only table (JSON + markdown) with paths.
It also lists where the line count "355" is still quoted as if it were an id count (path:line only), so the packet and
reports can be corrected. Deterministic (no timestamp): ``--selfcheck`` writes twice to a scratch dir and compares.

  python tools/s178_evd_svar_reconcile.py [--out-dir reports/s178/evd] [--selfcheck]

Status: AI_DRAFTED / PROPOSED, counts only. Writes no ledger.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s178_evd_common import (DEFAULT_OUT, ROOT, counter_dict, dumps, md_table, protected_hashes,  # noqa: E402
                             read_ledger, sha256_file, write_new_or_same)

TOOL_VERSION = "s178-evd-svar-reconcile-0.1.0-draft"
SVAR = "ledgers/data/SVAR.jsonl"
EVD = "ledgers/data/EVD.jsonl"
REG = "registry/state_variable_registry_v1.csv"
MAP = "registry/svar_duplicate_mapping_v1.csv"
# files that quote the SVAR count; scanned for the stale "355 ... SVAR" wording (path:line only)
SCAN = ("handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md", "registry/component_ledger_v1.csv",
        "reports/master_plan/master_plan_research_audit_v2.md", "docs/SSOT/computational_gastronomy_master_ssot_v16_0_DRAFT.md",
        "reports/orchestration/ssot_consensus/CONSENSUS_PLAN_2026-11-08.md", "reports/orchestration/ssot_consensus/CONSENSUS_DRAFT.md",
        "reports/orchestration/review/S176_REV-A_science.md", "reports/orchestration/S176_V16_report.md",
        "registry/execution_board_S178.csv")
STALE = re.compile(r"355 (?:SVAR|rows|state variables)|\(355 SVAR", re.I)  # "355 lines" is accurate and is not flagged
FIXED = re.compile(r"224 (?:distinct|SVAR ids?)|355 \*?\*?version records|355 lines / (?:\*\*)?224", re.I)


def build(root: Path) -> dict:
    latest, lines = read_ledger(root / SVAR)
    evd_latest, _ = read_ledger(root / EVD)
    reg_rows = list(csv.DictReader(open(root / REG, newline="", encoding="utf-8")))
    mp = list(csv.DictReader(open(root / MAP, newline="", encoding="utf-8")))
    vers = Counter(r["id"] for r in lines)
    ver_hist = Counter(vers.values())
    fam_lines = Counter(r["family"] for r in lines)
    fam_distinct = Counter(r["family"] for r in latest.values())
    fam_changes = sum(1 for i in vers if len({r["family"] for r in lines if r["id"] == i}) > 1) if len(lines) < 5000 else None
    st_latest = Counter(r["status"] for r in latest.values())
    st_lines = Counter(r["status"] for r in lines)
    active_evd = [e for e in evd_latest.values() if e["status"] == "ACTIVE"]
    used_active = Counter(e["target"]["state_variable_id"] for e in active_evd)
    used_any = {e["target"]["state_variable_id"] for e in evd_latest.values()}
    reg_ids = {r["state_variable_id"] for r in reg_rows}
    ledger_ids = set(latest)
    reg_status = Counter(r["status"] for r in reg_rows)
    reg_family = Counter(r["family"] for r in reg_rows)
    reg_future = [r for r in reg_rows if r["status"] == "FUTURE"]
    reg_nonfuture = {r["state_variable_id"] for r in reg_rows if r["status"] != "FUTURE"}
    dup = {m["duplicate_id"]: m["canonical_id"] for m in mp if m["relation"] == "DUPLICATE_SAME_ANALYTE"}
    canon_used = {dup.get(i, i) for i in used_active}
    reg_rowcount_sum = sum(int(r["current_row_count"] or 0) for r in reg_rows if r["status"] != "FUTURE")
    reg_rowcount_mismatch = sum(1 for r in reg_rows if r["status"] != "FUTURE" and int(r["current_row_count"] or 0) != used_active.get(r["state_variable_id"], 0))
    ids_sorted = sorted(ledger_ids)
    table = {
        "ledger_SVAR_jsonl": {"path": SVAR, "version_lines": len(lines), "distinct_ids": len(latest),
                              "ids_with_one_version": ver_hist.get(1, 0), "ids_with_two_or_more_versions": sum(v for k, v in ver_hist.items() if k >= 2),
                              "version_count_histogram": {str(k): v for k, v in sorted(ver_hist.items())},
                              "lines_by_family": counter_dict(fam_lines), "distinct_ids_by_family_latest_version": counter_dict(fam_distinct),
                              "ids_whose_family_differs_between_versions": fam_changes,
                              "lines_by_status": counter_dict(st_lines), "distinct_ids_by_status_latest_version": counter_dict(st_latest),
                              "id_range": [ids_sorted[0], ids_sorted[-1]], "sha256": sha256_file(root / SVAR)},
        "registry_csv": {"path": REG, "rows": len(reg_rows), "rows_by_status": counter_dict(reg_status), "rows_by_family": counter_dict(reg_family),
                         "FUTURE_rows": len(reg_future), "FUTURE_id_pattern_all_SVAR_FUT": all(r["state_variable_id"].startswith("SVAR-FUT-") for r in reg_future),
                         "FUTURE_by_family": counter_dict(Counter(r["family"] for r in reg_future)),
                         "non_FUTURE_rows": len(reg_nonfuture), "non_FUTURE_ids_equal_ledger_distinct_ids": reg_nonfuture == ledger_ids,
                         "ledger_ids_missing_from_registry": len(ledger_ids - reg_ids), "registry_non_FUTURE_ids_missing_from_ledger": len(reg_nonfuture - ledger_ids),
                         "sum_current_row_count_non_FUTURE": reg_rowcount_sum, "rows_whose_current_row_count_differs_from_active_evd_usage": reg_rowcount_mismatch,
                         "sha256": sha256_file(root / REG)},
        "evd_usage": {"path": EVD, "active_evd_rows": len(active_evd), "distinct_svar_ids_on_active_rows": len(used_active),
                      "distinct_svar_ids_on_any_evd_version_line_latest": len(used_any),
                      "ledger_ids_not_used_by_any_active_row": len(ledger_ids - set(used_active)),
                      "active_row_svar_ids_missing_from_ledger": len(set(used_active) - ledger_ids),
                      "rows_by_family": counter_dict(Counter(latest[e["target"]["state_variable_id"]]["family"] for e in active_evd))},
        "duplicate_mapping": {"path": MAP, "rows": len(mp), "rows_by_relation": counter_dict(Counter(m["relation"] for m in mp)),
                              "duplicate_ids_mapped_to_canonical": len(dup), "canonical_variables_after_mapping_on_active_rows": len(canon_used),
                              "sha256": sha256_file(root / MAP)},
    }
    stale: list[dict] = []
    fixed: list[dict] = []
    for rel in SCAN:
        p = root / rel
        if not p.is_file():
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = STALE.search(line)
            if m and not FIXED.search(line):
                a0 = max(0, m.start() - 60)
                stale.append({"path": rel, "line": n, "excerpt": re.sub(r"\s+", " ", line[a0:m.end() + 90].strip())})
            elif FIXED.search(line):
                fixed.append({"path": rel, "line": n})
    table["quotes"] = {"scanned_files": len(SCAN), "lines_quoting_355_as_a_count_without_the_224_correction": stale,
                       "lines_already_carrying_the_correction": fixed}
    L, R, E = table["ledger_SVAR_jsonl"], table["registry_csv"], table["evd_usage"]
    table["one_line_summary"] = (
        f"SVAR.jsonl has {L['version_lines']} version lines = {L['distinct_ids']} distinct ids ({L['distinct_ids_by_family_latest_version'].get('CHEMICAL', 0)} CHEMICAL + "
        f"{L['distinct_ids_by_family_latest_version'].get('PHYSICAL', 0)} PHYSICAL at the latest version; by line {L['lines_by_family'].get('CHEMICAL', 0)} CHEMICAL + "
        f"{L['lines_by_family'].get('PHYSICAL', 0)} PHYSICAL); the registry CSV has {R['rows']} rows = {R['non_FUTURE_rows']} ledger ids + {R['FUTURE_rows']} FUTURE ids; "
        f"{E['distinct_svar_ids_on_active_rows']} ids are used by the {E['active_evd_rows']:,} ACTIVE EVD rows ({table['duplicate_mapping']['canonical_variables_after_mapping_on_active_rows']} canonical after the duplicate mapping).")
    return {"record": "SVAR_RECONCILIATION_S178", "tool_version": TOOL_VERSION, "status": "AI_DRAFTED_PROPOSED", "contains_text": False,
            "counts_as_human_gate": False, "table": table,
            "protected_ledger_hashes_read": protected_hashes(root)}


def render_md(d: dict) -> str:
    t = d["table"]
    L, R, E, M = t["ledger_SVAR_jsonl"], t["registry_csv"], t["evd_usage"], t["duplicate_mapping"]
    rows = [
        ["ledger lines (version records)", L["version_lines"], f"`{L['path']}`"],
        ["ledger distinct ids", L["distinct_ids"], f"`{L['path']}` (latest version per id)"],
        ["  ids with 1 version / 2+ versions", f"{L['ids_with_one_version']} / {L['ids_with_two_or_more_versions']}", f"histogram {L['version_count_histogram']}"],
        ["  distinct ids by family (latest)", str(L["distinct_ids_by_family_latest_version"]), "same file"],
        ["  lines by family", str(L["lines_by_family"]), "same file"],
        ["  distinct ids by status (latest)", str(L["distinct_ids_by_status_latest_version"]), "same file"],
        ["registry rows", R["rows"], f"`{R['path']}`"],
        ["  registry rows by status", str(R["rows_by_status"]), "same file"],
        ["  registry FUTURE rows (SVAR-FUT-*)", R["FUTURE_rows"], str(R["FUTURE_by_family"])],
        ["  non-FUTURE registry ids equal ledger distinct ids", str(R["non_FUTURE_ids_equal_ledger_distinct_ids"]), f"missing from registry {R['ledger_ids_missing_from_registry']}; missing from ledger {R['registry_non_FUTURE_ids_missing_from_ledger']}"],
        ["distinct SVAR ids on ACTIVE EVD rows", E["distinct_svar_ids_on_active_rows"], f"`{E['path']}` ({E['active_evd_rows']:,} ACTIVE rows)"],
        ["  ledger ids unused by any ACTIVE row", E["ledger_ids_not_used_by_any_active_row"], "same file"],
        ["duplicate mapping rows", M["rows"], f"`{M['path']}` {M['rows_by_relation']}"],
        ["canonical variables on ACTIVE rows after mapping", M["canonical_variables_after_mapping_on_active_rows"], "DUPLICATE_SAME_ANALYTE ids folded to canonical"],
    ]
    out = ["# SVAR count reconciliation (S178, T2-C03-R3)", "",
           "Status: AI_DRAFTED / PROPOSED, counts only, no ledger written. Generated by `tools/s178_evd_svar_reconcile.py` "
           f"({TOOL_VERSION}); deterministic.", "",
           "**" + t["one_line_summary"] + "**", "",
           md_table(["quantity", "count", "path / note"], rows, align_right=(1,)), "",
           "## Which number to quote", "",
           "- \"355\" is the number of **version lines** in `ledgers/data/SVAR.jsonl`, not a number of state variables. Quote **224 distinct SVAR ids**.",
           f"- \"354 chemical, 1 physical\" is the split **by line**; by distinct id (latest version) it is {L['distinct_ids_by_family_latest_version'].get('CHEMICAL', 0)} chemical + {L['distinct_ids_by_family_latest_version'].get('PHYSICAL', 0)} physical.",
           f"- The registry CSV's {R['rows']} rows are the {R['non_FUTURE_rows']} ledger ids plus {R['FUTURE_rows']} reserved FUTURE ids; 355 and 254 are not the same population.",
           "", "## Lines that still quote 355 as a count (path:line, no edit made here)", ""]
    st = t["quotes"]["lines_quoting_355_as_a_count_without_the_224_correction"]
    out += [f"- `{s['path']}:{s['line']}`: {s['excerpt']}" for s in st] or ["- none"]
    out += ["", f"Already carrying the correction: {len(t['quotes']['lines_already_carrying_the_correction'])} lines in the scanned files.", ""]
    return "\n".join(out)


def run(out_dir: Path, root: Path = ROOT) -> dict:
    before = protected_hashes(root)
    d = build(root)
    after = protected_hashes(root)
    assert before == after, "protected ledger changed during run"
    d["protected_ledgers_unchanged_during_run"] = True
    j = write_new_or_same(out_dir / "svar_reconciliation_v1.json", dumps(d))
    m = write_new_or_same(out_dir / "svar_reconciliation_v1.md", render_md(d))
    return {"json_sha256": j, "md_sha256": m, "summary": d["table"]["one_line_summary"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--selfcheck", action="store_true", help="run twice into a scratch dir and compare hashes (writes nothing else)")
    a = ap.parse_args(argv)
    if a.selfcheck:
        with tempfile.TemporaryDirectory() as t1, tempfile.TemporaryDirectory() as t2:
            r1, r2 = run(Path(t1)), run(Path(t2))
        print(dumps({"selfcheck": "IDENTICAL" if r1 == r2 else "DIFFERENT", "run1": r1, "run2": r2}))
        return 0 if r1 == r2 else 1
    r = run(ROOT / a.out_dir)
    print(dumps(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
