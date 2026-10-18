# R4 graph expansion + near-evidence rule — analysis (2026-10-18)

Numbers: `graph_expansion_v1.md` (1,500 random measured cells, seed 7, leave-cell-out; fraction-scale MAE; silver).
SSOT: §241.1 R4 graph/evidence expansion, §241.3 categorical match types, §242.6 sufficiency modes.

| question | evidence | decision |
|---|---|---|
| Does the food graph add usable near evidence? | vertical hierarchy (ING parents + OFF parent/child/ancestor, RGN): coverage 7.1% -> 20.3%; on the 198 newly covered cells MAE 0.032 vs global process×target median 0.058, paired Δ **−0.026 [−0.035, −0.017]** | **promoted** (default relations) |
| Do OFF siblings help? | sibling medians MAE 0.183 vs 0.146 for the global median on the same cells; RG (with siblings) on its new cells Δ +0.018 [−0.003, +0.042] | not used (`siblings=False`); kept as an option |
| Should rows of unlinked foods count as NEAR when a food was asked? | RGU (old packet rule: matrix UNKNOWN allowed) on its new cells Δ **+0.018 [+0.012, +0.024]** — worse than the global median | **changed**: such rows make the packet BROAD_QUALITATIVE (direction only, "relation unknown"), never NEAR numbers |
| Group rows ("vegetables, such as broccoli")? | MAE 0.087 vs 0.075 on the same 51 cells, paired Δ +0.012 [−0.005, +0.029] (n.s.) | kept |
| Per relation vs global median (paired) | CHILD −0.028 [−0.040, −0.016], ANCESTOR −0.047 [−0.065, −0.029] (n=18), PARENT −0.008 [−0.022, +0.005], SIBLING +0.036 [+0.007, +0.070] | consistent with the decisions above |

Every relation is recorded per hit as `compat["match"]["matrix"]` (EXACT / PARENT / CHILD / SIBLING / ANCESTOR /
GROUP_ROW / FOOD_GROUP / NONE / UNKNOWN) and `["process"]` (EXACT / STEP / SAME_FAMILY / NONE / UNKNOWN).
Effect on demo answers: carrot beta-carotene and okra thiamin now answer qualitatively from unlinked foods instead
of quoting shellfish/flour numbers as "similar foods".
