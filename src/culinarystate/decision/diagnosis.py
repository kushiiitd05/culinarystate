"""Diagnosis proposer + verifier and a separate recovery index (SSOT §243.6–243.7; RQ16-18, RQ16-19).

Proposer: symptom text -> failure key (troubleshoot vocabulary) -> cited CAUSE candidates ranked by independent
source support. Verifier: a cause that names a process is CONSISTENT if that process is in the session history,
INCONSISTENT if it is not; causes naming no process are UNVERIFIABLE (listed as useful next observations).
Recovery and prevention come from their own relations — never by inverting a cause. Language stays QUALIFIED:
these are corpus statements, not controlled causal evidence. Recoverability is UNKNOWN until evidence says otherwise.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

from culinarystate.kg.troubleshoot import FAIL, _key
from culinarystate.process.vocab import BY_CANON
from culinarystate.state_graph.rule_compiler import step_processes

VERSION = "diagnosis@0.1"
SYMPTOM = re.compile(FAIL, re.I)
ADJECTIVE = {"heavy": "HEAVY", "dense": "HEAVY", "tough": "TOUGH", "chewy": "TOUGH", "rubbery": "TOUGH",
             "soggy": "SOGGY", "grainy": "GRAINY", "gritty": "GRAINY", "lumpy": "LUMPY", "burnt": "BURN",
             "burned": "BURN", "scorched": "BURN", "runny": "TOO_THIN", "watery": "TOO_THIN", "greasy": "OILY",
             "oily": "OILY", "salty": "TOO_SALTY", "split": "SPLIT", "curdled": "CURDLE"}
ADJ_RE = re.compile(r"\b(" + "|".join(ADJECTIVE) + r")\b", re.I)
GENERIC = {"COMBINATION", "TRANSFER", "SERVING", "RESERVATION"}      # verbs that cannot verify a cause
NEG = re.compile(r"\b(?:not|never|without|insufficient(?:ly)?|too little)\s+(?:\w+\s+)?$", re.I)


def failure_of(text: str) -> str | None:
    """Symptom text -> failure key: statement vocabulary first, then plain symptom adjectives ("my cake is heavy")."""
    m = SYMPTOM.search(text or "")
    if m:
        return _key(m["fail"])
    a = ADJ_RE.search(text or "")
    return ADJECTIVE[a.group(1).lower()] if a else None


class TroubleshootIndex:
    def __init__(self, rows: list[dict]):
        self.by = defaultdict(list)
        for r in rows:
            self.by[(r["relation"], r["failure"])].append(r)
        for v in self.by.values():
            v.sort(key=lambda r: (-int(r.get("support_sources") or 1), str(r.get("key"))))

    @classmethod
    def from_registry(cls, root: Path) -> TroubleshootIndex:
        df = pd.read_csv(root / "registry" / "kg" / "troubleshooting_candidates_v1.csv")
        df["text"] = df["text"].fillna(df["key"])                  # Wikibooks rows carry the normalised key only
        return cls(df.to_dict("records"))

    def get(self, relation: str, failure: str, k: int = 5, min_support: int = 1) -> list[dict]:
        return [r for r in self.by.get((relation, failure), []) if int(r.get("support_sources") or 1) >= min_support][:k]


def _verify(cause: str, history: set[str]) -> str:
    """Named (non-generic) process in the cause vs session history; a negated process flips the test.
    No history (no session) means nothing can be checked."""
    if not history:
        return "UNVERIFIABLE"
    verdicts = []
    for pos, p in step_processes(cause):
        if p not in BY_CANON or BY_CANON[p].family in GENERIC:
            continue
        present = p in history
        negated = bool(NEG.search(cause[:pos]))
        verdicts.append(present != negated)
    if not verdicts:
        return "UNVERIFIABLE"
    return "CONSISTENT" if all(verdicts) else "INCONSISTENT"


def diagnose(symptom: str, history: list[str], idx: TroubleshootIndex, k: int = 5, min_support: int = 2) -> dict:
    """min_support: independent sources a candidate needs to be shown (single-source mined statements are noisy)."""
    f = failure_of(symptom)
    out = {"version": VERSION, "symptom": symptom, "failure": f, "causal_language": "QUALIFIED",
           "recoverability": "UNKNOWN", "causes": [], "recovery": [], "prevention": [], "next_observations": [],
           "min_support": min_support}
    if f is None:
        return out
    hist = set(history)
    for r in idx.get("CAUSE", f, k, min_support):
        out["causes"].append({"cause": r["text"], "support_sources": int(r.get("support_sources") or 1),
                              "verdict": _verify(r["text"], hist)})
    rank = {"CONSISTENT": 0, "UNVERIFIABLE": 1, "INCONSISTENT": 2}
    out["causes"].sort(key=lambda c: (rank[c["verdict"]], -c["support_sources"]))
    out["next_observations"] = [c["cause"] for c in out["causes"] if c["verdict"] == "UNVERIFIABLE"][:3]
    out["recovery"] = [{"action": r["text"], "support_sources": int(r.get("support_sources") or 1)}
                       for r in idx.get("RECOVERY", f, k, min_support)]
    out["prevention"] = [{"action": r["text"], "support_sources": int(r.get("support_sources") or 1)}
                         for r in idx.get("PREVENTION", f, k, min_support)]
    return out
