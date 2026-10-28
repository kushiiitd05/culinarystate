"""Synthetic-fixture tests for the 35e typed similarity registry and lint (no real data)."""
import pytest

from culinarystate.representation import similarity_registry as sr


def row(sim_id="X-1", notion="CHEMICAL", **kw):
    base = {
        "sim_id": sim_id,
        "notion": notion,
        "level": "ingredient",
        "formula": "jaccard(A, B)",
        "aggregator": "none",
        "null_model": "curveball",
        "eval_set": "calibration-only",
        "split_family": "S-ing-clu",
        "valid_domain": "UNKNOWN",
        "evidence_class_required": "UNKNOWN",
        "licence_scope": "UNKNOWN",
        "status": "BASELINE",
    }
    base.update(kw)
    return sr.SimRow.from_mapping(base)


def test_nine_notions_and_six_statuses_pinned():
    assert sr.NOTIONS == (
        "STRUCTURAL", "CHEMICAL", "COMPOSITIONAL", "SENSORY", "FUNCTIONAL",
        "NUTRITIONAL", "CULTURAL", "PROCEDURAL", "PROCESS-RESPONSE",
    )
    assert set(sr.STATUSES) == {"BASELINE", "HYPOTHESIS", "PROMOTED", "RESEARCH_ONLY", "NEED_DATA", "UNSUPPORTED"}


def test_valid_row_and_unknown_is_a_valid_value():
    r = row()
    assert r.notion == "CHEMICAL" and r.valid_domain == "UNKNOWN"
    assert sr.lint_registry([r]) == []


def test_unknown_notion_and_alias_rejected():
    with pytest.raises(sr.RegistryError, match="notion"):
        row(notion="FLAVOUR")
    with pytest.raises(sr.RegistryError, match="PROCESS-RESPONSE"):
        row(notion="PROCESS-CONDITIONED")


def test_merged_notion_row_rejected():
    with pytest.raises(sr.RegistryError, match="notion"):
        row(notion="STRUCTURAL+CHEMICAL")


def test_bad_status_and_blank_core_field_rejected():
    with pytest.raises(sr.RegistryError, match="status"):
        row(status="DEFERRED")
    with pytest.raises(sr.RegistryError, match="level"):
        row(level="  ")
    with pytest.raises(sr.RegistryError, match="missing"):
        sr.SimRow.from_mapping({"sim_id": "X", "notion": "CHEMICAL"})


def test_outside_nine_only_as_research_only():
    assert row(notion=sr.OUTSIDE_NINE, status="RESEARCH_ONLY", split_family="none").notion == sr.OUTSIDE_NINE
    with pytest.raises(sr.RegistryError, match="RESEARCH_ONLY"):
        row(notion=sr.OUTSIDE_NINE, status="BASELINE")


def test_duplicate_ids_fail():
    problems = sr.lint_registry([row("A"), row("A", formula="ochiai(A, B)")])
    assert any("duplicate" in p for p in problems)


def test_formula_mixing_notions_fails():
    ok = row(formula="chemical presence jaccard")
    bad = row("B", formula="0.5 * chemical + 0.5 * cultural npmi")
    assert sr.lint_registry([ok]) == []
    assert any("mixes notions" in p for p in sr.lint_registry([bad]))


def test_fusion_is_never_a_registry_similarity():
    problems = sr.lint_registry([row(aggregator="fused reranker")])
    assert any("fusion" in p for p in problems)


def test_promoted_needs_decision_record():
    assert any("decision" in p for p in sr.lint_registry([row(status="PROMOTED")]))
    assert any("decision" in p for p in sr.lint_registry([row(status="PROMOTED", decision_ref="UNKNOWN")]))
    assert sr.lint_registry([row(status="PROMOTED", decision_ref="D-039")]) == []


def test_same_own_eval_target_for_two_notions_fails():
    cul = row("C", notion="CULTURAL", eval_set="TASK-ING-A", split_family="S-rec-grp", null_model="M0")
    chem_own = row("H", notion="CHEMICAL", eval_set="TASK-ING-A")
    chem_assoc = row("H", notion="CHEMICAL", eval_set="assoc:TASK-ING-A")
    assert any("TASK-ING-A" in p for p in sr.lint_registry([cul, chem_own]))
    assert sr.lint_registry([cul, chem_assoc]) == []


def test_same_target_within_one_notion_and_none_unknown_not_counted():
    a = row("A", eval_set="calibration-only")
    b = row("B", eval_set="calibration-only", formula="ochiai")
    n1 = row("N1", notion="FUNCTIONAL", eval_set="none", split_family="S-rec-grp", status="NEED_DATA")
    n2 = row("N2", notion="PROCEDURAL", eval_set="none", split_family="S-rec-grp", status="NEED_DATA")
    u1 = row("U1", notion="NUTRITIONAL", eval_set="UNKNOWN", status="NEED_DATA")
    assert sr.lint_registry([a, b, n1, n2, u1]) == []


