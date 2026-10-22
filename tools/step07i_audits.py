#!/usr/bin/env python3
"""STEP 07I part 5: ingredient / process / tool / quantity / condition / readiness / culture / bias audits and the final statistics package + ledger-graph impact matrix.
Consumes the frozen 07H-R ledgers and the 07I identity outputs. Read-only on every canonical ledger."""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
RS, RB, ID = ROOT / "ledgers/recipe_semantics", ROOT / "ledgers/recipe_base", ROOT / "ledgers/recipe_identity"
R = ROOT / "reports/step07i"
Q = lambda s: {k: (float(v) if isinstance(v, (int, float, np.floating, np.integer)) else v) for k, v in s.items()}
quant = lambda s: Q(s.quantile([0, .25, .5, .75, .9, .99, 1]).round(2).to_dict()) if len(s) else {}
pct = lambda a, b: round(100 * a / b, 2) if b else None


def led(name):
    d = {}
    for l in open(ROOT / f"ledgers/data/{name}.jsonl", encoding="utf-8"):
        r = json.loads(l)
        d[r["id"]] = r
    return d


def ingredient_audit(base):
    m = pq.read_table(RS / "recipe_ingredient_mentions_v1.parquet", columns=["recipe_id", "source_family", "raw_span", "candidate_ingredient_id", "link_status", "link_method"]).to_pandas()
    ing, alias = led("ING"), led("ALIAS")
    act_ing = {k for k, v in ing.items() if v["status"] == "ACTIVE"}
    out = {"total_mentions": len(m), "mentions_by_source": m.source_family.value_counts().to_dict()}
    m["raw_l"] = m.raw_span.str.lower().str.strip()
    out["unique_raw_ingredient_strings"] = int(m.raw_l.nunique())
    out["canonical_ING_active"] = len(act_ing)
    out["canonical_ING_matched_distinct"] = int(m[m.link_status.isin(["ACCEPT", "REVIEW"])].candidate_ingredient_id.nunique())
    out["alias_active"] = sum(1 for v in alias.values() if v["status"] == "ACTIVE")
    out["alias_exact_lookup_hits"] = int((m.link_method == "ALIAS_EXACT_LOOKUP").sum())
    out["alias_distinct_surface_forms_matched"] = int(m[m.link_method.str.startswith("ALIAS_EXACT")].raw_l.nunique())
    st = m.link_status.value_counts()
    nt = len(m)
    out["status_counts"] = st.to_dict()
    out["mapped_rate_pct(ACCEPT)"], out["ambiguous_review_rate_pct"], out["unmapped_rate_pct"] = pct(st.get("ACCEPT", 0), nt), pct(st.get("REVIEW", 0), nt), pct(st.get("UNRESOLVED", 0), nt)
    out["status_by_source_pct"] = {s: {k: pct(v, len(g)) for k, v in g.link_status.value_counts().items()} for s, g in m.groupby("source_family")}
    un = m[m.link_status == "UNRESOLVED"]
    g = un.groupby("raw_l").agg(mentions=("recipe_id", "size"), recipes=("recipe_id", "nunique"), sources=("source_family", "nunique")).sort_values("mentions", ascending=False)
    top = g.head(1000).reset_index()
    top.insert(0, "rank", range(1, len(top) + 1))
    top["proposed_action"] = "REVIEW_FOR_ALIAS_OR_NEW_ING (no automatic ING creation)"
    top.to_csv(R / "high_priority_unmapped_ingredients.csv", index=False)
    tot_un = int(g.mentions.sum())
    out["unmapped_unique_strings"] = int(len(g))
    out["unmapped_coverage_top100_pct"] = pct(int(g.mentions.head(100).sum()), tot_un)
    out["unmapped_coverage_top1000_pct"] = pct(int(g.mentions.head(1000).sum()), tot_un)
    out["unmapped_long_tail_strings_with_count_le_5"] = int((g.mentions <= 5).sum())
    out["unmapped_long_tail_mentions_share_pct"] = pct(int(g.mentions[g.mentions <= 5].sum()), tot_un)
    mm = m[m.link_status.isin(["ACCEPT", "REVIEW"]) & m.candidate_ingredient_id.notna()]
    name = {k: v["canonical_name"] for k, v in ing.items()}
    out["top_ingredients_global"] = [[name.get(k, k), int(v)] for k, v in mm.candidate_ingredient_id.value_counts().head(25).items()]
    out["top_ingredients_by_source"] = {s: [[name.get(k, k), int(v)] for k, v in g_.candidate_ingredient_id.value_counts().head(8).items()] for s, g_ in mm.groupby("source_family")}
    per = m.groupby("recipe_id").size()
    base_idx = base.set_index("recipe_id")
    out["ingredient_mentions_per_recipe"] = quant(per)
    out["ingredient_mentions_per_recipe_by_source"] = {s: quant(per[per.index.isin(g_.recipe_id)]) for s, g_ in base.groupby("source_family")}
    return out, m


