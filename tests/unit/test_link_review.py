from culinarystate.evidence.link_review import decide

NAMES = {"potato": "ING-000001", "courgette": "ING-000002", "zucchini": "ING-000002"}


def _r(**kw):
    return {"matrix_raw": "POTATOES", "source_family": "USDA", "suggested": "potato", "ai_recommended_link": "potato",
            "human_decision": "ACCEPT", "human_reviewer": "Kush", "human_review_date": "2026-10-18", **kw}


def test_signed_accept_links_and_correct_uses_recommended_concept_via_alias():
    assert decide(_r(), NAMES)["status"] == "LINKED" and decide(_r(), NAMES)["ingredient_id"] == "ING-000001"
    d = decide(_r(human_decision="CORRECT", ai_recommended_link="zucchini", suggested=None), NAMES)
    assert d["ingredient_id"] == "ING-000002"


def test_unsigned_or_ai_only_never_links():
    assert decide(_r(human_decision=""), NAMES)["status"] == "UNSIGNED"
    assert decide(_r(human_reviewer="Claude"), NAMES)["status"] == "INVALID_SIGNOFF"
    assert decide(_r(human_review_date="18/10/2026"), NAMES)["status"] == "INVALID_SIGNOFF"


def test_holds_never_link_and_missing_concepts_are_not_minted():
    for h in ("HOLD_CATEGORY_SCOPE", "HOLD_MULTI_MATRIX", "HOLD_COMPOSITE_DISH", "UNRESOLVED"):
        d = decide(_r(human_decision=h), NAMES)
        assert d["status"] == "HELD" and d["ingredient_id"] is None
    d = decide(_r(human_decision="CORRECT", ai_recommended_link="hare"), NAMES)
    assert d["status"] == "CONCEPT_MISSING" and d["ingredient_id"] is None
    assert decide(_r(human_decision="MAYBE"), NAMES)["status"] == "INVALID_DECISION"
