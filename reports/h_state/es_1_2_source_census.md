# ES-1.2 -- Source acquisition manifest and evidence-source census

**Status: RESEARCH + PLANNING ONLY.** Nothing was acquired, scraped, ingested, verified or simulated. EVD, Gold and all ledgers are unchanged. Web checks were made on 2026-10-22; each licence entry records how it was verified (`licence_verification`); where a statement could not be confirmed it is marked UNVERIFIED / UNKNOWN / CONFLICT, never assumed permitted.
Artifacts: `registry/data_source_acquisition_manifest.csv` (64 sources), `registry/source_claim_capability_matrix.csv`, `registry/evidence_query_matrix_v1.csv` (30 query templates with Europe PMC metadata counts), `reports/h_state/es_1_2_priority_cell_source_coverage.csv` (16 rows), `reports/h_state/es_1_2_h2_approval_queue.md`, `reports/h_state/_es_1_2_local_source_audit.json`. Generators: `tools/es12_local_source_audit.py`, `tools/build_es12_manifest.py`, `tools/es12_query_census.py`, `tools/build_es12_priority_cells.py`, `tools/write_es12_census.py`.

## 1. What the census says in five lines
1. The sources we already hold are **nutrient/phenolic retention aggregates (E3)**; no structured open source was found for **mechanism, kinetic or physical time-series** evidence. For the priority mechanisms (13 of 16 priority-cell rows) the structured-source status is **SOURCE_GAP**; the discovery route is open-access primary literature (Europe PMC / OA journals), which has large candidate pools (counts below) but needs extraction and human verification.
2. The best immediate structured wins are small: **USDA Cooking Yields (already on disk, not ingested)**, the 11 skipped Bognar tables, USDA Flavonoid DB 3.3, FNDDS/FDC portions, FDC Foundation Foods, UK CoFID factors (licence check), FSIS temperatures (manual).
3. Several local copies are **not in the SRC ledger** (USDA cooking yields, FNDDS, INFOODS density/AnFooD/uFiSh, Food.com, CoSyLab sets): provenance gaps to close before use.
4. Licence status is the main blocker for the most valuable composition sources (IFCT: BLOCKED_LICENSE; AFCD: CC BY-SA vs CC BY conflict; INFOODS: no statement; FooDB: NC reported). 21 actions need an H2 decision (`es_1_2_h2_approval_queue.md`).
5. Recipe data, ontologies, molecular identity and measured evidence are kept in separate planes; no source is credited with a capability it does not document (`source_claim_capability_matrix.csv`).

