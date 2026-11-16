"""Independent H3 scorer: claim extraction from the answer text + EVD-id lookup (S178; REV-B F-12, G-07/G-08;
consensus T8-C12-R1; SSOT v16 draft 287.3). DRAFT.

Why. B7 is built by ``generation.enforce.enforce``, which deletes the sentences that ``generation.claims.check_claims``
flags, and the S173 H3 scores UCR with the same ``check_claims``: UCR(B7) = 0 by construction. This module is a second
scorer on a separate code path. It shares no code with ``generation.claims`` or ``generation.enforce`` (a unit test
fails if it imports either) and it does not take the retrieval packet as the truth:

- Claims are extracted from the answer text with its own scanner: percentages, ranges, 0.x/1.x fractions, loss
  phrasing ("loses 20 %" means retention 0.80), and directional claims (decrease / increase / no change).
- A number is bound to the citation group that follows it (else the nearest one before it) inside its sentence, not
  to "any id in the sentence".
- Cited ids are looked up in the EVD ledger rows themselves (``evd`` mapping id -> row). An id that does not exist is
  NONEXISTENT_ID; an existing id the packet did not contain is only flagged (``outside_packet_ids``).
- A cited row supports a number only if its value matches AND, when the question's cell is known, its target,
  process and ingredient match the question (EXACT, or SIMILAR for a parent / aggregate row). A value inside the
  tolerance of some unrelated row is WRONG_CELL, not support (SSOT 287.3 item 4).

Coverage is reported with UCR: UCR = 0 with no claim made is not a good answer. ``summarize_rung`` returns UCR,
selective risk (questions with a claim that carry an unsupported one, Clopper-Pearson), coverage on answerable
questions, false abstention, abstention on ABSTAIN gold and numeric claims made on ABSTAIN gold. The gating test is the
exact sign test on questions where one rung has an unsupported claim and the other none.

The tolerance is a named constant with the same value as the S173 checker for comparability (0.03 on the fraction
scale); it is a scoring convention, not a measured quantity, and a pre-registration may set another.

S178 FIX-EVAL (SCI-B E2-E4): ``compare_rungs`` derives the significance floor from the exact test for the stated sidedness
(one-sided 5, two-sided 6 at alpha 0.05) and returns both flags; ingredient-name matching uses token boundaries ("pea" does
not match "Peanuts"); a value match whose cell was not checked (no ``cell``) is CELL_NOT_CHECKED, never SUPPORTED, is counted
separately by ``score_answer`` / ``summarize_rung`` and sets the question aside in ``compare_rungs``; ``require_cell=True``
(for the D5 path) refuses a missing cell.
"""
from __future__ import annotations

import math
import re
from typing import Iterable, Mapping, Sequence

from culinarystate.evaluation.paired_stats import mcnemar_exact

VERSION = "h3_independent@0.2"
VALUE_TOL = 0.03
EVD_ID = re.compile(r"EVD-\d{6}(?!\d)")
ANSWERABLE = ("ANSWER", "ANSWER_SIMILAR_ONLY", "COMPARE")
RELEVANCE_ORDER = {"EXACT": 2, "SIMILAR": 1}
VERDICTS = ("SUPPORTED", "UNCITED", "NONEXISTENT_ID", "ROW_NO_VALUE", "VALUE_MISMATCH", "WRONG_CELL", "CELL_NOT_CHECKED")
ALPHA = 0.05
SIDEDNESS = ("one-sided", "two-sided")

# ------------------------------------------------------------------ claim extraction

_SENT = re.compile(r"(?<=[.!?])\s+|\n+")
_FRAGMENT_JUNK = re.compile(r"EVD-\d{6}(?!\d)|[\s\[\](),;.:\-]")
_NUM = re.compile(
    r"(?P<range>(?P<lo>\d+(?:\.\d+)?)\s*(?:%|percent|per\s?cent)?\s*(?:-|–|—|to|and)\s*"
    r"(?P<hi>\d+(?:\.\d+)?)\s*(?:%|percent|per\s?cent))"
    r"|(?P<pct>(?P<pv>\d+(?:\.\d+)?)\s*(?:%|percent|per\s?cent))"
    r"|(?P<dec>(?<![\w.])(?P<dv>[01]?\.\d+)(?![\w%.]))", re.I)
