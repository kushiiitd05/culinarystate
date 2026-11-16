# S176 lane L-PH: FDA/CFSAN "Approximate pH of Foods and Food Products" registry draft

Status: DRAFT / AI_DRAFTED. No ledger was edited. Everything below is a proposal for the humans (ksh/prv under D-071, or Kush/Parv).
Built 2026-11-08 in worktree `~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`, base `07fc0d2`, uncommitted).

## 1. Source of record (official copy found)

| Field | Value |
|---|---|
| Title (as printed) | "US FDA/CFSAN - Approximate pH of Foods and Food products" (page `<title>`: "US FDA/CFSAN - Approximate pH of Foods and Food Products") |
| Publisher | US FDA, Center for Food Safety and Applied Nutrition (CFSAN), LACF programme (Acidified and Low-Acid Canned Foods) |
| Original URL | `http://www.cfsan.fda.gov/~comm/lacf-phs.html` |
| Copy used (web.archive.org capture of the fda.gov page, raw `id_` bytes) | `https://web.archive.org/web/20080223184205id_/http://www.cfsan.fda.gov/~comm/lacf-phs.html` (memento-datetime Sat 23 Feb 2008 18:42:05 GMT) |
| Revision date | Printed date line "April 2007"; footer "Hypertext updated ... April 25, 2007"; `<meta name="updated" content="04-25-2007">`; origin `Last-Modified: Wed, 25 Apr 2007 14:15:47 GMT` |
| Retrieval date | 2026-11-08 (response `Date: Sun, 08 Nov 2026 12:54:19 GMT`) |
| Local raw file | `data/raw/fda_ph/wayback_20080223_lacf-phs.html` (34,646 bytes), sha256 `f5b8faad71a83ff5b98ef1e7073e6405ac34730557903a89a70a8c058083d59f` |
| Response headers | `data/raw/fda_ph/wayback_20080223_headers.txt`, sha256 `5d94dd139c21d5aea54ee447df443af44689d5045a7e1667a5a88c402b1f3869` |

Additional official-page captures kept in `data/raw/fda_ph/` for cross-checking (same original URL, web.archive.org `id_`):

| Capture | Page date label | Origin Last-Modified | sha256 (html) | Result vs the April 2007 copy |
|---|---|---|---|---|
| 20080917123409 | April 2007 | updated 02-22-2008 (meta) | `bf26ae1fdfae5429fede4b24336393fcaece40787f157b73d03962cec42c7141` | 488 rows, 0 text differences, 0 indent differences |
| 20050406034124 | October 2003 | Thu 24 Mar 2005 | `7f74c886710038383b197d1bdf6340cd82b63850f31bf2d9afc7d8fde89770fe` | 488 rows, 0 text differences, 0 indent differences |
| 20040206082642 | October 2003 | Fri 23 Jan 2004 | `67065339301a44cae64e4d4126ac798dfdc540db5f08f2ae38e5e4b442d3b809` | 488 rows, 1 difference: row 446 Tamarind printed `6.00 -` (the later copies print `3.00 -`) |

Notes on the search for the official copy:
- `fda.gov/media/...` and the modern fda.gov page URLs I tried returned an FDA abuse-detection page to curl; not used.
- The `webharvest.gov` capture named in the review packet (`peth04/20041014211751/...lacf-phs.html`, "Oct 2003") returned an archive-it JavaScript proof-of-work challenge ("Session Verification"). I did not solve it. Instead the Wayback captures of the same fda.gov page were used. The table is identical across the Oct 2003 (Mar 2005 capture) and April 2007 revisions except the Tamarind correction above, so the packet's "Oct 2003 webharvest" description and this April 2007 source describe the same 488-row table.
- Third-party re-host (NOT a source of record, noted only): `https://riverstonehealth.org/wp-content/uploads/FDA-Approximate-pH-of-Foods.pdf` (13-page browser print of the same page, "April 2007"). Used only as a consistency check: all 488 (item, pH) pairs printed on the official capture also appear verbatim in its text, including the `5.2l` typo, which shows the typo is in the FDA source and not a capture artefact. Other mirrors seen in search results (pickyourown.org, Clemson, etc.) were not used.
- Raw location caveat: `data/` in the worktree is a symlink to the main checkout's `data/`. The download therefore physically sits in `~/kush_work/culinarystate/data/raw/fda_ph/` (a new directory; no existing file touched). It is git-ignored (main repo `.git/info/exclude` has `/data`, and `.gitignore` has `data/raw/`; `git check-ignore -v data/raw/fda_ph/test.html` run in the main repo reports the match; in the worktree git refuses with "beyond a symbolic link").

