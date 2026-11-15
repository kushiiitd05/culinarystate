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

---

## Amendment A2 — 15 Nov 2026, written after arm L v1 was recorded

**Disclosure first: arm L v1 had already been run and committed when this amendment was written.**
Its result is kept unchanged (`reports/s180/step7_arm_L_qwen7b_2026-11-15.json`, 60/60 answered,
schema 1.000, gate acceptance 0.4643, rejections `FIELD_NOT_LICENSED_BY_TRIGGER` × 45), exactly as
the pre-registration rule requires: the old result is kept and the change is logged.

**What changed, and why it is a defect not a tuning choice.** The v1 prompt offered *both* proposable
fields on every case:

```
"field": "alternative_group" or "condition_profile_id"
```

It did this regardless of which trigger fired, because the prompt was written before
`layer1_proposer.TRIGGER_FIELDS` existed. The gate then rejected the unlicensed choice. So the arm
was handed an option it was not allowed to take and penalised for taking it. All 45 rejections are
that one mistake, concentrated on the coreference and lot-resolution triggers
(`AMBIGUOUS_REFERENCE` 15, `VNEXT_MIXTURE_COREF` 13, `UNRESOLVED_LOT` 11).

**v2 changes the prompt only:**

1. the prompt names **only the field(s) the fired trigger licenses**, per `TRIGGER_FIELDS`;
2. each trigger is stated as the question it actually asks, instead of as a bare token.

**What does not change:** the sealed set (same 60 cases, same seed, same packet SHA-256
`b926c303993541d5380e4531f495f9c89c2111a0c5c902e99df0ad95f15da6e7`), the `Proposal` schema, the gate,
and the §3 measures. **The gate is not loosened.** Acceptance is not a target: raising it by relaxing
a check would be the one forbidden fix.

**How both runs are reported.** v1 and v2 are reported side by side and the delta is the result. A
single post-fix number would be tuning on a set whose results had been seen; the pair is the honest
object and is also the more informative one — it measures what contract-aware prompting is worth on
this task. Neither number is accuracy: §5 stands, there is no gold.

**Registered expectation, before running v2:** acceptance rises materially above 0.4643 but does
**not** approach 1.0. If it did, that would indicate the prompt had become an answer key rather than
a question, and the run would be reported as such rather than as a success.

---

## Amendment A3 — 15 Nov 2026, written and committed before the 72B result exists

**What changed:** the gate. D-135 removed `condition_profile_id` from `PROPOSABLE_FIELDS` (it is a
reference field with no referent and no consumer) and closed `VNEXT_FAT_STAYS` and the coreference
triggers. The licensed surface is now **one field, `alternative_group`, on one trigger,
`VNEXT_ALTERNATIVE_SKIPPED`**. New rejection code `FIELD_REQUIRES_EXISTING_REFERENT`;
`REJECTION_CODES` is declared and closed.

**Why this is not tuning.** §4 of this pre-registration says acceptance is decided by the gate, so a
gate change is material and must be declared. It is a **tightening**: it removes licensed surface and
can only lower an arm's acceptance count, never raise it. It was not chosen after seeing which arm it
favoured — it was forced by §5 of `step7_analysis_2026-11-15.md`, where three runs showed zero slot
agreement and the accepted values (`pan`, `chicken`, `bowl_content`, `boiling_time`) showed the field
was taking nouns from the sentence. The change was reviewed ACCEPT_WITH_CHANGES by ksh and prv
(AI, D-085) before implementation.

**Status of the sealed set:** unchanged. Same 60 cases, same seed, same packet SHA-256
`b926c303993541d5380e4531f495f9c89c2111a0c5c902e99df0ad95f15da6e7`. No case added, removed or
re-ranked.

**Status of recorded results:** kept, unedited. `step7_arm_L_qwen7b_2026-11-15.json` and
`step7_arm_L_qwen7b_v2_2026-11-15.json` stand as registered. Their re-scored figures (39 → 13,
24 → 1) are reported beside the recorded ones with denominators, never instead of them.

**One asymmetry, declared now.** The 7B runs were gated under the old gate and are re-scored by
filtering accepted proposals on field name. The 72B run will be gated live under the new gate. The
filter is deterministic on field name and the two routes give the same set, but they are not the same
procedure and this is recorded so no one discovers it later.

**Registered expectation, before running 72B:** on the 18 cases with a licensed trigger, 72B accepts
**more than 13** `alternative_group` proposals (the 7B v1 re-scored count) if scale helps on this
task, and **about 13 or fewer** if the task is limited by the prompt and the schema rather than by
model capability. Either outcome is reportable. Neither is accuracy: there is still **no gold**, §5
stands, and only the human packet in
`reports/s180/alternatives_verification_2026-11-15/` could make these proposals correct or incorrect.

**What would void this run:** any case not reaching the model. The previous 72B attempt is void at
20/60 after a VPN drop, and a partial on a stratified sealed set is not an arm.

---

## Amendment A4 — 15 Nov 2026, written while the 72B run is still in flight and before its result exists

**What changed:** the gate again. `span_grounds_value` now requires a proposal's span to contain a
standalone coordinator (`or` / `either`) that is not part of an endpoint construction
(`or until|till|when|so`). New code `SPAN_DOES_NOT_GROUND_VALUE`.

**Why.** §4 of this pre-registration states that "every span is range-checked", and the 15 Nov
directive requires that "every proposal must carry source-span grounding". Those are not the same
thing and the implementation only did the first. An AI-delegated evidence pass over the 14 accepted
`alternative_group` proposals
(`reports/s180/alternatives_verification_2026-11-15/AI_EVIDENCE_PASS_ksh_prv.md`) found that **none
of the 14 spans supported its value**, at distances of 43 to 530 characters from the real evidence.
So measure 4 of §3 — "span validity: share of accepted proposals whose span lies inside the raw
text" — measured exactly what it said and nothing more, and the step-7 figures "spans 39/39 valid"
and "24/24 valid" must be read as *range* validity, not grounding.

This is again a **tightening**: it can only lower an acceptance count.

**The in-flight asymmetry, declared now rather than discovered later.** The 72B process loaded
`layer1_proposer` when it started, which was **before** this change. Its live gate therefore applies
the D-135 surface **without** the D-137 grounding check. When it finishes, its accepted proposals
will be re-scored by applying `span_grounds_value` to their recorded spans, and **both numbers will
be reported**: as-gated and after grounding. The function is deterministic and reads only the
recorded span against the sealed text, so the re-score is reproducible from the committed artifact.

The sealed set is unchanged: same 60 cases, same seed, same packet SHA-256
`b926c303993541d5380e4531f495f9c89c2111a0c5c902e99df0ad95f15da6e7`.

**Registered expectation, before the 72B result exists:** after grounding, accepted counts for every
arm fall **substantially**, and it would not be surprising for an arm to reach **zero**. A zero is a
reportable result, not a failed run: it would say that on this corpus no model arm produced a
grounded alternatives binding, which is a statement about the task and the prompt rather than about
any model. Recorded results stay unedited either way.
