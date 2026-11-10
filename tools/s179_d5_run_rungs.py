#!/usr/bin/env python3
"""D5 rung runner (T8-C15-R1, S179): answers of every pre-registered rung on the FROZEN D5 benchmark.

Refuses unless ``frozen_guard.check_real_inputs`` passes on the freeze record (D-090: signoff AI_DELEGATED_D085).
Writes one run record per (qid, rung) in the ``d5_scoring.RUN_RECORD_FIELDS`` shape for ``tools/s178_d5_score.py``.

- S1 / S2: B0, B1, B2, B4 (``h1_rungs.context`` with ``pre_cut_only=True``; B4 state block ``state_view="ANSWER"`` as
  the locked prereg §2 says). The D5 ``qid`` is not passed to ``context``: its guard refuses the ANSWER view because,
  with ENGINE_DRAFT gold, the block would hand the rung the gold. Here the gold is AI_DRAFTED_GOLD written with the
  engine draft hidden (D-090), so the state block is the treatment H1 tests. The record says so (``config``).
- P1-P3, C, U, X: B0, B2, B5, B7 (= B5F + post-hoc enforcement), B5T, from ``tools/run_ladder.run_one``.
- LLM qwen2.5:7b-instruct, temperature 0, seed 7, num_predict 200 (``generation.llm.generate``; OLLAMA_URL).
  Embedding intfloat/e5-large-v2 revision f169b11e22de13617baa190a028a32f3493550b6, mean pooling, prefixes.

    OLLAMA_URL=http://localhost:11434 python tools/s179_d5_run_rungs.py \\
        --freeze-record registry/freezes/D5-BENCH-2026-11-10.json \\
        --s-context annotation/d5_review/d5_S_context_v1.jsonl --out reports/del5/d5_runs_v1_D085.jsonl

Labels: NON_CITABLE until scored; NO_HUMAN_SIGNOFF_D085.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

MODEL = "qwen2.5:7b-instruct"
E5, E5_REV = "intfloat/e5-large-v2", "f169b11e22de13617baa190a028a32f3493550b6"
S_RUNGS = ("B0", "B1", "B2", "B4")
LADDER_MAP = {"B0": "B0", "B2": "B2", "B5": "B5", "B5F+E": "B7", "B5T": "B5T"}
BENCH = ("benchmark/d5/d5_benchmark_v1_D085_S.csv", "benchmark/d5/d5_benchmark_v1_D085_PC.csv",
         "benchmark/d5/d5_benchmark_v1_D085_UX.csv")
LABELS = ("NON_CITABLE", "NO_HUMAN_SIGNOFF_D085", "MODEL_ASSISTED_GOLD")


def e5_embedder(device: str = "cuda") -> Callable[[list[str]], list[list[float]]]:
    """``embed([query] + passages)``: e5 prefixes, mean pooling, L2-normalised (as tools/embed_texts.py)."""
    import torch
    from transformers import AutoModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(E5, revision=E5_REV)
    model = AutoModel.from_pretrained(E5, revision=E5_REV).to(device).eval()

    @torch.no_grad()
    def embed(texts: list[str]) -> list[list[float]]:
        txt = ["query: " + texts[0]] + ["passage: " + t for t in texts[1:]]
        b = tok(txt, padding=True, truncation=True, max_length=512, return_tensors="pt").to(device)
        h = model(**b).last_hidden_state
        v = (h * b["attention_mask"][..., None]).sum(1) / b["attention_mask"].sum(1, keepdim=True)
        return torch.nn.functional.normalize(v, dim=-1).float().cpu().tolist()
    return embed


def cached_embedder(path: Path) -> Callable[[list[str]], list[list[float]]]:
    """Vectors from ``tools/s179_d5_embed_cache.py`` (same model, revision, pooling); a missing text raises."""
    import s179_d5_embed_cache as EC
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (doc.get("model"), doc.get("revision")) != (E5, E5_REV):
        raise SystemExit("embed cache is not e5-large-v2 at the pinned revision")
    vec = doc["vectors"]

    def embed(texts: list[str]) -> list[list[float]]:
        keys = [EC.key("query: ", texts[0])] + [EC.key("passage: ", t) for t in texts[1:]]
        missing = [k for k in keys if k not in vec]
        if missing:
            raise KeyError(f"{len(missing)} text(s) not in the embed cache")
        return [vec[k] for k in keys]
    return embed


def s_records(row: dict, steps: list[str], *, embed, generate, lex) -> list[dict]:
    from culinarystate.evaluation import d5_scoring as DS
    from culinarystate.evaluation import h1_rungs as H
    cut, out = int(row["cut_after_step"]), []
    for rung in S_RUNGS:
        ctx = H.context(rung, row["question"], steps, cut=cut, embed=embed, pre_cut_only=True, state_view="ANSWER")
        t0 = time.time()
        ans = generate(H.prompt(row["block"], row["question"], ctx))
        if row["block"] == "S1":
            gold = {i for i in row["gold_ingredient_ids"].split("|") if i}
            outcome = DS.s1_outcome(H.score_s1_detail(ans, gold, lex.linker.match_phrase))
        else:
            outcome = DS.s2_outcome(ans, row["gold_next_process_id"], lex.proc_ids.get)
        out.append({"qid": row["qid"], "rung": rung, "answer": ans, "s_outcome": outcome,
                    "latency_s": round(time.time() - t0, 2),
                    "config": {"pre_cut_only": True, "state_view": "ANSWER" if rung == "B4" else None,
                               "qid_guard": "NOT_USED_GOLD_IS_AI_DRAFTED_ENGINE_HIDDEN"}})
    return out


def _jsonable(x: Any) -> Any:
    return json.loads(json.dumps(x, default=str))


def pc_records(row: dict, ctx: tuple, *, model: str, branch: str) -> list[dict]:
    import run_ladder as RL
    rows = RL.run_one(row["question"], ctx, model)
    lex, R, req, fam, sup, ts = ctx
    r = RL.answer(row["question"], lex, R, req, fam, support_index=sup, troubleshoot=ts)
    d, packets, sl = r["decision"], r["packets"], r["slots"]
    ood = any(bool((v or {}).get("ood")) for v in (r.get("support") or {}).values())
    hyb = [h.evd_id for h in R.search(row["question"], RL.Query(), k=5)]
    decision = _jsonable({"mode": d.get("mode"), "precision": d.get("precision"), "sufficiency": d.get("reason"),
                          "reason": d.get("reason"), "per_option": d.get("per_option"),
                          "comparison": d.get("comparison"), "ood": ood})
    slots = {"ingredient_id": sl.ingredient_id, "process_ids": [p for _, p in sl.processes], "target": sl.target}
    pids = sorted({h.evd_id for p in packets.values() for h in p.direct + p.near})
    out = []
    for x in rows:
        rung = LADDER_MAP.get(x["rung"])
        if rung is None:
            continue
        rec = {"qid": row["qid"], "rung": rung, "answer": x["answer"], "route": {"branch": branch},
               "latency_s": x["latency_s"], "mode_violation": x["mode_violation"],
               "checker": {"numeric_claims": x["numeric_claims"], "unsupported": x["unsupported"]}}
        if rung == "B2":
            rec["retrieval"] = {"arm1": hyb}
        if rung in ("B5", "B7", "B5T"):
            rec.update(decision=decision, slots=slots, packet_ids=pids)
        if rung == "B7":
            rec["enforce"] = {"removed": [{"reason": z["reason"]} for z in x["removed"]], "fallback": x["fallback"],
                              "mode_fallback": False}
        out.append(rec)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--freeze-record", required=True)
    ap.add_argument("--s-context", required=True, help="recipe steps per S qid (Wikibooks / Gutenberg only)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--embed-cache", help="vectors from tools/s179_d5_embed_cache.py (torch-less hosts)")
    ap.add_argument("--blocks", nargs="+", default=None, help="smoke runs only: subset of blocks (new --out)")
    a = ap.parse_args(argv)
    from culinarystate.decision.query_router import route
    from culinarystate.evaluation import d5_scoring as DS
    from culinarystate.evaluation import frozen_guard as FG
    from culinarystate.generation.llm import generate
    out = Path(a.out)
    if out.exists():
        ap.error("refusing to overwrite an existing run file")
    chk = FG.check_real_inputs(ROOT, a.freeze_record, list(BENCH))
    if not chk["ok"]:
        ap.error(f"freeze guard refused: {chk['problems']}")
    rows = DS.load_benchmark([ROOT / b for b in BENCH])
    if a.blocks:
        rows = [r for r in rows if r["block"] in a.blocks]
    import run_ladder as RL
    st = RL.LedgerStore()
    lex, fam = RL.load_lexicon(st)
    cond = {c["id"]: c for c in st.all_latest("COND")}
    evd = st.all_latest("EVD")
    ctx = (lex, RL.EvidenceRetriever(evd, cond, fam), RL.load_requirements(st), fam, RL.SupportIndex(evd),
           RL.TroubleshootIndex.from_registry(ROOT))
    steps = {json.loads(x)["qid"]: json.loads(x)["steps"] for x in Path(a.s_context).read_text().splitlines() if x}
    need = any(r["block"] in ("S1", "S2") for r in rows)
    embed = (cached_embedder(Path(a.embed_cache)) if a.embed_cache else e5_embedder(a.device)) if need else None
    gen = lambda p: generate(p, a.model)  # noqa: E731
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    meta = {"record": "D5_RUN_META", "freeze_id": chk["freeze_id"], "freeze_record_sha256": chk["freeze_record_sha256"],
            "signoff": chk.get("signoff"), "git_commit": head, "model": a.model, "embed": [E5, E5_REV],
            "embed_cache_sha256": hashlib.sha256(Path(a.embed_cache).read_bytes()).hexdigest() if a.embed_cache else None,
            "labels": list(LABELS)}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    with out.open("x", encoding="utf-8") as fh:
        for r in rows:
            recs = (s_records(r, steps[r["qid"]], embed=embed, generate=gen, lex=lex) if r["block"] in ("S1", "S2")
                    else pc_records(r, ctx, model=a.model, branch=route(r["question"])["branch"]))
            for rec in recs:
                fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            fh.flush()
            print(r["qid"], len(recs), flush=True)
    print(json.dumps({"out": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
