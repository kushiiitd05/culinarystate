from culinarystate.ingest.bognar_yield import parse_yields

TEXT = """\x0cTable 17: Weight yield factors by cooking of vegetables based dishes
          - root, tuber and stem vegetables, without potatoes -
 Beetroots, with skin, boiled                                FR m.S            a        1.04    0.03       0.83     0.03   45
 Carrot, boiled                                            FR/TK m.S           a         -        -        0.94     0.06   103
 Asparagus, boiled, steamed                                   FR o.Z          a/b        -        -        1.00     0.00   2
 -              , egg part                                                                   -         -       0.40        -    -
 Roast veal (breast, leg, shoulder)                        FR m.S          e         > 80         -         -       0.67     0.04    11
 Green peas stew (peel peas)                               TR m.Z          a*         -         -       1.82      -        1
 x = mean value of available data; ± = confidence interval (p = 0,05); - = not available or not known
Table 18: Weight yield factors by cooking of vegetables based dishes
"""


def test_parse_yields():
    rows = parse_yields(TEXT)
    assert [r.description for r in rows] == ["Beetroots, with skin, boiled", "Carrot, boiled", "Asparagus, boiled, steamed",
                                             "Roast veal (breast, leg, shoulder)", "Green peas stew (peel peas)"]
    b = rows[0]
    assert (b.table, b.raw_states, b.recipe, b.methods, b.with_waste, b.edible, b.edible_ci, b.n) == \
        (17, ("fresh raw",), "with salt and spice", ("boil",), 1.04, 0.83, 0.03, 45)
    assert rows[1].raw_states == ("fresh raw", "deep frozen raw") and rows[1].with_waste is None
    assert rows[2].methods == ("boil", "steam")
    assert (rows[3].core_temp_c, rows[3].edible, rows[3].n) == ("> 80", 0.67, 11) and rows[0].core_temp_c is None
    assert rows[4].edible_ci is None and rows[4].by_producer_instruction and rows[4].raw_states == ("dried raw",)
