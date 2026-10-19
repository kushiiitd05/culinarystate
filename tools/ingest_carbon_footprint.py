#!/usr/bin/env python3
"""SU-EATABLE-LIFE-derived carbon footprints (via CoSyLab SustainableFoodDB, D-015) -> KGE ING_CARBON_FOOTPRINT.

  /opt/anaconda3/bin/python tools/ingest_carbon_footprint.py
One stat edge per ING whose normalised canonical name equals a FOOD COMMODITY ITEM (exact only; typology-level matches are
not used so a group value is never attached to a specific food). quantiles = p10/p50/p90/min/max over the literature
measurements, unit kgCO2e/kg (litre for drinks). Upstream licence of the commodity table is UNVERIFIED (noted in SRC).
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

CSV = ROOT / "data" / "external" / "sustainablefooddb" / "Sueatable_preprocessed_data.csv"
CB, AGENT = "Kush+Claude", "carbon_footprint@0.1"


def main() -> None:
    st = LedgerStore()
    d = pd.read_csv(CSV)
    col = [c for c in d.columns if c.startswith("Carbon footprint")][0]
    d = d.assign(item=d["FOOD COMMODITY ITEM"].map(lambda x: norm(str(x)))).dropna(subset=[col])
    sid = st.ids.mint("SRC", key="sueatable:carbon")
    st.upsert({"id": sid, "record_type": "SRC", "status": "ACTIVE", "created_by": CB,
               "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
               "kind": "DATABASE", "title": "SU-EATABLE LIFE carbon footprint table (as bundled in CoSyLab SustainableFoodDB)",
               "url": "https://github.com/cosylabiiit/SustainableFoodDB", "year": 2021,
               "licence": "No licence file in bundle; use permitted by Prof. Bagler (D-015); upstream SU-EATABLE LIFE licence UNVERIFIED",
               "licence_status": "ASSUMED", "storage_rule": "DERIVED_ONLY", "primary_or_secondary": "SECONDARY",
               "source_family_id": "SUEATABLE", "notes": f"{len(d)} literature measurements, {d['item'].nunique()} items"})
    w, n_edges = Counter(), 0
    for ing in st.all_latest("ING"):
        if ing["status"] != "ACTIVE":
            continue
        g = d[d["item"] == norm(ing["canonical_name"])][col].astype(float)
        if g.empty:
            continue
        q = {"n": int(len(g)), "unit": "kgCO2e/kg", "p10": float(np.percentile(g, 10)), "p50": float(g.median()),
             "p90": float(np.percentile(g, 90)), "min": float(g.min()), "max": float(g.max())}
        kid = st.ids.mint("KGE", key=f"ING_CARBON_FOOTPRINT|{ing['id']}|SUEATABLE")
        w[st.upsert({"id": kid, "record_type": "KGE", "status": "ACTIVE", "created_by": CB,
                     "provenance": {"method": "IMPORT", "source_ids": [sid], "agent": AGENT,
                                    "locator": f"Sueatable_preprocessed_data.csv item={norm(ing['canonical_name'])}"},
                     "verification": {"status": "UNVERIFIED"}, "predicate": "ING_CARBON_FOOTPRINT",
                     "subject_id": ing["id"], "object_id": None, "object_value": None, "quantiles": q,
                     "support": {"recipes": 0}, "confidence": 0.7, "confidence_band": "MEDIUM",
                     "method": "EXTERNAL_SOURCE", "corpus_ids": ["SUEATABLE"],
                     "notes": "literature LCA range; system boundary and country vary across measurements"})[0]] += 1
        n_edges += 1
    print(dict(w), "edges", n_edges)


if __name__ == "__main__":
    main()
