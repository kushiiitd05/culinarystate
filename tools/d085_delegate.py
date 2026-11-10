#!/usr/bin/env python
"""D-085: ksh+prv (AI) act on the humans' behalf. Writes approvals and pre-registration locks under the AI delegate
name only (never a human's), refuses to overwrite, and binds the current bytes.

    python tools/d085_delegate.py approve-freeze --snapshot 15A-BOOT-2026-11-08
    python tools/d085_delegate.py lock --doc D29|D5|AA
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evaluation.freeze_records import AI_DELEGATE  # noqa: E402

DOCS = {"D29": ("reports/step29/29diag_preregistration_DRAFT.md", "reports/step29/29diag_prereg_signature.json"),
        "D5": ("reports/del5/d5_benchmark_preregistration_DRAFT.md", "reports/del5/d5_prereg_lock_D085.json"),
        "AA": ("reports/step10/aa_pilot_preregistration_DRAFT.md", "reports/step10/aa_pilot_prereg_lock_D085.json")}


def lock(root: Path, doc: str, when: str) -> Path:
    text, out = DOCS[doc]
    p = root / out
    if p.exists():
        raise SystemExit(f"refusing: {out} exists")
    p.write_text(json.dumps({"prereg_sha256": hashlib.sha256((root / text).read_bytes()).hexdigest(),
                             "signed_by": AI_DELEGATE, "signed_date": when, "decision": "D-085",
                             "label": "NO_HUMAN_SIGNOFF_D085"}, indent=2) + "\n", encoding="utf-8")
    return p


def approve_freeze(root: Path, snapshot: str, when: str) -> Path:
    p = root / "registry" / "freezes" / f"{snapshot}.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    if rec.get("status") != "PROPOSED":
        raise SystemExit(f"refusing: status {rec.get('status')!r}")
    rec.update({"status": "FROZEN", "approved_by": AI_DELEGATE, "approved_date": when, "approval_decision": "D-085"})
    p.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("approve-freeze").add_argument("--snapshot", required=True)
    sub.add_parser("lock").add_argument("--doc", required=True, choices=sorted(DOCS))
    a = ap.parse_args()
    today = date.today().isoformat()
    out = approve_freeze(ROOT, a.snapshot, today) if a.cmd == "approve-freeze" else lock(ROOT, a.doc, today)
    print("wrote", out.relative_to(ROOT))