## 2. Reconciliation of what the repo already holds
SRC ledger: 488 active source records in 151 families. **Current EVD origins (unchanged, reconciled with ES-1.1 audit): USDA-RETN-R6 7,018; BOGNAR-2002 7,090 (6,594 retention + 496 yield); PHENOL-EXPLORER-3.6 3,870 from 125 primary papers (each a `pe_pub:*` SRC record with licence status UNKNOWN, publisher copyright); total 17,978, all E3.**
| Family | Ledger destinations (records) | Licence / storage (ledger) |
|---|---|---|
| GUTENBERG-PD | REC 73955 | Public domain in the USA (Project Gutenberg licence for the eBook) / VERIFIED / COMMIT_OK |
| FLAVORGRAPH | IMAP 29656, KGE 27530, MOL 1595 | Apache-2.0 (repository); data derived from Recipe1M + FlavorDB (CC BY- / ASSUMED / DERIVED_ONLY |
| BBCGF-A1 | KGE 15339, REC 11934, ALIAS 2052, ING 1951, PROC 156, TOOL 119 | Derived from bbcgoodfood.com pages (third-party copyright) / RESTRICTED / DERIVED_ONLY |
| WIKIBOOKS-COOKBOOK | KGE 15339, REC 3676, ALIAS 155, ING 97, TOOL 97 | CC BY-SA 4.0 (attribute page + revision; share-alike) / VERIFIED / LOCAL_ONLY |
| PHENOL-EXPLORER-3.6 | EVD 3870, COND 3870, SVAR 161 | Free public resource; commercial use/redistribution requires authors'  / VERIFIED / DERIVED_ONLY |
| BOGNAR-2002 | EVD 7090, COND 274, SVAR 37, MEAS 2 | Institutional report, open access in KIT repository; values cited, tex / ASSUMED / DERIVED_ONLY |
| USDA-RETN-R6 | EVD 7018, COND 270, SVAR 26, MEAS 1 | US federal government work (public domain, 17 U.S.C. §105) / ASSUMED / COMMIT_OK |
| PUBCHEM | MOL 1726, IMAP 638 | Public domain data (NCBI); cite PubChem / ASSUMED / COMMIT_OK |
| OFF-TAXONOMY | ALIAS 1896 | ODbL 1.0 (database) / DbCL (contents) / VERIFIED / COMMIT_OK |
| RECIPEDB2 | KGE 964 | No licence file; use permitted by Prof. Bagler (reported by Kush, D-01 / ASSUMED / DERIVED_ONLY |
| BITTERSWEET | KGE 524 | AGPL-3.0 / VERIFIED / COMMIT_OK |
| SPICEDISEASE | KGE 497 | No licence file; use permitted by Prof. Bagler (reported by Kush, D-01 / ASSUMED / DERIVED_ONLY |
| CHEMTASTESDB | KGE 204 | CC BY 4.0 / VERIFIED / COMMIT_OK |
| SUEATABLE | KGE 134 | No licence file in bundle; use permitted by Prof. Bagler (D-015); upst / ASSUMED / DERIVED_ONLY |
| UNITSRC-NIST_HB44_APPC | UNIT 10 | public standard / convention / ASSUMED / COMMIT_OK |
| UNITSRC-SI_BROCHURE | UNIT 9 | public standard / convention / ASSUMED / COMMIT_OK |
| SWEETPREDDB | KGE 9 | No licence file; use permitted by Prof. Bagler (reported by Kush, D-01 / ASSUMED / DERIVED_ONLY |
| FSSAI-LD-2020 | ALLERGEN 8 | Government of India publication / ASSUMED / COMMIT_OK |
| UNITSRC-UK_WMA_1985_SCH1 | UNIT 4 | public standard / convention / ASSUMED / COMMIT_OK |
| UNITSRC-CFR21_101_9 | UNIT 4 | public standard / convention / ASSUMED / COMMIT_OK |
| UNITSRC-CONV_METRIC_SPOON | UNIT 2 | public standard / convention / ASSUMED / COMMIT_OK |
| UNITSRC-CONV_AU_TBSP | UNIT 1 | public standard / convention / ASSUMED / COMMIT_OK |
| UNITSRC-CONV_METRIC_CUP | UNIT 1 | public standard / convention / ASSUMED / COMMIT_OK |
| UNITSRC-CONV_UK_DSP | UNIT 1 | public standard / convention / ASSUMED / COMMIT_OK |
| FOODON | (no ledger rows; crosswalk/refs only) | CC BY 4.0 / VERIFIED / COMMIT_OK |
| WIKIDATA | (no ledger rows; crosswalk/refs only) | CC0 1.0 (structured data) / VERIFIED / COMMIT_OK |

Local copies **without** a SRC family (provenance to be recorded before any use): USDA cooking yields (`data/external/usda_yields`), FNDDS (`data/external/fndds`, 70 MB), INFOODS density/AnFooD/uFiSh (`data/external/infoods`), Food.com (`data/external/foodcom`, CC0 only declared locally), AllerStack, NOVA nutrient CSVs, SustainableFoodDB, recipe_knowledge_mining, CoSyLab companion/NER sets, FDC SR Legacy (45.9 MB; crosswalk only). Re-ingesting USDA R6, Bognar (28/39 tables) or Phenol-Explorer would duplicate existing EVD; the only legitimate remaining Bognar work is the 11 skipped sub-variant tables.
Licence flags inside the repo: FlavorGraph (Apache-2.0 repo but data derived from Recipe1M/FlavorDB, NC upstream); CoSyLab sets (no licence file, verbal permission, D-015); USDA/Bognar licences ASSUMED in the SRC ledger; BBC corpus RESTRICTED.

## 3. Census by family (A-N) and priority
Sources by priority: {'EXISTING': 19, 'P1': 16, 'P0': 3, 'P2': 17, 'BLOCKED': 7, 'PARK': 2}; by wave: {'done': 9, 'A': 20, 'B': 10, 'none': 7, 'C': 9, 'D': 1, 'E': 8}; licence status heads: {'ASSUMED': 5, 'VERIFIED': 8, 'CC0': 6, 'PD': 1, 'UNVERIFIED': 11, 'CONFLICT': 2, 'OGL': 1, 'CC': 4, 'BLOCKED': 6, 'UNKNOWN': 2, 'NC': 3, 'SA': 1, 'TERMS': 1, 'PER': 5, 'POLICY': 1, 'METADATA': 1, 'RESTRICTIVE': 1, 'RESTRICTED': 1, 'MIXED': 2, 'PARTIAL': 1, 'FEDERAL': 1}; licence verification levels: {'CATALOG_RECORD': 7, 'SRC_LEDGER_AT_INGESTION': 19, 'CHECK_FAILED_THIS_RUN': 1, 'NOT_VERIFIED_THIS_RUN': 17, 'THIRD_PARTY_REPORT': 9, 'OFFICIAL_PAGE_QUOTED_BY_SEARCH': 11}.
Priority meaning: P0 acquire/use first; P1 second wave; P2 useful later; PARK weak/duplicative; BLOCKED access/licence/dependency; EXISTING already ingested.
Seven scores are kept separate (0 none ... 3 high; for human_verification_cost 3 = most expensive): scientific value, coverage value, condition richness, lineage quality, access/licence ease, automation feasibility, human verification cost. P0/P1 candidates:
| ID | Source | Pri | Wave | Sci | Cov | Cond | Lineage | Access | Auto | Verif.cost | Licence status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DS-040 | Open-access food-science publishers via PMC/Europe PMC (MDPI Foods/Mol | P0 | B | 3 | 3 | 2 | 3 | 2 | 2 | 3 | CC_BY_REPORTED_FOR_FOODS |
| DS-032 | Europe PMC REST API + OA full text | P0 | B | 3 | 3 | 0 | 3 | 2 | 3 | 2 | PER_ARTICLE_LICENCE |
| DS-006 | USDA Table of Cooking Yields for Meat and Poultry, Release 2 (2014) | P0 | A | 3 | 2 | 1 | 2 | 3 | 3 | 1 | CC0_REPORTED_BY_CATALOG |
| DS-043 | Open-access physical-property and drying literature (via Europe PMC /  | P1 | C | 3 | 1 | 3 | 3 | 2 | 1 | 3 | PER_ARTICLE_LICENCE |
| DS-045 | Open-access kinetic-parameter literature (Arrhenius, activation energy | P1 | C | 3 | 1 | 3 | 3 | 2 | 1 | 3 | PER_ARTICLE_LICENCE |
| DS-033 | PubMed Central Open Access Subset (comm / noncomm / other buckets) | P1 | B | 3 | 3 | 0 | 3 | 2 | 2 | 2 | PER_ARTICLE_LICENCE; ACCESS_ROUTE_CHANGE_NOT_CONFIRMED |
| DS-005 | USDA FDC - Foundation Foods | P1 | A | 3 | 1 | 1 | 3 | 3 | 3 | 1 | CC0_REPORTED_NOT_VERIFIED_THIS_RUN |
| DS-021 | ChEBI | P1 | A | 2 | 3 | 0 | 3 | 2 | 3 | 1 | UNVERIFIED |
| DS-034 | NCBI E-utilities (PubMed) | P1 | B | 2 | 3 | 0 | 3 | 2 | 3 | 1 | POLICY_RATE_LIMITS_ONLY |
| DS-047 | BRENDA (enzyme data) | P1 | C | 2 | 2 | 2 | 2 | 2 | 2 | 2 | CC_BY_4.0_WITH_ACCEPTANCE |
| DS-062 | USDA FSIS safe minimum internal temperatures / FoodSafety.gov / FDA Fo | P1 | A | 3 | 1 | 1 | 3 | 2 | 1 | 1 | FEDERAL_GUIDANCE_STATUS_PER_PAGE |
| DS-007 | USDA FNDDS (Food and Nutrient Database for Dietary Studies) | P1 | A | 2 | 3 | 0 | 2 | 3 | 3 | 1 | PD_REPORTED_BY_CATALOG |
| DS-008 | UK McCance and Widdowson's Composition of Foods Integrated Dataset (Co | P1 | A | 3 | 2 | 0 | 2 | 2 | 3 | 1 | UNVERIFIED |
| DS-009 | FSANZ Australian Food Composition Database (AFCD) Release 3 + AUSNUT 2 | P1 | A | 3 | 2 | 0 | 2 | 2 | 3 | 1 | CONFLICT_UNRESOLVED (share-alike vs attribution) |
| DS-016 | USDA Database for the Flavonoid Content of Selected Foods, Release 3.3 | P1 | A | 2 | 2 | 0 | 3 | 3 | 2 | 1 | CC0_REPORTED_BY_CATALOG |
| DS-036 | Unpaywall | P1 | B | 1 | 3 | 0 | 3 | 2 | 3 | 1 | UNVERIFIED |
| DS-046 | Rhea (biochemical reactions) | P1 | C | 2 | 2 | 0 | 3 | 3 | 3 | 1 | CC_BY_4.0 |
| DS-059 | USDA FNDDS / FDC portion tables; Open Food Facts quantities; UK MAFF p | P1 | A | 2 | 3 | 0 | 2 | 2 | 3 | 1 | PARTIAL |
| DS-014 | FAO/INFOODS Food Density Database v2.0 (+ AnFooD 2.0, uFiSh 1.0) | P1 | A | 2 | 2 | 0 | 2 | 1 | 3 | 1 | UNKNOWN_CAPABILITY_LICENCE |

## 4. What each plane can legitimately support (capability matrix summary)
- Before/after transition: DS-003. Retention: DS-001, DS-002, DS-003, DS-009. Yield: DS-002, DS-006.
- Time series: DS-043, DS-044, DS-045; kinetic fitting: DS-043, DS-044, DS-045 (literature routes and ComBase only); pH trajectory: none; moisture trajectory: DS-043; pressure effect: none.
- Reaction mechanism / products: DS-046 / DS-046 (Rhea, BRENDA provide reference reactions and in-vitro parameters, not in-food kinetics).
- Recipe procedure: DS-051, DS-052, DS-053, DS-054, DS-055, DS-057, DS-058 -- procedural only; the simulator contract forbids using it for magnitudes. Quantity conversion: DS-004, DS-007, DS-014, DS-059, DS-064. Safety guidance: DS-062, DS-063.
- Simulator parameterization: DS-043 (OA physical-property/drying literature; pure-compound NIST data partial). No open structured thermophysical food property database was identified (handbooks are copyrighted).
The matrix column `capability_basis` says whether a row was inspected locally or rests on provider descriptions/search snippets; for the latter, NO means "not claimed by anything seen", not "proven absent".

## 5. Priority-cell coverage ("where to look")
- **PC-01 garlic x crushing / cutting / resting** -> alliinase: alliin -> allicin (thiosulfinates): SOURCE_GAP (structured); local EVD rows for the matrix 0; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q01:476 / Q01:404 / Q01:24.
- **PC-02 garlic x heating (boil/fry/microwave), with or without resting after crushing** -> thermal inactivation of alliinase; allicin degradation: SOURCE_GAP (structured); local EVD rows for the matrix 0; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q02:1096 / Q02:971 / Q02:24.
- **PC-03 onion x cutting / slicing** -> alliinase + lachrymatory factor synthase -> propanethial S-oxide: SOURCE_GAP (structured); small literature pool; local EVD rows for the matrix 474; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q03:46 / Q03:34 / Q03:2.
- **PC-04 onion x boiling / frying / roasting** -> leaching, thermal degradation (flavonols, vitamin C): STRUCTURED_AVAILABLE (E3, 474 EVD rows) + literature; local EVD rows for the matrix 474; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q04:3473 / Q04:2921 / Q04:24.
- **PC-05 potato x frying (deep/shallow), baking, roasting** -> Maillard: asparagine + reducing sugars -> acrylamide: SOURCE_GAP (structured kinetics) ; literature rich; local EVD rows for the matrix 840; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q05:1240; Q06:583 / Q05:910; Q06:459 / Q05:89; Q06:28.
- **PC-06 potato x cutting / peeling** -> polyphenol oxidase enzymatic browning: SOURCE_GAP (structured); local EVD rows for the matrix 840; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q07:1835 / Q07:1594 / Q07:44.
- **PC-07 potato x boiling / steaming** -> leaching vs thermal destruction (vitamin C, polyphenols): STRUCTURED_AVAILABLE (E3) ; local EVD rows for the matrix 840; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q08:5473 / Q08:4735 / Q08:21.
- **PC-08 broccoli x steaming / boiling / blanching / chopping** -> myrosinase: glucosinolates -> isothiocyanates: SOURCE_GAP (structured mechanism); local EVD rows for the matrix 355; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q09:831 / Q09:636 / Q09:40.
- **PC-09 broccoli / green vegetables x heating with pH change** -> chlorophyll -> pheophytin (pheophytinization): SOURCE_GAP (structured); local EVD rows for the matrix 355; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q10:2550; Q13:60208 / Q10:2262; Q13:51102 / Q10:6; Q13:388.
- **PC-10 cabbage x chopping / shredding / cooking** -> myrosinase / glucosinolate hydrolysis: SOURCE_GAP (structured mechanism); local EVD rows for the matrix 256; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q11:980 / Q11:791 / Q11:26.
- **PC-11 cabbage x lactic fermentation (sauerkraut/kimchi)** -> lactic acid fermentation: pH/acidity change: SOURCE_GAP (structured); local EVD rows for the matrix 256; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q12:1161 / Q12:940 / Q12:18.
- **PC-12 apple / avocado / banana (PPO produce) x cutting / peeling** -> polyphenol oxidase browning: SOURCE_GAP (structured); local EVD rows for the matrix n/a (no EVD rows by this name); Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q14:2220 / Q14:1910 / Q14:77.
- **PC-13 wheat dough x mixing / kneading / proofing / baking** -> starch gelatinisation; gluten network; protein aggregation; fermentation: SOURCE_GAP (structured); local EVD rows for the matrix 0; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q15:1818; Q16:2592 / Q15:1512; Q16:1762 / Q15:570; Q16:258.
- **PC-14 rice x soaking / boiling / absorption cooking / cooling** -> starch gelatinisation; hydration; retrogradation: SOURCE_GAP (physical/mechanism); nutrient E3 present; local EVD rows for the matrix 129; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q17:21532; Q18:2282 / Q17:17938; Q18:1709 / Q17:59; Q18:595.
- **PC-15 beef x roasting / boiling / braising / grilling** -> water loss; protein denaturation; collagen changes: STRUCTURED_AVAILABLE (yield/moisture/fat end-points) + literature for texture/collagen; local EVD rows for the matrix 1785; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q19:5479; Q20:1093 / Q19:4597; Q20:906 / Q19:453; Q20:550.
- **PC-16 beef x searing / grilling / frying** -> Maillard / Strecker; heterocyclic amines: SOURCE_GAP (structured); local EVD rows for the matrix 1785; Europe PMC hits (mechanism, all/OA/title-abstract-OA) Q21:1145 / Q21:988 / Q21:94.
Counts are Europe PMC metadata hits (wildcard terms match full text, so they are upper bounds; the title/abstract-restricted OA column is a stricter proxy). They show where candidate literature exists, not how many usable measurements exist; garlic/onion cutting chemistry has the smallest focused pools (title-abstract OA hits: Q01 24, Q02 24, Q03 2; chlorophyll Q10 6), while potato acrylamide (Q05 89), PPO (Q07 44, Q14 77), dough (Q15 570, Q16 258), beef (Q19 453, Q20 550) and rice retrogradation (Q18 595) are larger. Precision is unmeasured and is a deliverable of ES-1.3.

## 6. Literature query taxonomy
`registry/evidence_query_matrix_v1.csv`: MATRIX x PROCESS x TARGET x MECHANISM x CONDITION templates Q01-Q30 in Europe PMC syntax, ready for the same query on OpenAlex/PubMed; each stores the all / OA / mechanism / title-abstract counts and date. No documents were downloaded.

## 7. Recommended acquisition waves (not executed)
Ordered by information/coverage gain, not row volume.
- **Wave A -- structured, reproducible, low licence risk:** (1) DS-006 USDA Cooking Yields R2 (local; beef yield/moisture/fat; fills physical-state gap); (2) finish DS-002 Bognar's 11 skipped tables; (3) DS-016 USDA Flavonoid DB 3.3; (4) DS-005 FDC Foundation Foods (replicate/method metadata, supports LOD/design fields); (5) DS-007/DS-004/DS-059 FNDDS + FDC portions and DS-014 INFOODS density (after licence reply) for POR/quantity; (6) DS-008 CoFID factors (after OGL confirmation); (7) DS-062 FSIS temperatures (manual) for WARN. Deferred inside Wave A: DS-009 AFCD (licence conflict), DS-010/011/012 composition cross-checks, IFCT (BLOCKED_LICENSE).
- **Wave B -- targeted open literature for zero-row mechanisms (H2):** order: garlic/onion cutting (alliinase/LFS: Q01-Q03), potato frying acrylamide (Q05), broccoli/cabbage myrosinase (Q09, Q11), PPO browning (Q07, Q14), chlorophyll/pheophytin (Q10, Q13); plus the 125 Phenol-Explorer cited papers as the verification seed. Routes: DS-032 Europe PMC, DS-040 OA food-science journals, DS-031 OpenAlex, DS-036 Unpaywall; DS-033 PMC only after the bulk route is confirmed.
- **Wave C -- physical and kinetic data:** dough, rice, beef texture/collagen/Maillard (Q15-Q21), drying/moisture/aw properties (Q26-Q27), kinetic parameters (Q13, Q23-Q25), BRENDA/Rhea reference priors, NIST WebBook for pure-compound parameters, ComBase for safety (terms permitting).
- **Wave D -- broader discovery and extraction at scale:** only after the ES-1.3 pilot reports extraction precision and verification throughput; includes pressure/microwave (Q28), leaching vs destruction (Q29), smoke chemistry (Q30), frying oils (Q22), sugar chemistry (Q25).
- **Wave E -- recipe semantic expansion:** Food.com after S116 confirmation, existing Wikibooks/Gutenberg, RecipeDB when the key arrives, r-FG only after its licence is verified; no scraping of recipe sites.

## 8. ES-1.1 deficits and the workstream that can resolve each (not fixed here)
| ES-1.1 deficit | Resolving source / workstream |
|---|---|
| 0 human-verified EVD rows | HV-001/HV-003; ES-1.3 pilot; Phenol-Explorer's 125 cited papers (DS-003) and OA primary studies (DS-032/DS-040) |
| 6,409 rows without ingredient_id | linking workstream (matrix names are USDA/Bognar food-group strings): FDC/FoodOn crosswalk (DS-004/005/027) + human link review HV-008; not a new-source problem |
| 5,536 rows without prior_state_id | controlled prior-state vocabulary from FoodOn/LanguaL processing terms (DS-027/030) + new primary studies that state the initial state |
| LOD/LOQ absent | primary literature (DS-040/043) and analytical databases with method metadata (DS-005); not recoverable from USDA/Bognar aggregates |
| Phenol-Explorer design strength unresolved | re-read the 125 cited primary papers (DS-003 seed; OA copies via DS-031/036); human task HV-003 |
| 278 Phenol-Explorer retention-vs-derived discrepancies | check cited tables in the primary papers and PE's yield sources (human, HV-003) |
| 7 state-variable equivalences unresolved | ChEBI/PubChem identity (DS-020/021) and analytical-method notes; human/analytical decision |
| Physical-state coverage very sparse | DS-006 (mass/moisture/fat, beef), DS-002 yields, DS-005; OA physical-property/drying literature (DS-043); structured texture/colour/phase = SOURCE_GAP |
| Mechanism evidence absent for priority families | DS-032/DS-040 literature (Wave B) with DS-046/047 reference reactions; structured mechanism data = SOURCE_GAP |

## 9. Pass-gate check
- Every current source reconciled: yes (Section 2; SRC families, local dirs, ingestion scripts).
- Candidate sources have explicit licence/access status: yes (`licence_status`, `licence_verification`); unconfirmed ones are marked.
- Capabilities bounded per source: yes (capability matrix with basis column).
- Recipe, ontology, molecular and experimental evidence not conflated: yes (evidence_plane + matrix).
- Priority zero-row mechanisms have discovery routes or SOURCE_GAP: yes (priority-cell table; 13 SOURCE_GAP rows, all with a literature route).
- First waves ranked; H2 actions isolated: yes (Section 7; H2 queue).
- No new data acquired; no scientific values invented: yes (only metadata hit counts were requested from the Europe PMC search API; nothing stored but counts).
- Items marked BLOCKED_LICENSE / BLOCKED_ACCESS / UNKNOWN_CAPABILITY: IFCT; FoodAtlas; FlavorDB; RecipeDB API; paywalled indexes; ASHRAE/handbooks; KEGG; PMC bulk route (post Aug-2026); INFOODS and CoFID/AFCD licences; EFSA acrylamide data; ComBase.

## 10. Non-blocking documentation backlog
`reports/ner/ner_program_closeout.md` is recorded in `docs/BACKLOG_NONBLOCKING.md`; it did not interrupt ES-1.2.

## 11. Next step (not started)
STEP 10 / ES-1.3 -- 20-row mechanism evidence extraction + human-verification pilot. Required first: your review of this census and H2 decisions #1, #3, #4 (Europe PMC full-text capture, NCBI registration, Unpaywall terms) and the choice of the pilot mechanism. The counts favour potato frying/acrylamide (Q05: 910 OA full-text hits with mechanism, 89 title-abstract OA) over garlic alliinase (Q01: 404 / 24) and onion LFS (Q03: 34 / 2) for a 20-row pilot; garlic remains the higher-priority zero-row cell, so this is a decision for you.
