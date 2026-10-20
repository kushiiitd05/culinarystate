# RecipeDB3 NER matched reproduction (A100)

Status: **PARTIAL** - theirs seeds 0/5, clean seeds 0/5, clean+SIZE seeds 0.
This is an apples-to-apples BASELINE (DeBERTa-base, 15 epochs, lr 5e-5, bs 16, max_len 128), NOT our final NER model. No 'beats RecipeDB3 / CoSyLab / SOTA' claim before H6.

## Headline (entity-level seqeval; mean +- sd over seeds)
| protocol / selection | n seeds | macro-F1 | micro-F1 |
|---|---|---|---|
| theirs: random 80/20, selected on TEST (best epoch) | 0 | None +- None | None +- None |
| theirs: same runs, LAST epoch (no test selection) | 0 | None +- None | None +- None |
| clean: grouped 80/10/10, selected on DEV, TEST at best-dev epoch | 0 | None +- None | None +- None |
| clean: LAST epoch | 0 | None +- None | None +- None |
| clean + SIZE label | 0 | None +- None | None +- None |

Reported by RecipeDB3 notebook: macro-F1 0.9557 (selection on test).

## Q6 Is DeBERTa+CRF still the strongest justified span-model candidate?
Not answered by this report: these runs are DeBERTa-base without CRF on RecipeDB3. TASTEset evidence (separate, exact F1): DeBERTa-v3-large+CRF 0.933, CRF significant (p=0.003). A CRF/large run on the clean RecipeDB3 split is the next NER block, not started.
