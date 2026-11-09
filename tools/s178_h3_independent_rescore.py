#!/usr/bin/env python
"""S178 (T8-C12-R1): rescore the stored DEL-5 ladder answers with the independent H3 scorer and dry-run the human
claim-audit sample generator. Counts only; refuses to overwrite.

Inputs: reports/del5/ladder_{smoke_v1,v2_qwen7b,v2_qwen32b}.jsonl (AI-authored DEV questions, silver; not the D5 benchmark).
Per file and rung: the S173 numbers stored in the file (check_claims, the checker that enforce() also uses) next to the
independent scorer's (claim extraction + EVD-id lookup, no question cell: the DEV questions carry no gold cell, so relevance
is NOT_CHECKED and this run exercises extraction, positional binding and ledger lookup only). B5F+E is the ladder's B7.
Also: the exact sign test B2 vs B7 and B5T vs B7 on questions with an unsupported claim, and a dry-run audit sample for
Kush/Parv (sheets under data/derived/, git-ignored; only counts and file hashes are reported).

    python tools/s178_h3_independent_rescore.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evaluation import claim_audit as CA  # noqa: E402
from culinarystate.evaluation import h3_independent as H3  # noqa: E402
from culinarystate.evaluation import split_registry as SR  # noqa: E402

OUT = ROOT / "reports/s178/h3_independent_rescore_ladder.json"
AUDIT_DIR = ROOT / "data/derived/s178_h3_audit_dryrun"
LADDERS = ["ladder_smoke_v1", "ladder_v2_qwen7b", "ladder_v2_qwen32b"]
H3_NAME = {"B2": "B2", "B5T": "B5T", "B5F+E": "B7"}          # H3 rung names for the ladder rungs the prereg compares
SEED = "s178-h3-audit-dryrun-2026-11-09"
PER_RUNG = 15


def latest_evd() -> dict:
    out = {}
    with open(ROOT / "ledgers/data/EVD.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r
    return out


def main() -> int:
    if OUT.exists() or AUDIT_DIR.exists():
        sys.exit("refusing to overwrite an existing S178 H3 output")
    evd = latest_evd()
    report: dict = {"tool": "tools/s178_h3_independent_rescore.py", "module": H3.VERSION,
                    "status": "AI_DRAFTED_COUNTS_ONLY_DEV_SILVER_NON_CITABLE", "value_tolerance": H3.VALUE_TOL, "ladders": {}}
    answers_for_audit = []
    for name in LADDERS:
        path = ROOT / f"reports/del5/{name}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        qs = sorted({r["question"] for r in rows})
        qid = {q: f"{name}-Q{i:02d}" for i, q in enumerate(qs)}
        per_rung: dict[str, dict] = {}
        for rung in sorted({r["rung"] for r in rows}):
            rr = [r for r in rows if r["rung"] == rung]
            res = {}
            old_claims = old_bad = disagree_old_clean = disagree_new_clean = 0
            verdicts, kinds = Counter(), Counter()
            nonexist = outside = 0
            for r in rr:
                packet = {i for ids in r["packet_rows"].values() for i in ids} if "packet_rows" in r else None
                sc = H3.score_answer(r["answer"], evd=evd, cell=None, packet_ids=packet)
                res[qid[r["question"]]] = sc
                old_claims += r["numeric_claims"]
                old_bad += r["unsupported"]
                disagree_old_clean += r["unsupported"] == 0 and sc["n_numeric_unsupported"] > 0
                disagree_new_clean += r["unsupported"] > 0 and sc["n_numeric_unsupported"] == 0
                verdicts.update(c["verdict"] for c in sc["claims"] if c["kind"] == "NUMERIC")
                kinds.update(c["kind"] for c in sc["claims"])
                nonexist += len(sc["nonexistent_ids"])
                outside += len(sc["outside_packet_ids"])
                if rung in H3_NAME and name != "ladder_smoke_v1":
                    answers_for_audit.append({"qid": qid[r["question"]], "rung": H3_NAME[rung], "question": r["question"],
                                              "answer": r["answer"], "scored": sc, "checker_unsupported": r["unsupported"]})
            summ = H3.summarize_rung(res, {})
            covered = sum((v["n_numeric"] - v["n_numeric_unsupported"]) > 0 for v in res.values())
            per_rung[rung] = {
                "n_answers": len(rr),
                "s173_checker": {"numeric_claims": old_claims, "unsupported": old_bad,
                                 "ucr": round(old_bad / old_claims, 4) if old_claims else None},
                "independent": {"numeric_claims": summ["n_numeric_claims"], "unsupported": summ["n_unsupported"],
                                "ucr": summ["ucr"], "verdicts": dict(sorted(verdicts.items())),
                                "claim_kinds": dict(sorted(kinds.items())),
                                "selective_risk": summ["selective_risk"],
                                "questions_with_a_supported_claim": covered,
                                "abstained_answers": sum(v["abstained"] for v in res.values()),
                                "answers_with_no_claim_and_no_abstention": summ["answers_with_no_claim_and_no_abstention"],
                                "nonexistent_cited_ids": nonexist, "valid_ids_outside_packet": outside},
                "answer_level_disagreement": {"s173_clean_but_independent_flags": disagree_old_clean,
                                              "s173_flags_but_independent_clean": disagree_new_clean}}
            per_rung[rung]["_res"] = res
        cmp = {}
        for worse, better in (("B2", "B5F+E"), ("B5T", "B5F+E"), ("B5F", "B5F+E")):
            if worse in per_rung and better in per_rung:
                cmp[f"{worse}_vs_{better}"] = H3.compare_rungs(per_rung[worse]["_res"], per_rung[better]["_res"])
        for v in per_rung.values():
            v.pop("_res")
        report["ladders"][name] = {"input_sha256": SR.sha256_file(path), "n_questions": len(qs), "rungs": per_rung,
                                   "sign_tests_independent": cmp}
    items = CA.audit_items(answers_for_audit)
    sample = CA.stratified_audit_sample(items, per_rung=PER_RUNG, seed=SEED, rungs=CA.DEFAULT_RUNGS)
    files = CA.write_audit_files(sample["sample"], evd, AUDIT_DIR, seed=SEED)
    blob = "".join(Path(p).read_text(encoding="utf-8-sig") for k, p in files["paths"].items() if k != "key")
    report["audit_sample_dry_run"] = {
        "seed_sha256": sample["seed_sha256"], "per_rung_requested": PER_RUNG, "n_items": files["n_items"],
        "pool_by_rung_and_stratum": sample["design"], "shortfalls": sample["shortfalls"], "file_sha256": files["sha256"],
        "sheets_location": "data/derived/s178_h3_audit_dryrun (git-ignored; hold answer text and ledger display fields)",
        "rung_blind_check": {"rung_names_absent_from_sheets": not any(t in blob for t in ("B2", "B5T", "B7", "B5F")),
                             "automatic_verdict_names_absent": not any(t in blob for t in
                                                                       ("VALUE_MISMATCH", "WRONG_CELL", "SUPPORTED", "NONEXISTENT_ID"))},
        "note": "DRY RUN on DEV silver answers: demonstrates the generator; the real sample is drawn from the D5 rung outputs "
                "after the benchmark is frozen and the rungs have run (B2, B5T, B7; REV-B: 40-60 claims per rung)."}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(report, indent=1, sort_keys=True) + "\n").encode()
    with open(OUT, "xb") as fh:
        fh.write(data)
    print(json.dumps({"out": OUT.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(data).hexdigest(),
                      "audit_files": files["sha256"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
