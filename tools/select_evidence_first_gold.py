#!/usr/bin/env python3
"""S116 evidence-first Gold selection (protocol: annotation/gold/evidence_first_expansion/selection_protocol_v1.md). Deterministic.

  tools/select_evidence_first_gold.py pool     -> candidate_pool_local.csv (LOCAL: has recipe text) + screening_log.csv skeleton (text-free)
  tools/select_evidence_first_gold.py select   -> selection_manifest_v1.csv (+ .sha256) from ELIGIBLE screened candidates (20 PRIMARY + <=10 RESERVE)
Uses only: evidence compatibility, instruction-level ingredient x process match, family dedupe, ingredient / process-family / evidence-source
diversity, annotation feasibility. Never uses B3/B4, NER/compiler errors or scores, or any desired result.
"""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.vocab.foodon import norm  # noqa: E402

D = ROOT / "annotation" / "gold" / "evidence_first_expansion"
CAND = ROOT / "data" / "interim" / "evidence_first" / "foodcom_full_with_spans.csv"
PQ = ROOT / "data" / "external" / "foodcom" / "recipes.parquet"
THERMAL = {"DRY_HEAT", "WET_HEAT", "FAT_HEAT"}
POOL_N, PRIMARY_N, RESERVE_N = 120, 20, 10
POOL_CAPS = {"ingredient": 5, "cell": 6}
FINAL_CAPS = {"ingredient": 3, "cell": 4, "pfam_share": 0.40}
MIN_CUTS, STEP_RANGE, ING_RANGE, MAX_STEP_CHARS = 2, (4, 12), (5, 18), 2500
SCREEN_COLS = ["candidate_id", "source_recipe_id", "recipe_family", "ingredient_id", "ingredient", "process_id", "process", "matched_evidence_ids",
               "automatic_score", "screening_decision", "screening_reason", "reviewer", "timestamp"]
DECISIONS = {"ELIGIBLE", "INELIGIBLE_FALSE_MATCH", "INELIGIBLE_AMBIGUOUS_PROCESS", "INELIGIBLE_DUPLICATE_FAMILY", "INELIGIBLE_NO_MEANINGFUL_CUT", "INELIGIBLE_OTHER"}


