#!/usr/bin/env python3
"""Quantity grammar coverage over the A1 BBC Good Food corpus (local raw data).

  /opt/anaconda3/bin/python tools/quantity_coverage.py [--raw ../a1/A1\\ 3/data/raw/recipes_raw.jsonl]
Writes reports/quantity_coverage_v0.json and reports/quantity_coverage_v0.md (derived stats only).
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.quantity.grammar import parse_line  # noqa: E402
from culinarystate.quantity.normalize import normalize  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--raw", default=str(ROOT.parent / "a1" / "A1 3" / "data" / "raw" / "recipes_raw.jsonl"))
ap.add_argument("--locale", default="UK")
a = ap.parse_args()

lines = []
with open(a.raw) as fh:
    for row in fh:
        lines += json.loads(row).get("ingredient_phrases_raw") or []

kinds, units, methods, qlev, flags = Counter(), Counter(), Counter(), Counter(), Counter()
chan = Counter()
none_heads, numeric_no_unit_heads = Counter(), Counter()
for line in lines:
    p = parse_line(line)
    z = normalize(p, locale=a.locale)
    kinds[p.kind] += 1
    units[p.unit_key or "-"] += 1
    methods[z.conversion_method] += 1
    qlev[z.q_level] += 1
    for f in z.flags:
        flags[f.split(":")[0]] += 1
    for name, q in (("mass", z.mass_g), ("volume", z.volume_ml), ("count", z.count)):
        chan[(name, q["status"])] += 1
    known = any(q["status"] in ("MEASURED", "RANGE") for q in (z.mass_g, z.volume_ml, z.count))
    chan[("any_numeric_channel", known)] += 1
    if p.kind == "NONE":
        none_heads[" ".join(re.findall(r"[a-z]+", line.lower())[:2])] += 1
    if p.kind in ("NUMBER", "RANGE", "FRACTION", "MIXED") and p.unit_key is None:
        numeric_no_unit_heads[" ".join(p.rest.lower().split()[:1])] += 1

N = len(lines)
pct = lambda c: round(100 * c / N, 2)  # noqa: E731
report = {
    "n_lines": N, "locale": a.locale,
    "kinds": {k: [v, pct(v)] for k, v in kinds.most_common()},
    "conversion_method": {k: [v, pct(v)] for k, v in methods.most_common()},
    "q_level_mass": {k: [v, pct(v)] for k, v in sorted(qlev.items())},
    "channels": {f"{k[0]}:{k[1]}": [v, pct(v)] for k, v in sorted(chan.items(), key=str)},
    "flags": dict(flags.most_common()),
    "units_top40": dict(units.most_common(40)),
    "no_quantity_heads_top40": dict(none_heads.most_common(40)),
    "count_without_unit_first_word_top40": dict(numeric_no_unit_heads.most_common(40)),
}
out = ROOT / "reports"
out.mkdir(exist_ok=True)
(out / "quantity_coverage_v0.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
md = [f"# Quantity grammar coverage v0 — A1 BBC corpus ({N:,} ingredient lines, locale {a.locale})", "",
      "| Kind | n | % |", "|---|---|---|"] + [f"| {k} | {v:,} | {p} |" for k, (v, p) in report["kinds"].items()]
md += ["", "| Mass evidence (Q-level) | n | % |", "|---|---|---|"] + \
      [f"| {k} | {v:,} | {p} |" for k, (v, p) in report["q_level_mass"].items()]
md += ["", "| Channel:status | n | % |", "|---|---|---|"] + \
      [f"| {k} | {v:,} | {p} |" for k, (v, p) in report["channels"].items()]
md += ["", "## Flags", ""] + [f"- {k}: {v:,}" for k, v in report["flags"].items()]
md += ["", "## Lines with no quantity — top first words", ""] + \
      [f"- {k}: {v}" for k, v in report["no_quantity_heads_top40"].items()]
(out / "quantity_coverage_v0.md").write_text("\n".join(md) + "\n")
print(json.dumps({k: report[k] for k in ("n_lines", "kinds", "q_level_mass", "flags")}, indent=1))
print("channels", report["channels"])
print("NONE heads", list(report["no_quantity_heads_top40"].items())[:25])
print("units", list(report["units_top40"].items())[:40])
