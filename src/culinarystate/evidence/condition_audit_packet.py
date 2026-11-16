"""Step 07.A-R1 condition-audit packet (reports/step07/07A_R1_preregistration_DRAFT.md §2). DRAFT_PENDING_SIGNATURES.

Same strata, quotas, columns and display format as the v4 builder (tools/step07_build_audit_packet.py, left
unchanged as history); new seed, and the v1-v4 conditions are excluded BEFORE ranking so the packet is disjoint.
``manifest`` holds counts, hashes and the seed only: no condition id and no raw string.
"""
from __future__ import annotations

import hashlib
from typing import Any, Mapping

from culinarystate.evidence import condition_normalizer as N

SEED_R1 = "step07-condition-audit-R1-2026-11-08"
QUOTA = {"S1_temperature_location_stated": 20, "S2_temperature_location_unspecified": 25, "S3_interval": 15,
         "S4_pressure_or_power": 15, "S5_medium_only": 10, "S6_all_unknown": 15}
COLS = ["audit_id", "condition_id", "stratum", "source_family", "raw_duration", "raw_temperatures(location|raw)",
        "raw_pressure", "raw_power", "medium", "normalised_duration", "normalised_temperatures", "normalised_pressure",
        "normalised_power", "normalised_medium", "normalised_reasons", "raw_measurement_context",
        "normalised_measurement_context", "normalizer_fingerprint_12"]
REV = ["duration_judgement", "temperature_value_judgement", "temperature_location_judgement", "pressure_judgement",
       "power_judgement", "medium_judgement", "basis_judgement", "retention_type_judgement", "censoring_judgement",
       "overall_judgement", "reason_if_not_correct"]


def rank(seed: str, cid: str) -> str:
    return hashlib.sha256((seed + cid).encode()).hexdigest()


def stratum(c: Mapping[str, Any]) -> str:
    t = c.get("temperatures") or []
    locs = {x.get("location") for x in t}
    if c.get("pressure") or c.get("power"):
        return "S4_pressure_or_power"
    if locs & {"CORE", "SETPOINT", "MEDIUM"}:
        return "S1_temperature_location_stated"
    if any((x.get("value") or {}).get("status") == "RANGE" for x in t) or \
            (c.get("duration") or {}).get("status") == "RANGE":
        return "S3_interval"
    if t:
        return "S2_temperature_location_unspecified"
    if c.get("medium"):
        return "S5_medium_only"
    return "S6_all_unknown"


def fmt(r: Mapping[str, Any]) -> str:
    """Normalised value as the v4 packet shows it: type/status, value or interval ends, '~' approximate, calendar."""
    t = f"{r['value_type']}/{r['status']}"
    u = r.get("canonical_unit") or ""
    if r["value_type"] == "POINT" and r.get("canonical_value") is not None:
        t += f" {'~' if r.get('approximate') else ''}{r['canonical_value']:.6g} {u}"
    elif r["value_type"] == "INTERVAL":
        lo, hi = r.get("canonical_low"), r.get("canonical_high")
        t += (f" {'(' if r.get('open_low') or lo is None else '['}{'-inf' if lo is None else format(lo, '.6g')}, "
              f"{'+inf' if hi is None else format(hi, '.6g')}{')' if r.get('open_high') or hi is None else ']'} {u}")
    if r.get("calendar_unit"):
        t += f" calendar:{r.get('calendar_value')} {r['calendar_unit']}"
    return t.strip()


def select(pool: Mapping[str, list[str]], *, seed: str, exclude: frozenset[str]) -> list[tuple[str, str]]:
    """(stratum, condition_id) pairs: per stratum the ``QUOTA`` smallest ranks after removing ``exclude``."""
    out = []
    for s, q in QUOTA.items():
        cands = sorted((c for c in pool.get(s, []) if c not in exclude), key=lambda c: rank(seed, c))
        if len(cands) < q:
            raise ValueError(f"stratum {s} has {len(cands)} eligible conditions, quota {q}")
        out += [(s, c) for c in cands[:q]]
    return out