## 2. What was built

| File | Description | sha256 |
|---|---|---|
| `registry/food_ph_fda_draft_v1.csv` | 488 rows, one per printed table row | `6c591cfdd0dd5dc2ee1300eea0a50582d173f8c39c0345dd62660d6f51ebc0d8` |
| `registry/food_ph_fda_ing_crosswalk_draft_v1.csv` | 1,718 rows (up to 5 candidates per ph_id, plus one NONE row where no candidate) | `bb39c2c29701ab9ecb5b2318f1d54c822f4899183b8cd86467c1bf6fa01b03fc` |
| `tools/build_food_ph_fda_draft.py` | Deterministic builder (stdlib only; checks the raw sha256 before parsing) | `cdf8479a25da7d197b3d5d0eb2fecc6c310f985eaff4035313ec038a503ab312` |
| `tests/test_food_ph_fda_draft.py` | 7 invariants over the two CSVs and the raw capture | n/a |
| `reports/orchestration/S176_L-PH_report.md` | this report | n/a |

Registry columns: the 12 requested (`ph_id, item_raw, item_norm, ph_low, ph_high, ph_value_type, page, source_id, source_url, retrieved_at, parse_status, notes`) in the requested order, then extras: `ph_raw` (the pH cell exactly as printed), `row_index`, `indent_level` (1 = printed indented under a parent row), `parent_item_raw`, `item_context_norm` (parent head word + child, e.g. "cabbage, savoy"; used for matching).
- `item_raw` and `ph_raw` are the printed strings with HTML tags removed and entities decoded; internal and trailing whitespace is kept (so `'Anchovies '` and `' Canned'` keep their spaces). The 8 empty cells hold a non-breaking space in `ph_raw`.
- `item_norm`: lower case, whitespace collapsed, spacing around commas fixed, trailing `+`/`?` markers and trailing `. , :` removed. No spelling is corrected.
- `page` = 1 for every row (the source is a single HTML page; `row_index` gives the position).
- `source_id` = `SRC-PROPOSED-FDA-CFSAN-PH-2007` (a proposal string, not a ledger id). `source_url` = the web.archive.org URL above. `retrieved_at` = `2026-11-08T12:54:19Z`.
- Vocabulary note: `ph_value_type` uses RANGE / POINT as requested, plus `NONE` for the 8 rows with no pH printed (there is no QUALITATIVE text anywhere in this source, so that value is unused). A printed `5.00 -` is kept as `RANGE` with `ph_low=5.00`, `ph_high` empty and `parse_status=PARSED_OPEN_ENDED`; it is not a POINT and no upper bound is invented. Consumers must treat an empty `ph_high` on a RANGE as "unknown upper bound".

## 3. Counts

| Quantity | Count |
|---|---|
| Printed table rows (independent markup count: 489 `<tr>` minus 1 header row) | 488 |
| Rows in registry | 488 (ids FDAPH-0001 .. FDAPH-0488) |
| POINT (single printed value, low = high) | 115 |
| RANGE, both bounds printed | 347 (includes 1 with whitespace repair, 1 printed `5.10 - 5.10`) |
| RANGE, open-ended (`x.xx -`, lower bound only) | 17 |
| Partially parsed: `Cheese, Snippy`, printed `5.18 - 5.2l` (low 5.18 kept, high empty, UNPARSED_REVIEW) | 1 |
| No pH printed: group headers (Apples, Bran, Junket type Dessert:, Rice (all cooked), Soup) | 5 |
| No pH printed, no children (Dungeness Crab Meat, Gherkin, Salsa) | 3 |
| Rows with at least one printed numeric pH value | 480 (479 fully parsed + the Snippy row) |
| Rows I could not fully parse | 1 (Snippy). No row is entirely dropped. |
| QUALITATIVE | 0 |

