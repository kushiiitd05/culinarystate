# SOURCE_ACCESS — every data source, how we got it, what we may store

Checked 2026-10-18. All facts are snapshot claims (AH15): re-verify before relying on them.

| Source | Access | Status | Licence / terms | Storage rule | Ledger | Command |
|---|---|---|---|---|---|---|
| USDA Retention Factors R6 (2007) | direct file `retn06.txt` + PDF | ✅ 7,018 rows | US federal work (public domain, assumed) | commit OK | SRC/SNAP/EVD/COND/SVAR | `tools/ingest_usda_r6.py` |
| Phenol-Explorer 3.6 retention factors | polite crawl (not in bulk downloads) — D-005 | ✅ crawl → EVD | free; commercial use needs permission; cite PE + papers | derived only (raw HTML local) | EVD/STUDY/SRC per paper | `tools/crawl_phenol_explorer.py` then `tools/ingest_phenol_explorer.py` |
| FoodData Central SR Legacy 2018-04 | bulk CSV zip | ✅ downloaded | CC0 | commit derived | crosswalk + portion candidates | `tools/build_fdc_crosswalk.py` |
| FDC API | `DEMO_KEY` (30 req/h) | ⚠️ too slow for bulk | CC0 | — | — | get a free key at api.data.gov if needed |
| PubChem PUG-REST | open API (≤5 req/s) | ✅ | NCBI public data | commit | MOL | `tools/build_molecule_registry.py` |
| OpenAlex | open API (polite pool, mailto) | ✅ | CC0 metadata | commit metadata | verification queue | `tools/build_verification_queue.py` |
| FSSAI Labelling & Display Regs 2020 (compendium 23-09-2021) | official PDF | ✅ | Govt of India publication | commit | SRC/SNAP/ALLERGEN | `tools/build_allergen_registry.py` |
| A1 BBC Good Food corpus (11,934 recipes) | scraped in A1 | ✅ local | third-party copyright | **local only**; derived stats committed (D-003) | REC/ING/ALIAS/PROC/TOOL | registry builders |
| TASTEset | local copy in A1 | ✅ local | check licence before redistribution | local | NER baseline (pending) | — |
| FoodOn OWL | GitHub raw | reachable, not yet ingested | CC BY 4.0 | commit derived | ING crosswalk (planned) | — |
| RecipeDB / RecipeDB3 / API | needs key from Prof. Bagler | ❌ blocked | unknown | — | — | see `API_BLOCKERS.md` |
| FlavorDB / FlavorDB2 bulk | web only | ❌ not acquired | unknown | — | IMAP (planned) | ask CoSyLab (H1 email) |
| USDA FSIS / FoodSafety.gov temperature charts | CDN blocks automated clients (403) | ❌ manual | US federal | commit | WARN (food safety) | human downloads page/PDF → `data/raw/fsis/` |

Network note: the home router's DNS returns SERVFAIL for `*.usda.gov`; scripts pin the IP resolved by public DNS
(`curl --resolve host:443:IP`). That works around a local DNS fault, not a site block. Where a site actively refuses
(403), we stop and download manually.

Books: only public-domain (e.g. Project Gutenberg cookbooks), open-licence textbooks, and government guides may be
downloaded and ingested. Copyrighted books may be read by humans for reference, never ingested or redistributed.
