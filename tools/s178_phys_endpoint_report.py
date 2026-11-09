#!/usr/bin/env python
"""Corpus count of endpoint cues per heat event (S178 PHYS2, T4-C03-R1): counts only, from the Layer 1 census reports. DRAFT, AI_DRAFTED.

    python tools/s178_phys_endpoint_report.py --census FOODCOM=reports/step26/binding_census_L1_FOODCOM_full_S178_v04.json [...] \
        --out reports/s178/phys/endpoint_cue_counts_S178.json --out-md reports/s178/phys/endpoint_cue_counts_S178.md

Reads the ``endpoint_cues`` block of each Layer 1 heat census (written by ``binding_census`` from the ``endpoint`` block of every heat
event record). The endpoint cues are stored outside ``inputs`` and never enter a feature row (SSOT 199.8; the leakage test is
tests/unit/test_s178_phys2_l1.py). Never overwrites.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.quantity import rc2_dryrun as D  # noqa: E402


def _sum_nested(dicts: list[dict]) -> dict:
    out: dict = {}
    for d in dicts:
        for k, v in d.items():
            if isinstance(v, dict):
                out[k] = _sum_nested([x for x in (out.get(k), v) if x])
            else:
                out[k] = out.get(k, 0) + v
    return out


def summarise(blocks: dict[str, dict]) -> dict:
    rows = {}
    for fam, b in blocks.items():
        n, w = b["heat_events"], b["heat_events_with_cue"]
        hist = b["cues_per_event"]
        total_cues = sum(int(k) * v for k, v in hist.items())
        cls = b["cue_class"]
        rows[fam] = {"heat_events": n, "heat_events_with_cue": w, "share_with_cue": round(w / n, 4) if n else None,
                     "cues_total": sum(cls.values()), "cues_per_event": hist, "cue_class": cls,
                     "unclassified_until_clause_share_of_cues": round(cls.get("UNTIL_CLAUSE_UNCLASSIFIED", 0) / max(1, sum(cls.values())), 4),
                     "target_food_temperature_cues": cls.get("TARGET_FOOD_TEMPERATURE", 0),
                     "stopping_criterion_class": b["stopping_criterion_class"], "events_with_cue_by_family": b["events_with_cue_by_family"],
                     "cue_and_duration_by_family": b["cue_and_duration_by_family"],
                     "cue_without_duration_by_family": b["cue_without_duration_by_family"],
                     "cue_without_temperature_by_family": b["cue_without_temperature_by_family"], "cue_trigger": b["cue_trigger"],
                     "extractor_version": b["extractor_version"], "stored_outside_inputs": b["stored_outside_inputs"]}
        _ = total_cues
    allb = {"heat_events": sum(r["heat_events"] for r in rows.values()), "heat_events_with_cue": sum(r["heat_events_with_cue"] for r in rows.values()),
            "cue_class": _sum_nested([r["cue_class"] for r in rows.values()]),
            "cues_per_event": _sum_nested([r["cues_per_event"] for r in rows.values()]),
            "events_with_cue_by_family": _sum_nested([r["events_with_cue_by_family"] for r in rows.values()]),
            "cue_without_duration_by_family": _sum_nested([r["cue_without_duration_by_family"] for r in rows.values()]),
            "cue_without_temperature_by_family": _sum_nested([r["cue_without_temperature_by_family"] for r in rows.values()])}
    allb["share_with_cue"] = round(allb["heat_events_with_cue"] / allb["heat_events"], 4) if allb["heat_events"] else None
    return {"all_non_bbc_families": allb, "by_source_family": rows}


def markdown(rep: dict) -> str:
    a = rep["summary"]["all_non_bbc_families"]
    L = ["# Endpoint cues per heat event, non-BBC corpus (S178 PHYS2, T4-C03-R1)", "",
         "Status: DRAFT / AI_DRAFTED, counts only. Endpoint cues (\"until golden\", \"until tender\", \"until reduced by half\", a food-probe target "
         "temperature) are stored in the `endpoint` block of each Layer 1 heat record, outside `inputs`, and never enter a feature row (SSOT 199.8). "
         "The lexicon is `registry/endpoint_cue_lexicon_v1.csv` (AI_DRAFTED); a clause with a trigger and no lexicon word is counted as "
         "UNTIL_CLAUSE_UNCLASSIFIED, not dropped.", "",
         f"**All non-BBC families: {a['heat_events']:,} heat events, {a['heat_events_with_cue']:,} with at least one endpoint cue ({a['share_with_cue']:.1%}).**", "",
         "| source family | heat events | with a cue | share | cues | unclassified share of cues | target-temperature cues |", "|---|---:|---:|---:|---:|---:|---:|"]
    for fam, r in rep["summary"]["by_source_family"].items():
        share = "n/a" if r["share_with_cue"] is None else r["share_with_cue"]
        L.append(f"| {fam} | {r['heat_events']:,} | {r['heat_events_with_cue']:,} | {share} | {r['cues_total']:,} | "
                 f"{r['unclassified_until_clause_share_of_cues']} | {r['target_food_temperature_cues']} |")
    L += ["", "## Cue classes (all non-BBC families)", "", "| class | cues |", "|---|---:|"]
    L += [f"| {k} | {v:,} |" for k, v in sorted(a["cue_class"].items(), key=lambda kv: -kv[1])]
    L += ["", "## Cues per heat event", "", "| cues in the event | events |", "|---|---:|"]
    L += [f"| {k}{'+' if k == '3' else ''} | {v:,} |" for k, v in sorted(a["cues_per_event"].items())]
    L += ["", "## By heat family: events with a cue; cue with no stated duration; cue with no stated temperature", "",
          "| heat family | events with a cue | cue and no duration | cue and no temperature |", "|---|---:|---:|---:|"]
    for f in sorted(a["events_with_cue_by_family"]):
        L.append(f"| {f} | {a['events_with_cue_by_family'].get(f, 0):,} | {a['cue_without_duration_by_family'].get(f, 0):,} | "
                 f"{a['cue_without_temperature_by_family'].get(f, 0):,} |")
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--census", nargs="+", required=True, help="FAMILY=path to a Layer 1 heat census JSON")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    a = ap.parse_args(argv)
    for p in (a.out, a.out_md):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    blocks, shas = {}, {}
    for item in a.census:
        fam, _, path = item.partition("=")
        if not fam or not path:
            ap.error("--census wants FAMILY=path")
        raw = Path(path).read_bytes()
        blocks[fam] = json.loads(raw)["endpoint_cues"]
        shas[fam] = hashlib.sha256(raw).hexdigest()
    rep = {"record": "ENDPOINT_CUE_COUNTS", "status": "AI_DRAFTED_COUNTS_ONLY", "contains_ids": False, "contains_text": False, "citable": False,
           "counts_as_human_gate": False, "summary": summarise(blocks), "source_census_sha256": shas,
           "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    D.write_report(a.out, rep, root=ROOT)
    a.out_md.write_text(markdown(rep), encoding="utf-8")
    print(json.dumps({"families": list(blocks), "report_sha256": hashlib.sha256(a.out.read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