Completeness checks run (all passed):
1. HTMLParser row count (488) equals the regex markup count (489 `<tr>` open and close tags, 1 header row).
2. A second, regex-only extraction of every `<tr>` compared with the CSV: 488 of 488 `(item_raw, ph_raw)` pairs identical, in order.
3. Numeric tokens printed in the pH cells = 828; bounds in the CSV account for 827 of them; the one remaining token is the `2` of `5.2l`, deliberately not used.
4. All 488 pairs also found in the independent third-party PDF print (consistency only).
5. Rebuild is deterministic (two runs, identical sha256 for both CSVs).
6. The document prints no item count of its own; the review packet's estimate ("about 488 items") matches.
7. `pytest -q tests/test_food_ph_fda_draft.py`: 7 passed.

Source quirks recorded in `notes` (printed text always kept):
- 17 open-ended pH values (`5.00 -` etc., one printed without spaces as `6.00-`), all handled as above.
- `5.2l` (letter ell) in Cheese, Snippy: NOT repaired; the candidate `5.21` is in the notes for a human to confirm.
- `4. 10` in Guava, canned: whitespace inside the number removed deterministically, status `PARSED_REPAIRED_WS` (high = 4.10).
- `4.50 -5.00`, `6.00 -7.50`, `7.5` parse normally.
- Trailing `+` (Bamboo Shoots) and `?` (Mangostine) markers with no printed explanation; `Loquat (May be acidified to pH 3.8)` carries a pH figure that is not the item's pH (5.10).
- 17 rows with probable name typos flagged in `notes` (16 as "possible source typo ... (AI-suggested ...)" covering 15 distinct words, 1 as a digit inside a word), for example Arrowroot Cruel, Eell, Escarolle, Enchalada, Edem, Calamyrna, fi1et, Kubbard, Suop/Saoup, Minestronen, Wheatnena, Yangsberries. The printed name is kept; the suggestions are unverified.
- Layout anomalies: "Prunes, dried, stewed" is indented under Potatoes and "Herring, Pickled" under Kippered Herring; parent context is not applied to these two (noted). Children of the "Soup" group are complete product names, so no prefix is added.
- Internal duplicates with different values exist in the source and are left as printed (for example Hearts of Palm 5.70 versus Palm, heart of 6.70; Tofu 7.20 printed twice under two names).
- Tamarind: `3.00 -` in this copy; an earlier capture printed `6.00 -` (see section 1).
- Printed values are the FDA's approximate pH of the edible portion "in their normal and natural state, unless otherwise designated"; the FDA text adds that considerable variation exists between varieties, growing conditions and processing. These are literature-compiled approximate ranges (references: Food Engineering 1962; Bridges and Mattice 1939; FDA BAM 8th ed. ch. 21 table 11; Grahn 1984), not measurements made for this project.

## 4. Crosswalk to ING (AI_DRAFTED, lexical only)

Method (deterministic, no model, no network): candidate names are the canonical names of the latest version of every ACTIVE ING (2,048 ids; `ING.jsonl` is append-only, 5,387 lines) plus the `normalized` form of every ACTIVE ALIAS that points to an ACTIVE ING (4,103 aliases); pool = 6,151 names. Words are lower-cased, singularised by simple rules, stop words dropped. Processing-state words (cooked, canned, frozen, dried, etc.) are set aside to form a "core". Relation and score:

| Basis | Score | Band | Meaning |
|---|---|---|---|
| FULL | 1.00 | EXACT | same word set as the item (order ignored, e.g. "Cheese, Cheddar" = "cheddar cheese") |
| CORE | 0.90 | HIGH | same word set once state words are dropped ("Peaches, canned" = peach) |
| CORE_ACID_PROCESS | 0.70 | MEDIUM | as CORE, but the dropped words include acidified/pickled/fermented/preserved: identity matches, pH of the processed form must not be applied to the base ING |
| GENERALISATION | 0.70 or 0.45 | MEDIUM or LOW | candidate is a broader ingredient; MEDIUM only if the extra item words are colour or state modifiers (red, green, white, etc.) |
| SPECIALISATION | 0.40 | LOW | candidate is narrower than the item |
| OVERLAP | at most 0.39 | LOW | partial word overlap |

Candidates below 0.30, or sharing only generic words (soup, sauce, juice, cream, milk, filet, shell, etc.), are dropped. Up to 5 candidates per `ph_id`, ranked by score, canonical-name before alias, corpus frequency, id. Extra crosswalk columns: `form_qualifiers`, `ph_applies_to` (ITEM_AS_PRINTED / PROCESSED_FORM / ACID_PROCESSED_FORM) so that a cooked, canned, juiced or pickled item's pH is never silently attached to the raw ING; all rows `status = AI_DRAFTED`.

