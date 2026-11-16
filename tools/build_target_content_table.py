#!/usr/bin/env python
"""Build registry/ing_sr_target_content_draft_v1.csv: SR Legacy content of each screened nutrient for the rank 1-3 SR
candidates (any band) of every ING with a usable identity (S176 L-ROUTER; S177 SCIFIX-ROUTER).

Identity source (S177, consolidation review 5.3): ``--identity defaults`` (default) takes the ING -> SR identity from the Mac's
curated registry ``registry/ing_sr_defaults_v1.csv`` through ``mechanism/sr_identity.py`` (DIRECT / UK_US / DEFAULT_FORM HIGH,
APPROX MEDIUM; the legacy lexical file only as alternates and a fallback capped at MEDIUM). ``--identity legacy`` rebuilds
the first S177 table (the legacy match file alone) with identity_source = legacy_match_only, for comparison runs. The ING
category and the SR food group of the rank-1 candidate are carried for the ABSENT category crosswalk. AI_DRAFTED, derived from
public-domain SR Legacy values and AI-proposed identities. The evidence gates read this table at run time, so the demo needs
no data/raw. S178 (FIX-ROUTER, SCI-B R4): every value also carries its SR derivation code (``sr_derivation_code``; NONE for a
blank derivation_id) and number of data points (``sr_data_points``), so the ABSENT screen can require analytical values.

    python tools/build_target_content_table.py [--identity defaults|legacy] [--out registry/ing_sr_target_content_draft_v1.csv] [--check]

``--check`` rebuilds in memory and exits 1 if the committed table differs (no write). Refuses to overwrite without
``--force``. Reads: registry/target_presence_floor_v1_PROPOSED.csv (which nutrient keys), registry/ing_sr_defaults_v1.csv,
registry/ing_sr_legacy_match_draft_v1.csv, ledgers/data/{ING,ALIAS}.jsonl and data/raw/fdc/sr_legacy (all read only).
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.mechanism import evidence_gates as EG  # noqa: E402
from culinarystate.mechanism import sr_identity as SI  # noqa: E402


def build(identity: str = "defaults") -> str:
    if identity not in ("defaults", "legacy"):
        raise ValueError("identity is 'defaults' or 'legacy'")
    floors = EG.read_floors()
    keys = sorted({f.nutrient_key for f in floors.values()})
    if identity == "defaults":
        idn = SI.build_identity(root=ROOT)
        recs = EG.read_sr_records(SI.default_dir(ROOT), {f for c in idn.cands.values() for f, _, _ in c}, keys)
        rows = SI.table_rows(idn, {k: v[0] for k, v in recs.items()}, keys, {k: (v[1], v[2]) for k, v in recs.items()})
    else:
        cands = EG.read_candidates()
        recs = EG.read_sr_records(SI.default_dir(ROOT), {f for c in cands.values() for f, _, _ in c}, keys)
        rows = EG.build_table_rows(cands, {k: v[0] for k, v in recs.items()}, keys, EG.read_categories(),
                                   {k: (v[1], v[2]) for k, v in recs.items()})
        for r in rows:
            r["identity_source"] = SI.LEGACY_SOURCE
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=EG.TABLE_COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(EG.TABLE_PATH))
    ap.add_argument("--identity", choices=("defaults", "legacy"), default="defaults")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    text, out = build(a.identity), Path(a.out)
    if a.check:
        same = out.exists() and out.read_text(encoding="utf-8") == text
        print("TABLE_MATCHES_REBUILD" if same else "TABLE_DIFFERS_OR_MISSING")
        return 0 if same else 1
    if out.exists() and not a.force:
        ap.error("refusing to overwrite an existing table (use --force)")
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({text.count(chr(10)) - 1} rows, identity={a.identity})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
