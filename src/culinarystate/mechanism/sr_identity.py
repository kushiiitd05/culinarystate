"""ING -> SR Legacy identity for the router's target-presence screen (S177, SCIFIX-ROUTER; consolidation review §5.3).
AI_DRAFTED, NON_CITABLE, DEMO_ONLY.

The identity of record is the Mac's curated registry ``registry/ing_sr_defaults_v1.csv`` (490 terms, every row AGENT_PROPOSED
/ UNVERIFIED), read through the read-only API of ``composition.ing_sr_match`` (``load_registry``, ``normalise``); nothing in
``composition/`` is copied or edited. The old lexical match file ``registry/ing_sr_legacy_match_draft_v1.csv`` (lotstate era)
is demoted to alternates and a fallback that is capped at MEDIUM, so it can never support an ABSENT claim on its own.

Registry kind -> candidates handed to ``evidence_gates.TargetPresenceScreen`` (``(fdc_id, band, score)``, rank 1 first):

  DIRECT, UK_US   (fdc, HIGH, 1)                                  alone; may support ABSENT
  DEFAULT_FORM    (fdc, HIGH, 1) + the legacy file's rank 1-3     the registry default is one UK / generic form, so every
                  foods for that ING as LOW alternates at score   other form must be known and below the floor too: ABSENT
                  1 (inside any identity margin)                  only if EVERY form is
  APPROX          (fdc, MEDIUM, 1)                                PRESENT only, never ABSENT
  NO_SR_EQUIVALENT, NOT_A_FOOD, AMBIGUOUS   none                  unknown identity (no fallback: the registry says no)
  term not in the registry   the legacy file's rank 1-3 with a HIGH rank 1 capped to MEDIUM   PRESENT only, never ABSENT

An ING is looked up by the normalised canonical name, then by its ACTIVE English aliases (only when they all agree on one
registry food). The ING category is the latest ACTIVE ING ledger row's ``category``; the SR food group is the rank-1
candidate's ``food_category`` in SR Legacy. Values are read as exact decimals from SR ``food_nutrient.csv`` (an SR food with
no row is UNKNOWN, never 0), with their SR derivation code and data-point count (S178 R4: SR values are analytical,
imputed, calculated or assumed; only analytical ones may support an ABSENT claim). The shipped derived table (``tools/build_target_content_table.py``) is written from this
module, so the demo needs no ``data/raw`` at run time.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Mapping

from culinarystate.composition import ing_sr_match as M
from culinarystate.composition.sr_legacy import NUTRIENTS as COMPOSITION_NUTRIENTS
from culinarystate.mechanism import evidence_gates as EG

ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = ROOT / "registry" / "ing_sr_defaults_v1.csv"
ING_LEDGER = ROOT / "ledgers" / "data" / "ING.jsonl"
ALIAS_LEDGER = ROOT / "ledgers" / "data" / "ALIAS.jsonl"
IDENTITY_SOURCE = "ing_sr_defaults_v1|legacy_match_alternates"     # code-like: it is written into counts-only reports
LEGACY_SOURCE = "legacy_match_only"
KIND_FALLBACK = "LEGACY_FALLBACK"
MAPPED_BAND = {"DIRECT": "HIGH", "UK_US": "HIGH", "DEFAULT_FORM": "HIGH", "APPROX": "MEDIUM"}
ANCHOR_SCORE = Fraction(1)
SR_DIRNAME = "FoodData_Central_sr_legacy_food_csv_2018-04"


# ----------------------------------------------------------------------------- SR nutrient keys (the gate's names)
def _split(name: str) -> tuple[str, str]:
    base, _, unit = name.rpartition("_")
    return base, unit


# gate key ("vitamin_c") -> (SR nutrient ids in preference order, unit), derived from the composition layer's roster
# ("vitamin_c_mg" = 1162), so the gate and the Mac's lot layer share one nutrient list
NUTRIENT_IDS: dict[str, tuple[tuple[int, ...], str]] = {
    _split(n)[0]: ((nid,), _split(n)[1]) for n, nid in COMPOSITION_NUTRIENTS.items()}
NUTRIENT_UNITS = {k: v[1] for k, v in NUTRIENT_IDS.items()}


def default_dir(root: Path = ROOT) -> Path:
    base = Path(root) / "data" / "raw" / "fdc" / "sr_legacy"
    cand = base / SR_DIRNAME
    return cand if cand.exists() else next(base.glob("FoodData_Central_sr_legacy_food_csv_*"))


# ----------------------------------------------------------------------------- ledgers and SR files (read only)
def _latest(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with Path(path).open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                if r["id"] not in out or r["version"] > out[r["id"]]["version"]:
                    out[r["id"]] = r
    return out


def read_ing(path: Path = ING_LEDGER) -> dict[str, tuple[str, str]]:
    """ACTIVE ING id -> (canonical name, category or '') from the latest version of each row."""
    return {i: (r["canonical_name"], r.get("category") or "") for i, r in _latest(path).items()
            if r.get("status") == "ACTIVE"}


def read_aliases(path: Path = ALIAS_LEDGER) -> dict[str, tuple[str, ...]]:
    """ACTIVE English alias surface (normalised) per ING id; ambiguous aliases (no single ING) are ignored."""
    out: dict[str, set] = {}
    for r in _latest(path).values():
        if r.get("status") == "ACTIVE" and r.get("language") == "en" and r.get("ingredient_id"):
            out.setdefault(r["ingredient_id"], set()).add(r.get("normalized") or r.get("surface") or "")
    return {k: tuple(sorted(v)) for k, v in out.items()}


def sr_food_groups(sr_dir: Path, fdc_ids: Iterable[int]) -> dict[int, str]:
    """fdc_id -> SR food group (``food_category.csv`` description), for the wanted foods; absent when SR has no row."""
    want = set(fdc_ids)
    d = Path(sr_dir)
    with (d / "food_category.csv").open(newline="", encoding="utf-8") as fh:
        cat = {r["id"]: r["description"] for r in csv.DictReader(fh)}
    out: dict[int, str] = {}
    with (d / "food.csv").open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            f = int(r["fdc_id"])
            if f in want and r["food_category_id"] in cat:
                out[f] = cat[r["food_category_id"]]
    return out


def sr_descriptions(sr_dir: Path, fdc_ids: Iterable[int]) -> dict[int, str]:
    """fdc_id -> SR description (public domain), for the human review lists."""
    want = set(fdc_ids)
    with (Path(sr_dir) / "food.csv").open(newline="", encoding="utf-8") as fh:
        return {int(r["fdc_id"]): r["description"] for r in csv.DictReader(fh) if int(r["fdc_id"]) in want}


# ----------------------------------------------------------------------------- identity
@dataclass(frozen=True)
class Identity:
    cands: Mapping[str, tuple[tuple[int, str, Fraction], ...]]      # ING id -> candidates, rank 1 first
    categories: Mapping[str, tuple[str, str]]                       # ING id -> (ING category, SR food group of rank 1)
    kinds: Mapping[str, str]                                        # ING id -> registry kind | LEGACY_FALLBACK
    diagnostics: Mapping[str, int] = field(default_factory=dict)    # counts only


def _legacy_rows(match_path: Path) -> dict[str, list[tuple[int, str, Fraction]]]:
    """The legacy match file's rank 1-3 foods per ING, any band, in rank order (the file is an alternate source)."""
    out: dict[str, list[tuple[int, str, Fraction]]] = {}
    for ing, rs in EG._read_match_rows(match_path).items():
        out[ing] = [(int(r["fdc_id"]), r["confidence_band"], Fraction(r["score"]))
                    for r in sorted(rs, key=lambda r: int(r["rank"]))]
    return out


