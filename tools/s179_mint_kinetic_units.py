#!/usr/bin/env python
"""S179 (T5-C07-R5, D-079): mint the 11 kinetic unit rows of registry/kinetic_units_v1_DRAFT.csv into the UNIT ledger.

Append-only through LedgerStore (validated against the D-079 schema; ids minted by IdMinter with key
``kinetic_unit:<KU-key>`` so a re-run mints nothing new). Refuses if any kinetic row is already in the ledger.

    /opt/anaconda3/bin/python tools/s179_mint_kinetic_units.py [--execute]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore, now_iso  # noqa: E402
from culinarystate.ledgers.validate import errors  # noqa: E402
from culinarystate.mechanism import kinetic_unit_registry as K  # noqa: E402

LED = ROOT / "ledgers" / "data"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args()
    if problems := K.check_rows():
        sys.exit(f"draft registry has problems: {problems}")
    if K.ledger_unit_ids(LED / "UNIT.jsonl"):
        sys.exit("refusing: kinetic rows already in the UNIT ledger")
    rows = K.read_rows()
    preview = K.unit_records(0, rows=rows, created_by="Kush+Claude", created_at=now_iso(),
                             ids=[f"UNIT-{0:06d}"] * len(rows))
    bad = {r["canonical_name"]: errors({**r, "id": "UNIT-000001"}) for r in preview}
    if any(bad.values()):
        sys.exit(f"schema errors: {bad}")
    if not a.execute:
        print(json.dumps([{k: r[k] for k in ("canonical_name", "dimension", "external_refs", "verification")}
                          for r in preview], indent=1))
        print("dry run: pass --execute to mint")
        return 0
    store = LedgerStore(LED)
    ids = [store.ids.mint("UNIT", f"kinetic_unit:{r['proposed_key']}") for r in rows]
    for rec in K.unit_records(0, rows=rows, created_by="Kush+Claude", created_at=now_iso(), ids=ids):
        store.append(rec)
    print("minted", ids[0], "..", ids[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
