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
