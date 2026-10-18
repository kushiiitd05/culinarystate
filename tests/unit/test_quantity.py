import pytest

from culinarystate.quantity.grammar import parse_line, to_number
from culinarystate.quantity.normalize import normalize


def n(line, locale="UK"):
    p = parse_line(line)
    return p, normalize(p, locale=locale)


def val(q):
    if q["status"] == "MEASURED":
        return q["value"]
    if q["status"] == "RANGE":
        return (q["low"], q["high"])
    return q["status"]


@pytest.mark.parametrize("tok,expected", [("1", 1), ("1/2", 0.5), ("1 1/2", 1.5), ("2.5", 2.5)])
def test_to_number(tok, expected):
    assert to_number(tok) == expected


@pytest.mark.parametrize("line,kind,unit,mass,vol,cnt,q", [
    ("100g butter softened", "NUMBER", "g", 100.0, "UNKNOWN", "UNKNOWN", "Q0"),
    ("1kg ripe tomatoes", "NUMBER", "kg", 1000.0, "UNKNOWN", "UNKNOWN", "Q0"),
    ("1.2 litres chicken stock", "NUMBER", "l", "UNKNOWN", 1200.0, "UNKNOWN", "Q6"),
    ("1 ½ tbsp vegetable oil", "MIXED", "tbsp", "UNKNOWN", 22.5, "UNKNOWN", "Q6"),
    ("¼ cup sugar", "FRACTION", "cup", "UNKNOWN", (59.147059, 62.5), "UNKNOWN", "Q6"),
    ("1 heaped tsp ground cumin", "NUMBER", "tsp", "UNKNOWN", 5.0, "UNKNOWN", "Q6"),
    ("2 x 400g cans chopped tomatoes", "MULTIPLIER", "can", 800.0, "UNKNOWN", 2.0, "Q0"),
    ("200g  can tuna in oil", "PACKAGE", "can", 200.0, "UNKNOWN", 1.0, "Q0"),
    ("142ml  carton soured cream", "PACKAGE", "carton", "UNKNOWN", 142.0, 1.0, "Q6"),
    ("4 leeks (about 500g), sliced", "NUMBER", None, 500.0, "UNKNOWN", 4.0, "Q0"),
    ("2-4 thick slices leftover roast turkey (about 100g)", "RANGE", "slice", 100.0, "UNKNOWN", (2.0, 4.0), "Q0"),
    ("1 small glass white wine", "NUMBER", "glass", "UNKNOWN", "UNKNOWN", 1.0, "Q6"),
    ("2 garlic cloves", "NUMBER", None, "UNKNOWN", "UNKNOWN", 2.0, "Q6"),
    ("1 egg", "NUMBER", None, "UNKNOWN", "UNKNOWN", 1.0, "Q6"),
    ("a couple of bay leaves", "NUMBER", None, "UNKNOWN", "UNKNOWN", 2.0, "Q6"),
    ("5cm piece ginger, grated", "NUMBER", "piece", "UNKNOWN", "UNKNOWN", 1.0, "Q6"),
    ("1 katori toor dal", "NUMBER", "katori", "UNKNOWN", "UNKNOWN", 1.0, "Q6"),
])
def test_parse_and_normalize(line, kind, unit, mass, vol, cnt, q):
    p, z = n(line)
    assert (p.kind, p.unit_key) == (kind, unit)
    assert (val(z.mass_g), val(z.volume_ml), val(z.count), z.q_level) == (mass, vol, cnt, q)


@pytest.mark.parametrize("line", ["a pinch of salt", "good handful pea shoots", "salt and pepper, to taste",
                                  "a little olive oil", "2 tbsp", "1 large pinch chilli flakes"])
def test_qualitative_never_numeric_mass(line):
    p, z = n(line)
    if p.kind == "QUALITATIVE":
        assert all(c["status"] == "QUALITATIVE" for c in (z.mass_g, z.volume_ml, z.count))
    assert z.mass_g["status"] in {"UNKNOWN", "QUALITATIVE"}


def test_no_invented_grams_for_counts_and_volumes():
    for line in ["3 eggs", "1 cup flour", "2 tbsp sugar", "1 bunch coriander", "6 rosemary sprigs", "1 small onion"]:
        _, z = n(line)
        assert z.mass_g["status"] == "UNKNOWN", line
        assert z.q_level == "Q6"


def test_locale_changes_spoon_volume():
    assert val(n("1 tbsp oil", "US")[1].volume_ml) == pytest.approx(14.78676478125)
    assert val(n("1 tbsp oil", "AU")[1].volume_ml) == 20.0
    assert val(n("1 tbsp oil", None)[1].volume_ml) == pytest.approx((14.78676478125, 20.0), abs=1e-5)


def test_cup_ambiguous_in_uk():
    _, z = n("1 cup rice", "UK")
    assert z.volume_ml["status"] == "RANGE" and "locale_ambiguous" in z.flags


def test_dual_units_keep_metric_and_flag_disagreement():
    p, z = n("100g/4oz butter")
    assert p.alt == (4.0, "oz") and val(z.mass_g) == 100.0 and "alt_unit_disagrees" not in z.flags
    _, z2 = n("100g/8oz butter")
    assert "alt_unit_disagrees" in z2.flags


def test_contradictory_stated_mass_flagged_not_rewritten():
    _, z = n("500g potatoes (about 200g)")
    assert val(z.mass_g) == 500.0 and "contradictory_stated_mass" in z.flags


def test_raw_preserved_and_rest():
    raw = "1 bunch of asparagus (about 250g)"
    p = parse_line(raw)
    assert p.raw == raw and p.rest == "asparagus"


def test_juice_of():
    p, z = n("juice of 1 lemon")
    assert p.part == "juice" and val(z.count) == 1.0 and p.rest == "lemon"


def test_no_quantity():
    p, z = n("olive oil for kneading")
    assert p.kind == "NONE" and z.mass_g["status"] == "UNKNOWN"


@pytest.mark.parametrize("line,mass,cnt,unit", [
    ("375g sheet ready-rolled puff pastry", 375.0, 1.0, "sheet"),
    ("150g ball mozzarella chopped", 150.0, 1.0, "ball"),
    ("175g gram (chickpea) flour", 175.0, "UNKNOWN", "g"),
    ("small bunch coriander chopped", "UNKNOWN", 1.0, "bunch"),
    ("thumb-sized piece ginger", "UNKNOWN", 1.0, "piece"),
    ("&frac12; onion finely chopped", "UNKNOWN", 0.5, None),
    ("250g pouch cooked grains", 250.0, 1.0, "pouch"),
])
def test_corpus_driven_cases(line, mass, cnt, unit):
    p, z = n(line)
    assert p.unit_key == unit and val(z.mass_g) == mass and val(z.count) == cnt
    assert not any(f.startswith("second_unit_ignored") for f in z.flags)


def test_implicit_one_is_marked():
    assert "implicit_one" in parse_line("large bunch spring onions").qualifiers


@pytest.mark.parametrize("line", ["few drops vanilla extract", "grating of nutmeg"])
def test_more_qualitative(line):
    assert parse_line(line).kind == "QUALITATIVE"