def process_audit(base):
    p = pq.read_table(RS / "recipe_process_mentions_v1.parquet", columns=["recipe_id", "raw_action", "candidate_proc_id", "mapping_status", "proc_kind"]).to_pandas()
    proc = led("PROC")
    nm = {k: v["canonical_name"] for k, v in proc.items()}
    fam = {k: v.get("family") for k, v in proc.items()}
    p["src"] = p.recipe_id.map(base.set_index("recipe_id").source_family)
    p["raw_l"] = p.raw_action.str.lower()
    out = {"process_mentions": len(p), "unique_raw_action_phrases": int(p.raw_l.nunique()), "canonical_PROC_active": sum(1 for v in proc.values() if v["status"] == "ACTIVE"), "canonical_PROC_matched_distinct": int(p.candidate_proc_id.nunique()),
           "mapping_status": p.mapping_status.value_counts().to_dict()}
    mp = p[p.candidate_proc_id.notna()]
    out["mapped_rate_pct"], out["unmapped_rate_pct"] = pct(len(mp), len(p)), pct(len(p) - len(mp), len(p))
    out["note"] = "mapped = verb-form candidate match to PROC (POS unchecked); UNMAPPED = leading token of a sentence with no PROC match"
    mp = mp.assign(fam=mp.candidate_proc_id.map(fam))
    out["process_family_coverage_pct_of_mapped"] = pct(int(mp.fam.notna().sum()), len(mp))
    out["mentions_by_PROC_family"] = mp.fam.value_counts().to_dict()
    out["top_processes"] = [[nm.get(k, k), int(v)] for k, v in mp.candidate_proc_id.value_counts().head(25).items()]
    out["top_processes_by_source"] = {s: [[nm.get(k, k), int(v)] for k, v in g.candidate_proc_id.value_counts().head(6).items()] for s, g in mp.groupby("src")}
    seq = mp.groupby("recipe_id").size()
    out["mapped_process_mentions_per_recipe"] = quant(seq)
    allr = set(base.recipe_id)
    out["recipes_with_no_mapped_process"] = int(len(allr - set(seq.index)))
    un = p[p.candidate_proc_id.isna()].groupby("raw_l").agg(mentions=("recipe_id", "size"), recipes=("recipe_id", "nunique")).sort_values("mentions", ascending=False).head(1000).reset_index()
    un.insert(0, "rank", range(1, len(un) + 1))
    un.to_csv(R / "high_frequency_unmapped_processes.csv", index=False)
    return out, mp


