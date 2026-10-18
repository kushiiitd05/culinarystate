from culinarystate.evidence.linker import IngredientLinker, link_process

C = {"cabbage": ("ING-1", 50), "red cabbage": ("ING-2", 20), "potato": ("ING-3", 700), "onion": ("ING-4", 900),
     "red onion": ("ING-5", 500), "red pepper": ("ING-6", 300), "pepper": ("ING-7", 400)}
L = IngredientLinker(C)


def test_ingredient_links():
    assert L.link("Common cabbage [Red], raw").concept == "red cabbage"
    assert L.link("POTATOES").band == "HIGH" and L.link("POTATOES").ing_id == "ING-3"
    assert L.link("onion").band == "EXACT"
    assert L.link("VEG,GREENS").band == "NONE"


def test_process_primary_is_heat_step():
    pids = {"boil": "PROC-1", "drain": "PROC-2", "stir": "PROC-3", "bake": "PROC-4"}
    assert link_process(["boil", "drain"], pids) == ("PROC-1", ["PROC-1", "PROC-2"])
    assert link_process(["stir", "bake|simmer"], pids)[0] == "PROC-4"
    assert link_process(["drain"], pids) == ("PROC-2", ["PROC-2"])


def test_linker_regressions_from_spot_check():
    c = {"fat": ("I-f", 100), "grain": ("I-g", 50), "white": ("I-w", 10), "maize": ("I-m", 5),
         "yellow pepper": ("I-yp", 40), "pepper": ("I-p", 400), "blackcurrant": ("I-b", 30), "blueberry": ("I-bb", 60)}
    lk = IngredientLinker(c, polysemous={"pepper"})
    assert lk.link("FINFISH,<5%FAT").band == "NONE"                      # 'fat' is not the food
    assert lk.link("Maize, whole grain").concept == "maize"
    assert lk.link("Maize [White]").concept == "maize"
    assert lk.link("Chilli pepper C. pubescens [Yellow], raw").band == "MEDIUM"
    assert lk.link("Blackcurrant, juice").band == "MEDIUM"                # form changes the matrix
    assert lk.link("Highbush blueberry, raw").band == "HIGH"
    assert lk.link("Pepper [Unknown color], raw").band == "MEDIUM"        # polysemous never auto-links


def test_plural_form_token_downgrades():
    lk = IngredientLinker({"buckwheat": ("I-1", 5)})
    assert lk.link("Buckwheat, grits").band == "MEDIUM"
