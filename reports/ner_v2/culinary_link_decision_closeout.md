# CulinaryLinkDecision-v1 -- closeout and linking decision record

Status: **CLOSED. D3 / DISTILL-A.** Evidence: `culinary_link_decision_final_report.md` (cbddba8), scores `_final_link_scores.json`.

## Decision
- **Operational linker: BGE retrieval / top-1** (strict Acc@1 0.881). Pipeline: NER span -> BGE retrieval -> canonical candidate, with the already-justified advisory-only NIL.
- **Rejected for deployment:** Tev1-4B (0.872), Nimble (0.881), CD-L1 (0.798), CD-L2 (0.862; CD-L2 - BGE = -0.019 [-0.043, +0.005]), zero-shot cross-encoder (0.619). No tested method supports safe autonomous NIL (BGE NIL AUROC 0.852 is highest).
- **Preserved secondary finding (DISTILL-A):** CD-L2 - CD-L1 = +0.064 [+0.038, +0.089]; all CD-L2 seeds beat all CD-L1 seeds. Wording: "teacher supervision materially improves the compact student relative to gold-only training, but the resulting student does not outperform BGE on fresh evaluation." Not: "distillation improves canonical linking overall." Recorded as a partial/negative result.
- **Sealed:** the 850-item set is historical evidence. Allowed: descriptive error analysis, reporting, limitations, stratum breakdowns. Not allowed: architecture/threshold/hyperparameter changes or retrain-and-rescore against it. Any new linking work needs new development and evaluation data. The 441 fresh set stays sealed. NER v1 untouched.
- **Process lesson:** DEV (n=61) Tev 0.836 > BGE 0.721; FINAL (n=430) BGE 0.881 > Tev 0.872. Fresh double-annotated human evaluation prevented a false deployment claim.
