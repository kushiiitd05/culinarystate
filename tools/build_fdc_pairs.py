#!/usr/bin/env python3
"""X15: SR Legacy raw/cooked description pairs -> dry-basis ratios, compared with USDA Retention Release 6.

  /opt/anaconda3/bin/python tools/build_fdc_pairs.py
Writes registry/evidence/fdc_raw_cooked_pairs_v1.csv (public-domain USDA values; candidates, not EVD) and
reports/del2/fdc_pairs_v1.md/json. "Analytical" = both values carry a derivation whose source code is 1, 6 or 13
(analytical or aggregated analytical); imputed values, including ones computed with retention factors, are
circular against R6 and are reported separately.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence.fdc_pairs import dry_basis_ratio, pair_foods  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.transition.cross_source import STEP, agreement, coarse_group, nutrient_key, prepare, prepare_groups  # noqa: E402
from culinarystate.transition.dataset import build_cells  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402
from culinarystate.vocab.line_link import LineLinker  # noqa: E402

SR = next((ROOT / "data" / "raw" / "fdc" / "sr_legacy").glob("FoodData_Central_sr_legacy_food_csv_*"))
WATER = 1051
ANALYTICAL_SOURCES = {1, 4, 10}       # food_nutrient_source ids for codes 1, 6, 13


def linker(st: LedgerStore) -> LineLinker:
    names = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") and a["language"] == "en":
            names.setdefault(norm(a["normalized"]), a["ingredient_id"])
    return LineLinker(names, set())


def load():
    food = pd.read_csv(SR / "food.csv")
    cat = pd.read_csv(SR / "food_category.csv").set_index("id").description
    nut = pd.read_csv(SR / "nutrient.csv").set_index("id")
    deriv = pd.read_csv(SR / "food_nutrient_derivation.csv").set_index("id").source_id
    fn = pd.read_csv(SR / "food_nutrient.csv", usecols=["fdc_id", "nutrient_id", "amount", "derivation_id"])
    fn["analytical"] = fn.derivation_id.map(deriv).isin(ANALYTICAL_SOURCES)
    return food, cat, nut, fn


def ratios(pairs: pd.DataFrame, nut: pd.DataFrame, fn: pd.DataFrame) -> pd.DataFrame:
    keyed = {i: nutrient_key(n) for i, n in nut.name.items() if nutrient_key(n)}
    water = fn[fn.nutrient_id == WATER].set_index("fdc_id").amount
    vals = fn[fn.nutrient_id.isin(keyed)].set_index(["fdc_id", "nutrient_id"])
    rows = []
    for p in pairs.itertuples():
        wr, wc = water.get(p.raw_id), water.get(p.cooked_id)
        if pd.isna(wr) or pd.isna(wc):
            continue
        for nid, key in keyed.items():
            if (p.raw_id, nid) not in vals.index or (p.cooked_id, nid) not in vals.index:
                continue
            r, c = vals.loc[(p.raw_id, nid)], vals.loc[(p.cooked_id, nid)]
            y = dry_basis_ratio(r.amount, wr, c.amount, wc)
            if y is not None:
                rows.append({**p._asdict(), "nutrient": key, "nutrient_name": nut.name[nid], "raw_amount": r.amount,
                             "cooked_amount": c.amount, "water_raw": wr, "water_cooked": wc,
                             "per_100g_ratio": round(c.amount / r.amount, 4), "dry_basis_ratio": y,
                             "analytical": bool(r.analytical and c.analytical)})
    return pd.DataFrame(rows).drop(columns="Index")


def cells(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    out = df.groupby(by + ["nutrient"], as_index=False).agg(y=("dry_basis_ratio", "median"), n=("dry_basis_ratio", "size"))
    return out.assign(censored_share=0.0).rename(columns={by[0]: "ingredient_id", by[1]: "step"})


def main() -> None:
    st = LedgerStore()
    food, cat, nut, fn = load()
    pairs = pair_foods(food)
    lk = linker(st)
    pairs["ingredient_id"] = pairs.base.map(lambda b: lk.match_phrase(b.split("|")[0]))
    meta = food.set_index("fdc_id")
    pairs["food_group"] = pairs.raw_id.map(meta.food_category_id).map(cat)
    pairs["raw_description"] = pairs.raw_id.map(meta.description)
    pairs["cooked_description"] = pairs.cooked_id.map(meta.description)
    pairs["step"] = pairs.method.fillna("cook")
    pairs["group"] = pairs.food_group.map(coarse_group)
    pairs["step_family"] = pairs.step.map(STEP)
    df = ratios(pairs, nut, fn)
    out = ROOT / "registry" / "evidence" / "fdc_raw_cooked_pairs_v1.csv"
    df.to_csv(out, index=False)

    usda = build_cells(st, "USDA-RETN-R6").df
    u1, u2 = prepare(usda), prepare_groups(usda)
    res = {"pairs": int(len(pairs)), "pairs_with_ratio": int(df[["raw_id", "cooked_id"]].drop_duplicates().shape[0]),
           "ratio_rows": int(len(df)), "analytical_rows": int(df.analytical.sum()),
           "pairs_linked_to_ING": int(pairs.ingredient_id.notna().sum()),
           "methods": pairs.step.value_counts().head(12).to_dict()}
    for tier, d in {"all": df, "analytical": df[df.analytical]}.items():
        d1 = d[d.ingredient_id.notna()]
        res[f"L1 ingredient x step: R6 vs FDC dry-basis ({tier})"] = agreement(u1, cells(d1, ["ingredient_id", "step"]))
        d2 = d[d.group.notna() & d.step_family.notna()]
        res[f"L2 group x step-family: R6 vs FDC dry-basis ({tier})"] = agreement(u2, cells(d2, ["group", "step_family"]))
    (ROOT / "reports" / "del2" / "fdc_pairs_v1.json").write_text(json.dumps(res, indent=1, default=str))
    lines = ["# FDC SR Legacy raw/cooked pairs v1 (X15, SSOT §198.7)", "",
             "Dry-basis ratio R = (N_c/(100-w_c)) / (N_r/(100-w_r)) equals true retention iff total solids are conserved;",
             "descriptions are paired, samples are not matched (SSOT caveat), so rows are candidates, not EVD.",
             "'analytical' = both values from source codes 1/6/13; imputed values (incl. retention-factor calculations) are",
             "circular against R6.", ""]
    for k, r in res.items():
        if not isinstance(r, dict) or "overlap_cells" not in r:
            lines.append(f"- {k}: {r}")
            continue
        lines += ["", f"## {k}"] + [f"- {kk}: {vv}" for kk, vv in r.items() if kk != "largest_disagreements"]
        for d in r.get("largest_disagreements", [])[:5]:
            lines.append(f"  - {d['ingredient_id']} / {d['step']} / {d['nutrient']}: R6={d['y_a']} FDC={d['y_b']}")
    (ROOT / "reports" / "del2" / "fdc_pairs_v1.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
