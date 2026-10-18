from culinarystate.ingest.bognar import method_groups, methods_of, parse_table

LINES = """Table 26: Average retention factors of food constituents by cooking of vegetable based dishes
          - root, tuber and bulb vegetables, such as kohlrabi, carrot, onions, boiled, steamed, stewed, fried -

                                                             retention factor
     constituents             boil            steam       stew            fry in pan      bake in oven deep fry
                        A             B      A      B       B           A            B         B          A
Protein                0.90          1.00   0.95   1.00   1.00        0.95         1.00      1.00       0.95
Fat uptake               -             -      -      -      -         1.00           -          -       1.00
Vitamin C              0.40          0.85   0.80   0.85   0.85        0.85         0.85      0.85       0.85
1)                      2)""".split("\n")


def test_groups_and_methods():
    assert method_groups(list("ABABBABBA")) == [[0, 1], [2, 3], [4], [5, 6], [7], [8]]
    assert methods_of("constituents  boil   steam  stew  fry in pan  bake in oven deep fry") == \
        ["boil", "steam", "stew", "fry in pan", "bake in oven", "deep fry"]


def test_parse_table_columns():
    rows, problem = parse_table(26, list(enumerate(LINES, 1)))
    assert problem is None
    vc = {(r.method, r.basis): r.value for r in rows if r.constituent == "Vitamin C"}
    assert vc[("boil", "A")] == "0.40" and vc[("boil", "B")] == "0.85" and vc[("deep fry", "A")] == "0.85"
    assert not any(r.constituent == "Fat uptake" for r in rows)             # not a retention factor
    assert rows[0].food_group.startswith("vegetable based dishes") and "kohlrabi" in rows[0].description


def test_variant_table_skipped():
    lines = LINES[:4] + ["                         whole                 polished"] + LINES[4:]
    assert parse_table(37, list(enumerate(lines, 1)))[1].startswith("table 37: product sub-columns")