_NOT_A_FRACTION = re.compile(r"^\s*(?:min|minute|hour|hr|sec|day|week|°|degree|cup|tbsp|tsp|tablespoon|teaspoon|gram|g\b|kg|"
                             r"mg|ml|l\b|oz|lb|inch|cm|mm|step|row|source|sample|stud|fold|time|x\b)", re.I)
_LOSS_BEFORE = re.compile(r"(?:lose|loses|losing|lost|loss(?:es)?|reduc\w*|decreas\w*|drop\w*|declin\w*|degrad\w*|destroy\w*|"
                          r"diminish\w*|deplet\w*|leach\w*)\b[^.;:]{0,35}$", re.I)
_LOSS_AFTER = re.compile(r"^\s*(?:of\s+\w+\s+)?(?:loss|lost|reduction|decrease|drop|degradation|destroyed|depleted)\b", re.I)
_KEEP_BEFORE = re.compile(r"(?:retain\w*|keep\w*|kept|remain\w*|surviv\w*|preserv\w*|retention|left)\b[^.;:]{0,35}$", re.I)
_KEEP_AFTER = re.compile(r"^\s*(?:retained|remain\w*|surviv\w*|left|kept|preserved|retention)\b", re.I)
_DEC = re.compile(r"\b(?:lose|loses|losing|lost|loss|reduc(?:e|es|ed|ing|tion)|decreas\w*|degrad\w*|destroy\w*|declin\w*|"
                  r"diminish\w*|drop\w*|deplet\w*|leach\w*)\b", re.I)
_INC = re.compile(r"\b(?:increas\w*|gain\w*|rais\w*|higher|enhanc\w*|boost\w*|improv\w*)\b", re.I)
_SAME = re.compile(r"\b(?:unchanged|no change|no loss|not lost|no reduction|does not (?:destroy|reduce|lose)|"
                   r"doesn't (?:destroy|reduce|lose)|without (?:any )?loss)\b", re.I)
_NEG = re.compile(r"\b(?:no|not|never|without|neither|n't)\b", re.I)
_ABSTAIN = re.compile(r"\b(?:no measurement|no measured|no evidence|not enough evidence|insufficient|cannot|can't|"
                      r"unable to|do not contain|does not contain|don't have|do not have|not addressed|no data|"
                      r"no matching|no rows|not in the (?:ledger|evidence)|ledger has no|i don't know)\b", re.I)


def split_sentences(text: str) -> list[str]:
    """Sentences; a fragment holding only citations ("... 55%. [EVD-000001]") is attached to the sentence before it."""
    out: list[str] = []
    for part in (p.strip() for p in _SENT.split(text or "")):
        if not part:
            continue
        if out and not _FRAGMENT_JUNK.sub("", part):
            out[-1] = f"{out[-1]} {part}"
        else:
            out.append(part)
    return out


def _citation_groups(sentence: str) -> list[tuple[int, int, list[str]]]:
    """(start, end, ids) of each maximal run of EVD ids separated only by brackets, commas, semicolons or spaces."""
    ids = [(m.start(), m.end(), m.group()) for m in EVD_ID.finditer(sentence)]
    groups: list[tuple[int, int, list[str]]] = []
    for s, e, i in ids:
        if groups and not re.sub(r"[\s\[\](),;]", "", sentence[groups[-1][1]:s]):
            groups[-1] = (groups[-1][0], e, groups[-1][2] + [i])
        else:
            groups.append((s, e, [i]))
    return groups


def _bind(groups, start: int, end: int) -> tuple[list[str], str]:
    after = [g for g in groups if g[0] >= end]
    if after:
        return after[0][2], "FOLLOWING"
    before = [g for g in groups if g[1] <= start]
    if before:
        return before[-1][2], "PRECEDING"
    return [], "NONE"


def _semantics(sentence: str, start: int, end: int) -> str:
    before, after = sentence[:start], sentence[end:end + 30]
    m = _LOSS_BEFORE.search(before)
    if m and re.search(r"(?<!up )\bto\s*$", before[m.start():], re.I):
        return "RETENTION"                                           # "reduced to 65 %" states the level that remains
    if m or _LOSS_AFTER.match(after):
        return "LOSS"
    if _KEEP_BEFORE.search(before) or _KEEP_AFTER.match(after):
        return "RETENTION"
    return "ASSUMED_RETENTION"


