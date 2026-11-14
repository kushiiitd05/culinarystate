#!/usr/bin/env python3
"""Exhaustive lexical number inventory and claim-word review queue for draft text.

Classification is local-label assistance, not a source-entailment certificate.
Unclassified numbers remain explicit; an empty gate set cannot authorize claims.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

NUMBER = re.compile(r"(?<!\d)(?:(?<![A-Za-z_])[+-])?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?(?:/\d+)?%?")
CLAIM = re.compile(r"(?<![\w])(?:validated|calibrated|supported|beats)(?![\w])", re.I)
CLASSES = [("E3_UNVERIFIED", "EVD(E3_UNVERIFIED/COND_UNAUDITED)"),
           ("E3-unverified", "EVD(E3_UNVERIFIED/COND_UNAUDITED)"),
           ("COND_UNAUDITED", "EVD(E3_UNVERIFIED/COND_UNAUDITED)"),
           ("TEXT_STATED", "TEXT_STATED"), ("SCENARIO", "SCENARIO/ASSUMED_DEFAULT"),
           ("ASSUMED_DEFAULT", "SCENARIO/ASSUMED_DEFAULT"), ("MODEL_DERIVED", "MODEL_DERIVED/NON_CITABLE"),
           ("DIAGNOSTIC", "DIAGNOSTIC/PRIOR_EXPOSURE"), ("PRIOR_EXPOSURE", "DIAGNOSTIC/PRIOR_EXPOSURE"),
           ("RESEARCH_ONLY", "RESEARCH_ONLY")]


def inspect_text(text, *, passed_gates=()):
    numbers, flags = [], []
    heading_context, paragraph = "", []
    for line_number, line in enumerate(text.splitlines(), 1):
        if re.match(r"^#{1,6}\s", line):
            heading_context, paragraph = line, []
        elif not line.strip():
            paragraph = []
        paragraph.append(line)
        context = heading_context + "\n" + "\n".join(paragraph[-8:])
        for match in NUMBER.finditer(line):
            token = match.group()
            before, after = line[:match.start()], line[match.end():]
            word_before = re.search(r"[\w.-]+$", before)
            embedded = bool((before and before[-1].isalnum()) or (after and after[0].isalnum()))
            id_prefix = bool(re.search(r"(?:EVD|COND|SVAR|ING|PROC|D|S|M|H|G|AAK|NEG|RUN|EXP|THR|SD|PC|T|B)[-_]?$", before))
            if id_prefix or embedded or (word_before and word_before.group().endswith("SHA")):
                cls = "IDENTIFIER_METADATA"
            elif re.search(r"\d{4}-\d{2}-\d{2}", line[max(0,match.start()-8):match.end()+8]):
                cls = "DATE_METADATA"
            else:
                cls = next((cls for label, cls in CLASSES if label.casefold() in context.casefold()), "UNCLASSIFIED_REVIEW_REQUIRED")
            numbers.append({"line": line_number, "column": match.start() + 1, "token": token, "class": cls,
                            "classification_basis": "LOCAL_LABEL_HEURISTIC" if cls not in ("IDENTIFIER_METADATA", "DATE_METADATA") else "LEXICAL_METADATA"})
        for match in CLAIM.finditer(line):
            prefix = line[max(0, match.start()-70):match.start()].casefold()
            negated = bool(re.search(r"\b(?:no|not|never|cannot|without|un)\b[^.;!?]*$", prefix))
            gate = next((g for g in sorted(passed_gates) if re.search(r"(?<![\w-])" + re.escape(g) + r"(?![\w-])", line)), None)
            if not negated and not gate:
                flags.append({"line": line_number, "column": match.start() + 1, "word": match.group(),
                              "reason": "NO_SUPPLIED_PASSED_GATE_OR_NEGATED_CONTEXT"})
    return {"numbers": numbers, "number_count": len(numbers),
            "class_counts": dict(Counter(r["class"] for r in numbers)),
            "unclassified": sum(r["class"] == "UNCLASSIFIED_REVIEW_REQUIRED" for r in numbers), "claim_flags": flags}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--passed-gate-manifest", type=Path)
    args = parser.parse_args(argv)
    if args.out.exists():
        parser.error("refusing overwrite")
    gates = set()
    if args.passed_gate_manifest:
        # Caller must supply explicit evidence paths and hashes, not just invented PASS strings.
        manifest = json.loads(args.passed_gate_manifest.read_text())
        for gate, record in manifest.items():
            path = Path(record["evidence_path"])
            if record["status"] != "PASS" or hashlib.sha256(path.read_bytes()).hexdigest() != record["evidence_sha256"]:
                parser.error("invalid gate evidence")
            gates.add(gate)
    artifacts = {str(p): inspect_text(p.read_text(), passed_gates=gates) for p in args.artifact}
    report = {"record": "DRAFT_NUMBER_CLASS_INVENTORY", "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "labels": ["AI_PRECHECKED", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"], "scientific_gate_pass": False,
              "artifact_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in args.artifact},
              "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "passed_gates_supplied": sorted(gates),
              "artifacts": artifacts, "status": "REVIEW_QUEUE" if any(v["unclassified"] or v["claim_flags"] for v in artifacts.values()) else "SCOPED_LEXICAL_CHECK_COMPLETE",
              "limitations": ["Lists numeric substrings including identifiers; not a scientific value/source entailment auditor.",
                              "Classes inferred from local paragraph/heading labels; no global default class or claim approval.",
                              "Positive-word flags can include methodological quotations; exceptions require explicit contextual review.",
                              "Supplied gate evidence hashes prove file identity, not the scientific validity of a passed-gate claim.",
                              "Author exceptions approval/final edits excluded by current user scope."]}
    with args.out.open("x") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({p: {k: v[k] for k in ("number_count", "unclassified")} | {"claim_flags": len(v["claim_flags"])} for p, v in artifacts.items()}))


if __name__ == "__main__":
    main()
