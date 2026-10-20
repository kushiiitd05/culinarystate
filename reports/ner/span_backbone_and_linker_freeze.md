# Span backbone + linker decisions (DEV only; TEST untouched)

## Span backbone
| Model | TASTEset DEV micro (5 seeds) | RecipeDB3 DEV micro (3 seeds) | min | GB |
|---|---|---|---|---|
| DeBERTa-base+CRF | 0.9396 | 0.9661 | 34 | 3.0 |
| DeBERTa-v3-large+CRF | 0.9443 | 0.9682 | 67 | 9.3 |
| DeBERTa-base K-TS (type-specific) | 0.9411 (+0.0015, 4/5 seeds) | not run | | |
| RoBERTa-large+CRF | 0.9412 (+0.0016, 4/5 seeds) | not run | | |

Rule: delta >= 0.003 with CI excluding 0, >= 4/5 seeds. v3-large: TASTEset +0.0047 (CI [-0.0016,+0.0105], n.s.), RecipeDB3 +0.0021 (3/3 seeds, below threshold) -> not promoted.
- Type-specific, RoBERTa-large: REJECT (< 0.003).
- Frozen span backbone (provisional): **DeBERTa-base+CRF = best CulinaryState candidate**. v3-large+CRF kept as accuracy/unseen Pareto point, not champion. OOF tables already exist for base+CRF (no 5 h regeneration).

## Linker (select on dev_alias n=61; unseen_alias n=96 reported only)
| Variant | dev_alias Acc@1 | unseen Acc@1 | R@5 | MRR |
|---|---|---|---|---|
| e5-large-v2 contrastive lr2e-5/6ep (best e5) | 0.645 | 0.660 | 0.819 | 0.729 |
| e5 + ING format | 0.656 | 0.635 | 0.840 | 0.709 |
| bge-large-en-v1.5 contrastive lr1e-5/4ep (3 seeds) | **0.699±0.008** | **0.677±0.017** | 0.851 | 0.750 |
| bge-reranker-large fine-tuned over retriever (3 seeds) | 0.601±0.039 (retriever 0.639) | 0.611 | | |
- bge bi-encoder: PROMOTE (provisional; dev_alias n=61 is small, +0.04 = ~3 queries, consistent across seeds).
- ING-format: REJECT. Reranker: REJECT (below its own retriever; NIL recall 0.017).
- Frozen linker candidate: bge-large-en-v1.5 contrastive, lr1e-5, 4 epochs.