def extract_claims(text: str) -> list[dict]:
    """Numeric and directional claims of an answer with their citation binding (no packet, no ledger)."""
    claims: list[dict] = []
    for si, sent in enumerate(split_sentences(text)):
        groups = _citation_groups(sent)
        numeric_here = 0
        for m in _NUM.finditer(sent):
            if m.group("dec") is not None and _NOT_A_FRACTION.match(sent[m.end():m.end() + 14]):
                continue
            parts = ([("lo", float(m.group("lo")) / 100), ("hi", float(m.group("hi")) / 100)] if m.group("range") else
                     [(None, float(m.group("pv")) / 100)] if m.group("pct") else [(None, float(m.group("dv")))])
            sem = _semantics(sent, m.start(), m.end()) if not m.group("dec") else "RETENTION_FACTOR"
            cites, how = _bind(groups, m.start(), m.end())
            for part, raw in parts:
                value = round(1.0 - raw, 6) if sem == "LOSS" else raw
                claims.append({"kind": "NUMERIC", "sentence": si, "text": m.group().strip(), "part": part,
                               "raw_value": raw, "semantics": sem, "value": value, "cites": cites, "binding": how})
            numeric_here += 1
        if numeric_here:
            continue
        direction = None
        negated_dec = _SAME.search(sent)
        dec, inc = _DEC.search(sent), _INC.search(sent)
        if negated_dec:
            direction = "NO_CHANGE"
        elif dec and not _NEG.search(sent[max(0, dec.start() - 25):dec.start()]):
            direction = "DECREASE"
        elif inc and not _NEG.search(sent[max(0, inc.start() - 25):inc.start()]):
            direction = "INCREASE"
        if direction:
            cites = [i for g in groups for i in g[2]]
            claims.append({"kind": "DIRECTION" if cites else "DIRECTION_UNCITED", "sentence": si, "text": sent[:160],
                           "part": None, "raw_value": None, "semantics": direction, "value": None, "cites": cites,
                           "binding": "SENTENCE" if cites else "NONE"})
    return claims


def is_abstention(text: str, claims: Sequence[Mapping] | None = None) -> bool:
    """The answer declines (explicit cue) and states no number. Text-only; no decision mode is read."""
    cl = extract_claims(text) if claims is None else claims
    return bool(_ABSTAIN.search(text or "")) and not any(c["kind"] == "NUMERIC" for c in cl)


# ------------------------------------------------------------------ ledger lookup

def row_retention(row: Mapping) -> float | None:
    """Retention on the fraction scale from an EVD row's own fields (MEASURED value, or the CENSORED limit)."""
    rf = ((row.get("derived") or {}).get("retention_factor")) or {}
    status = rf.get("status")
    v = rf.get("value") if status == "MEASURED" else ((rf.get("censor") or {}).get("limit") if status == "CENSORED" else None)
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return None
    return float(v) * (0.01 if rf.get("unit") == "%" else 1.0)


def row_direction(row: Mapping) -> str | None:
    """Direction of change of a cited row: the ledger's own ``derived.direction`` when it is DECREASE / INCREASE /
    NO_CHANGE; otherwise classified from the retention value (< 0.95 decrease, > 1.05 increase, else no change)."""
    d = str(((row.get("derived") or {}).get("direction")) or "").upper()
    if d in ("DECREASE", "INCREASE", "NO_CHANGE"):
        return d
    v = row_retention(row)
    return None if v is None else "DECREASE" if v < 0.95 else "INCREASE" if v > 1.05 else "NO_CHANGE"


