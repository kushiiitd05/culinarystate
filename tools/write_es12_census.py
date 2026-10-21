#!/usr/bin/env python3
"""ES-1.2 census report generator (numbers from the registry CSVs)."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
man = list(csv.DictReader(open(ROOT / "registry/data_source_acquisition_manifest.csv", encoding="utf-8")))
cap = list(csv.DictReader(open(ROOT / "registry/source_claim_capability_matrix.csv", encoding="utf-8")))
qm = list(csv.DictReader(open(ROOT / "registry/evidence_query_matrix_v1.csv", encoding="utf-8")))
pc = list(csv.DictReader(open(ROOT / "reports/h_state/es_1_2_priority_cell_source_coverage.csv", encoding="utf-8")))
loc = json.load(open(ROOT / "reports/h_state/_es_1_2_local_source_audit.json"))
pri = Counter(r["priority"] for r in man)
wave = Counter(r["acquisition_wave"] for r in man)
lic = Counter(r["licence_status"].split(" ")[0].split("_")[0] for r in man)
ver = Counter(r["licence_verification"] for r in man)
fam = Counter(r["source_family"][0] for r in man)
caps = [k for k in cap[0] if k not in ("source_id", "source_name", "priority", "capability_basis", "note")]
yes = {k: [r["source_id"] for r in cap if r[k] == "YES"] for k in caps}
fmt_ids = lambda ids: ", ".join(ids) if ids else "none"
sc = lambda r: sum(int(r[k]) for k in ("score_scientific_value", "score_coverage_value", "score_condition_richness", "score_lineage_quality"))
top = [r for r in man if r["priority"] in ("P0", "P1")]
top.sort(key=lambda r: (r["priority"], -sc(r)))
srcgap = [r for r in pc if "SOURCE_GAP" in r["discovery_status"]]
n_hit = lambda key: {r["query_id"]: r[key] for r in qm}
fam_ledgers = {f: v for f, v in loc["families"].items() if not f.startswith("pe_pub")}
pe_pub = [v for f, v in loc["families"].items() if f.startswith("pe_pub")]
txt = f"""# ES-1.2 -- Source acquisition manifest and evidence-source census

**Status: RESEARCH + PLANNING ONLY.** Nothing was acquired, scraped, ingested, verified or simulated. EVD, Gold and all ledgers are unchanged. Web checks were made on 2026-10-22; each licence entry records how it was verified (`licence_verification`); where a statement could not be confirmed it is marked UNVERIFIED / UNKNOWN / CONFLICT, never assumed permitted.
Artifacts: `registry/data_source_acquisition_manifest.csv` ({len(man)} sources), `registry/source_claim_capability_matrix.csv`, `registry/evidence_query_matrix_v1.csv` ({len(qm)} query templates with Europe PMC metadata counts), `reports/h_state/es_1_2_priority_cell_source_coverage.csv` ({len(pc)} rows), `reports/h_state/es_1_2_h2_approval_queue.md`, `reports/h_state/_es_1_2_local_source_audit.json`. Generators: `tools/es12_local_source_audit.py`, `tools/build_es12_manifest.py`, `tools/es12_query_census.py`, `tools/build_es12_priority_cells.py`, `tools/write_es12_census.py`.

