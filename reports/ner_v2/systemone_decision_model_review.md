# System-One decision models: what is public, what is reproducible (V2-DM, branch separate from NER v1)

NER v1 (tag `ner-v1-closeout`, H6-C) is immutable. This note belongs to the prospective **V2-DM** lane. Facts below were read on 2026-10-21 from the Ollama docs page, the Tev1 repo/README, and the Ollama library pages of Tev1 and Nimble; items marked (secondary) were not read at the source.

## Jev (TypeSafe AI)
Proprietary, API-hosted decision model (launch reported 2026-09-15, secondary). Reported design: typed decisions (Choice / Noul / Score) returned as probabilities, trained with a calibration method TypeSafe calls RLCD, with a new architecture and parallel sampler (TypeSafe blog as relayed in the research note; secondary). **Weights, architecture and the RLCD recipe are not public. Jev is not reproduced here.** A community "Jev reproduction" repo claims only the decision-inference mechanism (secondary, README not read).

## What Ollama implements (docs/capabilities/decision.mdx)
- `POST /v1/systemone` with `model`, `state` (text), `questions` (named; types `choice` 2-26 options, `noul` true/false, `score` 2-10 ordered levels). Minimum Ollama **v0.35.0**. Local needs no key; `:cloud` models would send data to ollama.com (**forbidden for protected recipe text**).
- Choice returns per-option `probabilities` + `confidence`; noul returns P(true); score returns a probability-weighted level. Context cap 65,536 tokens, request body <= 64 KiB.
- **No calibration claim**: `confidence` = how concentrated the distribution is, "a higher value does not guarantee the answer is correct". Not supported by the Ollama CLI or Python/JS libraries (HTTP API only).

## Tev1 (Together AI) -- open recipe
Base Qwen3.5-4B, ordinary LoRA SFT (rank 8, 1 epoch, lr 5e-5, 2,048 tokens). Code and docs MIT; **weights licence not stated on the pages read** (check the Hugging Face model card; dataset sources in `DATA_SOURCES.md` / `sources.lock.json` carry their own terms). 37,840 train / 4,568 validation examples (language classification, policy decisions, routing, synthetic research classification). Public: data builders, training example, evaluation code; not bundled: data and weights. **No RLCD**; the repo says returned logprobs are "model preferences, not calibrated confidence". Ollama tags: `tev1:4b` (4.4-4.6 GB), `tev1:0.8b` (0.8-1.5 GB); runs with ~2,000 tokens of context; not tested for calibration, non-English, out-of-distribution input. Reported accuracy: Together dev numbers 88.0% (not independent); Ollama 13-dataset mean 73.3% (4B), 63.5% (0.8B).

## Nimble (Bespoke Labs)
Qwen3.5-9B fine-tune, **Apache-2.0**, ~9.4 GB, prompts must fit 8,192 tokens, text only. Ollama 13-dataset mean 75.7% (Jev 1.13: 76.0%); held-out 324 examples 90.1% (Jev 93.2%). Page: a probability is not a measured accuracy rate, test thresholds on your own data.

## Conclusions for us
1. Reproducible: the **typed decision interface and candidate scoring**, via open weights (Tev1, Nimble) served locally. Not reproducible: Jev's weights, architecture, RLCD.
2. Probabilities are **normalised candidate scores, not known-calibrated probabilities**; calibration on our data is mandatory (protocol section G).
3. Licences to record before use: Tev1 weights (HF card), Qwen3.5 base licence, Nimble Apache-2.0; no data leaves the lab server.
4. Vendor numbers are on generic decision tasks, not recipe NER; they say nothing about our review problem.