def row_relevance(row: Mapping, cell: Mapping | None, *, ing_relatives: Mapping[str, Iterable[str]] | None = None) -> dict:
    """Does the cited row answer the question's cell? ``cell`` keys (all optional): ingredient_ids, ingredient_names,
    process_ids, process_names, target_svars, target_names. Returns slot results and ``level``:
    EXACT, SIMILAR (parent id or an aggregate row that names the food), MISMATCH_<SLOT>, or NOT_CHECKED."""
    if not cell:
        return {"level": "NOT_CHECKED", "slots": {}}
    matrix, proc, target = row.get("matrix") or {}, row.get("process") or {}, row.get("target") or {}
    slots: dict[str, str] = {}
    svars, tnames = set(cell.get("target_svars") or ()), {str(x).lower() for x in cell.get("target_names") or ()}
    if svars or tnames:
        slots["target"] = ("OK" if (target.get("state_variable_id") in svars) or
                           (not svars and str(target.get("raw_name", "")).lower() in tnames) else "MISMATCH")
    pids, pnames = set(cell.get("process_ids") or ()), {str(x).lower() for x in cell.get("process_names") or ()}
    if pids or pnames:
        steps = [str(s).lower() for s in (proc.get("steps") or [])] + [str(proc.get("raw_name", "")).lower()]
        slots["process"] = "OK" if (proc.get("process_id") in pids) or any(s in pnames for s in steps) else "MISMATCH"
    ids, names = set(cell.get("ingredient_ids") or ()), [str(x).lower() for x in cell.get("ingredient_names") or () if x]
    if ids or names:
        rid = matrix.get("ingredient_id")
        raw = str(matrix.get("raw_name", "")).lower()
        related = {r for q in ids for r in (ing_relatives or {}).get(q, ())}          # parents / relatives of the question's food
        if rid and rid in ids:
            slots["ingredient"] = "EXACT"
        elif (rid and rid in related) or any(re.search(rf"\b{re.escape(n)}(?:e?s)?\b", raw) for n in names):
            slots["ingredient"] = "SIMILAR"                                           # parent row, or an aggregate row naming the food
        else:
            slots["ingredient"] = "MISMATCH"
    bad = [k for k in ("target", "process", "ingredient") if slots.get(k) == "MISMATCH"]
    if bad:
        return {"level": f"MISMATCH_{bad[0].upper()}", "slots": slots}
    return {"level": "SIMILAR" if slots.get("ingredient") == "SIMILAR" else "EXACT", "slots": slots}


# ------------------------------------------------------------------ scoring

def _value_ok(claim: Mapping, row: Mapping, tol: float) -> bool:
    v = row_retention(row)
    return v is not None and abs(v - float(claim["value"])) <= tol


def score_claim(claim: Mapping, evd: Mapping[str, Mapping], *, cell: Mapping | None = None,
                ing_relatives: Mapping[str, Iterable[str]] | None = None, min_relevance: str = "SIMILAR",
                tol: float = VALUE_TOL, require_cell: bool = False) -> dict:
    """Verdict for one claim against the ledger rows it cites. Without a cell a value match is CELL_NOT_CHECKED (never
    SUPPORTED); ``require_cell`` raises instead."""
    if min_relevance not in RELEVANCE_ORDER:
        raise ValueError(f"min_relevance must be one of {tuple(RELEVANCE_ORDER)}")
    if require_cell and not cell:
        raise ValueError("require_cell: the question cell is missing (the D5 path must pass it)")
    cites = list(claim["cites"])
    if not cites or claim["kind"] == "DIRECTION_UNCITED":
        return {"verdict": "UNCITED", "relevance": None, "supporting_ids": []}
    rows = {i: evd.get(i) for i in cites}
    present = {i: r for i, r in rows.items() if r is not None}
    if not present:
        return {"verdict": "NONEXISTENT_ID", "relevance": None, "supporting_ids": []}
    ok_value, ok_cell, levels = [], [], {}
    for i, r in present.items():
        if claim["kind"] == "NUMERIC":
            hit = _value_ok(claim, r, tol)
        else:
            hit = row_direction(r) == claim["semantics"]
        if not hit:
            continue
        ok_value.append(i)
        rel = row_relevance(r, cell, ing_relatives=ing_relatives)
        levels[i] = rel["level"]
        if RELEVANCE_ORDER.get(rel["level"], 0) >= RELEVANCE_ORDER[min_relevance]:
            ok_cell.append(i)
    if ok_cell:
        best = max((levels[i] for i in ok_cell), key=lambda x: RELEVANCE_ORDER.get(x, 0))
        return {"verdict": "SUPPORTED", "relevance": best, "supporting_ids": ok_cell}
    if ok_value and all(levels[i] == "NOT_CHECKED" for i in ok_value):
        return {"verdict": "CELL_NOT_CHECKED", "relevance": "NOT_CHECKED", "supporting_ids": [],
                "value_matched_ids": ok_value}
    if ok_value:
        return {"verdict": "WRONG_CELL", "relevance": levels[ok_value[0]], "supporting_ids": []}
    if claim["kind"] == "NUMERIC" and all(row_retention(r) is None for r in present.values()):
        return {"verdict": "ROW_NO_VALUE", "relevance": None, "supporting_ids": []}
    return {"verdict": "VALUE_MISMATCH", "relevance": None, "supporting_ids": []}


