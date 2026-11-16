# Deliverable gap-closure queue — D1…D5

**`AI_DRAFTED` · `NOT_HUMAN_REVIEWED` · 17 Nov 2026.** Closes no deliverable and no D-085 gate.
Freeze 19 Nov · submit 21 Nov. **No deliverable is PASS; all five are PARTIAL.**

Source keys (every number below is copied from the file named beside it):
`[CM]` `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md` ·
`[MP]` `handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md` · `[ST]` `STATUS.md` ·
`[S7]` `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md` · `[D]` `DECISIONS.md` ·
`[SI]` `reports/s179/state_inventory_FINAL_2026-11-15.md` · `[IR]` `docs/EVENT_IR_CONTRACT.md`. ·
`[D4M]` `reports/s181/d4_contract_metrics.md`.

Classification: **A** still closable before 19 Nov · **B** impossible or data-limited before freeze ·
**C** reportable only as a limitation. Ranking weighs contractual importance first (is it a named
success check in the proposal?), then time, dependency and risk.

## Ranked queue

| # | Deliv. | Gap (as worded in `[CM]`) | Class | Owner | Time / dependency / risk |
|---|---|---|---|---|---|
| 1 | **D1** | ≥40 hand-verified literature rows; ledger records **0** human-verified rows, all **17,978** ACTIVE rows tier E3 `[CM]` | **A** (only if started now `[MP §4]`), else **C** | **human-only** (cannot be delegated under D-085 `[CM]`) | No code dependency. Risk: partial count (<40) — then report the true count, not "met". |
| 2 | **D5** | chef/peer review **not performed** `[CM]` | **A** ("3–5 reviewed scenarios closes it honestly" `[MP §4]`), else **C** | **human-only** | Depends on the 8 backend scenarios (`tools/s179_submission_demo.py`, exists). Risk: reviewer availability. |
| 3 | **D3** | 40-gold-recipe evaluation **not performed**; no state-field accuracy, replay consistency vs gold, or merge/split F1 `[CM]` | **B** ("unlikely" `[MP §4]`) → **C** | **human (gold) + agent (scoring)** `[CM]` | Gold must exist before any scoring; AI-drafted gold is not gold (D-085). Do not substitute the 30 scripted sessions. |
| 4 | **D4** | The four contract metrics are now each accounted for in `[D4M]` (17 Nov): risk–coverage **ALREADY_REPORTED**, AURC computed (B7 partial AURC 0.0977 over coverage 0.45–1.0, n = 40); unsupported-claim rate **ALREADY_REPORTED** (B7 4/34 = 0.118; B2 24/43 = 0.558; machine checker, no human audit); condition-compatible Recall@K **computed but degenerate** (0.20 / 0.34 / 0.375 / 0.375 at K = 1/3/5/10, n = 20, rung B2 only, equals plain recall by construction); **ECE NOT_COMPUTABLE** (no per-item numeric confidence). Residual gap: ECE and a condition-discriminating Recall@K | **Agent work done.** Residual is **B → C** (data-limited: benchmark has no condition column; system emits categorical classes only `[D4M]`) | agent task closed; residual not closable by an agent before freeze | All `[D4M]` figures are MODEL_ASSISTED_GOLD · NO_HUMAN_SIGNOFF_D085 · POST_HOC_DIAGNOSTIC · NON_CITABLE. D4 stays **PARTIAL**. `[CM]` (16 Nov) predates `[D4M]` and still says "not all reported". |
| 5 | **D5** | demo is a backend scenario runner, not the "8-scenario Streamlit demo" the contract names `[CM]` | **A** (declare the substitution) / build per `[MP §9]` | agent (build) + human (sign wording) | `web/` and `tools/build_demo_snapshot.py` did not exist on disk on 17 Nov (checked) — see `docs/final/FINAL_COMPONENT_INVENTORY.md`. |
| 6 | **D2** | not every one of propensity weighting, split-conformal intervals, study-level bootstrap CIs demonstrated to the stated form `[CM]` | **A** partially `[MP §4]`, remainder **C** | agent, if scoped `[CM]` | `[CM]` says "not demonstrated" = not found by the drafting agent; first action is to re-check `reports/del2/`, not to recompute. |
| 7 | Layer-1 (supports D3/D5 narrative, not a named contract check) | human verification packet open: **35 proposals across three arms** `[S7 §4]` | **A** | **human-only** | `[MP §4]` describes this as "9 divergent rows … (~20 min)"; `[ST]` as "the 35-proposal packet" — see contradiction note below. |
| 8 | Governance | human sign-off owed on **D-134, D-135, D-136, D-137** `[ST]`, `[D] D-138` | **A** | **human-only** | Kush concurrence of 16 Nov is recorded as "not independent verification" `[D] D-134`. |
| 9 | pH axis 7 | crosswalk is `UNVERIFIED_CROSSWALK_AI_DRAFTED`; any band used in a claim or figure needs human row verification `[SI]`, `[D] D-136` | **A** for the few demo rows (tomato / vinegar / lemon juice are the named verification targets `[SI]`), else **C** | **human-only** | The tomato demo flow rests on ING-000010 pH 4.3–4.9 `[SI]`. |
| 10 | D3 | `STATE_REPLAY_FROM_EVENT_HISTORY` is an **open** V4 invariant, not checked `[IR §5]` | **C** | agent (post-freeze) | Must not be described as closed. |
| 11 | Lineage vNext | no gold regression set; DIAGNOSTIC `[D] D-134` | **B → C** | human (gold) | Data-limited. |

