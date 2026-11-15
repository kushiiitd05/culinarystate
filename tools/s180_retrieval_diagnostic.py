"""Text vs process vs composition retrieval diagnostic (freeze step 9).

Three views retrieve neighbours for the same query states, over the same corpus:

  * **TEXT**        BM25 over the step's own action text.
  * **PROCESS**     the process signature: proc id, then family, then heat/not-heat.
  * **COMPOSITION** block-weighted cosine over ``STATE_VECTOR_V0``, on dimensions known in both
                    (``state_vector.similarity``). Masked, named, nothing learned.

The question is narrow and answerable: **do the three views retrieve the same neighbours?** If they
agree everywhere, a state-aware retriever buys nothing over BM25. If they diverge, the state is
carrying information the text does not.

**DIAGNOSTIC_ONLY.** There is no relevance gold for this corpus, so overlap is not precision and no
view can be called better. The output is a disagreement measurement, not a ranking.

Source is Wikibooks (CC-BY, public). The written artifact carries ids, counts and overlaps - never
step text.

Usage:
  python tools/s180_retrieval_diagnostic.py --recipes 150 --queries 40 --k 10 \
      --out reports/s180/retrieval_diagnostic_2026-11-15.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

RECIPES = ROOT / "data/interim/wikibooks/recipes.jsonl"
SEED = "s180-retrieval-diagnostic-2026-11-15"
VIEWS = ("TEXT", "PROCESS", "COMPOSITION")
LABELS = ("DIAGNOSTIC_ONLY", "NO_RELEVANCE_GOLD_SO_OVERLAP_IS_NOT_PRECISION",
          "WIKIBOOKS_CC_BY_PUBLIC_TEXT_ONLY", "STATE_VECTOR_V0_WEIGHTS_FIXED_NOT_VALIDATED")


def rank_key(text: str) -> str:
    return hashlib.sha256(f"{SEED}‖{text}".encode()).hexdigest()


def steps_text(record: dict) -> str:
    steps = record.get("steps") or []
    if isinstance(steps, str):
        steps = json.loads(steps.replace("'", '"')) if steps.startswith("[") else []
    return "\n".join(s.get("text", "") for s in steps if isinstance(s, dict) and s.get("text"))


def build_corpus(limit: int) -> list[dict]:
    """One entry per (food, step): its text, its process signature and its state vector."""
    from culinarystate.composition.state_full import StateBuilder
    from culinarystate.composition import state_vector as SV

    builder = StateBuilder()
    with RECIPES.open(encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]
    records.sort(key=lambda r: rank_key(str(r["pageid"])))

    corpus: list[dict] = []
    for record in records[:limit]:
        raw = steps_text(record)
        if not raw.strip():
            continue
        try:
            states = builder.build(raw)
        except Exception:
            continue
        for state in states:
            g, q, c = state["G"], state["Q"], state["C"]
            proc = (g.get("process") or {}).get("v") or ""
            family = (g.get("family") or {}).get("v") or ""
            try:
                vector = SV.encode(
                    family=family or None,
                    step_position=state["step"] / max(1, len(states)),
                    n_inputs=len((g.get("lot_members") or {}).get("v") or []),
                    n_members=len((g.get("lot_members") or {}).get("v") or []),
                    history=set((g.get("history") or {}).get("v") or []),
                    ctx=c,
                    temperature_c=(q.get("temperature_C") or {}).get("v"),
                    duration_min=(q.get("duration_min") or {}).get("v"),
                )
            except Exception:
                continue
            corpus.append({
                "id": f"{record['pageid']}:{state['step']}:{state['food_id']}",
                "pageid": str(record["pageid"]),
                "text": state["action"],
                "proc": proc,
                "family": family,
                "is_heat": bool((g.get("is_heat_step") or {}).get("v")),
                "vector": vector,
            })
    return corpus


def top_text(bm25, query_text: str, k: int, skip: int) -> list[int]:
    hits = bm25.top(query_text, k + 6)
    return [i for i, _ in hits if i != skip][:k]


def top_process(corpus: list[dict], qi: int, k: int) -> list[int]:
    """Exact proc id first, then same family, then same heat/not-heat. Ties by seeded rank."""
    q = corpus[qi]

    def tier(other: dict) -> int:
        if q["proc"] and other["proc"] == q["proc"]:
            return 0
        if q["family"] and other["family"] == q["family"]:
            return 1
        return 2 if other["is_heat"] == q["is_heat"] else 3

    order = sorted((i for i in range(len(corpus)) if i != qi),
                   key=lambda i: (tier(corpus[i]), rank_key(corpus[i]["id"])))
    return order[:k]


def top_composition(corpus: list[dict], qi: int, k: int) -> list[int]:
    from culinarystate.composition import state_vector as SV
    q = corpus[qi]["vector"]
    scored = [(SV.similarity(q, corpus[i]["vector"]), rank_key(corpus[i]["id"]), i)
              for i in range(len(corpus)) if i != qi]
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [i for _, _, i in scored[:k]]


def chance_jaccard(k: int, n: int) -> float:
    """Expected Jaccard of two independent uniform top-k draws from n items.

    Without this, a low observed overlap is uninterpretable: drawing 10 of 5,166 items twice
    almost never collides, so "low" has to be read against how low chance already is.
    """
    expected_shared = k * k / max(1, n - 1)
    return round(expected_shared / (2 * k - expected_shared), 4)


def jaccard(a: list[int], b: list[int]) -> float:
    sa, sb = set(a), set(b)
    union = sa | sb
    return round(len(sa & sb) / len(union), 4) if union else 0.0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipes", type=int, default=150)
    ap.add_argument("--queries", type=int, default=40)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    from culinarystate.retrieval.bm25 import BM25

    t0 = time.time()
    corpus = build_corpus(args.recipes)
    if len(corpus) < args.k + 2:
        raise SystemExit(f"corpus too small ({len(corpus)}) for k={args.k}")
    bm25 = BM25([c["text"] for c in corpus])

    queries = sorted(range(len(corpus)), key=lambda i: rank_key(corpus[i]["id"]))[: args.queries]
    overlaps = {f"{a}|{b}": [] for a, b in combinations(VIEWS, 2)}
    all_three, none_shared, rows = 0, 0, []

    for qi in queries:
        hits = {"TEXT": top_text(bm25, corpus[qi]["text"], args.k, qi),
                "PROCESS": top_process(corpus, qi, args.k),
                "COMPOSITION": top_composition(corpus, qi, args.k)}
        for a, b in combinations(VIEWS, 2):
            overlaps[f"{a}|{b}"].append(jaccard(hits[a], hits[b]))
        shared = set(hits["TEXT"]) & set(hits["PROCESS"]) & set(hits["COMPOSITION"])
        all_three += len(shared)
        if not shared:
            none_shared += 1
        rows.append({"query_id": corpus[qi]["id"], "family": corpus[qi]["family"],
                     "is_heat": corpus[qi]["is_heat"],
                     "shared_by_all_three": len(shared),
                     "overlap": {f"{a}|{b}": jaccard(hits[a], hits[b])
                                 for a, b in combinations(VIEWS, 2)},
                     "top1": {v: corpus[hits[v][0]]["id"] if hits[v] else None for v in VIEWS}})

    mean = {pair: round(sum(v) / len(v), 4) for pair, v in overlaps.items()}
    chance = chance_jaccard(args.k, len(corpus))
    lift = {pair: (round(m / chance, 1) if chance else None) for pair, m in mean.items()}
    result = {
        "labels": list(LABELS),
        "seed": SEED,
        "k": args.k,
        "recipes_scanned": args.recipes,
        "corpus_states": len(corpus),
        "queries": len(queries),
        "mean_jaccard_overlap_at_k": mean,
        "chance_jaccard_at_k": chance,
        "overlap_lift_over_chance": lift,
        "queries_with_no_shared_hit_in_all_three": none_shared,
        "mean_hits_shared_by_all_three": round(all_three / len(queries), 3),
        "top1_agreement": {
            f"{a}|{b}": round(sum(1 for r in rows if r["top1"][a] == r["top1"][b]) / len(rows), 4)
            for a, b in combinations(VIEWS, 2)},
        "family_distribution": dict(Counter(c["family"] for c in corpus).most_common(12)),
        "build_seconds": round(time.time() - t0, 1),
        "per_query": rows,
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True), encoding="utf-8")
    print(f"corpus {len(corpus)} states from {args.recipes} recipes | {len(queries)} queries | k={args.k}")
    print(f"mean Jaccard@k: {mean}")
    print(f"chance Jaccard@k: {chance} | lift over chance: {lift}")
    print(f"top-1 agreement: {result['top1_agreement']}")
    print(f"queries with nothing shared by all three: {none_shared}/{len(queries)}")
    print(f"-> {args.out}  ({result['build_seconds']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
