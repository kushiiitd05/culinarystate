# Step 19 independent agent methods precheck

**AI_DRAFT_PENDING_EXPERT_VERIFICATION — 2026-10-28.** Reviewer: delegated
pilot-methods AI agent, at Parv's request. This is an independent code/document
review relative to the engineering lane, not independent human annotation,
scientific approval, a signature or a passed pilot. No recipes, real labels,
packet keys or raw recipe text were read. No draw was performed. Only this file
was created; recommendations below have not amended existing thresholds.

## Scope and disposition

Reviewed Step 19 README, targeted sections 2–7, 9–12 and Appendix B of
`deep_gold_pilot_design_v1_draft.md`, current STATUS/D-040/D-042, and the
Step 16 strata README. The design has useful safeguards, but decision-producing
pilot analysis needs the corrections below before its outputs can support a
freeze or capacity claim. Engineering, synthetic fixtures, blank templates and
readiness checks can proceed now. Expert review is not an engineering blocker.
Actual independent human annotation and threshold/start approval remain distinct
requirements; another AI agent cannot supply them.

Read-input SHA-256 (recorded before this review file was written):

| Input | SHA-256 |
|---|---|
| Step 19 design | `0af23c96e6ab21c142bb82c4fe785e979dc1f1fe58bc734d41a85beadd26d342` |
| Step 19 README | `3ad7e89106e6a3be45c51615d590ca34cce06da9506bcbb8f37f67bfe0a058b6` |
| Step 16 strata README | `0567675411825fbf26f5ea3d46c385ef1ca000dcf50e2b8300fd30885f33ad76` |

## Findings and proposed resolutions

All resolutions here are **AI recommendations**, not adopted scientific rules.