def recipe_hash(title, ings, steps) -> str:
    return hashlib.sha256(json.dumps({"title": title, "ingredients": ings, "steps": steps}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def jaccard(a, b) -> float:
    return len(a & b) / len(a | b) if a | b else 0.0


def ingredient_in_text(name: str, text: str) -> bool:
    words = [w for w in re.findall(r"[a-z]+", name.lower()) if len(w) > 2]
    return bool(words) and any(re.search(rf"\b{re.escape(w)}(e?s)?\b", text.lower()) for w in words)


def load_recipes(ids):
    d = pd.read_parquet(PQ, columns=["RecipeId", "Name", "RecipeIngredientQuantities", "RecipeIngredientParts", "RecipeInstructions"])
    d = d[d.RecipeId.astype(int).map(lambda i: f"FC{i}").isin(ids)]
    out = {}
    for rid, name, q, parts, steps in zip(d.RecipeId, d.Name, d.RecipeIngredientQuantities, d.RecipeIngredientParts, d.RecipeInstructions):
        parts, steps = [str(x) for x in parts], [str(x) for x in steps]
        q = [str(x) for x in (q if q is not None else [])]
        lines = [f"{(q[i] if i < len(q) and q[i] != 'None' else '')} {p}".strip() for i, p in enumerate(parts)]
        out[f"FC{int(rid)}"] = {"title": name, "ings": lines, "parts": {norm(p) for p in parts}, "steps": steps}
    return out


def evd_source_map(ids):
    from culinarystate.ledgers.store import LedgerStore
    want = set(ids)
    return {e["id"]: e.get("source_family_id") or e.get("source_id") for e in LedgerStore().all_latest("EVD") if e["id"] in want}


def gain(cells, cov, ings, pfams, srcs, pfam_of, src_of):
    w = 0.0
    for c in cells:
        w += 1 / (1 + cov.get(c, 0)) + 0.5 * (c[0] not in ings) + 0.5 * (pfam_of[c[1]] not in pfams)
        w += 0.5 * len(src_of.get(c, set()) - srcs)
    return w


def greedy(cands, n, caps, pfam_of, src_of, chosen=None, jac_parts=None):
    """cands: {rid: {'cells': [(ing, proc)...], 'fam': str, 'parts': set}} -> list of (rid, cells, gain), deterministic (ties by rid)."""
    chosen = list(chosen or [])
    cov, ings, pfams, srcs = Counter(), set(), set(), set()
    ing_n, pfam_n = Counter(), Counter()
    fams = set()
    picked_parts = []
    for rid, cells, _ in chosen:
        for c in cells:
            cov[c] += 1; ings.add(c[0]); pfams.add(pfam_of[c[1]]); srcs |= src_of.get(c, set()); ing_n[c[0]] += 1; pfam_n[pfam_of[c[1]]] += 1
        fams.add(cands[rid]["fam"]); picked_parts.append(cands[rid]["parts"])
    out = list(chosen)
    while len(out) < n:
        best = None
        for rid in sorted(cands):
            c = cands[rid]
            if any(rid == r for r, _, _ in out) or c["fam"] in fams:
                continue
            if any(jaccard(c["parts"], p) >= 0.8 for p in picked_parts):
                continue
            cells = [x for x in c["cells"] if cov[x] < caps["cell"] and ing_n[x[0]] < caps["ingredient"]]
            if "pfam_share" in caps:
                cells = [x for x in cells if (pfam_n[pfam_of[x[1]]] + 1) / (sum(pfam_n.values()) + 1) <= caps["pfam_share"] + 1e-9 or len(out) < 5]
            if not cells:
                continue
            ranked = sorted(cells, key=lambda x: (-gain([x], cov, ings, pfams, srcs, pfam_of, src_of), x))[:3]
            g = gain(ranked, cov, ings, pfams, srcs, pfam_of, src_of)
            if best is None or g > best[2] + 1e-12:
                best = (rid, ranked, g)
        if best is None:
            break
        rid, cells, g = best
        out.append(best)
        for x in cells:
            cov[x] += 1; ings.add(x[0]); pfams.add(pfam_of[x[1]]); srcs |= src_of.get(x, set()); ing_n[x[0]] += 1; pfam_n[pfam_of[x[1]]] += 1
        fams.add(cands[rid]["fam"]); picked_parts.append(cands[rid]["parts"])
    return out


def build_candidates():
    d = pd.read_csv(CAND, dtype=str)
    d = d[(d.process_family.isin(THERMAL)) & (d.candidate_cut_count.astype(int) >= MIN_CUTS)]
    d = d.drop_duplicates(["recipe_id", "ingredient_id", "process_id"])
    ids = set(d.recipe_id)
    rec = load_recipes(ids)
    src = evd_source_map({e for s in d.evidence_ids for e in s.split("|")})
    src_of = defaultdict(set)
    for r in d.itertuples():
        for e in r.evidence_ids.split("|"):
            if src.get(e):
                src_of[(r.ingredient_id, r.process_id)].add(src[e])
    pfam_of = dict(zip(d.process_id, d.process_family))
    cands, rows = {}, defaultdict(list)
    for r in d.itertuples():
        x = rec.get(r.recipe_id)
        if not x:
            continue
        if not (STEP_RANGE[0] <= len(x["steps"]) <= STEP_RANGE[1] and ING_RANGE[0] <= len(x["ings"]) <= ING_RANGE[1] and sum(map(len, x["steps"])) <= MAX_STEP_CHARS):
            continue
        if any("http" in s.lower() for s in x["steps"]):
            continue
        if not ingredient_in_text(r.ingredient, r.instruction_span or ""):               # instruction-level: the matched sentence must name the ingredient
            continue
        rows[r.recipe_id].append(r)
    for rid, rs in rows.items():
        cands[rid] = {"cells": sorted({(r.ingredient_id, r.process_id) for r in rs}), "fam": rs[0].recipe_family, "parts": rec[rid]["parts"], "rows": rs, "rec": rec[rid]}
    return cands, src_of, pfam_of


ALLOWED_REPLACEMENT_REASONS = {"SOURCE_CORRUPTION", "DUPLICATE_AFTER_FREEZE", "MATCH_PROVEN_FALSE", "NOT_REPRESENTABLE_IN_SCHEMA", "SOURCE_UNAVAILABLE_LOCALLY"}


def replace_primary(manifest_rows, recipe_id: str, reason: str):
    """Replace a PRIMARY by the next RESERVE (selection order) - only for a pre-specified reason; difficulty or model behaviour is never one."""
    if reason not in ALLOWED_REPLACEMENT_REASONS:
        raise ValueError(f"replacement reason {reason!r} not allowed; allowed: {sorted(ALLOWED_REPLACEMENT_REASONS)}")
    ids = sorted({r["selection_id"] for r in manifest_rows if r["source_recipe_id"] == recipe_id and r["selection_role"] == "PRIMARY"})
    if not ids:
        raise ValueError(f"{recipe_id} is not a PRIMARY recipe")
    reserves = sorted({r["selection_id"] for r in manifest_rows if r["selection_role"] == "RESERVE"})
    if not reserves:
        raise ValueError("no reserve left")
    nxt = reserves[0]
    return [{**r, "selection_role": "REPLACED" if r["selection_id"] == ids[0] else "PRIMARY" if r["selection_id"] == nxt else r["selection_role"]} for r in manifest_rows]


def cmd_pool():
    cands, src_of, pfam_of = build_candidates()
    pool = greedy(cands, POOL_N, POOL_CAPS, pfam_of, src_of)
    D.mkdir(parents=True, exist_ok=True)
    local, log = [], []
    for k, (rid, cells, g) in enumerate(pool, 1):
        c = cands[rid]
        for r in c["rows"]:
            if (r.ingredient_id, r.process_id) not in cells:
                continue
            cid = f"EFC-{k:03d}-{r.ingredient_id[-4:]}-{r.process_id[-3:]}"
            local.append({"candidate_id": cid, "source_recipe_id": rid, "title": c["rec"]["title"], "ingredient": r.ingredient, "process": r.process, "matched_step": r.instruction_span,
                          "ingredient_line": next((l for l in c["rec"]["ings"] if ingredient_in_text(r.ingredient, l)), ""), "n_steps": len(c["rec"]["steps"]), "n_ing": len(c["rec"]["ings"])})
            log.append({"candidate_id": cid, "source_recipe_id": rid, "recipe_family": c["fam"], "ingredient_id": r.ingredient_id, "ingredient": r.ingredient,
                        "process_id": r.process_id, "process": r.process, "matched_evidence_ids": r.evidence_ids, "automatic_score": round(g, 3),
                        "screening_decision": "", "screening_reason": "", "reviewer": "", "timestamp": ""})
    pd.DataFrame(local).to_csv(D / "candidate_pool_local.csv", index=False)
    if not (D / "screening_log.csv").exists():                                              # never overwrite a screening in progress
        pd.DataFrame(log, columns=SCREEN_COLS).to_csv(D / "screening_log.csv", index=False)
    print(f"candidates after mechanical filters: {len(cands)} recipes; pool rows {len(log)} over {len(pool)} recipes")


def cmd_select():
    log = pd.read_csv(D / "screening_log.csv", dtype=str).fillna("")
    bad = set(log.screening_decision) - DECISIONS - {""}
    if bad or (log.screening_decision == "").any():
        sys.exit(f"screening incomplete or invalid decisions: {bad or 'blank rows'}")
    elig = log[log.screening_decision == "ELIGIBLE"]
    cands, src_of, pfam_of = build_candidates()
    keep = {}
    for rid, g in elig.groupby("source_recipe_id"):
        cells = sorted({(r.ingredient_id, r.process_id) for r in g.itertuples()})
        if rid in cands:
            keep[rid] = {**cands[rid], "cells": cells}
    chosen = greedy(keep, PRIMARY_N, FINAL_CAPS, pfam_of, src_of)
    chosen = greedy(keep, PRIMARY_N + RESERVE_N, {**FINAL_CAPS, "pfam_share": 1.0}, pfam_of, src_of, chosen=chosen)
    rows = []
    for k, (rid, cells, g) in enumerate(chosen, 1):
        c = cands[rid]
        role = "PRIMARY" if k <= PRIMARY_N else "RESERVE"
        for (iid, pid) in cells:
            ev = sorted({e for r in c["rows"] if (r.ingredient_id, r.process_id) == (iid, pid) for e in r.evidence_ids.split("|")})
            rows.append({"selection_id": f"EFG-{k:03d}", "source_recipe_id": rid, "selection_role": role, "recipe_family": c["fam"], "ingredient_id": iid, "process_id": pid,
                         "matched_evidence_ids": "|".join(ev[:8]), "evidence_tier": "E3", "process_family": pfam_of[pid],
                         "selection_stratum": f"{pfam_of[pid]}|{iid}", "selection_score": round(g, 3),
                         "source_hash": recipe_hash(c["rec"]["title"], c["rec"]["ings"], c["rec"]["steps"]), "licence_status": "CC0_DECLARED_UPLOADER_AUTHORITY_UNVERIFIED",
                         "local_only": "TRUE", "screening_status": "AI_SCREENED_PENDING_HUMAN_CONFIRM"})
    out = D / "selection_manifest_v1.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    (D / "selection_manifest_v1.csv.sha256").write_text(hashlib.sha256(out.read_bytes()).hexdigest() + "  selection_manifest_v1.csv\n")
    prim = [r for r in rows if r["selection_role"] == "PRIMARY"]
    print(f"primary recipes {len({r['source_recipe_id'] for r in prim})}, reserve {len({r['source_recipe_id'] for r in rows if r['selection_role'] == 'RESERVE'})}, rows {len(rows)}")


if __name__ == "__main__":
    {"pool": cmd_pool, "select": cmd_select}[sys.argv[1]]()