Coverage (best candidate per `ph_id`, over the 480 rows that have a printed numeric pH):

| Best band | Rows |
|---|---|
| EXACT | 143 |
| HIGH | 96 |
| MEDIUM | 23 |
| LOW | 158 |
| NONE (no candidate) | 60 |

- Rows with at least one candidate: 420 of 480 (87.5%). Rows with an EXACT or HIGH candidate: 239 of 480 (49.8%). Distinct ING ids at rank 1: 229.
- Over all 488 rows (including the 8 without a pH): EXACT 147, HIGH 96, MEDIUM 23, LOW 160, NONE 62.
- Known limitations (all lexical): parentheticals are ignored, so `Soy bean curd (tofu)` and `Calamary (Squid)` miss their alternative names; the word "cream"/"milk" is generic, so `Cream, 20 per cent` finds no candidate; British canonical names are matched via ING/ALIAS only (aubergine, courgette work through aliases); source typos are not corrected (Eell, Escarolle, Wheatnena find nothing); "greens" is singularised to "green" and can look like a colour modifier (`Turnip, greens, cooked` to `turnip` is a MEDIUM false friend). Items absent from ING (abalone, breadfruit, mangostine, jujube, persimmons, etc.) correctly show NONE. The crosswalk is a candidate list for human review; it must not be used to attach pH to ING ids without review.

## 5. Licence statement

The source is a document written by US FDA staff in the course of official duties, so it is a US government work. Under 17 U.S.C. section 105, copyright protection is not available for a work of the US Government in the United States. In addition, the FDA website policy page (fetched 2026-11-08 from `https://www.fda.gov/about-fda/about-website/website-policies`, read through the WebFetch summariser, so the quoted wording is second-hand) states that, unless otherwise noted, the contents of the FDA website, text and graphics, are not copyrighted, are in the public domain, and may be republished, reprinted and otherwise used freely without permission; credit to FDA is appreciated but not required. This is the same basis already used in SRC-000001 (USDA, "US federal government work (public domain, 17 U.S.C. section 105)", `licence_status ASSUMED`). Caveats: (a) the licence text is not printed on the archived page itself; (b) the table compiles values originally published by others (Food Engineering 1962, Bridges and Mattice 1939, FDA BAM, Grahn 1984); individual numerical facts are not copyrightable, but the humans may wish to note it; (c) the web.archive.org copy is a hosting mirror of the FDA page, not a separate rights holder. Proposed `licence_status`: ASSUMED (same as SRC-000001); a human can promote it to VERIFIED after reading the FDA policy page directly.

## 6. Proposed SRC row (text only, for the humans; the ledger was not touched)

The next free id in `SRC.jsonl` is `SRC-000489` (highest present: SRC-000488), but other S176 lanes may propose ids too, so the human who appends it should assign the id at append time.

```json
{"created_at": "<append time>", "created_by": "<human or persona that approves>", "id": "SRC-000489 (PROPOSED)",
 "kind": "DATABASE", "primary_or_secondary": "SECONDARY",
 "title": "US FDA/CFSAN, Approximate pH of Foods and Food Products (LACF), April 2007 revision, 488-row table",
 "publisher": "US FDA Center for Food Safety and Applied Nutrition",
 "url": "http://www.cfsan.fda.gov/~comm/lacf-phs.html",
 "year": 2007,
 "licence": "US federal government work (public domain, 17 U.S.C. section 105); FDA website policy: contents not copyrighted unless otherwise noted",
 "licence_status": "ASSUMED", "storage_rule": "COMMIT_OK", "source_family_id": "FDA-CFSAN-PH",
 "robots_terms_notes": "Retrieved 2026-11-08 from web.archive.org capture 20080223184205 (raw html sha256 f5b8faad71a83ff5b98ef1e7073e6405ac34730557903a89a70a8c058083d59f); fda.gov/media URLs blocked curl; webharvest.gov capture needs a JS challenge",
 "notes": "Compiled approximate pH ranges from literature (Food Engineering 1962; Bridges and Mattice 1939; FDA BAM 8th ed. ch. 21; Grahn 1984). Not measurements by this project. 17 open-ended values, 1 typo (5.2l), 8 rows without pH. Registry: registry/food_ph_fda_draft_v1.csv.",
 "provenance": {"method": "MANUAL", "source_ids": []}, "record_type": "SRC", "schema_version": "1.0.0",
 "status": "ACTIVE", "verification": {"status": "UNVERIFIED"}, "version": 1}
```

