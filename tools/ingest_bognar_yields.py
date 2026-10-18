#!/usr/bin/env python3
"""X5b: Bognár (2002) Part 1 weight-yield factors -> EVD derived.yield_factor (source family BOGNAR-2002).

  /opt/anaconda3/bin/python tools/ingest_bognar_yields.py      (after tools/ingest_bognar.py: same SRC/SNAP)
One EVD per (row, portion): edible part e(k,p) and, where printed, with waste d(k,p). Yield = cooked / raw weight.
Pooled methods ("a/b" = boil or steam) are not a sequence: steps = ["cook"], methods kept in modifiers.
Core temperatures (meat tables) go to COND with their printed qualifier ("> 80" = stated lower bound).
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.conditions import extract_conditions, mask_status  # noqa: E402
from culinarystate.evidence.linker import keep_linker_fields  # noqa: E402
from culinarystate.ingest.acquire import fetch  # noqa: E402
from culinarystate.ingest.bognar_build import FAMILY, MEDIUM, _env, source_records  # noqa: E402
from culinarystate.ingest.bognar_yield import parse_yields  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

URL = "https://publikationen.bibliothek.kit.edu/9642002/1928"
PDF = ROOT / "data" / "raw" / "bognar" / "bognar_2002.pdf"
TXT = PDF.with_suffix(".txt")
VERSION = "bognar_yield@0.1"
STEP = {"fry in pan": "pan-fry", "fry in oven": "roast", "deep fry": "deep-fry", "contact fry": "contact-fry"}
TITLE = re.compile(r"^\x0c?Table (\d+)\s*:\s*Weight yield factors? (?:by|during) (?:cooking|preparation) of (.*)$", re.M)


def cond_record(st, src_id, r, key):
    temps = extract_conditions(f"core temperature {r.core_temp_c} °C")["temperatures"] if r.core_temp_c else []
    rec = {**_env(st, "COND", key, [src_id], locator=f"Part 1 table {r.table}"),
           "duration": {"status": "UNKNOWN", "raw": None},
           "completeness_mask": {"duration": "UNKNOWN", "ph": "UNKNOWN", "moisture": "UNKNOWN",
                                 "temperature": mask_status(temps[0]["value"]) if temps else "UNKNOWN"}}
    if temps:
        rec["temperatures"] = temps
    if len(r.methods) == 1 and MEDIUM.get(r.methods[0]):
        rec["medium"] = MEDIUM[r.methods[0]]
    return rec


def main() -> None:
    st = LedgerStore()
    snap = fetch(URL, PDF)
    text = TXT.read_text()
    titles = {int(m.group(1)): m.group(2).strip() for m in TITLE.finditer(text)}
    rows = parse_yields(text)
    src_id, base = source_records(st, snap)
    meas = {**_env(st, "MEAS", "bognar:weight_yield", [src_id], locator="Part 1 I. Determination of weight yield"),
            "family": "GRAVIMETRY", "basis": "FRESH_WEIGHT",
            "protocol": "weight yield factor = weight after cooking / weight before cooking; d(k,p) incl. waste, "
                        "e(k,p) edible part; mean of available data with 95% CI",
            "comparability_notes": "German recipes (m.Z); n per row; '-' = not available"}
    svar = {**_env(st, "SVAR", "bognar:food mass", [src_id]), "canonical_name": "food mass", "family": "PHYSICAL",
            "dimension": "mass", "value_type": "SCALAR", "observable_in_session": True}
    w = Counter()
    for rec in [*base, meas, svar]:
        w[(rec["record_type"], st.upsert(rec)[0])] += 1
    conds, live = {}, set()
    for r in rows:
        meth = "/".join(r.methods)
        ck = f"bognar:yield:T{r.table}:{meth}:{r.core_temp_c or '-'}"
        if ck not in conds:
            conds[ck] = cond_record(st, src_id, r, ck)
            w[("COND", st.upsert(conds[ck])[0])] += 1
        steps = [STEP.get(r.methods[0], r.methods[0])] if len(r.methods) == 1 else ["cook"]
        key = f"bognar:yield:T{r.table}:{r.description}:{'/'.join(r.raw_states)}:{r.recipe}:{meth}"
        if r.core_temp_c:                                  # same dish at several core temperatures (meat tables)
            key += f":core {r.core_temp_c}"
        for portion, x, ci in (("FOOD_EDIBLE_PART", r.edible, r.edible_ci), ("FOOD_INCL_WASTE", r.with_waste, r.with_waste_ci)):
            if x is None:
                continue
            yf = {"status": "MEASURED", "value": x, "unit": "fraction", "raw": f"{x:.2f}"}
            if ci is not None:
                yf["uncertainty"] = ci
            mods = {"portion": portion, "recipe": r.recipe, "raw_product": "/".join(r.raw_states),
                    "n": None if r.n is None else str(r.n), "ci_95": None if ci is None else str(ci),
                    "pooled_methods": meth if len(r.methods) > 1 else None,
                    "core_temperature_raw": r.core_temp_c, "cooked_by_producer_instruction": r.by_producer_instruction}
            evd = {**_env(st, "EVD", f"{key}:{portion}", [src_id],
                          locator=f"bognar_2002.txt line {r.line} (Part 1 table {r.table}, {portion})"),
                   "origin_type": "DATABASE_AGGREGATE", "source_id": src_id, "source_family_id": FAMILY,
                   "study_ids": [], "study_id_status": "NOT_IDENTIFIABLE", "extraction_version": VERSION,
                   "matrix": {"ingredient_id": None, "raw_name": r.description, "initial_state": "/".join(r.raw_states),
                              "form": "breaded" if "breaded" in r.description.lower() else None,
                              "food_group": titles.get(r.table)},
                   "process": {"process_id": None, "raw_name": meth, "steps": steps,
                               "modifiers": {k: v for k, v in mods.items() if v is not None},
                               "condition_id": conds[ck]["id"],
                               "medium": MEDIUM.get(r.methods[0]) if len(r.methods) == 1 else None},
                   "target": {"state_variable_id": svar["id"], "raw_name": "weight yield", "basis": "FRESH_WEIGHT"},
                   "measurement_method_id": meas["id"],
                   "derived": {"yield_factor": yf,
                               "direction": "DECREASE" if x < 1 else "INCREASE" if x > 1 else "NO_CHANGE"},
                   "design": "DATABASE_AGGREGATE", "tier": "E3", "applicability": "GENERIC", "censored": False,
                   "independence_group": FAMILY}
            w[("EVD", st.upsert(keep_linker_fields(st.latest(evd["id"]), evd))[0])] += 1
            live.add(evd["id"])
    for old in st.all_latest("EVD"):                      # records this builder no longer derives
        if old["status"] == "ACTIVE" and old.get("extraction_version") == VERSION and old["id"] not in live:
            w[("EVD", "deprecated")] += st.upsert({**old, "status": "DEPRECATED"})[0] == "revised"
    by_method = Counter(m for r in rows for m in r.methods)
    lines = ["# Bognár (2002) Part 1 weight yields (X5b)", "",
             f"- rows parsed: {len(rows)} from {len({r.table for r in rows})} tables (~94% of table rows; bakery table 31 "
             "single-column layout, juice code 'P' (no legend found) and sub-part rows not parsed)",
             f"- edible-part yields: {sum(r.edible is not None for r in rows)}; with-waste yields: "
             f"{sum(r.with_waste is not None for r in rows)}; core temperature printed: {sum(bool(r.core_temp_c) for r in rows)}",
             f"- methods: {dict(by_method.most_common())}",
             f"- ledger writes: {dict(w)}",
             "- use: yield × per-100 g ratio = true retention (FDC pairs, X15); weight change per process for DEL-3."]
    (ROOT / "reports" / "bognar_yields_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
