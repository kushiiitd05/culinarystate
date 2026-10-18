#!/usr/bin/env python3
"""UNIT- ledger records (+ SRC for each unit authority/convention) from quantity/units.py.

  /opt/anaconda3/bin/python tools/build_unit_registry.py
Convention sources marked NEEDS_SOURCE keep verification status NEEDS_SOURCE until a human cites an authority.
"""
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.quantity.units import SOURCES, UNITS  # noqa: E402

KIND = {"AUTHORITY": "AUTHORITY_STANDARD", "CONVENTION": "PROJECT"}
DIM = {"MASS": "MASS", "VOLUME": "VOLUME", "COUNT": "COUNT", "LENGTH": "LENGTH", "NONE": "NONE"}
TYPE = {"REGIONAL": "CULINARY_VOLUME", "LENGTH": "PHYSICAL"}

st = LedgerStore()
counts = Counter()
src_ids = {}
for key, (title, kind, status) in SOURCES.items():
    rid = st.ids.mint("SRC", key=f"unitsrc:{key}")
    src_ids[key] = rid
    rec = {"id": rid, "record_type": "SRC", "status": "ACTIVE", "created_by": "Kush+Claude",
           "provenance": {"method": "MANUAL", "source_ids": [], "agent": "units.py@0.1"},
           "verification": {"status": "NEEDS_SOURCE" if status == "NEEDS_SOURCE" else "AI_PRECHECKED",
                            "ai_reviewer": "claude-opus-5-5",
                            "notes": "definition recalled by AI; human to confirm citation" if status != "NEEDS_SOURCE"
                            else "convention widely used; authority not yet cited"},
           "kind": KIND[kind], "title": title, "licence": "public standard / convention",
           "licence_status": "ASSUMED", "storage_rule": "COMMIT_OK", "primary_or_secondary": "PRIMARY"
           if kind == "AUTHORITY" else "UNKNOWN", "source_family_id": f"UNITSRC-{key}"}
    counts[("SRC", st.upsert(rec)[0])] += 1

rows = []
for u in UNITS:
    rid = st.ids.mint("UNIT", key=f"name:{u.key}")
    convs = [{"locale": loc, "si_value": {"status": "MEASURED", "value": ml, "unit": "mL"}, "source_ids": [src_ids[s]]}
             for loc, (ml, s) in sorted(u.conventions.items())]
    srcs = sorted({src_ids[u.si_source]} if u.si_source else set()) + sorted({src_ids[s] for _, s in u.conventions.values()})
    needs = any(SOURCES[s][2] == "NEEDS_SOURCE" for _, s in u.conventions.values())
    unit_type = TYPE.get(u.unit_type, u.unit_type)
    rec = {"id": rid, "record_type": "UNIT", "status": "ACTIVE", "created_by": "Kush+Claude",
           "provenance": {"method": "MANUAL", "source_ids": list(dict.fromkeys(srcs)), "agent": "units.py@0.1"},
           "verification": {"status": "NEEDS_SOURCE" if needs else "UNVERIFIED"},
           "canonical_name": u.key, "aliases": list(u.aliases), "unit_type": unit_type, "dimension": DIM[u.dimension],
           "si_unit": {"MASS": "g", "VOLUME": "mL", "LENGTH": "cm"}.get(u.dimension) if u.si or u.conventions else None,
           "conventions": convs, "ambiguity_notes": u.note or None,
           "external_refs": [f"si_factor:{u.si}"] if u.si else []}
    if u.unit_type == "REGIONAL":
        rec["ambiguity_notes"] = (u.note or "") + " [REGIONAL: no standard volume]"
    counts[("UNIT", st.upsert(rec)[0])] += 1
    rows.append({"unit_id": rid, "unit": u.key, "type": u.unit_type, "dimension": u.dimension, "si_factor": u.si,
                 "conventions": "; ".join(f"{k}={v[0]:g}mL[{v[1]}]" for k, v in sorted(u.conventions.items())),
                 "needs_source": needs, "aliases": "|".join(u.aliases)})
out = ROOT / "registry" / "units"
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(out / "unit_registry_v1.csv", index=False)
print(dict(counts), "->", out / "unit_registry_v1.csv")