`storage_rule COMMIT_OK` is proposed because the registry holds only US-government table values; the raw HTML stays in git-ignored `data/raw/`.

## 7. H2 note (new source acquisition)

This is a new source acquisition: the FDA pH table is not in `SRC.jsonl` and no SRC row, ledger edit or claim may use it until a decision is recorded. Under D-071 a ksh (Kush) verdict, or a prv verdict, or direct human approval is needed before any value from this registry is used in a claim, an evidence row, or the router. Until then every row is DRAFT. Use limits the humans should keep in mind: the table gives approximate ranges for foods "in their normal and natural state, unless otherwise designated", it is not a mixture or recipe pH (no buffering model; the review packet already says no mixture pH number), and it is a literature compilation, so any use must be Layer 2 SCENARIO (`ASSUMED_DEFAULT`/`NON_CITABLE`) or a lookup with its range intact, never a point estimate. Open-ended rows (17) give only a lower bound and must be treated as UNKNOWN upper bound.

## 8. Runs (rows matching the header of `registry/compute_runs_v1.csv`)

```
RUN-S176-LPH-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FDA_PH,1,"curl -sS -L -A Mozilla/5.0 https://web.archive.org/web/20080223184205id_/http://www.cfsan.fda.gov/~comm/lacf-phs.html",data/raw/fda_ph/wayback_20080223_lacf-phs.html,f5b8faad71a83ff5b98ef1e7073e6405ac34730557903a89a70a8c058083d59f,2026-11-08T12:54:19Z,2026-11-08T12:54:20Z,DONE,"official FDA page capture; 3 further captures kept for cross-check; raw dir is a symlink target in main data/"
RUN-S176-LPH-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FDA_PH,1,"nice -n 10 python -I tools/build_food_ph_fda_draft.py",registry/food_ph_fda_draft_v1.csv,6c591cfdd0dd5dc2ee1300eea0a50582d173f8c39c0345dd62660d6f51ebc0d8,2026-11-08T13:03:06Z,2026-11-08T13:03:06Z,DONE,"488 rows; deterministic (rebuilt twice, identical sha256)"
RUN-S176-LPH-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),07fc0d2+uncommitted,FDA_PH,1,"nice -n 10 python -I tools/build_food_ph_fda_draft.py",registry/food_ph_fda_ing_crosswalk_draft_v1.csv,bb39c2c29701ab9ecb5b2318f1d54c822f4899183b8cd86467c1bf6fa01b03fc,2026-11-08T13:03:06Z,2026-11-08T13:03:06Z,DONE,"1718 crosswalk rows; AI_DRAFTED; same invocation as RUN-S176-LPH-002"
```

Tests: `/home/manjot23309/kush_work/culinarystate/.venv312/bin/python -m pytest -q tests/test_food_ph_fda_draft.py` gave 7 passed. Ledger check: `git status --short ledgers` is empty (no ledger touched); new untracked files are only the two registry CSVs, the tool, the test and this report. Load was low (about 5) during the runs; each ran in under one second; no GPU.

## 9. Open questions and decisions for the humans

1. Approve or reject acquiring this source (H2 / D-071), and decide the SRC id, `licence_status` (ASSUMED proposed) and `storage_rule`.
2. Confirm `5.2l` in Cheese, Snippy: is it 5.21? Until then the row stays UNPARSED_REVIEW with `ph_high` empty.
3. Policy for the 17 open-ended rows: keep as lower-bound-only (current) or exclude from any numeric use.
4. Is `NONE` (no pH printed) an acceptable extra `ph_value_type` value? The brief listed RANGE/POINT/QUALITATIVE only.
5. The review packet and D-records describe the source as "Oct 2003, webharvest.gov"; the copy actually used is the April 2007 revision via web.archive.org (table text identical except Tamarind). If the Oct 2003 webharvest capture is required for citation, a human with a browser would need to pass its challenge.
6. Crosswalk review: 239 EXACT/HIGH candidates still need a human glance before anything is linked; 60 items have no ING candidate (the humans may want new ING ids for abalone, jujube, persimmon, breadfruit and similar).
7. Layer rule: any later use of these values belongs in Layer 2 SCENARIO (labelled, ranged), not Layer 1 TEXT_STATED.
