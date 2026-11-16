#!/usr/bin/env python
"""S178 (T8-C17-R1, T8-C15-R3): build and check registry/prompt_registry_v1.csv, and print the run-record note.

Purpose (SSOT 244.5, REV-B G-21): every D5 / H1 / H3 run records, next to its run row, the prompt template hashes, the
checker and scorer versions, and the model name and digest. This tool

* hashes each prompt template (sha256 of the template rendered with sentinel arguments, and sha256 of the producing
  function's source) and each checker / scorer / verbaliser file;
* writes ``registry/prompt_registry_v1.csv`` (``--write``) or verifies that the committed CSV still matches the code
  (``--check``; exit 1 on drift, so a changed prompt cannot slip past the lock);
* prints the one-line note to paste into the ``notes`` column of ``registry/compute_runs_v1.csv`` (``--run-note``),
  filling the model digest from ``--digest`` or, if ``--ollama-url`` is given, from that server's ``/api/tags``.

It never calls a model (no ``/api/generate``) and never runs on a GPU. The model digest cannot be known on the host that
will run the rungs unless that host answers: the committed registry therefore carries ``PENDING_PIN_ON_RUN_HOST`` for
the run host and a REFERENCE row with the digest observed on another server, never a substitute.

    python tools/s178_prompt_registry.py --check
    python tools/s178_prompt_registry.py --write
    python tools/s178_prompt_registry.py --run-note --digest <sha256> [--ollama-url http://localhost:11435]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

REGISTRY = ROOT / "registry/prompt_registry_v1.csv"
COLS = ["prompt_id", "kind", "rung_or_use", "module", "symbol", "version_tag", "rendering", "template_sha256",
        "source_sha256", "llm_required", "model_name", "model_digest", "digest_status", "temperature", "seed",
        "num_predict", "num_ctx", "lock_status", "notes"]
PENDING = "PENDING_PIN_ON_RUN_HOST"
RUN_MODEL = "qwen2.5:7b-instruct"   # generation/llm.py default; D5 prereg draft section 2
# Observed 2026-11-09 on the local Ollama (v0.1.32) of the manjot server, GET /api/tags, metadata only. REFERENCE only:
# it is not the run host, and whether this digest equals the digest of the tag above on the run host is UNVERIFIED.
MANJOT_LOCAL_REF = ("qwen2.5:latest", "845dbda0ea48")
SENTINEL_ROW = {"id": "EVD-000000", "matrix": {"raw_name": "{MATRIX}"}, "process": {"raw_name": "{PROCESS}"},
                "target": {"raw_name": "{TARGET}"}, "tier": "E3",
                "derived": {"retention_factor": {"status": "MEASURED", "value": 0.5, "unit": "fraction"}}}


def sha(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def file_sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def src_sha(fn) -> str:
    return sha(inspect.getsource(fn))


def _packet():
    from culinarystate.retrieval.compatibility import Query
    from culinarystate.retrieval.retriever import EvidencePacket, Hit
    hit = Hit(evd_id=SENTINEL_ROW["id"], score=1.0, bm25=1.0, compat={}, row=SENTINEL_ROW)
    return EvidencePacket(question="{QUESTION}", query=Query(), evidence_class="DIRECT", direct=[hit])


def _row(prompt_id, kind, use, module, symbol, version, rendering, tsha, ssha, llm, notes=""):
    return {"prompt_id": prompt_id, "kind": kind, "rung_or_use": use, "module": module, "symbol": symbol,
            "version_tag": version, "rendering": rendering, "template_sha256": tsha, "source_sha256": ssha,
            "llm_required": "yes" if llm else "no",
            "model_name": RUN_MODEL if llm else "", "model_digest": PENDING if llm else "",
            "digest_status": "NOT_PINNED_RUN_HOST_NOT_REACHABLE_FROM_MANJOT" if llm else "NOT_APPLICABLE",
            "temperature": 0 if llm else "", "seed": 7 if llm else "", "num_predict": 200 if llm else "",
            "num_ctx": 4096 if llm else "",
            "lock_status": "CODE_DEFAULT_NOT_LOCKED" if llm else "NOT_APPLICABLE", "notes": notes}


def build_rows() -> list[dict]:
    from culinarystate.evaluation import h1_rungs
    from culinarystate.generation import prompts as P
    pk = _packet()
    rows = []
    ev = [("PR-B0", "B0", P.b0_prompt, P.b0_prompt("{QUESTION}")),
          ("PR-B2", "B1/B2 style retrieval prompt (S173 'B2')", P.b2_prompt, P.b2_prompt("{QUESTION}", pk)),
          ("PR-B5-ANSWER", "B5 mode ANSWER", P.b5_prompt,
           P.b5_prompt("{QUESTION}", pk, {"mode": "ANSWER", "precision": "QUANTITATIVE"}, ["{DISALLOWED_1}"])),
          ("PR-B5-ABSTAIN", "B5 mode ABSTAIN", P.b5_prompt,
           P.b5_prompt("{QUESTION}", pk, {"mode": "ABSTAIN"}, [])),
          ("PR-B5-ASK", "B5 mode ASK", P.b5_prompt,
           P.b5_prompt("{QUESTION}", pk, {"mode": "ASK", "ask_for": ["{SLOT}"], "ask_options": ["{OPTION}"]}, []))]
    for pid, use, fn, rendered in ev:
        rows.append(_row(pid, "PROMPT", use, "culinarystate.generation.prompts", fn.__name__, "(no version string)",
                         "function called with sentinel arguments ({QUESTION}, one synthetic evidence row)",
                         sha(rendered), src_sha(fn), True,
                         "rendered text hash binds wording; the sentinel evidence row is synthetic, not data"))
    rows.append(_row("PR-B5F", "PROMPT", "B5F rephrase prompt (B7 base)", "culinarystate.generation.prompts",
                     "b5f_prompt", "(no version string)", "source only: needs verbaliser facts", "",
                     src_sha(P.b5f_prompt), True, "template_sha256 blank: rendering needs a decision and packets"))
    rows.append(_row("PR-EVIDENCE-RENDER", "PROMPT_PART", "evidence row format inside B2/B5 prompts",
                     "culinarystate.generation.prompts", "render_evidence + _rf", "(no version string)",
                     "source of both functions", "", sha(inspect.getsource(P.render_evidence) + inspect.getsource(P._rf)),
                     False, "changes the text every RAG rung sees"))
    for blk in ("S1", "S2"):
        rows.append(_row(f"PR-H1-{blk}", "PROMPT", f"H1 {blk} question wrapper", "culinarystate.evaluation.h1_rungs",
                         "prompt", "(no version string)", f"prompt('{blk}', '{{QUESTION}}', '{{CONTEXT}}')",
                         sha(h1_rungs.prompt(blk, "{QUESTION}", "{CONTEXT}")), src_sha(h1_rungs.prompt), True, ""))
    rows.append(_row("PR-H1-CONTEXT", "PROMPT_PART", "H1 context builder (retrieval cut, state block)",
                     "culinarystate.evaluation.h1_rungs", "context + state_block + independent_context",
                     "(no version string)", "source of the three functions", "",
                     sha(inspect.getsource(h1_rungs.context) + inspect.getsource(h1_rungs.state_block)
                         + inspect.getsource(h1_rungs.independent_context)), False,
                     "uncommitted S178 EVAL edits may change this hash before the lock; re-run --write after the lock text"))
    for pid, rel, ver, use in [
            ("CK-VERBALIZE", "src/culinarystate/generation/verbalize.py", "verbalize@0.2", "B5T template (no LLM)"),
            ("CK-C17-CLAIMS", "src/culinarystate/generation/claims.py", "claims@0.2", "C17 checker used by B7 enforcement"),
            ("CK-ENFORCE", "src/culinarystate/generation/enforce.py", "", "B7 post-hoc enforcement"),
            ("CK-H3-INDEPENDENT", "src/culinarystate/evaluation/h3_independent.py", "h3_independent@0.1",
             "independent H3 scorer (H3-A/H3-B)"),
            ("CK-CLAIM-AUDIT", "src/culinarystate/evaluation/claim_audit.py", "", "blind claim-audit sample"),
            ("CK-LLM-CLIENT", "src/culinarystate/generation/llm.py", "", "Ollama client: decoding options")]:
        rows.append(_row(pid, "CHECKER_OR_CODE", use, rel.replace("/", ".")[4:-3], "(whole file)", ver,
                         "file sha256", "", file_sha(rel), False, ""))
    rows.append({**_row("EMB-E5", "EMBEDDING", "B1/B2 dense retrieval (decision D-D5-4 option E5)",
                        "tools/embed_texts.py", "CARDS['intfloat/e5-large-v2']", "", "model card prefixes 'query: ' / 'passage: '",
                        "", file_sha("tools/embed_texts.py"), False,
                        "Hugging Face revision must be filled from the local cache before the lock (amendment C3); the lock may not be issued with it blank"),
                 "model_name": "intfloat/e5-large-v2", "model_digest": "PENDING_HF_REVISION",
                 "digest_status": "NOT_PINNED_NO_TORCH_OR_CACHE_ON_MANJOT"})
    rows.append(_row("MODEL-RUN-HOST", "MODEL", "LLM for rungs B0/B1/B2/B4/B5/B7 (D5 prereg section 2)",
                     "culinarystate.generation.llm", "generate", "", "digest from the run host's /api/tags at run time",
                     "", file_sha("src/culinarystate/generation/llm.py"), True,
                     "digest MUST be filled on the run host by --pin / --run-note before the dry run (T8-C15-R3)"))
    rows.append({**_row("MODEL-REF-MANJOT-LOCAL", "MODEL_REFERENCE", "informational only, not the run host",
                        "(Ollama on manjot, localhost, v0.1.32)", "", "", "GET /api/tags metadata, no generation", "", "", False,
                        f"observed 2026-11-09; digest prefix only; equality with the run host's {RUN_MODEL} is UNVERIFIED; "
                        "the D5 prereg draft names the tag qwen2.5:7b-instruct, this local tag is qwen2.5:latest"),
                 "model_name": MANJOT_LOCAL_REF[0], "model_digest": MANJOT_LOCAL_REF[1] + " (prefix, 12 hex)",
                 "digest_status": "REFERENCE_ONLY"})
    return rows


def write_csv(rows, path: Path) -> None:
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def check() -> list[str]:
    """Return the drift list: ids whose hash columns differ between the committed CSV and the code."""
    have = {r["prompt_id"]: r for r in read_csv(REGISTRY)}
    problems = []
    for r in build_rows():
        h = have.get(r["prompt_id"])
        if h is None:
            problems.append(f"{r['prompt_id']}: missing from the committed registry")
            continue
        for col in ("template_sha256", "source_sha256", "version_tag"):
            if str(r[col]) != h[col]:
                problems.append(f"{r['prompt_id']}: {col} changed")
    return problems


def ollama_digest(base_url: str, model: str, timeout: int = 10) -> str | None:
    """Digest of ``model`` from ``GET <base_url>/api/tags`` (metadata only; never calls /api/generate)."""
    with urllib.request.urlopen(f"{base_url.rstrip('/')}/api/tags", timeout=timeout) as r:
        for m in json.loads(r.read()).get("models", []):
            if m.get("name") == model or m.get("model") == model:
                return m.get("digest")
    return None


def registry_sha() -> str:
    return hashlib.sha256(REGISTRY.read_bytes()).hexdigest()


def run_note(digest: str | None, model: str = RUN_MODEL) -> str:
    ids = ",".join(r["prompt_id"] for r in read_csv(REGISTRY) if r["kind"] in ("PROMPT", "PROMPT_PART", "CHECKER_OR_CODE"))
    return (f"model={model} digest={digest or PENDING} temperature=0 seed=7 num_predict=200 num_ctx=4096 "
            f"(code defaults; lock values override) prompt_registry=registry/prompt_registry_v1.csv "
            f"sha256={registry_sha()} prompt_ids={ids}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--run-note", action="store_true")
    ap.add_argument("--digest")
    ap.add_argument("--model", default=RUN_MODEL)
    ap.add_argument("--ollama-url")
    a = ap.parse_args(argv)
    if a.write:
        write_csv(build_rows(), REGISTRY)
        print("wrote", REGISTRY.relative_to(ROOT), "sha256", registry_sha())
    if a.check:
        problems = check()
        for p in problems:
            print("DRIFT:", p)
        if problems:
            return 1
        print("registry matches the code")
    if a.run_note:
        digest = a.digest
        if not digest and a.ollama_url:
            digest = ollama_digest(a.ollama_url, a.model)
            if digest is None:
                print(f"model {a.model} not listed at {a.ollama_url}", file=sys.stderr)
                return 2
        print(run_note(digest, a.model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
