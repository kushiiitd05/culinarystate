"""DEL-2 baselines D0–D7 (plan P8). All fit on train rows only; predict for any rows.

D0 persistence (RF = 1, nothing changes)       D4 nearest compatible evidence (same target, similar matrix/process)
D1 global mean                                  D5 gradient boosting on categorical + mask features
D2 process mean (backoff global)                D6 TabPFN — not run (not installed; GPU) -> recorded as SKIPPED
D3 hierarchical shrinkage target×process -> process -> global (empirical-Bayes pseudo-counts)
D7 biased matrix factorisation: matrix × (process, target) with side-information biases
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .dataset import y_train


class Model:
    name = "base"

    def fit(self, df: pd.DataFrame) -> "Model":
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        raise NotImplementedError


class D0Persistence(Model):
    name = "D0_persistence"

    def predict(self, df):
        return np.ones(len(df))


class D1GlobalMean(Model):
    name = "D1_global_mean"

    def fit(self, df):
        self.mu = float(y_train(df).mean())
        return self

    def predict(self, df):
        return np.full(len(df), self.mu)


class D2ProcessMean(Model):
    name = "D2_process_mean"

    def fit(self, df):
        y = y_train(df)
        self.mu = float(y.mean())
        self.by = y.groupby(df["process"]).mean().to_dict()
        return self

    def predict(self, df):
        return df["process"].map(self.by).fillna(self.mu).to_numpy()


@dataclass
class D3Hierarchical(Model):
    k_proc: float = 5.0
    k_cell: float = 3.0
    name: str = "D3_hierarchical_shrinkage"

    def fit(self, df):
        y = y_train(df)
        self.mu = float(y.mean())
        g = y.groupby(df["process"]).agg(["sum", "count"])
        self.proc = ((g["sum"] + self.k_proc * self.mu) / (g["count"] + self.k_proc)).to_dict()
        key = df["target"] + "|" + df["process"]
        c = y.groupby(key).agg(["sum", "count"])
        self.cell = {}
        for k, row in c.iterrows():
            prior = self.proc.get(k.split("|", 1)[1], self.mu)
            self.cell[k] = (row["sum"] + self.k_cell * prior) / (row["count"] + self.k_cell)
        tgt = y.groupby(df["target"]).agg(["sum", "count"])
        self.tgt = ((tgt["sum"] + self.k_proc * self.mu) / (tgt["count"] + self.k_proc)).to_dict()
        return self

    def predict(self, df):
        out = []
        for t, p in zip(df["target"], df["process"]):
            v = self.cell.get(f"{t}|{p}")
            if v is None:
                v = self.proc.get(p, self.tgt.get(t, self.mu))
            out.append(v)
        return np.asarray(out, dtype=float)


def _tokens(s: str) -> set[str]:
    return {w for w in "".join(ch if ch.isalnum() else " " for ch in s.lower()).split() if len(w) > 1}


@dataclass
class D4NearestEvidence(Model):
    k: int = 5
    name: str = "D4_nearest_compatible_evidence"

    def fit(self, df):
        y = y_train(df).to_numpy()
        self.mu = float(y.mean())
        self.pool = {}
        for t, idx in df.groupby("target").indices.items():
            sub = df.iloc[idx]
            mt = [_tokens(a + " " + b) for a, b in zip(sub["matrix"], sub["food_group"])]
            pt = [_tokens(x) for x in sub["process"]]
            self.pool[t] = (mt, pt, y[idx])
        return self

    def predict(self, df):
        out = []
        for m, g, p, t in zip(df["matrix"], df["food_group"], df["process"], df["target"]):
            if t not in self.pool:
                out.append(self.mu)
                continue
            mts, pts, ys = self.pool[t]
            mt, pt = _tokens(m + " " + g), _tokens(p)
            sims = np.fromiter((0.5 * len(mt & a) / max(1, len(mt | a)) + 0.5 * len(pt & b) / max(1, len(pt | b))
                                for a, b in zip(mts, pts)), float, len(ys))
            top = np.argsort(-sims, kind="stable")[: self.k]
            out.append(float(np.average(ys[top], weights=sims[top] + 1e-6)))
        return np.asarray(out)


CAT = ["matrix", "matrix_form", "food_group", "process", "process_family", "target", "medium"]
NUM = ["n_steps", "duration_known", "temperature_known"]


@dataclass
class D5Boosting(Model):
    name: str = "D5_gradient_boosting"
    seed: int = 7

    def _X(self, df):
        X = pd.DataFrame({c: df[c].astype(str).map(self.codes[c]).fillna(-1) for c in CAT})
        for c in NUM:
            X[c] = df[c].astype(float)
        return X.to_numpy()

    def fit(self, df):
        from sklearn.ensemble import HistGradientBoostingRegressor
        self.codes = {c: {v: i for i, v in enumerate(sorted(df[c].astype(str).unique()))} for c in CAT}
        cat_mask = [True] * len(CAT) + [False] * len(NUM)
        self.m = HistGradientBoostingRegressor(categorical_features=cat_mask, max_iter=300, learning_rate=0.05,
                                               random_state=self.seed)
        X = self._X(df)
        X[:, :len(CAT)][X[:, :len(CAT)] < 0] = 0
        self.m.fit(X, y_train(df).to_numpy())
        return self

    def predict(self, df):
        X = self._X(df)
        unseen = X[:, :len(CAT)] < 0
        X[:, :len(CAT)][unseen] = np.nan                     # HGB treats NaN as missing category
        return self.m.predict(X)


@dataclass
class D7BiasedMF(Model):
    rank: int = 4
    epochs: int = 60
    lr: float = 0.05
    reg: float = 0.05
    seed: int = 7
    name: str = "D7_biased_mf_side_info"

    def fit(self, df):
        rng = np.random.default_rng(self.seed)
        y = y_train(df).to_numpy()
        self.mu = float(y.mean())
        self.rows = {m: i for i, m in enumerate(sorted(df["matrix"].unique()))}
        cols = (df["process"] + "|" + df["target"])
        self.cols = {c: i for i, c in enumerate(sorted(cols.unique()))}
        self.side = {s: i for i, s in enumerate(sorted(df["food_group"].astype(str).unique()))}
        self.tside = {s: i for i, s in enumerate(sorted(df["target"].unique()))}
        self.pside = {s: i for i, s in enumerate(sorted(df["process"].unique()))}
        R, C = len(self.rows), len(self.cols)
        self.P = rng.normal(0, 0.05, (R, self.rank))
        self.Q = rng.normal(0, 0.05, (C, self.rank))
        self.br, self.bc = np.zeros(R), np.zeros(C)
        self.bg, self.bt, self.bp = np.zeros(len(self.side)), np.zeros(len(self.tside)), np.zeros(len(self.pside))
        ri = df["matrix"].map(self.rows).to_numpy()
        ci = cols.map(self.cols).to_numpy()
        gi = df["food_group"].astype(str).map(self.side).to_numpy()
        ti = df["target"].map(self.tside).to_numpy()
        pi = df["process"].map(self.pside).to_numpy()
        order = np.arange(len(y))
        for _ in range(self.epochs):
            rng.shuffle(order)
            for n in order:
                r, c, g, t, p = ri[n], ci[n], gi[n], ti[n], pi[n]
                pred = self.mu + self.br[r] + self.bc[c] + self.bg[g] + self.bt[t] + self.bp[p] + self.P[r] @ self.Q[c]
                e = y[n] - pred
                for b, i in ((self.br, r), (self.bc, c), (self.bg, g), (self.bt, t), (self.bp, p)):
                    b[i] += self.lr * (e - self.reg * b[i])
                pr = self.P[r].copy()
                self.P[r] += self.lr * (e * self.Q[c] - self.reg * self.P[r])
                self.Q[c] += self.lr * (e * pr - self.reg * self.Q[c])
        return self

    def predict(self, df):
        out = []
        for m, p, t, g in zip(df["matrix"], df["process"], df["target"], df["food_group"].astype(str)):
            r, c = self.rows.get(m), self.cols.get(f"{p}|{t}")
            v = self.mu
            v += self.bg[self.side[g]] if g in self.side else 0
            v += self.bt[self.tside[t]] if t in self.tside else 0
            v += self.bp[self.pside[p]] if p in self.pside else 0
            if r is not None:
                v += self.br[r]
            if c is not None:
                v += self.bc[c]
            if r is not None and c is not None:
                v += self.P[r] @ self.Q[c]
            out.append(v)
        return np.asarray(out)


def all_models() -> list[Model]:
    return [D0Persistence(), D1GlobalMean(), D2ProcessMean(), D3Hierarchical(), D4NearestEvidence(), D5Boosting(),
            D7BiasedMF()]
