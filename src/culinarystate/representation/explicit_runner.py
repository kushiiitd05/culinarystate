"""Step 35 explicit-baseline runner entry, bound to the 35.0 v2 package (G35-PRE, THR-35P-01).

Every explicit-baseline run (35a-35e) must enter through ``run_explicit_baseline``. The
entry is pinned: it always checks ``PACKAGE_DOCUMENT`` against ``SIGNED_RECORD`` with
``prereg_guard.require_signed_prereg`` and the task's ``required_inputs`` as required bound
files; callers cannot substitute another document or record. It refuses (raises
``PreregNotSigned``) unless that record carries two distinct signers (or a written
single-signer override), an ISO date, the current document sha256 and the current sha256
of every required input. On top of the guard, each signer must name exactly one of Kush
or Parv and no AI worker/agent label (``ksh``/``prv`` are agents); both must sign unless
the record carries a single-signer override (review R2). This is an engineering control,
not a cryptographic signature: it stops accidental or agent "signing", not forgery.

Only an UNSIGNED template exists (``UNSIGNED_RECORD``, built by ``build_unsigned_record``).
This module never signs. ``MAC_ONLY_INPUTS`` are recipe files absent from the cloud
container; the 35b/35c/35d entries stay refused until a record binding them is signed.
No scoring code is here: the ``runner`` callable receives an ``Authorisation`` and its
code must itself be one of the bound inputs (a new or changed scorer = a new record).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar

from culinarystate.representation.prereg_guard import PreregNotSigned, require_signed_prereg, sign_record_template

T = TypeVar("T")

PACKAGE_DOCUMENT = "reports/step35/preregistration_35_0_v2_draft.md"
UNSIGNED_RECORD = "reports/step35/preregistration_35_0_v2_package.sha256.UNSIGNED.json"
SIGNED_RECORD = "reports/step35/preregistration_35_0_v2_package.sha256.SIGNED.json"
TASKS = ("35a", "35b", "35c", "35d", "35e")

_REP = "src/culinarystate/representation/"
COMMON_INPUTS: tuple[str, ...] = (
    "reports/step35/preregistration_35_0_v1_draft.md",
    "reports/step35/35_0_v2_threshold_rows.csv",
    "reports/step35/35_0_parv_review_DRAFT.md",
    "reports/review/protocol_review_addendum_DRAFT.md",
    _REP + "prereg_guard.py",
    _REP + "explicit_runner.py",
)
_MENTIONS = "ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet"
_RECIPE_BASE = "ledgers/recipe_base/recipe_base_v1.parquet"
_FIREWALL = "ledgers/recipe_identity/gold_firewall_v1.parquet"
_SPLIT_GROUPS = "ledgers/recipe_identity_v2/recipe_split_groups_v1.parquet"
_USAGE = "registry/recipe_source_usage_registry_v1.csv"
_RECIPE = (_REP + "recipe_rungs.py", _SPLIT_GROUPS, _USAGE, _MENTIONS, _RECIPE_BASE, _FIREWALL)
_CUISINE = (
    _REP + "cuisine_rungs.py",
    "registry/cuisine/cuisine_lookup_v1_DRAFT.csv",
    "registry/cuisine/foodcom_tag_cuisine_map_v1_DRAFT.csv",
    "registry/cuisine/explicit_cuisine_labels_v1.csv",
    "registry/cuisine/foodcom_tag_census_v1.csv",
    "tools/step35_foodcom_tag_census.py",
)
TASK_INPUTS: dict[str, tuple[str, ...]] = {
    "35a": ("ledgers/data/MOL.jsonl", "ledgers/data/KGE.jsonl"),
    "35b": ("ledgers/data/MOL.jsonl", "ledgers/data/IMAP.jsonl", "ledgers/data/ING.jsonl",
            "ledgers/data/KGE.jsonl") + _RECIPE,
    "35c": ("ledgers/data/ING.jsonl",) + _RECIPE,
    "35d": ("ledgers/data/ING.jsonl",) + _RECIPE + _CUISINE,
    "35e": (_REP + "similarity_registry.py", "registry/ssot15_similarity_registry.csv"),
}
MAC_ONLY_INPUTS: tuple[str, ...] = (_MENTIONS, _RECIPE_BASE, _FIREWALL)
HUMAN_SIGNERS = ("kush", "parv")
_AI_LABEL = re.compile(r"\b(ksh|prv|claude|anthropic|agent|ai|assistant|bot|gpt)\b", re.I)


@dataclass(frozen=True)
class Authorisation:
    """Proof that the guard passed for one task; log ``prereg_sha256`` into every result."""
    task: str
    prereg_sha256: str
    record: str
    required_files: tuple[str, ...]


def required_inputs(task: str) -> tuple[str, ...]:
    """Repository-relative files that must be bound in the signed record for ``task``."""
    if task not in TASK_INPUTS:
        raise ValueError(f"unknown Step 35 explicit task {task!r}; expected one of {TASKS}")
    return tuple(dict.fromkeys(COMMON_INPUTS + TASK_INPUTS[task]))


def package_inputs() -> tuple[str, ...]:
    """Every input of every task (sorted, unique): the full bound set of the v2 package."""
    return tuple(sorted({p for t in TASKS for p in required_inputs(t)}))


def build_unsigned_record(root: Path | str) -> dict[str, Any]:
    """UNSIGNED template for the v2 package binding every input present under ``root``.

    Absent inputs (``MAC_ONLY_INPUTS`` in the cloud container) are listed, never hashed.
    """
    base = Path(root)
    present = [p for p in package_inputs() if (base / p).is_file()]
    rec = sign_record_template(base / PACKAGE_DOCUMENT, bound_files=[base / p for p in present])
    rec["not_bound_absent_here"] = [p for p in package_inputs() if p not in present]
    return rec


def check_signer_identity(record: dict[str, Any]) -> None:
    """Each signer names exactly one of Kush/Parv and no AI label; both sign unless overridden."""
    who: list[str] = []
    for name in record.get("signers") or []:
        if not isinstance(name, str) or _AI_LABEL.search(name):
            raise PreregNotSigned(f"signer {name!r} is an AI worker or agent label, not a human signature")
        found = [h for h in HUMAN_SIGNERS if re.search(rf"\b{h}\b", name, re.I)]
        if len(found) != 1:
            raise PreregNotSigned(f"signer {name!r} must name exactly one of Kush or Parv")
        who.append(found[0])
    if len(who) != len(set(who)):
        raise PreregNotSigned("each human signer may appear once (Kush and Parv sign separately)")
    if set(who) != set(HUMAN_SIGNERS) and not record.get("single_signer_override"):
        raise PreregNotSigned("both Kush and Parv must be signers, or a single_signer_override is required")


def authorise_explicit_run(task: str, *, root: Path | str) -> Authorisation:
    """Run the G35-PRE guard on the pinned v2 package; raises PreregNotSigned if not signed."""
    required = required_inputs(task)
    base = Path(root)
    digest = require_signed_prereg(base / PACKAGE_DOCUMENT, base / SIGNED_RECORD,
                                   required_files=[base / p for p in required])
    check_signer_identity(json.loads((base / SIGNED_RECORD).read_text(encoding="utf-8")))
    return Authorisation(task, digest, SIGNED_RECORD, required)


def run_explicit_baseline(task: str, runner: Callable[[Authorisation], T], *, root: Path | str) -> T:
    """The only entry for explicit-baseline runs: guard first, then ``runner(authorisation)``."""
    return runner(authorise_explicit_run(task, root=root))
