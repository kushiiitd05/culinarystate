# Report section draft: data licences and split labels (S179)

Status: **AI_DRAFTED** for the final report and the release card (board items T9-C28-R1 and T9-C09-R3). It needs a
human read before it goes in (T9-C28-R1 acceptance: "paragraph reviewed"). It states what the registries record and
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

Checks the acceptance needs before this is final:
- **[human]** read and accept the paragraph, or edit it;
- **[agent, T9-C28-R2]** grep the slides, the report and the screenshots against the git-ignored raw text. This waits
  for the slides and report to exist.

## 2. Split label for every recipe-level result (T9-C09-R3)

**Rule.** Each results table carries a `split` column with one of two labels:
- `source-family-disjoint`, only where the test units come from a source family that no training or tuning step
  saw;
- otherwise, `near-duplicate leakage not controlled`.

The reason is that the recipe identity ledger is provisional. 07I-R uses uncalibrated star clustering, and the 07I-C
human calibration produced blind kappas of 0.571 and 0.588. Absence of a duplicate in that ledger is weak evidence,
so no recipe-level result can claim near-duplicate control. Descriptive corpus censuses have no test split; they
carry `descriptive (no split)`.

| Result (where it appears) | Unit | Split basis | Label |
|---|---|---|---|
| D5 H1, S1 + S2 (not run) | recipe at a cut | sampled from Wikibooks and Gutenberg only; 0 of 40 drafted S recipes in the gold index or the 7 Rung A dev samples (leakage audit S-1, S-2) | near-duplicate leakage not controlled; source-family-disjoint not verified. Also: 38 of 40 are Gutenberg prose, so H1 speaks only to that text type, and B0 may know public text from pre-training |
| D5 H3, P1-P3 + C (not run) | evidence cell | gold EVD rows: 101 of 101 are in the DEL-2 / 29-diag pool (PC-1) | not recipe-level; label `evidence rows seen in DEL-2` |
| D3 state tracking vs P1 gold (7 recipes) | recipe | P1 gold, AI-drafted and human-accepted; no held-out design | near-duplicate leakage not controlled |
| CulinaryNER, RecipeDB3 TEST (2,554 docs) | document | grouped benchmark split, frozen before TEST (commit 4ee0582) | near-duplicate leakage not controlled (groups are not checked against the identity ledger) |
| CulinaryNER, TASTEset | document | single-source split | near-duplicate leakage not controlled |
| Ingredient linker, held-out aliases and concepts | alias / concept | concept split (`tools/build_linker_data.py` buckets) | not recipe-level; label `concept split` |
| Corpus censuses: physics v06, router census 0.4.1, can-say v2, EVD coverage v2, Food.com card v2 | recipe / line | none (whole corpus) | descriptive (no split) |
| 29-diag S-1..S-4 (DEL-2 rerun) | EVD row | same seed-7 splits as DEL-2; independence groups leak fully for USDA-RETN-R6 and BOGNAR-2002 | not recipe-level; label `PRIOR_EXPOSURE` (prereg), plus the group-leak note |

No row in this table is `source-family-disjoint` today. A row moves to that label only with a check that names the
held-out family and shows that no training or tuning step read it.

## 3. Open items

- Human read of §1 (T9-C28-R1).
- Leakage grep of the finished slides and report (T9-C28-R2).
- Recompute the D5 rows of §2 once the benchmark is frozen; the audit counts are on the draft (40 S, 60 P/C).
- S-5 naming mismatch: the prereg says "food-group disjoint", but the runner builds `study_disjoint`. One must change
  (leakage audit, registry findings).
