"""Human claim-audit sample generator for H3 (S178; REV-B G-08; SSOT v16 draft 287.3 fix 1; T8-C12-R1). DRAFT.

Humans (Kush, Parv) label a rung-blind, stratified, seeded sample of numeric / directional claims so that the
precision and recall of the automatic "unsupported" flags (the independent scorer and the S173 checker) are estimated
against human labels rather than assumed.

- ``audit_items``: one item per claim of a scored answer (independent verdict + the S173 checker's answer-level flag).
- ``stratified_audit_sample``: per rung, strata = (independent says unsupported?) x (S173 checker flags the answer?);
  the disagreement strata are drawn first and every non-empty stratum gets an equal share (round robin), because
  B7 has almost no unsupported claims by construction and a plain random sample would never look at them.
  Selection inside a stratum is the smallest sha256(seed | rung | item_id). The design records every stratum's
  population and sample size so estimates can be inverse-probability weighted.
- ``write_audit_files``: two identical reviewer sheets (the rung, qid and any automatic verdict are NOT shown; claims are
  shuffled across rungs) and a separate key file. Refuses to overwrite. Sheets hold answer text and ledger display
  fields, so they belong under ``data/derived/`` (git-ignored), never in a committed folder.
- ``merge_reviewer_labels`` / ``estimate_checker_quality``: after labelling, agreement between the two reviewers and
  weighted precision / recall of each automatic flag.

AI drafts the sample; the labels are human. Nothing here is a signature or an approval (D-071).
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from culinarystate.evaluation.h3_independent import split_sentences

VERSION = "claim_audit@0.1"
STATUS = "AI_DRAFTED_SAMPLE"
DEFAULT_RUNGS = ("B2", "B5T", "B7")                 # REV-B: 40-60 claims per rung, rung-blind
# priority of strata when the quota cannot cover all of them: where the two scorers disagree is the most informative
STRATA = ("INDEP_UNSUPPORTED|CHECKER_CLEAN", "INDEP_SUPPORTED|CHECKER_FLAGGED", "INDEP_UNSUPPORTED|CHECKER_FLAGGED",
          "INDEP_SUPPORTED|CHECKER_CLEAN")
SHEET_COLS = ["audit_id", "question", "answer_sentence", "claim_text", "claim_kind", "cited_rows",
              "reviewer", "claim_supported_by_cited_row", "cited_row_matches_question", "reviewer_note"]
KEY_COLS = ["audit_id", "item_id", "qid", "rung", "claim_kind", "independent_verdict", "checker_flags_answer", "stratum",
            "stratum_population", "stratum_sampled"]
SUPPORTED_CODES = ("YES", "NO", "PARTLY", "CANNOT_TELL")
MATCH_CODES = ("RIGHT_CELL", "SIMILAR", "WRONG_CELL", "NO_CITATION")


def _h(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def stratum_of(independent_unsupported: bool, checker_flags_answer: bool) -> str:
    return (f"INDEP_{'UNSUPPORTED' if independent_unsupported else 'SUPPORTED'}|"
            f"CHECKER_{'FLAGGED' if checker_flags_answer else 'CLEAN'}")


def audit_items(answers: Sequence[Mapping[str, Any]], *, kinds: Sequence[str] = ("NUMERIC", "DIRECTION", "DIRECTION_UNCITED")
                ) -> list[dict]:
    """Claim items from answer records ``{qid, rung, question, answer, scored, checker_unsupported}``.

    ``scored`` is ``h3_independent.score_answer(...)``; ``checker_unsupported`` is the S173 checker's unsupported-claim
    count for the same answer (None when not run: such items are treated as CHECKER_CLEAN and marked in the key).
    """
    items = []
    for a in answers:
        sents = split_sentences(a.get("answer") or "")
        flagged = bool(a.get("checker_unsupported"))
        for k, c in enumerate(a["scored"]["claims"]):
            if c["kind"] not in kinds:
                continue
            unsup = c["verdict"] != "SUPPORTED"
            items.append({"item_id": "ITM-" + _h(str(a["qid"]), str(a["rung"]), str(k), c["text"])[:16],
                          "qid": a["qid"], "rung": a["rung"], "question": a.get("question", ""),
                          "sentence": sents[c["sentence"]] if c["sentence"] < len(sents) else "",
                          "claim_text": c["text"], "claim_kind": c["kind"], "cites": list(c["cites"]),
                          "independent_verdict": c["verdict"], "independent_unsupported": unsup,
                          "checker_flags_answer": flagged, "checker_run": a.get("checker_unsupported") is not None,
                          "stratum": stratum_of(unsup, flagged)})
    return items


def stratified_audit_sample(items: Sequence[Mapping[str, Any]], *, per_rung: int, seed: str,
                            rungs: Sequence[str] = DEFAULT_RUNGS) -> dict:
    """Seeded stratified draw of ``per_rung`` items per rung (fewer when the rung has fewer)."""
    if per_rung < 1 or not seed:
        raise ValueError("per_rung must be positive and seed non-empty")
    sample, design, short = [], {}, []
    for rung in rungs:
        pool = [i for i in items if i["rung"] == rung]
        ranked = {s: sorted((i for i in pool if i["stratum"] == s), key=lambda i: (_h(seed, rung, i["item_id"]), i["item_id"]))
                  for s in STRATA}
        taken = {s: 0 for s in STRATA}
        total = 0
        while total < min(per_rung, len(pool)):
            progressed = False
            for s in STRATA:
                if total >= per_rung:
                    break
                if taken[s] < len(ranked[s]):
                    taken[s] += 1
                    total += 1
                    progressed = True
            if not progressed:
                break
        if total < per_rung:
            short.append({"rung": rung, "requested": per_rung, "available": len(pool)})
        design[rung] = {s: {"population": len(ranked[s]), "sampled": taken[s],
                            "weight": round(len(ranked[s]) / taken[s], 6) if taken[s] else None} for s in STRATA}
        for s in STRATA:
            sample += [{**i, "stratum_population": len(ranked[s]), "stratum_sampled": taken[s]} for i in ranked[s][:taken[s]]]
    return {"version": VERSION, "status": STATUS, "seed_sha256": _h(seed), "per_rung": per_rung, "rungs": list(rungs),
            "sample": sample, "design": design, "shortfalls": short}


def _cited_display(ids: Sequence[str], evd: Mapping[str, Mapping]) -> str:
    out = []
    for i in ids:
        r = evd.get(i)
        if r is None:
            out.append(f"{i} | NOT IN LEDGER")
            continue
        rf = (r.get("derived") or {}).get("retention_factor") or {}
        val = rf.get("value") if rf.get("status") == "MEASURED" else (rf.get("censor") or {}).get("limit")
        unit = "" if rf.get("unit") != "%" else "%"
        out.append(f"{i} | {str((r.get('matrix') or {}).get('raw_name', ''))[:90]} | "
                   f"{(r.get('process') or {}).get('raw_name', '')} | {(r.get('target') or {}).get('raw_name', '')} | "
                   f"retention {val}{unit} ({rf.get('status', 'NONE')})")
    return "\n".join(out)


def write_audit_files(sample: Sequence[Mapping[str, Any]], evd: Mapping[str, Mapping], out_dir: Path, *, seed: str,
                      reviewers: Sequence[str] = ("Kush", "Parv")) -> dict:
    """Write the two blind reviewer sheets and the key; returns paths and sha256 (refuses to overwrite)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    order = sorted(sample, key=lambda i: _h(seed, "shuffle", i["item_id"]))
    aud = {i["item_id"]: f"AUD-{n:04d}" for n, i in enumerate(order, 1)}
    sheet = [{"audit_id": aud[i["item_id"]], "question": i["question"], "answer_sentence": i["sentence"],
              "claim_text": i["claim_text"], "claim_kind": i["claim_kind"],
              "cited_rows": _cited_display(i["cites"], evd)} for i in order]
    paths: dict[str, str] = {}
    for who in reviewers:
        p = out_dir / f"claim_audit_sheet_{who}.csv"
        with open(p, "x", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=SHEET_COLS)
            w.writeheader()
            w.writerows({**r, "reviewer": who, "claim_supported_by_cited_row": "", "cited_row_matches_question": "",
                         "reviewer_note": ""} for r in sheet)
        paths[who] = str(p)
    kp = out_dir / "claim_audit_key_SEALED.csv"
    with open(kp, "x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=KEY_COLS)
        w.writeheader()
        w.writerows({"audit_id": aud[i["item_id"]], "item_id": i["item_id"], "qid": i["qid"], "rung": i["rung"],
                     "claim_kind": i["claim_kind"], "independent_verdict": i["independent_verdict"],
                     "checker_flags_answer": i["checker_flags_answer"], "stratum": i["stratum"],
                     "stratum_population": i["stratum_population"], "stratum_sampled": i["stratum_sampled"]} for i in order)
    paths["key"] = str(kp)
    return {"paths": paths, "sha256": {k: hashlib.sha256(Path(v).read_bytes()).hexdigest() for k, v in paths.items()},
            "n_items": len(order), "columns": SHEET_COLS, "codes": {"claim_supported_by_cited_row": SUPPORTED_CODES,
                                                                    "cited_row_matches_question": MATCH_CODES}}


# ------------------------------------------------------------------ after the humans have labelled

def human_unsupported(supported: str, matches: str) -> bool | None:
    """A claim is unsupported unless the reviewer says YES and the row is not a wrong-cell citation; None = unusable."""
    s, m = (supported or "").strip().upper(), (matches or "").strip().upper()
    if s not in SUPPORTED_CODES or s == "CANNOT_TELL":
        return None
    if m and m not in MATCH_CODES:
        return None
    return s != "YES" or m in ("WRONG_CELL", "NO_CITATION")


def merge_reviewer_labels(a_rows: Sequence[Mapping[str, str]], b_rows: Sequence[Mapping[str, str]]) -> dict:
    """Per audit_id labels of two reviewers: agreed labels are usable, others need reconciliation (not discarded)."""
    b = {r["audit_id"]: r for r in b_rows}
    agreed, disputed, unusable = {}, [], []
    for r in a_rows:
        o = b.get(r["audit_id"])
        la = human_unsupported(r.get("claim_supported_by_cited_row", ""), r.get("cited_row_matches_question", ""))
        lb = None if o is None else human_unsupported(o.get("claim_supported_by_cited_row", ""),
                                                      o.get("cited_row_matches_question", ""))
        if la is None or lb is None:
            unusable.append(r["audit_id"])
        elif la == lb:
            agreed[r["audit_id"]] = la
        else:
            disputed.append(r["audit_id"])
    n = len(agreed) + len(disputed)
    return {"agreed": agreed, "disputed": sorted(disputed), "unusable": sorted(unusable),
            "raw_agreement": round(len(agreed) / n, 4) if n else None}


def estimate_checker_quality(key_rows: Sequence[Mapping[str, Any]], labels: Mapping[str, bool]) -> dict:
    """Weighted precision / recall of "unsupported" for the independent scorer and the S173 checker, per rung and
    pooled, from the key (strata, population, sample) and the agreed human labels (True = human says unsupported).

    Weight of an item = stratum population / stratum sampled. Raw (unweighted) counts are returned so that an
    exact interval can be put on a within-stratum rate; no single interval is claimed for the weighted figure.
    """
    out: dict[str, Any] = {"version": VERSION, "n_labelled": 0, "rungs": {}}
    rows = [r for r in key_rows if r["audit_id"] in labels]
    out["n_labelled"] = len(rows)

    def flag(r, scorer):
        return (str(r["independent_verdict"]) != "SUPPORTED") if scorer == "independent" else \
            str(r["checker_flags_answer"]).lower() == "true"

    def tally(group):
        res = {}
        for scorer in ("independent", "s173_checker"):
            tp = fp = fn = tn = 0.0
            raw = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
            for r in group:
                w = float(r["stratum_population"]) / float(r["stratum_sampled"])
                f, h = flag(r, scorer), bool(labels[r["audit_id"]])
                k = "tp" if f and h else "fp" if f else "fn" if h else "tn"
                raw[k] += 1
                if k == "tp":
                    tp += w
                elif k == "fp":
                    fp += w
                elif k == "fn":
                    fn += w
                else:
                    tn += w
            res[scorer] = {"precision": round(tp / (tp + fp), 4) if tp + fp else None,
                           "recall": round(tp / (tp + fn), 4) if tp + fn else None,
                           "est_population": {"tp": round(tp, 2), "fp": round(fp, 2), "fn": round(fn, 2), "tn": round(tn, 2)},
                           "raw_counts": raw}
        return res

    for rung in sorted({r["rung"] for r in rows}):
        out["rungs"][rung] = tally([r for r in rows if r["rung"] == rung])
    out["pooled"] = tally(rows)
    out["note"] = ("recall counts only claims the extractor produced; a claim neither scorer extracted is invisible here "
                   "(extraction recall needs a free-text read of whole answers).")
    return out


def write_json(path: Path, obj: Any) -> str:
    """Counts-only JSON helper for reports (refuses to overwrite); returns sha256."""
    data = (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode("utf-8")
    with open(path, "xb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()
