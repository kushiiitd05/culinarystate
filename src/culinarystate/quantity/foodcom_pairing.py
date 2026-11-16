"""Food.com quantity / part pairing rules (S178, corpus lane). DRAFT_PENDING_H4, OPT-IN ONLY: nothing here is wired into
``recipes.corpus.iter_foodcom`` (owned elsewhere), whose positional pairing stays the frozen default.

Why: Food.com stores ``RecipeIngredientQuantities`` and ``RecipeIngredientParts`` as two separate lists. They have different
lengths in 78.0 % of recipes (407,536 of 522,517; ``reports/s178/corpus/foodcom_quantity_alignment_v1.json``), so pairing
by position puts a quantity on the wrong food after the first drop. The lists carry no unit and no link back to the source
line, so a correct pairing cannot be recovered with certainty.

Rules (``RULES``):

  POSITIONAL            the frozen behaviour of ``iter_foodcom`` (pad / truncate). Kept only for comparison; 78.0 % of
                        recipes are mispaired after at least one position.
  EQUAL_LENGTH_ONLY     pair by position only when the two lists have the same length; otherwise every part gets NO
                        quantity (UNKNOWN, never imputed). Proposed default. Same idea as the lot-state reader's
                        ``FOODCOM_QP_LENGTH_MISMATCH``. Equal length is necessary, not sufficient, for a correct pairing.
  ALIGN_MODEL           EXPERIMENTAL. Monotone alignment of the parts to the quantities (some quantities or parts may
                        be skipped) scored by a bucket model trained on the equal-length recipes (P(quantity bucket | part)),
                        keeping only pairs whose forward-backward posterior reaches a threshold. Validated ONLY by
                        simulation (drop k parts or k quantities from an equal-length recipe); the real mechanism that
                        produced the mismatch is not known, so this is evidence about the method, not about the corpus.

Counts-only users should call the functions with strings and keep only integer counts. No third-party text is stored here.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Sequence

PAIRING_VERSION = "S178_FOODCOM_PAIRING_V1_DRAFT"
RULES = ("POSITIONAL", "EQUAL_LENGTH_ONLY", "ALIGN_MODEL")
FS = "⁄"
BUCKETS = ("NONE", "UNPARSED", "LT1", "E1", "F1", "E2", "M4", "M8", "M16", "BIG")

STATUS_PAIRED = "PAIRED_EQUAL_LENGTH"
STATUS_UNKNOWN = "QUANTITY_UNKNOWN_LENGTH_MISMATCH"
STATUS_ALIGNED = "PAIRED_BY_ALIGNMENT"
STATUS_UNPAIRED = "QUANTITY_UNKNOWN_NOT_ALIGNED"

_NUM = re.compile(r"^\d+(?:\.\d+)?$")


# ---------------------------------------------------------------- quantity string -> value / bucket
def qty_low_value(q: str | None) -> float | None:
    """Lower bound of a Food.com quantity string ("1 1⁄2", "1⁄4", "2 -3", "1.5"); None when missing or unparsable."""
    if q is None:
        return None
    s = q.replace(FS, "/").replace("∕", "/").strip()
    if not s:
        return None
    s = re.split(r"\s*-\s*", s, maxsplit=1)[0].strip()
    try:
        total = 0.0
        for tok in s.split():
            if "/" in tok:
                a, b = tok.split("/")
                total += float(a) / float(b)
            elif _NUM.match(tok):
                total += float(tok)
            else:
                return None
        return total if s else None
    except (ValueError, ZeroDivisionError):
        return None


def bucket_of(q: str | None) -> str:
    """Coarse magnitude bucket of a quantity string (a feature, not a conversion)."""
    if q is None or not str(q).strip():
        return "NONE"
    v = qty_low_value(q)
    if v is None:
        return "UNPARSED"
    if v < 1:
        return "LT1"
    if v == 1:
        return "E1"
    if v < 2:
        return "F1"
    if v == 2:
        return "E2"
    if v <= 4:
        return "M4"
    if v <= 8:
        return "M8"
    if v <= 16:
        return "M16"
    return "BIG"


def part_keys(part: str | None) -> tuple[str, str]:
    """(phrase key, head key): lower-case text before the first comma; head = its last word, plural 's' stripped."""
    s = (part or "").lower().split(",", 1)[0]
    words = re.findall(r"[a-z][a-z'-]*", s)
    phrase = " ".join(words)
    head = words[-1] if words else ""
    if len(head) > 3 and head.endswith("s") and not head.endswith("ss"):
        head = head[:-1]
    return phrase, head


# ---------------------------------------------------------------- rules 1 and 2
def pair_positional(quantities: Sequence[str | None], parts: Sequence[str]) -> list[tuple[str | None, str, str]]:
    """The frozen ``iter_foodcom`` behaviour: quantity i with part i; missing quantity -> None; extra quantities dropped."""
    return [((quantities[i] if i < len(quantities) and quantities[i] else None), p, "POSITIONAL") for i, p in enumerate(parts)]


def pair_equal_length(quantities: Sequence[str | None], parts: Sequence[str]) -> list[tuple[str | None, str, str]]:
    """Proposed default: pair only when len(quantities) == len(parts); a null quantity stays None (source says nothing)."""
    if len(quantities) == len(parts):
        return [((q if q else None), p, STATUS_PAIRED) for q, p in zip(quantities, parts)]
    return [(None, p, STATUS_UNKNOWN) for p in parts]


# ---------------------------------------------------------------- rule 3 (experimental)
@dataclass
class AlignmentModel:
    """P(bucket | part) with phrase -> head -> global back-off, trained on equal-length recipes."""
    phrase: dict = field(default_factory=lambda: defaultdict(Counter))
    head: dict = field(default_factory=lambda: defaultdict(Counter))
    glob: Counter = field(default_factory=Counter)
    alpha: float = 2.0
    min_phrase: int = 20

    def add(self, part: str, q: str | None) -> None:
        b = bucket_of(q)
        ph, hd = part_keys(part)
        self.phrase[ph][b] += 1
        self.head[hd][b] += 1
        self.glob[b] += 1

    def prob(self, part: str, b: str) -> float:
        ph, hd = part_keys(part)
        gtot = sum(self.glob.values())
        pg = (self.glob[b] + 0.5) / (gtot + 0.5 * len(BUCKETS))
        h = self.head.get(hd)
        if h:
            n = sum(h.values())
            ph_head = (h[b] + self.alpha * pg) / (n + self.alpha)
        else:
            ph_head = pg
        p = self.phrase.get(ph)
        if p and sum(p.values()) >= self.min_phrase:
            n = sum(p.values())
            return (p[b] + self.alpha * ph_head) / (n + self.alpha)
        return ph_head


def _lse(a: float, b: float) -> float:
    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    m = max(a, b)
    return m + math.log(math.exp(a - m) + math.exp(b - m))


def alignment_posteriors(model: AlignmentModel, quantities: Sequence[str | None], parts: Sequence[str], *,
                         skip_part_cost: float = 3.0, skip_qty_cost: float = 3.0) -> list[list[float]]:
    """post[i][j] = posterior that part i is paired with quantity j under all monotone alignments.

    Weight of pairing i with j = P(bucket(q_j) | part_i); skipping a quantity costs exp(-skip_qty_cost), skipping a
    part exp(-skip_part_cost). The part's row sums to <= 1; the rest is the posterior that the part has no quantity.
    """
    m, n = len(parts), len(quantities)
    buckets = [bucket_of(q) for q in quantities]
    w = [[math.log(model.prob(parts[i], buckets[j])) for j in range(n)] for i in range(m)]
    NEG = -math.inf
    f = [[NEG] * (n + 1) for _ in range(m + 1)]        # f[i][j]: parts[:i] and quantities[:j] consumed
    f[0][0] = 0.0
    for i in range(m + 1):
        for j in range(n + 1):
            v = f[i][j]
            if i == 0 and j == 0:
                continue
            acc = NEG
            if i > 0 and j > 0 and f[i - 1][j - 1] > NEG:
                acc = _lse(acc, f[i - 1][j - 1] + w[i - 1][j - 1])
            if j > 0 and f[i][j - 1] > NEG:
                acc = _lse(acc, f[i][j - 1] - skip_qty_cost)
            if i > 0 and f[i - 1][j] > NEG:
                acc = _lse(acc, f[i - 1][j] - skip_part_cost)
            f[i][j] = acc
    b = [[NEG] * (n + 2) for _ in range(m + 2)]        # b[i][j]: parts[i:] and quantities[j:] still to consume
    b[m][n] = 0.0
    for i in range(m, -1, -1):
        for j in range(n, -1, -1):
            if i == m and j == n:
                continue
            acc = NEG
            if i < m and j < n and b[i + 1][j + 1] > NEG:
                acc = _lse(acc, w[i][j] + b[i + 1][j + 1])
            if j < n and b[i][j + 1] > NEG:
                acc = _lse(acc, -skip_qty_cost + b[i][j + 1])
            if i < m and b[i + 1][j] > NEG:
                acc = _lse(acc, -skip_part_cost + b[i + 1][j])
            b[i][j] = acc
    logz = f[m][n]
    post = [[0.0] * n for _ in range(m)]
    if logz == NEG:
        return post
    for i in range(m):
        for j in range(n):
            if f[i][j] > NEG and b[i + 1][j + 1] > NEG:
                post[i][j] = math.exp(f[i][j] + w[i][j] + b[i + 1][j + 1] - logz)
    return post


def align_pairs(model: AlignmentModel, quantities: Sequence[str | None], parts: Sequence[str], *, threshold: float = 0.9,
                skip_part_cost: float = 3.0, skip_qty_cost: float = 3.0) -> list[tuple[str | None, str, str]]:
    """EXPERIMENTAL rule: pair a part with a quantity only when the posterior is >= threshold; else no quantity (UNKNOWN)."""
    if not parts:
        return []
    if not quantities:
        return [(None, p, STATUS_UNPAIRED) for p in parts]
    post = alignment_posteriors(model, quantities, parts, skip_part_cost=skip_part_cost, skip_qty_cost=skip_qty_cost)
    out = []
    for i, p in enumerate(parts):
        j = max(range(len(quantities)), key=lambda jj: post[i][jj])
        if post[i][j] >= threshold and quantities[j]:
            out.append((quantities[j], p, STATUS_ALIGNED))
        else:
            out.append((None, p, STATUS_UNPAIRED))
    return out


def map_alignment_indices(model: AlignmentModel, quantities: Sequence[str | None], parts: Sequence[str], **kw) -> list[int | None]:
    """For evaluation: for each part, the quantity index with the highest posterior and the posterior (index, posterior)."""
    post = alignment_posteriors(model, quantities, parts, **kw)
    out = []
    for i in range(len(parts)):
        j = max(range(len(quantities)), key=lambda jj: post[i][jj]) if quantities else None
        out.append((j, post[i][j]) if j is not None else (None, 0.0))
    return out


class PairedLines(list):
    """The lines of ``pair_lines`` (a plain ``list`` of str, so it is a drop-in for ``iter_foodcom``'s lines) that also KEEPS
    the pairing status of every line (S178 FIX-ROUTER, SCI-B CORP-3): ``statuses`` (one per line, e.g.
    ``QUANTITY_UNKNOWN_LENGTH_MISMATCH``), ``length_mismatch`` (the two source lists differ in length) and ``rule``. A
    consumer can therefore tell "misaligned, quantity withheld" from "the source gives no quantity"."""

    def __init__(self, lines: Sequence[str], statuses: Sequence[str], *, length_mismatch: bool, rule: str) -> None:
        super().__init__(lines)
        if len(statuses) != len(lines):
            raise ValueError("one status per line")
        self.statuses = tuple(statuses)
        self.length_mismatch = bool(length_mismatch)
        self.rule = rule

    def with_status(self) -> list[tuple[str, str]]:
        return list(zip(self, self.statuses))


def pair_lines_with_status(quantities: Sequence[str | None], parts: Sequence[str], rule: str = "EQUAL_LENGTH_ONLY", *,
                           model: AlignmentModel | None = None, threshold: float = 0.9) -> list[tuple[str, str]]:
    """``(line, status)`` per part (S178 CORP-3); see ``pair_lines``."""
    return pair_lines(quantities, parts, rule, model=model, threshold=threshold).with_status()


def pair_lines(quantities: Sequence[str | None], parts: Sequence[str], rule: str = "EQUAL_LENGTH_ONLY", *,
               model: AlignmentModel | None = None, threshold: float = 0.9) -> PairedLines:
    """Lines as ``recipes.corpus.iter_foodcom`` builds them (``"<quantity> <part>"``, bare part when there is no quantity) under ``rule``.

    ``POSITIONAL`` reproduces the frozen behaviour exactly; ``EQUAL_LENGTH_ONLY`` is the proposed default; ``ALIGN_MODEL`` needs a trained
    ``model`` (experimental). Drop-in for a consumer that wants to opt in without touching ``corpus.py``. S178 (CORP-3): the
    result is a ``PairedLines`` list that keeps each line's status and the length-mismatch flag (equal to a plain list of
    the same lines).
    """
    if rule == "POSITIONAL":
        pairs = pair_positional(quantities, parts)
    elif rule == "EQUAL_LENGTH_ONLY":
        pairs = pair_equal_length(quantities, parts)
    elif rule == "ALIGN_MODEL":
        if model is None:
            raise ValueError("ALIGN_MODEL needs a trained AlignmentModel")
        pairs = align_pairs(model, quantities, parts, threshold=threshold)
    else:
        raise ValueError(f"unknown rule {rule!r}; expected one of {RULES}")
    return PairedLines([f"{q or ''} {p}".strip() for q, p, _ in pairs], [st for _, _, st in pairs],
                       length_mismatch=len(quantities) != len(parts), rule=rule)
