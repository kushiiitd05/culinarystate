#!/usr/bin/env python3
"""bittersweet (AGPL-3.0, github.com/cosylabiiit/bittersweet) -> KGE MOL_HAS_TASTE for molecules already in MOL.

  /opt/anaconda3/bin/python tools/ingest_bittersweet_kg.py
Join key: InChIKey connectivity block (first 14 chars), computed offline with RDKit from the SMILES. Only positive
labels become edges (Bitterness / Sweetness, the ChemTastesDB class vocabulary); negatives are not taste claims.
Unmatched molecules are counted, not created (same scope rule as X11). Raw TSVs stay under data/external (gitignored).
"""
import csv
import sys
from collections import Counter
from pathlib import Path

from rdkit import Chem, RDLogger

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.acquire import sha256_file  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

DIR = ROOT / "data" / "external" / "bittersweet"
FILES = {"bitter": ("Bitterness", "Bitter"), "sweet": ("Sweetness", "Sweet")}
CB, AGENT = "Kush+Claude", "bittersweet@0.1"


def ik14(smiles: str) -> str | None:
    m = Chem.MolFromSmiles(smiles)
    return Chem.MolToInchiKey(m)[:14] if m else None


def main() -> None:
    RDLogger.DisableLog("rdApp.*")
    st = LedgerStore()
    by_ik = {m["inchikey"][:14]: m["id"] for m in st.all_latest("MOL") if m["status"] == "ACTIVE"}
    sid = st.ids.mint("SRC", key="bittersweet:cosylab")
    st.upsert({"id": sid, "record_type": "SRC", "status": "ACTIVE", "created_by": CB,
               "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
               "kind": "DATABASE", "title": "bittersweet: bitter/sweet molecule datasets (CoSyLab, IIIT Delhi)",
               "url": "https://github.com/cosylabiiit/bittersweet", "year": 2020, "licence": "AGPL-3.0",
               "licence_status": "VERIFIED", "storage_rule": "COMMIT_OK", "primary_or_secondary": "SECONDARY",
               "source_family_id": "BITTERSWEET",
               "notes": "AGPL-3.0 copyleft: derived edges carry this provenance; sha256 of train TSVs in report"})
    seen, w, total, matched = set(), Counter(), 0, 0
    for kind, (cls, col) in FILES.items():
        for split in ("train", "test"):
            path = DIR / f"{kind}-{split}.tsv"
            for r in csv.DictReader(path.open(), delimiter="\t"):
                total += 1
                if r[col] != "True":
                    continue
                key = ik14(r["Canonical SMILES"] or r["SMILES"])
                mid = by_ik.get(key) if key else None
                if not mid:
                    continue
                matched += 1
                if (mid, cls) in seen:
                    continue
                seen.add((mid, cls))
                kid = st.ids.mint("KGE", key=f"MOL_HAS_TASTE|{mid}|{cls}|BITTERSWEET")
                w[st.upsert({"id": kid, "record_type": "KGE", "status": "ACTIVE", "created_by": CB,
                             "provenance": {"method": "IMPORT", "source_ids": [sid], "agent": AGENT,
                                            "locator": f"{path.name}: {r['Name'][:60]} ({r['Reference'][:60]})"},
                             "verification": {"status": "UNVERIFIED"}, "predicate": "MOL_HAS_TASTE",
                             "subject_id": mid, "object_id": None, "object_value": cls,
                             "support": {"recipes": 0}, "confidence": 0.8, "confidence_band": "MEDIUM",
                             "method": "EXTERNAL_SOURCE", "corpus_ids": ["BITTERSWEET"],
                             "notes": "literature-curated label; positive class only"})[0]] += 1
    lines = ["# bittersweet -> MOL_HAS_TASTE", "",
             f"- rows read: {total:,}; positive rows matched to MOL: {matched:,}; distinct edges: {len(seen):,}",
             f"- KGE writes: {dict(w)}", "- licence AGPL-3.0 (verified: LICENSE file in repo); unmatched not created as MOL.",
             f"- train TSV sha256: bitter {sha256_file(DIR / 'bitter-train.tsv')[:16]}, "
             f"sweet {sha256_file(DIR / 'sweet-train.tsv')[:16]}"]
    (ROOT / "reports" / "bittersweet_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
