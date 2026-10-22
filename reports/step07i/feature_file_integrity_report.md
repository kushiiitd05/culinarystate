# STEP 07I-R -- integrity of `ledgers/recipe_identity/recipe_identity_features_v1.parquet`

**Verdict: COMPLETE_REUSABLE** (read-only audit; the file was not modified; it is not "a pair table" -- it is the *per-recipe* identity-feature table written by `tools/step07i_features.py`, one row per indexed recipe).

| Check | Result |
|---|---|
| Footer / read integrity | readable by pyarrow 14 (writer: parquet-cpp-arrow 14.0.2), 1,226 row groups, zstd; all row groups decode |
| Bytes / SHA-256 | 308,538,405 B / `10c15cd1b4169ac10d96ab3a745bc7c4d309a848009df3ad11a4a4a871e254f9` (an identical copy was pushed to the A100 server; size matches) |
| Rows | **612,782** = the 07H-R recipe base row count (`recipe_base_v1.parquet`, 612,782) |
| Unique `recipe_id` | 612,782 (0 duplicates, 0 ids missing from the file, 0 extra ids, 0 null/empty/non-string ids) |
| Coverage by source | identical id set to the base, therefore A1 11,934 + Wikibooks 3,676 + Gutenberg 73,955 + Food.com 522,517 + TASTEset 700 |
| Sort order | **not** sorted by `recipe_id` (corpus-iteration order). No downstream step may assume sortedness. The new pipeline sorts explicitly. |
| Nulls | `rec_content_sha256` 523,217 (only REC-backed ids carry one -- expected), `cuisine` 552,638 (explicit cuisine is rare -- expected), `mh_steps` 885, `mh_ing` 2,439 (recipes with no usable steps/ingredient tokens -- a MinHash of nothing is `None`, never zero) |
| Empty strings | `title_norm` 734, `title_key` 750 (untitled records); 995 records have `n_chars < 60` and are excluded from *exact-hash* grouping by the pre-registered validity rule |
| Schema | `recipe_id, source_family, title_norm, title_key, norm_text_hash, raw_hash, rec_content_sha256, ing_ids, ing_toks, n_ing_lines, n_steps, proc_seq, tool_ids, mass_ing, mass_g, mh_steps (binary, 64 x uint32), mh_ing (binary, 32 x uint32), n_chars, cuisine, existing_family_id` -- unchanged from the 07I part-2 contract |
| Pair-level content | none (this file has no pair rows). The candidate manifest is rebuilt deterministically: 611,714 representatives -> **8,639,518 unique candidate pairs** (identical to the count printed by the stalled run) in 87 input partitions at `chunk_size=100,000` (= ceil(8,639,518 / 100,000)); every pair has `i < j`, none repeats across partitions, global order is sorted. 526,342 of 611,714 representatives (86.0 %) occur in at least one candidate pair. |

Reuse decision: the file is reused as-is as the single per-recipe input of the new pipeline (`reps_view` is derived from it and carries its SHA-256 in the run manifest `phases.audit`). Nothing needed to be rebuilt. The existing builder is single-pass and was not re-run.

Caveat that is a *finding*, not a defect: 1.1 % of records have a missing instruction MinHash or ingredient MinHash; they can only be retrieved through title blocks or REC family co-membership.
