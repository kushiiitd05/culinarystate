# PARV — LATEST PROMPT, 19 Nov 2026 (CulinaryState) — report, deck, proposal, demo story

> **`AI_DRAFTED` · `NOT_HUMAN_REVIEWED`.** Paste this whole file into Claude Code at the repo root.
> Resolution rule: **ksh governs** (D-139). Closes no deliverable and no D-085 gate.

**Read order:** this file → `handoff/PARV_HANDOVER_2026-11-17.md` (task list A1–A5, B1–B10, `/live` setup)
→ `handoff/PARV_FINAL_EXECUTION_MASTER_PROMPT.md` (thesis, language rules, design system).
Where they differ, **this file wins**. It adds three things: what is still left, the **design decision**
for report + deck + proposal, and the **story and screenshot plan** for the demo.

**Dates:** freeze **today, 19 Nov** · verify **20 Nov** · submit **21 Nov** · rehearsal **24 Nov** · present **25–26 Nov**.

---

## 0. First ten minutes

```bash
git fetch && git switch kush/s181-explorer-build && git pull
/opt/anaconda3/bin/python -m pytest -q          # full suite; quote only the count you just saw
```
Then fill in the table in §1 with what is **actually** done on your machine. Do not trust it as written.

## 1. What is left (state at 19 Nov, Kush's side)

Last push on `origin/kush/s181-explorer-build` is `99482c6` (17 Nov). Nothing from Parv has reached the
remote since, so every item below shows as open. Mark what you finished locally, then push.

| # | Item | Owner | State |
|---|---|---|---|
| A1 | D1: 40 hand-verified literature rows (`reports/s181/human_audit/D1_*`) | **human** | open |
| A2 | D5: one real chef/peer review of the 8 scenarios | **human** | open |
| A3 | Proposal packet: 9 rows where ksh/prv differ | **human** | open |
| A4 | D3: spot-audit 10 gold recipes | **human** | open |
| B1 | Decision record for the `_triple` range bug | agent | open |
| B2–B3 | Hide `/live` in public build; deploy snapshot-only to Vercel | agent | open |
| B4–B5 | `tools/preflight.sh` + Playwright; freeze tag + manifest hashes | agent | open |
| B6 | Final report → PDF | agent | open |
| B7 | Deck → PPTX + PDF | agent | open |
| B8 | Submission zip | agent | open |
| B9 | Rehearsal script + fallback video of `/live` | agent + Parv | open |
| **N1** | **Screenshot set** (§6) | agent | new |
| **N2** | **Business proposal** — 1 slide + 1 page (§7) | agent | new, **confirm with Kush it is wanted** |
| **N3** | **Answer-diff panels** for the 4 stories (§5) | agent | new |

**Order for today:** A1 starts now, by hand, in parallel with everything else → B1 → B5 freeze → N1 screenshots
(need a frozen build) → B6/B7 (need the screenshots) → N2 → B2/B3 deploy → B8 on 20–21 Nov.
If A1–A4 are not done by 20 Nov, use the "not done" sentence in `reports/s181/human_audit/REPORT_WORDING.md`.
Never write around a gap.

---

## 2. Design decision — **minimal and direct** (decided; do not reopen)

One style for report, deck, proposal and screenshots:

1. **The title is the claim.** Every slide title is one full sentence that states the finding
   ("One ingredient changes the route"), not a topic ("Results"). The body is the evidence for that sentence.
2. **One idea per slide.** At most one figure or one table, at most ~30 words of body text.
3. **Every number has a source line** in small mono text at the slide foot (path to the frozen artifact).
   `slides.py` already does this with `source(...)`; keep it on every slide you add.
4. **No decoration.** No stock photos, icons used as ornament, gradients, or emoji. Colour only for status,
   using the palette already in `reports/final/deck/build_deck.py` (ink, blue = grounded, amber = UNKNOWN/limit, slate).
5. **UNKNOWN and limits are shown, not hidden.** Each results slide carries its limit in one line.
6. **Light background**, which projects well. Use the system fonts already in `build_deck.py` (Georgia / Helvetica Neue /
   Menlo), because PPTX does not embed fonts and the presenting laptop may not have IBM Plex. The web app keeps the
   design-system fonts.
7. **Report = deck story in long form.** Same section order, same numbers, same figures.

## 3. What we did, in a nutshell (content the deck and report must carry)

Regenerate every number from the artifact named. Do not copy from this table. **Reconcile the recipe counts:**
612,782 (recipe base v1), 611,902 (compiler corpus run) and 612,903 (similar-search titles) are three different
populations. State each one with its definition, or use one.

