#!/usr/bin/env python
"""Diagnosis and before / after of the stated-liquid-temperature lift (S178 PHYS2, S177 open item (a)). Counts only. DRAFT.

The S177 cap rule never sets the evaporation cap below a temperature the text states for an aqueous liquid; 520 events were lifted, 197 of
them above 150 C. This tool joins the S176 Layer 1 records (nearest-temperature rule, 0.1.0) with the S178 records (temperature ownership,
0.2.0) on (family, recipe id, event id) and reports, for the aqueous-medium heat events whose stated temperature was above 100 C:
what became of each (still a stated liquid temperature, boil by definition, unknown temperature, reassigned to another event, kept as an
oven / heat-level ambient temperature, a food target), and the Layer 2 numbers before (0.3.0) and after (0.4.0): events lifted by stated
temperature bucket, with a computed core, with a solute-rich lot member, and the highest core temperature of a lifted event.

    python tools/s178_phys_stated_liquid_report.py --family FOODCOM --l1-before DIR --l1-after DIR --l2-before DIR --l2-after DIR ... \
        --out reports/s178/phys/stated_liquid_t_before_after_S178.json --out-md reports/s178/phys/stated_liquid_t_before_after_S178.md

``--family`` repeats with the four directory arguments in the same order (one set per family). Never overwrites; counts only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

AQ = ("WATER", "LIQUID", "LIQUID_PARTIAL", "WATER_PRESSURIZED", "WATER_BATH_SEALED")
STATED = ("TEXT_STATED", "CARRIED_SETPOINT")
BUCKETS = ((105.0, "100_TO_105"), (120.0, "105_TO_120"), (150.0, "120_TO_150"), (1e9, "ABOVE_150"))
SOLUTE_CLASSES = ("SWEETENER", "CONDIMENT")


def bucket(hi: float) -> str:
    return next(n for lim, n in BUCKETS if hi <= lim)


def _hi(v) -> float:
    return max(float(Fraction(str(x))) for x in v) if isinstance(v, (list, tuple)) else float(Fraction(str(v)))


def _stated_above_100(rec: dict):
    i = rec["inputs"]
    t = i["temperature_profile"]
    if i["medium"]["value"] in AQ and t["status"] != "UNKNOWN" and t["basis"] in STATED:
        hi = _hi(t["value"])
        if hi > 100.0:
            return hi
    return None


def scan_before(path: str) -> dict:
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            hi = _stated_above_100(r)
            if hi is not None:
                out[(r["recipe_id"], r["event_id"])] = (bucket(hi), r["process_id"].replace("-", "_"), r["inputs"]["medium"]["value"])
    return out


def scan_after(path: str, keys: set) -> dict:
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            k = (r["recipe_id"], r["event_id"])
            if k not in keys:
                continue
            i, t = r["inputs"], r["inputs"]["temperature_profile"]
            groups = (i.get("matrix_groups") or {}).get("value") or []
            solute = any(g in SOLUTE_CLASSES for g in groups)
            why = "__".join(sorted({n["now"] for n in r.get("temperature_note", [])})) or "NO_NOTE"
            hi = _stated_above_100(r)
            if hi is not None:
                cat = "STILL_STATED_AQUEOUS_ABOVE_100"
            elif t["status"] == "UNKNOWN":
                cat = "NOW_UNKNOWN_TEMPERATURE"
            elif t["basis"] == "PHYSICAL_DEFINITION":
                cat = "NOW_BOIL_BY_PHYSICAL_DEFINITION"
            else:
                cat = "NOW_STATED_AT_OR_BELOW_100"
            out[k] = (cat, why, solute, bucket(hi) if hi is not None else None, "ambient_temperature" in i)
    return out


def scan_l2(path: str) -> dict:
    c: Counter = Counter()
    mx: dict = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if "STATED_LIQUID_T_ABOVE_TBOIL" not in line:
                continue
            r = json.loads(line)
            t = r["scenarios"].get("TYPICAL")
            if not t or "STATED_LIQUID_T_ABOVE_TBOIL" not in t["flags"]:
                continue
            b = bucket(t["bath_c"])
            solute = "TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER" in t["flags"]
            c[("lifted", b)] += 1
            c[("lifted_by_solute", b, "SOLUTE_RICH_MEMBER" if solute else "NO_SOLUTE_RICH_MEMBER")] += 1
            if t.get("core_end_c") is not None:
                c[("lifted_core_computed", b)] += 1
                mx[b] = max(mx.get(b, -1e9), t["core_end_c"])
    return {"c": dict(c), "max_core": mx}


def _pool(fn, items: list, workers: int):
    if workers > 1 and len(items) > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(workers) as pool:
            return pool.map(fn, items, chunksize=1)
    return [fn(x) for x in items]


def _after_job(a):
    return scan_after(*a)


def run_family(fam: str, d1b: Path, d1a: Path, d2b: Path, d2a: Path, workers: int) -> dict:
    before: dict = {}
    for part in _pool(scan_before, [str(f) for f in sorted(d1b.glob("*.jsonl"))], workers):
        before.update(part)
    keys = set(before)
    after: dict = {}
    for part in _pool(_after_job, [(str(f), keys) for f in sorted(d1a.glob("*.jsonl"))], workers):
        after.update(part)
    tab: Counter = Counter()
    for k, (b, pid, med) in before.items():
        cat, why, solute, nb, amb = after.get(k, ("EVENT_NOT_FOUND_IN_AFTER", "NONE", False, None, False))
        tab[("old_bucket_by_new_category", b, cat)] += 1
        tab[("old_process", b, pid)] += 1
        tab[("old_medium", med)] += 1
        if cat != "STILL_STATED_AQUEOUS_ABOVE_100":
            tab[("reason_of_change", b, why if cat != "EVENT_NOT_FOUND_IN_AFTER" else cat)] += 1
        if amb:
            tab[("ambient_temperature_kept", b)] += 1
        if cat == "STILL_STATED_AQUEOUS_ABOVE_100":
            tab[("remaining_by_solute_rich_member", b, "SOLUTE_RICH_MEMBER" if solute else "NO_SOLUTE_RICH_MEMBER")] += 1
    l2 = {}
    for tag, d in (("before_l2_0_3_0", d2b), ("after_l2_0_4_0", d2a)):
        c: Counter = Counter()
        mx: dict = {}
        for p in _pool(scan_l2, [str(f) for f in sorted(d.glob("*.jsonl"))], workers):
            c.update(p["c"])
            for b, v in p["max_core"].items():
                mx[b] = max(mx.get(b, -1e9), v)
        l2[tag] = {"counts": _nest(c.items()), "max_core_end_c_of_a_lifted_event_by_bucket": {k: round(v, 1) for k, v in sorted(mx.items())}}
    return {"l1_events_before": len(before), "l1_old_to_new": _nest(tab.items()), "l2": l2}


def _nest(items) -> dict:
    out: dict = {}
    for key, v in sorted(items, key=lambda kv: str(kv[0])):
        d = out
        for k in key[:-1]:
            d = d.setdefault(str(k), {})
        d[str(key[-1])] = v
    return out


def markdown(rep: dict) -> str:
    L = ["# Stated-liquid temperature lift: diagnosis and before / after (S178 PHYS2, S177 open item (a))", "",
         "Status: DRAFT / AI_DRAFTED, counts only. Before = Layer 1 0.1.0 (nearest temperature of the sentence) with Layer 2 0.3.0; after = Layer 1 "
         "0.2.0 (temperature ownership, oven / heat-level cue guard, food-target diversion) with Layer 2 0.4.0.", ""]
    for fam, d in rep["families"].items():
        L += [f"## {fam}", "", f"Aqueous-medium heat events with a stated temperature above 100 C (Layer 1, before): {d['l1_events_before']}.", ""]
        tab = d["l1_old_to_new"].get("old_bucket_by_new_category", {})
        cats = sorted({c for v in tab.values() for c in v})
        if tab:
            L += ["| stated T before | " + " | ".join(cats) + " |", "|---|" + "---:|" * len(cats)]
            for b in ("100_TO_105", "105_TO_120", "120_TO_150", "ABOVE_150"):
                if b in tab:
                    L.append(f"| {b} | " + " | ".join(str(tab[b].get(c, 0)) for c in cats) + " |")
            L.append("")
        l2 = d["l2"]
        for tag, name in (("before_l2_0_3_0", "Layer 2 0.3.0 (before)"), ("after_l2_0_4_0", "Layer 2 0.4.0 (after)")):
            c = l2[tag]["counts"]
            L.append(f"- {name}: events lifted by stated T bucket {c.get('lifted', {})}; with a computed core {c.get('lifted_core_computed', {})}; "
                     f"highest core of a lifted event {l2[tag]['max_core_end_c_of_a_lifted_event_by_bucket']}.")
        L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--family", action="append", required=True)
    ap.add_argument("--l1-before", action="append", required=True, type=Path)
    ap.add_argument("--l1-after", action="append", required=True, type=Path)
    ap.add_argument("--l2-before", action="append", required=True, type=Path)
    ap.add_argument("--l2-after", action="append", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--out-md", required=True, type=Path)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    if not (len(a.family) == len(a.l1_before) == len(a.l1_after) == len(a.l2_before) == len(a.l2_after)):
        ap.error("--family, --l1-before, --l1-after, --l2-before and --l2-after must be given the same number of times")
    for p in (a.out, a.out_md):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    fams = {f: run_family(f, b1, a1, b2, a2, a.workers) for f, b1, a1, b2, a2 in
            zip(a.family, a.l1_before, a.l1_after, a.l2_before, a.l2_after)}
    rep = {"record": "STATED_LIQUID_T_BEFORE_AFTER", "status": "AI_DRAFTED_COUNTS_ONLY", "contains_ids": False, "contains_text": False,
           "citable": False, "counts_as_human_gate": False, "families": fams,
           "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    D.write_report(a.out, rep, root=ROOT)
    a.out_md.write_text(markdown(rep), encoding="utf-8")
    print(json.dumps({"families": list(fams), "report_sha256": hashlib.sha256(a.out.read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
