#!/usr/bin/env python3
"""Apply human decisions from registry/evidence/human_review_pack_v1.csv to the EVD ledger.

  /opt/anaconda3/bin/python tools/apply_human_review.py [--dry-run]

Per filled row (verifier ∈ {Kush, Parv}, verified_at = YYYY-MM-DD, paper_locator e.g. "Table 2"):
  CONFIRM -> NEW EVD row: same values/conditions/lineage, provenance MANUAL + paper locator, HUMAN_VERIFIED,
             tier E1 (temperature AND duration stated) else E2. The imported E3 row stays untouched; both share
             independence_group, so retrieval/DEL-2 never double-count the study.
  REJECT  -> imported row gets verification HUMAN_REJECTED (+ notes).
  CORRECT -> imported row gets verification CONFLICT with the corrected value in notes (needs re-extraction).
Rows with an empty human_decision are skipped. Re-running is idempotent.
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.common import HUMANS  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.ledgers.validate import errors as validate_record  # noqa: E402

PACK = ROOT / "registry" / "evidence" / "human_review_pack_v1.csv"


def verified_row(st: LedgerStore, e: dict, cond: dict | None, r: pd.Series, paper_src: str | None) -> dict:
    mask = (cond or {}).get("completeness_mask") or {}
    full = mask.get("temperature") in ("MEASURED", "RANGE") and mask.get("duration") in ("MEASURED", "RANGE")
    when = f"{r.verified_at}T00:00:00+05:30"
    return {**e, "id": st.ids.mint("EVD", key=f"human:{e['id']}"), "version": 1, "created_by": r.verifier,
            "tier": "E1" if full else "E2", "source_id": paper_src or e["source_id"],
            "provenance": {"method": "MANUAL", "agent": f"human:{r.verifier}",
                           "source_ids": [s for s in [paper_src, e["source_id"]] if s],
                           "locator": f"{r.paper_locator} (checked against paper; mirrors {e['id']})"},
            "verification": {"status": "HUMAN_VERIFIED", "verifier": r.verifier, "verified_at": when,
                             "notes": str(r.human_notes or "") or None},
            "extraction_version": "human_review_pack_v1"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pack", type=Path, default=PACK)
    args = ap.parse_args()
    pack = pd.read_csv(args.pack, dtype=str).fillna("")
    st = LedgerStore()
    cond = {c["id"]: c for c in st.all_latest("COND")}
    papers = {s["id"] for s in st.all_latest("SRC") if s["kind"] == "PAPER"}
    out, errors = Counter(), []
    for _, r in pack[pack.human_decision.str.strip() != ""].iterrows():
        dec = r.human_decision.strip().upper()
        if r.verifier not in HUMANS or len(r.verified_at) != 10 or dec not in ("CONFIRM", "REJECT", "CORRECT"):
            errors.append(f"{r.evd_id}: need human_decision CONFIRM/REJECT/CORRECT, verifier in {sorted(HUMANS)}, "
                          f"verified_at YYYY-MM-DD")
            continue
        if dec == "CONFIRM" and not r.paper_locator.strip():
            errors.append(f"{r.evd_id}: CONFIRM needs paper_locator (table/figure/page)")
            continue
        e = st.latest(r.evd_id)
        when = f"{r.verified_at}T00:00:00+05:30"
        if dec == "CONFIRM":
            paper = next((s for s in e["provenance"]["source_ids"] if s in papers), None)
            new = verified_row(st, e, cond.get(e["process"].get("condition_id") or ""), r, paper)
        elif dec == "REJECT":
            new = {**e, "verification": {"status": "HUMAN_REJECTED", "verifier": r.verifier, "verified_at": when,
                                         "notes": r.human_notes or "rejected against paper"}}
        else:
            new = {**e, "verification": {"status": "CONFLICT", "notes": f"{r.verifier} {r.verified_at}: paper says "
                                         f"after={r.corrected_after_value} ({r.paper_locator}); {r.human_notes}"}}
        errs = validate_record(new)
        if errs:
            errors.append(f"{r.evd_id}: {errs}")
            continue
        out[dec if args.dry_run else (dec, st.upsert(new)[0])] += 1
    print("applied:", dict(out))
    if errors:
        print("problems (fix in the CSV and re-run):", *errors, sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main()
