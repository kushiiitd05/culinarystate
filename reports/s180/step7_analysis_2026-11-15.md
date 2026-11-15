# Freeze step 7 — sealed Layer-1 comparison: analysis

**DIAGNOSTIC_ONLY · NO_GOLD_SO_AGREEMENT_IS_NOT_ACCURACY · WIKIBOOKS_CC_BY_PUBLIC_TEXT_ONLY · SEALED_BEFORE_ANY_MODEL_RUN**

Written 15 Nov 2026 against `reports/s180/step7_sealed_comparison_preregistration.md` (+ amendments A1, A2).
Sealed set unchanged throughout: 60 cases, seed `s180-layer1-hardcases-2026-11-15`, packet SHA-256
`b926c303993541d5380e4531f495f9c89c2111a0c5c902e99df0ad95f15da6e7`.

§5 of the pre-registration governs every number below. There is **no gold** for Layer-1 proposals on
these cases. Acceptance measures contract compliance, never correctness. Nothing here is accuracy and
nothing here may become a headline claim.

## 1. What ran, and what did not

| Arm | Status | Artifact |
|---|---|---|
| **D** deterministic, rules only | **complete** | baselines in `hardcase_seal_2026-11-15.json` |
| **L** local qwen2.5:7b-instruct, prompt v1 | **complete**, 60/60 | `step7_arm_L_qwen7b_2026-11-15.json` |
| **L** local qwen2.5:7b-instruct, prompt v2 | **complete**, 60/60 | `step7_arm_L_qwen7b_v2_2026-11-15.json` |
| **L** local qwen2.5:72b, prompt v1 | **VOID — 20/60** | not committed; VPN dropped, 40 cases lost to SSH timeout |
| **H** hosted nemotron-3-ultra-550b | **no recorded result** | feasibility only, see §6 |

The 72B run is void for the same reason the first 7B run was voided: the VPN dropped mid-run and
40 of 60 cases never reached the model. A 20-case partial on a stratified sealed set is not an arm.
Its numbers appear in §5 **only** as a latency/feasibility note and for a within-case structural
observation that does not depend on n. It is not compared against the complete arms.

## 2. Arm D — the floor

Rules alone, `lineage_vnext=True`, over the 60 cases:

- **1,001 events**, 1,563 entities, **1,001 proposable slots** (16.7 per case)
- **4 allocations in total**, and **57 of 60 cases have zero allocations**

That last line is the honest statement of where Layer-1 sits. On the hardest 60 cases in the corpus,
the deterministic path commits essentially no allocations at all. It does not guess, and so it leaves
~1,000 categorical slots open. Every model arm below is competing for a tiny fraction of them.

## 3. Arm L — 7B, prompt v1 vs v2

| Measure | v1 | v2 | delta |
|---|---|---|---|
| Cases answered | 60/60 | 60/60 | — |
| Transport/parse failures | 0 | 0 | — |
| Proposals returned | 84 | 24 | −71% |
| Schema compliance | 1.000 | 1.000 | — |
| Gate acceptance rate | 0.4643 | **1.000** | +0.536 |
| Proposals accepted | **39** | 24 | **−15** |
| Accepted spans valid | 39/39 | 24/24 | — |
| Numeric values attempted | 0 | 0 | — |
| Cases with ≥1 acceptance | 31/60 | 17/60 | −14 |
| Rejections | 45 × `FIELD_NOT_LICENSED_BY_TRIGGER` | none | — |
| Latency mean / median / max (s) | 16.2 / 19.2 / 66.1 | 7.3 / 4.6 / 30.9 | −55% |

**v2 tripped the tripwire registered in A2.** Acceptance went to exactly 1.000, and A2 stated in
advance that this would mean the prompt had become an answer key rather than a question, to be
reported as such. It is reported as such. The prompt names only the licensed field, so the one
rejection code that existed cannot fire, and acceptance is uninformative by construction.

**v1 beats v2 on the measure that matters.** Accepted proposals fell 39 → 24 and cases with any
acceptance fell 31 → 17. A gate that cannot reject is not evidence of a better arm.

**The collapse is concentrated on one trigger.** Accepted proposals by first-listed trigger:

| Trigger | v1 | v2 |
|---|---|---|
| `VNEXT_ALTERNATIVE_SKIPPED` | **16** | **1** |
| `AMBIGUOUS_REFERENCE` | 10 | 10 |
| `VNEXT_MIXTURE_COREF` | 8 | 6 |
| `UNRESOLVED_LOT` | 5 | 7 |
| `VNEXT_FAT_STAYS` | 0 | 0 |

Narrowing the prompt suppressed almost all answers on `VNEXT_ALTERNATIVE_SKIPPED` — the one trigger
where `alternative_group` is the licensed field and where 48,520 corpus flags are waiting. v2 did not
only drop unlicensed junk; it dropped the licensed alternatives answers too (accepted
`alternative_group` 13 → 1). Neither prompt produced a single accepted proposal on `VNEXT_FAT_STAYS`.

## 4. Contract compliance is not the bottleneck

