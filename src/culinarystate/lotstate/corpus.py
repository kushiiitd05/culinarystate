"""Recipe record stream for the lot-state census (read-only).

Same records as ``recipes.corpus`` (ids, families, ingredient_lines, steps) with ONE addition for Food.com: the raw
quantity list length, because ``corpus.iter_foodcom`` pads / truncates the quantity list to the parts list and so hides
that the two Kaggle lists differ in length (``extra.q_len`` / ``extra.p_len``, ``extra.q_raw`` unpadded).
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

FAMILIES = ("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT", "FOODCOM", "TASTESET")


FC_COLS = ["RecipeId", "Name", "PrepTime", "CookTime", "TotalTime", "RecipeIngredientQuantities",
           "RecipeIngredientParts", "RecipeInstructions", "RecipeCategory"]


def _foodcom_record(row: dict) -> dict:
    rid = int(row["RecipeId"])
    q, p = list(row["RecipeIngredientQuantities"] or []), list(row["RecipeIngredientParts"] or [])
    lines = [f"{(q[i] if i < len(q) and q[i] else '')} {p[i]}".strip() for i in range(len(p))]
    return {"recipe_id": f"FC{rid}", "source_family": "FOODCOM", "source_record_id": str(rid), "title": row["Name"],
            "ingredient_lines": lines, "steps": list(row["RecipeInstructions"] or []),
            "extra": {"ingredient_parts": p, "q_raw": q, "q_len": len(q), "p_len": len(p),
                      "category": row["RecipeCategory"]}}


def iter_foodcom_raw(parquet: Path, batch_size: int = 5000) -> Iterator[dict]:
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(parquet)
    for b in pf.iter_batches(batch_size=batch_size, columns=FC_COLS):
        for row in b.to_pylist():
            yield _foodcom_record(row)


_REC: dict = {}


def _rec_cache(corpus) -> dict:
    """REC ledger (latest rows) loaded once per process."""
    if not _REC:
        _REC.update(corpus.rec_latest())
    return _REC


def stream(families, root: Path) -> Iterator[dict]:
    """Yield records of the requested families. A missing family is skipped (BBC is not on this server)."""
    from culinarystate.recipes import corpus
    root = Path(root)
    rec_f = tuple(f for f in families if f in ("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT"))
    rec = _rec_cache(corpus) if rec_f else None
    for fam in rec_f:                                  # one family per call: a missing family must not hide the rest
        try:
            yield from corpus.iter_rec_corpora(rec, families=(fam,))
        except (FileNotFoundError, OSError):
            continue
    if "FOODCOM" in families:
        yield from iter_foodcom_raw(root / "data/external/foodcom/recipes.parquet")
    if "TASTESET" in families:
        yield from corpus.iter_tasteset()


def sample_records(families, seed: str, size: int, root: Path) -> list[dict]:
    """The ``size`` records with the smallest sha256(seed || recipe_id): the same rule and the same sample as
    ``rung_a_measure.seeded_sample`` over the combined stream, without building every Food.com record first."""
    import heapq

    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    from culinarystate.extraction.rung_a_measure import rank
    root = Path(root)
    others = tuple(f for f in families if f != "FOODCOM")
    parquet = root / "data/external/foodcom/recipes.parquet"

    def keyed():
        if "FOODCOM" in families:
            for rid in pq.read_table(parquet, columns=["RecipeId"]).column(0).to_pylist():
                i = f"FC{int(rid)}"
                yield rank(seed, i), i, "FOODCOM"
        for rec in stream(others, root):
            i = rec.get("recipe_id")
            if isinstance(i, str) and i:
                yield rank(seed, i), i, rec["source_family"]

    chosen = heapq.nsmallest(size, keyed())
    order = {i: n for n, (_, i, _) in enumerate(chosen)}
    out: list[dict] = []
    fc_ids = [int(i[2:]) for _, i, fam in chosen if fam == "FOODCOM"]
    if fc_ids:
        tbl = pq.read_table(parquet, columns=FC_COLS, filters=[("RecipeId", "in", fc_ids)])
        out.extend(_foodcom_record(r) for r in tbl.to_pylist())
    want = {i for _, i, fam in chosen if fam != "FOODCOM"}
    if want:
        for rec in stream(others, root):
            if rec.get("recipe_id") in want:
                out.append(rec)
    out.sort(key=lambda r: order[r["recipe_id"]])
    return out
