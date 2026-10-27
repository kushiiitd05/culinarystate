"""Step 35.0 (D-036) Food.com tag census. DRAFT, unsigned. Local research use only.

Reads ONLY columns Keywords and RecipeCategory from data/external/foodcom/recipes.parquet.
Writes aggregate tag counts only (no recipe id, no text).

Parsing: Keywords is a list<string> column; null -> empty list. Each tag is whitespace-stripped
(str.strip) and empty strings dropped; case is preserved (census is case-sensitive, exact).
RecipeCategory is a scalar string, same strip; null/empty dropped. A tag is counted once per recipe
per source column (duplicates inside one recipe's list count once).
Cut: tags with n_recipes < MIN_RECIPES (20) are dropped. This is a privacy/noise cut, not a science claim.
Map n_recipes = union over both columns (a recipe with the tag in both counts once); the census counts per
(tag, column), so they differ by design. The map carries n_recipes_keywords / n_recipes_category = census rows.
Output sorted by (-n_recipes, tag, source_column). Deterministic.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/external/foodcom/recipes.parquet"
OUT = ROOT / "registry/cuisine/foodcom_tag_census_v1.csv"
MIN_RECIPES = 20
COLUMNS = ["Keywords", "RecipeCategory"]


def clean_tags(value) -> frozenset[str]:
    """Parse one cell (list/ndarray/str/None) into a set of stripped non-empty tags."""
    if value is None:
        return frozenset()
    if isinstance(value, str):
        value = [value]
    out = set()
    for t in value:
        if isinstance(t, str):
            t = t.strip()
            if t:
                out.add(t)
    return frozenset(out)


def count_tags(path: Path = SRC) -> tuple[Counter, int]:
    """Return Counter[(tag, source_column)] -> n_recipes, and the parquet row count."""
    pf = pq.ParquetFile(path)
    counts: Counter = Counter()
    for batch in pf.iter_batches(columns=COLUMNS, batch_size=50_000):
        for col in COLUMNS:
            for v in batch.column(col).to_pylist():
                for t in clean_tags(v):
                    counts[(t, col)] += 1
    return counts, pf.metadata.num_rows


def rows(counts: Counter, min_n: int = MIN_RECIPES) -> list[tuple[str, int, str]]:
    kept = [(t, n, c) for (t, c), n in counts.items() if n >= min_n]
    return sorted(kept, key=lambda r: (-r[1], r[0], r[2]))


LOOKUP = ROOT / "registry/cuisine/cuisine_lookup_v1_DRAFT.csv"
MAP_OUT = ROOT / "registry/cuisine/foodcom_tag_cuisine_map_v1_DRAFT.csv"
EXPL_OUT = ROOT / "registry/cuisine/explicit_cuisine_labels_v1.csv"
BASE = ROOT / "ledgers/recipe_base/recipe_base_v1.parquet"
PLACEHOLDERS = ("NEEDS_HUMAN", "MIXED", "UNKNOWN")
CONTINENTS = ("Africa", "Americas", "Asia", "Europe", "Oceania")  # UN M49


def load_lookup(path: Path = LOOKUP) -> dict[str, dict[str, str]]:
    """Fixed table, exact match on str.casefold() of the stripped tag. No fuzzy matching."""
    with path.open(newline="", encoding="utf-8") as f:
        return {r["term"].casefold(): r for r in csv.DictReader(f)}


def _continent_labels(entries) -> set[str]:
    """Real UN M49 continents carried by CUISINE or REGION entries (MIXED / NEEDS_HUMAN ignored)."""
    return {e["continent"] for e in entries
            if e["label_level"] in ("CUISINE", "REGION") and e["continent"] in CONTINENTS}


def derive(path: Path = SRC, lookup: dict | None = None):
    """One pass: per-tag recipe counts and aggregate recipe-level stats.

    Returns (tag_n, stats, col_n). tag_n[tag] = recipes carrying the tag in Keywords OR RecipeCategory
    (union, once per recipe); col_n[(tag, column)] = recipes carrying it in that column (equals the
    census). Cuisine analysis uses CUISINE-level terms only; continent analysis uses CUISINE or REGION
    terms. Nothing per-recipe is returned or written.
    """
    lookup = load_lookup() if lookup is None else lookup
    pf = pq.ParquetFile(path)
    tag_n: Counter = Counter()
    col_n: Counter = Counter()
    st = Counter()
    for batch in pf.iter_batches(columns=COLUMNS, batch_size=50_000):
        kw = batch.column("Keywords").to_pylist()
        rc = batch.column("RecipeCategory").to_pylist()
        for a, b in zip(kw, rc):
            ka, kb = clean_tags(a), clean_tags(b)
            tags = ka | kb
            tag_n.update(tags)
            col_n.update((t, "Keywords") for t in ka)
            col_n.update((t, "RecipeCategory") for t in kb)
            ents = [e for e in (lookup.get(t.casefold()) for t in tags) if e is not None]
            cuis = {e["cuisine"] for e in ents if e["label_level"] == "CUISINE"}
            conts = _continent_labels(ents)
            st["n_rows"] += 1
            if cuis:
                st["n_cuisine_level"] += 1
                st["n_cuisine_conflicting"] += len(cuis) > 1
            else:
                st["n_cuisine_unknown"] += 1
                st["n_cuisine_unknown_with_region_or_needs_human_term"] += any(
                    e["label_level"] != "CUISINE" for e in ents)
            if conts:
                st["n_continent_level"] += 1
                st["n_continent_conflicting"] += len(conts) > 1
            else:
                st["n_continent_unknown"] += 1
                st["n_continent_unknown_with_mixed_or_needs_human_term"] += bool(ents)
    return tag_n, dict(st), col_n


def explicit_labels(path: Path = BASE) -> list[tuple[str, int, int, str]]:
    """Aggregate cuisine_if_explicit by label and source_family (reads two columns only)."""
    t = pq.read_table(path, columns=["cuisine_if_explicit", "source_family"]).to_pylist()
    c: Counter = Counter()
    for r in t:
        lab = r["cuisine_if_explicit"]
        if lab is not None and str(lab).strip():
            c[(str(lab).strip(), r["source_family"])] += 1
    by: dict[str, dict[str, int]] = {}
    for (lab, fam), n in c.items():
        by.setdefault(lab, {})[fam] = n
    out = [(lab, sum(d.values()), len(d), ";".join(f"{k}={d[k]}" for k in sorted(d))) for lab, d in by.items()]
    return sorted(out, key=lambda r: (-r[1], r[0]))


def build_map(tag_n: Counter, lookup: dict, col_n: Counter, min_n: int = MIN_RECIPES) -> list[list]:
    """n_recipes = union over both columns (what labelling uses); the per-column counts reconcile
    to foodcom_tag_census_v1.csv, which counts each (tag, column) separately."""
    out = []
    for tag, n in sorted(tag_n.items(), key=lambda kv: (-kv[1], kv[0])):
        if n < min_n:
            continue
        cols = [col_n[(tag, "Keywords")], col_n[(tag, "RecipeCategory")]]
        e = lookup.get(tag.casefold())
        if e is None:
            out.append([tag, n, *cols, "UNKNOWN", "UNKNOWN", "UNKNOWN", "NO_LOOKUP_MATCH", "DRAFT_PENDING_SIGN"])
        else:
            out.append([tag, n, *cols, e["cuisine"], e["continent"], e["label_level"], e["basis"],
                        "DRAFT_PENDING_SIGN"])
    return out


def main() -> None:
    import json
    counts, n = count_tags()
    r = rows(counts)
    lookup = load_lookup()
    tag_n, stats, col_n = derive(SRC, lookup)
    mp = build_map(tag_n, lookup, col_n)
    with MAP_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["tag", "n_recipes", "n_recipes_keywords", "n_recipes_category", "proposed_cuisine",
                    "proposed_continent", "label_level", "match_basis", "status"])
        w.writerows(mp)
    ex = explicit_labels()
    with EXPL_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["label", "n_recipes", "n_source_families", "source_family_counts"])
        w.writerows(ex)
    real = [m for m in mp if m[6] == "CUISINE"]
    print(json.dumps({**stats, "tags_in_map": len(mp), "tags_mapped_real": len(real),
                      "tags_region": sum(m[6] == "REGION" for m in mp),
                      "tags_needs_human": sum(m[6] == "NEEDS_HUMAN" for m in mp),
                      "explicit_labels": len(ex), "explicit_recipes": sum(e[1] for e in ex)}))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        f.write(f"# Food.com tag census v1 DRAFT; aggregate counts only; source rows={n}; "
                f"cut: n_recipes>={MIN_RECIPES} (privacy/noise cut, not a science claim)\n")
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["tag", "n_recipes", "source_column"])
        w.writerows(r)
    print(f"rows={n} distinct_tag_col={len(counts)} kept={len(r)} -> {OUT}")


if __name__ == "__main__":
    main()
