"""DRAFT_PENDING_30_0 -- Step 30 bake-off scaffold: model registry and paired cluster bootstrap.

Plan Step 30 (30.0 harness + pre-registration): every rung on identical folds, paired
comparisons with a cluster CI, and promotion only when the paired-cluster lower bound
exceeds a margin set BEFORE the run (delta_30 is PROPOSED_PILOT; nothing here sets it).

* ``ModelRegistry``: rungs must be names from the plan's Phase G ladder table (Steps 29-30;
  D8+ belong to Steps 32/33, D10/D11 are deferred). ``freeze()`` returns a manifest hash;
  no registration afterwards. The fit code is referenced by name, not hashed: binding code
  bytes is the pre-registration's job.
* ``evaluate``: fit each frozen model on the train role only, score the test role.
* ``paired_cluster_bootstrap``: delta per row = baseline loss - challenger loss (positive =
  challenger better); clusters are resampled with replacement. ``margin``, ``n_resamples``,
  ``confidence``, ``seed`` and ``weighting`` are keyword-only with NO default. Verdict
  ``LOWER_BOUND_ABOVE_MARGIN`` iff the percentile lower bound is strictly above ``margin``.
  With few clusters the research note (r_eval_splits Q5) prefers a cluster sign-flip
  permutation test; that choice, and its cluster cut-off, are not made here.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

from culinarystate.evaluation.splits import GroupSplit

STATUS = "DRAFT_PENDING_30_0"
LADDER_RUNGS = ("D0", "D1", "D2", "D3-legacy", "D4", "D5-HistGB",
                "D3-R", "D3-full", "D5-tuned", "D6", "D7a", "D7b", "D7d", "D7e")
WEIGHTINGS = ("CLUSTER", "ROW")
INTERVAL_RULE = "percentile: lower = sorted[floor(a/2*B)], upper = sorted[ceil((1-a/2)*B)-1], a = 1-confidence"
DELTA_DEFINITION = "baseline_loss - challenger_loss (positive = challenger better)"
LABELS = ("DIAGNOSTIC_ONLY",)

FitFn = Callable[[Sequence[Mapping[str, Any]]], Callable[[Mapping[str, Any]], float]]


class BakeoffRefused(RuntimeError):
    """The registry or comparison refuses; ``blockers`` lists every reason as ``CODE: detail``."""

    def __init__(self, blockers: Iterable[str]):
        self.blockers = list(blockers)
        super().__init__("bake-off refused: " + "; ".join(self.blockers))


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    rung: str
    description: str
    fit: FitFn


class ModelRegistry:
    """Append-then-freeze registry of the models compared in one bake-off."""

    def __init__(self) -> None:
        self._specs: dict[str, ModelSpec] = {}
        self._manifest: dict[str, Any] | None = None

    def register(self, spec: ModelSpec) -> None:
        blockers = []
        if self._manifest is not None:
            blockers.append("REGISTRY_FROZEN: no model may be added after freeze()")
        if not spec.model_id:
            blockers.append("MODEL_ID_MISSING: empty model id")
        elif spec.model_id in self._specs:
            blockers.append(f"MODEL_ID_DUPLICATE: {spec.model_id}")
        if spec.rung not in LADDER_RUNGS:
            blockers.append(f"RUNG_UNKNOWN: {spec.rung!r} is not a Step 29/30 ladder rung")
        if not callable(spec.fit):
            blockers.append("FIT_NOT_CALLABLE: spec.fit must be callable")
        if blockers:
            raise BakeoffRefused(blockers)
        self._specs[spec.model_id] = spec

    @property
    def frozen(self) -> bool:
        return self._manifest is not None

    def models(self) -> tuple[ModelSpec, ...]:
        return tuple(self._specs.values())

    def freeze(self) -> dict[str, Any]:
        if self._manifest is None:
            if not self._specs:
                raise BakeoffRefused(["REGISTRY_EMPTY: nothing to freeze"])
            models = [{"model_id": s.model_id, "rung": s.rung, "description": s.description,
                       "fit_ref": f"{getattr(s.fit, '__module__', '?')}.{getattr(s.fit, '__qualname__', '?')}"}
                      for s in self._specs.values()]
            digest = hashlib.sha256(json.dumps(models, sort_keys=True).encode("utf-8")).hexdigest()
            self._manifest = {"status": STATUS, "models": models, "sha256": digest}
        return dict(self._manifest)


def evaluate(registry: ModelRegistry, split: GroupSplit, rows: Sequence[Mapping[str, Any]], *, id_column: str,
             target: Callable[[Mapping[str, Any]], float], loss: Callable[[float, float], float],
             train_role: str, test_role: str) -> dict[str, dict[str, float]]:
    """model id -> {test row id -> loss}; each model is fitted on the train role only."""
    blockers = []
    if not registry.frozen:
        blockers.append("REGISTRY_NOT_FROZEN: call freeze() before evaluating")
    for role in (train_role, test_role):
        if role not in split.roles:
            blockers.append(f"ROLE_UNKNOWN: {role!r}")
    if train_role == test_role:
        blockers.append("ROLE_SAME: train and test roles must differ")
    if blockers:
        raise BakeoffRefused(blockers)
    by_id = {str(r.get(id_column)): r for r in rows}
    train = [by_id[i] for i in split.rows(train_role) if i in by_id]
    test = [by_id[i] for i in split.rows(test_role) if i in by_id]
    if not train or not test:
        raise BakeoffRefused(["ROLE_EMPTY: train or test role has no rows"])
    out: dict[str, dict[str, float]] = {}
    for spec in registry.models():
        predict = spec.fit(train)
        out[spec.model_id] = {str(r.get(id_column)): float(loss(target(r), predict(r))) for r in test}
    return out


@dataclass(frozen=True)
class PairedComparison:
    n_clusters: int
    n_rows: int
    estimate: float
    lower: float
    upper: float
    margin: float
    confidence: float
    n_resamples: int
    weighting: str
    seed_sha256: str
    verdict: str

    def as_record(self) -> dict[str, Any]:
        return {**asdict(self), "status": STATUS, "interval_rule": INTERVAL_RULE,
                "delta_definition": DELTA_DEFINITION, "labels": list(LABELS)}


def _is_real(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _statistic(sample: Sequence[tuple[float, int]], weighting: str) -> float:
    if weighting == "CLUSTER":
        return sum(s / n for s, n in sample) / len(sample)
    return sum(s for s, _ in sample) / sum(n for _, n in sample)


def paired_cluster_bootstrap(baseline_losses: Mapping[str, float], challenger_losses: Mapping[str, float],
                             clusters: Mapping[str, str], *, margin: float, n_resamples: int, confidence: float,
                             seed: str, weighting: str) -> PairedComparison:
    """Paired cluster-bootstrap CI of the mean loss gain; refuses with every blocker collected."""
    blockers: list[str] = []
    if not _is_real(margin):
        blockers.append("MARGIN_INVALID: a finite pre-registered margin is required (no default)")
    if not isinstance(n_resamples, int) or isinstance(n_resamples, bool) or n_resamples < 1:
        blockers.append("N_RESAMPLES_INVALID: a positive integer is required")
    if not _is_real(confidence) or not 0 < confidence < 1:
        blockers.append("CONFIDENCE_INVALID: a level strictly between 0 and 1 is required")
    if not isinstance(seed, str) or not seed:
        blockers.append("SEED_MISSING: a non-empty seed string is required")
    if weighting not in WEIGHTINGS:
        blockers.append(f"WEIGHTING_INVALID: {weighting!r} not in {WEIGHTINGS}")
    if set(baseline_losses) != set(challenger_losses):
        blockers.append("ROWS_NOT_PAIRED: baseline and challenger losses cover different rows")
    rows = sorted(set(baseline_losses) & set(challenger_losses))
    missing = [r for r in rows if not clusters.get(r)]
    if missing:
        blockers.append(f"CLUSTER_MISSING: {len(missing)} row(s) have no cluster")
    bad = [r for r in rows if not (_is_real(baseline_losses[r]) and _is_real(challenger_losses[r]))]
    if bad:
        blockers.append(f"LOSS_NOT_FINITE: {len(bad)} row(s)")
    acc: dict[str, list[float]] = {}
    if not missing and not bad:
        for r in rows:
            cell = acc.setdefault(str(clusters[r]), [0.0, 0])
            cell[0] += float(baseline_losses[r]) - float(challenger_losses[r])
            cell[1] += 1
        if len(acc) < 2:
            blockers.append(f"TOO_FEW_CLUSTERS: {len(acc)} cluster(s); a cluster bootstrap needs at least 2")
    if blockers:
        raise BakeoffRefused(blockers)
    cells = [(acc[c][0], int(acc[c][1])) for c in sorted(acc)]
    estimate = _statistic(cells, weighting)
    seed_sha = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    rng = random.Random(int(seed_sha, 16))
    k = len(cells)
    stats = sorted(_statistic([cells[rng.randrange(k)] for _ in range(k)], weighting) for _ in range(n_resamples))
    alpha = 1 - confidence
    lo = stats[min(n_resamples - 1, math.floor(alpha / 2 * n_resamples))]
    hi = stats[max(0, min(n_resamples - 1, math.ceil((1 - alpha / 2) * n_resamples) - 1))]
    verdict = "LOWER_BOUND_ABOVE_MARGIN" if lo > margin else "NOT_ABOVE_MARGIN"
    return PairedComparison(n_clusters=k, n_rows=len(rows), estimate=estimate, lower=lo, upper=hi,
                            margin=float(margin), confidence=float(confidence), n_resamples=n_resamples,
                            weighting=weighting, seed_sha256=seed_sha, verdict=verdict)
