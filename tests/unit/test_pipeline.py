from culinarystate.decision.pipeline import Lexicon, parse_query
from culinarystate.vocab.line_link import LineLinker

LEX = Lexicon(linker=LineLinker({"broccoli": "ING-1", "spinach": "ING-2"}, set()),
              proc_ids={"boil": "PROC-1", "steam": "PROC-2", "fry": "PROC-3", "microwave": "PROC-4",
                        "reserve": "PROC-5", "divide": "PROC-6", "can": "PROC-7"},
              parents={"ING-1": ("ING-9",)}, processed_by={"ING-2": ("PROC-2", "PROC-1", "PROC-3")},
              heat_procs=frozenset({"PROC-1", "PROC-2", "PROC-3", "PROC-4"}))


def test_parse_answer_query():
    s = parse_query("How much vitamin C does boiled broccoli keep?", LEX)
    assert (s.ingredient_id, s.target, [p for _, p in s.processes]) == ("ING-1", "vitamin c", ["PROC-1"])
    assert s.parents == ("ING-9",) and s.candidates == ()


def test_parse_compare_keeps_both_processes_in_order():
    s = parse_query("What happens to folate in spinach if I steam instead of boiling?", LEX)
    assert [p for _, p in s.processes] == ["PROC-2", "PROC-1"] and s.target == "folate"


def test_recommend_without_process_generates_corpus_candidates():
    s = parse_query("How should I cook spinach to keep vitamin C?", LEX)
    assert s.processes == () and s.candidates == ("PROC-2", "PROC-1", "PROC-3")


def test_unlinked_ingredient_stays_none():
    assert parse_query("How much vitamin C does boiled kohlrabi keep?", LEX).ingredient_id is None


def test_question_homographs_are_not_processes():
    assert parse_query("How should I cook spinach to keep vitamin C?", LEX).processes == ()
    assert parse_query("Why did my sauce split?", LEX).processes == ()
    assert [p for _, p in parse_query("I boiled the broccoli too long; how can I recover?", LEX).processes] == ["PROC-1"]


def test_ingredient_name_is_carried():
    assert parse_query("How much vitamin C does boiled broccoli keep?", LEX).ingredient_name == "broccoli"


def test_negated_and_affirmed_same_process_is_contradiction():
    s = parse_query("How much vitamin C does boiled and also not boiled broccoli keep?", LEX)
    assert s.contradictions == ("PROC-1",)
    assert parse_query("How much vitamin C does boiled broccoli keep?", LEX).contradictions == ()


def test_food_graph_relations_reach_the_query():
    from dataclasses import replace
    from culinarystate.decision.pipeline import answer
    seen = {}

    class R:
        def packet(self, q, query, k):
            seen["rel"] = query.ingredient_relations
            from culinarystate.retrieval.retriever import EvidencePacket
            return EvidencePacket(q, query, "UNSUPPORTED")
    lex = replace(LEX, relations={"ING-1": (("ING-9", "PARENT"),)})
    from culinarystate.decision.feasibility import Requirements
    answer("How much vitamin C does boiled broccoli keep?", lex, R(), Requirements({"PROC-1": "boil"}, {}, {}, {}),
           {"PROC-1": "WET"})
    assert seen["rel"] == (("ING-9", "PARENT"),)
