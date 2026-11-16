#!/usr/bin/env python3
"""T9-C07-R3 (S179): which decisions and gates were made by a human and which by an AI, generated from DECISIONS.md.

Every ``### D-NNN`` entry is classed from its ``**Approver:**`` line:
- ``AI_DELEGATED_D085``: approver ``ksh+prv (AI, D-085)`` (D-085: the personas act on the humans' behalf);
- ``AI_PERSONA_D071`` / ``MIXED_PERSONA_AND_HUMAN``: ksh / prv under D-071 (alone, or with a human for part);
- ``AI_AGENT_PROVISIONAL``: approver starts with "Claude" (reversible agent choices for the humans to confirm);
- ``HUMAN``: Kush and / or Parv (a relay through Kush is noted), or a standing user rule;
- ``HUMAN`` (``basis`` TITLE_OR_INSTRUCTION): no Approver line, but the title says "decided by Kush" / "reported by
  Kush" or names Parv's own request or review, or the ``**Instruction:**`` line is Kush's or Parv's;
- ``NO_APPROVER_LINE``: none of these.

  python tools/s179_gate_provenance_report.py [--check]

Writes `reports/final/sections/S179_gate_provenance_DRAFT.md`. Deterministic; ``--check`` compares with the file.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "DECISIONS.md"
OUT = ROOT / "reports/final/sections/S179_gate_provenance_DRAFT.md"
ENTRY = re.compile(r"^### (D-\d{3}[a-z]?) · ([0-9-]+) · (.+)$", re.M)
APPROVER = re.compile(r"\*\*Approver[^*]*:\*\*\s*(.+)")
HUMAN_HINT = re.compile(r"(decided|reported) by Kush|\bParv(?:'s)? (?:request|review|authoris|cuisine|Step)|"
                        r"\*\*Instruction:\*\* (?:Kush|Parv)\b")
CLASSES = ("HUMAN", "AI_DELEGATED_D085", "AI_PERSONA_D071", "MIXED_PERSONA_AND_HUMAN", "AI_AGENT_PROVISIONAL",
           "NO_APPROVER_LINE")


def classify(approver: str | None) -> str:
    if not approver:
        return "NO_APPROVER_LINE"
    a = approver.strip()
    if "ksh+prv (AI, D-085)" in a:
        return "AI_DELEGATED_D085"
    if re.search(r"\bAI\b.*D-071|D-071.*\bAI\b", a):
        return "MIXED_PERSONA_AND_HUMAN" if re.search(r"\bKush for\b|\bParv for\b", a) else "AI_PERSONA_D071"
    if a.startswith("Claude"):
        return "AI_AGENT_PROVISIONAL"
    if re.search(r"\b(Kush|Parv)\b|standing user rule", a):
        return "HUMAN"
    return "NO_APPROVER_LINE"


def entries(text: str) -> list[dict]:
    heads = list(ENTRY.finditer(text))
    out = []
    for i, m in enumerate(heads):
        body = text[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        ap = APPROVER.search(body)
        approver = ap.group(1).strip() if ap else None
        cls, basis = classify(approver), "APPROVER_LINE"
        if cls == "NO_APPROVER_LINE" and re.search(r"decided by ksh\+prv \(AI, D-085\)", m.group(3)):
            cls, basis = "AI_DELEGATED_D085", "TITLE_OR_INSTRUCTION"
        if cls == "NO_APPROVER_LINE" and HUMAN_HINT.search(m.group(3) + "\n" + body[:400]):
            cls, basis = "HUMAN", "TITLE_OR_INSTRUCTION"
        out.append({"id": m.group(1), "date": m.group(2), "title": m.group(3).strip(), "approver": approver,
                    "class": cls, "basis": basis, "relayed": bool(approver and "relay" in approver.lower())})
    return out


def render(rows: list[dict]) -> str:
    n = Counter(r["class"] for r in rows)
    lines = ["# Gate provenance: human and AI decisions (S179, T9-C07-R3)", "",
             "Status: **AI_DRAFTED, generated** by `tools/s179_gate_provenance_report.py` from `DECISIONS.md`. Each "
             "decision is classed from its Approver line or explicit recorded title/instruction.",
             "",
             "**What D-085 changed.** From D-085 (2026-11-10) the AI personas ksh and prv (one model) act on Kush and "
             "Parv's behalf for every remaining human gate, always under the name `ksh+prv (AI, D-085)` and never a "
             "human's. Every output that rests on such an act carries `NO_HUMAN_SIGNOFF_D085`. Agreement between the "
             "two personas is not inter-rater evidence, so 07.A-R1 was not attempted and its v4 FAIL stays on record; "
             "AI-written gold is labelled AI (`AI_DRAFTED_GOLD`), never HUMAN_BLIND.",
             "", "## Counts", "", "| Class | Decisions |", "|---|---|"]
    lines += [f"| {c} | {n.get(c, 0)} |" for c in CLASSES]
    lines += [f"| **all** | {len(rows)} |", "",
              f"Of the HUMAN decisions, {sum(r['relayed'] for r in rows if r['class'] == 'HUMAN')} record Parv's view "
              f"as relayed by Kush, and {sum(r['basis'] == 'TITLE_OR_INSTRUCTION' and r['class'] == 'HUMAN' for r in rows)} name the human in the "
              "title or instruction line instead of an Approver line.", "", "## Decisions not made by a human", "",
              "| Decision | Date | Title | Class |", "|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['date']} | {r['title'].replace('|', '/')} | {r['class']} |"
              for r in rows if r["class"] != "HUMAN"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    text = render(entries(DECISIONS.read_text(encoding="utf-8")))
    if a.check:
        ok = OUT.is_file() and OUT.read_text(encoding="utf-8") == text
        print("OK" if ok else "DIFFERS")
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