def tool_audit(base, mp):
    t = pq.read_table(RS / "recipe_tool_mentions_v1.parquet").to_pandas()
    cm = pd.read_csv(ROOT / "registry/recipe_tool_structural_class_map_v1.csv").set_index("tool_id")
    t["cls"] = t.tool_id.map(cm.structural_class)
    nm = cm.canonical_name.to_dict()
    out = {"tool_mentions": len(t), "canonical_TOOL_active": len(cm), "canonical_TOOL_matched_distinct": int(t.tool_id.nunique()), "recipes_with_tool_mention": int(t.recipe_id.nunique()), "structural_class_mentions": t.cls.value_counts().to_dict(),
           "structural_class_vocabulary": cm.structural_class.value_counts().to_dict(), "top_tools": [[nm.get(k, k), int(v)] for k, v in t.tool_id.value_counts().head(20).items()],
           "top_appliances": [[nm.get(k, k), int(v)] for k, v in t[t.cls.isin(["HEATING_APPLIANCE", "COOLING_APPLIANCE", "MECHANICAL_APPLIANCE", "PRESSURE_EQUIPMENT"])].tool_id.value_counts().head(10).items()],
           "mapped_rate_note": "tool mentions are lexicon matches (mapped by construction); the unmapped rate is estimated by the review queue below from a text sample"}
    t["src"] = t.recipe_id.map(base.set_index("recipe_id").source_family)
    out["tool_mentions_by_source_per_1000_recipes"] = {s: round(1000 * len(g) / (base.source_family == s).sum(), 1) for s, g in t.groupby("src")}
    # tool-process co-occurrence within the same instruction step
    tt = t[t.step_index.notna()][["recipe_id", "step_index", "tool_id"]].drop_duplicates()
    pp = mp[["recipe_id", "candidate_proc_id"]].copy()
    pr = pq.read_table(RS / "recipe_process_mentions_v1.parquet", columns=["recipe_id", "instruction_index", "candidate_proc_id"]).to_pandas()
    pr = pr[pr.candidate_proc_id.notna()].drop_duplicates()
    j = tt.merge(pr, left_on=["recipe_id", "step_index"], right_on=["recipe_id", "instruction_index"])
    pn = {k: v["canonical_name"] for k, v in led("PROC").items()}
    co = j.groupby(["tool_id", "candidate_proc_id"]).size().sort_values(ascending=False).head(25)
    out["top_tool_process_cooccurrence"] = [[nm.get(a, a), pn.get(b, b), int(v)] for (a, b), v in co.items()]
    return out


def tool_queue(cm_names):
    from culinarystate.recipes import corpus as C
    suf = r"pan|pot|bowl|dish|tin|tray|sheet|skillet|wok|jar|bottle|bag|basin|cooker|processor|blender|mixer|grinder|sieve|colander|strainer|grill|griddle|kettle|steamer|oven|fryer|board|knife|spoon|whisk|spatula|ladle|jug|container|casserole|ramekin|mould|mold|machine|thermometer|scales|press|mortar|pestle|rack|cloth|foil|paper"
    rx = re.compile(rf"\b(?:in|into|using|with|on|onto|over|to)\s+(?:a|an|the|your|each)?\s*((?:[a-z\-]+\s+){{0,2}}(?:{suf}))\b", re.I)
    cnt, n = Counter(), 0
    import itertools
    its = [C.iter_rec_corpora(C.rec_latest(), ("A1_BBC_GOOD_FOOD", "WIKIBOOKS")), itertools.islice(C.iter_foodcom(), 60000)]
    for it in its:
        for rec in it:
            n += 1
            for s in rec["steps"]:
                for m in rx.finditer(s):
                    cnt[m.group(1).lower().strip()] += 1
    known = {w.lower() for w in cm_names}
    rows = [(k, v) for k, v in cnt.most_common(600) if k not in known and k.split()[-1] not in {x.split()[-1] for x in known}]
    pd.DataFrame(rows, columns=["candidate_phrase", "count_in_sample"]).head(300).to_csv(R / "tool_review_queue.csv", index=False)
    return {"sample_recipes_scanned": n, "candidate_noun_phrases_distinct": len(cnt), "phrases_with_unknown_head_noun_in_queue": len(rows)}