## 1. What the census says in five lines
1. The sources we already hold are **nutrient/phenolic retention aggregates (E3)**; no structured open source was found for **mechanism, kinetic or physical time-series** evidence. For the priority mechanisms ({len(srcgap)} of {len(pc)} priority-cell rows) the structured-source status is **SOURCE_GAP**; the discovery route is open-access primary literature (Europe PMC / OA journals), which has large candidate pools (counts below) but needs extraction and human verification.
2. The best immediate structured wins are small: **USDA Cooking Yields (already on disk, not ingested)**, the 11 skipped Bognar tables, USDA Flavonoid DB 3.3, FNDDS/FDC portions, FDC Foundation Foods, UK CoFID factors (licence check), FSIS temperatures (manual).
3. Several local copies are **not in the SRC ledger** (USDA cooking yields, FNDDS, INFOODS density/AnFooD/uFiSh, Food.com, CoSyLab sets): provenance gaps to close before use.
4. Licence status is the main blocker for the most valuable composition sources (IFCT: BLOCKED_LICENSE; AFCD: CC BY-SA vs CC BY conflict; INFOODS: no statement; FooDB: NC reported). 21 actions need an H2 decision (`es_1_2_h2_approval_queue.md`).
5. Recipe data, ontologies, molecular identity and measured evidence are kept in separate planes; no source is credited with a capability it does not document (`source_claim_capability_matrix.csv`).

## 2. Reconciliation of what the repo already holds
SRC ledger: {sum(v['n_src_records'] for v in loc['families'].values())} active source records in {len(loc['families'])} families. **Current EVD origins (unchanged, reconciled with ES-1.1 audit): USDA-RETN-R6 7,018; BOGNAR-2002 7,090 (6,594 retention + 496 yield); PHENOL-EXPLORER-3.6 3,870 from {len(pe_pub)} primary papers (each a `pe_pub:*` SRC record with licence status UNKNOWN, publisher copyright); total 17,978, all E3.**
| Family | Ledger destinations (records) | Licence / storage (ledger) |
|---|---|---|
""" + "\n".join(f"| {f} | {', '.join(f'{k} {v}' for k, v in sorted(d['records_by_ledger'].items(), key=lambda kv: -kv[1])) or '(no ledger rows; crosswalk/refs only)'} | {list(d['licences'])[0][:70]} / {list(d['licence_status'])[0]} / {list(d['storage_rule'])[0]} |" for f, d in sorted(fam_ledgers.items(), key=lambda kv: -sum(kv[1]['records_by_ledger'].values()))) + f"""

Local copies **without** a SRC family (provenance to be recorded before any use): USDA cooking yields (`data/external/usda_yields`), FNDDS (`data/external/fndds`, 70 MB), INFOODS density/AnFooD/uFiSh (`data/external/infoods`), Food.com (`data/external/foodcom`, CC0 only declared locally), AllerStack, NOVA nutrient CSVs, SustainableFoodDB, recipe_knowledge_mining, CoSyLab companion/NER sets, FDC SR Legacy (45.9 MB; crosswalk only). Re-ingesting USDA R6, Bognar (28/39 tables) or Phenol-Explorer would duplicate existing EVD; the only legitimate remaining Bognar work is the 11 skipped sub-variant tables.
Licence flags inside the repo: FlavorGraph (Apache-2.0 repo but data derived from Recipe1M/FlavorDB, NC upstream); CoSyLab sets (no licence file, verbal permission, D-015); USDA/Bognar licences ASSUMED in the SRC ledger; BBC corpus RESTRICTED.

