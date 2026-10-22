"""STEP 07I: interpretable pair features, ranking score and the PRE-REGISTERED provisional family-edge rule (reports/step07i/preregistration_v1.md). Missing data is never 0: *_missing flags + the score renormalises over available features."""
from __future__ import annotations

import math
from collections import Counter

import numpy as np

from .features import mh_sim

W = {"title_token": 0.15, "ingredient_idf": 0.30, "ingredient_id": 0.10, "multiset": 0.10, "instruction_shingle": 0.20, "process_seq": 0.05, "condition": 0.05, "quantity_profile": 0.05}
# pre-registered family-edge thresholds
T_IDF, T_TITLE, T_SHINGLE, T_PROC, MIN_ING = 0.80, 0.50, 0.30, 0.70, 4


def jacc(a, b):
    if not a or not b:
        return None
    i = len(a & b)
    return i / (len(a) + len(b) - i)


def trigrams(s: str):
    return {s[i:i + 3] for i in range(len(s) - 2)} if len(s) >= 3 else set()


def lcs_ratio(a, b):
    if len(a) < 1 or len(b) < 1:
        return None
    a, b = a[:40], b[:40]
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[-1]))
        prev = cur
    return prev[-1] / max(len(a), len(b))


class Store:
    """column store over representative recipes (row index = position)"""

    def __init__(self, df, idf):
        self.n = len(df)
        self.id = df.recipe_id.tolist()
        self.src = df.source_family.tolist()
        self.sid = df.source_id.tolist()
        self.locale = df.locale.tolist()
        self.cuisine = df.cuisine_if_explicit.tolist()
        self.title_norm = df.title_norm.tolist()
        self.twords = [frozenset(str(t).split()) for t in df.title_key]
        self.ids = df.ids_set.tolist()
        self.toks = df.toks_list.tolist()
        self.tokset = df.toks_set.tolist()
        self.proc = df.proc_seq.tolist()
        self.mh_steps = df.mh_steps.tolist()
        self.cond = df.cond_set.tolist()
        self.mass = df.mass_dict.tolist()
        self.idf = idf
        self.n_steps = df.n_steps.tolist()
        self.n_ing = df.n_ing_lines.tolist()

    @classmethod
    def from_lists(cls, **kw):
        """store over an explicit subset of representatives (used per partition); keys mirror the attributes set in __init__"""
        o = cls.__new__(cls)
        o.__dict__.update(kw)
        o.n = len(kw["id"])
        return o

    def features(self, i, j):
        """components + final score/edge (kept for tests and the legacy sample path)"""
        return self.finalize(self.components(i, j))

    def components(self, i, j):
        f = {}
        f["title_token"] = jacc(self.twords[i], self.twords[j])
        ti, tj = trigrams(self.title_norm[i]), trigrams(self.title_norm[j])
        f["title_trigram"] = jacc(ti, tj)
        f["ingredient_id"] = jacc(self.ids[i], self.ids[j])
        a, b = self.tokset[i], self.tokset[j]
        f["ingredient_token"] = jacc(a, b)
        if a and b:
            w = self.idf
            inter = sum(w.get(t, 1.0) for t in a & b)
            uni = sum(w.get(t, 1.0) for t in a | b)
            f["ingredient_idf"] = inter / uni if uni else None
            ca, cb = Counter(self.toks[i]), Counter(self.toks[j])
            keys = set(ca) | set(cb)
            f["multiset"] = sum(min(ca[k], cb[k]) for k in keys) / sum(max(ca[k], cb[k]) for k in keys)
        else:
            f["ingredient_idf"] = f["multiset"] = None
        f["instruction_shingle"] = mh_sim(self.mh_steps[i], self.mh_steps[j])
        cheap = f["ingredient_idf"] is not None and f["ingredient_idf"] >= 0.5
        pa, pb = self.proc[i], self.proc[j]
        f["process_set"] = jacc(set(pa), set(pb))
        f["process_seq"] = lcs_ratio(pa, pb) if (cheap and len(pa) >= 3 and len(pb) >= 3) else None
        f["condition"] = jacc(self.cond[i], self.cond[j])
        qs, hint = None, None
        ma, mb = self.mass[i], self.mass[j]
        if cheap and ma and mb:
            sh = [k for k in ma if k in mb and ma[k] > 0 and mb[k] > 0]
            if len(sh) >= 3:
                va, vb = np.array([ma[k] for k in sh]), np.array([mb[k] for k in sh])
                qs = float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb)))
                r = va / vb
                med, cv = float(np.median(r)), float(r.std() / r.mean())
                f["scale_ratio"] = med
                if cv <= 0.10 and (med > 1.15 or med < 0.87):
                    hint = "SCALED_VARIANT_HINT"
        f["quantity_profile"] = qs
        f["hint"] = hint
        f["same_source"] = self.sid[i] == self.sid[j]
        f["cross_source_family"] = self.src[i] != self.src[j]
        f["locale_agree"] = (self.locale[i] == self.locale[j]) if (self.locale[i] and self.locale[j]) else None
        f["cuisine_agree"] = (self.cuisine[i] == self.cuisine[j]) if (self.cuisine[i] and self.cuisine[j]) else None
        f["min_tok_ok"] = len(self.tokset[i]) >= MIN_ING and len(self.tokset[j]) >= MIN_ING
        f["proc3_ok"] = len(self.proc[i]) >= 3 and len(self.proc[j]) >= 3
        return f

    def finalize(self, f):
        num = den = 0.0
        for k, w_ in W.items():
            v = f.get(k)
            if v is not None:
                num += w_ * v
                den += w_
        f["score"] = num / den if den else None
        f["features_available"] = sum(1 for k in W if f.get(k) is not None)
        f["family_edge"] = self.family_edge(None, None, f)
        return f

    def family_edge(self, i, j, f):
        if not f["min_tok_ok"]:
            return False
        if f["ingredient_idf"] is None or f["ingredient_idf"] < T_IDF:
            return False
        if f["title_token"] is None or f["title_token"] < T_TITLE:
            return False
        sup = (f["instruction_shingle"] is not None and f["instruction_shingle"] >= T_SHINGLE) or (f["process_seq"] is not None and f["process_seq"] >= T_PROC and f["proc3_ok"])
        if not sup:
            return False
        if f["cuisine_agree"] is False:
            return False
        return True
