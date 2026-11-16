# Report section draft: data licences and split labels (S179)

Status: **AI_DRAFTED** for the final report and the release card (board items T9-C28-R1 and T9-C09-R3). D-079
records Kush's acceptance of the licence paragraph. It states what the registries record and
does not verify or change any licence. Written 2026-11-10 by the Mac agent on `kush/s179-finish-fixes`.

Sources: `registry/recipe_source_usage_registry_v1.csv`, `registry/data_source_acquisition_manifest.csv`, the SRC
ledger, `DECISIONS.md` D-003, `src/culinarystate/decision/public_mode.py`, `registry/split_registry_v1.csv` and
`reports/s178/leakage_audit_d5_findings.md`.

## 1. Licence and redistribution paragraph (T9-C28-R1)

> **Data, licences and what is shown.** The project reads five recipe sources. Their status, as recorded in
> `registry/recipe_source_usage_registry_v1.csv`, is:
> - **BBC Good Food** (11,934 recipes, scraped for an earlier course assignment) is third-party copyright,
>   LOCAL_RESEARCH_ONLY. Its text stays on one researcher's machine. It never goes to a server or an external
>   service, and it is never committed (D-003).
> - **Food.com** (Kaggle download) is declared CC0 by the uploader, but that authority is not verified
>   (LICENCE_UNVERIFIED), so its text is not redistributed either.
> - **TASTEset** is LICENCE_UNVERIFIED in the usage registry. The acquisition manifest notes an MIT licence, but no
>   source row confirms it.
> - **Wikibooks Cookbook** pages are CC BY-SA 4.0, with attribution by page and revision.
> - **Project Gutenberg** cookbooks (338 books) are public domain in the USA under the Project Gutenberg licence.
>
> Process-effect evidence comes from:
> - the USDA retention tables (US government work, public domain);
> - Phenol-Explorer 3.6, a free public resource whose redistribution needs the authors' permission. We therefore
>   publish only derived counts and identifiers from it, never its tables. The publications it cites remain under
>   publisher copyright and are cited, not reproduced.
>
> Everything committed or shown in this report, the slides and the demo screenshots is counts, identifiers, hashes
> and figures computed from them. No recipe text from BBC Good Food or Food.com appears.
>
> The demo has a public mode for anything that is not the researcher's own machine. It drops every knowledge-graph
> edge computed over the BBC corpus before any answer is built, and it omits the carbon figures, whose upstream
> licence is unverified. In local mode, any request that arrives through a tunnel or proxy is refused (HTTP 503).

Checks before final assembly:
- **DONE D-079:** Kush read and accepted the licence paragraph; this is not independent licence verification;
- **[agent, T9-C28-R2]** grep the slides, the report and the screenshots against the git-ignored raw text. This waits
  for the slides and report to exist.

## 2. Split label for every recipe-level result (T9-C09-R3)

Updated 12 November 2026 from `registry/d5_frozen_split_registry_v3.csv` and
`reports/s179/d5_frozen_split_leakage_v3.{json,md}`. This additive refresh supersedes the historical
frozen-D5 refresh-to-do in §3; old registries and draft-era audits remain unchanged.
**AI_PRECHECKED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

**Rule.** Each recipe-level results table carries `source-family-disjoint` only where an explicit check shows
that no training or tuning step saw the held-out family; otherwise it carries
`near-duplicate leakage not controlled`. Descriptive corpus censuses carry `descriptive (no split)`.
The identity ledger remains provisional: 07I-R star clustering is uncalibrated, and the 07I-C blind kappas
were 0.571 and 0.588. Exact recipe-ID nonoverlap and provisional-group nonoverlap cannot establish near-duplicate
control. No row below establishes source-family independence.

