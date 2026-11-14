#!/usr/bin/env python
"""v04 -> v05 comparison of the non-BBC physical layers (S178 FIX-PHYS). Counts only, read from run reports. DRAFT, AI_DRAFTED.

Reuses the PHYS2 comparison functions (``tools/s178_phys_v04_comparison.py``) on the reports v04 (S178 PHYS2: Layer 1 0.2.0, Layer 2
0.4.0) -> v05 (FIX-PHYS: heat and non-heat Layer 1 0.3.0, Layer 2 0.5.0) for FOODCOM, GUTENBERG_SEGMENT, WIKIBOOKS and TASTESET, and
adds the FIX-PHYS counters (the until-clause check and cue axes of the v05 Layer 1 census, the Q1 lift-gate / moist-piece / water-bath
flags of the v05 Layer 2 report) and the before / after record audit of ``tools/s178_phys_fixphys_audit.py`` (``--audit-before`` /
``--audit-after``). Nothing here is a new measurement; ``source_report_sha256`` names each input.

    python tools/s178_fixphys_v05_comparison.py --audit-before reports/s178/phys/fixphys_audit_S178_v04.json \
        --audit-after reports/s178/phys/fixphys_audit_S178_v05.json \
        --out reports/s178/phys/v04_to_v05_comparison_S178.json --out-md reports/s178/phys/v04_to_v05_comparison_S178.md
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

_spec = importlib.util.spec_from_file_location("_s178_phys_v04_comparison", ROOT / "tools/s178_phys_v04_comparison.py")
V4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V4)

VERSION = "s178-fixphys-v05-comparison-0.1.0"
FAMILIES = V4.FAMILIES
SOURCES = {
    "heat_l1": ("binding_census_L1_{f}_full_S178_v04.json", "binding_census_L1_{f}_full_S178_v05.json"),
    "heat_l2": ("scenario_L2_{f}_full_S178_v04.json", "scenario_L2_{f}_full_S178_v05.json"),
    "nonheat_l1": ("nonheat_L1_{f}_full_S178_v04.json", "nonheat_L1_{f}_full_S178_v05.json"),
    "nonheat_l2": ("nonheat_L2_{f}_full_S178_v04.json", "nonheat_L2_{f}_full_S178_v05.json")}
AUDIT_KEYS = ("until_clause_bound_temperature_reviewer_method", "until_clause_bound_temperature_clause_spans",
              "until_clause_bound_temperature_clause_spans_syrup_exempt", "oven_text_stated_below_77",
              "oven_text_stated_below_77_core_computed", "lifted_typical", "lifted_typical_above_150", "lifted_typical_with_core",
              "lifted_typical_core_above_100", "moist_piece_core_above_tboil", "fat_heat_temperature_from_setter",
              "aqueous_above_100_from_setter", "aqueous_above_100_all", "l1_ambient_temperature", "l1_text_stated_range")


def heat_l2(a: dict, b: dict) -> dict:
    out = V4.heat_l2(a, {**b, "v03_to_v04": b.get("v04_to_v05", {})})
    out["v04_to_v05_event_comparison"] = out.pop("v03_to_v04_event_comparison")
    out.pop("new_in_v04", None)
    out["fixphys_flag_typical"] = V4._g(b["counts"], "fixphys_flag_typical", default={})
    return out


def heat_l1(a: dict, b: dict) -> dict:
    out = V4.heat_l1(a, b)
    out["fixphys_layer1"] = b.get("fixphys_layer1", {})
    return out


def nonheat_l2(a: dict, b: dict) -> dict:
    out = V4.nonheat_l2(a, {**b, "v03_to_v04": b.get("v04_to_v05", {})})
    out["v04_to_v05_counts"] = out.pop("v03_to_v04_counts")
    return out


def nonheat_l1(a: dict, b: dict) -> dict:
    out = V4.nonheat_l1(a, b)
    out["endpoint_status_after"] = b.get("endpoint_status", {})
    return out


FN = {"heat_l1": heat_l1, "heat_l2": heat_l2, "nonheat_l1": nonheat_l1, "nonheat_l2": nonheat_l2}


def audit_pairs(before: dict | None, after: dict | None) -> dict:
    cb, ca = (before or {}).get("counts", {}), (after or {}).get("counts", {})
    keys = list(AUDIT_KEYS) + sorted(k for k in set(cb) | set(ca) if k.startswith(("lifted_typical|", "flag_typical|",
                                                                                    "moist_piece_core_above_tboil|", "l1_")))
    seen, out = set(), {}
    for k in keys:
        if k in seen:
            continue
        seen.add(k)
        out[re.sub(r"[^A-Za-z0-9_]", "_", k)] = V4._pair(cb.get(k, 0), ca.get(k, 0))
    return out


def superseded(r: Path) -> list[dict]:
    rows = []
    for kind, (old, _) in SOURCES.items():
        for f in FAMILIES:
            if (r / old.format(f=f)).exists():
                rows.append({"output": f"reports/step26/{old.format(f=f)}", "kind": kind, "status": "SUPERSEDED_BY_S178_v05"})
    return rows


def markdown(rep: dict) -> str:
    L = ["# v04 -> v05 comparison, non-BBC physical layers (S178 FIX-PHYS)", "",
         "Status: DRAFT / AI_DRAFTED, counts only, read from the run reports named in `source_report_sha256`. v04 = PHYS2 (Layer 1 0.2.0, "
         "Layer 2 0.4.0); v05 = FIX-PHYS (Layer 1 0.3.0: food targets, medium-compatible temperatures, window cut, ambient cues, cue axes; "
         "Layer 2 0.5.0: the Q1 lift gate, the moist-piece boundary, the water bath; non-heat Layer 1 0.3.0, Layer 2 0.5.0).", ""]
    au = rep.get("record_audit")
    if au:
        L += ["## Record audit (SCI-A figures, all non-BBC families)", "", "| counter | v04 | v05 | delta |", "|---|---:|---:|---:|"]
        L += [f"| {k} | {p['before']} | {p['after']} | {p['delta']} |" for k, p in au.items()]
        L.append("")
    for fam, d in rep["families"].items():
        h1, h2, n1, n2 = d["heat_l1"], d["heat_l2"], d["nonheat_l1"], d["nonheat_l2"]
        L += [f"## {fam}", "", "| quantity | v04 | v05 | delta |", "|---|---:|---:|---:|"]
        for k in ("heat_events", "driver_ready_events", "driver_bounded_events", "contract_bindings"):
            p = h1[k]
            L.append(f"| heat L1 {k} | {p['before']} | {p['after']} | {p['delta']} |")
        for k, p in h1["input_basis"]["temperature_profile"].items():
            L.append(f"| heat L1 temperature basis {k} | {p['before']} | {p['after']} | {p['delta']} |")
        for k, p in h2["status"].items():
            L.append(f"| heat L2 status {k} | {p['before']} | {p['after']} | {p['delta']} |")
        p = h2["stated_liquid_lifted_typical"]
        L.append(f"| heat L2 stated-liquid events lifted (TYPICAL) | {p['before']} | {p['after']} | {p['delta']} |")
        for k, p in h2["typical_core_reaches_70"].items():
            L.append(f"| heat L2 TYPICAL core reaches 70 C = {k} | {p['before']} | {p['after']} | {p['delta']} |")
        for k, p in h2["cap_flag_typical"].items():
            if k.startswith(("TBOIL_CAP_LOWER", "SUGAR_PHASE", "SALT_MEMBER", "STATED_LIQUID", "WATER_BATH")):
                L.append(f"| heat L2 cap flag {k} (TYPICAL) | {p['before']} | {p['after']} | {p['delta']} |")
        for f, p in n1["events_by_family"].items():
            L.append(f"| non-heat L1 events {f} | {p['before']} | {p['after']} | {p['delta']} |")
        for f, p in n2["computed_by_family"].items():
            L.append(f"| non-heat L2 computed {f} | {p['before']} | {p['after']} | {p['delta']} |")
        L.append("")
        ev = h2["v04_to_v05_event_comparison"]
        L.append(f"Heat L2 per-event comparison over {ev['events']} events: bath temperature changed (TYPICAL) "
                 f"{ev['counts'].get('bath_c_changed', {}).get('TYPICAL', 0)}; core end temperature changed "
                 f"{ev['counts'].get('changed', {}).get('TYPICAL', {}).get('core_end_c', 0)}; non-heat events whose status changed "
                 f"{sum(n2['events_whose_status_changed_by_family'].values())}. FIX-PHYS flags (TYPICAL): {h2['fixphys_flag_typical']}. "
                 f"Until-clause check (Layer 1): {h1['fixphys_layer1'].get('bound_text_stated_temperature_inside_an_until_clause_by_role', {})}.")
        L.append("")
    L += ["## SUPERSEDED outputs", "", "The v05 reports replace these v04 reports for the non-BBC families (kept for the audit trail).", ""]
    L += [f"- `{r['output']}` ({r['kind']})" for r in rep["superseded"]]
    L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    ap.add_argument("--audit-before", type=Path, default=None)
    ap.add_argument("--audit-after", type=Path, default=None)
    ap.add_argument("--reports-dir", type=Path, default=ROOT / "reports/step26")
    ap.add_argument("--families", nargs="+", default=list(FAMILIES))
    a = ap.parse_args(argv)
    for p in (a.out, a.out_md):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    r = a.reports_dir
    fams, shas = {}, {}
    for f in a.families:
        fams[f] = {}
        for kind, (old, new) in SOURCES.items():
            pa, pb = r / old.format(f=f), r / new.format(f=f)
            ja, jb = json.loads(pa.read_text(encoding="utf-8")), json.loads(pb.read_text(encoding="utf-8"))
            shas[old.format(f=f)], shas[new.format(f=f)] = (hashlib.sha256(pa.read_bytes()).hexdigest(),
                                                             hashlib.sha256(pb.read_bytes()).hexdigest())
            fams[f][kind] = FN[kind](ja, jb)
    audit = None
    if a.audit_before or a.audit_after:
        ab = json.loads(a.audit_before.read_text()) if a.audit_before else None
        aa = json.loads(a.audit_after.read_text()) if a.audit_after else None
        audit = audit_pairs(ab, aa)
        for p in (a.audit_before, a.audit_after):
            if p:
                shas[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    rep = {"record": "PHYSICAL_LAYERS_V04_TO_V05_COMPARISON", "status": "AI_DRAFTED_COUNTS_ONLY", "version": VERSION, "contains_ids": False,
           "contains_text": False, "citable": False, "counts_as_human_gate": False, "families": fams, "record_audit": audit,
           "source_report_sha256": {re.sub(r"[^A-Za-z0-9_]", "_", k): v for k, v in sorted(shas.items())},
           "superseded": superseded(r), "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    D.write_report(a.out, rep, root=ROOT)
    a.out_md.write_text(markdown(rep), encoding="utf-8")
    print(json.dumps({"families": list(fams), "report_sha256": hashlib.sha256(a.out.read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
