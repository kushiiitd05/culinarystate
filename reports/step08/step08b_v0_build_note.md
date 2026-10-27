# Step 08b-v0 build note (library packaging; authority D-035; written 2026-10-27)

Status: 08b-v0 library built and unit-tested on fixtures and tmp dirs only. It is NOT 08b v1 (THR-08B-05 unsigned, D-035 answer 1), NOT an 08a PASS (G08-3 is FAIL, D-034), and makes NO detector precision or recall claim. The real ledgers were not read or run.

## Files (all new)
- `src/culinarystate/lineage/library.py` (module docstring carries the rule_version recipe and the properties)
- `tests/unit/test_lineage_library.py` (20 tests)
- this note

## API
| Function | Does | Wraps (unchanged) |
|---|---|---|
| `register_document(src_id, source, out_dir)` | streams bytes / Path / binary file in 1 MiB chunks, sha256, key `<src_id>\|sha256:<hex>` (D-029 D-11), mints a scratch `DOC-######` in `out_dir/_ids.jsonl`, appends one record to `out_dir/DOC_library.jsonl`; same bytes again returns the stored record, writes nothing | key format of `docs.doc_mint_key` (parity tested), `guard.assert_safe_write_target` |
| `propose_edges(items)` | B0, B1, B2, B3, STRONG edges, B3 cut 0.75 | `detectors.detect_edges` |
| `assign_keys(rows, studies, docs, srcs, edges, **kw)` | study / lineage_root / split_group / independence keys, `SCRATCH_PROVISIONAL` | `keys.assign_keys` |
| `check_disjointness(records, expected_rows=, studies=, docs=, drv_parents=None)` | coverage, nesting, DRV-parent checks as data | `keys.check_gates`, `keys.check_drv_gate` |
| `write_jsonl(records, path, out_dir)` | sorted-key JSONL, atomic replace, path must be inside `out_dir` | `guard.assert_safe_write_target` |

Every returned dict and every record in it carries `rule_version`. The 08a versions are preserved as `detector_rule_version` (edges) and `keys_rule_version` (key records). Inputs are never mutated; outputs are new dicts.

## rule_version recipe
`rule_version = "lib-v0-" + sha256("\n".join(f"{name}={value!r}" for name in sorted(constants)).hexdigest()` (full 64 hex digits). `constants` = `library.rule_constants()`: detectors B3_CUT, B1_SF, B2_SF, _ROUND_SFS, LEVEL_ORDER, RULE_VERSION; keys RULE_VERSION, SAME_LAB_WINDOW_YEARS and the sorted MERGING_TYPES, GROUPING_DEFAULT_TYPES, HUB_SRC_KINDS, HUB_REPORT_KINDS; `library.LIBRARY_VERSION`. A test recomputes it independently and checks it changes when a constant changes.

## Measured memory (tracemalloc peak, this Mac, scratch data; inputs built before tracing, so input lists are excluded)
- `register_document`: peak 2.0 MiB for a 1 MiB document, 3.0 MiB for 64 MiB and for 512 MiB (flat; one 1 MiB chunk plus hasher).
- `propose_edges` on synthetic items: 2.8 MiB at 2,000 items, 13.6 MiB at 10,000, 55.2 MiB at 40,000 (about 1.4 KB per item, linear). It is not streaming: `detect_edges` sorts and indexes all items, and B3 compares all pairs inside a block, so the worst case is quadratic in the largest block. No bound number is claimed beyond these measurements; the plan gives none.
- `assign_keys`: not separately measured (it holds rows, edges and union-find maps in memory).

## Reused unchanged
`detectors.py` (detect_edges, B3_CUT 0.75), `keys.py` (assign_keys, check_gates, check_drv_gate), `guard.py` (assert_safe_write_target), `seeding.py` (generate_seeded_pairs, in the fixture test). No existing file was edited.

## Seeded fixture (G08b-3 as unit test only)
`generate_seeded_pairs(20261027, 60)`: 420 pairs, seven THR-08A-17 classes, each pair run through `propose_edges` at the frozen cut 0.75; the test asserts one edge per pair. This tests the code path on synthetic scratch data. It is not detector recall on real data.

## Open / flagged
1. `lineage/docs.py` imports `requests` (via `evidence.doi_resolve`) and `ledgers/store.py` imports jsonschema (which loads urllib/socket). To keep the library offline without editing them, `library.py` imports neither and reproduces the DOC key format and a 15-line id minter (same `_ids.jsonl` row shape). Key parity with `docs.doc_mint_key` is tested. Decision for Kush: keep as is, or later split the pure parts out of `docs.py`.
2. Hash algorithm / length for `rule_version` (sha256, 64 hex, prefix `lib-v0-`) and the DOC record fields are my choice; the plan says NOT GIVEN. Library DOC ids are scratch ids per output directory, not ledger DOC ids.
3. `check_disjointness` keeps the 08a check names (G08-1, G08-2, G08-8, G08-10) as labels only; they are library checks, not gate verdicts.
4. Not done (not authorised): v1 release, consumer wiring for Steps 10-14, ledger writes, `register_document` on the real `data/raw`.
