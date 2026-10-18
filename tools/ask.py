#!/usr/bin/env python3
"""Ask CulinaryState a question (DEL-5 rule baseline): slots -> evidence packets -> feasibility -> decision.

  /opt/anaconda3/bin/python tools/ask.py "How much vitamin C does boiled broccoli keep?"
  /opt/anaconda3/bin/python tools/ask.py --demo          # the fixed demo questions below
Prints the decision, the evidence class per option and the cited EVD ids. No free-text generation here:
the output is the structured decision a generator would be constrained by.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.decision.constraints import load_constraint_lexicons, parse_constraints  # noqa: E402
from culinarystate.decision.feasibility import load_requirements  # noqa: E402
from culinarystate.decision.ood import SupportIndex  # noqa: E402
from culinarystate.decision.pipeline import answer, load_lexicon  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.retrieval.retriever import EvidenceRetriever  # noqa: E402

DEMO = ["How much vitamin C does boiled broccoli keep?",
        "What happens to folate in spinach if I steam instead of boiling?",
        "How should I cook spinach to keep vitamin C?",
        "Will microwaving produce the same texture?",
        "What is the next instruction?",
        "Why did my sauce split?",
        "How much thiamin does fried okra keep?",
        "I accidentally boiled the carrots too long; how can I recover?"]


def show(q: str, r: dict) -> dict:
    d = r["decision"]
    opts = {k: {"class": p.evidence_class, "direct": [h.evd_id for h in p.direct[:3]],
                "near": [h.evd_id for h in p.near[:3]], "feasibility": r["feasibility"][k]["decision"],
                "precision": d.get("per_option", {}).get(k, {}).get("precision"),
                "support": (r.get("support") or {}).get(k)}
            for k, p in r["packets"].items()}
    s = r["slots"]
    return {"question": q, "mode": d["mode"], "reason": d.get("reason"), "precision": d.get("precision"),
            "gate": d["gate"]["reason"], "intent": d["intent"],
            "slots": {"ingredient": s.ingredient_id, "processes": [n for n, _ in s.processes], "target": s.target,
                      "candidates": list(s.candidates)}, "ask_for": d.get("ask_for"), "options": opts}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--constraints", default="", help='free text, e.g. "no oven, gluten-free, 20 minutes"')
    a = ap.parse_args()
    st = LedgerStore()
    lex, family = load_lexicon(st)
    cond = {c["id"]: c for c in st.all_latest("COND")}
    evd = st.all_latest("EVD")
    retriever = EvidenceRetriever(evd, cond, family)
    sup = SupportIndex(evd)
    req = load_requirements(st)
    qs = DEMO if a.demo else [a.question]
    cons, info = parse_constraints(a.constraints, *load_constraint_lexicons(st))
    out = [show(q, answer(q, lex, retriever, req, family, constraints=cons, support_index=sup)) for q in qs if q]
    if a.constraints:
        out.append({"constraints": str(cons), "unresolved": info["unresolved"]})
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
