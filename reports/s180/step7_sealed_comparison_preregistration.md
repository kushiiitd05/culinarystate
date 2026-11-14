# Freeze step 7 — sealed Layer-1 comparison: pre-registration

**Status: REGISTERED, NO MODEL HAS BEEN RUN.** Written 15 Nov 2026 (S248) by the coding agent, from the 15 Nov architecture freeze. Committed **before** any hosted or local model sees a case. After this file is committed, nothing in §2–§5 may change: a change is a dated amendment committed before the first model result, or the attempt is void.

This registers a **small** comparison, as the freeze requires. It is not a benchmark and it cannot support a headline claim.

## 1. What is being compared, and why it is small

The freeze (item 7) says: keep hosted-LLM integration provider-agnostic, **stop broad model hunting**, and evaluate only a small number of viable providers against the same structured schema on a sealed hard-case set.

The 14 Nov probe already cut the field. Of the hosted candidates tried, only `nvidia/nemotron-3-ultra-550b-a55b` answered at all (4.8 s, valid JSON, correct on salt = INGREDIENT and oil kept); the rest returned 404, 503 or timed out. So the comparison is three arms, not a sweep:

| Arm | What it is |
|---|---|
| **D** deterministic | rules only, the existing Rung-A path with `lineage_vnext=True`. **Already recorded** in the seal manifest as `baseline` per case. |
| **L** local | Qwen2.5 on vinayak via the existing tunnel. No API key needed. |
| **H** hosted | `nvidia/nemotron-3-ultra-550b-a55b` via NVIDIA NIM. |

All three are asked for the **same structured proposal schema** — `composition/layer1_proposer.Proposal` — and all three pass through the identical gate in `layer1_proposer.review`. No arm gets a different prompt contract, a different validator, or a second chance.

## 2. The sealed set (frozen now)

Built by `tools/s180_seal_hardcases.py`, manifest `reports/s180/hardcase_seal_2026-11-15.json`.

- **60 cases**, selected from **1,880 eligible** out of **3,797** Wikibooks recipes scanned, **0 parse failures**.
- Eligible = at least one Layer-1 ambiguity trigger fires under rules alone.
- Seed `s180-layer1-hardcases-2026-11-15`; ranked inside each stratum by `sha256(seed ‖ pageid)`.
- Stratified by primary trigger. Selected: `VNEXT_ALTERNATIVE_SKIPPED` 15, `VNEXT_MIXTURE_COREF` 15, `AMBIGUOUS_REFERENCE` 12, `UNRESOLVED_LOT` 9, `VNEXT_FAT_STAYS` 9.
- Packet `data/interim/s180_hardcases/hardcases_60_s180-layer1-hardcases-2026-11-15.jsonl`, git-ignored, **SHA-256 `b926c303993541d5380e4531f495f9c89c2111a0c5c902e99df0ad95f15da6e7`**. The committed manifest holds pageid, revid, url, title, triggers and the deterministic baseline — **no step text** (verified).
- **Wikibooks only (CC-BY, public).** No BBC or other third-party raw text is in this set, because arm H sends the case text to an external API and only public or self-written text may go there. Every case is citable by pageid and revid.

## 3. What is measured (registered now)

Per arm, over the 60 cases:

1. **Gate acceptance rate** — accepted proposals / proposals returned.
2. **Rejection reasons**, as the counted histogram of the gate's own codes: `TRIGGER_NOT_IN_VOCABULARY`, `TRIGGER_DID_NOT_FIRE`, `FIELD_NOT_PROPOSABLE`, `NUMERIC_VALUE_NOT_ALLOWED`, `EVENT_NOT_IN_GRAPH`, `SPAN_OUT_OF_RANGE`, `WOULD_VIOLATE_INVARIANT`, `MALFORMED_PROPOSAL`.
3. **Schema compliance** — share of returns that parse into `Proposal` at all.
4. **Span validity** — share of accepted proposals whose span lies inside the raw text.
5. **Latency** per case, and failure/timeout count.
6. **Arm agreement** — pairwise agreement on `(event_id, field, value)` across D, L and H.

