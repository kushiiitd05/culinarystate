#!/usr/bin/env python3
"""Baseline ladder smoke run (SSOT §245.12): B0 LLM-only vs B2 hybrid-RAG prompt vs B5 packet+decision prompt.

  ssh -f -N -L 11435:localhost:11434 vinayak-server     # VPN on; Ollama on the A100
  /opt/anaconda3/bin/python tools/run_ladder.py --model qwen2.5:7b-instruct
Scores every answer with the C17 claim checker (numeric claims cited and matching packet rows -> UCR) and records
abstain/ask behaviour. DEV smoke on the demo questions only; the locked benchmark (D-008, humans) is the evaluation.
Writes reports/del5/ladder_smoke_v1.md/jsonl.
"""
import argparse
import json
import sys
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
from culinarystate.generation.llm import generate  # noqa: E402
from culinarystate.generation.prompts import b0_prompt, b2_prompt, b5_prompt  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.retrieval.compatibility import Query  # noqa: E402
from culinarystate.retrieval.retriever import EvidencePacket, EvidenceRetriever  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    a = ap.parse_args()
    st = LedgerStore()
    lex, fam = load_lexicon(st)
    cond = {c["id"]: c for c in st.all_latest("COND")}
    evd = st.all_latest("EVD")
    R, req, sup = EvidenceRetriever(evd, cond, fam), load_requirements(st), SupportIndex(evd)
    ts = TroubleshootIndex.from_registry(ROOT)
    out, rows = ROOT / "reports" / "del5", []
    out.mkdir(parents=True, exist_ok=True)
    for q in DEMO:
        r = answer(q, lex, R, req, fam, support_index=sup, troubleshoot=ts)
        d = r["decision"]
        main_pk = next(iter(r["packets"].values()), EvidencePacket(q, Query(), "UNSUPPORTED"))
        hyb = EvidencePacket(q, Query(), "RETRIEVED", [], R.search(q, Query(), k=5))
        disallowed = sorted({x for p in r["packets"].values() for x in p.disallowed_claims})
        for rung, prompt, pk in (("B0", b0_prompt(q), main_pk), ("B2", b2_prompt(q, hyb), hyb),
                                 ("B5", b5_prompt(q, main_pk, d, disallowed), main_pk)):
            text = generate(prompt, a.model)
            c = check_claims(text, pk)
            rows.append({"question": q, "rung": rung, "mode": d["mode"], "answer": text, "numeric_claims": c["numeric_claims"],
                         "unsupported": c["unsupported"], "fabricated": c["fabricated_citations"]})
            print(rung, d["mode"], c["numeric_claims"], c["unsupported"], q[:50])
    (out / "ladder_smoke_v1.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n")
    lines = [f"# Ladder smoke v1 ({a.model}; dev demo questions, silver)", "",
             "| rung | numeric claims | unsupported | UCR | fabricated citations |", "|---|---|---|---|---|"]
    for rung in ("B0", "B2", "B5"):
        rs = [x for x in rows if x["rung"] == rung]
        n, u = sum(x["numeric_claims"] for x in rs), sum(x["unsupported"] for x in rs)
        lines.append(f"| {rung} | {n} | {u} | {round(u / n, 3) if n else '—'} | {sum(len(x['fabricated']) for x in rs)} |")
    lines += ["", "Demo questions only (n=8); not a benchmark. B5 numbers must be cited and match packet rows."]
    (out / "ladder_smoke_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
