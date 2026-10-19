#!/usr/bin/env python3
"""Ask CulinaryState a question (DEL-5 rule baseline): slots -> evidence packets -> feasibility -> decision.

  /opt/anaconda3/bin/python tools/ask.py "How much vitamin C does boiled broccoli keep?"
  /opt/anaconda3/bin/python tools/ask.py --demo          # the fixed demo questions below
Prints the answer from the promoted C16 template verbaliser (reports/del5/generator_c16_v1.md), the decision,
the evidence class per option and the cited EVD ids.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.decision.constraints import load_constraint_lexicons, parse_constraints  # noqa: E402
from culinarystate.decision.diagnosis import TroubleshootIndex  # noqa: E402
from culinarystate.decision.feasibility import load_requirements  # noqa: E402
from culinarystate.decision.ood import SupportIndex  # noqa: E402
from culinarystate.decision.pipeline import answer, load_lexicon  # noqa: E402
from culinarystate.decision.session_state import SessionState  # noqa: E402
from culinarystate.generation.verbalize import verbalize  # noqa: E402
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
    pv, cs = r.get("pareto"), r.get("candidates")
    tradeoff = None if pv is None else {
        "front": [{"option": o.name, "retention": o.retention, "minutes": o.time_minutes, "feasibility": o.feasibility}
                  for o in pv.front],
        "dominated": [o.name for o in pv.dominated], "rejected": [o.name for o in pv.rejected]}
    alternatives = None if cs is None else [{"type": c.type, "name": c.name, "confidence": c.confidence, "why": c.reason}
                                            for c in cs.candidates]
    return {"question": q, "state_trace": r.get("state_trace"), "tradeoff": tradeoff, "alternatives": alternatives, "answer": verbalize(q, d, r["packets"]), "mode": d["mode"], "reason": d.get("reason"), "precision": d.get("precision"),
            "gate": d["gate"]["reason"], "intent": d["intent"],
            "diagnosis": {k: d["diagnosis"][k] for k in ("failure", "causes", "recovery", "next_observations")}
            if d.get("diagnosis") else None, "recovery_options": d.get("recovery_options"),
            "slots": {"ingredient": s.ingredient_id, "processes": [n for n, _ in s.processes], "target": s.target,
                      "candidates": list(s.candidates)}, "ask_for": d.get("ask_for"), "ask_options": d.get("ask_options"), "options": opts}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--constraints", default="", help='free text, e.g. "no oven, gluten-free, 20 minutes"')
    ap.add_argument("--session", default="", help="path to a session JSON file (annotation/sessions/SES-*.json)")
    ap.add_argument("--use-state", action="store_true", help="rung B4: fill empty slots from the reconstructed session state")
    ap.add_argument("--turn", type=int, default=None, help="replay only up to this turn number (inclusive)")
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
    ts = TroubleshootIndex.from_registry(ROOT)
    sess = None
    if a.session:
        sd = json.loads(Path(a.session).read_text())
        if a.turn is not None:
            sd = {**sd, "turns": [t for t in sd.get("turns", []) if t.get("turn", 0) <= a.turn]}
        sess = SessionState.from_session(sd)
    out = [show(q, answer(q, lex, retriever, req, family, constraints=cons, support_index=sup,
                          troubleshoot=ts, session=sess, use_state=a.use_state))
           for q in qs if q]
    if a.constraints:
        out.append({"constraints": str(cons), "unresolved": info["unresolved"],
                    "unresolved_exclusions": info["unresolved_exclusions"]})
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