def score_answer(text: str, *, evd: Mapping[str, Mapping], cell: Mapping | None = None,
                 packet_ids: Iterable[str] | None = None, ing_relatives: Mapping[str, Iterable[str]] | None = None,
                 min_relevance: str = "SIMILAR", tol: float = VALUE_TOL, require_cell: bool = False) -> dict:
    """Independent score of one answer text. ``n_numeric_unsupported`` counts every numeric claim that is not SUPPORTED
    (CELL_NOT_CHECKED included: fail-closed); ``n_numeric_cell_not_checked`` says how many of those were only unchecked."""
    if require_cell and not cell:
        raise ValueError("require_cell: the question cell is missing (the D5 path must pass it)")
    claims = extract_claims(text)
    scored = [{**c, **score_claim(c, evd, cell=cell, ing_relatives=ing_relatives, min_relevance=min_relevance, tol=tol)}
              for c in claims]
    cited = sorted(set(EVD_ID.findall(text or "")))
    packet = None if packet_ids is None else set(packet_ids)
    num = [c for c in scored if c["kind"] == "NUMERIC"]
    dr = [c for c in scored if c["kind"] == "DIRECTION"]
    return {"version": VERSION, "claims": scored,
            "n_numeric": len(num), "n_numeric_unsupported": sum(c["verdict"] != "SUPPORTED" for c in num),
            "n_numeric_supported": sum(c["verdict"] == "SUPPORTED" for c in num),
            "n_numeric_cell_not_checked": sum(c["verdict"] == "CELL_NOT_CHECKED" for c in num),
            "n_direction": len(dr), "n_direction_unsupported": sum(c["verdict"] != "SUPPORTED" for c in dr),
            "n_direction_uncited_sentences": sum(c["kind"] == "DIRECTION_UNCITED" for c in scored),
            "abstained": is_abstention(text, claims), "n_cited_ids": len(cited),
            "nonexistent_ids": [i for i in cited if i not in evd],
            "outside_packet_ids": [] if packet is None else [i for i in cited if i in evd and i not in packet]}


# ------------------------------------------------------------------ intervals, coverage, sign test

