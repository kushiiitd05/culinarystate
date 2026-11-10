#!/usr/bin/env python3
"""S179 / D-085: ksh+prv (AI) review of the D5 drafts and the build of the D5 benchmark v1 for freezing.

AI_DELEGATED_D085, NO_HUMAN_SIGNOFF_D085. The reviewers are the AI personas ksh and prv (one model) acting for Kush
and Parv under D-085; their agreement is not inter-rater evidence. Verdicts are KEEP or DROP (no edits). Entry is by
rank: the first ``TAKE[block]`` kept rows of each block enter, so a drop never lets the reviewer choose a replacement.

- **S gold** was written by the personas from the recipe text alone (steps 1..cut for S1, step cut+1 for S2), with the
  engine draft and every ``gold_*`` column hidden. It is ``AI_DRAFTED_GOLD``, not HUMAN_BLIND: H1 is never
  INDEPENDENT_GOLD on it. A question whose gold cannot be linked to an ING / PROC id by the scorer's own linker is
  dropped (no answer could score correct).
- **P / C gold** is the S171 draft, rechecked here against the EVD ledger (latest version of each cited row): the
  range and n must equal the cited rows' retention values (USDA % / 100; Bognar and Phenol-Explorer fractions as
  stored), else the build refuses.
- **U / X** are the S178 drafts (`reports/s178/evd/d5_UX_blocks_S178_DRAFT.csv`), all kept.

  python tools/s179_d085_d5_review.py [--check]

Writes `benchmark/d5/d5_benchmark_v1_D085_{S,PC,UX}.csv` and `reports/del5/d5_review_ksh_prv_D085.csv` (ids,
questions, gold and verdicts only; no recipe text). Deterministic; ``--check`` compares with the files on disk.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

REVIEWER = "ksh+prv (AI, D-085)"
LABEL = "NO_HUMAN_SIGNOFF_D085"
TAKE = {"S1": 15, "S2": 15, "P1": 10, "P2": 10, "P3": 10, "C": 10, "U": 5, "X": 5}
S_DRAFT = ROOT / "benchmark/d5/d5_draft_S_v1.csv"
PC_DRAFT = ROOT / "benchmark/d5/d5_draft_PC_v1.csv"
UX_DRAFT = ROOT / "reports/s178/evd/d5_UX_blocks_S178_DRAFT.csv"
OUT = {"S": ROOT / "benchmark/d5/d5_benchmark_v1_D085_S.csv", "PC": ROOT / "benchmark/d5/d5_benchmark_v1_D085_PC.csv",
       "UX": ROOT / "benchmark/d5/d5_benchmark_v1_D085_UX.csv", "REVIEW": ROOT / "reports/del5/d5_review_ksh_prv_D085.csv"}

# ---------------------------------------------------------------- S verdicts and gold (recipe text only, engine hidden)
S = {
 "D5-S2-001": ("KEEP", "stir", "step 4: egg-sugar mix added to cornstarch-milk and stirred into the boiling milk"),
 "D5-S2-002": ("KEEP", "pour", "step 4: vanilla into the syrup at hard crack, poured over the corn"),
 "D5-S2-003": ("DROP", None, "steps 1-6 are ingredient-list fragments; step 6 is not an action"),
 "D5-S2-004": ("KEEP", "chill", "step 5: put on ice"),
 "D5-S2-005": ("DROP", None, "descriptive text about lamb, no procedure; step 4 is not an action"),
 "D5-S2-006": ("DROP", None, "household tips about the oven, not a recipe"),
 "D5-S2-007": ("KEEP", "crush", "step 3: crackers pounded fine and rolled in butter"),
 "D5-S2-008": ("DROP", None, "ingredient list only; step 5 is not an action"),
 "D5-S2-009": ("KEEP", "beat", "step 6: add sugar, salt and vinegar and keep beating"),
 "D5-S2-010": ("DROP", None, "step 8 is a substitution note, not an action"),
 "D5-S2-011": ("KEEP", "reduce", "step 7: reduce the cream to one-third pint"),
 "D5-S2-012": ("DROP", None, "step 8 is a negative instruction (do not stir); no next action"),
 "D5-S2-013": ("DROP", None, "table of contents, not a recipe"),
 "D5-S2-014": ("KEEP", "cool", "step 4: cool, add salt and flavouring, spread"),
 "D5-S2-015": ("KEEP", "bake", "step 4: bake the mixture in puff paste"),
 "D5-S2-016": ("KEEP", "cook", "step 4: heat slowly and cook about six hours"),
 "D5-S2-017": ("KEEP", "stir", "step 5: stir in the sugar and chill"),
 "D5-S2-018": ("DROP", None, "gold action (drop by spoonfuls) has no PROC id, so no answer can be scored"),
 "D5-S2-019": ("KEEP", "drain", "step 3: drain the sago and add milk"),
 "D5-S2-020": ("KEEP", "remove", "step 14: remove the steak from the gravy"),
 "D5-S1-001": ("KEEP", ["cider"], "cider boiled (steps 2-3); step 4 is cheesecloth prep"),
 "D5-S1-002": ("DROP", None, "two sauce receipts merged with cross-references; whether step 5 heats is not stated"),
 "D5-S1-003": ("DROP", None, "several alternative apple preparations, not one sequence"),
 "D5-S1-004": ("KEEP", [], "nothing heated by step 3 (bake is step 4)"),
 "D5-S1-005": ("KEEP", ["rhubarb juice", "sugar", "water", "vinegar", "cloves", "mace", "allspice", "ginger", "cinnamon"],
               "drained juice (with the dissolved sugar), water and vinegar boiled with the spice bag (step 5)"),
 "D5-S1-006": ("KEEP", ["beef", "brandy", "red wine", "veal gravy", "espagnole sauce", "bouquet garni", "mushrooms", "butter",
                        "bacon", "onions"], "braise liquid and garnish all heated by step 11"),
 "D5-S1-007": ("DROP", None, "culinary glossary, not a recipe"),
 "D5-S1-008": ("KEEP", ["sausages"], "sausages boiled (step 1)"),
 "D5-S1-009": ("KEEP", ["orange rind", "orange", "sugar", "water"], "rinds boiled in water; marmalade boiled with pulp, juice and sugar"),
 "D5-S1-010": ("KEEP", ["celery", "water", "salt"], "celery boiled in salted water (step 6)"),
 "D5-S1-011": ("KEEP", ["chicken", "water", "salt", "rice", "herbs", "onions", "celery", "parsley"],
               "soup boiled through step 6; steps 7-13 are serving notes and variants"),
 "D5-S1-012": ("KEEP", ["prunes", "water", "salt", "cream of wheat"], "prunes cooked in soak water; salt and wheat cooked over hot water"),
 "D5-S1-013": ("DROP", None, "general poaching method for any fish, not one recipe"),
 "D5-S1-014": ("KEEP", ["vinegar", "sugar", "spices"], "vinegar, sugar and spices boiled (step 2); citron not yet added"),
 "D5-S1-015": ("KEEP", ["sugar", "milk"], "sugar melted and added to scalded milk; eggs only receive the hot mixture (not cooked)"),
 "D5-S1-016": ("KEEP", ["meat", "salt pork", "water", "salt", "pepper", "butter", "dumplings"], "stew cooked and seasoned; dumplings cooked (step 5)"),
 "D5-S1-017": ("KEEP", ["artichokes", "onion", "water", "butter", "flour", "milk"], "artichokes and onion cooked in water; roux with scalded milk"),
 "D5-S1-018": ("DROP", None, "several veal receipts in one text"),
 "D5-S1-019": ("KEEP", ["beef", "veal", "bones", "bacon", "ham", "butter", "onions", "cloves", "turnip", "carrots", "celery", "sugar",
                        "salt", "pepper", "mace", "herbs", "water"], "every stock ingredient simmered (steps 12-14)"),
 "D5-S1-020": ("DROP", None, "pairing table (roast X with Y sauce), no process"),
}
S_UNLINKABLE = {"D5-S1-016": "gold item 'dumplings' has no ING id, so no answer can be scored correct",
                "D5-S1-019": "gold item 'bones' has no ING id, so no answer can be scored correct"}

# ---------------------------------------------------------------- P / C verdicts (KEEP unless listed)
ABSENT = "target is near-absent in this food: a correct system may answer TARGET_ABSENT, which gold ANSWER would mark wrong"
NONSENSE = "process is implausible for this food; the question tests nothing a cook would ask"
PC_DROP = {"D5-P1-005": ABSENT, "D5-P1-011": ABSENT, "D5-P1-012": ABSENT, "D5-P1-015": ABSENT,
           "D5-P2-021": NONSENSE + " (frying stock); also " + ABSENT, "D5-P2-026": NONSENSE + " (deep-frying stock)",
           "D5-P2-027": NONSENSE + " (baking stock)", "D5-P2-029": ABSENT,
           "D5-P3-035": NONSENSE + " (deep-frying juice)", "D5-P3-044": NONSENSE + " (deep-frying a spice)",
           "D5-C-006": ABSENT, "D5-C-010": ABSENT, "D5-C-013": ABSENT}


class BuildRefused(RuntimeError):
    pass


def _read(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def _evd_latest(path: Path = ROOT / "ledgers/data/EVD.jsonl") -> dict[str, dict]:
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            out[r["id"]] = r
    return out


def gold_range(evd_ids: str, evd: dict[str, dict]) -> str:
    """'lo-hi fraction retained (n=k)' from the cited rows' MEASURED retention values (as fractions)."""
    vals = []
    for i in (s for s in evd_ids.split("|") if s):
        rf = ((evd.get(i) or {}).get("derived") or {}).get("retention_factor") or {}
        scale = {"%": 100, "fraction": 1}.get(rf.get("unit"))
        if rf.get("status") != "MEASURED" or scale is None:
            raise BuildRefused(f"{i}: not a MEASURED retention row in % or fraction")
        vals.append(Fraction(str(rf["value"])) / scale)
    if not vals:
        return ""
    return f"{float(min(vals)):.2f}-{float(max(vals)):.2f} fraction retained (n={len(vals)})"


