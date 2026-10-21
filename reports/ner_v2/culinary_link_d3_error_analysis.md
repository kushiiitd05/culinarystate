# Why the Tev advantage did not reproduce on the 850 set -- descriptive analysis (closed linker lane; nothing tuned)

Script `tools/v2dm_link_d3_descriptive.py`, numbers `_link_d3_descriptive.json`. Descriptive only: no model, threshold, K or architecture is changed from it, and it is not a development input.

## The progression
| Set | n (View A strict) | BGE | Tev1-4B | Tev - BGE |
|---|---|---|---|---|
| DEV (n=61 alias positives, benchmark-derived labels) | 61 | 0.721 | 0.836 | +0.115 (CI wide, lower bound for the student near 0) |
| Fresh 441 (human, double-annotated) | 191 MATCH | 0.796 | 0.901 | **+0.105 [+0.058, +0.152]** |
| Final 850 (human, double-annotated) | 293 MATCH / 430 incl. AMBIGUOUS sets | 0.887 / 0.881 | 0.884 / 0.872 | **-0.003 / -0.009 [-0.042, +0.021]** |

Note: the advantage *did* reproduce once, on an independent human set (the 441). The 850 is the second independent human set and it does not reproduce. So the n=61 DEV result was not simply noise relative to the 441; the failure is between two human sets with different composition. Two samples of one effect (+0.105, -0.003) are consistent with a true gain that depends on set difficulty, not with a stable +0.10 gain.

## What differs (descriptive)
1. **BGE has far fewer errors to fix on the 850.** MATCH items BGE gets wrong: 39/191 (20%) on the 441 vs 33/293 (11%) on the 850. A reranker can only gain on those items. 51% of 850 MATCH items are S1 exact-gallery-known mentions where every system is ~100%; BGE top-1 is an exact gallery hit (score >= 0.999) for 50.9% of 850 MATCH items vs 30.4% on the 441. The 850 is dominated by easy retrieval cases.
2. **Alias-like stratum was much easier for BGE.** S2 MATCH BGE accuracy 0.833 (850) vs 0.646 (441). The 441 sample over-represented hard alias cases for BGE; the 850 sampled mentions "not used before (viewed linker sets and the 441 excluded)", so the hardest, already-viewed mentions were removed from the pool. This is a plausible cause but not verified from sampling logs.
3. **Tev rescues fewer and breaks many more.** Rescues (BGE wrong, Tev right): 22 (441) vs 13 (850). Breaks (BGE right, Tev wrong): 2 vs 14. Examples of 850 breaks: Tev prefers a longer or more specific candidate over the gold ("yolks" -> egg yolk when gold is `yolk`; "potatoes" -> "potato unpeeled"; "soft brown sugar" -> "brown muscovado sugar"; "cider apple" -> apple). Many S3/S4 mentions are garbled strings ("fleeceable grapeshot", "xanthous ship s bell common pepper") where the semantics are weak for any model. Not tested whether the 441 mentions were cleaner.
4. **NIL prevalence 18% vs 46%.** NONE was 80/441 and is 391/850. The forced-choice View A ignores NONE items, but the 850 stratum design (S3 likely novel 180, S6 long-qualified 150) shifts the mix toward noisy mentions; Tev's NIL advantage (AUROC +0.031 on 441) also vanished (-0.015).
5. **Ambiguity scoring changed.** The 441 left 139 AMBIGUOUS items unscored; the 850 scores them set-valued (137 items, median set size 2, 32% of View A). On these BGE 0.869, Tev 0.847, CD-L2 0.837: sets reward any defensible pick, which compresses differences. MATCH-only Tev - BGE is -0.003, so ambiguity scoring is not the main driver.
6. **Teacher/student disagreement.** Tev and BGE pick the same concept on 66% of the 850; CD-L2 agrees with Tev 63% and BGE 66%: the student is not a copy of the teacher, and on a set where the teacher's edge vanished, the student inherits that.
7. **Pooling bias (both sets).** Candidate pools were unions of system picks, so a concept missed by every system could be labelled NONE; this affects retrieval failures, not the Tev-vs-BGE contrast.
8. **Label quality.** The 850 gold kappa was 0.317 pre-adjudication (the NONE vs AMBIGUOUS rule differed by annotator); adjudication reasons are templated. Gold noise is larger than on the 441, which also dilutes differences.

## Reading
The n=61 DEV gain was an estimate with a very wide interval from alias positives whose BGE accuracy was low (0.72); the 441 was similarly hard (BGE 0.80). The 850 contains many more easy cases where BGE is near ceiling and Tev sometimes over-specifies, so there is little headroom (BGE oracle 0.983 vs BGE 0.881 = 10 pts, but on MATCH only 33 errors). The honest statement: Tev's gain is conditional on the BGE-hard share of the data; across two independent human sets the pooled evidence is not enough to deploy a 4B reranker, and the compact student did not exceed the retrieval baseline on either regime it was selected for. This is why the final deployment rule remained "BGE unless a fresh set shows a lower-bound gain".

Limits: the sampling-pool explanation (item 2) is an inference, not a verified fact; no sampling-log audit was done; no new scores were computed for the closed systems beyond descriptive slices.
