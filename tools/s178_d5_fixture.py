#!/usr/bin/env python3
"""S178 H1H3H: build the SYNTHETIC D5 scoring fixture in tests/fixtures/d5_synthetic/. AI_DRAFTED.

Everything here is invented for testing the harness: ``SYN-`` qids, made-up foods (fixturefruit, fixtureleaf, ...),
synthetic ids (ING-99xxxx, PROC-99xxxx, SVAR-99xxxx, EVD-99xxxx), synthetic answers and synthetic retention values.
Nothing is drawn from the D5 drafts, the EVD ledger or any recipe; no number in it is a food-chemistry value. The
fixture exists so that every metric can be checked by hand before the benchmark is frozen
(``SYNTHETIC_FIXTURE_NOT_A_RESULT``).

  python tools/s178_d5_fixture.py [--check]

Deterministic; ``--check`` verifies that the files on disk equal what this script would write.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests/fixtures/d5_synthetic"
STAMP = "SYNTHETIC_FIXTURE_NOT_A_RESULT"
D = "SYNTHETIC_FIXTURE"
COLS = ["qid", "block", "question", "ingredient_id", "food", "process", "process_id", "process_2", "process_id_2",
        "target", "target_svars", "gold_mode", "gold_branch", "gold_compare", "gold_evd_ids", "gold_retention_range",
        "gold_evd_ids_2", "gold_retention_range_2", "gold_origin", "drafted_by"]

FRUIT, LEAF, ROOTV, STONE, GROUP, PEPPER = "ING-990001", "ING-990002", "ING-990003", "ING-990004", "ING-990009", "ING-990005"
BOIL, STEAM, BAKE, FRY = "PROC-990001", "PROC-990002", "PROC-990003", "PROC-990004"
VITC, FOL = "SVAR-990001", "SVAR-990002"


def evd_row(n, ing, raw, proc, step, svar, tname, value, fam, group):
    return {"id": f"EVD-{n:06d}", "status": "ACTIVE", "tier": "E3", "source_family_id": fam, "independence_group": group,
            "matrix": {"ingredient_id": ing, "raw_name": raw}, "process": {"process_id": proc, "steps": [step], "raw_name": step},
            "target": {"state_variable_id": svar, "raw_name": tname},
            "derived": {"retention_factor": {"status": "MEASURED", "value": value, "unit": "fraction"}}}


EVD = [
    evd_row(990001, FRUIT, "fixturefruit", BOIL, "boil", VITC, "Vitamin C", 0.65, "SYN-FAM-A", "SYN-G1"),
    evd_row(990002, FRUIT, "fixturefruit", BOIL, "boil", VITC, "Vitamin C", 0.70, "SYN-FAM-A", "SYN-G2"),
    evd_row(990003, FRUIT, "fixturefruit", STEAM, "steam", VITC, "Vitamin C", 0.85, "SYN-FAM-B", "SYN-G3"),
    evd_row(990004, GROUP, "fixturegroup", BOIL, "boil", VITC, "Vitamin C", 0.55, "SYN-FAM-B", "SYN-G4"),
    evd_row(990005, ROOTV, "fixtureroot", BAKE, "bake", FOL, "Folate", 0.40, "SYN-FAM-A", "SYN-G5"),
    evd_row(990006, ROOTV, "fixtureroot", BOIL, "boil", FOL, "Folate", 0.45, "SYN-FAM-A", "SYN-G6"),
]
RELATIVES = {LEAF: [GROUP]}


def row(qid, block, question, **kw):
    r = {c: "" for c in COLS}
    r.update(qid=qid, block=block, question=question, drafted_by=D, **kw)
    return r


S_Q = "Synthetic recipe state question number {n}."
ROWS = [
    *[row(f"SYN-S1-{i:03d}", "S1", S_Q.format(n=i), gold_branch="UNKNOWN", gold_origin="HUMAN_BLIND") for i in (1, 2, 3)],
    *[row(f"SYN-S2-{i:03d}", "S2", S_Q.format(n=i + 3), gold_branch="UNKNOWN", gold_origin="HUMAN_BLIND") for i in (1, 2, 3)],
    row("SYN-P1-001", "P1", "Synthetic: vitamin C left in boiled fixturefruit?", ingredient_id=FRUIT, food="fixturefruit",
        process="boil", process_id=BOIL, target="vitamin C", target_svars=VITC, gold_mode="ANSWER",
        gold_branch="TRANSFORMATION", gold_evd_ids="EVD-990001|EVD-990002", gold_retention_range="0.65-0.70 fraction retained (n=2)"),
    row("SYN-P1-002", "P1", "Synthetic: folate left in boiled fixtureroot?", ingredient_id=ROOTV, food="fixtureroot",
        process="boil", process_id=BOIL, target="folate", target_svars=FOL, gold_mode="ANSWER", gold_branch="TRANSFORMATION",
        gold_evd_ids="EVD-990006", gold_retention_range="0.45-0.45 fraction retained (n=1)"),
    row("SYN-P2-001", "P2", "Synthetic: vitamin C left in boiled fixtureleaf?", ingredient_id=LEAF, food="fixtureleaf",
        process="boil", process_id=BOIL, target="vitamin C", target_svars=VITC, gold_mode="ANSWER_SIMILAR_ONLY",
        gold_branch="TRANSFORMATION", gold_evd_ids="EVD-990004", gold_retention_range="0.55-0.55 fraction retained (n=1)"),
    row("SYN-P3-001", "P3", "Synthetic: vitamin C left in fried fixturestone?", ingredient_id=STONE, food="fixturestone",
        process="fry", process_id=FRY, target="vitamin C", target_svars=VITC, gold_mode="ABSTAIN", gold_branch="TRANSFORMATION"),
    row("SYN-P3-002", "P3", "Synthetic: folate left in baked fixtureleaf?", ingredient_id=LEAF, food="fixtureleaf",
        process="bake", process_id=BAKE, target="folate", target_svars=FOL, gold_mode="ABSTAIN", gold_branch="TRANSFORMATION"),
    row("SYN-C-001", "C", "Synthetic: boil or steam fixturefruit for vitamin C?", ingredient_id=FRUIT, food="fixturefruit",
        process="boil", process_id=BOIL, process_2="steam", process_id_2=STEAM, target="vitamin C", target_svars=VITC,
        gold_mode="COMPARE", gold_branch="TRANSFORMATION", gold_evd_ids="EVD-990001|EVD-990002",
        gold_retention_range="0.65-0.70 fraction retained (n=2)", gold_evd_ids_2="EVD-990003",
        gold_retention_range_2="0.85-0.85 fraction retained (n=1)"),
    row("SYN-C-002", "C", "Synthetic: bake or boil fixtureroot for folate?", ingredient_id=ROOTV, food="fixtureroot",
        process="bake", process_id=BAKE, process_2="boil", process_id_2=BOIL, target="folate", target_svars=FOL,
        gold_mode="COMPARE", gold_branch="TRANSFORMATION", gold_compare="CANNOT_SEPARATE", gold_evd_ids="EVD-990005",
        gold_retention_range="0.40-0.40 fraction retained (n=1)", gold_evd_ids_2="EVD-990006",
        gold_retention_range_2="0.45-0.45 fraction retained (n=1)"),
    row("SYN-U-001", "U", "Synthetic: what replaces fixturepepper?", ingredient_id=PEPPER, food="fixturepepper",
        gold_mode="ABSTAIN_NO_EDGE", gold_branch="RELATIONSHIP"),
    row("SYN-X-001", "X", "Synthetic food-safety control question.", gold_mode="REFUSE", gold_branch="SAFETY"),
    row("SYN-X-002", "X", "Synthetic vague control question.", gold_mode="ABSTAIN", gold_branch="UNKNOWN"),
]
BRANCH = {r["qid"]: r["gold_branch"] for r in ROWS}
BRANCH["SYN-S2-003"] = "TRANSFORMATION"          # one router miss in S
BRANCH["SYN-X-002"] = "TRANSFORMATION"           # one router miss in X

ABSTAIN_TXT = "There is no measured evidence for this, so I can't give a number."
H3_ANSWERS = {
    "B2": {"SYN-P1-001": "Boiled fixturefruit keeps about 90 % of its vitamin C [EVD-990001].",
           "SYN-P1-002": "About 45 % of the folate remains after boiling [EVD-990006].",
           "SYN-P2-001": "It keeps 80 % of the vitamin C.",
           "SYN-P3-001": "Frying keeps about 60 % of vitamin C.",
           "SYN-P3-002": ABSTAIN_TXT,
           "SYN-C-001": "Steaming keeps more: 85 % [EVD-990003] versus 65 % [EVD-990001].",
           "SYN-C-002": "Baking loses 70 % of folate.",
           "SYN-U-001": "Use fixturechili instead.", "SYN-X-001": "It is fine at 20 % doneness.", "SYN-X-002": ABSTAIN_TXT},
    "B7": {"SYN-P1-001": "Boiled fixturefruit keeps 65 % of its vitamin C [EVD-990001].",
           "SYN-P1-002": "About 50 % of the folate remains after boiling [EVD-990006].",
           "SYN-P2-001": "Only similar foods are measured: about 55 % is kept [EVD-990004].",
           "SYN-P3-001": ABSTAIN_TXT, "SYN-P3-002": ABSTAIN_TXT,
           "SYN-C-001": "Steaming keeps more: 85 % [EVD-990003] versus 65 % [EVD-990001].",
           "SYN-C-002": "Too few independent sources to compare the options.",
           "SYN-U-001": "No recorded alternative exists, so I can't suggest one.",
           "SYN-X-001": "I can't answer food-safety questions; please check official guidance.",
           "SYN-X-002": "I don't know what you are asking."},
}
H3_ANSWERS["B5T"] = {**H3_ANSWERS["B7"], "SYN-P1-002": "About 45 % of the folate remains after boiling [EVD-990006]."}
H3_ANSWERS["B5"] = {**H3_ANSWERS["B2"], "SYN-P2-001": "Only similar foods are measured: about 55 % is kept [EVD-990004]."}
H3_ANSWERS["B0"] = {q: "It keeps roughly 50 %." for q in H3_ANSWERS["B2"]}

DECISIONS = {
    "SYN-P1-001": {"mode": "ANSWER", "precision": "QUANTITATIVE", "sufficiency": "DIRECT", "ood": False},
    "SYN-P1-002": {"mode": "ANSWER", "precision": "QUANTITATIVE", "sufficiency": "DIRECT", "ood": False},
    "SYN-P2-001": {"mode": "ANSWER", "precision": "INTERVAL", "sufficiency": "NEAR_PARTIAL", "ood": False},
    "SYN-P3-001": {"mode": "ABSTAIN", "precision": "ABSTAIN", "sufficiency": "NO_EVIDENCE", "ood": True},
    "SYN-P3-002": {"mode": "ABSTAIN", "precision": "ABSTAIN", "sufficiency": "NO_EVIDENCE", "ood": True},
    "SYN-C-001": {"mode": "COMPARE", "ood": False, "comparison": {"verdict": "SEPARATED", "order": ["steam", "boil"]},
                  "per_option": {"boil": {"precision": "QUANTITATIVE", "sufficiency": "DIRECT", "process_id": BOIL},
                                 "steam": {"precision": "QUANTITATIVE", "sufficiency": "DIRECT", "process_id": STEAM}}},
    "SYN-C-002": {"mode": "COMPARE", "ood": False, "comparison": {"verdict": "OVERLAPPING", "order": None},
                  "per_option": {"bake": {"precision": "QUALITATIVE", "sufficiency": "BROAD_QUALITATIVE", "process_id": BAKE},
                                 "boil": {"precision": "QUANTITATIVE", "sufficiency": "DIRECT", "process_id": BOIL}}},
    "SYN-U-001": {"mode": "ABSTAIN", "precision": "ABSTAIN"},
    "SYN-X-001": {"mode": "ABSTAIN", "precision": "ABSTAIN"},
    "SYN-X-002": {"mode": "ASK"},
}
ENFORCE = {"SYN-P1-001": {"removed": [{"reason": "UNSUPPORTED_NUMBER"}], "fallback": False, "mode_fallback": False},
           "SYN-P3-001": {"removed": [{"reason": "PRECISION_CAP"}], "fallback": True, "mode_fallback": False},
           "SYN-C-002": {"removed": [], "fallback": True, "mode_fallback": False}}
SLOTS = {  # B7 / B5T slot extraction (synthetic)
    "SYN-P1-001": {"ingredient_id": FRUIT, "process_ids": [BOIL], "target": "vitamin C", "target_svar": VITC},
    "SYN-P1-002": {"ingredient_id": ROOTV, "process_ids": [BOIL], "target": "folate", "target_svar": FOL},
    "SYN-P2-001": {"ingredient_id": LEAF, "process_ids": [BOIL], "target": "vitamin C"},
    "SYN-P3-001": {"ingredient_id": None, "process_ids": None, "target": None},
    "SYN-P3-002": {"ingredient_id": LEAF, "process_ids": [BAKE], "target": "folate", "target_svar": FOL},
    "SYN-C-001": {"ingredient_id": FRUIT, "process_ids": [BOIL], "target": "vitamin C", "target_svar": VITC},
    "SYN-C-002": {"ingredient_id": ROOTV, "process_ids": [BAKE, BOIL], "target": "folate", "target_svar": FOL},
    "SYN-U-001": {"ingredient_id": PEPPER, "process_ids": [], "target": None},
}
M = {"matrix": "MATCH", "process": "MATCH", "target": "MATCH", "time": "UNKNOWN", "temperature": "UNKNOWN", "medium": "UNKNOWN"}
RETRIEVAL = {  # rung -> qid -> (arm lists, compat vectors for gold ids, states_condition)
    "B2": {"SYN-P1-001": ({"arm1": ["EVD-990003", "EVD-990001", "EVD-990005", "EVD-990002"]},
                          {"EVD-990001": {**M, "time": "MATCH"}, "EVD-990002": {**M, "time": "MISMATCH"}}, True),
           "SYN-P1-002": ({"arm1": ["EVD-990006"]}, {"EVD-990006": M}, False),
           "SYN-P2-001": ({"arm1": ["EVD-990001", "EVD-990003"]}, {"EVD-990004": M}, False),
           "SYN-P3-001": ({"arm1": []}, {}, False),
           "SYN-P3-002": ({"arm1": ["EVD-990006"]}, {}, False),
           "SYN-C-001": ({"arm1": ["EVD-990001", "EVD-990002"], "arm2": ["EVD-990001", "EVD-990003"]},
                         {"EVD-990001": M, "EVD-990002": M, "EVD-990003": M}, False),
           "SYN-C-002": ({"arm1": ["EVD-990005"], "arm2": ["EVD-990006"]}, {"EVD-990005": M, "EVD-990006": M}, False)},
    "B7": {"SYN-P1-001": ({"arm1": ["EVD-990001", "EVD-990002"]},
                          {"EVD-990001": {**M, "time": "MATCH"}, "EVD-990002": {**M, "time": "MISMATCH"}}, True),
           "SYN-P1-002": ({"arm1": ["EVD-990006"]}, {"EVD-990006": M}, False),
           "SYN-P2-001": ({"arm1": ["EVD-990004"]}, {"EVD-990004": M}, False),
           "SYN-P3-001": ({"arm1": []}, {}, False),
           "SYN-P3-002": ({"arm1": []}, {}, False),
           "SYN-C-001": ({"arm1": ["EVD-990001", "EVD-990002"], "arm2": ["EVD-990003"]},
                         {"EVD-990001": M, "EVD-990002": M, "EVD-990003": M}, False),
           "SYN-C-002": ({"arm1": ["EVD-990005"], "arm2": ["EVD-990006"]}, {"EVD-990005": M, "EVD-990006": M}, False)},
}
S_OUTCOME = {"B4": [True] * 6, "B1": [False, False, False, False, False, True], "B2": [False, True, False, False, False, False],
             "B0": [False, False, "UNRESOLVED", False, False, False]}
S_QIDS = [r["qid"] for r in ROWS if r["block"] in ("S1", "S2")]
ABL = {  # ablated B7 answers (one component off at a time); FULL = B7
    "state_conditioning": {"SYN-P1-001": ABSTAIN_TXT},
    "evidence_compatibility": {"SYN-P2-001": "About 65 % is kept [EVD-990001]."},
    "claim_enforcement": {"SYN-P1-001": "Boiled fixturefruit keeps 90 % of its vitamin C [EVD-990001]."},
    "ood_gate": {"SYN-P3-001": "Roughly 60 % survives [EVD-990001]."},
}


def records() -> list[dict]:
    out = []
    for r in ROWS:
        q = r["qid"]
        for rung in ("B0", "B1", "B2", "B4", "B5", "B7", "B5T"):
            rec: dict = {"qid": q, "rung": rung, "route": {"branch": BRANCH[q]}}
            if q in S_QIDS:
                if rung not in S_OUTCOME:
                    continue
                rec["answer"] = "synthetic S answer"
                rec["s_outcome"] = S_OUTCOME[rung][S_QIDS.index(q)]
                out.append(rec)
                continue
            if rung not in H3_ANSWERS and rung not in RETRIEVAL:
                continue
            rec["answer"] = H3_ANSWERS.get(rung, {}).get(q, "")
            if rung in ("B7", "B5T") and q in DECISIONS:
                rec["decision"] = DECISIONS[q]
                if q in SLOTS:
                    rec["slots"] = SLOTS[q]
            if rung == "B7" and q in DECISIONS:
                rec["enforce"] = ENFORCE.get(q, {"removed": [], "fallback": False, "mode_fallback": False})
            if rung in RETRIEVAL and q in RETRIEVAL[rung]:
                lists, vec, cond = RETRIEVAL[rung][q]
                rec.update(retrieval=lists, gold_compat=vec, query_states_condition=cond)
            if rung == "B2" and q == "SYN-C-001":
                rec["predicted_compare"] = "ARM2_BETTER"
            if rung in ("B2", "B7"):
                rec["checker"] = {"numeric_claims": rec["answer"].count("%"),
                                  "unsupported": 0 if rung == "B7" else int("[EVD-" not in rec["answer"] and "%" in rec["answer"])}
                rec["mode_violation"] = rung == "B2" and q.startswith("SYN-X")
                rec["latency_s"] = 1.5 if rung == "B2" else 2.5
            out.append(rec)
    return out


def ablation_records() -> list[dict]:
    b7 = {r["qid"]: r for r in records() if r["rung"] == "B7" and r["qid"][4:6] in ("P1", "P2", "P3", "C-")}
    out = []
    for cfg in ("FULL",) + tuple(ABL):
        for q, rec in sorted(b7.items()):
            new = {k: v for k, v in rec.items() if k in ("qid", "answer", "decision")}
            new.update(rung="B7", config=cfg)
            if cfg != "FULL" and q in ABL[cfg]:
                new["answer"] = ABL[cfg][q]
            out.append(new)
    return out


def _csv(rows) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def _jsonl(objs) -> str:
    return "".join(json.dumps(o, sort_keys=True) + "\n" for o in objs)


def build() -> dict[str, str]:
    files = {"benchmark_synthetic.csv": _csv(ROWS), "runs_synthetic.jsonl": _jsonl(records()),
             "evd_synthetic.jsonl": _jsonl(EVD), "relatives_synthetic.json": json.dumps(RELATIVES, sort_keys=True, indent=1) + "\n",
             "ablation_runs_synthetic.jsonl": _jsonl(ablation_records())}
    man = {"stamp": STAMP, "synthetic": True, "built_by": "tools/s178_d5_fixture.py",
           "note": "invented ids, foods, answers and values for harness tests; not D5 data, not food-chemistry values",
           "files": {k: hashlib.sha256(v.encode("utf-8")).hexdigest() for k, v in sorted(files.items())}}
    files["manifest.json"] = json.dumps(man, sort_keys=True, indent=1) + "\n"
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="verify the files on disk instead of writing")
    a = ap.parse_args(argv)
    files = build()
    if a.check:
        bad = [k for k, v in files.items() if not (OUT / k).is_file() or (OUT / k).read_text(encoding="utf-8") != v]
        print("OK" if not bad else f"DIFFERS: {bad}")
        return 1 if bad else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for k, v in files.items():
        (OUT / k).write_text(v, encoding="utf-8", newline="\n")
    print(json.dumps({k: hashlib.sha256(v.encode()).hexdigest() for k, v in files.items()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
