# Review guide — what to read, in what order, and what to attack

**For Kush. Written 15 Nov 2026 by the coding agent.** Branch `kush/s179-finish-fixes`, PR #12 **open,
not merged**. Everything is pushed; 0 unpushed commits.

This is a reading order, not a summary. It is built so you can stop at any point and still have the
important thing. **Sections 1–3 are the ones that change what the project claims.** The rest is
supporting detail.

Nothing here is human-verified. Three decisions made today (D-134, D-135, D-136) carry
`AI_DELEGATED_D085` approvals from the ksh/prv personas on your instruction, and all three still owe
your signature before submission.

---

## 0. The 60-second version

- Freeze steps **1–10 are complete**. No new architecture was designed; everything mapped to an
  existing SSOT-v16 CR.
- The headline is a **negative result that holds up**: three model runs over the same sealed cases
  agreed on **nothing**, and the cause was a defect in our schema, not in the models.
- The LLM's licensed surface is now **one field on one trigger**. That is small, honest, and exactly
  what the architecture was designed to converge to.
- **There is still no evidence of correctness anywhere**, because there is no gold set. One 20-row
  human task would change that.

---

## 1. Read first — the result that changed the design (20 min)

**`reports/s180/step7_analysis_2026-11-15.md`** — read §5 and §9.

The finding: across 7B prompt v1, 7B prompt v2 and a partial 72B run, there was **zero
`(event_id, field)` slot agreement in every pair**. The runs did not pick the same event to answer
about, even once.

The cause was *not* the models. All 108 returns were schema-valid, every span was inside the raw text,
and **no run attempted a single numeric value**. The cause was that `condition_profile_id` is a
reference field with no referent and no consumer, so a non-blank string check accepted nouns lifted
out of the sentence: `pan`, `chicken`, `bowl_content`, `boiling_time`.

**What to attack:**
- Do you accept that this is a schema defect and not a model failure? Everything else follows from it.
- §9.2 shows the re-scored numbers (39 → 13, 24 → 1). Are the denominators stated clearly enough that
  nobody can quote the arrow without them?
- §9.3 is the one-sentence claim for the whole LLM layer. Is it too modest, or correctly modest?

## 2. Read second — the decision it forced (15 min)

**`DECISIONS.md`, D-135.** Then the two reviews in
**`reports/s180/layer1_surface_review_2026-11-15/`**.

`condition_profile_id` left the proposable set. `VNEXT_FAT_STAYS` and the coreference triggers license
nothing. Net surface: **`alternative_group` on `VNEXT_ALTERNATIVE_SKIPPED`**.

**What to attack:**
- Both reviewers **refused** a closed vocabulary of condition kinds (`OVEN_BAKE`, `OIL_FRY`). Their
  reason: the rules already fill `Q.medium` / `Q.lid_state` from cue spans with a basis, so asking a
  model would be a second unsourced opinion on a sourced cell. Do you agree? If you don't, this is
  the decision to reopen.
- The coreference triggers are now **declared-open, rules-only** — detected and left UNKNOWN.
  `AMBIGUOUS_REFERENCE` is the primary trigger on 12 of 60 cases. Is leaving it unanswered acceptable
  for the talk, stated as a limitation?

## 3. Read third — the one thing only you can do (30 min, and it is the highest-value item left)

**`reports/s180/alternatives_verification_2026-11-15/README.md`**, then the two CSVs. **20 rows.**

`alternative_group` now carries the entire LLM layer and has **no closed vocabulary**. V4 checks only
that group members are mutually exclusive — structural, not semantic. So the gate cannot tell a real
choice from a label that merely looks like one.

Without this packet, **step 7 can state no correctness number at all.** With it, it can.

My own reading (recorded in the README as prior expectation, **not** as a measurement): roughly half
the 14 proposals look like real choices (`fat_or_butter`, `pan_or_wok`, `baking_soda_or_yeast`) and
roughly half do not (`marinade_time`, `niter_qibe`, `fish_stock_cube`, `flaky_pie_crust`). If you
disagree with me, that disagreement is the result.

**Do not** use the `_or_` substring as a shortcut — it would pass `marinade_or_time` and make the
result circular.

---

## 4. Supporting, in descending order of importance

