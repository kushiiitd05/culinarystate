#!/usr/bin/env python3
"""S116: classify raw->cooked/processed rows in official FAO/INFOODS and USDA yield files as TRANSITION-EVIDENCE CANDIDATES.
Never infers that raw row + cooked row is a controlled before/after pair; classes:
  MATCHED_EXPERIMENT | SAME_STUDY_UNMATCHED | CROSS_STUDY_COMPARISON | COMPILED_REFERENCE | QUALITATIVE_ONLY

  /opt/anaconda3/bin/python tools/infoods_transition_candidates.py     (reads data/external/{infoods,usda_yields}, local only)
Writes reports/sources/infoods_transition_candidates.csv (no recipe text, no copyrighted tables: ids, names, classes only).
"""
import csv
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "data" / "external"
OUT = ROOT / "reports" / "sources" / "infoods_transition_candidates.csv"
FIELDS = ["source", "record_id", "food", "initial_state", "final_state", "process", "quantity", "evidence_class", "provenance_ref", "reason"]


def classify_ufish_row(ref_id: str, raw_ref_ids: set[str]) -> tuple[str, str]:
    ref = (ref_id or "").strip().lower()
    if ref.startswith("calc"):
        return "COMPILED_REFERENCE", "cooked/processed value is CALCULATED from the raw row (not an independent measurement)"
    if ref and ref in raw_ref_ids:
        return "SAME_STUDY_UNMATCHED", "raw and cooked rows share a reference id but sample pairing is not stated"
    return "CROSS_STUDY_COMPARISON" if ref else "QUALITATIVE_ONLY", "different/unstated references"


def ufish(rows):
    x = pd.ExcelFile(EXT / "infoods" / "uFiSh1.0.xlsx")
    d = x.parse("04 NV_sum (per 100 g EP)", header=None).iloc[2:, :7]
    d.columns = ["id", "isscaap", "alpha3", "name", "habitat", "state", "ref"]
    raw_refs = set()
    for r in d[d.state == "r"].ref.astype(str):
        raw_refs |= {p.strip().lower() for p in r.split(",")}
    for _, r in d[d.state.isin(["c", "p"])].iterrows():
        cls, why = classify_ufish_row(str(r.ref), raw_refs)
        rows.append({"source": "uFiSh1.0 NV_sum", "record_id": r["id"], "food": r["name"], "initial_state": "raw", "final_state": r.state,
                     "process": "", "quantity": "nutrient values (per 100 g EP)", "evidence_class": cls, "provenance_ref": str(r.ref)[:80], "reason": why})
    y = x.parse("09 Yield Factors", header=None).iloc[4:, :8]
    y.columns = ["id", "alpha3", "name", "yf", "method", "comment", "stats", "reference"]
    for _, r in y[y.yf.notna() & y.id.astype(str).str.fullmatch(r"\d{6}")].iterrows():
        rows.append({"source": "uFiSh1.0 Yield Factors", "record_id": r["id"], "food": r["name"], "initial_state": "raw", "final_state": "cooked",
                     "process": r.method, "quantity": f"yield factor {r.yf} ({r.stats})", "evidence_class": "COMPILED_REFERENCE",
                     "provenance_ref": str(r.reference)[:80], "reason": "compiled yield factor with literature reference and n"})


def usda_yields(rows):
    d = pd.read_csv(EXT / "usda_yields" / "cooking_yields_meat_poultry_r2.csv")
    d.columns = [c.strip() for c in d.columns]
    for _, r in d.iterrows():
        ah102 = int(r["Release Year2"]) == 1975
        rows.append({"source": "USDA Cooking Yields Meat&Poultry R2 (CC0)", "record_id": f"NDB{r['NDB']}", "food": r["Yield Description"][:90],
                     "initial_state": "raw", "final_state": "cooked", "process": r["Preparation Method1"],
                     "quantity": f"yield {r['Cooking Yield %']}% n={r['n']} SD={r['SD']} moisture {r['Moisture Gain/ Loss %']}% fat {r['Fat   Gain/ Loss %']}%",
                     "evidence_class": "COMPILED_REFERENCE", "provenance_ref": "AH-102 (1975)" if ah102 else f"USDA studies {r['Release Year2']}",
                     "reason": "compiled mean over USDA cooking studies; moisture/fat change absent for 1975 AH-102 items" if ah102 else "compiled mean over USDA cooking studies with n, SD, moisture and fat change"})


def anfood(rows):
    x = pd.ExcelFile(EXT / "infoods" / "AnFooD2.0.xlsx")
    for s in x.sheet_names[3:15]:
        d = x.parse(s, header=None).iloc[3:, :13]
        d = d[d[0].notna()]
        d.columns = ["id", "country", "own", "name", "proc", "sci", "season", "other", "n", "comment", "year", "biblio", "compiler"]
        raw = d[d.proc == "r"]
        for _, p in d[d.proc == "p"].iterrows():
            same = raw[(raw.sci == p.sci) & (raw.country == p.country) & (raw.biblio == p.biblio)]
            rows.append({"source": f"AnFooD2.0 {s}", "record_id": p["id"], "food": str(p["name"])[:80], "initial_state": "raw" if len(same) else "unknown",
                         "final_state": "processed (unspecified)", "process": "", "quantity": "nutrient values",
                         "evidence_class": "SAME_STUDY_UNMATCHED" if len(same) else "QUALITATIVE_ONLY",
                         "provenance_ref": f"bib {p.biblio}", "reason": "same species, place and bibliography as a raw row; process not specified" if len(same) else "no matching raw row"})


def main():
    rows: list[dict] = []
    for f in (ufish, usda_yields, anfood):
        try:
            f(rows)
        except FileNotFoundError as e:
            print("MISSING", e, file=sys.stderr)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter((r["source"].split()[0], r["evidence_class"]) for r in rows))


if __name__ == "__main__":
    main()
