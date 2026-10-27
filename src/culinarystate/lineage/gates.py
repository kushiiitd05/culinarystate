"""08a.9: assemble the Step 08a gate report and freeze manifest from the per-package outputs."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

CARD_SHARE = 0.40  # THR-08A-08
_OK_BASELINE = {"IDENTICAL", "PREFIX_IDENTICAL"}


def _sha256(path: Path) -> tuple[str, int]:
    data = Path(path).read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


def compare_runs(a: Mapping[str, Path], b: Mapping[str, Path]) -> dict[str, Any]:
    """G08-6: byte comparison of named outputs from two independent rebuilds."""
    diffs = sorted(n for n in a.keys() | b.keys()
                   if n not in a or n not in b or _sha256(a[n])[0] != _sha256(b[n])[0])
    return {"pass": not diffs, "differences": diffs}


def freeze_manifest(files: Mapping[str, Path]) -> dict[str, dict[str, Any]]:
    out = {}
    for name in sorted(files):
        digest, size = _sha256(files[name])
        out[name] = {"sha256": digest, "bytes": size}
    return out


def _pf(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def build_gate_report(*, keys_counts: Mapping, seeded: Mapping, feasibility: Mapping, largest_share: float,
                      overlap: Mapping, baseline_after: Mapping[str, str], export_v1_identical: bool,
                      rebuild: Mapping) -> dict[str, Any]:
    kg = keys_counts["gates"]
    g: dict[str, dict[str, Any]] = {}
    for gid in ("G08-1", "G08-2", "G08-8", "G08-10"):
        g[gid] = {"status": _pf(bool(kg[gid]["pass"])), "detail": kg[gid]}
    g["G08-3"] = {"status": "PENDING_HUMAN", "detail": "needs the blind ~150-edge audit by two reviewers (THR-08A-03, 04, 16)"}
    g["G08-4"] = {"status": _pf(bool(seeded["all_pass"])), "detail": seeded,
                  "natural_duplicate_recall": "PENDING_HUMAN (blind 200-pair review, report only; THR-08A-18)"}
    base_ok = all(v in _OK_BASELINE for v in baseline_after.values()) and bool(baseline_after)
    g["G08-5"] = {"status": _pf(base_ok and export_v1_identical),
                  "detail": {"baseline_after": dict(baseline_after), "export_v1_identical": export_v1_identical}}
    g["G08-6"] = {"status": _pf(bool(rebuild["pass"])), "detail": dict(rebuild)}
    exceeded = largest_share > CARD_SHARE
    g["G08-7"] = {"status": "LABEL_FORCED", "card_rule_exceeded": exceeded, "largest_share": largest_share,
                  "label_verdict": feasibility.get("label_verdict"),
                  "note": "reports the forced label (THR-08A-08, 09, 15, 20); not a pass/fail"}
    g["G08-9"] = {"status": "PASS_RECORDED" if overlap.get("verdict") else "FAIL",
                  "verdict": overlap.get("verdict"), "expert_reading": "PENDING_HUMAN (before Step 15)"}
    g["G08-H"] = {"status": "PENDING_HUMAN", "detail": "two reviewers, files not identical, counts_as_human_gate = true"}
    statuses = [v["status"] for v in g.values()]
    overall = "FAIL" if "FAIL" in statuses else ("BLOCKED_PENDING_HUMAN" if "PENDING_HUMAN" in statuses else "PASS")
    return {"gates": g, "overall": overall}