## Exact report wording allowed if the gap stays open

| # | Allowed wording (verbatim from the cited file unless marked *composed*) |
|---|---|
| 1 | "The row-count and provenance requirements are met; the hand-verified literature requirement is not. No row in the ledger has been verified by a human." `[CM]` |
| 2, 5 | "The benchmark and ablations exist at n=74 over 8 task types. The chef/peer review was not performed. The demo exists as eight backend scenarios rather than the interactive demo the proposal names." `[CM]` — and, if a web app is shown: "the proposal specified an 8-scenario Streamlit demo; we built an interactive web application covering the same eight scenarios." `[CM]` (only if that app actually exists at submission). |
| 3 | "The engine is built and runs corpus-wide; the 40-gold-recipe scoring prescribed by the contract was not performed, so no state-field accuracy or merge/split F1 is reported." `[CM]` |
| 4 | *Composed from `[D4M]`; replaces the `[CM]` sentence "…ECE is not reported", which is now incomplete:* "Risk–coverage and the unsupported-claim rate are reported. Condition-compatible Recall@K was computed but is degenerate — it equals plain recall because no benchmark question states a condition — so it shows nothing about condition-aware retrieval. ECE is not computable: the system emits categorical confidence classes, not per-item probabilities. All figures are post-hoc diagnostics on model-assisted gold." The decision-layer retriever itself was not measured (B2 hybrid baseline list only) `[D4M]`. |
| 6 | "H2 is addressed with negative results reported as the contract requires; not every prescribed statistical treatment is demonstrated." `[CM]` |
| 7 | *Composed from `[S7 §4]`:* "Layer-1 produces 21 grounded, contract-passing proposals on 60 sealed cases. There is no gold; the review is AI-delegated and not independent; no accuracy is claimed. The human packet is open." Per `[D] D-139` the report may say the proposals are **well-formed** and may **not** say they are **consequential**. |
| 8 | *Composed from `[D] D-138`:* "D-134…D-137 are AI-delegated (D-085) with recorded concurrence; human sign-off is owed." |
| 9 | *Composed from `[SI]`:* "A sourced pH table exists and is wired to the evidence compiler; the ingredient crosswalk is AI-drafted and unverified; `C_t` is not wired." Never "tomato sauce is acidic" `[MP §8]`. |
| 10 | *Composed from `[IR §5]`:* "Replay of state from event history is an open invariant; it is reported as not checked." |
| 11 | Permitted form `[D] D-134`: "DIAGNOSTIC; aggregate behaviour consistent with the intended corrections; **no gold regression set**." The 29.3% figure may not appear without "DIAGNOSTIC" in the same sentence. Never "clean", "validated" or "verified". |

## Forbidden in every case

"completed" for any deliverable `[MP §3]`; any SOTA claim `[MP §7]`; any accuracy number from the
Layer-1 comparison `[MP §8]`; presenting AI review as human verification (D-085).

## Contradictions / NOT_EVIDENCED found while writing this file

- **Packet size.** `[MP §4]` item 4: "9 divergent rows"; `[ST]` and `[S7 §4]`: "35 proposals across
  three arms"; an older `[ST]` block: "20-row alternatives packet". The count of rows still needing a
  *human* verdict after D-139 (ksh governs) is `NOT_EVIDENCED` in the files opened.
- **D3/D4 status label.** `[CM]` body rows read "STRONG CORE, EVALUATION PARTIAL" / "STRONG CORE,
  METRICS PARTIAL"; `[MP §3]` and `[D] D-138` read PARTIAL. This queue uses **PARTIAL**.
- **Hours required** for gaps 1–3: `NOT_EVIDENCED` (only "~20 min" for the packet is stated, `[MP §4]`).
- The contract wording quoted here is taken from `[CM]`'s quotations; the PDF
  `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf` itself was **not opened** by this drafting pass.
- **D4 metrics.** `[CM]` and `[MP §3–4]` (16 Nov) list Recall@K / risk–coverage / ECE as an open
  agent task; `[D4M]` (17 Nov) supersedes them. `[D4M]` also notes the frozen score JSON records
  "compat" recall as 0.0 (a missing-input artifact, not a measured zero) and that the frozen label
  "pooled_P1_P2_C" is P1+P2 in fact.
