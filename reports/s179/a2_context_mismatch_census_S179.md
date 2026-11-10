# A2: CONTEXT_MISMATCH route, router census old vs new (S179)

Status: **NON_CITABLE, counts only.** D-084 item 7 accepted CONTEXT_MISMATCH as a route value (H4 enum change). It
is added test-first (`tests/unit/test_s179_context_mismatch_route.py`) and is opt-in
(`EvidenceGates(context_mismatch_route=True)`, census flag `--context-mismatch-route`), so the S176-S178 records stay
reproducible.

**Rule.** The router says CONTEXT_MISMATCH when the lot-context gate withheld a DIRECT / BRACKETING pre-check
(reason MERGED_LOT_CONTEXT, PRIOR_PROCESS_CONTEXT, PRIOR_PROCESS_UNRESOLVED or LOT_CONTEXT_UNKNOWN) and the engine has
nothing weaker than UNKNOWN. Meaning: "a table row exists for this pair, but not for this food in this context". It has
the strength of UNKNOWN, so it never upgrades a route, and its §141 class is `unsupported`. TARGET_ABSENT stays
NOT_APPLICABLE. SIMULATE may still replace it, exactly as it replaced UNKNOWN before.

Vitamin C (SVAR-000009), seed 20261104, gates on.

| Census | Run (flag off) | Run (flag on) | ungated DIRECT | DIRECT | CONTEXT_MISMATCH | NOT_APPLICABLE | UNKNOWN (off -> on) |
|---|---|---|---|---|---|---|---|
| non-BBC, 1,000 recipes (57,511 items) | RUN-S179-ROUTER-007 (Mac) = RUN-S179-ROUTER-005 (vinayak) | RUN-S179-ROUTER-008 | 450 | 57 | 358 | 113 | 57,341 -> 56,983 |
| BBC full, 11,934 recipes (1,103,301 items, Mac only, D-003) | RUN-S179-BBC6-005 | RUN-S179-BBC6-007 | 6,125 | 1,058 | 4,904 | 2,044 | 1,100,199 -> 1,095,295 |
| non-BBC full (vinayak) | RUN-S179-ROUTER-006 | RUN-S179-ROUTER-009 | 267,933 | 30,220 | 224,240 | 74,597 | 35,151,784 -> 34,927,544 |

- DIRECT is the same with the flag off and on in every run: the flag only names what was already withheld.
- Flag off on the Mac reproduces the committed vinayak 1,000-recipe report on every non-provenance key, so the two
  hosts agree for this census.
- In the 1,000 sample, of the 450 ungated DIRECT items: 57 stay DIRECT, 358 are CONTEXT_MISMATCH and 35 stay UNKNOWN
  (non-step event roles: attributive state or serving suggestion, S178 R3).
- BBC run note: `code_unchanged_during_run` is false only because `git_dirty` flipped (an untracked tools file was
  written during the run); every code hash and the src tree hash are equal (RUN-S179-BBC6-007 notes).

Outputs: `reports/step23/router_demo_census_vitc_nonBBC_1000_S179_cm{off,on}.json`,
`reports/step23/router_demo_census_vitc_BBC_full_S179_cmon.json`.
