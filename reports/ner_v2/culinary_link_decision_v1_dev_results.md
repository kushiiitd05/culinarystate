# CulinaryLinkDecision-v1 -- DEV results (provisional; n = 61 dev_alias positives + 252 dev NIL; 3 seeds per config; 441 fresh gold NOT used)

Training data: 2,020 OOF TRAIN examples (260 positives, 1,760 NIL) from concept/alias-grouped 5-fold BGE candidate generation; Tev1-4B teacher (frozen TEV-LINK-v0) run on those examples only. Student: BAAI/bge-small-en-v1.5 cross-encoder, 33.4M parameters, NONE as an option. Forced Acc@1 = best of the K candidates (View A style); DEV references: BGE top-1 0.721, zero-shot cross-encoder 0.705, **Tev1-4B 0.820 (K=5) / 0.836 (K=10)**, pool oracle 0.852 / 0.869.

| Model | K | forced Acc@1 (mean±sd) | paired gain vs BGE top-1 [95% CI] | NIL AUROC | AUPRC | false-NONE on aliases (default option) | latency (GPU, bs 1) |
|---|---|---|---|---|---|---|---|
| CD-L0 structured (no text) | 5 / 10 | 0.639 / 0.656 | negative | 0.778 / 0.757 | 0.919 / 0.910 | - | CPU, sub-ms |
| CD-L1 gold only | 5 | 0.787±0.000 | +0.066 [-0.016, +0.153] | 0.861 | 0.946 | 0.481 | 14.6 ms |
| CD-L2 gold + Tev (lambda 0.3) | 5 | 0.781±0.020 | +0.060 [-0.022, +0.153] | 0.862 | 0.939 | 0.410 | 14.1 ms |
| CD-L2 (lambda 1.0) | 5 | 0.792±0.008 | +0.071 [-0.011, +0.158] | 0.850 | 0.937 | 0.311 | 14.2 ms |
| CD-L1 gold only | 10 | 0.787±0.023 | +0.066 [-0.011, +0.153] | 0.852 | 0.946 | 0.421 | 16.8 ms |
| **CD-L2 (lambda 1.0)** | **10** | **0.831±0.008** | **+0.109 [+0.016, +0.208]** | **0.877** | 0.943 | 0.251 | 16.7 ms |
Paired (items, seed-averaged): CD-L2 - CD-L1: K=5 lambda 0.3 -0.005 [-0.071, +0.060]; K=5 lambda 1.0 +0.005 [-0.060, +0.071]; **K=10 lambda 1.0 +0.044 [-0.016, +0.104]**. CD-L1 K=10 - K=5: 0.000 [-0.044, +0.044].

## Reading against the pre-registered gate
- **Student works:** CD-L2 (K=10, lambda 1.0) reaches 0.831 = **99% of Tev's DEV accuracy (0.836)** with a paired gain over BGE whose lower bound is > 0, at 33M parameters and ~17 ms (vs Tev 4B, 51-112 ms) -> meets the **D1 criterion at DEV level**; it is the only configuration that does (gold-only students gain over BGE but their lower bounds include 0).
- **Distillation claim NOT established:** CD-L2 - CD-L1 is significantly positive in no configuration (K=10: +0.044, CI includes 0; K=5: none). Per protocol, without a CI-separated CD-L2 > CD-L1 the teacher-distillation claim is not accepted; the DEV evidence is suggestive for K=10 only and the set is small (n = 61, five configurations compared -> multiplicity, provisional).
- K: no gain from K=10 for the gold-only student; K=10 helps only with distillation.
- NIL: students are NIL-AUROC 0.85-0.88 (BGE cosine 0.72 on the same DEV; Tev 0.88-0.90); default NONE option over-fires on aliases (training set is 87% NIL), so no autonomous NONE action is validated.
- Structured baseline CD-L0 (0.64-0.66) is below BGE: the gain needs text-level reasoning, not retrieval-feature recombination.

## Not done / limits
Separate NIL head and the mention+context ablation are deferred (no legitimate gold-labelled mentions in context; NIL-head design is a secondary item); only 260 positive training examples; DEV n = 61; student selection on DEV is provisional until a **new sealed human set** designed after the student and hyper-parameters are frozen (ambiguous items with explicit acceptable-concept sets, regional/multilingual coverage). The 441 gold set stays sealed.