## 3. Census by family (A-N) and priority
Sources by priority: {dict(pri)}; by wave: {dict(wave)}; licence status heads: {dict(lic)}; licence verification levels: {dict(ver)}.
Priority meaning: P0 acquire/use first; P1 second wave; P2 useful later; PARK weak/duplicative; BLOCKED access/licence/dependency; EXISTING already ingested.
Seven scores are kept separate (0 none ... 3 high; for human_verification_cost 3 = most expensive): scientific value, coverage value, condition richness, lineage quality, access/licence ease, automation feasibility, human verification cost. P0/P1 candidates:
| ID | Source | Pri | Wave | Sci | Cov | Cond | Lineage | Access | Auto | Verif.cost | Licence status |
|---|---|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(f"| {r['source_id']} | {r['source_name'][:70]} | {r['priority']} | {r['acquisition_wave']} | {r['score_scientific_value']} | {r['score_coverage_value']} | {r['score_condition_richness']} | {r['score_lineage_quality']} | {r['score_access_licence_ease']} | {r['score_automation_feasibility']} | {r['score_human_verification_cost']} | {r['licence_status'][:60]} |" for r in top) + f"""

## 4. What each plane can legitimately support (capability matrix summary)
- Before/after transition: {fmt_ids(yes['before/after transition'])}. Retention: {fmt_ids(yes['retention'])}. Yield: {fmt_ids(yes['yield'])}.
- Time series: {fmt_ids(yes['time series'])}; kinetic fitting: {fmt_ids(yes['kinetic fitting'])} (literature routes and ComBase only); pH trajectory: {fmt_ids(yes['pH trajectory'])}; moisture trajectory: {fmt_ids(yes['moisture trajectory'])}; pressure effect: {fmt_ids(yes['pressure effect'])}.
- Reaction mechanism / products: {fmt_ids(yes['reaction mechanism'])} / {fmt_ids(yes['reaction products'])} (Rhea, BRENDA provide reference reactions and in-vitro parameters, not in-food kinetics).
- Recipe procedure: {fmt_ids(yes['recipe procedure'])} -- procedural only; the simulator contract forbids using it for magnitudes. Quantity conversion: {fmt_ids(yes['quantity conversion'])}. Safety guidance: {fmt_ids(yes['safety guidance'])}.
- Simulator parameterization: {fmt_ids(yes['simulator parameterization'])} (OA physical-property/drying literature; pure-compound NIST data partial). No open structured thermophysical food property database was identified (handbooks are copyrighted).
The matrix column `capability_basis` says whether a row was inspected locally or rests on provider descriptions/search snippets; for the latter, NO means "not claimed by anything seen", not "proven absent".

## 5. Priority-cell coverage ("where to look")
""" + "\n".join(f"- **{r['cell_id']} {r['priority_cell']} x {r['process']}** -> {r['mechanism_or_target']}: {r['discovery_status']}; local EVD rows for the matrix {r['existing_local_EVD_rows_for_matrix']}; Europe PMC hits (mechanism, all/OA/title-abstract-OA) {r['europepmc_hits_with_mechanism_all']} / {r['europepmc_hits_with_mechanism_OA']} / {r['europepmc_hits_titleabs_OA']}." for r in pc) + f"""
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
- Priority zero-row mechanisms have discovery routes or SOURCE_GAP: yes (priority-cell table; {len(srcgap)} SOURCE_GAP rows, all with a literature route).
- First waves ranked; H2 actions isolated: yes (Section 7; H2 queue).
- No new data acquired; no scientific values invented: yes (only metadata hit counts were requested from the Europe PMC search API; nothing stored but counts).
- Items marked BLOCKED_LICENSE / BLOCKED_ACCESS / UNKNOWN_CAPABILITY: IFCT; FoodAtlas; FlavorDB; RecipeDB API; paywalled indexes; ASHRAE/handbooks; KEGG; PMC bulk route (post Aug-2026); INFOODS and CoFID/AFCD licences; EFSA acrylamide data; ComBase.

## 10. Non-blocking documentation backlog
`reports/ner/ner_program_closeout.md` is recorded in `docs/BACKLOG_NONBLOCKING.md`; it did not interrupt ES-1.2.

## 11. Next step (not started)
STEP 10 / ES-1.3 -- 20-row mechanism evidence extraction + human-verification pilot. Required first: your review of this census and H2 decisions #1, #3, #4 (Europe PMC full-text capture, NCBI registration, Unpaywall terms) and the choice of the pilot mechanism. The counts favour potato frying/acrylamide (Q05: 910 OA full-text hits with mechanism, 89 title-abstract OA) over garlic alliinase (Q01: 404 / 24) and onion LFS (Q03: 34 / 2) for a 20-row pilot; garlic remains the higher-priority zero-row cell, so this is a decision for you.
"""
(ROOT / "reports/h_state/es_1_2_source_census.md").write_text(txt)
print(len(txt))
