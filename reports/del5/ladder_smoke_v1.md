# Ladder smoke v1 (qwen2.5:7b-instruct; dev demo questions, silver)

| rung | numeric claims | unsupported | UCR | fabricated citations |
|---|---|---|---|---|
| B0 | 0 | 0 | — | 0 |
| B2 | 5 | 4 | 0.8 | 3 |
| B5 | 17 | 12 | 0.706 | 0 |

Demo questions only (n=8); not a benchmark. B5 numbers must be cited and match packet rows.

## Analysis (2026-10-18) — negative result, kept
- B0 made no numeric claims (UCR undefined, not "0"); qwen2.5-7B answers vaguely without evidence.
- B5 UCR 0.71 overstates the problem partly: the checker missed multi-id citations "[EVD-1, EVD-2]" (fixed after
  this run; rerun pending). Real overreach remains: uncited numbers about NEAR foods ("potatoes … 60–75%"), RECOVER
  narrating cause-evidence numbers, invented "[1]" citations on non-evidence routes.
- Next: per-route B5 prompts (RECIPE_STATE, DIAGNOSIS/RECOVER render candidates not rows), post-hoc enforcement of the
  precision cap (strip numbers when QUALITATIVE), rerun with stored packets, then qwen2.5-32B.