def test_shared_split_families_follow_the_table():
    comp = row("C", notion="COMPOSITIONAL", split_family="S-rec-grp; S-rec-src", eval_set="masked-ingredient recovery")
    proc = row("P", notion="PROCEDURAL", split_family="S-rec-grp", eval_set="dish-family retrieval", status="NEED_DATA")
    chem = row("H", notion="CHEMICAL", split_family="S-rec-grp")
    assert sr.lint_registry([comp, proc]) == []
    assert any("S-rec-grp" in p for p in sr.lint_registry([comp, chem]))


def test_only_families_and_unlisted_families():
    cui = row("C", notion="CULTURAL", split_family="S-cui-src", eval_set="cross-cuisine transfer")
    comp_on_cui = row("M", notion="COMPOSITIONAL", split_family="S-cui-src", eval_set="masked-ingredient recovery")
    assert sr.lint_registry([cui]) == []
    assert any("S-cui-src" in p for p in sr.lint_registry([comp_on_cui]))
    one = row("A", notion="STRUCTURAL", level="molecule", split_family="S-new", eval_set="ST-1")
    two = row("B", notion="SENSORY", level="molecule", split_family="S-new", eval_set="SE-1")
    assert sr.lint_registry([one]) == []
    assert any("S-new" in p for p in sr.lint_registry([one, two]))


def test_open_babel_ecfp_never_labelled_sim06():
    ob = row("O", notion="STRUCTURAL", level="molecule", split_family="S-mol-cc", eval_set="ST-2",
             fp_definition_ref="Open Babel ECFP4", ssot_sim_ref="SIM-06")
    rd = row("R", notion="STRUCTURAL", level="molecule", split_family="S-mol-cc", eval_set="ST-2",
             fp_definition_ref="RDKit Morgan r=2 2048", ssot_sim_ref="SIM-06")
    assert any("SIM-06" in p for p in sr.lint_registry([ob]))
    assert sr.lint_registry([rd]) == []


def test_split_rows_of_frozen_sim14_pass():
    s = row("14-S", notion="STRUCTURAL", level="molecule", status="HYPOTHESIS", eval_set="none",
            split_family="S-mol-cc", ssot_sim_ref="SIM-14", formula="learned structural")
    c = row("14-C", notion="CHEMICAL", status="HYPOTHESIS", eval_set="none",
            ssot_sim_ref="SIM-14", formula="learned chemical")
    assert sr.lint_registry([s, c]) == []


def test_lint_columns_needs_exactly_one_notion():
    assert sr.lint_columns(["chemical_sim", "process_response_similarity", "chemicalSim", "simulated_size"]) == []
    bad = sr.lint_columns(["sim", "score", "simScore", "cultural_chemical_score"])
    assert len(bad) == 4
    assert any("cultural_chemical_score" in p and "more than one" in p for p in bad)
    assert sr.lint_columns(["f1_score"], exempt=("f1_score",)) == []


def test_assert_lint_clean_raises_with_every_problem():
    with pytest.raises(sr.RegistryError) as e:
        sr.assert_lint_clean(rows=[row("A"), row("A")], columns=["score"])
    assert "duplicate" in str(e.value) and "score" in str(e.value)
    assert sr.assert_lint_clean(rows=[row()], columns=["chemical_score"]) is None


def test_parse_csv_round_trip_and_strict_header():
    text = sr.to_csv([row("A"), row("B", notion="CULTURAL", split_family="S-cui-src", eval_set="motifs")])
    back = sr.parse_registry_csv(text)
    assert [r.sim_id for r in back] == ["A", "B"] and back[1].notion == "CULTURAL"
    with pytest.raises(sr.RegistryError, match="missing"):
        sr.parse_registry_csv("sim_id,notion\nA,CHEMICAL\n")
    with pytest.raises(sr.RegistryError, match="unknown column"):
        sr.parse_registry_csv(text.replace("sim_id,", "sim_id,flavour_score,", 1).replace("\nA,", "\nA,1,").replace("\nB,", "\nB,2,"))
    with pytest.raises(sr.RegistryError, match="more values"):
        sr.parse_registry_csv(text.replace("\nA,", "\nA,extra,"))


def test_notion_coverage_lists_missing_notions():
    cov = sr.notion_coverage([row(), row("C", notion="CULTURAL", split_family="S-cui-src", eval_set="motifs")])
    assert cov["CHEMICAL"]["rows"] == 1 and cov["CHEMICAL"]["statuses"] == {"BASELINE"}
    assert cov["STRUCTURAL"]["rows"] == 0
    assert set(sr.unlisted_notions([row()])) == set(sr.NOTIONS) - {"CHEMICAL"}


@pytest.mark.parametrize("column", ["sim_id", "decision_ref"])
def test_duplicate_csv_headers_cannot_silently_overwrite_values(column):
    text = sr.to_csv([row()])
    header, record = text.splitlines()
    # DictReader otherwise keeps only the final occurrence of each column.
    malformed = f"{header},{column}\n{record},overwritten\n"
    with pytest.raises(sr.RegistryError, match="duplicate column"):
        sr.parse_registry_csv(malformed)
