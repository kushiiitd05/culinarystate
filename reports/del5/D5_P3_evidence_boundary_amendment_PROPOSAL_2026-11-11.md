# D5 P3 evidence-boundary amendment proposal — 11 November 2026

Status: **AI_DRAFTED / PROPOSED_NOT_ADOPTED / EXPLORATORY_POST_HOC / NON_CITABLE /
NO_HUMAN_SIGNOFF_D085**. This document changes no code, benchmark, gold, preregistration, freeze or result.

## Finding retained

D-092 and NEG-0051 retain the original H3 verdict **RULE_NOT_MET**. On the frozen P3 block (10 questions),
B7 abstained on 0/10 and B2 on 3/10. The paired unsupported-claim sign test does not override the separate
P3 condition. The 30-claim audit was NOT_RUN; it cannot reverse the already failed conjunction.

Evidence: `reports/del5/d5_score_v1_D085/d5_scoring_result.json`,
`reports/del5/d5_runs_v1_D085.jsonl`, `registry/negative_results_register_v1.csv` NEG-0051,
and `DECISIONS.md` D-090..D-092. Original benchmark freeze: `D5-BENCH-2026-11-10`, supplemented by
`D5-BENCH-2026-11-10b` for scorer reference inputs. The supplement was written after rung generation began;
that timing deviation remains visible.

The benchmark's P3 no-evidence boundary used exact/parent-food evidence. The decision layer admitted broader
cross-food evidence: the run records report 9 BROAD_QUALITATIVE modes and 1 NEAR_PARTIAL mode. Its existing
`decision/confidence.py` permits qualitative output for BROAD_QUALITATIVE; `decision/policy.py` answers when
at least one option's precision is not ABSTAIN. This explains the route disagreement; it does not certify the
appropriateness of the transferred evidence or establish the counterfactual result of another implementation.

## Proposed next experiment

Use an explicit, named **question-specific evidence-admissibility policy**, shared by benchmark construction,
retrieval, decision routing and the independent scorer. Proposed conservative course scope:

- Exact ingredient, requested process and requested target must match. Any parent-food allowance must have a
  separately declared relation and transfer rule; otherwise it is outside scope.
- Broad cross-food evidence may be displayed as related background with its original IDs and limitations.
  It must not supply the requested question-specific effect or satisfy the answerability condition.
- An answerable question requires at least one admissible row. Without one, the answer is ABSTAIN for that
  effect. Conflicting admissible rows retain the conflict rather than selecting a favourable one.
- Unknown required context remains unknown. No inference from database coverage or absent labels creates
  a negative experimental result.

This is a proposed tightening, not a claim that every existing DIRECT or parent-food match is scientifically
applicable. G08-3 remains FAIL, E3 rows remain unverified, and lineage independence is not restored by this rule.

## Freeze and evaluation sequence if adopted

1. Record a dated decision with the exact evidence boundary and the AI-delegated approver/label under D-085,
   or an actual human decision if supplied. Do not amend the locked v1 text in place.
2. Write a new, dated preregistration amendment and versioned implementation. Specify all allowed transfer
   relations, handling of missing context, comparator behaviour and the complete conjunctive H3 rule before
   executing it. No benchmark question ID or gold label may be used to force an abstention.
3. Test the policy on synthetic exact, parent, broad, absent and conflicting examples. Freeze the new policy,
   relevant retrieval/decision/scorer code, prompts, benchmark and reference hashes together before running.
4. The old 74 questions have already been inspected. A rerun on them is **EXPLORATORY_POST_HOC / NON_CITABLE**,
   even with a new freeze. A confirmatory reading would require genuinely uninspected evaluation data and
   appropriate independent gold; personas of one model do not provide independent labels.
5. Use new output paths and a new RUN ID. Retain the original D-092 output byte-for-byte and present original
   and amended results side by side, including every abstention and coverage cost. Do not replace the original
   verdict or advertise a corrected system as a successful preregistered H3 experiment.

## Present disposition

**Proposal only.** Prefer completing the original-result report before spending GPU time on the reused
benchmark. The H3 result is already reportable as RULE_NOT_MET with NEG-0051. Missing private D5 context and
unconfirmed GPU access also prevent a full new rung run here. No adoption or new run is implied by this memo.
