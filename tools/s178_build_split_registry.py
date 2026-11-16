#!/usr/bin/env python
"""S178 (T9-C09-R1): build and hash registry/split_registry_v1.csv for the three evaluations that will run.

Evaluations: D5 benchmark questions (S1/S2 recipes, P1-P3/C cells; drafts), the 29-diag splits S-1..S-5 (DEL-2 split
generators on the EVD ledger, pre-seal) and the 07.A-R1 packet (recomputed from the ledgers, checked byte for byte
against the issued manifest). Ids and hashes only. Refuses to overwrite: a changed evaluation set is a new registry
version, not an edit. Also writes reports/s178/split_registry_units_v1.csv (D5 and 07.A unit ids) and
reports/s178/split_registry_report.json (counts, checks, cross-evaluation overlaps).

    python tools/s178_build_split_registry.py
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evaluation import split_registry as SR  # noqa: E402
from culinarystate.evidence import condition_audit_packet as P  # noqa: E402
from culinarystate.evidence import condition_normalizer as N  # noqa: E402
from culinarystate.transition.dataset import cells_from_rows  # noqa: E402
from culinarystate.transition.splits import all_splits, leakage  # noqa: E402

REGISTRY = ROOT / "registry/split_registry_v1.csv"
UNITS = ROOT / "reports/s178/split_registry_units_v1.csv"
REPORT = ROOT / "reports/s178/split_registry_report.json"
S_DRAFT, PC_DRAFT = ROOT / "benchmark/d5/d5_draft_S_v1.csv", ROOT / "benchmark/d5/d5_draft_PC_v1.csv"
FREEZE = ROOT / "registry/freezes/15A-BOOT-2026-11-08.json"
V4_COPY = ROOT / "annotation/condition_audit/parv_v4_csv_20261027_2f1714.txt"
R1_MANIFEST = ROOT / "reports/step07/07A_R1_packet_manifest.json"
DIAG_SEED = 7                                    # diag29_runner.run(..., seed=7) and tools/run_del2.py default
PREREG_SPLITS = {"random": "S-1", "pair_holdout": "S-2", "matrix_disjoint": "S-3", "process_disjoint": "S-4",
                 "study_disjoint": "S-5"}
CODE_S, CODE_PC = ROOT / "tools/d5_draft_s.py", ROOT / "tools/d5_draft_pc.py"
D5_PLANNED_ENTER = {"S1": 15, "S2": 15, "P1": 10, "P2": 10, "P3": 10, "C": 10, "U": 5, "X": 5}   # prereg s1, s3


def latest(name: str) -> dict:
    out = {}
    with open(ROOT / f"ledgers/data/{name}.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r
    return out


def read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def const(path: Path, name: str) -> str:
    m = re.search(rf'^{name}\s*=\s*"([^"]+)"', path.read_text(encoding="utf-8"), re.M)
    if not m:
        raise SystemExit(f"constant {name} not found in {path}")
    return m.group(1)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def d5_rows(units: list[dict], report: dict) -> list[dict]:
    s_rows, pc_rows = read(S_DRAFT), read(PC_DRAFT)
    seed = const(CODE_S, "SEED")
    assert seed == const(CODE_PC, "SEED"), "S and PC drafts use different seeds"
    rows = []
    checks = {}
    # ---- S blocks
    s_recipes = {b: [r["recipe_id"] for r in s_rows if r["block"] == b] for b in ("S1", "S2")}
    all_s = s_recipes["S1"] + s_recipes["S2"]
    s_ok = {"one_recipe_per_question": len(all_s) == len(set(all_s)),
            "s1_s2_recipe_overlap": SR.disjoint_report(s_recipes),
            "families_allowed_only": all(r["source_family"] in ("WIKIBOOKS", "GUTENBERG_SEGMENT") for r in s_rows),
            "min_4_steps": all(int(r["n_steps"]) >= 4 for r in s_rows),
            "cut_in_range": all(2 <= int(r["cut_after_step"]) <= int(r["n_steps"]) - 1 for r in s_rows)}
    checks["S"] = s_ok
    for b in ("S1", "S2"):
        br = [r for r in s_rows if r["block"] == b]
        fams = Counter(r["source_family"] for r in br)
        rows.append(SR.make_row(
            registry_id=f"SPL-D5-{b}", evaluation="D5_BENCHMARK", block_or_split=b, split_unit="RECIPE",
            n_units=len(br), roles=f"drafted={len(br)}|planned_to_enter={D5_PLANNED_ENTER[b]}",
            ids_sha256=SR.ids_sha256(r["qid"] for r in br), unit_ids_sha256=SR.ids_sha256(r["recipe_id"] for r in br),
            seed=seed, seed_rule="WIKIBOOKS+GUTENBERG_SEGMENT, >=4 steps, <=3000 chars; rank = sha256(seed||recipe_id) "
                                 "ascending; cut = 2 + sha256(seed||recipe_id) mod (n_steps-2); first drafted per block by rank",
            source_artifact=rel(S_DRAFT), source_sha256=SR.sha256_file(S_DRAFT), code_artifact=rel(CODE_S),
            code_sha256=SR.sha256_file(CODE_S), status="DRAFT_UNFROZEN",
            checks="; ".join(f"{k}={v}" for k, v in s_ok.items()),
            notes=f"families {dict(sorted(fams.items()))}; AI-drafted engine gold (gold_origin ENGINE_DRAFT); "
                  "ids change when review drops/edits questions"))
        units += [{"registry_id": f"SPL-D5-{b}", "unit_id": r["qid"], "role": "draft",
                   "attributes": f"recipe_id={r['recipe_id']};family={r['source_family']};cut_after_step={r['cut_after_step']}"}
                  for r in br]
    # ---- P/C blocks
    def cell_key(r):
        return "|".join([r["ingredient_id"], r["process_id"], r["process_id_2"], r["target"]])
    for b in ("P1", "P2", "P3", "C"):
        br = [r for r in pc_rows if r["block"] == b]
        ing = Counter(r["ingredient_id"] for r in br)
        rows.append(SR.make_row(
            registry_id=f"SPL-D5-{b}", evaluation="D5_BENCHMARK", block_or_split=b, split_unit="CELL",
            n_units=len(br), roles=f"drafted={len(br)}|planned_to_enter={D5_PLANNED_ENTER[b]}",
            ids_sha256=SR.ids_sha256(r["qid"] for r in br), unit_ids_sha256=SR.ids_sha256(cell_key(r) for r in br),
            seed=seed, seed_rule="cell = ingredient|process|target; stratum DIRECT/SIMILAR_ONLY/NONE from EVD pairs; "
                                 "pick = smallest sha256(seed||cell) per stratum, quota 15, max 2 per ingredient",
            source_artifact=rel(PC_DRAFT), source_sha256=SR.sha256_file(PC_DRAFT), code_artifact=rel(CODE_PC),
            code_sha256=SR.sha256_file(CODE_PC), status="DRAFT_UNFROZEN",
            checks=f"distinct_ingredients={len(ing)};max_per_ingredient={max(ing.values())};"
                   f"strata={dict(sorted(Counter(r['stratum'] for r in br).items()))}",
            notes="AI-drafted; first 10 by rank enter after review (prereg s3)"))
        units += [{"registry_id": f"SPL-D5-{b}", "unit_id": r["qid"], "role": "draft",
                   "attributes": f"cell={cell_key(r)};stratum={r['stratum']};gold_mode={r['gold_mode']}"} for r in br]
    p_all = [r for r in pc_rows if r["block"] in ("P1", "P2", "P3", "C")]
    unique = all(len({cell_key(r) for r in pc_rows if r["block"] == b}) == sum(r["block"] == b for r in pc_rows)
                 for b in ("P1", "P2", "P3", "C"))
    checks["PC"] = {"distinct_ingredients": len({r["ingredient_id"] for r in p_all}),
                    "distinct_processes": len({r["process_id"] for r in p_all} | {r["process_id_2"] for r in p_all if r["process_id_2"]}),
                    "cells_unique_within_block": unique, "prereg_floor": ">=8 ingredients and >=4 processes"}
    for b in ("U", "X"):
        rows.append(SR.make_row(
            registry_id=f"SPL-D5-{b}", evaluation="D5_BENCHMARK", block_or_split=b, split_unit="QUESTION", n_units=0,
            roles=f"drafted=0|planned_to_enter={D5_PLANNED_ENTER[b]}", ids_sha256=SR.ids_sha256([]), seed=seed,
            seed_rule="not drafted", source_artifact="reports/del5/d5_benchmark_preregistration_DRAFT.md",
            source_sha256=SR.sha256_file(ROOT / "reports/del5/d5_benchmark_preregistration_DRAFT.md"),
            status="NOT_DRAFTED", notes="prereg s1 composition lists this block; no draft file exists yet"))
    report["d5"] = {"checks": checks, "n_s": len(s_rows), "n_pc": len(pc_rows)}
    return rows


def diag_rows(report: dict) -> tuple[list[dict], dict]:
    evd, cond = latest("EVD"), latest("COND")
    active = [r for r in evd.values() if r["status"] == "ACTIVE"]
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    snap = {k: ("MATCH" if SR.sha256_file(ROOT / k) == v else "MISMATCH")
            for k, v in freeze["ledger_sha256"].items() if k.startswith("ledgers/data/")}
    evd_sha = SR.sha256_file(ROOT / "ledgers/data/EVD.jsonl")
    rows, pool = [], {}
    for fam in sorted({r["source_family_id"] for r in active}):
        df = cells_from_rows(active, cond, fam).df
        if not len(df):
            continue
        splits, notes = all_splits(df, DIAG_SEED)
        got = {s.name for s in splits}
        del2 = {}
        p = ROOT / f"reports/del2/{fam}_results.json"
        if p.exists():
            for r in json.loads(p.read_text())["results"]:
                del2.setdefault(r.get("split") or r.get("split_name"), r["split_sha256"])
        pool[fam] = set(df["evd_id"])
        for name, sx in PREREG_SPLITS.items():
            rid = f"SPL-29D-{fam}-{sx}-{name}"
            common = dict(registry_id=rid, evaluation="DIAG29", block_or_split=f"{sx}:{name}", source_family=fam,
                          split_unit="EVD_ROW", seed=DIAG_SEED, source_artifact="ledgers/data/EVD.jsonl+COND.jsonl",
                          source_sha256=evd_sha, code_artifact="src/culinarystate/transition/splits.py",
                          code_sha256=SR.sha256_file(ROOT / "src/culinarystate/transition/splits.py"),
                          snapshot_id=freeze["snapshot_id"], status="PROVISIONAL_PRE_SEAL")
            if name not in got:
                rows.append(SR.make_row(**common, n_units=0, ids_sha256=SR.ids_sha256([]), roles="not_possible",
                                        seed_rule="transition.splits.study_disjoint refuses (single source family / giant component)",
                                        checks="NOT_POSSIBLE",
                                        notes="prereg S-5 is food-group disjoint; the runner implements study_disjoint instead (see report)"))
                continue
            s = next(x for x in splits if x.name == name)
            ids = df["evd_id"].to_numpy()
            pairs = [(ids[i], role) for role, idx in (("train", s.train), ("cal", s.cal), ("test", s.test)) for i in idx]
            lk = leakage(df, s, ["group", "study", "matrix", "process"])
            match = ("DEL2_SPLIT_SHA_MATCH" if del2.get(name) == s.sha256()[:16] else
                     "DEL2_SPLIT_SHA_NOT_COMPARABLE" if not del2 else "DEL2_SPLIT_SHA_DIFFERS")
            rows.append(SR.make_row(
                **common, n_units=len(pairs), roles=f"train={len(s.train)}|cal={len(s.cal)}|test={len(s.test)}",
                ids_sha256=SR.assignment_sha256(pairs), unit_ids_sha256=SR.ids_sha256(ids),
                seed_rule="transition.splits.all_splits(df, seed): numpy default_rng permutation of groups (random: rows); "
                          "cal 15 %, test 20 %",
                checks=f"{match};test_share_seen_in_train=" + ",".join(f"{k}:{v}" for k, v in lk.items()),
                notes=f"split_sha256_16={s.sha256()[:16]}; pre-seal (no 15a.R sealed list here); rebuild after the seal removes "
                      "RESERVED cells; rows are the 17,978 ACTIVE EVD rows DEL-2 already used (PRIOR_EXPOSURE_REANALYSIS)"))
    report["diag29"] = {"snapshot_hash_check": snap, "families": sorted(pool),
                        "prereg_vs_runner": {"S-5": "prereg says food-group disjoint; runner builds study_disjoint (possible only "
                                                    "for PHENOL-EXPLORER-3.6)",
                                             "grouping": "prereg says all splits grouped by independence_group; runner groups "
                                                         "S-2/S-3/S-4 by matrix/process keys and only S-5 by study component"},
                        "n_rows_by_family": {f: len(v) for f, v in pool.items()}}
    return rows, pool


def r1_rows(units: list[dict], report: dict) -> list[dict]:
    cond, evd = latest("COND"), latest("EVD")
    fam, ctx = P.evd_context(evd)
    v4 = read(V4_COPY)
    excluded = frozenset(r["condition_id"] for r in v4)
    man = json.loads(R1_MANIFEST.read_text(encoding="utf-8"))
    pool: dict[str, list[str]] = {}
    for cid in sorted(fam):
        if cid in cond:
            pool.setdefault(P.stratum(cond[cid]), []).append(cid)
    sample = P.select(pool, seed=P.SEED_R1, exclude=excluded)
    fp12 = N.fingerprint()["combined_sha256"][:12]
    built = [P.build_row(i, s, cid, cond[cid], fam, ctx, fp12) for i, (s, cid) in enumerate(sample, 1)]
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=P.COLS + P.REV)
    w.writeheader()
    w.writerows(built)
    packet_sha = SR.sha256_bytes(("﻿" + buf.getvalue()).encode("utf-8"))
    ids_sha = SR.ids_sha256(c for _, c in sample)
    ok = {"excluded_set_sha256_matches_manifest": SR.ids_sha256(excluded) == man["excluded_set_sha256"],
          "packet_bytes_reproduced": packet_sha == man["sha256_packet_Kush"] == man["sha256_packet_Parv"],
          "pool_sizes_match": {k: len(v) for k, v in sorted(pool.items())} == man["pool_sizes"],
          "selected_by_stratum_match": {s: sum(1 for a, _ in sample if a == s) for s in P.QUOTA} == man["selected_by_stratum"],
          "source_family_counts_match": dict(Counter(r["source_family"] for r in built)) == man["source_family_counts"],
          "overlap_with_v4": len(excluded & {c for _, c in sample})}
    if not (all(v for k, v in ok.items() if k != "overlap_with_v4") and ok["overlap_with_v4"] == 0):
        raise SystemExit(f"07.A-R1 reproduction failed: {ok}")
    report["r1"] = {**ok, "packet_sha256": packet_sha, "selected_ids_sha256": ids_sha, "n": len(sample)}
    rows = [SR.make_row(
        registry_id="SPL-07AR1-PACKET", evaluation="07A_R1", block_or_split="packet_100", split_unit="CONDITION", n_units=100,
        roles="audit=100", ids_sha256=ids_sha, unit_ids_sha256=ids_sha, seed=P.SEED_R1,
        seed_rule="condition_audit_packet.select: quota per stratum S1-S6, smallest sha256 rank, v4 conditions excluded",
        source_artifact=rel(R1_MANIFEST), source_sha256=SR.sha256_file(R1_MANIFEST),
        code_artifact="src/culinarystate/evidence/condition_audit_packet.py",
        code_sha256=SR.sha256_file(ROOT / "src/culinarystate/evidence/condition_audit_packet.py"),
        status="PACKET_ISSUED_DRAFT",
        checks="; ".join(f"{k}={v}" for k, v in ok.items()),
        notes=f"packet csv sha256 {packet_sha} recomputed in memory = manifest; source mix "
              f"{dict(sorted(Counter(r['source_family'] for r in built).items()))}; audited_by_humans false"),
        SR.make_row(
        registry_id="SPL-07AR1-EXCLUDED-V4", evaluation="07A_R1", block_or_split="excluded_v4_100", split_unit="CONDITION",
        n_units=100, roles="excluded=100", ids_sha256=SR.ids_sha256(excluded), unit_ids_sha256=SR.ids_sha256(excluded),
        seed="n/a", seed_rule="the 100 conditions of the failed 07.A v4 packet, excluded from R1 (R-20: the v4 FAIL stays on record)",
        source_artifact=rel(V4_COPY), source_sha256=SR.sha256_file(V4_COPY), status="PACKET_ISSUED_DRAFT",
        checks=f"matches manifest excluded_set_sha256={ok['excluded_set_sha256_matches_manifest']}",
        notes="text copy of the v4 packet (git-tracked); condition ids only are listed")]
    units += [{"registry_id": "SPL-07AR1-PACKET", "unit_id": cid, "role": "audit",
               "attributes": f"audit_id=CA-{i:03d};stratum={s};family={b['source_family']}"}
              for i, ((s, cid), b) in enumerate(zip(sample, built), 1)]
    units += [{"registry_id": "SPL-07AR1-EXCLUDED-V4", "unit_id": c, "role": "excluded", "attributes": ""} for c in sorted(excluded)]
    report["_r1_ids"] = {c for _, c in sample}
    return rows


def main() -> int:
    for p in (REGISTRY, UNITS, REPORT):
        if p.exists():
            sys.exit(f"refusing to overwrite {p}; a changed evaluation set is a new registry version")
    report: dict = {"tool": "tools/s178_build_split_registry.py", "module": SR.VERSION}
    units: list[dict] = []
    rows = d5_rows(units, report)
    drows, pool = diag_rows(report)
    rows += drows
    rows += r1_rows(units, report)
    # cross-evaluation counts (D5 gold evidence vs the other two evaluations)
    gold = set()
    for r in read(PC_DRAFT):
        for k in ("gold_evd_ids", "gold_evd_ids_2"):
            gold |= {x for x in r[k].split("|") if x}
    evd = latest("EVD")
    conds = {evd[i]["process"].get("condition_id") for i in gold if i in evd} - {None}
    report["cross"] = {"d5_gold_evd_ids": len(gold),
                       "d5_gold_evd_ids_in_diag29_pool_pre_seal": len(gold & set().union(*pool.values())),
                       "d5_gold_evd_conditions": len(conds), "d5_gold_conditions_in_07ar1_packet": len(conds & report.pop("_r1_ids"))}
    UNITS.parent.mkdir(parents=True, exist_ok=True)
    hashes = SR.write_registry(rows, units, REGISTRY, UNITS)
    findings = SR.verify_registry(REGISTRY, UNITS)
    report["verify_findings"] = findings
    report["n_rows"], report["n_units_listed"] = len(rows), len(units)
    report.update(hashes)
    with open(REPORT, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(report, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({**hashes, "report_sha256": hashlib.sha256(REPORT.read_bytes()).hexdigest(), "n_rows": len(rows),
                      "verify_findings": findings}))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
