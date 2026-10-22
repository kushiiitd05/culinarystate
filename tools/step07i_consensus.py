#!/usr/bin/env python3
"""STEP 07I part 4: family registry, consensus profiles (support over duplicate-group representatives, so copies never inflate support), field-support table, FK update of the derived recipe base,
view membership, Gold firewall, era/culture provenance. Consumes tools/step07i_identity.py outputs. Consensus is a PROFILE of observed members; no fake recipe is synthesised; no E1-E7 tier is used."""
import argparse
import csv
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
ID = ROOT / "ledgers/recipe_identity"
STATUS_RANK = {"PROCEDURALLY_RICH": 4, "PARTIAL_CONDITIONS": 3, "QUALITATIVE_ONLY": 2, "INSUFFICIENT_CONDITIONS": 1, "UNKNOWN": 0}
USAGE_RANK = {"PUBLIC_OPEN": 5, "REDISTRIBUTABLE_WITH_ATTRIBUTION": 4, "LOCAL_RESEARCH_ONLY": 3, "LICENCE_UNVERIFIED": 2, "UNKNOWN": 1}
REL_RANK = {"NONE": 0, "EXACT_NORMALIZED_COPY": 1, "MIRRORED_COPY": 2, "EXACT_BINARY_COPY": 3}


def level(count, n, conflict=False):
    if conflict:
        return "CONFLICTING"
    if n >= 2 and count == n:
        return "UNANIMOUS"
    f = count / n
    if f >= 0.80:
        return "HIGH_SUPPORT"
    if f >= 0.50:
        return "MAJORITY"
    return "SINGLETON_VARIANT" if count == 1 else "MINORITY_VARIANT"


