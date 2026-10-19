#!/usr/bin/env python3
"""Validate Kush's H_STATE questions (benchmark/h_state/questions_to_write.csv). Checks only; writes nothing, runs no B3/B4.

  /opt/anaconda3/bin/python tools/validate_hstate_questions.py [path]
Rules: 80 rows = 20 recipes x (3 STATE_DEPENDENT + 1 CONTROL); author == Kush; question_text filled by Kush; gold_mode valid;
gold_evidence_cell = known ACTIVE EVD id(s) or UNSUPPORTED; no near-duplicate text; STATE_DEPENDENT questions must NOT let the
production question parser recover both an ingredient and a process from the text alone (else the state is not required);
CONTROL questions must state ingredient and process. Exit 2 = BLOCKED_HUMAN while questions are unwritten.
"""
import csv
import sys
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
MODES = {"ANSWER", "ASK", "COMPARE", "DIAGNOSE", "RECOVER", "RECOMMEND", "ABSTAIN"}
REQ = {"ENTITY", "FORM", "PROCESS", "LOCATION", "TIME", "TEMPERATURE", "ENDPOINT", "PRIOR_EVENT", "COMPOSITION", "RESERVED_STATUS", "COMBINATION"}


def check(rows, parse=None, evd_ids=None):
    errs = []
    if len(rows) != 80:
        errs.append(f"{len(rows)} rows, expected 80")
    c = Counter((r["recipe_id"], r["question_class"]) for r in rows)
    for rid in {r["recipe_id"] for r in rows}:
        if c[(rid, "STATE_DEPENDENT")] != 3 or c[(rid, "CONTROL")] != 1:
            errs.append(f"{rid}: needs 3 STATE_DEPENDENT + 1 CONTROL")
    texts = []
    for r in rows:
        q = r["question_id"]
        if not r["question_text"].strip():
            errs.append(f"{q}: question_text empty (BLOCKED_HUMAN)")
            continue
        if r["author"].strip() != "Kush":
            errs.append(f"{q}: author must be Kush")
        if r["gold_mode"] not in MODES:
            errs.append(f"{q}: gold_mode {r['gold_mode']!r} invalid")
        ev = r["gold_evidence_cell"].strip()
        if ev != "UNSUPPORTED" and (not ev or (evd_ids is not None and not all(x.strip() in evd_ids for x in ev.split(";")))):
            errs.append(f"{q}: gold_evidence_cell must be UNSUPPORTED or known EVD id(s) separated by ';'")
        if r["question_class"] == "STATE_DEPENDENT":
            if not r["state_information_required"].strip() or not set(x.strip() for x in r["state_information_required"].split(";")) <= REQ:
                errs.append(f"{q}: state_information_required must list fields from {sorted(REQ)}")
            if not r["why_state_is_required"].strip():
                errs.append(f"{q}: why_state_is_required empty")
        if parse is not None:
            s = parse(r["question_text"])
            if r["question_class"] == "STATE_DEPENDENT" and s.ingredient_id and s.processes:
                errs.append(f"{q}: parser recovers ingredient AND process from the text alone (state not required)")
            if r["question_class"] == "CONTROL" and not (s.ingredient_id and s.processes):
                errs.append(f"{q}: control must state ingredient and process")
        for t, other in texts:
            if SequenceMatcher(None, r["question_text"].lower(), t.lower()).ratio() > 0.85:
                errs.append(f"{q}: near-duplicate of {other}")
        texts.append((r["question_text"], q))
    return errs


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "benchmark" / "h_state" / "questions_to_write.csv"
    rows = list(csv.DictReader(path.open()))
    if not any(r["question_text"].strip() for r in rows):
        print(f"BLOCKED_HUMAN: 0 of {len(rows)} questions written by Kush")
        return 2
    from culinarystate.decision.pipeline import load_lexicon, parse_query
    from culinarystate.ledgers.store import LedgerStore
    st = LedgerStore()
    lex, _ = load_lexicon(st)
    ids = {e["id"] for e in st.all_latest("EVD") if e["status"] == "ACTIVE"}
    errs = check(rows, lambda q: parse_query(q, lex), ids)
    print("\n".join(errs) if errs else "OK: 80 questions pass the checks")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