| ID / priority | Evidence / inconsistency | Proposed resolution and later verification |
|---|---|---|
| PM-01 / high | §7.3 and THR-19P-34 compare cluster bootstrap bounds for a pooled statistic with a t interval on per-recipe statistics. Micro F1 and mean recipe F1 are different estimands. One recipe with TP=1, FP=FN=0 and another with TP=0, FP=100, FN=0 yields micro F1=0.019608 but macro F1=0.5. Taking their outer envelope is not three methods estimating the same parameter. | Keep micro and macro tables separate. Implement a t interval on per-recipe F1 only for macro F1. A micro-statistic interval needs a method targeting that pooled ratio, e.g. a reviewed recipe-level influence/pseudo-value construction, not a mean of recipe F1. Until reviewed, make micro bound-dependent outcomes INDETERMINATE; synthetic reporting can still run. Expert checks estimands and the precise small-cluster method. |
| PM-02 / high | THR-19P-27 specifies a t interval on ln(time), Appendix B correctly identifies its back-transformation as a geometric-mean interval, but GO-40 multiplies this timing quantity by N to assess total hours. Expected total time depends on arithmetic mean. For lognormal sigma=0.5/0.7, arithmetic/geometric factors are 1.13315/1.27762. | Report geometric timing descriptively. Capacity uses total active minutes/arithmetic mean and an explicitly reviewed upper uncertainty bound, separately per annotator, plus measured setup/design/adjudication. Censored completion times cannot supply an ordinary complete-case mean: an unresolved >=120-minute item means no demonstrated completion-cost upper bound. Do not treat 120 as the actual completion time. NIST explains the distinction [S1]. |
| PM-03 / high | §7.3 says percentile bootstrap undercovers with 7 and 13 clusters as an unconditional statement; the three-interval envelope is called conservative without specifying handling of undefined statistics. BCa can return NaN for identical observations; alpha/kappa can be undefined under constant labels; resamples may lack a rare class. | Say small-cluster coverage may be poor; this design has not demonstrated nominal 95% coverage. Keep all method statuses and invalid-replicate counts. Do not silently drop undefined replicates or unavailable CI methods and then pass a bound gate. Route such a gate INDETERMINATE pending a predeclared alternative. Never replace undefined alpha by 1. SciPy explicitly documents BCa degeneracy [S2]; synthetic check reproduced it below. |
| PM-04 / high | §4.5/THR-19P-10 coverage-greedy P2 does not have the ordinary equal-probability stratified sampling distribution. §12 threat 5 calls its timing bias upward/conservative, but hard-case tag coverage has no established monotone relationship with time. §7.3 resamples all recipes as exchangeable despite fixed source/tier quotas and changing contracts. | Label inference conditional/descriptive for the selected pilot design. Remove any guaranteed upward timing-bias assertion in a reviewed addendum. If population/design-based timing inference is wanted, specify a random design, estimand and weights before the draw. Do not invent inclusion probabilities from cell sizes for the greedy, overlapping-tag, group-excluding design. Small cells also prevent an informative ordinary within-cell bootstrap. Expert must choose the inferential target before numerical decision intervals are used. |
| PM-05 / medium | §4.4 mandates original `reserve_split`, while D-040 selects corrected `reserve_split_v2` pending Kush. The old regex fails on `reserve synthetic water`, and v2 matches. | Pin tag-rule version/hash and selected column in the proposed manifest; show both versions' counts for comparison. Keep actual draw readiness pending the remaining approval. Do not overwrite historical v1 or pretend its counts refer to v2. |
| PM-06 / medium | Fixed 6/10/4 source and 5/9/6 tier quotas are arithmetically consistent before fallback. A cell fallback to another source can violate source quotas; FOODCOM has no Indian label and therefore cannot satisfy that cell. Joint group exclusions can make individually populated cells infeasible. | Validate global cell assignment and distinct groups before drawing; preserve tier/tag eligibility on every fallback. A deficit produces a readiness failure with counts, not a silently relaxed quota. Record a proposed deterministic reallocation for human approval if necessary. Reserve groups must also be checked for conflicts with all selected/reserve groups. |
| PM-07 / medium | §7.4/Appendix B apply the binomial-proportion half-width formula directly to F1 and a fixed-p_e simplification to kappa. F1 is a ratio of dependent TP/FP/FN counts; kappa's expected-agreement estimate also varies. These are heuristics, not demonstrated F1/alpha/kappa precision guarantees. | Retain as explicitly simplified planning sensitivity checks, not achieved power/precision. No synthetic F1 coverage claim from the binomial formula. Before sizing, simulate or use a reviewed variance procedure under the actual cluster/design assumptions and metric. |
| PM-08 / medium | The zero-event formula 1−0.05^(1/n) is numerically correct under an independent common-rate Bernoulli model. Merely writing “pilot design population” does not establish that model for fixed quotas plus coverage-selected P2; complete under-detection of a schema problem would also invalidate a rate interpretation. | Print the exact number only as a model-conditional illustration, not a design-valid population bound, unless assumptions are justified. The observed result remains “0 detected in n selected recipes; unexercised classes remain untested.” NIST's exact method is explicitly binomial [S3]. |
| PM-09 / medium | THR-19P-22 says high-prevalence alpha is printed but not interpreted; THR-19P-18/19/28 nevertheless route on alpha, including stop/extension. Constant fields also yield undefined alpha. Routing for zero-support F1 and absent classes is not fully specified. | Explicitly identify suppressed/undefined routing metrics. Pending a registered policy, high-prevalence or insufficient-support fields cannot earn an alpha-based pass or extension, and AC1 must not silently replace the registered alpha threshold. Print counts/specific agreement and the unresolved status. Missing/unmatched annotations must not disappear as ordinary missing data. |
| PM-10 / medium | PV-9 describes git timestamps as an external time anchor; git identity and author/committer dates are locally configurable [S4]. PV-8 demands detecting an “11-second pair,” but time separation alone is not a standalone rule in PV-1..10. | Preserve local commits as auditable content/order evidence, not authenticated human identity or trusted wall-clock time. Document self-attestation. Define planted fixtures by concrete violated rules (e.g. recorded active time <5 minutes), not 11 seconds between files alone. No need to invent a new timing threshold. Never automatically infer cheating from REVIEW heuristics. |
| PM-11 / medium | Contract under test is explicitly v0 + handbook v1 + Addendum A, not new rc2. Agent-authored handbook v2 examples supplied to the humans beforehand would change the contract/prime the schema-gap audit. P2 may or may not acquire Addendum B, although THR-19P-23 calls versions necessarily different. | Keep rc2 and handbook v2 as engineering/analyst proposals; do not distribute them as pilot annotation guidance without an explicit new contract/version decision. Snapshot exact v0/schema/handbook/Addendum hashes at issue. Report actual handbook versions by wave, calibration history regardless of byte equality, and no pooled reliability claim. Analyst known-gap lists remain separate. |
| PM-12 / low | Design header says Step 08 not started and §2/F9 says BBC absent “on this server”; current STATUS says 08a built and takeover notes say BBC data unpacked locally. THR-19P-15 projection can double-count setup/adjudication if “P1 hours so far” already includes them; Appendix B includes 2 design hours that the projection does not explicitly mention. | Mark historical environment assertions as dated, and use a current, local readiness inventory. Compute capacity from an additive phase ledger: completed phase minutes plus remaining projected phase minutes, each counted once. Arithmetic “about93 minutes” is valid only with the stated 6+1+2 overhead. |

## Checks that passed, with limits

- P1 source counts BBC2/Food.com3/Wikibooks2 plus P2 4/7/2 give 6/10/4.
  P1 tiers2/3/2 plus P2 3/6/4 give 5/9/6; totals are20. These are matrix
  arithmetic checks, not a check of actual post-exclusion recipe eligibility.
