#!/usr/bin/env python3
"""Step 07: deterministic 100-condition human audit packet (NOT audited here). Seeded stratified sample over conditions referenced by active EVD rows.
Writes annotation/condition_audit/condition_audit_packet_100.csv (git-ignored: raw strings from third-party databases) and reports/step07/condition_audit_sampling_manifest.json (committed)."""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence import condition_normalizer as N  # noqa: E402

SEED = "step07-condition-audit-v1"  # unchanged in v3: same deterministic stratified design, same 100 conditions
VERSION = "v4"
FP = N.fingerprint()
L = ROOT / "ledgers/data"


def latest(n):
    d = {}
    for line in open(L / f"{n}.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            d[r["id"]] = r
    return d


cond, evd = latest("COND"), latest("EVD")
fam, ctx = {}, {}
for r in evd.values():
    if r["status"] == "ACTIVE":
        cid = r["process"].get("condition_id")
        fam.setdefault(cid, r["source_family_id"])
        t, rf = r["target"], (r.get("derived") or {}).get("retention_factor")
        has = bool(rf and rf.get("status") in ("MEASURED", "CENSORED"))
        raw_c = f"target_basis={t.get('basis')}; retention_value={'yes' if has else 'no'}; retention_status={(rf or {}).get('status', 'ABSENT')}; censor={((rf or {}).get('censor') or {}).get('kind')}"
        rt, cs = N.classify_retention_type(r["source_family_id"], t.get("basis"), has), N.classify_censoring(rf)
        norm_c = f"basis={N.classify_basis(t.get('basis'))['basis_id']}; retention_type={rt['retention_type_id']}/{rt['status']}; censoring={cs['name']}"
        ctx.setdefault(cid, {})[(raw_c, norm_c)] = ctx.get(cid, {}).get((raw_c, norm_c), 0) + 1
def fmt(r):
    """human-readable normalised value: type/status + canonical value or interval with open/closed ends; '~' marks an approximate flag"""
    t = f"{r['value_type']}/{r['status']}"
    u = r.get("canonical_unit") or ""
    if r["value_type"] == "POINT" and r.get("canonical_value") is not None:
        t += f" {'~' if r.get('approximate') else ''}{r['canonical_value']:.6g} {u}"
    elif r["value_type"] == "INTERVAL":
        lo, hi = r.get("canonical_low"), r.get("canonical_high")
        t += f" {'(' if r.get('open_low') or lo is None else '['}{'-inf' if lo is None else format(lo, '.6g')}, {'+inf' if hi is None else format(hi, '.6g')}{')' if r.get('open_high') or hi is None else ']'} {u}"
    if r.get("calendar_unit"):
        t += f" calendar:{r.get('calendar_value')} {r['calendar_unit']}"
    return t.strip()


rank = lambda cid: hashlib.sha256((SEED + cid).encode()).hexdigest()


def stratum(c):
    t = c.get("temperatures") or []
    locs = {x.get("location") for x in t}
    if c.get("pressure") or c.get("power"):
        return "S4_pressure_or_power"
    if locs & {"CORE", "SETPOINT", "MEDIUM"}:
        return "S1_temperature_location_stated"
    if any(x["value"].get("status") == "RANGE" for x in t) or (c.get("duration") or {}).get("status") == "RANGE":
        return "S3_interval"
    if t:
        return "S2_temperature_location_unspecified"
    if c.get("medium"):
        return "S5_medium_only"
    return "S6_all_unknown"


QUOTA = {"S1_temperature_location_stated": 20, "S2_temperature_location_unspecified": 25, "S3_interval": 15, "S4_pressure_or_power": 15, "S5_medium_only": 10, "S6_all_unknown": 15}
pool = {}
for cid in sorted(fam):
    c = cond.get(cid)
    if c:
        pool.setdefault(stratum(c), []).append(cid)
sample = []
for s, q in QUOTA.items():
    sample += [(s, cid) for cid in sorted(pool.get(s, []), key=rank)[:q]]
cols = ["audit_id", "condition_id", "stratum", "source_family", "raw_duration", "raw_temperatures(location|raw)", "raw_pressure", "raw_power", "medium", "normalised_duration", "normalised_temperatures", "normalised_pressure", "normalised_power", "normalised_medium", "normalised_reasons", "raw_measurement_context", "normalised_measurement_context", "normalizer_fingerprint_12"]
rev = ["duration_judgement", "temperature_value_judgement", "temperature_location_judgement", "pressure_judgement", "power_judgement", "medium_judgement", "basis_judgement", "retention_type_judgement", "censoring_judgement", "overall_judgement", "reason_if_not_correct"]
(ROOT / "annotation/condition_audit").mkdir(parents=True, exist_ok=True)
rows = []
for i, (s, cid) in enumerate(sample, 1):
    c = cond[cid]
    d = N.from_qvalue("time_duration", c.get("duration"))
    ts = list(zip([t.get("location") for t in (c.get("temperatures") or [])], N.normalize_temperatures(c.get("temperatures") or [])))
    pw = N.from_qvalue("microwave_power", c.get("power") if isinstance(c.get("power"), dict) else None)
    p = N.from_qvalue("pressure", c.get("pressure") if isinstance(c.get("pressure"), dict) else None)
    rows.append({"audit_id": f"CA-{i:03d}", "condition_id": cid, "stratum": s, "source_family": fam[cid], "raw_duration": (c.get("duration") or {}).get("raw"),
                 "raw_temperatures(location|raw)": " ; ".join(f"{x.get('location')}|{(x.get('value') or {}).get('raw')}" for x in (c.get("temperatures") or [])), "raw_pressure": (c.get("pressure") or {}).get("raw") if isinstance(c.get("pressure"), dict) else None,
                 "raw_power": (c.get("power") or {}).get("raw") if isinstance(c.get("power"), dict) else None, "medium": c.get("medium"), "normalised_duration": fmt(d),
                 "normalised_temperatures": " ; ".join(f"{loc}:{fmt(r)}" for loc, r in ts) or "UNKNOWN", "normalised_pressure": fmt(p) + (f" ref={p.get('pressure_reference')}" if p.get("pressure_reference") else ""), "normalised_power": fmt(pw), "normalised_medium": c.get("medium") or "NOT_STATED", "normalised_reasons": ",".join(sorted({x for _, r in ts for x in r['reasons']} | set(d['reasons']) | set(p['reasons']) | set(pw['reasons']))), "raw_measurement_context": " || ".join(f"{a} [n={n}]" for (a, _), n in sorted(ctx.get(cid, {}).items())[:4]), "normalised_measurement_context": " || ".join(f"{b}" for (_, b), n in sorted(ctx.get(cid, {}).items())[:4]), "normalizer_fingerprint_12": FP['combined_sha256'][:12]})
for who in ("Kush", "Parv"):
    with open(ROOT / f"annotation/condition_audit/condition_audit_packet_100_{VERSION}_{who}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols + rev)
        w.writeheader()
        for r in rows:
            w.writerow(r)
sha = lambda who: hashlib.sha256(open(ROOT / f"annotation/condition_audit/condition_audit_packet_100_{VERSION}_{who}.csv", "rb").read()).hexdigest()
man = {"seed": SEED, "n": len(rows), "quota": QUOTA, "pool_sizes": {k: len(v) for k, v in pool.items()}, "selected_by_stratum": {s: sum(1 for x in rows if x["stratum"] == s) for s in QUOTA},
       "source_family_counts": {f: sum(1 for x in rows if x["source_family"] == f) for f in sorted({x["source_family"] for x in rows})},
       "packet_version": f"{VERSION} (frozen 07H normalizer; normalised columns now show canonical values, open/closed interval ends, approximate marker, pressure reference, calendar durations; same 100 conditions as v1/v2; v1/v2 invalid as audit inputs)",
       "normalizer_fingerprint": FP, "sha256_packet_Kush": sha("Kush"), "sha256_packet_Parv": sha("Parv"), "audited_by_humans": False, "status": "PENDING_HUMAN_SUBGATE (kappa >= 0.8)"}
(ROOT / "reports/step07/condition_audit_sampling_manifest.json").write_text(json.dumps(man, indent=1))
print(json.dumps({k: man[k] for k in ("n", "pool_sizes", "selected_by_stratum", "source_family_counts", "sha256_packet_Kush", "sha256_packet_Parv")}))
