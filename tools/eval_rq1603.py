#!/usr/bin/env python3
"""EXP-000006 (RQ16-03 silver pilot) evaluation — pre-registered in experiments/EXP-000006/card.md.

  /opt/anaconda3/bin/python tools/eval_rq1603.py
Systems: S0 BM25 · S1 generic cross-encoder (bge-reranker-large; base reported too) · S2 structured compatibility
(retriever compat score, hard-mismatch penalty, runtime R4 relations) with ORACLE slots · S2p the same with slots
PREDICTED by the runtime parser (decision.pipeline.parse_query; §257B predicted-upstream) · S3 logistic regression on [S2 axis one-hots,
S1 logit], out-of-fold under food-cold and process-cold GroupKFold (5 folds, seed 7).
Metric: within-query pairwise AUROC (positive vs each negative; ties 0.5), overall and per negative type, Recall@1;
CI = grouped bootstrap over queries; paired differences vs S1. Writes reports/del4/rq1603_pilot_v1.md/json.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.decision.pipeline import load_lexicon, parse_query  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.retrieval.compatibility import Query, compatibility  # noqa: E402
from culinarystate.retrieval.retriever import EvidenceRetriever  # noqa: E402
from culinarystate.scoring.metrics import grouped_bootstrap  # noqa: E402

D = ROOT / "data" / "interim" / "rq1603"
TYPES = ("WRONG_PROCESS", "WRONG_TARGET", "RELATED_FOOD", "EASY")
AXES = ("matrix", "process", "target", "state", "time", "temperature", "medium")
VALS = ("MATCH", "NEAR", "UNKNOWN", "MISMATCH")


def per_query(qs: list[dict], score: dict) -> list[dict]:
    """score: {(qid, evd_id): float} -> per query {type: win rate of positive vs that negative, 'r1': 0/1}."""
    out = []
    for q in qs:
        pos = next(c for c in q["candidates"] if c["type"] == "POSITIVE")
        sp = score[(q["qid"], pos["evd_id"])]
        r = {}
        for c in q["candidates"]:
            if c["type"] != "POSITIVE":
                sn = score[(q["qid"], c["evd_id"])]
                r[c["type"]] = 1.0 if sp > sn else 0.5 if sp == sn else 0.0
        r["r1"] = float(all(v == 1.0 for v in r.values()))
        out.append(r)
    return out


def ci_of(vals: list[float]) -> dict:
    return grouped_bootstrap({i: [v] for i, v in enumerate(vals)}, lambda xs: sum(xs) / len(xs), n_boot=1000)


def summary(pq: list[dict]) -> dict:
    out = {"ALL": ci_of([np.mean([v for k, v in r.items() if k != "r1"]) for r in pq if len(r) > 1]),
           "HARD": ci_of([np.mean([r[t] for t in ("WRONG_PROCESS", "RELATED_FOOD") if t in r]) for r in pq
                          if "WRONG_PROCESS" in r or "RELATED_FOOD" in r]),
           "R@1": ci_of([r["r1"] for r in pq])}
    for t in TYPES:
        out[t] = ci_of([r[t] for r in pq if t in r])
    return out


def paired(a: list[dict], b: list[dict], key: str) -> dict:
    def val(r):
        if key == "HARD":
            ks = [t for t in ("WRONG_PROCESS", "RELATED_FOOD") if t in r]
            return np.mean([r[t] for t in ks]) if ks else None
        return r.get(key)
    d = [val(x) - val(y) for x, y in zip(a, b) if val(x) is not None]
    return ci_of(d)


def main() -> None:
    qs = [json.loads(line) for line in (D / "pairs.jsonl").open()]
    st = LedgerStore()
    cond = {c["id"]: c for c in st.all_latest("COND")}
    family = {p["id"]: p["family"] for p in st.all_latest("PROC")}
    R = EvidenceRetriever(st.all_latest("EVD"), cond, family)
    idx = {e["id"]: i for i, e in enumerate(R.evd)}
    S = {"S0 BM25": {}, "S2 structured": {}, "S2p structured (predicted slots)": {}}
    lex, _ = load_lexicon(st)
    slot_ok = defaultdict(int)
    feats, ys, groups_food, groups_proc, keys = [], [], [], [], []
    for name in ("BAAI__bge-reranker-large", "BAAI__bge-reranker-base"):
        ce = json.loads((D / f"ce_{name}.json").read_text())
        S[f"S1 CE {name.split('__')[1]}"] = {(q, e): v for q, d in ce.items() for e, v in d.items()}
    ce_large = S["S1 CE bge-reranker-large"]
    for q in qs:
        bm = R.bm25.scores(q["question"])
        rel = tuple((i, k) for i, k in q["relations"] if k != "SIBLING")
        Q = Query(ingredient_id=q["ingredient_id"], ingredient_name=q["ingredient_name"],
                  ingredient_parents=frozenset(q["parents"]), process_id=q["process_id"],
                  process_family=family.get(q["process_id"]), target=q["target"], ingredient_relations=rel)
        sl = parse_query(q["question"], lex)
        pid = sl.processes[0][1] if sl.processes else None
        slot_ok["ingredient"] += sl.ingredient_id == q["ingredient_id"]
        slot_ok["process"] += pid == q["process_id"]
        slot_ok["target"] += (sl.target or "") == q["target"]
        Qp = Query(ingredient_id=sl.ingredient_id, ingredient_name=sl.ingredient_name, ingredient_parents=frozenset(sl.parents),
                   process_id=pid, process_family=family.get(pid), target=sl.target,
                   ingredient_relations=lex.relations.get(sl.ingredient_id, ()))
        for c in q["candidates"]:
            e = R.evd[idx[c["evd_id"]]]
            cnd = cond.get(e["process"].get("condition_id") or "")
            comp = compatibility(Q, e, cnd, family)
            cp = compatibility(Qp, e, cnd, family)
            S["S2p structured (predicted slots)"][(q["qid"], c["evd_id"])] = cp["score"] * (0.3 if cp["hard_mismatch"] else 1.0)
            k = (q["qid"], c["evd_id"])
            S["S0 BM25"][k] = bm.get(idx[c["evd_id"]], 0.0)
            S["S2 structured"][k] = comp["score"] * (0.3 if comp["hard_mismatch"] else 1.0)
            feats.append([float(comp["vector"][a] == v) for a in AXES for v in VALS] + [ce_large[k]])
            ys.append(int(c["type"] == "POSITIVE"))
            groups_food.append(q["ingredient_id"])
            groups_proc.append(q["process_id"])
            keys.append(k)
    X, y = np.array(feats), np.array(ys)
    for split, groups in (("food-cold", groups_food), ("process-cold", groups_proc)):
        oof = np.zeros(len(y))
        for tr, te in GroupKFold(n_splits=5).split(X, y, groups):
            m = LogisticRegression(max_iter=2000, C=1.0).fit(X[tr], y[tr])
            oof[te] = m.decision_function(X[te])
        S[f"S3 struct+CE ({split})"] = dict(zip(keys, oof.tolist()))
    pq = {n: per_query(qs, s) for n, s in S.items()}
    summ = {n: summary(v) for n, v in pq.items()}
    lines = ["# RQ16-03 silver pilot v1 (EXP-000006, pre-registered)", "",
             f"{len(qs)} templated queries; within-query pairwise AUROC (positive vs negative), grouped bootstrap 95% CI. "
             "SILVER labels (cell identity) — cannot promote RQ16-03 (needs human-labelled pairs).",
             f"Parser slot accuracy on these questions: ingredient {slot_ok['ingredient'] / len(qs):.3f}, "
             f"process {slot_ok['process'] / len(qs):.3f}, target {slot_ok['target'] / len(qs):.3f}.", "",
             "| system | ALL | HARD (wrong process ∪ related food) | WRONG_PROCESS | WRONG_TARGET | RELATED_FOOD | EASY | Recall@1 |",
             "|---|---|---|---|---|---|---|---|"]
    f = lambda c: f"{c['estimate']:.3f} [{c['low']:.3f}, {c['high']:.3f}]"  # noqa: E731
    for n, s in summ.items():
        lines.append(f"| {n} | {f(s['ALL'])} | {f(s['HARD'])} | " + " | ".join(f(s[t]) for t in TYPES) + f" | {f(s['R@1'])} |")
    base = pq["S1 CE bge-reranker-large"]
    lines += ["", "Paired differences vs S1 (bge-reranker-large):", "", "| system | Δ HARD | Δ WRONG_PROCESS | Δ RELATED_FOOD | Δ Recall@1 |",
              "|---|---|---|---|---|"]
    for n in S:
        if n.startswith(("S2", "S3")):
            lines.append(f"| {n} | " + " | ".join(f"{(c := paired(pq[n], base, k))['estimate']:+.3f} "
                                                  f"[{c['low']:+.3f}, {c['high']:+.3f}]"
                                                  for k in ("HARD", "WRONG_PROCESS", "RELATED_FOOD", "r1")) + " |")
    (ROOT / "reports" / "del4" / "rq1603_pilot_v1.json").write_text(json.dumps(summ, indent=1))
    (ROOT / "reports" / "del4" / "rq1603_pilot_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
