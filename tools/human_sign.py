#!/usr/bin/env python
"""Human-run signing helper (S179). RUN ONLY BY THE SIGNER, in the signer's own session; the coding agent never runs it
and never commits its output (D-071: signatures and freeze approvals are human-only).

    python tools/human_sign.py sign --doc D5 --signer "Kush Tokas"        # also: --doc D29 (Kush only), --doc AA
    python tools/human_sign.py approve-freeze --snapshot 15A-BOOT-2026-11-08 --approver "Kush Tokas"

It hashes the pre-registration text exactly as it is on disk now, writes the signer's own signature file in the
shape the checkers read (`evaluation/freeze_records.prereg_signed`, `evaluation/frozen_guard`), never overwrites a
signature, and prints the commit command. Read the text first: the signature binds these bytes, and any later edit
voids it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUMANS = {"Kush Tokas": "Kush", "Parv Goyal": "Parv"}
DOCS = {
    "D5": ("reports/del5/d5_benchmark_preregistration_DRAFT.md", "reports/del5/d5_prereg_signature_{who}.json",
           ("Kush Tokas", "Parv Goyal")),
    "AA": ("reports/step10/aa_pilot_preregistration_DRAFT.md", "reports/step10/aa_pilot_prereg_signature_{who}.json",
           ("Kush Tokas", "Parv Goyal")),
    "D29": ("reports/step29/29diag_preregistration_DRAFT.md", "reports/step29/29diag_prereg_signature.json",
            ("Kush Tokas",)),
}


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sign(root: Path, doc: str, signer: str, when: str) -> Path:
    if doc not in DOCS:
        raise SystemExit(f"unknown doc {doc!r}; one of {sorted(DOCS)}")
    text, sig, allowed = DOCS[doc]
    if signer not in allowed:
        raise SystemExit(f"{signer!r} may not sign {doc}; allowed: {allowed} (AI personas never sign, D-071)")
    out = Path(root) / sig.format(who=HUMANS[signer])
    if out.exists():
        raise SystemExit(f"refusing: {out.relative_to(root)} exists (a signature is never overwritten)")
    out.write_text(json.dumps({"prereg_sha256": sha(Path(root) / text), "signed_by": signer, "signed_date": when},
                              indent=2) + "\n", encoding="utf-8")
    return out


def approve_freeze(root: Path, snapshot: str, approver: str, when: str) -> Path:
    if approver not in HUMANS:
        raise SystemExit(f"{approver!r} may not approve a freeze (D-071)")
    p = Path(root) / "registry" / "freezes" / f"{snapshot}.json"
    rec = json.loads(p.read_text(encoding="utf-8"))
    if rec.get("status") != "PROPOSED":
        raise SystemExit(f"refusing: {p.name} status is {rec.get('status')!r}, not PROPOSED")
    rec.update({"status": "FROZEN", "approved_by": approver, "approved_date": when})
    p.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sign")
    s.add_argument("--doc", required=True, choices=sorted(DOCS))
    s.add_argument("--signer", required=True)
    f = sub.add_parser("approve-freeze")
    f.add_argument("--snapshot", required=True)
    f.add_argument("--approver", required=True)
    a = ap.parse_args()
    today = date.today().isoformat()
    if a.cmd == "sign":
        p = sign(ROOT, a.doc, a.signer, today)
        who = a.signer
    else:
        p = approve_freeze(ROOT, a.snapshot, a.approver, today)
        who = a.approver
    rel = p.relative_to(ROOT)
    print(f"wrote {rel}\ncommit it yourself:\n  git add {rel} && git -c user.name=\"{who}\" -c user.email=<your own email> commit -m \"sign: {rel.name}\" -- {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