def _enter(rows: list[dict], verdict: dict[str, tuple[str, str]]) -> tuple[list[dict], list[dict]]:
    """Rank-order entry: the first TAKE[block] KEEP rows enter. Returns (entered rows, review rows)."""
    entered, review, taken = [], [], {}
    for r in sorted(rows, key=lambda x: (x["block"], int(x["rank_in_block"]))):
        v, why = verdict[r["qid"]]
        ok = v == "KEEP" and taken.get(r["block"], 0) < TAKE[r["block"]]
        if ok:
            taken[r["block"]] = taken.get(r["block"], 0) + 1
            entered.append(r)
        review.append({"qid": r["qid"], "block": r["block"], "rank_in_block": r["rank_in_block"], "verdict": v,
                       "reason": why, "entered": "true" if ok else "false", "reviewer": REVIEWER, "label": LABEL})
    return entered, review


def build_s() -> tuple[list[dict], list[dict]]:
    from culinarystate.decision.pipeline import load_lexicon
    from culinarystate.ledgers.store import LedgerStore
    lex, _ = load_lexicon(LedgerStore())
    drafts = _read(S_DRAFT)
    if {r["qid"] for r in drafts} != set(S):
        raise BuildRefused("S verdict table does not cover exactly the S drafts")
    verdict, gold = {}, {}
    for q, (v, g, why) in S.items():
        if v == "KEEP" and q in S_UNLINKABLE:
            v, why = "DROP", S_UNLINKABLE[q]
        if v == "KEEP" and isinstance(g, list):
            ids = [lex.linker.match_phrase(n) for n in g]
            if None in ids:
                raise BuildRefused(f"{q}: unlinkable gold item(s) {[n for n, i in zip(g, ids) if i is None]}")
            gold[q] = (g, sorted(set(ids)))
        elif v == "KEEP":
            pid = lex.proc_ids.get(g)
            if pid is None:
                raise BuildRefused(f"{q}: gold action {g!r} has no PROC id")
            gold[q] = (g, pid)
        verdict[q] = (v, why)
    entered, review = _enter(drafts, verdict)
    out = []
    for r in entered:
        names, gid = gold[r["qid"]]
        s1 = r["block"] == "S1"
        out.append({"qid": r["qid"], "block": r["block"], "rank_in_block": r["rank_in_block"], "recipe_id": r["recipe_id"],
                    "source_family": r["source_family"], "n_steps": r["n_steps"], "cut_after_step": r["cut_after_step"],
                    "question": r["question"], "gold_ingredients": "|".join(names) if s1 else "",
                    "gold_ingredient_ids": "|".join(gid) if s1 else "", "gold_next_action": "" if s1 else names,
                    "gold_next_process_id": "" if s1 else gid, "gold_origin": "AI_DRAFTED_GOLD",
                    "gold_source": "AI_DELEGATE_D085", "seen_system_output": "false", "drafted_by": r["drafted_by"],
                    "reviewed_by": REVIEWER, "label": LABEL})
    return out, review


