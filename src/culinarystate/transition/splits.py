"""DEL-2 split generators. Every split returns (train_idx, cal_idx, test_idx) as sorted index arrays plus a
report of what was held out. Grouped splits never place a group in two roles (leakage-checked).

  random            sanity only
  pair_holdout      unseen (matrix, process) pairs; all targets of a pair go to the same role
  matrix_disjoint   unseen matrices (ingredient-disjoint for course cells)
  process_disjoint  unseen process signatures
  study_disjoint    connected components of row -> study/publication graph (AM3); refuses when impossible
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Split:
    name: str
    train: np.ndarray
    cal: np.ndarray
    test: np.ndarray
    groups_col: str | None
    note: str = ""

    def sha256(self) -> str:
        h = hashlib.sha256()
        for part in (self.train, self.cal, self.test):
            h.update(np.asarray(part, dtype=np.int64).tobytes())
            h.update(b"|")
        return h.hexdigest()


def _assign_groups(keys: pd.Series, fracs: tuple[float, float], seed: int) -> tuple[np.ndarray, ...]:
    uniq = np.array(sorted(keys.unique(), key=str), dtype=object)
    rng = np.random.default_rng(seed)
    rng.shuffle(uniq)
    n = len(uniq)
    n_test = max(1, int(round(fracs[1] * n)))
    n_cal = max(1, int(round(fracs[0] * n)))
    test_g, cal_g = set(uniq[:n_test]), set(uniq[n_test:n_test + n_cal])
    role = keys.map(lambda k: 2 if k in test_g else (1 if k in cal_g else 0)).to_numpy()
    idx = np.arange(len(keys))
    return idx[role == 0], idx[role == 1], idx[role == 2]


def random_split(df: pd.DataFrame, seed: int = 7, cal: float = 0.15, test: float = 0.2) -> Split:
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(df))
    n_t, n_c = int(test * len(df)), int(cal * len(df))
    return Split("random", np.sort(perm[n_t + n_c:]), np.sort(perm[n_t:n_t + n_c]), np.sort(perm[:n_t]), None)


def grouped_split(df: pd.DataFrame, cols: list[str], name: str, seed: int = 7, cal: float = 0.15,
                  test: float = 0.2) -> Split:
    keys = df[cols].astype(str).agg("||".join, axis=1)
    tr, ca, te = _assign_groups(keys, (cal, test), seed)
    return Split(name, tr, ca, te, "+".join(cols), f"{keys.nunique()} groups")


def study_components(df: pd.DataFrame) -> pd.Series:
    """Component id per row: rows sharing a study id are connected; rows without study get their own group."""
    parent: dict[str, str] = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for g, s in zip(df["group"].astype(str), df["study"].astype(str)):
        a, b = find(f"g:{g}"), find(f"s:{s}")
        if a != b:
            parent[a] = b
    return df["group"].astype(str).map(lambda g: find(f"g:{g}"))


def study_disjoint(df: pd.DataFrame, seed: int = 7, cal: float = 0.15, test: float = 0.2,
                   max_component_share: float = 0.5) -> Split | None:
    comp = study_components(df)
    sizes = comp.value_counts(normalize=True)
    if len(sizes) < 3 or sizes.iloc[0] > max_component_share:
        return None                      # AM3: report impossibility instead of a fake study-disjoint split
    tr, ca, te = _assign_groups(comp, (cal, test), seed)
    return Split("study_disjoint", tr, ca, te, "study_component",
                 f"{len(sizes)} components; largest {sizes.iloc[0]:.1%}")


def leakage(df: pd.DataFrame, s: Split, cols: list[str]) -> dict:
    out = {}
    for c in cols:
        tr = set(df.iloc[s.train][c].astype(str))
        te = set(df.iloc[s.test][c].astype(str))
        out[c] = round(len(te & tr) / len(te), 4) if te else None
    return out


def food_group_disjoint(df: pd.DataFrame, seed: int = 7) -> Split:
    """S-5 food-group-disjoint (29-diag only, D-082): grouped by ``food_group``; rows with no food group form one group."""
    return grouped_split(df, ["food_group"], "food_group_disjoint", seed)


def all_splits(df: pd.DataFrame, seed: int = 7) -> tuple[list[Split], list[str]]:
    splits = [random_split(df, seed),
              grouped_split(df, ["matrix", "process"], "pair_holdout", seed),
              grouped_split(df, ["matrix"], "matrix_disjoint", seed),
              grouped_split(df, ["process"], "process_disjoint", seed)]
    notes = []
    sd = study_disjoint(df, seed)
    if sd is None:
        notes.append("study_disjoint: NOT POSSIBLE (single source family or one giant component) — not reported")
    else:
        splits.append(sd)
    return splits, notes
