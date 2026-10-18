from culinarystate.kg.mine import alternatives, endpoints, forms, is_optional, media

def _link(t):
    t = t.lower()
    return next((v for k, v in {"margarine": "ING-2", "butter": "ING-1", "oil": "ING-3"}.items() if k in t), None)


def test_optional_and_forms():
    assert is_optional("1 tsp chilli flakes (optional)") and is_optional("salt to taste")
    assert not is_optional("2 onions, chopped")
    assert forms("2 onions, finely chopped and 1 carrot, grated") == {"finely chopped", "grated"}


def test_alternatives():
    assert alternatives("50g butter or margarine", _link) == ("ING-1", "ING-2")
    assert alternatives("butter or more butter", _link) is None
    assert alternatives("butter or oil or margarine", _link) is None                      # only binary choices


def _link_head(t):
    names = {"chicken stock": "ING-CS", "vegetable stock": "ING-VS", "stock": "ING-S", "chicken": "ING-C",
             "pasta": "ING-P", "egg noodles": "ING-EN", "noodles": "ING-N"}
    w = t.lower().split()
    return next((names[" ".join(w[i:i + n])] for n in (2, 1) for i in range(len(w) - n, -1, -1)
                 if " ".join(w[i:i + n]) in names), None)


def test_alternatives_distribute_head():
    assert alternatives("500ml chicken or vegetable stock", _link_head) == ("ING-CS", "ING-VS")
    assert alternatives("250g pasta or egg noodles", _link_head) == ("ING-P", "ING-EN")   # "pasta noodles" is no concept


def test_media_and_endpoints():
    assert media("Fry the onions in a little oil, then boil in salted water") == {"oil", "water"}
    procs = [(0, "fry"), (40, "simmer")]
    s = "Fry the onions until golden brown, then simmer until thickened."
    assert endpoints(s, procs) == [("fry", "golden brown"), ("simmer", "thickened")]
