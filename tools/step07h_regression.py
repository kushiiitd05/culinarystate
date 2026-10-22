#!/usr/bin/env python3
"""Step 07H current-data regression: rerun the full read-only COND/EVD audit with the hardened normalizer, prove determinism over two complete rebuilds, compare every condition field against the
pre-07H normalizer (commit 8a9b56b), and classify EVERY difference by cause. Any difference without a known cause is listed as UNEXPLAINED and fails the gate.
  python tools/step07h_regression.py -> reports/step07/step07h_regression_audit.json"""
import hashlib
import importlib.util
import io
import json
import runpy
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence import condition_normalizer as NEW  # noqa: E402

OLD_SHA = "8a9b56b"
L = ROOT / "ledgers/data"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
RENAMES = {"OUT_OF_PHYSICAL_RANGE": "PHYSICALLY_IMPOSSIBLE", "TEMPERATURE_IMPLAUSIBLY_HIGH": "OUTSIDE_TYPICAL_CULINARY_RANGE"}


def load_old():
    d = Path(tempfile.mkdtemp(prefix="old_norm_"))
    pkg = d / "src/culinarystate/evidence"
    pkg.mkdir(parents=True)
    (d / "registry").symlink_to(ROOT / "registry")
    (pkg / "condition_normalizer_old.py").write_text(subprocess.check_output(["git", "show", f"{OLD_SHA}:src/culinarystate/evidence/condition_normalizer.py"], cwd=ROOT, text=True))
    spec = importlib.util.spec_from_file_location("condition_normalizer_old", pkg / "condition_normalizer_old.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def latest(n):
    d = {}
    for line in open(L / f"{n}.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            d[r["id"]] = r
    return d


def fields(mod, cond, used):
    out = {}
    for cid in sorted(used):
        c = cond.get(cid)
        if not c:
            continue
        out[(cid, "duration")] = mod.from_qvalue("time_duration", c.get("duration"))
        for i, r in enumerate(mod.normalize_temperatures(c.get("temperatures") or [])):
            out[(cid, f"temperature[{i}]")] = r
        pr, po = c.get("pressure"), c.get("power")
        out[(cid, "pressure")] = mod.from_qvalue("pressure", pr if isinstance(pr, dict) else None)
        out[(cid, "power")] = mod.from_qvalue("microwave_power", po if isinstance(po, dict) else None)
    return out


def summ(r):
    return {"vt": r["value_type"], "st": r["status"], "reasons": sorted(RENAMES.get(x, x) for x in r["reasons"]), "ol": bool(r.get("open_low")), "oh": bool(r.get("open_high")),
            "cv": r.get("canonical_value"), "cl": r.get("canonical_low"), "ch": r.get("canonical_high")}


def cause(o, n):
    """-> cause label for an (old,new) pair that differs, or None if UNEXPLAINED"""
    if o["vt"] == n["vt"] and o["st"] == n["st"] and o["reasons"] == n["reasons"]:
        if o["oh"] and n["ol"] and not o["ol"] and not n["oh"] and o["cl"] == n["cl"]:
            return "OPEN_BOUND_FIX (GT_*: old open_high=True, new open_low=True; same endpoint, same status)"
        if o["ol"] and n["oh"] and not o["oh"] and not n["ol"] and o["ch"] == n["ch"]:
            return "OPEN_BOUND_FIX (LT_*/ND: old open_low=True, new open_high=True; same endpoint, same status)"
        close = lambda a, b: (a is None and b is None) or (a is not None and b is not None and abs(a - b) <= 1e-9 * max(abs(a), abs(b), 1.0))
        if all(close(o[k], n[k]) for k in ("cv", "cl", "ch")) and o["ol"] == n["ol"] and o["oh"] == n["oh"]:
            return "UNIT_FACTOR_PRECISION (psi factor 6894.757293168 -> exact lbf/in2 6894.757293168361; relative change < 1e-9, status unchanged)"
        return None
    if "CALENDAR_DURATION_NOT_CONVERTED" in n["reasons"] and "CALENDAR_DURATION_NOT_CONVERTED" not in o["reasons"]:
        return "CALENDAR_DURATION_NOT_CONVERTED (month/year no longer converted to fixed seconds)"
    if any(x.startswith("UNRECOGNISED_CENSOR_KIND") for x in n["reasons"]):
        return "UNRECOGNISED_CENSOR_KIND (old code treated every non-GT kind as left-censored)"
    if "CENSORED_LIMIT_NOT_STATED" in n["reasons"]:
        return "CENSORED_LIMIT_NOT_STATED (old code reported NOT_STATED / raw-unparsed)"
    if "UNIT_CONVERSION_NOT_SUPPORTED" in n["reasons"] and o["st"] == "INVALID":
        return "UNIT_CONVERSION_NOT_SUPPORTED (allowed unit with no conversion: INVALID -> AMBIGUOUS)"
    if "NEGATIVE_PRESSURE_REQUIRES_GAUGE_OR_DIFFERENTIAL" in n["reasons"]:
        return "NEGATIVE_PRESSURE_UNSPECIFIED (INVALID -> AMBIGUOUS)"
    return None


def main():
    before = {n: sha(L / f"{n}.jsonl") for n in ("COND", "EVD", "MEAS", "SVAR")}
    audits = []
    for _ in range(2):  # two complete rebuilds
        buf = io.StringIO()
        with redirect_stdout(buf):
            g = runpy.run_path(str(ROOT / "tools/step07_condition_audit.py"))
        audits.append(json.dumps(g["out"], sort_keys=True))
    deterministic = audits[0] == audits[1]
    new_audit = json.loads(audits[0])
    base = json.loads((ROOT / "reports/step07/_pre07h_baseline_audit.json").read_text())
    cond, evd = latest("COND"), latest("EVD")
    used = {v["process"].get("condition_id") for v in evd.values() if v["status"] == "ACTIVE"}
    old_mod = load_old()
    of, nf = fields(old_mod, cond, used), fields(NEW, cond, used)
    assert of.keys() == nf.keys()
    trans = defaultdict(lambda: {"n": 0, "examples": []})
    same = 0
    for k in sorted(of):
        o, n = summ(of[k]), summ(nf[k])
        if o == n:
            same += 1
            continue
        c = cause(o, n) or "UNEXPLAINED"
        key = f"{c} | {o['vt']}/{o['st']} -> {n['vt']}/{n['st']}"
        t = trans[key]
        t["n"] += 1
        if len(t["examples"]) < 3:
            t["examples"].append({"condition_id": k[0], "field": k[1], "raw": nf[k]["raw"], "old": o, "new": n})
    unexplained = sum(v["n"] for k, v in trans.items() if k.startswith("UNEXPLAINED"))
    # count-level comparison (explained by the transitions above)
    cnt_diff = {}
    for sec in ("value_type_counts", "status_counts", "temperature_location_counts", "measurement_basis_counts", "retention_type_counts", "censoring_counts", "method_counts", "value_origin_counts"):
        b, nn = base.get(sec, {}), new_audit.get(sec, {})
        if b != nn:
            cnt_diff[sec] = {"before": b, "after": nn}
    rb, rn = Counter(base["reason_counts"]), Counter(new_audit["reason_counts"])
    reason_diff = {k: {"before": rb.get(k, 0), "after": rn.get(k, 0)} for k in sorted(set(rb) | set(rn)) if rb.get(k, 0) != rn.get(k, 0)}
    after = {n: sha(L / f"{n}.jsonl") for n in before}
    out = {"normalizer_fingerprint": NEW.fingerprint(), "baseline_commit": OLD_SHA, "conditions_audited": new_audit["conditions_audited"], "evd_references_covered": new_audit["evd_rows"],
           "evd_references_expected": 17978, "evd_coverage_ok": new_audit["evd_rows"] == 17978 and new_audit["conditions_audited"] == 4414,
           "ledger_sha256_before": before, "ledger_sha256_after": after, "ledgers_byte_identical": before == after, "audit_deterministic_over_two_rebuilds": deterministic,
           "audit_output_sha256": hashlib.sha256(audits[0].encode()).hexdigest(), "fields_compared": len(of), "fields_unchanged": same, "fields_changed": len(of) - same,
           "unexplained_field_changes": unexplained, "transitions": {k: v for k, v in sorted(trans.items(), key=lambda kv: -kv[1]["n"])}, "count_section_differences": cnt_diff, "reason_count_differences": reason_diff,
           "reason_renames_applied_before_compare": RENAMES}
    (ROOT / "reports/step07/step07h_regression_audit.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps({k: out[k] for k in ("conditions_audited", "evd_references_covered", "evd_coverage_ok", "ledgers_byte_identical", "audit_deterministic_over_two_rebuilds", "fields_compared", "fields_unchanged", "fields_changed", "unexplained_field_changes")}, indent=1))
    for k, v in out["transitions"].items():
        print(v["n"], k[:150])
    print("count diffs:", list(cnt_diff))
    print("reason diffs:", reason_diff)


if __name__ == "__main__":
    main()
