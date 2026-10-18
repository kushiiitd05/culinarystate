# DATASETS — every source, its licence, what we keep, where it lands

Counts as of S041 (2026-10-18). Ledger counts: `py -c` snippet in RUNBOOK §0 or reports/*.md.

| Source family | What | Licence / terms | Stored in git | Local raw | Feeds |
|---|---|---|---|---|---|
| BBCGF-A1 | 11,934 BBC Good Food recipes (A1 scrape) | third-party copyright | derived only (REC hashes, links) | ../a1/A1 3/data | REC, ING, ALIAS, PROC, TOOL, KGE |
| WIKIBOOKS-COOKBOOK | 3,676 recipes + 130 equipment + 749 ingredient + 81 technique pages | CC BY-SA 4.0 (attribute URL + revid) | derived only (IDs, counts) | data/raw/wikibooks, data/interim/wikibooks | REC, ING (+97), ALIAS, TOOL refs, PROC refs, silver NER |
| GUTENBERG-PD | public-domain English cookbooks (347 selected) | public domain (US) | derived; text local for consistency | data/raw/gutenberg | REC (family 3), tool-word candidates |
| USDA-RETN-R6 | 7,018 nutrient retention factors | US government work | values | data/raw/usda_r6 | EVD (E3) |
| PHENOL-EXPLORER-3.6 | 3,870 polyphenol retention factors / 125 papers | database terms (cite); polite crawl (D-005) | values + citations | data/raw/phenol_explorer | EVD (E3), STUDY, SRC per paper |
| BOGNAR-2002 | 6,594 retention factors (28/39 Part-2 tables) | institutional report, open access (KIT) | values only | data/raw/bognar | EVD (E3) |
| OFF-TAXONOMY | 5,719 ingredient taxonomy entries (pinned git a1ce1d36) | ODbL 1.0 | refs + aliases (attribution) | data/raw/off | ALIAS (+1,770 incl. 13 Indian languages), ING refs |
| FOODON | 28,684 food ontology terms | CC BY 4.0 | IDs + categories | data/raw/foodon | ING crosswalk + category |
| WIKIDATA | QIDs for ingredients (via OFF) and tools | CC0 | QIDs | data/raw/wikidata | ING/TOOL refs |
| PUBCHEM | 131 molecules | public domain (NCBI) | IDs, InChIKeys, fingerprints | data/raw/pubchem | MOL, IMAP |
| FSSAI-LD-2020 | allergen list (Reg. 5(14)) | Indian government regulation | verbatim list | data/raw/fssai | ALLERGEN |
| UNITSRC-* | NIST HB44, UK WMA 1985, 21 CFR 101.9, SI brochure + conventions | public standards | unit definitions | — | UNIT |
| OpenAlex / Crossref | paper metadata for verification queue + DOI resolution | CC0 metadata | DOIs, titles | data/raw/openalex, data/raw/doi_resolve | queue, SRC.doi |

## Not used (and why)
- RecipeDB / FlavorDB: API access pending (Prof. Bagler) — crosswalks stay `UNRESOLVED_EXTERNAL` (AH2).
- RecipeNLG, Kaggle Food.com: require accepting terms with a personal login — human gate.
- FSIS / FoodSafety.gov: refused scripted downloads (403) — manual browser save (MANUAL_NEXT_STEPS).

## Licence rules
- Third-party recipe text never enters git (D-003); only hashes, IDs, counts.
- CC BY-SA / ODbL / CC BY: keep attribution (URL + revision / commit) in SRC/SNAP or record refs.
- Values from papers/databases are cited facts with locators; we do not redistribute full texts.
