"""S178 PREREG lane: exact McNemar / sign-test / Clopper-Pearson tables for the amendment drafts.
Uses the project's own paired_stats.mcnemar_exact (two-sided exact binomial on discordant pairs).
Run from the worktree root:  <python> -I <this file>   (adds ./src to sys.path itself)."""
import json, math, sys
sys.path.insert(0, "src")
from culinarystate.evaluation.paired_stats import mcnemar_exact
from scipy.stats import beta, binom

ALPHA = 0.05
out = {}

# 1. Minimum discordant split for two-sided exact McNemar p <= 0.05, per d.
def min_split(d):
    for b in range(d, -1, -1):
        pass
    best = None
    for b in range(d + 1):           # b = B4-only, c = d - b; need b > c
        c = d - b
        if b > c and mcnemar_exact(b, c) <= ALPHA:
            return b, c, mcnemar_exact(b, c)
    return None

ms = {}
for d in range(1, 61):
    r = min_split(d)
    ms[d] = None if r is None else {"b": r[0], "c": r[1], "p": round(r[2], 5)}
out["mcnemar_min_split"] = ms
for n in (30, 60):
    rows = []
    for d in range(1, n + 1):
        r = ms[d]
        if r:
            rows.append((d, r["b"], r["c"], round((r["b"] - r["c"]) / n, 4), r["p"]))
    out[f"min_sig_gap_n{n}"] = min(rows, key=lambda x: x[3])
    out[f"min_split_rows_n{n}"] = rows

# 2. Exact power: D ~ Bin(n, psi) discordant pairs; B | D ~ Bin(D, pi); pi = (1 + gap/psi)/2.
def power(n, gap, psi):
    if gap > psi + 1e-12:
        return None
    pi = (1 + gap / psi) / 2
    tot = 0.0
    for d in range(0, n + 1):
        pd = binom.pmf(d, n, psi)
        if pd < 1e-15:
            continue
        r = ms.get(d) if d >= 1 else None
        if not r:
            continue
        bmin = r["b"]                    # rejection region in favour of B4: b >= bmin (monotone)
        # check monotonicity: every b >= bmin is significant
        tot += pd * binom.sf(bmin - 1, d, pi)
    return tot

grid = {}
for n in (30, 45, 60):
    for gap in (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40):
        for psi in (0.20, 0.30, 0.40, 0.50):
            p = power(n, gap, psi)
            grid[f"n{n}_gap{gap:.2f}_psi{psi:.2f}"] = None if p is None else round(p, 3)
out["power_grid"] = grid
# REV-B scenarios
out["revb_scenarios"] = {f"gap{g}_psi{ps}_n{n}": round(power(n, g, ps), 3)
                         for (g, ps) in ((0.30, 0.40), (0.20, 0.30), (0.15, 0.25), (0.10, 0.20)) for n in (30, 45, 60)}
# MDE at 80% power per psi
mde = {}
for n in (30, 60):
    for psi in (0.20, 0.30, 0.40, 0.50):
        g = None
        for k in range(1, int(psi * 1000) + 1):
            gg = k / 1000
            p = power(n, gg, psi)
            if p is not None and p >= 0.80:
                g = gg
                break
        mde[f"n{n}_psi{psi:.2f}"] = g
out["mde80"] = mde
# monotonicity check of rejection region
mono_ok = all(all(mcnemar_exact(b, d - b) <= ALPHA for b in range(ms[d]["b"], d + 1)) for d in ms if ms[d])
out["rejection_region_monotone"] = mono_ok

# 3. Sign test (H3): m questions where exactly one of (B2, B7) has an unsupported claim; k favour B7.
st = {}
for m in range(1, 41):
    one = next((k for k in range(m + 1) if binom.sf(k - 1, m, 0.5) <= ALPHA), None)
    two = next((k for k in range(m + 1) if k > m - k and min(1.0, 2 * binom.sf(k - 1, m, 0.5)) <= ALPHA), None)
    st[m] = {"one_sided_min_k": one, "p1": None if one is None else round(binom.sf(one - 1, m, 0.5), 5),
             "two_sided_min_k": two, "p2": None if two is None else round(min(1, 2 * binom.sf(two - 1, m, 0.5)), 5)}
out["sign_test_min_split"] = st

# H3 sign-test power: n questions; per question P(B2 unsupp & B7 clean)=r, P(B7 unsupp & B2 clean)=s.
def sign_power(n, r, s, sided="one"):
    tot = 0.0
    for m in range(0, n + 1):
        pm = binom.pmf(m, n, r + s)
        if m == 0 or pm < 1e-15:
            continue
        k0 = st[m]["one_sided_min_k" if sided == "one" else "two_sided_min_k"]
        if k0 is None:
            continue
        tot += pm * binom.sf(k0 - 1, m, r / (r + s))
    return tot
sp = {}
for n in (40,):
    for r in (0.05, 0.10, 0.15, 0.20, 0.30):
        for s in (0.0, 0.025, 0.05):
            sp[f"n{n}_r{r:.3f}_s{s:.3f}"] = {"one": round(sign_power(n, r, s, "one"), 3), "two": round(sign_power(n, r, s, "two"), 3)}
out["sign_power"] = sp

# 4. Clopper-Pearson one-sided 95% bounds for x defects in 100 conditions.
cp = {}
for x in range(0, 9):
    ub = 1.0 if x == 100 else beta.ppf(0.95, x + 1, 100 - x)
    cp[x] = {"upper95_defect": round(ub, 4), "lower95_accuracy": round(1 - ub, 4)}
out["cp_100"] = cp
# two-sided 95% for x/n generic helper outputs used in the human claim audit (10 claims per rung)
cp10 = {}
for x in range(0, 11):
    lo = 0.0 if x == 0 else beta.ppf(0.025, x, 10 - x + 1)
    hi = 1.0 if x == 10 else beta.ppf(0.975, x + 1, 10 - x)
    cp10[x] = (round(lo, 3), round(hi, 3))
out["cp_two_sided_n10"] = cp10

# 5. Planted rows: P(reviewer flags >= k of 10) for true sensitivity theta.
pr = {}
for k in (7, 8, 9):
    pr[k] = {f"{t:.2f}": round(binom.sf(k - 1, 10, t), 3) for t in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)}
out["planted_pass_prob"] = pr
# CP one-sided lower bound on sensitivity for k/10 detected
out["planted_cp_lower95"] = {k: round(0.0 if k == 0 else beta.ppf(0.05, k, 10 - k + 1), 3) for k in range(0, 11)}

json.dump(out, open(sys.argv[1], "w"), indent=1, default=str)
print("ok")
