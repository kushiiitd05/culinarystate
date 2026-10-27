"""08a.6: component-feasibility report for gate G08-7 (THR-08A-08, 09, 15, 20).

Pure functions, no I/O, no mutation of inputs. A "row" here is a flat dict (see join_rows):
evd_id, source_family, target_family, analyte, matrix_family, process_family, split_group_id,
independence_resolution, tier, verification_status, lab_group_status.
Contract: reports/step04/lineage_contract_v1_1.md 4.4, 4.5, L-05, L-06, L-08, L-18.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable, Mapping, Optional, Sequence

SHARE_THRESHOLD = 0.40      # THR-08A-08 / 20 (strictly greater than fails)
K_MIN_NEFF = 10             # THR-08A-20 (K, same as G15-c)
K_CELL_GROUPS = 5           # supplied by the 08a.6 work order; NOT found in the registry rows read
POOL_RESOLUTIONS = frozenset({"STUDY", "PUBLICATION_ONLY"})
NON_TEST_TIERS = frozenset({"E5", "E6", "E7"})  # L-08; no other tier exclusion is stated
LABEL_STUDY = "study-disjoint"
LABEL_PUB = "publication-component CV"
LABEL_LOSFO = "leave-one-source-family-out"
LABEL_RANK = {LABEL_LOSFO: 0, LABEL_PUB: 1, LABEL_STUDY: 2}  # weaker label wins = min rank
FORMULAS = {
    "kish_n_eff": "n_eff = (sum_g w_g)^2 / sum_g w_g^2 with w_g = n_g = number of rows of split group g inside the pool",
    "largest_share": "max_g n_g / sum_g n_g",
    "card_rule": "largest split-group share of ALL rows of the target family > 0.40 (THR-08A-08)",
    "refined_rule": "pool = independence_resolution in {STUDY, PUBLICATION_ONLY} and TEST-eligible tier; pass = n_eff >= 10 AND share <= 0.40 (THR-08A-20)",
    "label": "weaker of the two rules wins; study-disjoint needs every pool row = STUDY (L-06); a failed rule gives publication-component CV plus leave-one-source-family-out (THR-08A-15)",
}


def kish_neff(sizes: Iterable[int]) -> Optional[float]:
    s = [int(x) for x in sizes if x]
    if not s:
        return None
    return sum(s) ** 2 / sum(x * x for x in s)


def group_sizes(rows: Iterable[Mapping]) -> dict[str, int]:
    c = Counter(r["split_group_id"] for r in rows)
    return dict(sorted(c.items()))


def giant_stats(sizes: Mapping[str, int]) -> dict:
    tot = sum(sizes.values())
    top = max(sizes.values()) if sizes else 0
    return {"rows": tot, "groups": len(sizes), "largest_group_rows": top,
            "largest_share": (top / tot) if tot else None, "n_eff": kish_neff(sizes.values())}


def exceeds_share(sizes: Mapping[str, int], threshold: float = SHARE_THRESHOLD) -> Optional[bool]:
    tot = sum(sizes.values())
    if not tot:
        return None
    return max(sizes.values()) / tot > threshold


def _eligible(r: Mapping, require_human: bool) -> bool:
    if r.get("independence_resolution") not in POOL_RESOLUTIONS or r.get("tier") in NON_TEST_TIERS:
        return False
    return (r.get("verification_status") == "HUMAN_VERIFIED") if require_human else True


def _reading(rows: Sequence[Mapping], card_exceeds: Optional[bool], require_human: bool) -> dict:
    pool = [r for r in rows if _eligible(r, require_human)]
    st = giant_stats(group_sizes(pool))
    out = {"pool_rows": st["rows"], "pool_groups": st["groups"], "pool_largest_group_rows": st["largest_group_rows"],
           "pool_largest_share": st["largest_share"], "n_eff": st["n_eff"], "card_exceeds": card_exceeds}
    if not pool:
        out.update(share_pass=None, neff_pass=None, refined_pass=None, all_pool_study=False, label=LABEL_LOSFO,
                   fallback_pair=None)
        return out
    share_pass = st["largest_share"] <= SHARE_THRESHOLD
    neff_pass = st["n_eff"] >= K_MIN_NEFF
    refined = share_pass and neff_pass
    all_study = all(r["independence_resolution"] == "STUDY" for r in pool)
    failed = bool(card_exceeds) or not refined
    label = LABEL_PUB if failed else (LABEL_STUDY if all_study else LABEL_PUB)
    out.update(share_pass=share_pass, neff_pass=neff_pass, refined_pass=refined, all_pool_study=all_study,
               label=label, fallback_pair=[LABEL_PUB, LABEL_LOSFO] if failed else None)
    return out


def evaluate_family(rows: Sequence[Mapping]) -> dict:
    """Card rule on all rows, refined rule on the pool; two readings of 'TEST-eligible tiers'.

    CONTRACT-AMBIGUITY: THR-08A-20 says 'TEST-eligible tiers'; the contract excludes only E5/E6/E7/IMPUTED (L-08)
    and separately demands human verification for held-out labels (G14-3). Reading A = tier only,
    reading B = tier and HUMAN_VERIFIED. Both are reported; the weaker label across readings applies in the verdict.
    """
    allsz = group_sizes(rows)
    card = exceeds_share(allsz)
    return {"all_rows": giant_stats(allsz), "card_exceeds": card,
            "A_tier_only": _reading(rows, card, False),
            "B_tier_and_human_verified": _reading(rows, card, True)}


def losfo_feasibility(rows: Sequence[Mapping]) -> dict:
    fam_of_group: dict[str, set] = defaultdict(set)
    for r in rows:
        fam_of_group[r["split_group_id"]].add(r["source_family"])
    spanning = sum(1 for f in fam_of_group.values() if len(f) > 1)
    fams = sorted({r["source_family"] for r in rows})
    total = len(rows)
    per = {}
    for f in fams:
        inn = [r for r in rows if r["source_family"] == f]
        rest = [r for r in rows if r["source_family"] != f]
        rg = len({r["split_group_id"] for r in rest})
        per[f] = {"rows": len(inn), "groups": len({r["split_group_id"] for r in inn}), "heldout_rows": len(inn),
                  "heldout_share": len(inn) / total if total else None, "remaining_rows": len(rest),
                  "remaining_groups": rg, "remaining_has_ge_k_groups": rg >= K_CELL_GROUPS}
    return {"families": fams, "groups_spanning_families": spanning,
            "structurally_feasible": len(fams) >= 2 and spanning == 0, "per_family": per}


def cell_survival(rows: Sequence[Mapping], k: int = K_CELL_GROUPS, pool_only: bool = False) -> dict:
    cells: dict[tuple, list] = defaultdict(list)
    for r in rows:
        if pool_only and not _eligible(r, False):
            continue
        cells[(r["analyte"], r["matrix_family"], r["process_family"])].append(r)
    surv = [c for c in cells.values() if len({r["split_group_id"] for r in c}) >= k]
    multi_src = sum(1 for c in cells.values() if len({r["source_family"] for r in c}) >= 2)
    dist = Counter(min(len({r["split_group_id"] for r in c}), 10) for c in cells.values())
    return {"k": k, "pool_only": pool_only, "cells": len(cells), "cells_with_ge_k_groups": len(surv),
            "surviving_rows": sum(len(c) for c in surv), "cells_with_ge_2_source_families": multi_src,
            "groups_per_cell_capped_at_10": {str(a): dist[a] for a in sorted(dist)}}


def _weakest(labels: Iterable[str]) -> str:
    return min(labels, key=lambda x: LABEL_RANK[x])


def _source_family_table(rows: Sequence[Mapping]) -> dict:
    out = {}
    for f in sorted({r["source_family"] for r in rows}):
        sub = [r for r in rows if r["source_family"] == f]
        st = giant_stats(group_sizes(sub))
        out[f] = {**st, "resolution": dict(sorted(Counter(r["independence_resolution"] for r in sub).items()))}
    return out


def build_report(rows: Sequence[Mapping]) -> dict:
    rows = sorted(rows, key=lambda r: r["evd_id"])
    overall = evaluate_family(rows)
    tfs = sorted({r["target_family"] for r in rows})
    by_tf = {t: evaluate_family([r for r in rows if r["target_family"] == t]) for t in tfs}
    an = {a: evaluate_family([r for r in rows if r["analyte"] == a]) for a in sorted({r["analyte"] for r in rows})}
    an_summary = {"analytes": len(an), "card_exceeds": sum(1 for v in an.values() if v["card_exceeds"]),
                  "pool_nonempty": sum(1 for v in an.values() if v["A_tier_only"]["pool_rows"]),
                  "refined_pass_A": sum(1 for v in an.values() if v["A_tier_only"]["refined_pass"]),
                  "labels_A": dict(sorted(Counter(v["A_tier_only"]["label"] for v in an.values()).items()))}
    tf_labels = {t: v["A_tier_only"]["label"] for t, v in by_tf.items()}
    readings = {"overall_A": overall["A_tier_only"]["label"], "overall_B": overall["B_tier_and_human_verified"]["label"]}
    for t, v in by_tf.items():
        readings[f"{t}_A"] = v["A_tier_only"]["label"]
        readings[f"{t}_B"] = v["B_tier_and_human_verified"]["label"]
    lab = "NEED_DATA" if all(r.get("lab_group_status") in (None, "UNKNOWN") for r in rows) else "UNKNOWN_RULE"
    return {
        "formulas": FORMULAS,
        "thresholds": {"share": SHARE_THRESHOLD, "K_neff": K_MIN_NEFF, "k_cell_groups": K_CELL_GROUPS},
        "rows": len(rows),
        "overall": overall,
        "by_target_family": by_tf,
        "by_analyte_summary": an_summary,
        "by_source_family": _source_family_table(rows),
        "losfo": losfo_feasibility(rows),
        "losfo_by_target_family": {t: losfo_feasibility([r for r in rows if r["target_family"] == t]) for t in tfs},
        "cells_k5": {"all_rows": cell_survival(rows), "eligible_pool_A": cell_survival(rows, pool_only=True)},
        "lab_disjoint": lab,
        "label_verdict": {"headline_overall_A": overall["A_tier_only"]["label"],
                          "weakest_across_target_families_A": _weakest(tf_labels.values()) if tf_labels else None,
                          "weakest_across_all_readings": _weakest(readings.values()) if readings else None,
                          "readings": dict(sorted(readings.items()))},
        "unknowns": [
            "UNKNOWN: 'target family' is not defined in the registry or contract; reported as whole ACTIVE set, SVAR.family, and analyte (SVAR canonical name).",
            "UNKNOWN: 'TEST-eligible tiers' is not defined beyond L-08 (E5/E6/E7/IMPUTED excluded); readings A (tier only) and B (tier + HUMAN_VERIFIED) are both reported.",
            "UNKNOWN: matrix-family and process-family taxonomies are not defined; raw matrix.food_group and the ordered process.steps tuple are used.",
            "UNKNOWN: what 'enough rows' means for leave-one-source-family-out; structural feasibility and the k=5 remaining-group reading are both reported.",
            "UNKNOWN: the FEASIBLE / DIAGNOSTIC_ONLY cut-offs of THR-08A-09 are not given; no cell verdict is issued, only counts at k=5 (k supplied by the work order).",
            "UNKNOWN: STUDY resolution needs confirmed experiment boundaries (D-10); none confirmed, so study-disjoint is unreachable today (L-06).",
        ],
    }


def join_rows(evd: Sequence[Mapping], keys: Sequence[Mapping], svar: Mapping[str, Mapping]) -> list[dict]:
    kmap = {k["evd_id"]: k for k in keys}
    out = []
    for e in evd:
        k = kmap.get(e["id"])
        if k is None:
            raise ValueError(f"no key record for {e['id']}")
        t = e.get("target") or {}
        sv = svar.get(t.get("state_variable_id")) or {}
        out.append({
            "evd_id": e["id"], "source_family": e.get("source_family_id"),
            "target_family": sv.get("family") or "UNKNOWN",
            "analyte": sv.get("canonical_name") or t.get("raw_name") or "UNKNOWN",
            "matrix_family": (e.get("matrix") or {}).get("food_group") or "UNKNOWN",
            "process_family": "+".join((e.get("process") or {}).get("steps") or []) or "UNKNOWN",
            "split_group_id": k["split_group_id"], "independence_resolution": k["independence_resolution"],
            "tier": e.get("tier"), "verification_status": (e.get("verification") or {}).get("status"),
            "lab_group_status": k.get("lab_group_status"),
        })
    return out
