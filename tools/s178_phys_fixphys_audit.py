"""S178 FIX-PHYS: counts-only before/after audit of the SCI-A review findings on the Layer 1 / Layer 2 heat records.

Reads per-record JSONL files (git-ignored, under data/derived/) and writes COUNTS only (no text, no recipe id). The same
counters run on the v04 records (the review's figures) and on the v05 records (after the fixes), so the before/after table of
``reports/orchestration/S178_FIX-PHYS_report.md`` is reproducible:

- ``until_clause_bound_temperature_reviewer_method`` (M1): heat events whose TEXT_STATED temperature span lies inside the span of
  an UNTIL cue of the event's endpoint block (the SCI-A scan; v04: 869).
- ``until_clause_bound_temperature_clause_spans`` (M1, v05 only): the same against the full until-clause spans that Layer 1
  0.3.0 stores in ``endpoint.until_clauses``; ``..._syrup_exempt`` counts the syrup / candy / jam clauses that may keep one.
- ``oven_text_stated_below_77`` (M1, Layer 2 TYPICAL): OVEN_AIR events with a text-stated bath below 77 C (v04: 318; an upper
  bound, warm-oven holds are genuine), and those with a core computed.
- ``lifted_typical`` (M4): events whose TYPICAL cap was lifted to a stated liquid temperature (v04: 241), by Layer 1 row and by
  the solute / cue condition; ``not_lifted_dilute`` counts the new flag.
- ``moist_piece_core_above_tboil`` (M5): events with a cut piece whose core end temperature exceeds T_boil + 0.5 C in any bracket
  (pressure media: their bracket saturation temperature + 0.5 C) and the cap is active (v04 lifted cores above 100 C: 12).
- ``fat_heat_temperature_from_setter`` (M2): FAT_HEAT temperatures shared from a setter step (v04: 460).

Usage: tools/s178_phys_fixphys_audit.py --l1 <dir>... --l2 <dir>... --out <json> [--workers N]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

AQ = {"WATER", "LIQUID", "LIQUID_PARTIAL", "WATER_PRESSURIZED", "WATER_BATH_SEALED"}
TOL_C = 0.5
PRESSURE_T = {"GENTLE": 108.4, "TYPICAL": 115.2, "INTENSE": 121.0}  # PC-002 bracket (registry/phase_change_v1.csv)
VERSION = "s178-phys-fixphys-audit-0.1.0"


def _val(v) -> tuple[float, float]:
    if isinstance(v, list):
        return float(Fraction(str(v[0]))), float(Fraction(str(v[1])))
    x = float(Fraction(str(v)))
    return x, x


def _inside(sp, spans) -> bool:
    return bool(sp) and any(c[0] <= sp[0] and sp[1] <= c[1] for c in spans)


def scan_l1(path: str) -> Counter:
    c: Counter = Counter()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            inp, fam = r["inputs"], r["family"]
            c["l1_heat_events"] += 1
            t = inp["temperature_profile"]
            amb = inp.get("ambient_temperature") or {}
            if amb.get("status", "UNKNOWN") != "UNKNOWN":
                c["l1_ambient_temperature"] += 1
            for f in (t.get("flags") or []):
                c[f"l1_temperature_flag|{f}"] += 1
            for k in ("syrup_stage_cue", "pressure_cue", "water_bath_cue"):
                if (inp.get(k) or {}).get("status", "UNKNOWN") != "UNKNOWN":
                    c[f"l1_{k}"] += 1
            if t["status"] == "UNKNOWN" or t["basis"] != "TEXT_STATED":
                continue
            row = t.get("row")
            c[f"l1_text_stated|{fam}"] += 1
            if t["status"] == "RANGE":
                c["l1_text_stated_range"] += 1
            lo, hi = _val(t["value"])
            med = (inp.get("medium") or {}).get("value")
            if fam == "FAT_HEAT" and row == "CB_RULE:TEMPERATURE_FROM_SETTER_STEP":
                c["fat_heat_temperature_from_setter"] += 1
            if med in AQ and hi > 100 and row == "CB_RULE:TEMPERATURE_FROM_SETTER_STEP":
                c["aqueous_above_100_from_setter"] += 1
            if med in AQ and hi > 100:
                c["aqueous_above_100_all"] += 1
            if fam in ("DRY_HEAT", "FAT_HEAT") and row == "CB_RULE:TEMPERATURE_FROM_SETTER_STEP":
                c[f"setter_shared|{fam}"] += 1
            ep = r.get("endpoint") or {}
            sp = t.get("span")
            until = [cue["span"] for cue in ep.get("cues", []) if cue.get("trigger") == "UNTIL"]
            if _inside(sp, until):
                c["until_clause_bound_temperature_reviewer_method"] += 1
                c[f"until_clause_bound_temperature_reviewer_method|{fam}"] += 1
            if "until_clauses" in ep:
                c["l1_records_with_until_clause_spans"] += 1
                clauses = ep["until_clauses"]
                hit = [cl for cl in clauses if cl["span"][0] <= (sp or [0])[0] and (sp or [0, 0])[1] <= cl["span"][1]]
                if sp and hit:
                    if any(cl.get("syrup_exempt") for cl in hit):
                        c["until_clause_bound_temperature_clause_spans_syrup_exempt"] += 1
                    else:
                        c["until_clause_bound_temperature_clause_spans"] += 1
    return c


def scan_l2(path: str) -> Counter:
    c: Counter = Counter()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            c["l2_heat_records"] += 1
            if r.get("status") != "SCENARIO_COMPUTED":
                continue
            c["l2_computed"] += 1
            sc = r["scenarios"]
            ty = sc["TYPICAL"]
            tp = (r.get("l1_provenance") or {}).get("temperature_profile") or {}
            has_piece = "piece_size_class" in (r.get("l1_provenance") or {})
            flags = ty.get("flags", [])
            for f in ("STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE", "STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE",
                      "SUGAR_PHASE_TBOIL_LOWER_ESTIMATE", "SALT_MEMBER_BPE_SMALL", "TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER",
                      "WATER_BATH_IN_OVEN", "FAN_VS_CONVENTIONAL_UNRESOLVED", "PAN_CONTACT_TWO_SIDED_FAST_END"):
                if f in flags:
                    c[f"flag_typical|{f}"] += 1
            if "STATED_LIQUID_T_ABOVE_TBOIL" in flags:
                c["lifted_typical"] += 1
                c[f"lifted_typical|row={tp.get('row')}"] += 1
                solute = "TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER" in flags or "SUGAR_PHASE_TBOIL_LOWER_ESTIMATE" in flags
                c[f"lifted_typical|solute_member={'YES' if solute else 'NO'}"] += 1
                if ty.get("bath_c", 0) > 150:
                    c["lifted_typical_above_150"] += 1
                if ty.get("core_end_c") is not None:
                    c["lifted_typical_with_core"] += 1
                    if ty["core_end_c"] > 100 + TOL_C:
                        c["lifted_typical_core_above_100"] += 1
            if r["medium"] == "OVEN_AIR" and ty["bases"].get("bath_c") == "L1:TEXT_STATED" and ty["bath_c"] < 77:
                c["oven_text_stated_below_77"] += 1
                c["oven_text_stated_below_77_core_computed"] += int(ty.get("core_end_c") is not None)
            if has_piece:
                over = False
                for b, s in sc.items():
                    ce = s.get("core_end_c")
                    if ce is None or s.get("t_cap_c") is None:
                        continue
                    lim = (PRESSURE_T.get(b, 121.0) if r["medium"] == "WATER_PRESSURIZED" else 100.0) + TOL_C
                    if ce > lim:
                        over = True
                if over:
                    c["moist_piece_core_above_tboil"] += 1
                    c[f"moist_piece_core_above_tboil|medium={r['medium']}"] += 1
    return c


def _files(dirs) -> list[str]:
    out: list[str] = []
    for d in dirs:
        out += sorted(glob.glob(str(Path(d) / "*.jsonl"))) or sorted(glob.glob(str(Path(d) / "*" / "*.jsonl")))
    return out


def run(l1_dirs, l2_dirs, workers: int = 8) -> dict:
    tot: Counter = Counter()
    with Pool(workers) as p:
        for cnt in p.imap_unordered(scan_l1, _files(l1_dirs)):
            tot.update(cnt)
        for cnt in p.imap_unordered(scan_l2, _files(l2_dirs)):
            tot.update(cnt)
    return {"tool": VERSION, "status": "AI_DRAFTED_COUNTS_ONLY", "l1_dirs": [str(d) for d in l1_dirs],
            "l2_dirs": [str(d) for d in l2_dirs], "counts": dict(sorted(tot.items()))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--l1", nargs="*", default=[])
    ap.add_argument("--l2", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args(argv)
    res = run(a.l1, a.l2, a.workers)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(out, hashlib.sha256(out.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
