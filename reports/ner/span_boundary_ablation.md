# Span-boundary auxiliary head (TASTEset DEV, 5 seeds, CRF decodes; control = identical architecture without the head)
CRF+head 0.9378 vs control 0.9385 (delta −0.0008, CI [−0.0029, +0.0012], won 1/5, unseen −0.0102, boundary-error 0.0314 vs 0.0303).
Decision: REJECT (no gain, boundary errors not reduced). Backflow = base+CRF. Code kept (src/culinarystate/ner/heads.py). Head-based rescoring is a separate experiment and is not opened.
