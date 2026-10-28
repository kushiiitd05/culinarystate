# 35e typed similarity registry: build note (pre-signature, synthetic-fixture only)

Code: `src/culinarystate/representation/similarity_registry.py`. Tests: `tests/unit/test_representation_similarity_registry.py` (20, synthetic rows only). Draft basis: 35.0 v1 draft sections 8.1, 8.2, 8.2b, 8.4 and Appendix B (UNSIGNED). Permitted by section 1.3 / THR-35P-02 (specs and unit tests on synthetic fixtures). No real registry, ledger or recipe file was opened; `registry/ssot15_similarity_registry.csv` was read for its header only and not edited; no similarity was computed.

## API (pure functions, in-memory rows only)
- `SimRow.from_mapping(m)`: the 8.1 schema. Twelve core fields must be present and non-blank (`UNKNOWN` is allowed, blank is not); `notion` is one of the nine `NOTIONS` (8.2, exact names); `status` is one of the six `STATUSES` (8.1). Optional: `coverage_fields`, `fp_definition_ref`, `ssot_sim_ref`, `rung`, `decision_ref`. Unknown columns are refused.
- `lint_registry(rows)`: duplicate `sim_id`; a formula that names another notion (8.4 "mixes notions"); fusion words in formula or aggregator (fusion is a task-conditioned reranker, SSOT 246.2); `PROMOTED` without a decision reference (8.4); one evaluation target listed as own by two notions (8.2b); a split family used outside the 8.2b sharing table, or shared by two notions without being listed; Open Babel ECFP labelled SIM-06 (D35-3). Returns every problem; fixes nothing.
- `lint_columns(columns, exempt=())`: a column named like `sim` / `similarity` / `score` must carry exactly one notion; two or more = a fused scalar (8.3). Nothing is exempt by default.
- `assert_lint_clean(rows, columns)` raises `RegistryError` listing every problem. `parse_registry_csv(text)` / `to_csv(rows)` (the caller reads and writes files). `notion_coverage(rows)` and `unlisted_notions(rows)` are descriptive only (no pass/fail).

## Chosen here, flagged for sign-off (not defined in the draft)
1. `OUTSIDE_NINE` is the notion value for SIM-13 (reaction-center similarity) and is allowed only with status `RESEARCH_ONLY` (D35-11).
2. `;` separates several values in `eval_set` and `split_family`; `assoc:<target>` marks a cross-notion association test (8.2b), never a notion's own target; `none` and `UNKNOWN` count as no target / no family.
3. `decision_ref` is an added optional field, so the 8.4 rule "PROMOTED needs a decision-record reference" has somewhere to look; `UNKNOWN`, `none`, `TBD` or a `<placeholder>` do not count.
4. The audit's name `PROCESS-CONDITIONED` is refused with a pointer to `PROCESS-RESPONSE` (not silently mapped); notion and status names are case-exact.
5. The column lint follows 8.4 literally, so a metric column such as `f1_score` fails unless the caller lists it in `exempt`.
6. "Mixes notions" is detected from notion words in the formula text, which is conservative: a formula that merely mentions another notion's word fails and must be reworded.

## Not built, open for Kush (H4)
- No real registry rows and no `registry/similarity_registry_v2.csv`: the `sim_id` scheme is H4 (D35-12).
- Appendix B uses crosswalk states that are not v2 statuses (`WAITS (rdkit)`, `DATA-MISSING`, `DEFERRED`, `available`). Mapping them onto the six statuses is not decided; in particular 14-S / 14-C (learned, 35g) are `DEFERRED`, which has no v2 status.
- G35-SEP as a pass/fail gate: 8.3 says "every supported notion", but the draft does not say which statuses count as supported (for example whether HYPOTHESIS does). Only the descriptive `notion_coverage` is built.
- Level-specific split rules (for example `S-cui-*` at cuisine level only) are not enforced; the 8.2b check works per notion.
- BAN-35-1 (`THR-35P-38`) is not checked here: rows carry no inputs field, and FlavorGraph-derived profiles are allowed while FlavorGraph edges and embeddings are banned, so a text check would be unreliable.
- The 8.3 separation statistics (Spearman, kNN overlap) need real data and wait for the signature.