def era_map(base):
    cat = {}
    for r in csv.DictReader(open(ROOT / "data/raw/gutenberg/pg_catalog.csv", encoding="utf-8")):
        cat[r["Text#"]] = r["Authors"]
    src = {}
    for l in open(ROOT / "ledgers/data/SRC.jsonl", encoding="utf-8"):
        r = json.loads(l)
        m = re.search(r"#(\d+)\)?$", r.get("title", "")) or re.search(r"Gutenberg #(\d+)", r.get("title", ""))
        if m:
            src[r["id"]] = m.group(1)
    out = {}
    for rid, sid, fam in zip(base.recipe_id, base.source_id, base.source_family):
        if fam == "GUTENBERG_SEGMENT":
            a = cat.get(src.get(sid, ""), "")
            m = re.search(r"(\d{4})\??-", a)
            out[rid] = f"AUTHOR_BORN_{(int(m.group(1)) // 50) * 50}s" if m else "UNKNOWN"
    fc = pq.read_table(ROOT / "data/external/foodcom/recipes.parquet", columns=["RecipeId", "DatePublished"]).to_pandas()
    fcy = dict(zip(("FC%d" % int(r) for r in fc.RecipeId), (f"PUBLISHED_{d.year}" if pd.notna(d) else "UNKNOWN" for d in fc.DatePublished)))
    out.update({k: v for k, v in fcy.items() if k in set(base.recipe_id)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true")
    a = ap.parse_args()
    suf = "_sample" if a.sample else ""
    df = pd.read_pickle(ID / f"_identity_work{suf}.pkl")
    reps = pd.read_pickle(ID / f"_reps_work{suf}.pkl")
    feat = pq.read_table(ID / "recipe_identity_features_v1.parquet", columns=["recipe_id", "ing_ids", "proc_seq", "tool_ids", "mass_ing", "mass_g"]).to_pandas().set_index("recipe_id")
    base = pq.read_table(ROOT / "ledgers/recipe_base/recipe_base_v1.parquet").to_pandas()
    if "duplicate_group_id" in base.columns:  # idempotent rerun: drop previous FK columns (legacy ids were saved on first update)
        base = base.drop(columns=["duplicate_group_id", "recipe_family_id", "dish_family_candidate_id", "representative_recipe_id", "family_role", "duplicate_relation", "duplicate_status", "usage_class", "training_allowed", "raw_redistribution_allowed"], errors="ignore")
        base = base.rename(columns={"legacy_family_id": "recipe_family_id", "legacy_family_method": "family_method"})
    ready = pq.read_table(ROOT / "ledgers/recipe_base/recipe_simulation_readiness_v1.parquet", columns=["recipe_id", "readiness_status", "has_time", "has_numeric_temperature", "has_temperature_location", "has_pressure", "has_power", "has_qualitative_heat", "has_endpoint_condition",
                                                                                                      "has_quantity_information", "has_geometry_information", "has_medium_information"]).to_pandas().set_index("recipe_id")
    usage = {r["source_id"]: r for r in csv.DictReader(open(ROOT / "registry/recipe_source_usage_registry_v1.csv", encoding="utf-8"))}
    era = era_map(base)
    reps = reps.set_index("recipe_id", drop=False)
    fam_groups = reps.groupby("recipe_family_id").recipe_id.apply(list)
    multi = fam_groups[fam_groups.map(len) >= 2]
    need = set(r for l in multi for r in l)
    cm = pq.read_table(ROOT / "ledgers/recipe_semantics/recipe_condition_mentions_v1.parquet", columns=["recipe_id", "expression_family", "canonical_value", "qualitative_value", "raw_expression", "measurement_location", "normalized_status"],
                       filters=[("expression_family", "in", ["TEMPERATURE", "TIME", "MEDIUM", "PRESSURE", "POWER", "ENDPOINT"])]).to_pandas()
    cm = cm[cm.recipe_id.isin(need)]
    cmg = {k: g for k, g in cm.groupby("recipe_id")}
    rows_fs = []

    def add(fid, ftype, key, cnt, n, srcs, **kw):
        rows_fs.append({"recipe_family_id": fid, "field_type": ftype, "field_key": str(key), "unit_of_support": "DUPLICATE_GROUP", "group_count": n, "support_count": cnt, "support_fraction": cnt / n, "source_support_count": len(srcs),
                        "support_level": kw.pop("lvl", None) or level(cnt, n), "stat_min": kw.get("mn"), "stat_median": kw.get("md"), "stat_max": kw.get("mx"), "position_mean": kw.get("pos"), "extra": kw.get("extra")})
    for fid, members in multi.items():
        n = len(members)
        sub = reps.loc[members]
        srcof = sub.source_id.to_dict()
        ing_s, proc_s, tool_s, procpos, mass = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(list), defaultdict(list)
        cond = defaultdict(lambda: defaultdict(set))
        for r in members:
            f = feat.loc[r]
            for i in set(f.ing_ids):
                ing_s[i].add(r)
            sq = list(f.proc_seq)
            for k, p in enumerate(sq):
                if r not in proc_s[p]:
                    procpos[p].append(k / max(1, len(sq) - 1))
                proc_s[p].add(r)
            for t in f.tool_ids:
                tool_s[t].add(r)
            for i, m in zip(f.mass_ing, f.mass_g):
                mass[i].append(m)
            g = cmg.get(r)
            if g is not None:
                for fam_, v, q, raw, loc, st in zip(g.expression_family, g.canonical_value, g.qualitative_value, g.raw_expression, g.measurement_location, g.normalized_status):
                    if fam_ == "TEMPERATURE" and pd.notna(v):
                        cond["TEMPERATURE"][f"{loc}:{round(v)}K"].add(r)
                    elif fam_ == "TIME" and pd.notna(v):
                        cond["TIME"][f"{round(v / 60)}min"].add(r)
                    elif fam_ == "MEDIUM":
                        cond["MEDIUM"][str(q).lower().strip()].add(r)
                    elif fam_ == "PRESSURE" and pd.notna(v):
                        cond["PRESSURE"][f"{round(v)}Pa"].add(r)
                    elif fam_ == "POWER" and pd.notna(v):
                        cond["POWER"][f"{round(v)}W"].add(r)
                    elif fam_ == "ENDPOINT":
                        cond["ENDPOINT"][" ".join(str(raw).lower().split()[:2])].add(r)
        for k, s in ing_s.items():
            add(fid, "INGREDIENT", k, len(s), n, {srcof[x] for x in s})
        for k, s in proc_s.items():
            add(fid, "PROCESS", k, len(s), n, {srcof[x] for x in s}, pos=float(np.mean(procpos[k])))
        for k, s in tool_s.items():
            add(fid, "TOOL", k, len(s), n, {srcof[x] for x in s})
        for ft, d in cond.items():
            holders = set().union(*d.values())
            top = max(len(v) for v in d.values())
            conflict = ft in ("TEMPERATURE", "TIME", "PRESSURE", "POWER") and len(d) >= 2 and top / len(holders) < 0.50
            add(fid, ft, "__DISTRIBUTION__", len(holders), n, {srcof[x] for x in holders}, lvl="CONFLICTING" if conflict else level(top, max(len(holders), 1)), extra=json.dumps({"distinct_values": len(d), "top_value_fraction_among_members_with_field": round(top / len(holders), 3)}))
            for k, s in d.items():
                add(fid, ft, k, len(s), n, {srcof[x] for x in s}, lvl="CONFLICTING" if conflict else None)
        for k, v in mass.items():
            add(fid, "QUANTITY_MASS_G", k, len(v), n, set(), mn=min(v), md=statistics.median(v), mx=max(v), extra="mass-grounded values only; no averaging across bases/units")
    fs = pd.DataFrame(rows_fs)
    fs.to_parquet(ID / f"recipe_family_field_support_v1{suf}.parquet", compression="zstd", index=False)
    # ---------------- family registry + consensus (all families) ----------------
    allf = df.groupby("recipe_family_id")
    reg = pd.DataFrame({"n_recipes": allf.size(), "n_duplicate_groups": allf.duplicate_group_id.nunique(), "source_count": allf.source_family.nunique(), "independent_source_count": allf.source_id.nunique(),
                        "family_center_id": allf.family_center_id.first(), "representative_recipe_id": allf.representative_recipe_id.first(), "heterogeneous": allf.heterogeneous.first()})
    reg["family_method"], reg["calibrated"] = "PROVISIONAL_STAR_V1", False
    reg["member_duplicate_certainty"] = allf.duplicate_relation.agg(lambda s: max(REL_RANK.get(x if x != "REPRESENTATIVE" else "EXACT_NORMALIZED_COPY", 0) for x in s))
    reg = reg.reset_index()
    ready_rank = ready.readiness_status.map(STATUS_RANK)
    df["_rr"] = df.recipe_id.map(ready_rank)
    df["_era"] = df.recipe_id.map(era).fillna("UNKNOWN")
    df["_usage"] = df.source_id.map(lambda s: usage.get(s, {}).get("usage_class", "UNKNOWN"))
    df["_ur"] = df._usage.map(USAGE_RANK)
    cons = reg.copy()
    cons["source_families"] = cons.recipe_family_id.map(allf.source_family.agg(lambda s: json.dumps(dict(Counter(s)))))
    cons["locale_dist"] = cons.recipe_family_id.map(allf.locale.agg(lambda s: json.dumps(dict(Counter(s.dropna())))))
    cons["cuisine_dist_explicit"] = cons.recipe_family_id.map(allf.cuisine_if_explicit.agg(lambda s: json.dumps(dict(Counter(s.dropna())))))
    cons["era_dist"] = cons.recipe_family_id.map(allf._era.agg(lambda s: json.dumps(dict(Counter(s)))))
    cons["best_readiness_status"] = cons.recipe_family_id.map(allf._rr.max()).map({v: k for k, v in STATUS_RANK.items()})
    cons["best_usage_class"] = cons.recipe_family_id.map(allf._ur.max()).map({v: k for k, v in USAGE_RANK.items()})
    cons["human_verification_status"] = cons.recipe_family_id.map(allf.has_gold_annotations.max()).map({True: "CONTAINS_GOLD_PENDING_RECORD", False: "UNVERIFIED"})
    cons["mapping_quality"] = cons.recipe_family_id.map(allf.has_ingredients.mean())
    cons["structured_field_coverage"] = cons.recipe_family_id.map(allf.has_conditions.mean())
    sp = fs[fs.field_type == "INGREDIENT"].groupby("recipe_family_id").support_fraction.mean()
    cons["agreement_fraction"] = cons.recipe_family_id.map(sp)
    core = fs[(fs.support_fraction >= 0.5)].groupby(["recipe_family_id", "field_type"]).size().unstack(fill_value=0)
    for ft in ("INGREDIENT", "PROCESS", "TOOL"):
        cons[f"core_{ft.lower()}_count"] = cons.recipe_family_id.map(core[ft]) if ft in core else np.nan
    confl = fs[fs.support_level == "CONFLICTING"].groupby("recipe_family_id").size()
    cons["conflicting_field_count"] = cons.recipe_family_id.map(confl).fillna(0).astype(int)
    cons["unit_of_support"] = "DUPLICATE_GROUP"
    cons["confidence_vector_note"] = "components are reported separately and never multiplied into one truth score; no E1-E7 tier"
    reg.to_parquet(ID / f"recipe_family_registry_v1{suf}.parquet", compression="zstd", index=False)
    cons.to_parquet(ID / f"recipe_family_consensus_v1{suf}.parquet", compression="zstd", index=False)
    # ---------------- recipe base FK update ----------------
    keep = df[["recipe_id", "duplicate_group_id", "recipe_family_id", "dish_family_candidate_id", "representative_recipe_id", "family_role", "duplicate_relation", "duplicate_status", "_usage"]].rename(columns={"_usage": "usage_class"})
    base2 = base.rename(columns={"recipe_family_id": "legacy_family_id", "family_method": "legacy_family_method"}).merge(keep, on="recipe_id", how="left", validate="1:1")
    base2["training_allowed"] = base2.source_id.map(lambda s: usage.get(s, {}).get("training_allowed", "UNKNOWN"))
    base2["raw_redistribution_allowed"] = base2.source_id.map(lambda s: usage.get(s, {}).get("raw_redistribution_allowed", "UNKNOWN"))
    if not a.sample:
        pq.write_table(pa.Table.from_pandas(base2, preserve_index=False), ROOT / "ledgers/recipe_base/recipe_base_v1.parquet", compression="zstd")
    # ---------------- views ----------------
    missing_raw = base2.annotation_status.eq("RAW_SEGMENT_MISSING_LOCALLY")
    v = pd.DataFrame({"recipe_id": base2.recipe_id, "usage_class": base2.usage_class, "in_SOURCE_ALL": True, "in_EXACT_DEDUP": base2.recipe_id == base2.duplicate_group_id.map(df.set_index("duplicate_group_id").group_representative_id[~df.set_index("duplicate_group_id").index.duplicated()]),
                      "is_family_representative": base2.recipe_id == base2.representative_recipe_id, "in_MODEL_ELIGIBLE": (base2.training_allowed == "YES") & ~missing_raw, "in_RELEASE_ELIGIBLE": (base2.raw_redistribution_allowed == "YES") & ~missing_raw,
                      "in_RELEASE_CONDITIONAL": (base2.raw_redistribution_allowed == "CONDITIONAL") & ~missing_raw, "in_LOCAL_ANALYSIS": ~missing_raw, "in_GOLD": base2.has_gold_annotations & base2.quality_tier.eq("GOLD_PENDING_INDEPENDENT_IAA")})
    v.to_parquet(ID / f"recipe_view_membership_v1{suf}.parquet", compression="zstd", index=False)
    # ---------------- Gold firewall ----------------
    gold = pq.read_table(ROOT / "ledgers/recipe_base/gold_recipe_index_v1.parquet").to_pandas()
    di = df.set_index("recipe_id")
    gf = []
    for rid, st in zip(gold.recipe_id, gold.gold_status):
        if rid not in di.index:
            continue
        g, f_ = di.loc[rid, "duplicate_group_id"], di.loc[rid, "recipe_family_id"]
        same_g = df[(df.duplicate_group_id == g) & (df.recipe_id != rid)]
        same_f = df[(df.recipe_family_id == f_) & (df.recipe_id != rid) & (df.duplicate_group_id != g)]
        gf.append({"gold_recipe_id": rid, "gold_status": st, "duplicate_group_id": g, "recipe_family_id": f_, "same_group_members": len(same_g), "same_group_non_gold": int((same_g.quality_tier != "GOLD_PENDING_INDEPENDENT_IAA").sum()), "same_family_other_group_members": len(same_f),
                   "cross_source_relatives": int((same_g.source_family != di.loc[rid, "source_family"]).sum() + (same_f.source_family != di.loc[rid, "source_family"]).sum()), "split_lock_group_id": g,
                   "relative_ids_sample": json.dumps((list(same_g.recipe_id[:3]) + list(same_f.recipe_id[:3])))})
    gfd = pd.DataFrame(gf)
    gfd.to_parquet(ID / f"gold_firewall_v1{suf}.parquet", compression="zstd", index=False)
    out = {"families_total": int(len(reg)), "multi_member_families_over_recipes": int((reg.n_recipes > 1).sum()), "multi_group_families": int((reg.n_duplicate_groups > 1).sum()), "field_support_rows": int(len(fs)), "families_with_field_support": int(fs.recipe_family_id.nunique()),
           "families_with_conflicts": int((cons.conflicting_field_count > 0).sum()), "heterogeneous_families": int(reg.heterogeneous.sum()), "gold_firewall": {"gold_in_index": len(gfd), "gold_with_same_group_non_gold_members": int((gfd.same_group_non_gold > 0).sum()), "gold_with_family_relatives": int((gfd.same_family_other_group_members > 0).sum())},
           "views": {c: int(v[c].sum()) for c in v.columns if c.startswith("in_") or c.startswith("is_")}, "era_known_recipes": int((df._era != "UNKNOWN").sum())}
    (ROOT / f"reports/step07i/_consensus_summary{suf}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