def _registry_entry(registry: Mapping, name: str, aliases: Iterable[str]) -> M.RegistryEntry | None:
    """Canonical name first; else the ACTIVE aliases, only when every alias that hits the registry gives the same entry."""
    e = registry.get(M.normalise(name))
    if e is not None:
        return e
    hits = {registry[k] for a in aliases if (k := M.normalise(a)) in registry}
    return next(iter(hits)) if len(hits) == 1 else None


def build_identity(*, root: Path = ROOT, sr_dir: Path | None = None, registry_path: Path | None = None,
                   ing_path: Path | None = None, alias_path: Path | None = None,
                   match_path: Path | None = None) -> Identity:
    """Candidates, categories and registry kinds for every ACTIVE ING that has a usable identity (see module docstring)."""
    root = Path(root)
    registry = M.load_registry(registry_path or REGISTRY_PATH)
    ing = read_ing(ing_path or ING_LEDGER)
    aliases = read_aliases(alias_path or ALIAS_LEDGER)
    legacy = _legacy_rows(match_path or EG.MATCH_PATH)
    cands: dict[str, tuple] = {}
    kinds: dict[str, str] = {}
    diag: Counter = Counter()
    for ing_id in sorted(ing):
        e = _registry_entry(registry, ing[ing_id][0], aliases.get(ing_id, ()))
        alts = [(f, "LOW", ANCHOR_SCORE) for f, _, _ in legacy.get(ing_id, ())]
        if e is not None:
            diag[f"registry_{e.kind}"] += 1
            if e.kind not in MAPPED_BAND:
                continue                                                  # NO_SR_EQUIVALENT / NOT_A_FOOD / AMBIGUOUS
            anchor = (e.fdc_id, MAPPED_BAND[e.kind], ANCHOR_SCORE)
            rest = [a for a in alts if a[0] != e.fdc_id] if e.kind == "DEFAULT_FORM" else []
            seen: set = set()
            cands[ing_id] = tuple(c for c in (anchor, *rest) if not (c[0] in seen or seen.add(c[0])))
            kinds[ing_id] = e.kind
        else:
            rows = legacy.get(ing_id)
            if not rows or rows[0][1] not in EG.USABLE_BANDS:
                diag["legacy_no_usable_rank1"] += 1
                continue
            capped = [(f, "MEDIUM" if band == "HIGH" else band, sc) for f, band, sc in rows]   # never HIGH from here
            cands[ing_id], kinds[ing_id] = tuple(capped), KIND_FALLBACK
            diag["legacy_fallback"] += 1
    sr_dir = Path(sr_dir) if sr_dir else default_dir(root)
    groups = sr_food_groups(sr_dir, {c[0][0] for c in cands.values()})
    cats = {i: (ing[i][1], groups.get(cs[0][0], "")) for i, cs in cands.items()}
    return Identity(cands, cats, kinds, dict(sorted(diag.items())))


def table_rows(identity: Identity, values: Mapping[tuple[int, str], Fraction], keys: Iterable[str],
               basis: Mapping[tuple[int, str], tuple[str, int]] | None = None) -> list[dict[str, str]]:
    """The derived content table's rows: ``evidence_gates.build_table_rows`` plus the identity source and registry kind.
    S178 (R4): ``basis`` ((fdc, key) -> (SR derivation code, data points), ``evidence_gates.read_sr_basis``) fills the
    ``sr_derivation_code`` / ``sr_data_points`` columns."""
    rows = EG.build_table_rows(identity.cands, values, keys, identity.categories, basis)
    for r in rows:
        r["identity_source"] = IDENTITY_SOURCE
        r["registry_kind"] = identity.kinds[r["ing_id"]]
    return rows
