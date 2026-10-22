#!/usr/bin/env python3
"""Step 07: read-only condition/measurement coverage audit over the current COND + EVD ledgers (no source row is modified or populated).
  python tools/step07_condition_audit.py -> reports/step07/step07_condition_coverage_audit.json"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence import condition_normalizer as N  # noqa: E402

L = ROOT / "ledgers/data"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
before = {n: sha(L / f"{n}.jsonl") for n in ("COND", "EVD", "MEAS", "SVAR")}


def latest(n):
    d = {}
    for line in open(L / f"{n}.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            d[r["id"]] = r
    return d


cond, evd, meas = latest("COND"), latest("EVD"), latest("MEAS")
act = {k: v for k, v in evd.items() if v["status"] == "ACTIVE"}
used = {v["process"].get("condition_id") for v in act.values()}
cnt = {k: Counter() for k in ("duration", "temperature", "pressure", "power", "medium", "ph", "moisture", "aw")}
stat = {k: Counter() for k in cnt}
reasons = Counter()
loc = Counter()
normed = []


def tally(key, res):
    cnt[key][res["value_type"]] += 1
    stat[key][res["status"]] += 1
    for r in res["reasons"]:
        reasons[(key, r)] += 1


for cid in sorted(used):
    c = cond.get(cid)
    if not c:
        continue
    r = N.from_qvalue("time_duration", c.get("duration"))
    tally("duration", r)
    temps = c.get("temperatures") or []
    if temps:
        for t in temps:
            v = N.temperature_variable_for(t.get("location"))
            res = N.from_qvalue(v, t.get("value"), location=t.get("location"))
            tally("temperature", res)
            loc[t.get("location") or "UNSPECIFIED"] += 1
    else:
        tally("temperature", N.normalize_value("temp_unspecified"))
        loc["(none stated)"] += 1
    pr = c.get("pressure")
    tally("pressure", N.from_qvalue("pressure", pr if isinstance(pr, dict) else None))
    po = c.get("power")
    tally("power", N.from_qvalue("microwave_power", po if isinstance(po, dict) else None))
    mask = c.get("completeness_mask") or {}
    for k, key, var in (("ph", "ph", "ph"), ("moisture", "moisture", "moisture_content"), ("aw", "aw", "water_activity")):
        res = N.normalize_value(var)  # no source field exists in COND for these; never populated here
        tally(key, res)
    cnt["medium"][("STATED" if c.get("medium") else "NOT_STATED")] += 1
    stat["medium"]["VALID" if c.get("medium") else "UNKNOWN"] += 1
# measurement side over active EVD rows
bas, ret, cens, meth, vorig = Counter(), Counter(), Counter(), Counter(), Counter()
for r in act.values():
    t = r["target"]
    bas[N.classify_basis(t.get("basis"))["basis_id"]] += 1
    rf = (r.get("derived") or {}).get("retention_factor")
    rt = N.classify_retention_type(r["source_family_id"], t.get("basis"), bool(rf and rf.get("status") in ("MEASURED", "CENSORED")))
    ret[(rt["retention_type_id"], rt["status"])] += 1
    cens[N.classify_censoring(rf)["name"] if rf else "NOT_REPORTED"] += 1
    m = meas.get(r.get("measurement_method_id")) or {}
    meth[N.classify_method(None, m.get("family"))["name"]] += 1
    vorig["SOURCE_IMPUTATION_POSSIBLE" if r["source_family_id"] == "USDA-RETN-R6" else "REPORTED"] += 1
after = {n: sha(L / f"{n}.jsonl") for n in before}
out = {"conditions_audited": len(used), "evd_rows": len(act), "value_type_counts": {k: dict(v) for k, v in cnt.items()}, "status_counts": {k: dict(v) for k, v in stat.items()}, "reason_counts": {f"{a}:{b}": n for (a, b), n in reasons.most_common()},
       "temperature_location_counts": dict(loc), "measurement_basis_counts": dict(bas), "retention_type_counts": {f"{a}|{b}": n for (a, b), n in ret.items()}, "censoring_counts": dict(cens), "method_counts": dict(meth), "value_origin_counts": dict(vorig),
       "ledger_sha256_unchanged": before == after, "ledger_sha256": after}
(ROOT / "reports/step07").mkdir(exist_ok=True)
(ROOT / "reports/step07/step07_condition_coverage_audit.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("conditions_audited", "evd_rows", "value_type_counts", "status_counts", "temperature_location_counts", "measurement_basis_counts", "retention_type_counts", "censoring_counts", "method_counts", "ledger_sha256_unchanged")}, indent=1))
print("top reasons", list(out["reason_counts"].items())[:8])
