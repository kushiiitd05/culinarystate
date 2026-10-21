#!/usr/bin/env python3
"""ES-1.1 gate: independent validation of exports/evd/evd_export_v1.jsonl against the ledger (own re-derivation; does not call export_row).
  python tools/validate_evd_export_v1.py  -> reports/es1/es1_1_evd_export_audit.json + .md ; exit 0 on PASS, 2 on FAIL"""
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.evd_export import build_export, canon_json, file_sha256  # noqa: E402  (only for the determinism rebuild)

L = ROOT / "ledgers/data"
EXP = ROOT / "exports/evd/evd_export_v1.jsonl"
MAN = json.loads((ROOT / "exports/evd/evd_export_v1.manifest.json").read_text())
OUT = ROOT / "reports/es1"
OUT.mkdir(parents=True, exist_ok=True)
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()


def latest(name):
    d, n = {}, 0
    for line in open(L / f"{name}.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            n += 1
            d[r["id"]] = r
    return d, n


evd, n_lines = latest("EVD")
rows = [json.loads(x) for x in open(EXP, encoding="utf-8") if x.strip()]
byid = {r["evd_id"]: r for r in rows}
active = {k: v for k, v in evd.items() if v["status"] == "ACTIVE"}
schema = json.load(open(ROOT / "registry/schemas/evd_export_v1.schema.json"))
V = jsonschema.Draft202012Validator(schema)
checks, fails = {}, {}


def ck(name, ok, detail=None, gating=True):
    checks[name] = {"pass": bool(ok), "gating": gating, "detail": detail}
    if not ok and gating:
        fails[name] = detail


def num(x):
    return None if x is None else float(x)


# 1 accounting
excluded = Counter(v["status"] for k, v in evd.items() if k not in active)
ck("1_every_active_row_accounted", set(byid) == set(active) and len(rows) == len(active) == len(byid), {"ledger_version_lines": n_lines, "ledger_ids_latest": len(evd), "active": len(active), "export_rows": len(rows), "excluded_latest_by_status": dict(excluded)})
# 2 schema
bad = [(r["evd_id"], [e.message[:80] for e in list(V.iter_errors(r))[:2]]) for r in rows if not V.is_valid(r)]
ck("2_schema_validation", not bad, {"failures": len(bad), "examples": bad[:5]})
# 3 lineage hash + unchanged source fields
lin, mism = 0, []
for k, r in byid.items():
    src = active[k]
    ok = r["source_row_sha256"] == sha(canon_json(src)) and r["ledger_version"] == src["version"]
    lin += ok
    for ek, sv in (("source_id", src["source_id"]), ("source_family_id", src["source_family_id"]), ("evidence_tier", src["tier"]), ("censoring_flag", bool(src["censored"])), ("target_state_variable_id", src["target"]["state_variable_id"]),
                   ("ingredient_id", src["matrix"].get("ingredient_id")), ("process_id", src["process"].get("process_id")), ("condition_id", src["process"].get("condition_id")), ("matrix_raw_name", src["matrix"].get("raw_name")),
                   ("verification_status", src["verification"]["status"]), ("before_value", (src.get("before") or {}).get("value")), ("after_value", (src.get("after") or {}).get("value")),
                   ("retention_fraction", ((src.get("derived") or {}).get("retention_factor") or {}).get("value")), ("yield_fraction", ((src.get("derived") or {}).get("yield_factor") or {}).get("value")),
                   ("percent_change", ((src.get("derived") or {}).get("percent_change") or {}).get("value"))):
        if r[ek] != sv:
            mism.append((k, ek))
    if not ok:
        mism.append((k, "lineage_hash"))
ck("3_source_lineage_and_copied_values", lin == len(rows) and not mism, {"lineage_hash_ok": lin, "copied_value_mismatches": len(mism), "examples": mism[:5]})
# 4 derived fields: independent recomputation, and no derived value where inputs fail
dn = lf = lr = 0
bad4 = []


def meas(x):
    if not x or x.get("status") != "MEASURED" or x.get("censor"):
        return None
    v = x.get("value")
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


for k, r in byid.items():
    s = active[k]
    b, a, rf = s.get("before"), s.get("after"), ((s.get("derived") or {}).get("retention_factor"))
    bv, av = meas(b), meas(a)
    same_unit = bool(b and a and b.get("unit") and b.get("unit") == a.get("unit"))
    e_delta = (av - bv) if (bv is not None and av is not None and same_unit) else None
    e_lfc = math.log(av / bv) if (bv is not None and av is not None and same_unit and bv > 0 and av > 0) else None
    rv = meas(rf)
    e_lr = math.log(rv) if (rv is not None and rv > 0) else None
    for name, got, exp in (("delta_value", r["delta_value"], e_delta), ("log_fold_change", r["log_fold_change"], e_lfc), ("log_retention_factor", r["log_retention_factor"], e_lr)):
        if (got is None) != (exp is None) or (got is not None and abs(got - exp) > 1e-12 * max(1.0, abs(exp))):
            bad4.append((k, name))
    for name, prov, val in (("delta", r["delta_provenance"], r["delta_value"]), ("lfc", r["log_fold_change_provenance"], r["log_fold_change"]), ("lr", r["log_retention_provenance"], r["log_retention_factor"])):
        if (val is not None) != (prov == "DERIVED_DETERMINISTIC"):
            bad4.append((k, name + "_provenance"))
    if r["censoring_flag"] and (r["log_retention_factor"] is not None and rf and rf.get("status") == "CENSORED"):
        bad4.append((k, "derived_from_censored"))
    dn += r["delta_value"] is not None
    lf += r["log_fold_change"] is not None
    lr += r["log_retention_factor"] is not None
ck("4_derivations_reproducible_and_no_invention", not bad4, {"delta_value": dn, "log_fold_change": lf, "log_retention_factor": lr, "violations": len(bad4), "examples": bad4[:5]})
# 5 no value where the source has none (unknown stays unknown)
inv = [(k, f) for k, r in byid.items() for f in ("lod", "loq") if r[f] is not None] + [(k, "prior_state_id") for k, r in byid.items() if r["prior_state_id"] and not (active[k]["matrix"].get("initial_state") or active[k]["matrix"].get("prior_processing"))]
ck("5_unknown_stays_unknown(lod,loq,prior_state)", not inv, {"violations": len(inv)})
# 6 duplicate mapping reversible
mp = list(csv.DictReader(open(ROOT / "registry/svar_duplicate_mapping_v1.csv", newline="", encoding="utf-8")))
dups = {m["duplicate_id"]: m["canonical_id"] for m in mp if m["relation"] == "DUPLICATE_SAME_ANALYTE"}
rev_ok = all(r["target_state_variable_id"] == active[k]["target"]["state_variable_id"] for k, r in byid.items())
canon_ok = all(r["canonical_variable_id"] == dups.get(r["target_state_variable_id"], r["target_state_variable_id"]) for r in rows)
cnt_t = Counter(r["target_state_variable_id"] for r in rows)
cnt_c = Counter(r["canonical_variable_id"] for r in rows)
sum_ok = all(cnt_c[c] == cnt_t[c] + sum(cnt_t[d] for d, cc in dups.items() if cc == c) for c in cnt_c)
ck("6_duplicate_mapping_reversible", rev_ok and canon_ok and sum_ok and len(dups) == 11 and all(m["relation"] != "DUPLICATE_SAME_ANALYTE" or m["canonical_id"] not in dups for m in mp),
   {"duplicate_pairs": len(dups), "equivalent_candidates_not_merged": sum(m["relation"] == "EQUIVALENT_CANDIDATE_NOT_MERGED" for m in mp), "original_ids_preserved": rev_ok, "canonical_consistent": canon_ok, "group_counts_additive": sum_ok,
    "evd_rows_on_duplicate_ids": sum(cnt_t[d] for d in dups), "evd_rows_after_canonical_merge_for_those": sum(cnt_c[c] for c in set(dups.values()))})
# 7 canonical sources unchanged
now = {n: file_sha256(L / f"{n}.jsonl") for n in ("EVD", "SVAR", "COND", "PROC", "ING", "SRC")}
before = MAN["ledger_sha256_before_after"]["before"]
ck("7_canonical_ledgers_unchanged", now == before == MAN["ledger_sha256_before_after"]["after"], {"ledger_sha256_now": now})
# 8 determinism: rebuild twice, compare bytes with the file
r1, _, _, m1 = build_export()
b1 = "".join(canon_json(r) + "\n" for r in r1)
r2, _, _, _ = build_export()
b2 = "".join(canon_json(r) + "\n" for r in r2)
fh = hashlib.sha256(open(EXP, "rb").read()).hexdigest()
ck("8_deterministic_rebuild_identical", hashlib.sha256(b1.encode()).hexdigest() == fh == hashlib.sha256(b2.encode()).hexdigest() == MAN["export_sha256"], {"export_sha256": fh})
# 9 enumerations / policy
tier_ok = all(r["evidence_tier"] in {"E1", "E2", "E3", "E4", "E5", "E6", "E7"} for r in rows)
pol = all(not (r["human_verified"] and r["verification_status"] != "HUMAN_VERIFIED") for r in rows)
ck("9_tier_provenance_verification_design_separate_fields", tier_ok and pol and all(k in rows[0] for k in ("evidence_tier", "provenance_class", "verification_status", "design_strength")), {"tier_vocab_ok": tier_ok})
# non-gating diagnostics
pe_incons = pe_n = 0
pct_bad = pct_n = 0
for k, r in byid.items():
    if r["source_family_id"] == "PHENOL-EXPLORER-3.6" and None not in (r["before_value"], r["after_value"], r["retention_fraction"], r["yield_fraction"]) and r["before_value"] > 0:
        pe_n += 1
        if abs(r["after_value"] / r["before_value"] * r["yield_fraction"] - r["retention_fraction"]) > 0.02:
            pe_incons += 1
    if r["percent_change"] is not None and r["before_value"] and r["after_value"] is not None and r["before_value"] > 0:
        pct_n += 1
        if abs((r["after_value"] - r["before_value"]) / r["before_value"] * 100 - r["percent_change"]) > 0.05:
            pct_bad += 1
ck("D1_PE_retention≈(after/before)*yield (diagnostic)", True, {"checked": pe_n, "outside_0.02": pe_incons}, gating=False)
ck("D2_percent_change≈(after-before)/before*100 (diagnostic)", True, {"checked": pct_n, "outside_0.05": pct_bad}, gating=False)

# audit counts
def cnt(f):
    return dict(Counter(r[f] for r in rows).most_common())


unk = {"prior_state_id": sum(r["prior_state_id"] is None for r in rows), "ingredient_id": sum(r["ingredient_id"] is None for r in rows), "process_id": sum(r["process_id"] is None for r in rows), "measurement_id": sum(r["measurement_id"] is None for r in rows),
       "before_value": sum(r["before_value"] is None for r in rows), "after_value": sum(r["after_value"] is None for r in rows), "delta_value": sum(r["delta_value"] is None for r in rows), "log_fold_change": sum(r["log_fold_change"] is None for r in rows),
       "log_retention_factor": sum(r["log_retention_factor"] is None for r in rows), "retention_fraction": sum(r["retention_fraction"] is None for r in rows), "yield_fraction": sum(r["yield_fraction"] is None for r in rows),
       "lod": len(rows), "loq": len(rows), "direction_UNKNOWN": sum(r["direction"] == "UNKNOWN" for r in rows),
       "condition_temperature_UNKNOWN": sum((r["condition_completeness"] or {}).get("temperature") in (None, "UNKNOWN") for r in rows), "condition_duration_UNKNOWN": sum((r["condition_completeness"] or {}).get("duration") in (None, "UNKNOWN") for r in rows),
       "condition_moisture_UNKNOWN": sum((r["condition_completeness"] or {}).get("moisture") in (None, "UNKNOWN") for r in rows), "condition_ph_UNKNOWN": sum((r["condition_completeness"] or {}).get("ph") in (None, "UNKNOWN") for r in rows)}
reasons = {f: dict(Counter(r[f] for r in rows if r[f])) for f in ("delta_reason_if_unknown", "log_fold_change_reason_if_unknown", "log_retention_reason_if_unknown")}
gate = "PASS" if not fails else "FAIL"
audit = {"gate": gate, "failures": fails, "input_row_count_active": len(active), "ledger_version_lines": n_lines, "ledger_ids_latest": len(evd), "output_row_count": len(rows), "validation_failures": len(bad), "checks": checks,
         "deterministic_derived_field_counts": {"delta_value": dn, "log_fold_change": lf, "log_retention_factor": lr}, "unknown_counts": unk, "unknown_reasons": reasons,
         "evidence_tier_counts": cnt("evidence_tier"), "provenance_counts": cnt("provenance_class"), "verification_counts": cnt("verification_status"), "design_strength_counts": cnt("design_strength"), "applicability_counts": cnt("applicability"),
         "censoring_flag_counts": cnt("censoring_flag"), "source_family_counts": cnt("source_family_id"), "duplicate_variable_mappings": mp, "export_sha256": fh, "ledger_sha256": now}
(OUT / "es1_1_evd_export_audit.json").write_text(json.dumps(audit, indent=1, default=str))
print(gate, json.dumps({k: audit[k] for k in ("input_row_count_active", "output_row_count", "validation_failures", "deterministic_derived_field_counts", "evidence_tier_counts", "provenance_counts", "verification_counts", "design_strength_counts")}, indent=1))
for k, v in checks.items():
    print(("ok  " if v["pass"] else "FAIL"), k, json.dumps(v["detail"])[:300])
sys.exit(0 if gate == "PASS" else 2)
