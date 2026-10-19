# S093 — dataset + ledger status, and the reasoned model plan (NER · bi-encoder · autoencoder)

Written 2026-10-19 from SSOT v15 (§190.4, §245 E16-A, §257B), Master Plan v4.0 Parts K/L/N, BUILD_TRACKER, STATUS, ledger counts.
T-37 days. Course contract = DEL-1…5; FlavorTwin and large pretraining are after DEL-5 (plan §A2), so model work below is bounded
by "keep only if it earns its place against the strongest simpler baseline" (§257B promotion rule).

## 1. Ledger state (latest ACTIVE records)
| Ledger | Active | Source families | Notes |
|---|---|---|---|
| EVD | 17,978 | USDA R6, Phenol-Explorer, Bognár | 0/40 human-verified rows (DEL-1 gate) |
| REC | 89,565 | BBC 11,934 · Wikibooks 3,676 · Gutenberg silver 65,738 · … | REC.jsonl 94 MB (D-012 size watch) |
| ING / ALIAS | 2,048 / 4,103 | A1 + FoodOn + OFF + Wikibooks | FoodOn/OFF-linked ≈ 75–81% of mentions |
| KGE | 45,067 | 21 predicates | incl. 737 MOL_HAS_TASTE, 964 ING_COSYLAB_CATEGORY, 497 ING_HEALTH_ASSOCIATION (D-015) |
| MOL / IMAP | 1,726 / 30,294 | FlavorGraph, PubChem, ChemTastesDB | FlavorDB still missing |
| COND/SVAR/SNAP/SRC/STUDY | 4,414 / 224 / 346 / 487 / 125 | — | — |
| PROC / TOOL / UNIT / ALLERGEN | 156 / 119 / 74 / 8 | corpus + Wikibooks + Wikidata + FSSAI | allergen table awaits human sign-off |

## 2. Downloaded but not yet in a ledger (data/external, local-only, D-015: ASSUMED / DERIVED_ONLY)
| Dataset | Size | Best ledger route | Value for grading |
|---|---|---|---|
| RecipeDB3 NER (ingredient 26,444 rows) | 3 MB | NER eval harness only (no ledger) | matched reproduction + hygiene re-evaluation (Part K.1–2) |
| recipe_ner_dl (train/test/Machine_Annotated 84k) | 9 MB | NER training/eval; SRC + SNAP | extra labelled sentences, cross-source NER generalisation |
| cosylab_companion (AllRecipes + FOOD.com tags) | 1 MB | REC metadata (cuisine/diet tags) → ING_USED_IN_CUISINE check | independent cuisine labels |
| sustainablefooddb (118k recipes, carbon footprint) | 40 MB | new ING attribute (CFP per ingredient) + REC↔ING for dedup vs our REC | sustainability axis for COMPARE/RECOMMEND (C15 objective) |
| NOVA food processing (2,970 × 103 nutrients) | 8 MB | EVD-adjacent nutrient reference; ING processing class | processing-degree prior for PROC effects |
| AllerStack (4,316 proteins) | 16 MB | ALLERGEN support (allergen protein → ING), still needs FSSAI human sign-off | safety layer evidence |
| recipe_knowledge_mining | 18 MB | KGE (ING_CO_OCCURS cross-check) | replication source for A2-style claims |
| bittersweet · SweetpredDB · RecipeDB2 · spice-disease | small | already ingested (S088–S090) | — |

Route rule (D-009): one source → SRC record → derived rows through `LedgerStore` (never edit exported CSVs) → validators → rebuild exports → test → WORKLOG.

## 3. Sequential order from here (next units)
1. **E16-A closing**: A100 matched reproduction + clean re-evaluation of RecipeDB3 (`gpu/ner_recipedb3/`) — blocked on VPN only.
2. **Mention → ING linking (Part K.6, the stated contribution)**: bi-encoder candidate generation + cross-encoder/rules rerank; metrics Acc@1/R@5 by frequency bucket; ING-grouped splits.
3. **DEL-5 ladder B0–B5 + ablations (E16-L)**: C10/C15 now in `answer()`; time axis for C15 from PROC_TYPICAL_DURATION (39 KGE).
4. **SustainableFoodDB → ING carbon attribute** (cheap, deterministic, gives C15 a second real objective).
5. **AllerStack/NOVA** routes after human allergen sign-off.
6. Human-gated throughout: 40 verified rows, 30 sessions, benchmark (D-008), H1 send.

## 4. Model plan, reasoned

