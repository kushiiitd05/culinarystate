#!/usr/bin/env python3
"""Baseline ladder (SSOT §245.12) with C16 generator ablation.

  ssh -f -N -L 11435:localhost:11434 vinayak-server     # VPN on; Ollama on the A100
  /opt/anaconda3/bin/python tools/run_ladder.py --model qwen2.5:7b-instruct --tag v2
Rungs: B0 LLM-only | B2 hybrid-RAG rows prompt | B5 packet+decision rows prompt (v1) | B5F per-route fact prompt
(LLM rephrases verbaliser facts) | B5F+E B5F after post-hoc enforcement | B5T deterministic template (no LLM).
Scores with the C17 checker (UCR), counts "[1]"-style non-evidence citations and decision-mode violations (numbers
when the cap forbids them; ASK without a question). DEV smoke on AI-authored questions — the locked benchmark (D-008,
humans) is the evaluation. Decisions + packet row ids are stored for replay. Writes reports/del5/ladder_<tag>.md/jsonl.
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from ask import DEMO  # noqa: E402
from culinarystate.decision.diagnosis import TroubleshootIndex  # noqa: E402
from culinarystate.decision.feasibility import load_requirements  # noqa: E402
from culinarystate.decision.ood import SupportIndex  # noqa: E402
from culinarystate.decision.pipeline import answer, load_lexicon  # noqa: E402
from culinarystate.generation.claims import check_claims  # noqa: E402
from culinarystate.generation.enforce import NUM_BRACKET, _union, enforce, number_cap  # noqa: E402
from culinarystate.generation.llm import generate  # noqa: E402
from culinarystate.generation.prompts import b0_prompt, b2_prompt, b5_prompt, b5f_prompt  # noqa: E402
from culinarystate.generation.verbalize import verbalize  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.retrieval.compatibility import Query  # noqa: E402
from culinarystate.retrieval.retriever import EvidencePacket, EvidenceRetriever  # noqa: E402

DEV = ["How much vitamin C does boiled cabbage keep?", "How much folate does steamed broccoli keep?",
       "How much beta-carotene does boiled carrot keep?", "Does frying potatoes reduce vitamin C?",
       "Is roasting or boiling better for keeping vitamin C in potatoes?", "Why did my custard curdle?",
       "My gravy is too thick, how can I fix it?", "How much riboflavin does baked salmon keep?",
       "What happens to iron in spinach when boiled?", "Tell me a joke about pasta.",
       "How much vitamin C does boiled unobtainium keep?", "The fudge turned grainy; how can I recover?"]
RUNGS = ("B0", "B2", "B5", "B5F", "B5F+E", "B5T")


def score(text: str, pk: EvidencePacket, d: dict) -> dict:
    c = check_claims(text, pk)
    violation = (number_cap(d) and c["numeric_claims"] > 0) or (d["mode"] == "ASK" and "?" not in text)
    reasons = [x["reason"] for x in c["claims"] if not x["supported"]]
    return {"numeric_claims": c["numeric_claims"], "unsupported": c["unsupported"],
            "uncited": reasons.count("UNCITED"), "value_mismatch": reasons.count("VALUE_NOT_IN_CITED_EVIDENCE"),
            "fabricated": c["fabricated_citations"], "non_evidence_cites": len(NUM_BRACKET.findall(text)),
            "mode_violation": bool(violation)}


def run_one(q, ctx, model, stored: dict | None = None) -> list[dict]:
    """stored: {rung: answer} from an earlier run -> rescore with the current checker/enforcer, no LLM calls."""
    lex, R, req, fam, sup, ts = ctx
    r = answer(q, lex, R, req, fam, support_index=sup, troubleshoot=ts)
    d, packets = r["decision"], r["packets"]
    main_pk = next(iter(packets.values()), EvidencePacket(q, Query(), "UNSUPPORTED"))
    union = _union(packets) if packets else main_pk
    hyb = EvidencePacket(q, Query(), "RETRIEVED", [], R.search(q, Query(), k=5))
    disallowed = sorted({x for p in packets.values() for x in p.disallowed_claims})
    base = {"question": q, "mode": d["mode"], "route": d.get("route"), "reason": d.get("reason"),
            "packet_rows": {k: [h.evd_id for h in p.direct + p.near] for k, p in packets.items()}}
    rows, timings = [], {}
    for rung, prompt, pk in (("B0", b0_prompt(q), union), ("B2", b2_prompt(q, hyb), hyb),
                             ("B5", b5_prompt(q, main_pk, d, disallowed), union),
                             ("B5F", b5f_prompt(q, d, packets), union)):
        t0 = time.time()
        text = stored[rung]["answer"] if stored else generate(prompt, model)
        timings[rung] = stored[rung]["latency_s"] if stored else round(time.time() - t0, 2)
        rows.append({**base, "rung": rung, "answer": text, "latency_s": timings[rung], **score(text, pk, d)})
    e = enforce(rows[-1]["answer"], d, packets)
    rows.append({**base, "rung": "B5F+E", "answer": e["text"], "latency_s": timings["B5F"], "fallback": e["fallback"],
                 "removed": e["removed"], **score(e["text"], union, d)})
    t = verbalize(q, d, packets)
    rows.append({**base, "rung": "B5T", "answer": t, "latency_s": 0.0, **score(t, union, d)})
    return rows


def report(rows: list[dict], model: str, tag: str, n_q: int) -> list[str]:
    lines = [f"# Ladder {tag} ({model}; {n_q} dev questions, AI-authored, silver)", "",
             "| rung | numeric claims | unsupported (uncited / wrong value) | UCR | fabricated cites | `[n]` cites | "
             "mode violations | mean latency s |", "|---|---|---|---|---|---|---|---|"]
    for rung in RUNGS:
        rs = [x for x in rows if x["rung"] == rung]
        n, u = sum(x["numeric_claims"] for x in rs), sum(x["unsupported"] for x in rs)
        uc, vm = sum(x["uncited"] for x in rs), sum(x["value_mismatch"] for x in rs)
        lines.append(f"| {rung} | {n} | {u} ({uc} / {vm}) | {round(u / n, 3) if n else '—'} | {sum(len(x['fabricated']) for x in rs)} | "
                     f"{sum(x['non_evidence_cites'] for x in rs)} | {sum(x['mode_violation'] for x in rs)} | "
                     f"{round(sum(x['latency_s'] for x in rs) / max(len(rs), 1), 2)} |")
    e = [x for x in rows if x["rung"] == "B5F+E"]
    lines += ["", f"B5F+E: fallback to template {sum(x['fallback'] for x in e)}/{len(e)}; sentences removed "
              f"{sum(len(x['removed']) for x in e)} (reasons: "
              f"{sorted({r['reason'] for x in e for r in x['removed']})})."]
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    ap.add_argument("--tag", default="v2")
    ap.add_argument("--rescore", action="store_true", help="re-score reports/del5/ladder_<tag>.jsonl answers, no LLM")
    a = ap.parse_args()
    st = LedgerStore()
    lex, fam = load_lexicon(st)
    cond = {c["id"]: c for c in st.all_latest("COND")}
    evd = st.all_latest("EVD")
    ctx = (lex, EvidenceRetriever(evd, cond, fam), load_requirements(st), fam, SupportIndex(evd),
           TroubleshootIndex.from_registry(ROOT))
    out, rows, qs = ROOT / "reports" / "del5", [], DEMO + DEV
    out.mkdir(parents=True, exist_ok=True)
    stored = {}
    if a.rescore:
        for x in map(json.loads, (out / f"ladder_{a.tag}.jsonl").read_text().splitlines()):
            stored.setdefault(x["question"], {})[x["rung"]] = x
        qs = list(stored)
    for q in qs:
        rows += run_one(q, ctx, a.model, stored.get(q))
        print(rows[-1]["mode"], q[:60], flush=True)
    (out / f"ladder_{a.tag}.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n")
    lines = report(rows, a.model, a.tag, len(qs))
    (out / f"ladder_{a.tag}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
