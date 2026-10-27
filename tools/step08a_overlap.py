#!/usr/bin/env python3
"""Step 08a.4 / G08-9: USDA R6 vs Bognar 2002 bibliography overlap verdict.

  /opt/anaconda3/bin/python tools/step08a_overlap.py
Reads local raw files read-only; writes only the JSON and md report. Method: see
culinarystate.lineage.overlap. The USDA retn06.txt is the data table (no bibliography); its
reference list is in retn06.pdf, converted in memory with pdftotext. Verdict is the agent's,
pending the expert reading (THR-08A-11 / G08-9 human step).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.lineage.overlap import (  # noqa: E402
    cites_title, extract_references, match, normalise_key, verdict)

L1_KEY = "L1 ingredient-level: USDA-RETN-R6 vs BOGNAR-2002"
L2_KEY = "L2 food-group x step-family: USDA-RETN-R6 vs BOGNAR-2002"
R6_TITLE = "Table of Nutrient Retention Factors"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _pdf_text(p: Path) -> str:
    return subprocess.run(["pdftotext", "-layout", str(p), "-"], check=True,
                          capture_output=True, text=True).stdout


def _md(d: dict) -> str:
    rows = lambda ks: "\n".join(f"- {k}" for k in ks) or "- (none)"
    return f"""# USDA R6 vs Bognar 2002: bibliography overlap (08a.4, G08-9)

Verdict (AGENT, pending expert reading; THR-08A-11 vocabulary): **{d['verdict']}**

## Method
{d['method']}

## Counts
- USDA R6 references extracted: {d['usda_reference_count']}
- Bognar 2002 references extracted: {d['bognar_reference_count']}
- Exact matches: {d['exact_match_count']}
- Fuzzy matches (separate): {d['fuzzy_match_count']}

Exact matches (surname, year, journal):
{rows(d['exact_matches'])}

Fuzzy matches (surname, year, journal):
{rows(d['fuzzy_matches'])}

## Compilation-to-compilation citation (separate from the primary-source verdict)
Bognar entries citing the USDA retention table (surname, year): {d['bognar_cites_usda_retention_table']}.
This is a direct citation of an earlier release of the same table family, not a shared primary
source, so it does not change the mechanical verdict, but the expert should weigh it for independence.

## Cells affected if overlap were real
L1 USDA-vs-Bognar cells: {d['cells_affected_if_overlap']['L1']}; L2 cells: {d['cells_affected_if_overlap']['L2']}
(all cells of the pair; cross_source_v1.json counts only).

## Limitations
{chr(10).join('- ' + x for x in d['limitations'])}
"""


def build(usda_text: str, bognar_text: str, cs: dict, inputs: dict) -> dict:
    ua, bo = extract_references(usda_text), extract_references(bognar_text)
    m = match(ua, bo)
    return {
        "step": "08a.4", "gate": "G08-9", "threshold": "THR-08A-11",
        "verdict": verdict(ua, bo, m),
        "verdict_author": "AGENT; expert reading pending (human step of G08-9)",
        "method": ("Extract each reference list, normalise (lowercase, accent-fold, strip "
                   "punctuation) to surname|year|first 3 title words. Exact = equal key. "
                   "Fuzzy = same surname, year within 1, title-word Jaccard >= 0.5. "
                   "NOT_DETERMINABLE if a list is empty or any entry lacks surname or year."),
        "usda_reference_count": len(ua), "bognar_reference_count": len(bo),
        "usda_keys": sorted(normalise_key(r) for r in ua),
        "bognar_keys": sorted(normalise_key(r) for r in bo),
        "exact_match_count": m.exact_count, "fuzzy_match_count": m.fuzzy_count,
        "exact_matches": [f"{s}|{y}|{v}" for s, y, v in m.exact],
        "fuzzy_matches": [f"{s}|{y}|{v}" for s, y, v in m.fuzzy],
        "bognar_cites_usda_retention_table": [f"{s}|{y}" for s, y in cites_title(bo, R6_TITLE)],
        "cells_affected_if_overlap": {"L1": cs[L1_KEY]["overlap_cells"],
                                      "L2": cs[L2_KEY]["overlap_cells"]},
        "inputs": inputs,
        "limitations": [
            "Only the two printed reference lists were compared; neither names the primary papers behind individual retention values.",
            "Bibliography overlap is a necessary-not-sufficient signal: shared underlying data without shared citations is not detectable here.",
            "USDA R6 retn06.txt is the data table; its bibliography comes from retn06.pdf via pdftotext (layout text, in memory).",
            "Fuzzy matching is deliberately conservative (surname, year +-1, title overlap) and may miss differently transliterated or untitled entries.",
            "Bognar [4] (online database) and [11] (unpublished data) are keyed like any other entry.",
        ],
    }


def main() -> None:
    raw = ROOT / "data" / "raw"
    ap = argparse.ArgumentParser()
    ap.add_argument("--usda-pdf", type=Path, default=raw / "usda_r6" / "retn06.pdf")
    ap.add_argument("--usda-text", type=Path, help="pre-extracted USDA text (overrides --usda-pdf)")
    ap.add_argument("--bognar-text", type=Path, default=raw / "bognar" / "bognar_2002.txt")
    ap.add_argument("--cross-source", type=Path, default=ROOT / "reports/del2/cross_source_v1.json")
    ap.add_argument("--out-json", type=Path, default=ROOT / "reports/step08/usda_bognar_overlap_v1.json")
    ap.add_argument("--out-md", type=Path, default=ROOT / "reports/step08/usda_bognar_overlap_v1.md")
    a = ap.parse_args()
    usda_src = a.usda_text or a.usda_pdf
    usda = a.usda_text.read_text() if a.usda_text else _pdf_text(a.usda_pdf)
    d = build(usda, a.bognar_text.read_text(), json.loads(a.cross_source.read_text()),
              {"usda_source_sha256": _sha(usda_src), "bognar_txt_sha256": _sha(a.bognar_text)})
    a.out_json.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
    a.out_md.write_text(_md(d))
    print(d["verdict"], d["usda_reference_count"], d["bognar_reference_count"],
          d["exact_match_count"], d["fuzzy_match_count"])


if __name__ == "__main__":
    main()
