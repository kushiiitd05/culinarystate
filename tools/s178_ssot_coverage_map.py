#!/usr/bin/env python
"""S178 (T0-C19-R1): SSOT coverage map. Which top-level SSOT sections does no ledger component anchor?

Method (reproducible, read-only, counts and titles only):
1. Top-level numbered sections come from ``docs/SSOT_INDEX.md`` (level-1 rows ``N. TITLE``, ``257A`` style letters kept).
2. A section is ANCHORED if some component of ``registry/component_ledger_v1.csv`` names its number in ``ssot_anchor``
   (``§N``, ``§N.M``, ranges ``§a-§b``, ``§§a-b``, letter ranges ``§257G-§257K``) or if a line range ``La-b`` / ``Ln`` of
   an anchor overlaps the section's line range. T0-C19 itself (the coverage component) is excluded: it anchors the
   sections it exists to classify.
3. Every UNANCHORED section must have a class in ``registry/ssot_coverage_classes_S178.csv``:
   SUPERSEDED / OUT_OF_SCOPE_25NOV / OWNER / UNCOVERED (classes are the agent's reading, AI_DRAFTED, not human-verified).

    python tools/s178_ssot_coverage_map.py            # writes reports/s178/ssot_coverage_map.csv
    python tools/s178_ssot_coverage_map.py --check    # exit 1 if a class is missing or surplus
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs/SSOT_INDEX.md"
LEDGER = ROOT / "registry/component_ledger_v1.csv"
CLASSES = ROOT / "registry/ssot_coverage_classes_S178.csv"
OUT = ROOT / "reports/s178/ssot_coverage_map.csv"
EXCLUDE = {"T0-C19"}
VALID = {"SUPERSEDED", "OUT_OF_SCOPE_25NOV", "OWNER", "UNCOVERED"}


def sections() -> dict[str, tuple[int, int, str]]:
    out = {}
    for line in INDEX.read_text().split("\n"):
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*1\s*\|\s*(.*?)\s*\|\s*$", line)
        if not m:
            continue
        t = re.match(r"^(\d+[A-Z]?)\.\s*(.*)", m.group(3))
        if t:
            out[t.group(1)] = (int(m.group(1)), int(m.group(2)), t.group(2))
    return out


def anchor_sections(anchor: str) -> set[str]:
    out: set[str] = set()
    s = anchor.replace("–", "-").replace("—", "-")
    for m in re.finditer(r"§\s*(\d+)([A-Z]?)(?:\.\d+)*\s*-\s*§?\s*(\d+)([A-Z]?)(?![\d.])", s):
        a, la, b, lb = int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)
        if a == b and la and lb:
            out |= {f"{a}{chr(c)}" for c in range(ord(la), ord(lb) + 1)}
        elif not la and not lb and a < b and b - a < 200:
            out |= {str(n) for n in range(a, b + 1)}
    for m in re.finditer(r"§\s*(\d+)([A-Z]?)(?:\.\d+)*", s):
        out.add(m.group(1) + m.group(2))
    for m in re.finditer(r"§§\s*(\d+)\s*-\s*(\d+)", s):
        out |= {str(n) for n in range(int(m.group(1)), int(m.group(2)) + 1)}
    return out


def line_ranges(anchor: str) -> list[tuple[int, int]]:
    r = [(int(m.group(1)), int(m.group(2))) for m in re.finditer(r"L\s*(\d{3,6})\s*-\s*(\d{3,6})", anchor)]
    r += [(int(m.group(1)),) * 2 for m in re.finditer(r"(?<![\d-])L\s*(\d{3,6})(?![\d-])", anchor)]
    return r


def anchored() -> dict[str, list[str]]:
    secs = sections()
    by: dict[str, set[str]] = {k: set() for k in secs}
    seen = set()
    with LEDGER.open(newline="") as fh:
        for row in csv.DictReader(fh):
            cid = row["component_id"]
            if cid in EXCLUDE or cid in seen:
                continue
            seen.add(cid)
            nums = anchor_sections(row["ssot_anchor"])
            lr = line_ranges(row["ssot_anchor"])
            for k, (a, b, _t) in secs.items():
                if k in nums or any(not (hi < a or lo > b) for lo, hi in lr):
                    by[k].add(cid)
    return {k: sorted(v) for k, v in by.items()}


def read_classes() -> dict[str, dict]:
    with CLASSES.open(newline="") as fh:
        return {r["section"]: r for r in csv.DictReader(fh)}


def problems() -> list[str]:
    secs, by, cls = sections(), anchored(), read_classes()
    un = {k for k, v in by.items() if not v}
    p = [f"unanchored section {k} has no class" for k in sorted(un - set(cls))]
    p += [f"class row for {k} but the section is anchored or missing" for k in sorted(set(cls) - un)]
    p += [f"section {k}: invalid class {r['class']}" for k, r in cls.items() if r["class"] not in VALID]
    p += [f"section {k}: class OWNER needs an owner" for k, r in cls.items() if r["class"] == "OWNER" and not r["owner_or_superseded_by"]]
    return p


def build() -> list[dict]:
    secs, by, cls = sections(), anchored(), read_classes()
    rows = []
    for k, (a, b, t) in sorted(secs.items(), key=lambda kv: kv[1][0]):
        c = cls.get(k)
        rows.append({"section": k, "line_start": a, "line_end": b, "title": t,
                     "status": "ANCHORED" if by[k] else "UNANCHORED",
                     "anchored_by": ";".join(by[k][:6]) + ("..." if len(by[k]) > 6 else ""),
                     "class": c["class"] if c else "", "owner_or_superseded_by": c["owner_or_superseded_by"] if c else "",
                     "rationale": c["rationale"] if c else ""})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    p = problems()
    for x in p:
        print("PROBLEM:", x)
    if a.check:
        if not p:
            print("every unanchored section has a class")
        return 1 if p else 0
    rows = build()
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    un = [r for r in rows if r["status"] == "UNANCHORED"]
    print(f"{len(rows)} top-level sections; {len(un)} unanchored; wrote {OUT.relative_to(ROOT)}")
    return 1 if p else 0


if __name__ == "__main__":
    sys.exit(main())
