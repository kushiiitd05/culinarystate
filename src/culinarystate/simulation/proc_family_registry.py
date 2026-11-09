"""PROC -> process-family registry for the physical layers (S178 PHYS2, T4-C01-R1). DRAFT, AI_DRAFTED.

One row per PROC of the PROC ledger (latest version of every id), with exactly ONE primary family, an optional secondary
family with the verb-ambiguity rule that decides between them, the FORM candidate class and the binder that handles the
verb. The primary family is the PROC ledger family, with one override: ``store`` (PROC-000113, ledger family TRANSFER) is the
physical family STORAGE, exactly as ``nonheat_binding.NonHeatBinder.nh_family`` treats it. Families: the four heat families
(WET_HEAT, DRY_HEAT, FAT_HEAT, HEAT_GENERAL), HEAT_CONTROL (setpoint carriers), the eight non-heat families (COOLING,
SEPARATION, FERMENT_LEAVEN, PRESERVATION, MECHANICAL_CUT, MECHANICAL_MIX, RESTING, STORAGE), ENDPOINT (stopping-criterion
words, never inputs) and BOOKKEEPING (composition / location only: COMBINATION, TRANSFER, SHAPING, SERVING, RESERVATION).

The ambiguity rules are PROPOSED disambiguation cues for the verbs whose family depends on context (soak, brine, dry, rest and
others). They are rules about WORDS in recipe text, not food science; none is human verified. The registry is the contract the
binders are tested against (``validate``): every PROC exactly once, one primary family, every non-heat family inhabited, the
primary family of every non-heat PROC equal to what ``nh_family`` returns.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[3]
VERSION = "proc-family-registry-1.0.0-draft"
REGISTRY = "registry/proc_family_registry_v1.csv"
COLUMNS = ("proc_id", "canonical", "ledger_family", "primary_family", "layer_scope", "binder", "form_candidate_class",
           "medium_code", "secondary_family", "ambiguity_flag", "ambiguity_rule", "family_override_note", "status")
HEAT_FAMILIES = ("WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL")
NONHEAT_FAMILIES = ("COOLING", "SEPARATION", "FERMENT_LEAVEN", "PRESERVATION", "MECHANICAL_CUT", "MECHANICAL_MIX", "RESTING",
                    "STORAGE")
OTHER_FAMILIES = ("HEAT_CONTROL", "ENDPOINT", "BOOKKEEPING")
PRIMARY_FAMILIES = HEAT_FAMILIES + NONHEAT_FAMILIES + OTHER_FAMILIES
BOOKKEEPING_LEDGER_FAMILIES = ("COMBINATION", "TRANSFER", "SHAPING", "SERVING", "RESERVATION")
STORE_PROC = "PROC-000113"
UNSUPPORTED_MEDIA = ("MICROWAVE", "RADIANT")
FORM_HEAT = "TRANSIENT_CONDUCTION_SLAB_SERIES|EQUIVALENT_TIME_DOSE|EVAPORATION_CAP"
FORM_NONE = {"HEAT_CONTROL": "NONE_SETPOINT_CARRIER", "ENDPOINT": "NONE_ENDPOINT_CUE_NOT_AN_INPUT",
             "BOOKKEEPING": "NONE_STATE_GRAPH_BOOKKEEPING"}
STATUS = "AI_DRAFTED_PENDING_REVIEW"

# verb ambiguity: proc_id -> (secondary family, rule). PROPOSED word-level cues, not food science.
AMBIGUITY: dict[str, tuple[str, str]] = {
    "PROC-000129": ("SEPARATION", "SOAK_DISCARD: soak is FERMENT_LEAVEN (uptake); when the soaking liquid is drained, strained or "
                    "discarded in the next physical step (follows_soak_or_brine) the step pair is also a SEPARATION leaching hand-off"),
    "PROC-000155": ("FERMENT_LEAVEN", "BRINE_SHORT_VS_LONG: brine is PRESERVATION by default (long, days, with vinegar or pickling "
                    "context); a short brine of meat or poultry (hours, salt solution, then cooked) is FERMENT_LEAVEN uptake; the "
                    "noun brine in 'bring the brine to a boil' is not a process"),
    "PROC-000100": ("PRESERVATION", "MARINATE_ACID_LONG: marinate is FERMENT_LEAVEN; an acid or salt marinade held for days is "
                    "closer to PRESERVATION; the noun marinade is not a process (NON_VERB_SURFACES)"),
    "PROC-000133": ("SEPARATION", "DRY_PROCESS_VS_WORD: dry / dehydrate is PRESERVATION only with a drying medium (oven, dehydrator, "
                    "sun, air) or a duration of an hour or more; 'pat dry', 'wipe dry' and 'dry ingredients' are not drying (SEPARATION "
                    "pat-dry or no process); 'dry-fry' is FAT_HEAT"),
    "PROC-000042": ("FERMENT_LEAVEN", "REST_AFTER_HEAT_VS_DOUGH: rest / stand / sit is RESTING (carry-over, still air) after a heat "
                    "step; on a dough or batter lot with no heat before it, a rest is a relaxation or proving step (FERMENT_LEAVEN); "
                    "'let stand 10 minutes before cooking' on cut aromatics is a waiting time (RESTING, no carry-over)"),
    "PROC-000130": ("FERMENT_LEAVEN", "CURE_SALT_UPTAKE_VS_PICKLE: pickle is PRESERVATION; the alias cure (salt cure of meat or fish) "
                    "is salt uptake, also FERMENT_LEAVEN"),
    "PROC-000132": ("BOOKKEEPING", "CAN_MODAL_VS_VERB: 'can' is the verb (PRESERVATION) only with jars, a canner or a water bath; the "
                    "modal 'can' and the noun 'can' (tin) are not processes (NON_VERB_SURFACES)"),
    "PROC-000131": ("HEAT_GENERAL", "STERILISE_JARS_VS_CANNING: sterilise jars is a conditions-only step; the canning step is the "
                    "process in a pressure canner (F0 scope, S177); sterilise as a word on a utensil is not food physics"),
    "PROC-000028": ("ENDPOINT", "REDUCE_VERB_VS_ENDPOINT: reduce the sauce is WET_HEAT (evaporation); 'simmer until reduced by half' "
                    "is an endpoint cue (EVAPORATE_REDUCE) of the simmer; 'reduce the heat' is HEAT_CONTROL adjust-heat"),
    "PROC-000138": ("WET_HEAT", "REDUCE_HEAT_VS_REDUCE: lower / increase the heat is HEAT_CONTROL; the verb reduce is PROC-000028"),
    "PROC-000102": ("ENDPOINT", "SET_PUT_VS_SET_FIRM: 'set aside', 'set the pan on the hob' is TRANSFER (put alias set); 'until set', "
                    "'leave to set' is the ENDPOINT PROC-000146 (set / firm)"),
    "PROC-000146": ("BOOKKEEPING", "SET_FIRM_VS_PUT: see PROC-000102; an ENDPOINT word is never an input"),
    "PROC-000016": ("ENDPOINT", "BROWN_VERB_VS_COLOUR: brown the meat is FAT_HEAT (a pan step); 'cook until browned' is an endpoint cue "
                    "(COLOUR) of the cooking step"),
    "PROC-000147": ("FERMENT_LEAVEN", "RISE_ENDPOINT_VS_PROVE: puff / rise as an oven state ('until risen') is ENDPOINT; 'let the "
                    "dough rise' is a proving step (FERMENT_LEAVEN prove)"),
    "PROC-000070": ("PRESERVATION", "PROCESS_BLEND_VS_CANNING: the alias process (food processor) is MECHANICAL_MIX blend; 'process the "
                    "jars in a boiling water bath' is PRESERVATION canning (jar, canner or water-bath cue)"),
    "PROC-000136": ("STORAGE", "KEEP_RESERVE_VS_STORE: reserve / save / keep for later is RESERVATION (lot bookkeeping); 'keep in the "
                    "fridge for 3 days' is STORAGE (store)"),
    "PROC-000113": ("BOOKKEEPING", "STORE_PHYSICAL_VS_TRANSFER: the ledger family of store is TRANSFER; the physical family is STORAGE "
                    "when a time or a storage temperature class is stated, else it is lot location only"),
    "PROC-000038": ("RESTING", "COOL_AMBIENT_VS_REST: cool / let cool on a rack or the counter is COOLING to ambient (environment ROOM); "
                    "RESTING is only the verbs rest / stand / sit; 'a cool place' is a noun phrase, not a process"),
    "PROC-000039": ("FERMENT_LEAVEN", "CHILL_VS_RELAX: chill the dish is COOLING; chill a dough or batter to relax or firm it is "
                    "still COOLING (temperature falls); only a stated fermentation or proving time makes it FERMENT_LEAVEN"),
    "PROC-000085": ("BOOKKEEPING", "SQUEEZE_WATER_VS_JUICE: squeeze out the water is SEPARATION; squeeze / juice a lemon produces an "
                    "ingredient lot (composition only)"),
    "PROC-000096": ("FAT_HEAT", "BASTE_ALIAS_COLLISION: brush (COMBINATION) has the alias baste; PROC-000152 baste is FAT_HEAT; the "
                    "primary family is per PROC id, the verb in text needs a heat or pan context to be FAT_HEAT"),
    "PROC-000152": ("BOOKKEEPING", "BASTE_ALIAS_COLLISION: see PROC-000096"),
    "PROC-000052": ("BOOKKEEPING", "TOP_ALIAS_COLLISION: trim has the alias top ('top and tail'); PROC-000094 top is COMBINATION "
                    "('top with cheese')"),
    "PROC-000094": ("MECHANICAL_CUT", "TOP_ALIAS_COLLISION: see PROC-000052"),
    "PROC-000029": ("FERMENT_LEAVEN", "INFUSE_HOT_VS_COLD: infuse / steep in hot liquid is WET_HEAT; a cold steep over hours is uptake "
                    "(FERMENT_LEAVEN)"),
}


def latest_proc(root: Path = ROOT) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with open(root / "ledgers/data/PROC.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                if r["id"] not in out or r.get("version", 0) >= out[r["id"]].get("version", 0):
                    out[r["id"]] = r
    return out


def primary_family(proc_id: str, ledger_family: str) -> str:
    if proc_id == STORE_PROC:
        return "STORAGE"
    if ledger_family in HEAT_FAMILIES + NONHEAT_FAMILIES:
        return ledger_family
    if ledger_family in ("HEAT_CONTROL", "ENDPOINT"):
        return ledger_family
    if ledger_family in BOOKKEEPING_LEDGER_FAMILIES:
        return "BOOKKEEPING"
    raise ValueError(f"{proc_id}: unmapped ledger family {ledger_family!r}")


def build_rows(root: Path = ROOT) -> list[dict]:
    from culinarystate.simulation import nonheat_binding as NB
    procs = latest_proc(root)
    with open(root / "registry/process_medium_map_v1.csv", newline="", encoding="utf-8") as fh:
        medium = {r["process_id"]: r["medium_code"] for r in csv.DictReader(fh)}
    rows = []
    for pid in sorted(procs):
        r = procs[pid]
        led = r.get("family")
        fam = primary_family(pid, led)
        sec, rule = AMBIGUITY.get(pid, ("", ""))
        if fam in HEAT_FAMILIES:
            med = medium.get(pid, "")
            form = "UNSUPPORTED_MEDIUM_NO_FORM" if med in UNSUPPORTED_MEDIA else FORM_HEAT
            scope, binder = "HEAT_L1_L2", "condition_binding"
        elif fam in NONHEAT_FAMILIES:
            med, form = "", NB.FORM_CANDIDATE[fam]
            scope, binder = "NONHEAT_L1_L2", "nonheat_binding"
        elif fam == "HEAT_CONTROL":
            med, form, scope, binder = "", FORM_NONE[fam], "HEAT_SETPOINT_CARRIER", "condition_binding"
        elif fam == "ENDPOINT":
            med, form, scope, binder = "", FORM_NONE[fam], "ENDPOINT_CUE_ONLY", "endpoint_cues"
        else:
            med, form, scope, binder = "", FORM_NONE[fam], "NO_PHYSICS", "none"
        note = f"ledger family {led}; physical family {fam} (nonheat_binding.nh_family)" if fam != led and fam != "BOOKKEEPING" else ""
        rows.append({"proc_id": pid, "canonical": r.get("canonical_name", ""), "ledger_family": led, "primary_family": fam,
                     "layer_scope": scope, "binder": binder, "form_candidate_class": form, "medium_code": med,
                     "secondary_family": sec, "ambiguity_flag": "YES" if rule else "NO", "ambiguity_rule": rule,
                     "family_override_note": note, "status": STATUS})
    return rows


def write_registry(path: Path, rows: Iterable[Mapping]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in COLUMNS})


def read_registry(path: Path | None = None, root: Path = ROOT) -> list[dict]:
    with open(path or root / REGISTRY, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def validate(rows: list[Mapping], root: Path = ROOT) -> list[str]:
    """Problems (empty list = valid): every PROC exactly once, one primary family from the closed list, every non-heat family
    inhabited, ambiguity rows have a rule and a different secondary family, the primary family of a non-heat PROC equals
    ``nh_family`` and the heat families equal the binder's HEAT set."""
    from culinarystate.simulation import condition_binding as CB
    from culinarystate.simulation import nonheat_binding as NB
    probs: list[str] = []
    procs = latest_proc(root)
    ids = [r["proc_id"] for r in rows]
    for pid in sorted(set(ids)):
        if ids.count(pid) != 1:
            probs.append(f"{pid}: {ids.count(pid)} rows")
    for pid in procs:
        if pid not in ids:
            probs.append(f"{pid}: missing")
    for pid in set(ids) - set(procs):
        probs.append(f"{pid}: not in the PROC ledger")
    base = type("B", (), {"family": {p: r.get("family") for p, r in procs.items()}})()
    nh = NB.NonHeatBinder(base, {})
    for r in rows:
        pid, fam = r["proc_id"], r["primary_family"]
        if fam not in PRIMARY_FAMILIES:
            probs.append(f"{pid}: primary family {fam!r} not in the closed list")
        if not r["form_candidate_class"]:
            probs.append(f"{pid}: no FORM candidate class")
        if r["ambiguity_flag"] == "YES":
            if not r["ambiguity_rule"] or not r["secondary_family"] or r["secondary_family"] == fam:
                probs.append(f"{pid}: ambiguity row needs a rule and a secondary family different from the primary")
            if r["secondary_family"] not in PRIMARY_FAMILIES:
                probs.append(f"{pid}: secondary family {r['secondary_family']!r} not in the closed list")
        elif r["ambiguity_rule"] or r["secondary_family"]:
            probs.append(f"{pid}: rule or secondary family without the ambiguity flag")
        nf = nh.nh_family(pid)
        if (nf or "") != (fam if fam in NONHEAT_FAMILIES else ""):
            probs.append(f"{pid}: primary {fam} but nh_family says {nf}")
        if (fam in HEAT_FAMILIES) != (r["ledger_family"] in CB.HEAT):
            probs.append(f"{pid}: heat family mismatch with condition_binding.HEAT")
    for f in NONHEAT_FAMILIES:
        if not any(r["primary_family"] == f for r in rows):
            probs.append(f"non-heat family {f} has no PROC")
    return probs