Across both complete runs, 108 returns: **schema compliance 1.000, span validity 100%, numeric
attempts 0, invariant violations 0, transport failures 0.** Every rejection in v1 was the single
code `FIELD_NOT_LICENSED_BY_TRIGGER`, and A2 established that as a defect in my prompt, not in the
arm: the v1 prompt offered both proposable fields on every case because it was written before
`layer1_proposer.TRIGGER_FIELDS` existed.

So the 7B arm has no headroom left on the contract. It cannot widen the schema, invent lineage, or
emit a number, and it did not try. Whatever Layer-1 still needs, a larger model cannot supply it by
being better at the contract.

## 5. Finding: the gate is blind to the *kind* of the value

A1 warned that the gate "still cannot judge whether a *licensed* value is the right one". That is no
longer hypothetical. Comparing accepted proposals **within the same case**:

| Pair | cases both accepted ≥1 | exact `(event_id, field, value)` agreement | same `(event_id, field)` slot |
|---|---|---|---|
| 7B v1 ↔ 7B v2 | 10 | **0** | **0** |
| 7B v1 ↔ 72B v1 *(20-case void subset)* | — | **0** | **0** |

**Zero slot agreement in every pair.** Three runs over the same sealed cases through the same gate do
not merely disagree on the answer — they do not pick the same event to answer about, even once
(1 of 10 shared cases shared any `event_id` at all).

The accepted values show why. Same case, `AMBIGUOUS_REFERENCE`:

- v1: `E14 condition_profile_id = "tomato_meat_sauce"`
- v2: `E1 = "pan"`, `E23 = "dish/pan"`, `E23 = "tomato meat sauce"`

and elsewhere `"chicken"`, `"oil"`, `"bowl_content"`, `"dates_seeds"`, `"boiling_time"`, `"cooked"`,
`"bake"`, `"fried"`. These are at least four incompatible kinds of thing — ingredient names, vessel
names, process names, and duration references — all accepted as a **condition profile id**.

`condition_profile_id` has no vocabulary, so the gate accepts any non-numeric string. All 63 accepted
proposals across the two complete runs are therefore "contract-compliant" and a large share are
semantically void. **This is the binding constraint on Layer-1, and it is a validator gap, not a
model gap.** It is the same class of hole A1 closed one level up: A1 stopped an unlicensed *field*;
nothing yet stops an out-of-kind *value* in a licensed field.

This is also why the pre-registration's refusal to call agreement accuracy was the right call. Had
the three runs agreed, the agreement would have been equally uninterpretable.

## 6. Latency and provider selection

| Arm | mean | median | max |
|---|---|---|---|
| 7B v1 | 16.2 s | 19.2 s | 66.1 s |
| 7B v2 | 7.3 s | 4.6 s | 30.9 s |
| 72B v1 *(void, n=20)* | 117.5 s | 101.6 s | 355.9 s |
| hosted 550B | no recorded run | — | — |

The 72B figures include a ~40 s cold load of a 47 GB model on first call. Even warm it is ~6–15×
the 7B cost per case for no measurable contract gain, on a link that has now dropped two runs.

**Hosted arm H produced no recorded result and is closed.** The 14 Nov pre-registration cites a
single hand probe of `nvidia/nemotron-3-ultra-550b-a55b` answering in 4.8 s with valid JSON; the
15 Nov 2-case probe returned 0/2 inside a 120 s timeout, the timeout was raised, and the run was
stopped on Kush's decision ("arm H is not worth it"). That is a **feasibility and latency note, not
an arm** — two cases cannot be one. Its partial output was discarded, not committed.

Per freeze item 7, provider selection rests on contract compliance, latency and cost, never on an
accuracy claim this set cannot support. On those three, the local 7B is the standing choice: it meets
the contract fully, costs nothing, and sends no data off the machine.

## 7. What this step does and does not license

**Does:**
- Layer-1 as specified is contract-safe. 108 model returns produced no numeric chemistry, no invented
  lineage, no schema widening, no invariant violation. The validator-decides design held.
- Prompt specification, not model scale, explained the whole of v1's rejection histogram.
- The next real constraint is named and evidenced: `condition_profile_id` needs a closed vocabulary
  or a reference to an existing condition profile, because the gate currently accepts free text.

**Does not:**
- No arm is correct, better or more accurate on these cases. There is no gold.
- No number here enters a figure without the DIAGNOSTIC_ONLY label.
- The 72B question is **unanswered**, not answered negatively: its run is void at 20/60.
- Human verification of individual proposals remains a separate, human-only act (D-085).

## 8. Open

1. Re-run qwen2.5:72b prompt v1 over all 60 cases when the VPN is stable. Void run kept out of `reports/`.
2. Decide whether `condition_profile_id` becomes a closed vocabulary before the freeze — it is a
   validator invariant question (§ "no unsupported values"), mapped to the existing SSOT-v16 work,
   not a new component.
3. `VNEXT_FAT_STAYS` got zero accepted proposals under either prompt. Unexplained.
