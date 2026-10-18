# Resource + graph gap map (SSOT deep-dive, 2026-10-18, S043)

Sources read: SSOT §12.7.3, §47.x (licences), §65.x (compound-link honesty), §96.x (FlavorGraph gate), §157/§175.3
(data inventory), §198.7 (data reality), §203 (resource priority), §225.5 (KG construction), §227.8 (priority list),
the Level-12 entity/relation lists (lines ~9248–9290).

## A. Resources the SSOT names
| Resource (SSOT §) | Role | Licence (SSOT §47.x / checked) | Status |
|---|---|---|---|
| USDA retention R6 (§203.3 A) | process-effect evidence | public domain | ✅ EVD 7,018 |
| Phenol-Explorer retention (§203.3 A) | polyphenol evidence | DB terms | ✅ EVD 3,870 |
| Bognár 2002 (retention tables, EuroFIR family) | process-effect evidence | open-access report | ✅ EVD 6,594 |
| FoodData Central raw/cooked (§198.7) | matched composition pairs | public domain | ✅ X15: 867 description pairs, 16,365 dry-basis ratios (4,984 analytical) vs R6 → `reports/del2/fdc_pairs_v1.md`; candidates, not EVD |
| FoodAtlas 2026 (§9048, §227.8) | food–chemical evidence graph (1,430 foods × 3,610 chemicals, 48,474 quantitative) | code MIT; **data CC BY-NC 4.0 since 2026-10-09** (repo LICENSE-DATA.md) | ⛔ X13: bundles private (pre-signed S3 via site, bot checkpoint) → manual download (MANUAL_NEXT_STEPS #12); candidate, not ground truth (§9119) |
| FlavorGraph (§96.x, §4296) | ingredient–compound + co-occurrence graph, E4/B4 baseline | Apache-2.0 repo; data from FlavorDB/Recipe1M | ✅ X9: counts match release (8,298 nodes / 147,179 edges); +1,595 MOL, 29,656 IMAP PRESENCE, ING_CO_OCCURS\|FLAVORGRAPH; NC upstream → no redistribution |
| FooDB (§175.3) | food constituents with concentrations | CC BY-NC 4.0 | ⛔ site 403 to scripts → manual download (MANUAL_NEXT_STEPS) |
| FlavorDB2 / RecipeDB (§175.3) | molecules ↔ ingredients; recipes | CC BY-NC-SA 3.0, API via Prof. Bagler | ⏳ H1 email |
| ChemTastesDB (§175.3) | taste classes for molecules | CC BY 4.0 (Zenodo 15051366) | ✅ X11: 204 MOL_HAS_TASTE (curated class) |
| BitterDB, Pyrfume, GS-LF, Keller/DREAM (§175.3) | odour/taste labels | free / per-source | later (FlavorTwin scope is out, final prompt) |
| TASTEset (§2295, §4216) | recipe NER reference | MIT | ✅ X10: rule floor micro F1 0.791 exact / 0.898 relaxed (`reports/ner/`) |
| OpenPI / r-FG / NHK-state (§227.8) | procedural state-change corpora | OpenPI MIT; r-FG repo not found | ✅ X12: food subset 197 procedures, 7,629 state changes |
| Recipe1M+ (§463, §2896) | 1M recipes | research access, no open licence | ⛔ needs human terms acceptance |
| BioModels BIOMD0000000052 (§175.3) | Maillard ODE (sugar–casein) | open | later (P9 reaction substrate) |
| Maillard / acrylamide kinetic literature (§203.3 C) | kinetics | papers | via verification queue Route B |
| FoodOn (§225.5) | food ontology | CC BY 4.0 | ✅ crosswalk |
| PubChem (§65.x) | molecule anchor | open | ✅ MOL 131 → 1,726 (FlavorGraph compounds) |

## B. Relations the SSOT names vs what exists
SSOT core relations: HAS_QUANTITY, HAS_UNIT, HAS_FORM, HAS_STATE, UNDERGOES, USES_TOOL, USES_MEDIUM, AT_TEMPERATURE,
FOR_DURATION, PRODUCES, CONSUMES, PRECEDES, REFERS_TO, ALTERNATIVE_TO, OPTIONAL_IF.

| SSOT relation | Concept-level KGE now | Gap → planned predicate (X14, mined from 3 recipe corpora) |
|---|---|---|
| UNDERGOES | ING_PROCESSED_BY ✅ | — |
| USES_TOOL | PROC_USES_TOOL ✅ | — |
| PRECEDES | PROC_FOLLOWED_BY ✅ | — |
| FOR_DURATION / AT_TEMPERATURE | PROC_TYPICAL_DURATION / _TEMPERATURE ✅ | — |
| HAS_UNIT | ING_MEASURED_IN_UNIT ✅ | — |
| ALTERNATIVE_TO | ING_ALTERNATIVE_TO ✅ (X14) | mined; closed vocabulary — **ING_ALTERNATIVE_TO** ("butter or margarine") |
| OPTIONAL_IF | ING_OFTEN_OPTIONAL ✅ (X14) | mined; closed vocabulary — **ING_OFTEN_OPTIONAL** (share of lines marked optional / to taste) |
| HAS_FORM | ING_PREP_FORM ✅ (X14) | mined; closed vocabulary — **ING_PREP_FORM** (chopped, minced, grated … per ingredient) |
| USES_MEDIUM | PROC_USES_MEDIUM ✅ (X14) | mined; closed vocabulary — **PROC_USES_MEDIUM** (water, oil, butter, stock, milk) |
| HAS_STATE / PRODUCES (endpoint) | PROC_ENDPOINT_STATE ✅ (X14) | mined; closed vocabulary — **PROC_ENDPOINT_STATE** ("until golden", "until tender", "until thickened") |
| ingredient → compound (§65.x) | IMAP PRESENCE ✅ (FlavorGraph, qualitative; X9) | FoodAtlas quantitative (X13) |
| REFERS_TO / CONSUMES | instance-level (DEL-3 state engine), not concept edges | — |

## C. Order (sequential, D-009)
X14 corpus-mined predicates → X9 FlavorGraph → X10 TASTEset → X11 ChemTastesDB → X12 OpenPI → X13 FoodAtlas →
X15 FDC raw/cooked pairs → X7 recipe-scrapers → X8 NER (A100).