def evd_context(evd: Mapping[str, Mapping]) -> tuple[dict, dict]:
    """Per condition: first source family and the (raw, normalised) measurement-context strings, as v4."""
    fam: dict[str, str] = {}
    ctx: dict[str, dict] = {}
    for r in evd.values():
        if r["status"] != "ACTIVE":
            continue
        cid = r["process"].get("condition_id")
        fam.setdefault(cid, r["source_family_id"])
        t, rf = r["target"], (r.get("derived") or {}).get("retention_factor")
        has = bool(rf and rf.get("status") in ("MEASURED", "CENSORED"))
        raw_c = (f"target_basis={t.get('basis')}; retention_value={'yes' if has else 'no'}; "
                 f"retention_status={(rf or {}).get('status', 'ABSENT')}; censor={((rf or {}).get('censor') or {}).get('kind')}")
        rt, cs = N.classify_retention_type(r["source_family_id"], t.get("basis"), has), N.classify_censoring(rf)
        norm_c = (f"basis={N.classify_basis(t.get('basis'))['basis_id']}; "
                  f"retention_type={rt['retention_type_id']}/{rt['status']}; censoring={cs['name']}")
        slot = ctx.setdefault(cid, {})
        slot[(raw_c, norm_c)] = slot.get((raw_c, norm_c), 0) + 1
    return fam, ctx


def build_row(i: int, s: str, cid: str, c: Mapping, fam: Mapping, ctx: Mapping, fp12: str) -> dict:
    d = N.from_qvalue("time_duration", c.get("duration"))
    temps = c.get("temperatures") or []
    ts = list(zip([t.get("location") for t in temps], N.normalize_temperatures(temps)))
    raw_pw = c.get("power") if isinstance(c.get("power"), dict) else None
    raw_p = c.get("pressure") if isinstance(c.get("pressure"), dict) else None
    pw, p = N.from_qvalue("microwave_power", raw_pw), N.from_qvalue("pressure", raw_p)
    reasons = {x for _, r in ts for x in r["reasons"]} | set(d["reasons"]) | set(p["reasons"]) | set(pw["reasons"])
    cc = sorted(ctx.get(cid, {}).items())[:4]
    return {"audit_id": f"CA-{i:03d}", "condition_id": cid, "stratum": s, "source_family": fam[cid],
            "raw_duration": (c.get("duration") or {}).get("raw"),
            "raw_temperatures(location|raw)": " ; ".join(f"{x.get('location')}|{(x.get('value') or {}).get('raw')}"
                                                        for x in temps),
            "raw_pressure": (raw_p or {}).get("raw") if raw_p else None,
            "raw_power": (raw_pw or {}).get("raw") if raw_pw else None, "medium": c.get("medium"),
            "normalised_duration": fmt(d),
            "normalised_temperatures": " ; ".join(f"{loc}:{fmt(r)}" for loc, r in ts) or "UNKNOWN",
            "normalised_pressure": fmt(p) + (f" ref={p.get('pressure_reference')}" if p.get("pressure_reference")
                                             else ""),
            "normalised_power": fmt(pw), "normalised_medium": c.get("medium") or "NOT_STATED",
            "normalised_reasons": ",".join(sorted(reasons)),
            "raw_measurement_context": " || ".join(f"{a} [n={n}]" for (a, _), n in cc),
            "normalised_measurement_context": " || ".join(b for (_, b), _n in cc),
            "normalizer_fingerprint_12": fp12}


def manifest(*, rows: list[Mapping], pool: Mapping[str, list], excluded: frozenset[str], fingerprint: Mapping,
             packet_sha: Mapping[str, str]) -> dict:
    fams = sorted({r["source_family"] for r in rows})
    return {"attempt": "07A-R1", "seed": SEED_R1, "n": len(rows), "quota": QUOTA,
            "pool_sizes": {k: len(v) for k, v in sorted(pool.items())},
            "selected_by_stratum": {s: sum(1 for r in rows if r["stratum"] == s) for s in QUOTA},
            "source_family_counts": {f: sum(1 for r in rows if r["source_family"] == f) for f in fams},
            "excluded_count": len(excluded),
            "excluded_set_sha256": hashlib.sha256("\n".join(sorted(excluded)).encode()).hexdigest(),
            "normalizer_fingerprint": dict(fingerprint),
            **{f"sha256_packet_{who}": h for who, h in sorted(packet_sha.items())},
            "audited_by_humans": False, "status": "DRAFT_PENDING_SIGNATURES",
            "preregistration": "reports/step07/07A_R1_preregistration_DRAFT.md"}
