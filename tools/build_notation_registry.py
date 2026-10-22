#!/usr/bin/env python3
"""Step 07: build registry/notation_rule_registry_v1.csv - data-derived catalogue of symbols/notations seen in raw COND strings.
Rules are the single source for the normaliser's notation handling (actions FLAG / QUALIFY / SPLIT are executed; INFO is documentation only).
meaning_status: STANDARD_CONVENTION | CANDIDATE_READINGS (several plausible, none source-verified) | UNKNOWN_UNVERIFIED. Counts/examples are observed in ledgers/data/COND.jsonl."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["rule_id", "field", "symbol", "pattern", "requires_value_type", "var_prefix", "candidate_readings", "meaning_status", "action", "reason_code", "evidence_needed", "observed_count", "examples"]
SLASH = r"\d+(?:[.,]\d+)?\s*/\s*\d+(?:[.,]\d+)?\s*(?:s|sec|min|mins|h|hr|hrs|hours?|d|days?)\b"
R = [
    ("NR-001", "duration", "/", SLASH, "INTERVAL", "", "range 15/20 min | alternatives | per-step times", "CANDIDATE_READINGS", "FLAG", "SLASH_NOTATION_RANGE_OR_ALTERNATIVES", "source legend for the database that uses it"),
    ("NR-002", "temperature", "- (spaced)", r"(?:^|[\s;,])[-−–]\s+\d", "", "temp_", "negative sign | range fragment of a preceding value", "CANDIDATE_READINGS", "FLAG", "SPACED_DASH_SIGN_OR_RANGE_FRAGMENT", "check the neighbouring value in the same COND record against the source"),
    ("NR-003", "any", "~ / approx / around / about / ca.", r"(~|≈|\bapprox\w*\.?|\bca\.|\babout\b|\baround\b|\broughly\b)", "", "", "approximate value (qualifier)", "STANDARD_CONVENTION", "QUALIFY", "APPROXIMATE", "none: value kept, approximate=True so downstream does not treat it as exact"),
    ("NR-004", "duration", ";", r";", "", "time_", "list of separate durations whose roles (e.g. cook vs storage) are not stated", "CANDIDATE_READINGS", "SPLIT", "MULTI_VALUE_LIST_ROLES_UNKNOWN", "source row context to assign a role per component"),
    ("NR-005", "temperature", "- (tight, leading)", r"(?:^|[\s;,(])[-−]\d", "", "temp_", "negative temperature (e.g. frozen storage)", "STANDARD_CONVENTION", "INFO", "", "location still required before use"),
    ("NR-006", "temperature", "- (between numbers)", r"\d\s*[-–−]\s*\d", "", "temp_", "range low-high", "STANDARD_CONVENTION", "INFO", "", ""),
    ("NR-007", "any", "> / above / over / at least", r"(>|≥|\babove\b|\bover\b|\bmore than\b|\bat least\b)", "", "", "open upper bound (value is a lower limit)", "STANDARD_CONVENTION", "INFO", "", ""),
    ("NR-008", "any", "< / below / up to", r"(<|≤|\bbelow\b|\bunder\b|\bless than\b|\bup to\b)", "", "", "open lower bound (value is an upper limit)", "STANDARD_CONVENTION", "INFO", "", ""),
    ("NR-009", "duration", ", (descriptor)", r"[A-Za-z],\s*[A-Za-z]", "", "time_", "separator between descriptor words (USDA style), not between values", "CANDIDATE_READINGS", "INFO", "", "USDA legend"),
    ("NR-010", "duration", "CKD BLD BKD DRND FRIED", r"\b(CKD|BLD|BKD|DRND|DRAIND|FRIED|BRLD|STMD)\b", "", "time_", "USDA method/state abbreviations; expansions not source-verified here", "UNKNOWN_UNVERIFIED", "INFO", "", "USDA SR documentation (check, do not guess)"),
    ("NR-011", "duration", "+", r"\+", "", "time_", "sequential methods (BOILED+BAKED) | combined", "CANDIDATE_READINGS", "INFO", "", "USDA legend"),
    ("NR-012", "duration", "/ (between words)", r"[A-Za-z]/[A-Za-z]", "", "time_", "alternative or combined methods (BKD/SIMMRD)", "CANDIDATE_READINGS", "INFO", "", "USDA legend"),
    ("NR-013", "pressure", "psi bar atm kPa MPa", r"\b(psi|bar|atm|kpa|mpa)\b", "", "", "unit; gauge vs absolute not stated", "STANDARD_CONVENTION", "INFO", "", "reference stated by source (existing PRESSURE_REFERENCE_UNSPECIFIED)"),
]


def scan():
    rows = []
    latest = {}  # append-only ledger: latest version per id only
    for line in open(ROOT / "ledgers/data/COND.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            latest[r["id"]] = r
    for c in latest.values():
        d = c.get("duration") or {}
        if d.get("raw"):
            rows.append(("duration", d["raw"]))
        for t in c.get("temperatures") or []:
            if (t.get("value") or {}).get("raw"):
                rows.append(("temperature", t["value"]["raw"]))
        for k in ("pressure", "power"):
            v = c.get(k)
            if isinstance(v, dict) and v.get("raw"):
                rows.append((k, v["raw"]))
    return rows


if __name__ == "__main__":
    raws = scan()
    out = []
    for rid, fld, sym, pat, vt, vp, cand, ms, act, rc, ev in R:
        rx = re.compile(pat, re.I)
        hit = [r for f, r in raws if (fld in ("any", f)) and rx.search(str(r))]
        ex = list(dict.fromkeys(hit))[:3]
        out.append(dict(rule_id=rid, field=fld, symbol=sym, pattern=pat, requires_value_type=vt, var_prefix=vp, candidate_readings=cand, meaning_status=ms, action=act, reason_code=rc, evidence_needed=ev, observed_count=len(hit), examples=" || ".join(ex)))
    with open(ROOT / "registry/notation_rule_registry_v1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(out)
    for o in out:
        print(o["rule_id"], o["field"], o["action"], o["observed_count"], o["examples"][:70])