| Theme | What to say | Source |
|---|---|---|
| **Problem** | Cooking assistants treat a recipe as text: no food state, no process effect, confident with no evidence. | proposal brief §1 |
| **Data and sources** | Recipes: Food.com, BBC Good Food (local only, D-003), TASTEset, Wikibooks (CC BY-SA), Project Gutenberg (public domain). Evidence: USDA SR Legacy, Phenol-Explorer, FDA/CFSAN pH. Licence per family, counts only redistributed. | `registry/recipe_source_usage_registry_v1.csv`, `reports/final/RELEASE_CARD.md` |
| **D1 ledger** | 17,978 active evidence rows, each with source + tier; 0 of 40 hand-verified rows (unless A1 done). | compliance matrix, release card |
| **D2 sparsity** | splits + baselines, negative results reported; not every statistic shown. | compliance matrix |
| **D3 state engine** | `S_t=(G,C,Q,Y,P)`, event-sourced, 30 scripted sessions, corpus-wide replay; six invariants. | `docs/final/FINAL_STATE_SCHEMA.md` |
| **D4 retrieval + abstention** | compatibility MATCH / MISMATCH / UNKNOWN (unknown ≠ mismatch); unsupported-claim rate B7 4/34 vs B2 24/43; ECE not computable. | `reports/s181/d4_contract_metrics.md` |
| **D5 end-to-end** | 74 questions / 8 task types, baseline ladder, ablations, 8 scenarios; H1, H3 RULE_NOT_MET. | `reports/del5/d5_score_v1_D085/` |
| **Models and comparisons** | NER DeBERTa-base+CRF (tie on a clean split; **the protocol-leak finding is the result**) · dense retrieval e5-large-v2 · Layer-1 proposer qwen2.5 7B vs 72B × prompt v1 vs v3 (**0 → 21 grounded**; grounding was a protocol defect, model size did not fix it) · `/live` Nemotron-Ultra (NIM) through the system vs plain. | `STATUS.md`, `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md` |
| **Tests** | full unit-suite count from today's run; s181/s182 suites; preflight + Playwright once B4 lands. | your pytest output |
| **Negative results** | H1/H3 not met, NER no win, lineage vNext diagnostic only, pH/salt/fat fractions always UNKNOWN. | master prompt §7, handover §4 |
| **What is left** | the open rows of §1, worded with `REPORT_WORDING.md`. | — |

## 4. Deck structure (~18 slides; extend `reports/final/deck/slides.py`, keep its 15)

Existing order stays: title · problem · compliance · pipeline · state · compatibility · tomato · plain-LLM ·
D4 · Layer-1 · pH · NER · negative · app · close. **Add four, at these places:**

| New slide | Insert after | Title (the claim) | Body |
|---|---|---|---|
| `s02b_data` | problem | "Five recipe families and three evidence sources, each with its own licence" | one table: family · count · licence · leaves the Mac? |
| `s12b_models` | NER | "Bigger models did not fix grounding; the protocol did" | one table: model · role · compared against · result · label |
| `s14b_live` | app | "Same model, different context" | §5 diff panel for one story + screenshot of the 7-stage pipeline |
| `s14c_business` | live | §7 title | §7 one-slide layout |

Put the honest-limits slide second to last, before "Questions". Talk time is ≈6 min of demo plus the deck,
so **cut slides before adding words**.

## 5. Stories — how to depict them (4 stories, one format)

Each story is told in **one panel with four rows**, in this order. The same panel goes in the deck, the report and the rehearsal.

```
QUESTION      the user's words, verbatim
PLAIN MODEL   its answer, verbatim, with invented values marked [no source]
CULINARYSTATE its answer, verbatim, every claim tagged [EVD-…] / (step N: field = value ✓) / UNKNOWN: reason
WHY           the one pipeline stage that made the difference, plus the one honest limit
```

| # | Story | The difference to show | Limit to state |
|---|---|---|---|
| 1 | **Tomato A–D** (`/compare`, snapshot) | one ingredient changes state, so the evidence route changes; tomato pH 4.3–4.9 straddles 4.6, so the system refuses "acidic" | crosswalk is AI-drafted |
| 2 | **Carrots came out mushy** (`/live`) | the advice cites simulated thermal dose and state facts, each checked against the trace (✓) | the advice itself is unverified; simulated ≠ measured |
| 3 | **Tomatoes · vitamin C** (`/live`) | cited USDA 95.0 % [EVD-002765] vs plain model's invented "40–60 %" | the plain model is sometimes fine; say so |
| 4 | **Chicken · is it safe?** (`/live`) | refused before any model call | refusal is by design, not a capability |

