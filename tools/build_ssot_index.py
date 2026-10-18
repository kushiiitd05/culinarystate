#!/usr/bin/env python3
"""Build docs/SSOT_INDEX.md: headings with line ranges, ID anchors, boxed statements.

Verifies counts against master plan Appendix 1. Exit code 1 if any check fails.
Never loads the SSOT into an LLM context — read targeted ranges via the index.
"""
from __future__ import annotations

import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "docs/SSOT/computational_gastronomy_master_ssot_v15_0.md"
OUT = ROOT / "docs/SSOT_INDEX.md"

ID_PATTERNS = {
    "RQ16": r"\bRQ16-(\d{2})\b",
    "RQ13E": r"\bRQ13E-(\d{2})\b",
    "E16": r"\bE16-([A-L])\b",
    "E13E": r"\bE13E-(\d{2})\b",
    "G13E": r"\bG13E-(\d{2})\b",
    "G16": r"\bG16-([A-Z]+)\b",
    "G15": r"\bG15-(\d{1,2}|H|HYB|I|INV|R|RXN)\b",
    "G14": r"\bG14-(\d{1,2})\b",
    "G13": r"\bG13-([0-4])\b",
    "RISK-E": r"\bRISK-E(\d{1,2})\b",
    "R13E": r"\bR13E-(\d{2})\b",
}
EXPECTED = {
    "RQ16": {f"{i:02d}" for i in range(1, 31)},
    "RQ13E": {f"{i:02d}" for i in range(1, 23)},
    "E16": set("ABCDEFGHIJKL"),
    "E13E": {f"{i:02d}" for i in range(1, 19)},
    "G13E": {f"{i:02d}" for i in range(1, 16)},
    "G16": {"CAL", "CONFLICT", "DATA", "DEC", "EVID", "FT", "GRAPH", "OOD", "PROV", "QTY", "REC", "SEM", "TRANS", "VOCAB"},
    "G15": {str(i) for i in range(1, 13)} | {"H", "HYB", "I", "INV", "R", "RXN"},
    "G14": {str(i) for i in range(1, 13)},
    "G13": {str(i) for i in range(0, 5)},
    "RISK-E": {str(i) for i in range(1, 13)},
    "R13E": {f"{i:02d}" for i in range(1, 21)},
}


def main() -> int:
    raw = SSOT.read_bytes()
    lines = raw.decode("utf-8").splitlines()
    heads = [(i + 1, len(m.group(1)), m.group(2).strip())
             for i, l in enumerate(lines) if (m := re.match(r"^(#{1,3})\s+(.*)", l))]
    ids: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    boxed: list[tuple[int, str]] = []
    for n, l in enumerate(lines, 1):
        for fam, pat in ID_PATTERNS.items():
            for m in re.finditer(pat, l):
                ids[fam][m.group(1)].append(n)
        if "\\boxed{" in l or (l.strip() == "\\boxed{"):
            boxed.append((n, l.strip()[:160]))

    checks = []
    top = sum(1 for _, lvl, _ in heads if lvl == 1)
    checks.append(("bytes ≈ 1,799,542", len(raw), abs(len(raw) - 1_799_542) < 2000))
    checks.append(("lines = 45,697", len(lines), len(lines) == 45_697))
    checks.append(("top-level # sections = 309", top, top == 309))
    for fam, exp in EXPECTED.items():
        found = set(ids[fam])
        missing = sorted(exp - found)
        extra = sorted(found - exp)
        checks.append((f"{fam} ids", f"found {len(found & exp)}/{len(exp)}"
                       + (f" missing={missing}" if missing else "") + (f" extra={extra[:8]}" if extra else ""),
                       not missing))

    out = ["# SSOT v15.0 INDEX (machine-built — `python tools/build_ssot_index.py`)", "",
           f"Source: `{SSOT.relative_to(ROOT)}` · sha256 `{hashlib.sha256(raw).hexdigest()[:16]}` · "
           f"{len(raw):,} bytes · {len(lines):,} lines", "",
           "Read targeted ranges: `sed -n 'START,ENDp' docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`", "",
           "## Inventory check (vs master plan Appendix 1)", "", "| Check | Value | OK |", "|---|---|---|"]
    out += [f"| {c} | {v} | {'✅' if ok else '❌'} |" for c, v, ok in checks]
    out += ["", "## ID anchors (first 6 line numbers each)", ""]
    for fam in ID_PATTERNS:
        out.append(f"**{fam}:** " + "; ".join(f"{k}→{','.join(map(str, v[:6]))}"
                                               for k, v in sorted(ids[fam].items())))
        out.append("")
    out += ["## Headings (H1–H3) with line ranges", "", "| Start | End | Lvl | Heading |", "|---|---|---|---|"]
    for idx, (n, lvl, t) in enumerate(heads):
        end = next((m - 1 for m, l2, _ in heads[idx + 1:] if l2 <= lvl), len(lines))
        out.append(f"| {n} | {end} | {lvl} | {t[:140].replace('|', '/')} |")
    out += ["", f"## Boxed statements ({len(boxed)})", ""]
    out += [f"- L{n}: `{t.replace('`', '')}`" for n, t in boxed]
    OUT.write_text("\n".join(out) + "\n")
    bad = [c for c in checks if not c[2]]
    for c in checks:
        print(("OK  " if c[2] else "FAIL"), c[0], "->", c[1])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