def build_pc() -> tuple[list[dict], list[dict]]:
    drafts, evd = _read(PC_DRAFT), _evd_latest()
    for r in drafts:
        for ids_col, rng_col in (("gold_evd_ids", "gold_retention_range"), ("gold_evd_ids_2", "gold_retention_range_2")):
            if gold_range(r[ids_col], evd) != r[rng_col]:
                raise BuildRefused(f"{r['qid']}: {rng_col} {r[rng_col]!r} != ledger {gold_range(r[ids_col], evd)!r}")
    verdict = {r["qid"]: ("DROP", PC_DROP[r["qid"]]) if r["qid"] in PC_DROP else
               ("KEEP", "gold range rechecked against the EVD ledger") for r in drafts}
    entered, review = _enter(drafts, verdict)
    return [{**r, "gold_origin": "AI_DRAFTED_GOLD", "reviewed_by": REVIEWER, "label": LABEL} for r in entered], review


def build_ux() -> tuple[list[dict], list[dict]]:
    drafts = _read(UX_DRAFT)
    verdict = {r["qid"]: ("KEEP", "expected behaviour as drafted (S178); gold branch set by intent") for r in drafts}
    entered, review = _enter(drafts, verdict)
    return [{**r, "gold_origin": "AI_DRAFTED_GOLD", "reviewed_by": REVIEWER, "label": LABEL} for r in entered], review


def _csv(rows: list[dict]) -> bytes:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def build() -> dict[str, bytes]:
    s, rs = build_s()
    pc, rp = build_pc()
    ux, ru = build_ux()
    return {"S": _csv(s), "PC": _csv(pc), "UX": _csv(ux), "REVIEW": _csv(rs + rp + ru)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the files on disk; write nothing")
    a = ap.parse_args(argv)
    files = build()
    if a.check:
        bad = [k for k, b in files.items() if not OUT[k].exists() or OUT[k].read_bytes() != b]
        print(json.dumps({"check": "OK" if not bad else "DIFFERS", "differs": bad}))
        return 1 if bad else 0
    for k, b in files.items():
        if OUT[k].exists() and OUT[k].read_bytes() != b:
            raise SystemExit(f"refusing to overwrite {OUT[k].relative_to(ROOT)} with different bytes")
        OUT[k].write_bytes(b)
    counts = {k: b.decode().count("\n") - 1 for k, b in files.items()}
    print(json.dumps({"written": {k: str(OUT[k].relative_to(ROOT)) for k in files}, "rows": counts}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