Rules: answers are **pasted verbatim** from a saved run (JSON in `reports/final/screens/runs/`), never retyped.
Temperature 0, but state the run date. **No "more accurate" wording.** There is no gold.

## 6. Screenshots and demo links (N1)

Capture with Playwright from the **frozen** build at 1600×1000, light mode, into `reports/final/screens/`
with a `MANIFEST.json` (file, route, commit, timestamp, sha256):

`01_landing` · `02_lab_tomato_state` · `03_lab_unknown_axis` · `04_compare_A-D` · `05_method_pipeline` ·
`06_live_pipeline_ticking` · `07_live_answer_carrots` · `08_live_compare_plain_carrots` · `09_live_vitc_compare` ·
`10_live_similar_recipes` · `11_live_safety_refusal` · `12_snapshot_signature_badge` · plus `04_compare_A-D?vision=deut`
as the colour-blind check.

Demo links go on the close slide, in the report appendix and in the submission README:
- **Public:** Vercel URL (snapshot only, signature badge visible).
- **Local live:** `./tools/live_demo.sh` → `localhost:3000/live`, which needs your own key in `~/.config/culinarystate/nvidia.env`.
- **Fallback:** the B9 screen recording, linked and also inside the zip.
Never show a private host path, a key or BBC/Food.com text in any screenshot.

## 7. Business proposal (N2), only if Kush confirms it is required

One slide plus one page in the report appendix, written in the same minimal style. **No market-size numbers
unless they are cited; no accuracy claims.**

| Block | Content |
|---|---|
| Problem | cooking assistants answer confidently without evidence or food state |
| User / buyer | recipe platforms, smart-appliance makers, meal-kit and nutrition apps (B2B API) |
| Product | state-tracking + evidence-grounded answer API that says UNKNOWN with a reason |
| Why us | event-sourced food state + licensed evidence ledger + claim verifier; the LLM is replaceable |
| Proof today | the 4 stories in §5 and the compliance matrix, PARTIAL stated honestly |
| Risks | data licences (BBC/Food.com local only), no independent gold, pH/salt/fat ungrounded |
| Next 3 steps | human-verified gold set · chef review at scale · licensed recipe partner |

## 8. Report (B6)

Same order as the deck: problem → data → D1…D5 (each: what, number, limit) → models and comparisons →
stories (§5 panels) → negative results → what is left → demo links → reproducibility index.
Update `reports/final/FINAL_REPORT_DRAFT_S179_2026-11-11.md` plus `sections/S180_freeze_results_DRAFT.md`; do not start
a new draft. Export: pandoc → HTML → Chrome print → `reports/final/CulinaryState_final_report.pdf`.

## 9. Laws (unchanged; full list in the 17 Nov handover §5)

No invented values · AI review ≠ human verification · `src/` frozen without a decision record · BBC/Food.com raw
text never leaves the machine · your own NVIDIA key, never committed · one commit per file, tests first, no AI
attribution · push every session · log in `WORKLOG.md`.

**Stop and ask Kush** only for: a science/governance call ksh cannot make, a credential, a missing file, or the P1-A
label. Format: QUESTION · RECOMMENDED · ALTERNATIVES · CONSEQUENCE · DEADLINE IMPACT.

## 10. Finalise everything — definition of done (by 21 Nov)

Finish the whole project, not only the slides. Tick each line in `STATUS.md` with the commit that closed it:

- [ ] A1–A4 done by a human, **or** the "not done" sentence from `REPORT_WORDING.md` is in report + deck
- [ ] B1 decision record merged; full test suite green; count quoted from that run
- [ ] Freeze tag on the frozen commit; snapshot `--check` FRESH; manifest hashes in `STATUS.md`
- [ ] Vercel URL live (snapshot only, `/live` hidden, signature badge visible)
- [ ] `reports/final/screens/` complete with `MANIFEST.json`
- [ ] `CulinaryState_final_report.pdf` and `CulinaryState_final.pptx` + PDF tell the same story with the same numbers
- [ ] Business proposal slide + page (if Kush confirmed)
- [ ] Fallback video recorded; rehearsal script in `handoff/`
- [ ] Submission zip built, `unzip -t` clean, hashes verified on a fresh extract, no key / private path / BBC or Food.com text inside
- [ ] Everything pushed, PR `kush/s181-explorer-build` → `main` opened, `WORKLOG.md` updated
- [ ] One-line WhatsApp to Kush: what is DONE, what is PARTIAL and why

If something cannot be finished, **say so in the report and deck**, never leave it silent.

**The one thing to remember:** minimal, direct, sourced. Each slide is one sentence with its evidence,
and D1, the chef review and the proposal packet are still human work.