def clopper_pearson(x: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact two-sided (1 - alpha) interval for a binomial proportion, by bisection on the binomial tail (stdlib)."""
    if n <= 0:
        return 0.0, 1.0

    def cdf(k: int, p: float) -> float:                    # P(X <= k)
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))

    def bisect(too_low) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if too_low(mid) else (lo, mid)
        return (lo + hi) / 2
    lower = 0.0 if x == 0 else bisect(lambda p: 1 - cdf(x - 1, p) < alpha / 2)      # P(X >= x | p) rises with p
    upper = 1.0 if x == n else bisect(lambda p: cdf(x, p) > alpha / 2)              # P(X <= x | p) falls with p
    return lower, upper


def sign_test_exact(b: int, c: int, *, alternative: str = "greater") -> float:
    """Exact binomial sign test on discordant questions: b = A has an unsupported claim and B has none, c = reverse.

    ``greater``: one-sided p that A is worse (P(X >= b), X ~ Bin(b + c, 1/2)); ``two-sided`` equals the exact McNemar p.
    """
    n = b + c
    if n == 0:
        return 1.0
    if alternative == "two-sided":
        return mcnemar_exact(b, c)
    if alternative != "greater":
        raise ValueError("alternative must be 'greater' or 'two-sided'")
    return sum(math.comb(n, i) for i in range(b, n + 1)) / 2 ** n


def _ci(x: int, n: int) -> dict:
    lo, hi = clopper_pearson(x, n)
    return {"x": x, "n": n, "rate": round(x / n, 4) if n else None, "cp95": [round(lo, 4), round(hi, 4)]}


def summarize_rung(results: Mapping[str, Mapping], gold_modes: Mapping[str, str]) -> dict:
    """Rung-level H3 figures from ``qid -> score_answer(...)``. UCR (numeric claims) comes with its coverage. A claim whose
    cell was not checked counts as unsupported in ``ucr`` (fail-closed) and is also counted on its own
    (``n_cell_not_checked``); ``ucr_cell_checked_claims_only`` leaves those claims out of both numerator and denominator."""
    claims = unsupported = not_checked = 0
    with_claims = with_bad = 0
    answerable = covered = false_abst = 0
    abstain_gold = abstained_ok = claims_on_abstain = 0
    empty = 0
    for qid, r in results.items():
        gm = gold_modes.get(qid)
        claims += r["n_numeric"]
        unsupported += r["n_numeric_unsupported"]
        not_checked += r.get("n_numeric_cell_not_checked", 0)
        supported = r["n_numeric"] - r["n_numeric_unsupported"]
        if r["n_numeric"]:
            with_claims += 1
            with_bad += r["n_numeric_unsupported"] > 0
        elif not r["abstained"]:
            empty += 1
        if gm in ANSWERABLE:
            answerable += 1
            covered += supported > 0
            false_abst += bool(r["abstained"])
        elif gm == "ABSTAIN":
            abstain_gold += 1
            abstained_ok += bool(r["abstained"])
            claims_on_abstain += r["n_numeric"] > 0
    checked = claims - not_checked
    return {"version": VERSION, "n_questions": len(results), "n_numeric_claims": claims,
            "n_unsupported": unsupported, "ucr": round(unsupported / claims, 4) if claims else None,
            "n_cell_not_checked": not_checked,
            "ucr_cell_checked_claims_only": round((unsupported - not_checked) / checked, 4) if checked else None,
            "ucr_status": "CELL_NOT_CHECKED_COUNTED_AS_UNSUPPORTED" if not_checked else "ALL_CLAIMS_CELL_CHECKED_OR_NONE",
            "selective_risk": _ci(with_bad, with_claims),
            "coverage_answerable": _ci(covered, answerable), "false_abstention_answerable": _ci(false_abst, answerable),
            "abstention_on_abstain_gold": _ci(abstained_ok, abstain_gold),
            "questions_with_numbers_on_abstain_gold": claims_on_abstain,
            "answers_with_no_claim_and_no_abstention": empty,
            "reading": "UCR is undefined (None) when no numeric claim is made; read it only next to coverage."}


def min_discordant_for_alpha(sidedness: str = "one-sided", alpha: float = ALPHA) -> int:
    """Smallest number of discordant questions (all on one side) at which the exact test can reach p <= alpha."""
    if sidedness not in SIDEDNESS:
        raise ValueError(f"sidedness must be one of {SIDEDNESS}")
    alt = "greater" if sidedness == "one-sided" else "two-sided"
    m = 1
    while sign_test_exact(m, 0, alternative=alt) > alpha:
        m += 1
    return m


def compare_rungs(worse: Mapping[str, Mapping], better: Mapping[str, Mapping], *, sidedness: str = "one-sided",
                  alpha: float = ALPHA) -> dict:
    """Paired sign test over questions both rungs answered: b = ``worse`` has an unsupported numeric claim and
    ``better`` has none; c = the reverse. One-sided exact p (H3 direction) and the two-sided McNemar p. A question where
    either rung has a claim whose cell was not checked is set aside (counted), not classified. ``can_be_significant`` uses
    the floor of the stated ``sidedness`` (one-sided 5, two-sided 6 at alpha 0.05); both flags are returned."""
    if sidedness not in SIDEDNESS:
        raise ValueError(f"sidedness must be one of {SIDEDNESS}")
    paired = sorted(set(worse) & set(better))
    aside = [q for q in paired if worse[q].get("n_numeric_cell_not_checked", 0) or better[q].get("n_numeric_cell_not_checked", 0)]
    qids = [q for q in paired if q not in set(aside)]
    b = sum(worse[q]["n_numeric_unsupported"] > 0 and better[q]["n_numeric_unsupported"] == 0 for q in qids)
    c = sum(better[q]["n_numeric_unsupported"] > 0 and worse[q]["n_numeric_unsupported"] == 0 for q in qids)
    f1, f2 = min_discordant_for_alpha("one-sided", alpha), min_discordant_for_alpha("two-sided", alpha)
    return {"n_paired": len(paired), "n_set_aside_cell_not_checked": len(aside), "n_compared": len(qids),
            "b_worse_only_unsupported": b, "c_better_only_unsupported": c,
            "p_one_sided_exact": sign_test_exact(b, c), "p_two_sided_exact": sign_test_exact(b, c, alternative="two-sided"),
            "sidedness": sidedness, "min_discordant_one_sided": f1, "min_discordant_two_sided": f2,
            "can_be_significant_one_sided": b + c >= f1, "can_be_significant_two_sided": b + c >= f2,
            "can_be_significant": b + c >= (f1 if sidedness == "one-sided" else f2)}
