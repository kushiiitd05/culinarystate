# D3 — status of the 40 gold recipes

**`AI_DELEGATED_D085` · `AI_PRECHECKED` · `NOT_HUMAN_VERIFIED`** · 17 Nov 2026. Read-only inventory: no
gold was created, edited or re-labelled. `~/.culinarystate_private` (sealed 15a list) and
`annotation/gold/deep_gold_pilot_v1/sealed_key_P1_A.json` were **not opened**.

Contract clause: *"Evaluated on 40 gold recipes and 30 scripted sessions: state-field accuracy,
replay consistency, merge/split F1."*

## Headline: the compliance matrix's D3 row is out of date

`reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md` says the 40-gold-recipe evaluation "was
not performed". **A scoring exists:** `reports/del3/compiler_vs_gold_pooled_S179.md` (run
RUN-S179-GOLD-001) reports all three contract metrics on 40 dev-gold recipes plus 7 P1 recipes. What
is missing is **gold of the kind a reader assumes the word means** — independent and held out. So the
gap is the *quality of the gold*, not the absence of an evaluation. The matrix wording should be
corrected by a human; this packet does not edit it.

## What exists

| Set | Recipes | Path | Who labelled it | Step events? |
|---|---:|---|---|---|
| pilot_20, Gold-v1.1 | 20 (BBC Good Food) | `annotation/gold/pilot_20_adjudicated_v1_1/` | AI-drafted (GPT model), accepted by Kush; Parv's review delegated to Kush (D-016, D-017); v1.1 corrections decided by Kush (S108) | yes — Merge 86, Transform 97, Split 21, Transfer 22, Discard 10, Reserve 1 |
| Food.com, AI-assisted v1.1 (joint) | 20 (Food.com) | `annotation/gold/foodcom_ai_assisted_v1_1/foodcom_v1_1_joint.json` | one AI proposal; Kush and Parv sets identical (per the S179 report) | yes |
| P1 side A ("P1-A") | 7 (BBC) | `annotation/gold/deep_gold_pilot_v1/A/` | report label `HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND`; **the files' own notes say "AI first pass by ksh; awaiting Kush review (D-045 W2)"** | yes — Merge 36, Transform 35, Split 8, Transfer 22, Discard 1 |
| evidence-first expansion | 20 + 20 | `annotation/gold/evidence_first_expansion/` | DRAFT, Kush and Parv | **no** — ingredient lines only, 0 step events; cannot score state |
| sealed 15a list | — | `~/.culinarystate_private` | not opened | — |

So **40 dev-gold recipes + 7 P1** = 47 with step events (the "47 gold recipes" in D-097 Lane T).
**None is independent gold** (D-017, D-060): every set started as an AI draft, and the engine was
developed with pilot_20 in view since S107. The 30 scripted sessions (`annotation/sessions/`, 30 files)
are a separate artefact and already pass (`reports/del3/sessions_v1.md`, deterministic replay true).

## Can the contract metrics be computed today? Yes — they already were

From `reports/del3/compiler_vs_gold_pooled_S179.md`, level P (no oracle):

| Metric (contract name) | P1 A (7) | pilot_20 v1.1 (20) | Food.com v1.1 (20) |
|---|---|---|---|
| State-field accuracy (final state fields correct) | 5/31 = 0.16 | 9/79 = 0.11 | 24/120 = 0.20 |
| Merge/split F1 (structural edges merge/split/reserve) | 0.36 | 0.36 | 0.47 |
| Replay consistency (recipes with replay issues) | 0 | 0 | 0 |

These are low, labelled `AI_DIAGNOSTIC · NOT_INDEPENDENT`, and not a held-out estimate. The report's
own allowed wording: *"against 7 P1 recipes and 40 AI-assisted dev recipes (not independent) the rule
compiler matched 11-20 % of final state fields."*

## Persona pre-check of the D3 items

| Item | ksh_AI_precheck | prv_AI_precheck | chef_AI_precheck | resolved (ksh governs) | chef differs from ksh |
|---|---|---|---|---|---|
| 1. Do 40 recipes with gold step events exist? | YES — 20 + 20 at the paths above | YES | NOT_APPLICABLE | YES | no |
| 2. Is it "gold" as the contract reader will understand it? | NO — AI-drafted, human-accepted, not blind, not held out; must be named as dev gold | NO — and its labels were never checked against what happens in the pan (e.g. whether a Transfer really moves the whole lot) | NOT_APPLICABLE | NO | no |
| 3. Are the three metrics computed? | YES — S179 pooled run, all three | YES | NOT_APPLICABLE | YES | no |
| 4. Is the compliance-matrix D3 wording accurate? | NO — "not performed" understates what exists; should say performed on non-independent dev gold | NO | NOT_APPLICABLE | NO | no |
| 5. Is P1-A's provenance label consistent with its files? | AMBIGUOUS — report says human-accepted, file notes say awaiting Kush review | AMBIGUOUS | NOT_APPLICABLE | AMBIGUOUS | no |
| 6. Are the gold step events plausible cooking? (spot-read of op counts only, no recipe-by-recipe read) | NOT_ASSESSED — structure only | AMBIGUOUS — Reserve appears once in 20 BBC recipes, which is low for recipes that set aside portions; may be the handbook's "whole-item RESERVE not written" rule (D-016) | AMBIGUOUS — cooks reserve pasta water, half a sauce, a garnish constantly; one Reserve in 20 recipes suggests the gold under-records it, which would also depress the merge/split F1 on reserve | NOT_ASSESSED | **YES** |

Each persona judged 6 items (chef 1 of 6, NOT_APPLICABLE on 5). ksh/prv differ on 1 (item 6); chef
differs from ksh on 1 (item 6).

## Smallest honest path to closing D3 by 19 Nov

1. **(Kush, ~10 min) Settle the P1-A label** (item 5): either confirm the 7 files were reviewed, or
   relabel them AI-drafted in the report.
2. **(Kush or Parv, ~45–60 min) Human spot-audit of the existing 40**: open 5 pilot_20 and 5 Food.com
   gold files, read each recipe's final state fields and merge/split events against the recipe text,
   and record agree / disagree per field. This does **not** make the set independent; it lets the
   report say a human re-checked a stated sample. Use a new sheet under this folder; do not edit the
   gold files.
3. **(agent, after 2)** nothing to re-run — the metrics stand; only the wording changes.

What cannot be done honestly by 19 Nov: blind, independent gold on unseen recipes. Drafting new gold
with an AI and calling it gold is excluded.

Wording for each state is in `REPORT_WORDING.md`.
