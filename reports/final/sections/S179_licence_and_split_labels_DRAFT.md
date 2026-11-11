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
| D5 H1, S1 + S2 (D-092) | recipe at a cut | frozen S questions: 24 recipes, 22 Gutenberg and 2 Wikibooks; AI_DRAFTED_GOLD; old leakage audit was on 40 drafts | near-duplicate leakage not controlled; source-family-disjoint not verified; B0 may know public text from pre-training; new frozen-set registry/audit still needed |
| D5 H3, P1-P3 + C (D-092) | evidence cell | frozen P/C questions: 40; EVD reference is the same resource used in DEL-2; old PC-1 audit counted 101 draft gold rows | not recipe-level; label `evidence resource seen in DEL-2`; draft-era counts are not a fresh frozen-set audit |
| D3 state tracking vs P1 gold (7 recipes) | recipe | P1 gold, AI-drafted and human-accepted; no held-out design | near-duplicate leakage not controlled |
| CulinaryNER, RecipeDB3 TEST (2,554 docs) | document | grouped benchmark split, frozen before TEST (commit 4ee0582) | near-duplicate leakage not controlled (groups are not checked against the identity ledger) |
| CulinaryNER, TASTEset | document | single-source split | near-duplicate leakage not controlled |
| Ingredient linker, held-out aliases and concepts | alias / concept | concept split (`tools/build_linker_data.py` buckets) | not recipe-level; label `concept split` |
| Corpus censuses: physics v06, router census 0.4.1, can-say v2, EVD coverage v2, Food.com card v2 | recipe / line | none (whole corpus) | descriptive (no split) |
| 29-diag S-1..S-4 (DEL-2 rerun) | EVD row | same seed-7 splits as DEL-2; independence groups leak fully for USDA-RETN-R6 and BOGNAR-2002 | not recipe-level; label `PRIOR_EXPOSURE` (prereg), plus the group-leak note |

No row in this table is `source-family-disjoint` today. A row moves to that label only with a check that names the
held-out family and shows that no training or tuning step read it.

## 3. Open items

- D-079 completes the recorded read of §1; final report/deck edits remain for the authors.
- Leakage grep of the finished slides and report (T9-C28-R2).
- Refresh the frozen D5 split registry and leakage audit; historical audit counts concern the drafts (40 S, 60 P/C).
- The historical S-5 naming mismatch was resolved in S188: S-5 is food-group-disjoint; S-6 is study-disjoint.
  `registry/split_registry_v1.csv` retains its older mapping and needs a new version, not a silent edit.
