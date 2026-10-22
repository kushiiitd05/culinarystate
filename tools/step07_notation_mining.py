#!/usr/bin/env python3
"""Step 07: mine the notation actually present in raw condition strings (COND ledger) so normaliser rules are derived from data, not guessed.
Read-only. Writes reports/step07/_notation_mining.json (feature -> count, examples, current normaliser status distribution)."""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence import condition_normalizer as N  # noqa: E402

FEATURES = {
    "slash_between_numbers": r"\d\s*/\s*\d", "dash_between_numbers": r"\d\s*[-–−]\s*\d", "spaced_leading_dash": r"(?:^|[\s;,])[-−–]\s+\d", "tight_leading_dash": r"(?:^|[\s;,(])[-−]\d",
    "tilde_or_approx": r"(~|≈|\bapprox|\bca\.|\babout\b|\baround\b)", "greater_than": r"(>|≥|\babove\b|\bover\b|\bmore than\b|\bat least\b)", "less_than": r"(<|≤|\bbelow\b|\bunder\b|\bless than\b|\bup to\b)",
    "to_word_range": r"\d\s*to\s*\d", "plus_sign": r"\+", "semicolon_list": r";", "comma_list": r",", "multiplier_x": r"\d\s*[x×]\s*\d", "or_alternative": r"\bor\b", "and_word": r"\band\b", "degree_symbol_variants": r"[°º]|\bdeg",
    "fahrenheit_unit": r"°\s*F|\bdegF|\bF\b", "kelvin_unit": r"\bK\b", "parentheses": r"[()]", "per_slash_unit": r"[a-z]/(?:100\s*)?[a-z]", "decimal_comma": r"\d,\d(?!\d{3})", "hrs_variants": r"\bhrs?\b|\bhours?\b", "min_variants": r"\bmins?\b|\bminutes?\b",
    "psi_bar_atm_unit": r"\b(psi|bar|atm|kpa|mpa)\b", "watts": r"\b\d+\s*(w|kw|watts?)\b", "percent_sign": r"%", "usda_abbrev_cooking": r"\b(CKD|BLD|BKD|DRND|DRAIND|FRIED|BRLD|ROASTED|STMD)\b",
}
RX = {k: re.compile(v, re.I) for k, v in FEATURES.items()}
L = ROOT / "ledgers/data"
cond = {}
for line in open(L / "COND.jsonl", encoding="utf-8"):
    if line.strip():
        r = json.loads(line)
        cond[r["id"]] = r
fields = []  # (field, var, raw, qv, location)
for c in cond.values():
    d = c.get("duration") or {}
    if d.get("raw"):
        fields.append(("duration", "time_duration", d["raw"], d, None))
    for t in c.get("temperatures") or []:
        v = t.get("value") or {}
        if v.get("raw"):
            fields.append(("temperature", N.temperature_variable_for(t.get("location")), v["raw"], v, t.get("location")))
    for k, var in (("pressure", "pressure"), ("power", "microwave_power")):
        v = c.get(k)
        if isinstance(v, dict) and v.get("raw"):
            fields.append((k, var, v["raw"], v, None))
stat = defaultdict(Counter)
ex = defaultdict(list)
cnt = Counter()
for fld, var, raw, qv, loc in fields:
    res = N.from_qvalue(var, qv, location=loc)
    for feat, rx in RX.items():
        if rx.search(str(raw)):
            cnt[(fld, feat)] += 1
            stat[(fld, feat)][f"{res['value_type']}/{res['status']}"] += 1
            if len(ex[(fld, feat)]) < 3 and raw not in ex[(fld, feat)]:
                ex[(fld, feat)].append(raw)
out = {f"{a}|{b}": {"count": n, "examples": ex[(a, b)], "current_normaliser": dict(stat[(a, b)])} for (a, b), n in cnt.most_common()}
(ROOT / "reports/step07/_notation_mining.json").write_text(json.dumps({"fields_scanned": len(fields), "features": out}, indent=1, ensure_ascii=False))
print(len(fields), "raw strings scanned")
for k, v in list(out.items())[:40]:
    print(k.ljust(42), str(v["count"]).rjust(5), v["current_normaliser"], v["examples"][:2])
