"""S178 corpus lane tools: ING reconciliation, Food.com bare-count shapes, SP-002 rerun aggregation, verb census. Synthetic inputs (invented foods)."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from culinarystate.extraction.rung_a import RungA
from culinarystate.extraction.rung_a_lexicon import build_lexicon
from culinarystate.quantity.rc2_dryrun import assert_counts_only, load_schema
from tests.unit.test_s178_analysis_helpers import ROOT, load_tool

R = load_tool("s178_corpus_ing_reconcile")
Q = load_tool("s178_corpus_foodcom_quantity")
U = load_tool("s178_corpus_prenorm_rerun")
V = load_tool("s178_corpus_verb_census")
S = load_tool("s178_corpus_span_agreement")
QU = load_tool("s178_corpus_ing_review_queue")
CARD = load_tool("s178_corpus_foodcom_card")
CEN = load_tool("s178_analysis_coverage_census")
FS = "⁄"


# ------------------------------------------------------------------ ING reconciliation
def _ing(i, version, status, agent, **kw):
    return {"id": f"ING-{i:06d}", "version": version, "status": status, "canonical_name": f"zorb{i}", "record_type": "ING",
            "provenance": {"agent": agent}, "created_at": "2026-10-18T05:44:53+00:00", "schema_version": "1.0.0",
            "verification": {"status": "UNVERIFIED"}, "scientific_identity_status": "UNKNOWN",
            "crosswalks": {"fdc": {"status": "UNRESOLVED_EXTERNAL"}, "foodon": {"status": kw.get("foodon", "NO_MATCH")}},
            "facets": {}, "parent_ids": kw.get("parents", [])}


def _write(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


@pytest.fixture()
def tiny_root(tmp_path):
    led = tmp_path / "ledgers" / "data"
    a1, wb = "a1_ner+registry_build@0.1", "wikibooks_links@0.1"
    ing = [_ing(1, 1, "ACTIVE", a1), _ing(1, 2, "ACTIVE", a1, foodon="LINKED"), _ing(2, 1, "ACTIVE", a1), _ing(2, 2, "SUPERSEDED", a1),
           _ing(3, 1, "ACTIVE", a1, parents=["ING-000001"]), _ing(4, 1, "ACTIVE", wb), _ing(4, 2, "ACTIVE", wb), _ing(5, 1, "DEPRECATED", a1)]
    _write(led / "ING.jsonl", ing)
    _write(led / "ALIAS.jsonl", [{"id": "ALIAS-000001", "version": 1, "status": "ACTIVE", "surface": "x", "ingredient_id": "ING-000001",
                                  "provenance": {"agent": a1}, "created_at": "2026-10-18"},
                                 {"id": "ALIAS-000002", "version": 1, "status": "ACTIVE", "surface": "y", "ingredient_id": "ING-000002",
                                  "provenance": {"agent": a1}, "created_at": "2026-10-18"}])
    _write(led / "PROC.jsonl", [{"id": "PROC-000001", "version": 1, "status": "ACTIVE", "provenance": {"agent": "p"}}])
    _write(led / "_ids.jsonl", [{"id": "ING-000001", "prefix": "ING"}, {"id": "PROC-000001", "prefix": "PROC"}])
    return tmp_path


def test_reconciliation_identities(tiny_root):
    res = R.build(tiny_root)
    ing = res["ledgers"]["ING"]
    assert (ing["lines"], ing["ids"], ing["active_ids"]) == (8, 5, 3)
    assert ing["latest_status"] == {"ACTIVE": 3, "DEPRECATED": 1, "SUPERSEDED": 1}
    assert ing["lines_beyond_first_version"] == 3 and ing["versions_per_id"] == {"1": 2, "2": 3}
    rec = res["reconciliation"]
    assert rec["ids_from_a1_registry_build"] == 4 and rec["active_ids_from_a1_registry_build"] == 2
    assert rec["active_ids_from_other_origins"] == {"wikibooks_links@0.1": 1}
    assert all(rec["identities"].values())
    v = ing["vocab_status"]
    assert v["active_concepts"] == 3 and v["crosswalk_foodon"] == {"LINKED": 1, "NO_MATCH": 2} and v["with_parent_ids"] == 1
    al = res["ledgers"]["ALIAS"]["vocab_status"]
    assert al["active_aliases"] == 2 and al["active_aliases_with_an_active_ing_target"] == 1 and al["active_aliases_without_an_active_ing_target"] == 1
    assert res["minted_id_registry"]["by_prefix"] == {"ING": 1, "PROC": 1}
    assert "_ids" not in res["ledgers"]
    assert R.md(res).startswith("# ING count reconciliation")
    assert not any(c["found_in_file"] for c in res["claims_checked_against_files"] if "found_in_file" in c and c["found_in_file"] is not None)


def test_claim_check_reads_the_number_from_the_file(tmp_path):
    f = tmp_path / "reports"
    f.mkdir()
    (f / "ingredient_registry_v1.md").write_text("- ING concepts: 1,951 (with parent link: 993)\n", encoding="utf-8")
    truth = {"what_it_counts": {"1951": "x", "5387": "y", "2048": "z", "2110": "w"}}
    rows = R.claim_check(tmp_path, truth)
    hit = next(r for r in rows if r["claim"] == "ING_CONCEPTS_1951")
    assert hit["found_in_file"] is True and hit["line"] == 1
    assert next(r for r in rows if r["claim"] == "ING_ROWS_5387_PACKET")["status"] == "SOURCE_FILE_MISSING"
    assert R.to_int("5,387") == 5387


def test_committed_reconciliation_matches_the_live_ledger():
    path = ROOT / "reports/s178/corpus/ing_count_reconciliation_v1.json"
    if not path.is_file():
        pytest.skip("report not generated yet")
    doc = json.loads(path.read_text(encoding="utf-8"))
    live = R.ledger_block("ING", R.read_ledger(ROOT / "ledgers/data/ING.jsonl"))
    for k in ("lines", "ids", "active_ids", "latest_status", "lines_beyond_first_version"):
        assert doc["ledgers"]["ING"][k] == live[k], k
    r = doc["reconciliation"]
    assert (r["ledger_lines"], r["distinct_ids"], r["active_ids"]) == (5387, 2110, 2048)
    assert r["active_ids_from_a1_registry_build"] + sum(r["active_ids_from_other_origins"].values()) == 2048
    assert r["active_ids_from_a1_registry_build"] == 1951          # the number of reports/ingredient_registry_v1.md
    assert doc["contains_text"] is False


# ------------------------------------------------------------------ Food.com quantity shapes
@pytest.mark.parametrize("q,shape", [
    ("1", "INTEGER"), ("12", "INTEGER"), ("1.5", "DECIMAL"), (f"1{FS}2", "FRACTION"), ("1/2", "FRACTION"), (f"1 1{FS}2", "MIXED_NUMBER"),
    ("1 -2", "RANGE"), (f"1{FS}2 - 3{FS}4", "RANGE"), (f"1  - 2 1{FS}2", "RANGE"), ("", "EMPTY"), ("  ", "EMPTY"),
    ("2 cups", "HAS_ALPHABETIC"), ("x", "HAS_ALPHABETIC"), ("1,5", "OTHER_NUMERIC"),
])
def test_shape_of(q, shape):
    assert Q.shape_of(q) == shape


def test_quantity_tool_pct_and_prose_strip():
    assert Q.pct(1, 3) == 33.333 and Q.pct(1, 0) is None
    assert_counts_only(Q.strip_prose({"n": 1, "verdict": {"statement": "free text, here"}}))


# ------------------------------------------------------------------ SP-002 rerun aggregation
@pytest.fixture(scope="module")
def schema():
    return load_schema()


def test_process_chunk_counts_weights_and_transitions(schema):
    U._init(schema)
    items = [(f"1{FS}2 kg zorbfruit", 3), ("2 kg zorbfruit", 5), (f"11{FS}2 kg zorbfruit", 2), ("1-1/2 cups quibbleroot", 4), ("", 7),
             ("3 zorbfruit", 1)]
    fam, blk = U.process_chunk(("TASTESET", items, 10))
    assert fam == "TASTESET"
    assert blk["affected_lines"] == 3 + 2 + 4 and blk["refused_lines"] == 2
    assert blk["rule_lines"] == Counter({"SP002_U2044": 3, "SP002_GLUED_REFUSE": 2, "SP002_HYPHEN_MIXED": 4})
    assert blk["before"]["lines_total"] == 3 + 5 + 2 + 4 + 7 + 1 == blk["after"]["lines_total"]
    assert blk["before"]["lines_blank"] == 7
    # 1⁄2 kg: before a count of 1 item, after 500 g of exact mass (Q0)
    assert blk["after"]["lines_with_rc2_mass"] - blk["before"]["lines_with_rc2_mass"] == 3 + 5 - 5      # 2 kg lines are unchanged and counted in both
    assert blk["transitions"]["mass_route__NO_INGREDIENT_LINK__TO__AST_EXACT_PHYSICAL"] == 3
    assert blk["transitions"]["mass_route__NO_INGREDIENT_LINK__TO__UNSUPPORTED_EXPRESSION"] == 2
    assert blk["value_changed_lines"] >= 3 + 4 and blk["before_value_exactly_one_lines"] >= 3
    assert blk["verify_unaffected"]["checked_unique"] == blk["verify_unaffected"]["identical_unique"] == 2
    assert blk["changed_record_lines"] <= blk["affected_lines"]
    assert not any(k.startswith("flag_added__PRENORM") for k in blk["transitions"])         # markers are not changes
    assert_counts_only(U.plain({"t": blk["transitions"], "r": blk["rule_lines"]}))


def test_merge_block_is_additive(schema):
    U._init(schema)
    items = [(f"1{FS}2 kg zorbfruit", 1), ("2 kg zorbfruit", 2)]
    _, a = U.process_chunk(("FOODCOM", items, 0))
    _, b = U.process_chunk(("FOODCOM", items, 0))
    tot = U._empty_block()
    U.merge_block(tot, a)
    U.merge_block(tot, b)
    assert tot["affected_lines"] == 2 * a["affected_lines"] and tot["before"]["lines_total"] == 2 * a["before"]["lines_total"]
    assert tot["after"]["q_level"]["Q0"] == 2 * a["after"]["q_level"]["Q0"]


def test_vclass():
    assert U._vclass({"status": "MEASURED", "value": 1}) == "E1"
    assert U._vclass({"status": "MEASURED", "value": 0.5}) == "LT1"
    assert U._vclass({"status": "MEASURED", "value": 3}) == "INT_GT1"
    assert U._vclass({"status": "MEASURED", "value": 1.5}) == "FRACTIONAL_GT1"
    assert U._vclass({"status": "RANGE", "low": 1, "high": 2}) == "RANGE"
    assert U._vclass({"status": "UNKNOWN"}) == "UNKNOWN"


# ------------------------------------------------------------------ verb census
def test_fold_forms_merges_onto_a_present_base():
    c = Counter({"whisk": 10, "whisked": 5, "whisking": 2, "carrying": 3, "carry": 1, "stopped": 4, "stop": 9, "bakes": 2, "glass": 4, "lone": 3})
    f = V.fold_forms(c)
    assert f["whisked"] == "whisk" and f["whisking"] == "whisk" and f["whisk"] == "whisk"
    assert f["carrying"] == "carry" and f["stopped"] == "stop"
    assert f["bakes"] == "bakes"                                  # base "bake" absent: stays its own key
    assert f["glass"] == "glass" and f["lone"] == "lone"


@pytest.fixture()
def tiny_rung(monkeypatch):
    lex = build_lexicon(foods={"flour": ["ING-1"], "zorbfruit": ["ING-2"]}, procs={"stir": ["PROC-1"], "bake": ["PROC-2"], "mix": ["PROC-3", "PROC-4"]},
                        proc_info={"PROC-1": ("stir", "MECHANICAL_MIX", "ACTION"), "PROC-2": ("bake", "DRY_HEAT", "ACTION"),
                                   "PROC-3": ("mix", "MECHANICAL_MIX", "ACTION"), "PROC-4": ("mix", "COMBINATION", "ACTION")},
                        tools={"bowl": ["TOOL-1"]}, tool_classes={}, units=[])
    monkeypatch.setattr(V, "_RUNG", RungA(lex))
    return lex


def test_count_texts_on_a_synthetic_text(tiny_rung):
    text = "Stir the flour. Gently fumble the zorbfruit, then bake. Mix well and wobble in a bowl. Flour the bowl."
    got = V.count_texts([text, "", "   "])
    c = got["c"]
    assert c["texts"] == 1 and c["texts_empty"] == 2 and c["sentences"] == 4
    assert c["action_events"] == 3                                  # stir, bake, mix (ambiguous)
    assert c["action_ambiguous"] == 1 and c["action_unique_exact"] == 2
    assert got["by_family"]["MECHANICAL_MIX"] == 1 and got["by_family"]["DRY_HEAT"] == 1      # the ambiguous mix has no single family
    assert got["unm_slot"]["fumble"] == 1 and got["unm_slot"]["wobble"] == 1
    assert got["unm_init"] == Counter()                              # every sentence starts with a mapped verb or an adverb
    assert c["cand_slot_mapped"] + sum(got["unm_slot"].values()) == c["cand_slot"]
    assert c["slot_food_or_tool_word"] == 1                           # the sentence-initial food word is excluded from the candidates


def test_top_unmapped_and_curve_respect_min_count():
    agg = {"unm_slot": Counter({"whisk": 30, "whisked": 10, "rare": 5}), "unm_init": Counter({"whisk": 20}),
           "occ": Counter({"whisk": 40, "whisked": 10, "rare": 50})}
    rows = V.top_unmapped(agg, {"whisk"})
    assert [r["lemma"] for r in rows] == ["whisk"] and rows[0]["slot_count"] == 40 and rows[0]["forms_merged"] == 2
    assert rows[0]["in_bbc_spacy_list"] is True and rows[0]["slot_share_pct"] == 80.0
    assert V.curve(rows, 45) == {"top_1": 88.89}


# ------------------------------------------------------------------ span agreement (TASTEset proxy for T3-C09-R1)
def test_lexicon_spans_and_comparison():
    from culinarystate.extraction.rung_a_lexicon import tokens
    lex = build_lexicon(foods={"olive oil": ["ING-1"], "oil": ["ING-2"], "zorbfruit": ["ING-3"], "salt": ["ING-4"]}, procs={}, proc_info={}, tools={},
                        tool_classes={}, units=[])
    text = "2 tbsp olive oil, 1 zorbfruit, salt, chopped quibbleroot"
    spans = S.lexicon_spans(lex, text, tokens)
    assert [text[a:b] for a, b in spans] == ["olive oil", "zorbfruit", "salt"]           # longest match wins
    def at(sub):
        i = text.index(sub)
        return i, i + len(sub)
    gold = [(*at("olive oil"), "FOOD"), (*at("zorbfruit"), "FOOD"), (*at("chopped quibbleroot"), "FOOD"), (*at("salt"), "PHYSICAL_QUALITY")]
    c, missed, extra = Counter(), Counter(), Counter()
    S.compare(gold, spans, c, missed, extra, text)
    assert c["gold_food_spans"] == 3 and c["gold_food_exact_boundary"] == 2 and c["gold_food_missed_no_overlap"] == 1
    assert missed == Counter({"chopped quibbleroot": 1})
    assert c["lexicon_spans"] == 3 and c["lexicon_overlapping_gold_food"] == 2 and c["lexicon_overlapping_only_gold_PHYSICAL_QUALITY"] == 1
    assert c["lexicon_extra_no_gold_span"] == 0 and extra == Counter()
    # containment and partial overlap
    c2, m2, e2 = Counter(), Counter(), Counter()
    S.compare([(0, 20, "FOOD")], [(2, 8)], c2, m2, e2, "x" * 30)
    S.compare([(0, 5, "FOOD")], [(0, 9)], c2, m2, e2, "x" * 30)
    S.compare([(3, 9, "FOOD")], [(0, 5), (4, 10)], c2, m2, e2, "x" * 30)
    assert c2["gold_food_contains_shorter_lexicon_span"] == 1 and c2["gold_food_inside_a_longer_lexicon_span"] == 1 and c2["gold_food_partial_overlap"] == 1
    assert S.overlap((0, 5), (4, 9)) and not S.overlap((0, 5), (5, 9))


def test_committed_span_agreement_is_counts_only():
    path = ROOT / "reports/s178/corpus/span_agreement_tasteset_v1.json"
    if not path.is_file():
        pytest.skip("report not generated yet")
    d = json.loads(path.read_text(encoding="utf-8"))
    c = d["counts"]
    assert d["label"] == "DIAGNOSTIC_NOT_GOLD" and d["ner_vs_rung_a"] == "BLOCKED_DATA" and d["contains_text"] is False
    assert c["gold_food_spans"] == sum(c[k] for k in ("gold_food_exact_boundary", "gold_food_inside_a_longer_lexicon_span", "gold_food_contains_shorter_lexicon_span",
                                                       "gold_food_partial_overlap", "gold_food_missed_no_overlap"))
    assert not any("phrase" in k for k in d["counts"])


# ------------------------------------------------------------------ review queue
def test_review_queue_rows_bands_and_summary():
    lex = build_lexicon(foods={"salt": ["ING-1"], "pepper": ["ING-2", "ING-3"], "oil": ["ING-4"]}, procs={}, proc_info={}, tools={}, tool_classes={}, units=[])
    from culinarystate.extraction.rung_a_lexicon import key_of
    m = CEN.Matcher(lex, {key_of("salt"), key_of("pepper"), key_of("oil")})
    counter = Counter({("salt",): 50, ("fine", "salt"): 40, ("black", "pepper"): 8, ("zorb", "herb"): 1, ("oil",): 30, ("quibble",): 1})
    cls_of = {k: m.classify(list(k)) for k in counter}
    rows = QU.build_rows(counter, cls_of, m)
    assert [r["phrase"] for r in rows] == ["fine salt", "black pepper", "quibble", "zorb herb"]          # exact phrases are not queued; ties by text
    assert rows[0]["class"] == "PARTIAL" and rows[0]["candidate_ing_ids"] == "ING-1" and rows[0]["n_candidate_ids"] == 1
    assert rows[1]["n_candidate_ids"] == 2 and rows[1]["candidate_ing_ids"] == "ING-2|ING-3"             # polysemous surface
    assert rows[2]["class"] == "MISS" and rows[2]["candidate_ing_ids"] == "" and rows[2]["covered_tokens"] == 0
    assert rows[-1]["cum_share_pct"] == 100.0 and [r["rank"] for r in rows] == [1, 2, 3, 4]
    assert [r["band"] for r in rows] == ["A", "B", "C", "C"]                        # a row is band A while the rows before it hold < 80 % of the mentions
    assert rows[1]["default_confidence"] == "REVIEW_QUEUE" and rows[3]["default_confidence"] == "LOW_CONFIDENCE_UNREVIEWED"
    assert all(r["reviewer_id"] == "" and r["verdict"] == "" for r in rows)
    sm = QU.summarise(rows, family_mentions=sum(counter.values()))
    assert sm["nonexact_phrases"] == 4 and sm["nonexact_mentions"] == 50 and sm["partial_phrases"] == 2 and sm["miss_phrases"] == 2
    assert sm["partial_polysemous_more_than_one_candidate_id"] == 1 and sm["mentions_in_phrases_seen_once"] == 2
    assert sm["phrases_for_pct_of_nonexact_mentions"]["P80"] == 1


def test_committed_queue_summary_reproduces_the_coverage_census():
    q = ROOT / "reports/s178/corpus/ing_review_queue_summary_v1.json"
    c = ROOT / "reports/s178/analysis/ing_alias_coverage_census_v1.json"
    if not (q.is_file() and c.is_file()):
        pytest.skip("report not generated yet")
    qd, cd = json.loads(q.read_text(encoding="utf-8")), json.loads(c.read_text(encoding="utf-8"))
    for fam in ("FOODCOM", "WIKIBOOKS", "TASTESET"):
        assert qd["families"][fam]["nonexact_phrases"] == cd["families"][fam]["nonexact_types"]
        assert qd["families"][fam]["nonexact_mentions"] == cd["families"][fam]["nonexact_mentions"]
        assert qd["families"][fam]["phrases_for_pct_of_nonexact_mentions"]["P80"] == cd["families"][fam]["nonexact_types_needed_for_pct_of_nonexact_mentions"]["80"]
    assert qd["contains_text"] is False and all(f["git_ignored"] for f in qd["files"].values())


# ------------------------------------------------------------------ data card
def test_data_card_numbers_equal_their_sources():
    try:
        card = CARD.build(ROOT)
    except FileNotFoundError:
        pytest.skip("source reports not generated yet")
    n = card["numbers"]
    al = json.loads((ROOT / CARD.SRC["align"]).read_text(encoding="utf-8"))["diagnostic"]
    assert n["recipes"] == al["recipes"] == 522517 and n["recipes_unequal_lists"] == al["recipes_unequal"]
    assert n["lines_unit_missing_in_source_s177"] == n["ingredient_part_lines"] == 4129433 and n["lines_with_grams_s177"] == 0
    assert n["quantity_strings_with_a_letter"] == 0
    assert [s["id"] for s in card["sentences"]] == ["LICENCE", "SHAPE", "NO_UNITS", "GRAMS", "MISALIGNMENT", "SP002", "NAMES", "STEPS"]
    assert "NOT verified" in card["sentences"][0]["text"] and card["contains_text"] is False
    assert CARD.md(card).count("|") > 20
