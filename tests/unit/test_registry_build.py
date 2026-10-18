import pandas as pd

from culinarystate.vocab.registry_build import (build_aliases, build_concepts, classify_reject, coverage_curve,
                                                structural_parent)


def test_classify_reject():
    assert classify_reject("wooden skewer") == "non_food_utensil"
    assert classify_reject("pork skin") == "food_part_needs_part_model"   # edible part: review, not delete
    assert classify_reject("dark") == "adjective_only"
    assert classify_reject("butter") is None


def test_structural_parent():
    known = {"turmeric", "butter", "milk", "almond milk", "potato", "roast potato", "harissa"}
    assert structural_parent("turmeric powder", known)[:2] == ("turmeric", "FORM_OF")
    assert structural_parent("unsalted butter", known)[:2] == ("butter", "VARIANT_OF")
    assert structural_parent("roast potato", known)[:2] == ("potato", "VARIANT_OF")
    assert structural_parent("almond milk", known)[:2] == ("milk", "HEAD_NOUN")   # not taxonomy
    assert structural_parent("harissa", known)[:2] == (None, None)


def _mentions():
    rows = []
    for r in range(5):
        rows += [{"recipe_id": f"R{r}", "ingredient_normalized": "eggs", "ingredient_canonical": "egg"},
                 {"recipe_id": f"R{r}", "ingredient_normalized": "egg", "ingredient_canonical": "egg"},
                 {"recipe_id": f"R{r}", "ingredient_normalized": "coriander", "ingredient_canonical": "coriander"}]
    rows += [{"recipe_id": "R0", "ingredient_normalized": "rare thing", "ingredient_canonical": "rare thing"}]
    return pd.DataFrame(rows)


def test_concepts_min_freq_and_polysemy():
    concepts, rejects = build_concepts(_mentions(), min_recipes=3)
    names = {c.name: c for c in concepts}
    assert set(names) == {"egg", "coriander"}          # 'rare thing' below threshold, never padded in
    assert names["coriander"].ambiguity == "HIGH"
    assert rejects.empty


def test_aliases_and_coverage():
    m = _mentions()
    concepts, _ = build_concepts(m, 3)
    al = {a.surface: a for a in build_aliases(m, {c.name for c in concepts})}
    assert al["eggs"].canonical == "egg" and al["eggs"].alias_type == "PLURAL"
    assert al["egg"].link_band == "EXACT"
    cur = coverage_curve(m, concepts)
    assert cur["cum_share"].iloc[-1] == 1.0 and not cur.loc[cur.canonical == "rare thing", "in_registry"].iloc[0]