### 4.1 NER (E16-A) — what is already earned, and what is next
Measured: rules 0.774 → base+CRF 0.927 → large+CRF 0.933 (5 seeds, dev-selected); kNN-NER null; GLiNER zero-shot 0.232 exact / 0.643 relaxed
(FOOD 0.470/0.801), so GLiNER is a fallback for unseen labels only. Error profile: 46.5% of errors are boundaries, top confusion FOOD↔PHYSICAL_QUALITY.
Next steps that can still move the number, ordered by expected value per cost:
1. **Span-level decoding** (biaffine/GlobalPointer head or constrained-Viterbi BIO) instead of token softmax — attacks the 46.5% boundary errors directly. Bounded: 1 encoder × 5 seeds.
2. **Train on more labelled data**: TASTEset + RecipeDB3 (26k) + NER_DL, with source-disjoint evaluation (train on two, test on the third). This measures generalisation, which is the claim the SSOT cares about (RQ16-28), and gives RecipeDB3-trained models a fair out-of-source score.
3. **GLiNER fine-tuned** on the union (script supports `--mode finetune`); report vs encoder+CRF with paired bootstrap. Promote only if it wins on unseen-FOOD bucket.
4. **Calibration of span confidence** (temperature + isotonic on dev) so the hybrid's fixed confidences (rule 0.80–0.95, encoder 0.90, GLiNER 0.40) become measured; verifier thresholds from dev.
Not planned: larger LLM taggers (cost, no earn-in evidence), further kNN variants (null).

### 4.2 Bi-encoders — where they genuinely help
Retrieval is already settled by data: structured retrieval MRR 0.856 beats hybrid 0.704 and BM25 0.597; free-text fallback RRF(BM25 + e5-large-v2) 0.762; cross-encoders negative; dense blend on structured +0.005 n.s.
So bi-encoders do **not** go into evidence retrieval again. The open use is **mention → ING linking**:
- **Candidate generation**: embed ING canonical names + ALIAS strings (4.1k aliases, 14 languages from OFF) with a bi-encoder (e5-large-v2 zero-shot first; then SapBERT-style or contrastive fine-tune with positives = alias↔canonical, hard negatives = siblings under the same FoodOn/OFF parent).
- **Leakage guard**: aliases were used to build the lexicon, so evaluate on mentions from corpora not used for lexicon building (TASTEset, RecipeDB3, NER_DL) with ING-grouped splits for any fine-tune; report Acc@1/R@5 by ING frequency bucket (RQ16-29).
- **Baseline to beat**: current `LineLinker` (lexicon + aliases). Keep the bi-encoder only if it improves R@5 on rare/unseen foods without lowering Acc@1 on head foods; otherwise it stays a documented negative.
- **Compute**: embedding ≈ 6k strings + eval mentions → fits Mac MPS; fine-tune on A100 only if zero-shot shows headroom.

### 4.3 Autoencoders — scoped honestly
SSOT §190.4: recipe reconstruction is an information-retention objective, not evidence of useful transfer; an autoencoder can memorise identity. The report cited in §23888 explicitly deprioritises autoencoder recommenders at sparse scale. So no autoencoder is on the DEL-1…5 critical path.
One bounded use that fits the ledgers and has a testable claim:
- **Denoising/masked-ingredient autoencoder over REC ingredient sets** (mask 10–20%, predict the masked set, §190.3 protocol) as the *substitution/anomaly prior* for ING_ALTERNATIVE_TO and for flagging mislabelled categories (the RecipeDB2 errors, e.g. vanilla=Legume, shallot=Seafood, are exactly what an embedding-vs-label disagreement test would catch).
- **Baselines first** (PMI/SVD co-occurrence, then masked-set kNN); the AE ships only if it beats PMI/SVD on masked-ingredient recovery R@10 on family-grouped splits (Part N: L2 tested, L3 replicated on a second source such as SustainableFoodDB's 118k recipes).
- Everything else (VAE for molecules, graph AEs, FlavorTwin) stays ➖ after DEL-5.

## 5. Claims discipline
No "beats CoSyLab / SOTA" statement before H6 approval, a matched reproduction and a paired significant difference (Part K.8). Leakage numbers reproduce the merged plan's figures (5.1% exact / 13.6% masked) within noise: ours 5.4% ± 0.2% / 13.5% ± 0.4% over 100 splits.

## 6. First result (S094): leave-one-alias-out surface linking, zero-shot
`tools/eval_alias_linking.py` (recsys_env, MPS), 623 English alias queries vs 2,680 surfaces / 2,048 ING, `reports/ner/alias_linking_v1.json`.

| Method | Acc@1 | R@5 | MRR |
|---|---|---|---|
| char 2–4-gram TF-IDF | 0.555 | 0.783 | 0.659 |
| e5-large-v2 bi-encoder (zero-shot) | 0.607 | 0.820 | 0.699 |
| RRF fusion | 0.586 | 0.809 | 0.687 |

Paired Acc@1 bi-encoder − TF-IDF = +0.051, bootstrap 95% CI [0.014, 0.090] (excludes 0). Fusion does not beat the bi-encoder alone.
Reading: headroom is large (~40% of held-out aliases miss at rank 1), so a contrastive fine-tune with sibling hard negatives is justified
as the next bounded A100 experiment, evaluated ING-grouped. Caveat stands: surface-form generalisation only, not in-context linking.
