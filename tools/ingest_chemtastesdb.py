#!/usr/bin/env python3
"""X11: ChemTastesDB v2.1 (Zenodo 15051366, CC BY 4.0) -> KGE MOL_HAS_TASTE for molecules already in MOL.

  /opt/anaconda3/bin/python tools/ingest_chemtastesdb.py
Join key: PubChem CID (MOL.pubchem_cid). Molecules not yet in MOL are counted, not created (scope: compounds that
already connect to ingredients/evidence). Confidence 0.9 (curated literature labels), band MEDIUM (not verified here). Object = the curated "Class taste"
(10 classes: Bitterness, Sweetness, Umaminess, Multitaste, ...); the free-text "Taste" label stays in notes.
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import sha256_file  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

XLSX = ROOT / "data" / "raw" / "chemtastesdb" / "ChemTastesDB_database.xlsx"
CB, AGENT = "Kush+Claude", "chemtastesdb@0.1"


def main() -> None:
    st = LedgerStore()
    df = pd.read_excel(XLSX)
    sid = st.ids.mint("SRC", key="chemtastesdb:v2.1")
    st.upsert({"id": sid, "record_type": "SRC", "status": "ACTIVE", "created_by": CB,
               "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
               "kind": "DATABASE", "title": "ChemTastesDB: A Curated Database of Molecular Tastants (v2.1)",
               "url": "https://zenodo.org/records/15051366", "year": 2025, "licence": "CC BY 4.0",
               "licence_status": "VERIFIED", "storage_rule": "COMMIT_OK", "primary_or_secondary": "SECONDARY",
               "source_family_id": "CHEMTASTESDB", "notes": f"{len(df)} tastants; sha256 {sha256_file(XLSX)[:16]}"})
    by_cid = {}
    for m in st.all_latest("MOL"):
        if m["status"] == "ACTIVE" and m.get("pubchem_cid"):
            by_cid[int(m["pubchem_cid"])] = m["id"]
    w, matched, tastes, live = Counter(), 0, Counter(), set()
    for r in df.itertuples():
        cid = pd.to_numeric(r[3], errors="coerce")
        if pd.isna(cid) or int(cid) not in by_cid:
            continue
        matched += 1
        mid = by_cid[int(cid)]
        taste = str(r[7]).strip()
        tastes[taste] += 1
        kid = st.ids.mint("KGE", key=f"MOL_HAS_TASTE|{mid}|{taste}|CHEMTASTESDB")
        live.add(kid)
        w[st.upsert({"id": kid, "record_type": "KGE",
                     "status": "ACTIVE", "created_by": CB,
                     "provenance": {"method": "IMPORT", "source_ids": [sid], "agent": AGENT,
                                    "locator": f"ChemTastesDB ID {r.ID} ({r.Name}); refs {str(r[8])[:120]}"},
                     "verification": {"status": "UNVERIFIED"}, "predicate": "MOL_HAS_TASTE", "subject_id": mid,
                     "object_id": None, "object_value": taste, "support": {"recipes": 0},
                     "confidence": 0.9, "confidence_band": "MEDIUM", "method": "EXTERNAL_SOURCE",
                     "corpus_ids": ["CHEMTASTESDB"], "notes": f"label: {r.Taste}"})[0]] += 1
    for old in st.all_latest("KGE"):                  # edges no longer derived (e.g. v0 free-text objects)
        if old["status"] == "ACTIVE" and old["id"] not in live and old["provenance"].get("agent") == AGENT:
            w["deprecated"] += st.upsert({**old, "status": "DEPRECATED", "notes": "no longer derived"})[0] == "revised"
    lines = ["# ChemTastesDB v2.1 -> MOL_HAS_TASTE (X11)", "",
             f"- tastants: {len(df):,}; MOL with PubChem CID: {len(by_cid):,}; matched: {matched:,}",
             f"- tastes among matched: {dict(tastes.most_common())}", f"- KGE writes: {dict(w)}",
             "- unmatched tastants are not created as MOL (scope); re-run after MOL grows (FlavorGraph/FoodAtlas)."]
    (ROOT / "reports" / "chemtastesdb_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
