"""Step 19 real-pilot gate and P1 draw (S154; AI engineering draft, PENDING_H5).

Turns the synthetic rehearsal into real-pilot tooling that STOPS at every human
prerequisite. ``check_prerequisites`` lists every missing fact with its owner;
``draw_p1`` refuses unless that list is empty. Nothing here supplies, guesses or
generates a nonce, signature, capacity, budget, H5 decision or method ruling,
and the start record is only ever read.

Draw specification (``DRAW_ALGORITHM_ID``; binds design section 4.5 / THR-19P-07,
-08 and the AI-review items PR09 / PM-06; must itself be bound in the signed
start record before use):

- frame_sha256 = SHA-256 of ``"<sha256(frame.csv bytes)>\\n<sha256(strata.csv bytes)>\\n"``
  (frame and text-strata files are two separate text-free CSVs).
- seed = first 8 bytes of SHA-256(UTF-8(frame_sha256 hex) || UTF-8(wave) || UTF-8(nonce)),
  plain concatenation without separators, as written in THR-19P-08.
- stable shuffle inside a cell = ascending SHA-256(seed || UTF-8(recipe_id)) hex,
  ties by recipe_id.
- cells in fixed order P1-1..P1-7; per cell take the first candidate whose group
  is unused, then the next two as ordered reserves; selected AND reserve groups
  are all marked used (no group appears twice anywhere in the wave).
- group key = split_group_id when nonblank, else the fallback group_id.
- a cell with fewer than 30 eligible rows STOPS the draw (CELL_UNDERFILLED):
  the design's source fall-through can break the signed quotas (PM-06), so
  it is a human decision, not applied automatically.

P2 (coverage-greedy, D19-10 open, tag-rule spec not yet written) is refused.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path

TOOL_VERSION = "STEP19_REAL_PILOT_TOOL_V1_DRAFT"
DRAW_ALGORITHM_ID = "STEP19_P1_DRAW_SHA256_RANK_V1_DRAFT"
P1_CELLS = (("P1-1", "baking", "FOODCOM", "MID"), ("P1-2", "drain_discard", "A1_BBC_GOOD_FOOD", "LOW"),
            ("P1-3", "indian", "WIKIBOOKS", "MID"), ("P1-4", "multi_component", "FOODCOM", "HIGH"),
            ("P1-5", "random", "A1_BBC_GOOD_FOOD", "MID"), ("P1-6", "reserve_split", "FOODCOM", "HIGH"),
            ("P1-7", "simple", "WIKIBOOKS", "LOW"))
MIN_ELIGIBLE_PER_CELL = 30
THRESHOLD_IDS = tuple(f"THR-19P-{i:02d}" for i in range(1, 36))
ANNOTATORS = ("Kush", "Parv")
PILOT_COLUMNS = ("reserve_split", "reserve_split_v2")
FRAME_COLUMNS = frozenset((
    "recipe_id", "source_family", "source_id", "usage_class", "n_ingredient_lines", "n_steps",
    "complexity_c", "complexity_tier", "stratum_simple", "stratum_indian", "stratum_random",
    "text_regex_strata_status", "split_group_id", "group_id", "group_basis", "group_size",
    "duplicate_group_id", "recipe_family_id", "dish_family_candidate_id"))
STRATA_COLUMNS = frozenset(("recipe_id", "baking", "drain_discard", "reserve_split", "reserve_split_v2",
                            "multi_component"))
MANIFEST_COLUMNS = ("wave", "cell_id", "stratum", "stratum_column", "source_family", "tier", "role", "recipe_id",
                    "group_key", "eligible_count", "seed_hex", "frame_sha256", "draw_algorithm", "tool_version")
_PROTECTED = (("ledgers",), ("data",), ("exports",), ("annotation", "gold"))
_DECISION = re.compile(r"^D-\d{3}$")


class PilotGateError(RuntimeError):
    """A human prerequisite is missing or an input is unsafe; nothing was drawn."""


@dataclass(frozen=True)
class Blocker:
    code: str
    owner: str
    detail: str


def _sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _positive(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0


def _nonblank(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _utc(value):
    if not _nonblank(value):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else None


def _iso_date(value) -> bool:
    if not _nonblank(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _decision_ids(root: Path) -> set[str]:
    try:
        text = (root / "DECISIONS.md").read_text(encoding="utf-8")
    except OSError:
        return set()
    return set(re.findall(r"^#{2,3} (D-\d{3})\b", text, re.M))


def _threshold_blockers(root: Path) -> list[Blocker]:
    path = root / "registry/preregistered_thresholds_v1.csv"
    try:
        rows = {r.get("threshold_id"): r for r in csv.DictReader(open(path, newline="", encoding="utf-8"))}
    except OSError:
        rows = {}
    missing = [t for t in THRESHOLD_IDS
               if not (t in rows and _nonblank(rows[t].get("signed_by")) and _nonblank(rows[t].get("signed_at"))
                       and not str(rows[t].get("registry_status", "")).startswith("DRAFT"))]
    if missing:
        return [Blocker("THRESHOLDS_NOT_SIGNED", "Kush+Parv",
                        f"{len(missing)} of {len(THRESHOLD_IDS)} THR-19P rows are absent from the registry or unsigned")]
    return []


def check_prerequisites(record_path: Path, *, root: Path, wave: str = "P1") -> list[Blocker]:
    """Every missing human prerequisite for drawing ``wave``; an empty list means ready."""
    record_path, root = Path(record_path), Path(root)
    out: list[Blocker] = []

    def block(code, owner, detail):
        out.append(Blocker(code, owner, detail))

    if wave != "P1":
        block("WAVE_P2_NOT_SUPPORTED", "Kush+Parv",
              "P2 needs the reviewed tag-rule spec, D19-10, a finished P1 and closed 07I-C labelling")
    try:
        rec = json.loads(record_path.read_text(encoding="utf-8"))
        if not isinstance(rec, dict):
            raise ValueError
    except (OSError, ValueError):
        return out + [Blocker("START_RECORD_UNREADABLE", "Kush+Parv", "start record missing or not a JSON object")]

    signers = {s.strip().lower() for s in rec.get("signers") or [] if _nonblank(s)}
    if rec.get("status") in (None, "UNSIGNED_TEMPLATE") or not signers or not _iso_date(rec.get("date")):
        block("START_RECORD_UNSIGNED", "Kush+Parv", "start record has no signers/date (UNSIGNED_TEMPLATE)")
    elif not {a.lower() for a in ANNOTATORS} <= signers:
        block("BOTH_ANNOTATOR_SIGNATURES_REQUIRED", "Kush+Parv",
              "both annotators must sign the pilot start; a single-signer override is not accepted here")

    design = record_path.parent / str(rec.get("document") or "")
    if not rec.get("document") or not design.is_file() or _sha_file(design) != str(rec.get("sha256", "")).lower():
        block("DESIGN_HASH_MISMATCH", "Kush+Parv", "pilot design bytes differ from the start record hash")
    for entry in rec.get("bound_files") or []:
        target = record_path.parent / str(entry.get("path") or "")
        if not target.is_file() or _sha_file(target) != str(entry.get("sha256", "")).lower():
            block("BOUND_FILE_HASH_MISMATCH", "Kush+Parv", f"bound file changed or missing: {entry.get('path')}")

    auth = rec.get("human_start_authorization")
    if not isinstance(auth, dict) or not _nonblank(auth.get("decided_by")) or not _DECISION.match(str(auth.get("decision_id", ""))):
        block("H5_START_AUTHORIZATION_MISSING", "Kush", "no H5 start decision (decided_by + DECISIONS id) recorded")
    else:
        if auth["decision_id"] not in _decision_ids(root):
            block("H5_DECISION_NOT_RECORDED", "Kush", f"{auth['decision_id']} is not a DECISIONS.md entry")
        if wave not in (auth.get("waves") or []):
            block("H5_WAVE_NOT_AUTHORISED", "Kush", f"H5 decision does not cover wave {wave}")

    nonce = rec.get("pre_frame_nonce")
    if not _nonblank(nonce):
        block("NONCE_MISSING", "Kush", "pre-frame nonce absent; the agent never chooses the seed")
    else:
        if rec.get("nonce_supplier") != "Kush":
            block("NONCE_SUPPLIER_NOT_KUSH", "Kush", "design 4.5: the nonce is written by Kush")
        if str(rec.get("nonce_commitment", "")).lower() != hashlib.sha256(nonce.encode("utf-8")).hexdigest():
            block("NONCE_COMMITMENT_MISMATCH", "Kush", "nonce_commitment is not SHA-256 of the nonce")
        if _utc(rec.get("nonce_committed_at")) is None:
            block("NONCE_COMMITTED_AT_MISSING", "Kush", "timezone-aware nonce commitment time required")

    for field, code in (("weekly_capacity_hours", "CAPACITY_MISSING"), ("per_annotator_budget_B_h", "BUDGET_MISSING")):
        values = rec.get(field) or {}
        absent = [a for a in ANNOTATORS if not _positive(values.get(a))]
        if absent:
            block(code, "Kush" if code == "CAPACITY_MISSING" else "Kush+Parv",
                  f"{field} missing or non-positive for {', '.join(absent)}")

    out.extend(_threshold_blockers(root))
    if not _nonblank(rec.get("selected_instrument")):
        block("INSTRUMENT_NOT_SELECTED", "Kush+Parv", "measurement instrument version not selected")
    if rec.get("pilot_column_confirmation") != "CONFIRMED_BY_KUSH" or rec.get("pilot_column_parv_choice") not in PILOT_COLUMNS:
        block("PILOT_COLUMN_NOT_CONFIRMED", "Kush", "reserve_split column choice not confirmed by Kush")
    amend = rec.get("methodological_amendments")
    if not (isinstance(amend, dict) and amend.get("status") == "RESOLVED"
            and amend.get("decision_id") in _decision_ids(root)):
        block("METHOD_AMENDMENTS_UNRESOLVED", "Kush+Parv+expert",
              "AI methods/readiness recommendations (PM-01..12, PR01..10) need a recorded human ruling")
    if rec.get("draw_algorithm") != DRAW_ALGORITHM_ID:
        block("DRAW_SPEC_NOT_BOUND", "Kush+Parv", f"signed record must bind draw algorithm {DRAW_ALGORITHM_ID}")
    if rec.get("real_draw_performed") is not False:
        block("ALREADY_DRAWN", "Kush", "record says a real draw already happened (or the flag is absent)")
    return out


def _read_csv(path: Path, allowed: frozenset, required: set) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = set(reader.fieldnames or [])
        if not cols <= allowed or not required <= cols:
            raise PilotGateError(f"FRAME_COLUMNS_NOT_ALLOWED: {Path(path).name} must be text-free allowlisted columns")
        return list(reader)


def _guard_out(out_dir: Path, root: Path) -> None:
    try:
        parts = Path(out_dir).resolve().relative_to(Path(root).resolve()).parts
    except ValueError:
        return
    if any(parts[:len(p)] == p for p in _PROTECTED):
        raise PilotGateError("PROTECTED_OUTPUT: manifests never go into ledgers/, data/, exports/ or annotation/gold/")


def draw_p1(record_path: Path, frame_csv: Path, strata_csv: Path, *, out_dir: Path, root: Path) -> dict:
    """Draw P1 per the bound specification, or raise PilotGateError naming every blocker."""
    blockers = check_prerequisites(record_path, root=root, wave="P1")
    if blockers:
        raise PilotGateError("PREREQUISITES_MISSING: " + ", ".join(b.code for b in blockers))
    _guard_out(out_dir, root)
    out_dir = Path(out_dir)
    manifest = out_dir / "manifest_P1.csv"
    if manifest.exists() or (out_dir / "manifest_P1.csv.sha256").exists():
        raise PilotGateError("MANIFEST_EXISTS: P1 was already drawn; no redraw")
    rec = json.loads(Path(record_path).read_text(encoding="utf-8"))
    committed = _utc(rec["nonce_committed_at"])
    for path in (frame_csv, strata_csv):
        built = datetime.fromtimestamp(os.stat(path).st_mtime, tz=timezone.utc)
        if built < committed:
            raise PilotGateError(f"FRAME_PREDATES_NONCE_COMMITMENT: {Path(path).name} was written before the nonce")
    frame = _read_csv(frame_csv, FRAME_COLUMNS, {"recipe_id", "source_family", "complexity_tier", "group_id",
                                                 "split_group_id", "stratum_simple", "stratum_indian", "stratum_random"})
    strata = {r["recipe_id"]: r for r in _read_csv(strata_csv, STRATA_COLUMNS, set(STRATA_COLUMNS))}
    if len({r["recipe_id"] for r in frame}) != len(frame):
        raise PilotGateError("FRAME_DUPLICATE_RECIPE_ID")
    frame_sha = hashlib.sha256(f"{_sha_file(frame_csv)}\n{_sha_file(strata_csv)}\n".encode()).hexdigest()
    seed = hashlib.sha256(frame_sha.encode() + b"P1" + rec["pre_frame_nonce"].encode("utf-8")).digest()[:8]
    pilot_col = rec["pilot_column_parv_choice"]

    def tagged(row, stratum):
        if stratum in {"simple", "indian", "random"}:
            return row.get(f"stratum_{stratum}") == "Y"
        column = pilot_col if stratum == "reserve_split" else stratum
        return strata.get(row["recipe_id"], {}).get(column) == "Y"

    used, rows = set(), []
    for cell, stratum, source, tier in P1_CELLS:
        eligible = [r for r in frame if r["source_family"] == source and r["complexity_tier"] == tier and tagged(r, stratum)]
        if len(eligible) < MIN_ELIGIBLE_PER_CELL:
            raise PilotGateError(f"CELL_UNDERFILLED: {cell} has {len(eligible)} < {MIN_ELIGIBLE_PER_CELL} eligible; "
                                 "fall-through would change signed quotas and needs a human decision")
        ranked = sorted(eligible, key=lambda r: (hashlib.sha256(seed + r["recipe_id"].encode()).hexdigest(), r["recipe_id"]))
        picked = []
        for r in ranked:
            key = r["split_group_id"].strip() or r["group_id"]
            if key in used:
                continue
            used.add(key)
            picked.append((r, key))
            if len(picked) == 3:
                break
        if len(picked) < 3:
            raise PilotGateError(f"CELL_GROUPS_EXHAUSTED: {cell} lacks three distinct unused groups")
        for role, (r, key) in zip(("PRIMARY", "RESERVE_1", "RESERVE_2"), picked):
            rows.append({"wave": "P1", "cell_id": cell, "stratum": stratum,
                         "stratum_column": pilot_col if stratum == "reserve_split" else stratum,
                         "source_family": source, "tier": tier, "role": role, "recipe_id": r["recipe_id"],
                         "group_key": key, "eligible_count": len(eligible), "seed_hex": seed.hex(),
                         "frame_sha256": frame_sha, "draw_algorithm": DRAW_ALGORITHM_ID, "tool_version": TOOL_VERSION})
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(manifest, "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    with open(out_dir / "manifest_P1.csv.sha256", "x", encoding="utf-8") as fh:
        fh.write(f"{_sha_file(manifest)}  manifest_P1.csv\n")
    return {"rows": rows, "frame_sha256": frame_sha, "seed_hex": seed.hex(), "manifest": str(manifest)}


def blockers_as_json(blockers) -> list[dict]:
    return [asdict(b) for b in blockers]