- Minimum30 units from5 recipes is an explicit operational support floor, not
  proof of reliable intervals. Counts below the floor must remain counts-only.
- Separate A/B commitment-before-comparison, immutable originals, fresh exposed
  recipe exclusion, per-wave versioning, no inside-wave convention change,
  dev-only group locks and any-logger blocking triage are useful safeguards.
- F1 vs chance-corrected alpha are explicitly distinguished. Keeping the same
  numeric cutoffs as a routing convention does not make the scales equivalent.
  Krippendorff's own university resource is the primary reference entry [S5];
  the book/article cutoff passage could not be fetched in this review, so no new
  assertion about universal acceptability of those thresholds is made here.
- STOP-SCHEMA same-family blocking items on >=2 recipes and retained older
  trigger can coexist. Zero open BLOCKING items does not prove zero underlying
  representability defects or supersede Step16 zero-tolerance freeze review.

## Reproduced synthetic/arithmetic checks

Executed with existing project venv, Python standard library plus installed
SciPy/NumPy; no recipe data. These checks do not constitute statistical coverage
validation. The exact expressions below reproduce the reported values.

```python
from math import exp
from fractions import Fraction
for n in (5, 7, 13, 20, 40):
    print(n, round(100 * (1 - .05 ** (1/n)), 4))
# 5:45.0720; 7:34.8164; 13:20.5817; 20:13.9108; 40:7.2158 percent
print(float(Fraction(2, 102)), (1 + 0) / 2)
# micro F1=0.0196078431372549; macro F1=0.5
print([exp(s*s/2) for s in (.5, .7)])
# [1.1331484530668263, 1.2776213132048866]
print([20*93/60 + a + 1 + 2 for a in (4, 6)])
# [38.0, 40.0] hours
import warnings
import numpy as np
from scipy.stats import bootstrap
with warnings.catch_warnings(record=True) as seen:
    warnings.simplefilter('always')
    result = bootstrap((np.ones(7),), np.mean, n_resamples=1000,
                       method='BCa', random_state=19)
    print(result.confidence_interval)
    print(sorted(set(type(w.message).__name__ for w in seen)))
# (nan, nan); ['DegenerateDataWarning', 'RuntimeWarning']
```

Additional counterexamples: choosing a recipe that covers3 mechanically tagged
classes but takes10 minutes over one covering1 class taking90 minutes disproves
a guaranteed upward timing bias. For19 recipes taking30 minutes and one censored
at120,11.5 hours is only a lower bound on total completion time. Replacing the
censored duration by120 and computing a normal complete-case upper interval
would conceal the unresolved tail.

## Primary sources checked

Access date for all entries: **2026-10-28**. Web copies may evolve; the local
input hashes above identify the reviewed project documents. No recipe text was
submitted to browsing tools.

- **S1:** [NIST Dataplot, Confidence Limits (Mean)](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/conflimi.htm).
  Distinguishes ordinary mean inference from the lognormal arithmetic-mean
  procedure; back-transforming logged-data mean limits does not estimate the
  arithmetic-mean interval. Supports PM-02, not a claim that a particular method
  is validated for this13-recipe, censored, selected sample.
- **S2:** [SciPy bootstrap API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).
  Describes paired resampling and warns that BCa intervals may be NaN on
  degenerate data. Supports explicit undefined-status handling in PM-03.
- **S3:** [NIST Dataplot, Exact Binomial](https://itl.nist.gov/div898/software/dataplot/refman2/auxillar/exacbino.htm).
  Defines exact binomial confidence limits; supports the model qualification in
  PM-08, not validity under greedy coverage sampling.
- **S4:** [Git commit documentation, Commit Information](https://git-scm.com/docs/git-commit#_commit_information).
  Author/committer names and dates can come from environment variables; names do
  not authenticate a person. Supports PM-10's audit limitation.
- **S5:** [Annenberg, Krippendorff's Alpha Reliability](https://www.asc.upenn.edu/krippendorffs-alpha-reliability).
  Primary university reference entry. The repository full-text request for
  `b6ea3a5b-3dee-4f27-a159-e44393eda7d4/download` returned403; no cutoff wording
  was treated as freshly verified from that unavailable passage.

## Next verifiable work

Engineering can build deterministic readiness, phase-accounting, finite-status
metric, provenance and manifest checks against synthetic fixtures. Expert review
later checks PM-01..04/07..09, endorses a precise inferential target/method and
records any amendments without rewriting historical rows. Humans still supply
actual blank annotations, capacity, nonce and required approvals. This review
does not certify H4/H5, the disputed scientific gates, human independence or
actual pilot completion.