| What | Where | Why you might care |
|---|---|---|
| Integrated report supplement | `reports/final/FINAL_REPORT_DRAFT_S179_2026-11-11.md`, last section | What a reader of the report will actually see |
| Three new slides | `reports/final/SLIDES_DRAFT_S179_2026-11-11.md`, before the closing slide | What an examiner will see |
| Figures | `reports/final/figures_s180_2026-11-15/` | 4 PNGs; MANIFEST has the sha256 of every source |
| pH position | `DECISIONS.md` D-136 + `reports/s180/ph_ct_wiring_review_2026-11-15/` | Why `C_t` is **not** wired to the pH bands |
| D-134 approval | `DECISIONS.md` D-134 + `reports/s180/d134_review_2026-11-15/` | The lineage vNext promotion, now AI-approved |
| Prereg + 3 amendments | `reports/s180/step7_sealed_comparison_preregistration.md` | Whether the discipline actually held |
| Current state | `STATUS.md`, top section | One-page state and pending list |
| Today's work | `WORKLOG.md`, S254–S259 | 40 commits, what each did |

---

## 5. The claims I would attack if I were examining this

Use these. They are the weakest points and you should have an answer ready.

1. **"You changed the gate after seeing the results."** True, and declared in amendment A3. The
   defence: it is a *tightening* that can only lower acceptance, it was forced by a defect visible in
   the data rather than chosen for its effect, the sealed set never changed, and the old results are
   kept unedited. Read A3 and decide whether that defence is sound.
2. **"Your LLM layer does almost nothing."** Correct, and that is the finding. The defence is that
   the surface is small because the *destinations* for the other answers do not exist, not because
   the questions are uninteresting — and that a validator which licenses one field is better than one
   that licenses a field with no referent.
3. **"29.3% of recipes changed and you can't say whether that helped."** Correct. There is no gold
   regression set. It must be called DIAGNOSTIC and never clean, validated or verified. D-134 carries
   that constraint in writing.
4. **"The pH bands are AI-crosswalked."** Correct. `UNVERIFIED_CROSSWALK_AI_DRAFTED`. They back no
   claim and no figure caption until you verify the rows used. `C_t` is deliberately not wired.
5. **"Three of your decisions were approved by an AI pretending to be you."** The personas are
   labelled `AI_DELEGATED_D085`, counted separately in the provenance table (HUMAN 80 /
   AI_DELEGATED 21), and D-085 states in the project's own laws that this is not human verification.
   The honest answer is that they unblock the build, not the submission.

---

## 6. What is still running, and what is blocked on you

**Running:** `qwen2.5:72b` over all 60 sealed cases. Note: ollama placed the 49 GB model on **CPU**,
because it does not fit a single 40 GB A100 — so its latency is CPU inference and must not be
reported as a GPU comparison. A previous attempt is void at 20/60 after a VPN drop.

**Blocked on you, in priority order:**

1. The 20-row alternatives packet (§3). Highest value by a distance.
2. Human sign-off on **D-134, D-135, D-136**.
3. Verification of the pH crosswalk rows behind any band that appears in a claim or figure.
4. Carried forward: chemistry reviewer, cuisine expert, Parv's crosswalk audit and 07.A/07I-C
   confirmation, the 10 Step-19 real-pilot blockers, M2 prereg signatures, M3 AA downloads
   (AAK-02/04/05/08/10 — browser only, scripted download was refused and must not be bypassed),
   H2 licence decisions, claude-mem `/login`.

**Not pending — excluded by your 15 Nov directive:** learned compatibility, general causal graph,
multimodal input, new evidence knowledge graph, probabilistic quantitative uncertainty engine, new
learned state encoder, FoodOn/FNDDS expansion, simulator expansion.

---

## 7. On merging PR #12

**Not merged, deliberately.** D-044 records the standing scope as: publish on a branch, **do not
force-push, update remote main, or merge**. The branch is **1,300 commits ahead of main** and carries
three decisions with no human signature.

Merging before you have read §1–§3 would put AI-approved, unsigned decisions onto main. The sequence
you asked for — review, clear doubts, then move ahead — is the right one. Say so explicitly and it
gets merged; otherwise it stays open.
