"""S178 PREREG lane: what each 07.A-R1 gate option tolerates, on SYNTHETIC label vectors (no real label exists).
Uses the project's own condition_agreement (gwet_ac1, cohen_kappa, _bootstrap: 2,000 condition resamples)."""
import json, sys
sys.path.insert(0, "src")
from culinarystate.evidence import condition_agreement as CA

F = CA.FIELDS
def build(D, per_cond=1, field_cycle=F, other="SHOULD_BE_AMBIGUOUS", na_share=0.0, one_sided=True):
    ids = [f"CA-{i:03d}" for i in range(1, 101)]
    A = {i: {f: "CORRECT" for f in F} for i in ids}
    B = {i: {f: "CORRECT" for f in F} for i in ids}
    # optional N/A block (agreed) to vary prevalence
    n_na = int(round(na_share * 900)); k = 0
    for i in ids:
        for f in F:
            if k < n_na:
                A[i][f] = B[i][f] = "N/A"; k += 1
    # place D disagreements on CORRECT cells
    placed = 0; ci = 0
    while placed < D:
        i = ids[ci % 100]; slots = 0
        for f in reversed(field_cycle):
            if placed >= D or slots >= per_cond: break
            if A[i][f] == "CORRECT" and B[i][f] == "CORRECT":
                A[i][f] = other if (one_sided or placed % 2 == 0) else "CORRECT"
                B[i][f] = "CORRECT" if (one_sided or placed % 2 == 0) else other
                placed += 1; slots += 1
        ci += 1
        if ci > 100000: raise RuntimeError("cannot place")
    return A, B, ids

def stats(A, B, ids, boot=False):
    a = CA._codes(A, ids); b = CA._codes(B, ids)
    raw = CA._exact(a, b)
    s = {"ac1": round(CA.gwet_ac1(a, b, q=7), 4), "kappa": round(CA.cohen_kappa(a, b), 4),
         "raw": round(raw, 4), "pabak_binary_as_coded": round(2 * raw - 1, 4), "pabak_q7": round((7 * raw - 1) / 6, 4)}
    if boot:
        s["ac1_boot_lo"] = round(CA._bootstrap(A, B, ids)[0], 4)
    return s

res = {}
for scen, kw in {"spread_1_per_condition_onesided": dict(per_cond=1),
                 "clustered_3_per_condition_onesided": dict(per_cond=3),
                 "spread_with_46pct_NA_agreed": dict(per_cond=1, na_share=0.46)}.items():
    pt = {}
    for D in range(0, 200):
        try:
            A, B, ids = build(D, **kw)
        except RuntimeError:
            break
        pt[D] = stats(A, B, ids)
    mx = lambda key, thr: max(D for D, s in pt.items() if s[key] >= thr)
    # bootstrap lower bound: binary search (monotone in D for these constructions)
    lo, hi = 0, mx("ac1", 0.95)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        A, B, ids = build(mid, **kw)
        if stats(A, B, ids, boot=True)["ac1_boot_lo"] >= 0.95: lo = mid
        else: hi = mid - 1
    A, B, ids = build(lo, **kw); at = stats(A, B, ids, boot=True)
    A, B, ids = build(lo + 1, **kw); above = stats(A, B, ids, boot=True)
    res[scen] = {"max_D_AC1_point_ge_0.80": mx("ac1", 0.80), "max_D_AC1_point_ge_0.95": mx("ac1", 0.95),
                 "max_D_AC1_bootlo_ge_0.95": lo, "stats_at_max": at, "stats_at_max_plus_1": above,
                 "max_D_kappa_ge_0.80": mx("kappa", 0.80),
                 "at_D": {D: pt[D] for D in (0, 5, 20, 45, 90, 180) if D in pt}}

# v4 reconstruction (REV-B F-01/F-03): Parv all CORRECT; Kush SBA on duration x4, temperature_value x1, 5 conditions.
ids = [f"CA-{i:03d}" for i in range(1, 101)]
A = {i: {f: "CORRECT" for f in F} for i in ids}; B = {i: {f: "CORRECT" for f in F} for i in ids}
for j, f in enumerate(["duration_judgement"] * 4 + ["temperature_value_judgement"]):
    A[ids[j]][f] = "SHOULD_BE_AMBIGUOUS"
v4 = stats(A, B, ids, boot=True)
dur = CA._field(CA._codes(A, ids, ("duration_judgement",)), CA._codes(B, ids, ("duration_judgement",)))[0]
v4["duration_field"] = {k: dur[k] for k in ("ac1", "exact_agreement", "disagreements", "top_disagreement_pairs")}
v4["optionA_duration_repeat_pair_flag"] = dur["top_disagreement_pairs"][0][1] >= 3
v4["optionA_pooled_bootlo_ge_0.95"] = v4["ac1_boot_lo"] >= 0.95
v4["positive_specific_agreement"] = 0.0  # 2*both_flagged/(flagged_A+flagged_B) = 0/(5+0)
res["v4_reconstruction"] = v4
json.dump(res, open(sys.argv[1], "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k.endswith("_max") or k == "v4_reconstruction"}, indent=1))