| Result (where it appears) | Unit | Current split/exposure evidence | Label |
|---|---|---|---|
| D5 H1, S1 + S2 (D-092) | recipe at a cut | 24 frozen recipes: 22 Gutenberg, 2 Wikibooks; 12 per block, no shared recipe ID. Zero overlaps with 50 gold recipe IDs, seven declared seeded Rung-A/dev samples and 68 J4 hashes. Identity groups provisional; full-corpus label-free development is prior exposure; public-text pretraining unknown. Gold is AI_DRAFTED_GOLD. | near-duplicate leakage not controlled; source-family-disjoint not verified |
| D5 H1, NER surface exposure supplement | normalized ingredient line | Only 2 Wikibooks recipes provide ingredient lines: 9 total. Exact matches: RecipeDB3 train 1/9, calibration 0/9, dev 0/9, test 1/9; TASTEset any split 2/9. The 22 Gutenberg segments expose no ingredient-line channel. | surface exposure only; no learned-NER accuracy, whole-recipe identity or independence conclusion |
| D5 H3, P1-P3 + C (D-092) | evidence cell | 40 frozen questions, 10 per block; 79 distinct gold EVD IDs, all in the 17,458-row DEL-2 retention pool. Shared gold IDs: C/P1=2, C/P2=1, P1/P2=9. Retrieval-silver overlap: 2 gold IDs, 1 gold cell, 13/44 ingredient/process pairs. | not recipe-level; evidence resource seen in DEL-2; positive overlap retained |
| D5 U + X | authored control question | 5 questions per block; no stochastic training/test draw. Whole freeze is 74 questions across eight blocks. | authored controls; not independent empirical gold |
| D3 state tracking vs P1 gold (7 recipes) | recipe | P1 gold, AI-drafted and human-accepted; no held-out design | near-duplicate leakage not controlled |
| CulinaryNER, RecipeDB3 TEST (2,554 docs) | document | grouped benchmark split, frozen before TEST (commit 4ee0582) | near-duplicate leakage not controlled (groups not checked against identity ledger) |
| CulinaryNER, TASTEset | document | single-source split | near-duplicate leakage not controlled |
| Ingredient linker, held-out aliases and concepts | alias / concept | concept buckets; frozen S1 gold concepts train/dev/test=25/4/5; P/C concepts=16/3/8 | not recipe-level; concept split, with exposure disclosed |
| Corpus censuses: physics v06, router census 0.4.1, can-say v2, EVD coverage v2, Food.com card v2 | recipe / line | none (whole corpus) | descriptive (no split) |
| 29-diag S-1…S-6 | EVD row / declared group | Recorded manifest/result hashes retained, not private post-seal assignment reconstruction. Actual S-5 is food-group-disjoint; S-6 study-disjoint. Historical registry's older S-5 naming preserved. USDA-RETN-R6 and BOGNAR-2002 lineage limitations remain. | not recipe-level; PRIOR_EXPOSURE where recorded; provisional lineage is not independent-study certification |
| Strict-v2 runtime diagnostic, 12 November | synthetic metadata-template call | 1,000 calls, including 200 synthetic recipe requests; no held-out natural-user distribution | engineering diagnostic; not a scientific or accuracy result |

The 29-diag and 07.A-R1 entries in the refresh are `RECORDED_PROVENANCE_NOT_REDERIVED`; 07.A-R1 remains
NOT_RUN under D-085. No sealed assignment is fabricated. The v3 audit supplies fresh frozen-D5 counts;
v2 remains the historical missing-input run. Positive source/evidence exposure is reported, not removed.
No table row becomes `source-family-disjoint` without a named held-out-family and training/tuning exposure check.

## 3. Open items

- D-079 completes the recorded read of §1; final report/deck edits remain for the authors.
- Leakage grep of the finished slides and report (T9-C28-R2).
- Refresh the frozen D5 split registry and leakage audit; historical audit counts concern the drafts (40 S, 60 P/C).
- The historical S-5 naming mismatch was resolved in S188: S-5 is food-group-disjoint; S-6 is study-disjoint.
  `registry/split_registry_v1.csv` retains its older mapping and needs a new version, not a silent edit.