def quantity_audit():
    q = pq.read_table(RS / "recipe_quantity_mentions_v1.parquet", columns=["source_family", "parse_kind", "number", "range_low", "unit_key", "unit_raw", "multiplier", "package_key", "qualitative_amount", "mass_status", "volume_status", "count_status", "conversion_method", "flags", "locale_used", "q_level"]).to_pandas()
    n = len(q)
    present = q.parse_kind != "NONE"
    out = {"quantity_lines": n, "parse_kind": q.parse_kind.value_counts().to_dict(), "quantity_present_pct": pct(int(present.sum()), n), "numeric_parse_pct": pct(int((q.number.notna() | q.range_low.notna()).sum()), n), "range_pct": pct(int(q.range_low.notna().sum()), n),
           "qualitative_pct": pct(int((q.parse_kind == "QUALITATIVE").sum()), n), "unit_coverage_pct_of_numeric": pct(int(((q.number.notna() | q.range_low.notna()) & q.unit_key.notna()).sum()), int((q.number.notna() | q.range_low.notna()).sum())),
           "unit_alias_resolved_pct_of_unit_raw": pct(int((q.unit_raw.notna() & q.unit_key.notna()).sum()), int(q.unit_raw.notna().sum())), "container_package_expressions": int(q.package_key.notna().sum()), "multiplier_expressions": int(q.multiplier.notna().sum()),
           "mass_grounded_pct": pct(int(q.mass_status.isin(["MEASURED", "RANGE"]).sum()), n), "volume_grounded_pct": pct(int(q.volume_status.isin(["MEASURED", "RANGE"]).sum()), n), "count_channel_pct": pct(int(q.count_status.isin(["MEASURED", "RANGE"]).sum()), n),
           "ambiguous_conversion_pct(locale range)": pct(int(q["flags"].fillna("").str.contains("locale_ambiguous").sum()), n), "conversion_method": q.conversion_method.value_counts().to_dict(), "q_level": q.q_level.value_counts().to_dict(),
           "top_units": q.unit_key.value_counts().head(20).to_dict(), "units_by_locale": {str(k): v.unit_key.value_counts().head(8).to_dict() for k, v in q.groupby(q.locale_used.fillna("UNKNOWN"))},
           "by_source_mass_grounded_pct": {s: pct(int(g.mass_status.isin(["MEASURED", "RANGE"]).sum()), len(g)) for s, g in q.groupby("source_family")}, "no_invented_grams": "pinch/handful/cup carry no gram value without POR evidence (q_level Q6 / UNKNOWN)"}
    return out