Arm D returns no proposals by construction: it is the floor. Its contribution is the baseline state already in the manifest, and the count of proposable slots the rules left open.

## 4. The gate, and what cannot happen

Acceptance is decided by `layer1_proposer.review`, not by any arm:

- a proposal **cannot be constructed without a span**, and `raw` is a required argument to `review`, so every span is range-checked;
- only categorical fields are proposable (`alternative_group`, `condition_profile_id`). `produces` / `consumes` are never proposable;
- any numeric-looking value is refused outright — **no numeric chemistry comes from a model**;
- a proposal whose trigger did not actually fire for that case is refused;
- V4 runs on the would-be graph, and anything that introduces a new issue code is refused.

So a model cannot widen the schema, invent lineage, or produce a number, whatever it returns.

## 5. How the result may be described

**This comparison is DIAGNOSTIC_ONLY.** There is **no gold** for Layer-1 proposals on these 60 cases, so:

- agreement between arms is **not** accuracy, and no arm may be called "correct" on the strength of it;
- the gate acceptance rate measures how often an arm respects the contract, **not** whether its proposal is right;
- no number from this comparison may be used as a headline claim, and none may enter a figure without the DIAGNOSTIC_ONLY label beside it;
- a provider is selected, if at all, on contract compliance, latency and cost — never on an accuracy claim this set cannot support.

Human verification of individual proposals stays a separate, human-only act (D-085: AI review ≠ human verification).

## 6. Order of execution

1. Commit this file and the seal manifest. **(no model has run)**
2. Arm D: already recorded in the manifest.
3. Arm L: local Qwen on vinayak. Needs VPN; no external data egress.
4. Arm H: hosted Nemotron-Ultra. **Sends public Wikibooks step text to NVIDIA NIM.** Needs the key at `~/.config/culinarystate/nvidia.env` (0600, outside the repo; rotate after the project) and an explicit go-ahead from Kush before the first call, since it is an external, metered call.
5. Write the result JSON beside this file, labelled DIAGNOSTIC_ONLY.

## 7. Labels carried by every artifact of this step

`DETERMINISTIC_BASELINE_RULES_ONLY` · `WIKIBOOKS_CC_BY_PUBLIC_TEXT_ONLY` · `SEALED_BEFORE_ANY_MODEL_RUN` · `NO_GOLD_SO_AGREEMENT_IS_DIAGNOSTIC`

---

## Amendment A1 — 15 Nov 2026, before any recorded model result

**What changed:** the gate now also refuses a proposal whose field is not licensed by its trigger
(`FIELD_NOT_LICENSED_BY_TRIGGER`, `layer1_proposer.TRIGGER_FIELDS`). Only `VNEXT_ALTERNATIVE_SKIPPED`
may bind `alternative_group`; every other trigger may touch `condition_profile_id` only.

**Why:** a 3-case throwaway probe of arm L (not recorded, written to `/tmp`) returned proposals that
the gate accepted although they were semantically wrong — `VNEXT_MIXTURE_COREF` was answered with
`alternative_group = "filling"` and `= "dish"`. Those are coreference answers smuggled in as an
alternatives binding. The gate could not see it, because any categorical string is structurally
valid. Shipping a gate that lets a coref answer through as a lineage choice would have made the
acceptance rate meaningless.

**Status of the sealed set:** unchanged. Same 60 cases, same seed, same packet SHA-256
`b926c303993541d5380e4531f495f9c89c2111a0c5c902e99df0ad95f15da6e7`. No case was added, removed or
re-ranked, and no arm result had been recorded when this amendment was written.

**Effect on §3 measures:** none are added or removed. `FIELD_NOT_LICENSED_BY_TRIGGER` joins the
rejection-reason histogram in measure 2.

**What this does not fix:** the gate still cannot judge whether a *licensed* value is the right one.
A plausible `condition_profile_id` that is simply wrong will be accepted. That is why §5 stands:
acceptance measures contract compliance, never correctness, and human verification stays separate.