def main():
    base = pq.read_table(RB / "recipe_base_v1.parquet").to_pandas()
    df = pd.read_pickle(ID / "_identity_work.pkl")
    cons = pd.read_parquet(ID / "recipe_family_consensus_v1.parquet")
    fs = pd.read_parquet(ID / "recipe_family_field_support_v1.parquet", columns=["recipe_family_id", "field_type", "support_level"])
    ready = pq.read_table(RB / "recipe_simulation_readiness_v1.parquet").to_pandas()
    res = {}
    res["ingredients"], _ = ingredient_audit(base)
    res["processes"], mp = process_audit(base)
    res["tools"] = tool_audit(base, mp)
    cmn = pd.read_csv(ROOT / "registry/recipe_tool_structural_class_map_v1.csv").canonical_name.tolist()
    res["tool_review_queue_estimate"] = tool_queue(cmn)
    res["quantities"] = quantity_audit()
    # condition + readiness at recipe and family level
    rd = ready.merge(df[["recipe_id", "recipe_family_id", "source_id"]], on="recipe_id")
    flags = ["has_time", "has_numeric_temperature", "has_temperature_location", "has_pressure", "has_power", "has_qualitative_heat", "has_endpoint_condition", "has_quantity_information", "has_geometry_information", "has_medium_information"]
    res["conditions_recipe_level_pct"] = {f: pct(int(rd[f].sum()), len(rd)) for f in flags}
    fam = rd.groupby("recipe_family_id")[flags].any()
    res["conditions_family_level_pct"] = {f: pct(int(fam[f].sum()), len(fam)) for f in flags}
    rank = {"PROCEDURALLY_RICH": 4, "PARTIAL_CONDITIONS": 3, "QUALITATIVE_ONLY": 2, "INSUFFICIENT_CONDITIONS": 1, "UNKNOWN": 0}
    res["readiness_recipe_level"] = ready.readiness_status.value_counts().to_dict()
    res["readiness_family_level"] = cons.best_readiness_status.value_counts().to_dict()
    inst = base.set_index("recipe_id").has_instructions
    d2 = df.assign(_hi=df.recipe_id.map(inst))
    multi_src = d2[d2._hi].groupby("recipe_family_id").source_id.nunique()
    both = rd[rd.has_time & rd.has_numeric_temperature].groupby("recipe_family_id").size()
    qual_only = fam[(~fam.has_time) & (~fam.has_numeric_temperature) & (fam.has_qualitative_heat | fam.has_endpoint_condition)]
    conf = fs[fs.support_level == "CONFLICTING"].recipe_family_id.nunique()
    res["family_readiness_extras"] = {"families_with_multiple_independent_procedural_sources": int((multi_src >= 2).sum()), "families_with_conflicting_condition_fields": int(conf), "families_with_usable_T_and_time_in_one_recipe": int(len(both)), "families_with_only_qualitative_conditions": int(len(qual_only)),
                                      "disclaimer": "text availability only; NOT simulation eligibility"}
    # culture / era / bias
    from step07i_consensus import era_map
    era = pd.Series(era_map(base))
    res["bias"] = {"source_share_pct": {k: pct(v, len(base)) for k, v in base.source_family.value_counts().items()}, "language": base.language.value_counts().to_dict(), "locale": base.locale.value_counts().to_dict(),
                   "explicit_cuisine_labelled_pct": pct(int(base.cuisine_if_explicit.notna().sum()), len(base)), "explicit_cuisine_by_source": {s: pct(int(g.cuisine_if_explicit.notna().sum()), len(g)) for s, g in base.groupby("source_family")},
                   "top_explicit_cuisines": base.cuisine_if_explicit.value_counts().head(15).to_dict(), "era_known_pct": pct(int(len(era[era != "UNKNOWN"])), len(base)), "era_distribution": era.value_counts().head(25).to_dict(),
                   "steps_per_recipe_by_source": {s: quant(g.n_steps) for s, g in base.groupby("source_family")}, "ingredient_lines_per_recipe_by_source": {s: quant(g.n_ingredient_lines) for s, g in base.groupby("source_family")},
                   "representativeness_statement": "NOT globally representative: dominated by Food.com (US user content) and historic English-language Gutenberg text; cuisine/region labels are dataset-derived and sparse; no claim of cultural coverage is made"}
    # family size / ingredient per family
    feat = pq.read_table(ID / "recipe_identity_features_v1.parquet", columns=["recipe_id", "ing_ids"]).to_pandas()
    feat["fam"] = feat.recipe_id.map(df.set_index("recipe_id").recipe_family_id)
    ex = feat.explode("ing_ids").dropna(subset=["ing_ids"]).groupby("fam").ing_ids.nunique()
    res["ingredients"]["distinct_canonical_ING_per_family"] = quant(ex)
    res["_work"] = {"base_rows": len(base)}
    (R / "_audits.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: (v if k in ("conditions_family_level_pct", "family_readiness_extras", "readiness_family_level") else "ok") for k, v in res.items()}, indent=1, default=str)[:2500])


if __name__ == "__main__":
    main()
