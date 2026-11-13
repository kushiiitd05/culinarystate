#!/usr/bin/env python
"""T3-C09-R1: NER vs Rung A mention agreement on the deployed ingredient lines. DIAGNOSTIC, not gold.

Reference = FOOD spans of the frozen NER checkpoint (DeBERTa-base+CRF, sha256 prefix 582c056ac20625ac) bound in the
S174 deployment files (RUN-S174-003, one file per family, each line carries ``model``). Compared = Rung A food
lexicon (greedy longest match, same as tools/s178_corpus_span_agreement.py). Neither side is human gold, so the
rates are method agreement, not accuracy of either. Also counts lines where NER finds FOOD but the lexicon finds
nothing ("FOOD span in lexicon-missed lines"). Phrase lists (top missed / extra) go to a git-ignored folder;
the committed JSON is counts only. Run on the host that holds the spans (vinayak):

    python tools/s179_ner_vs_runga_agreement.py --spans ~/Kush/cs_runs/ner_*_S174.jsonl --out OUT.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("s178_span", ROOT / "tools" / "s178_corpus_span_agreement.py")
s178 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s178)

TOOL_VERSION = "s179-ner-vs-runga-0.1.0"
EXPECTED_MODEL = "582c056ac20625ac"
DERIVED_DIR = "data/derived/s179_ner_vs_runga"
TOP_N = 500
LABELS = ["DIAGNOSTIC", "NOT_GOLD", "AI_PRECHECKED", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"]


def family_of(path: Path) -> str:
    m = re.fullmatch(r"ner_(.+)_S174\.jsonl", path.name)
    if not m:
        raise ValueError(f"unexpected span file name {path.name}")
    return m.group(1)


def run_file(path: Path, lex, tokens) -> tuple[dict, Counter, Counter]:
    """Counts for one family file; refuses any line whose model is not the frozen checkpoint."""
    c, missed, extra = Counter(), Counter(), Counter()
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            if not raw.strip():
                continue
            r = json.loads(raw)
            if r.get("model") != EXPECTED_MODEL:
                raise ValueError(f"{path.name}: span model {r.get('model')!r} is not {EXPECTED_MODEL}")
            text = r.get("text") or ""
            ref = [(int(s), int(e), str(t)) for s, e, t, *_ in r.get("spans") or []]
            lx = s178.lexicon_spans(lex, text, tokens)
            c["lines"] += 1
            n_food = sum(t == "FOOD" for _, _, t in ref)
            c["lines_with_ner_food"] += n_food > 0
            if n_food and not lx:
                c["lines_lexicon_empty_ner_food"] += 1
                c["ner_food_spans_in_lexicon_empty_lines"] += n_food
            s178.compare(ref, lx, c, missed, extra, text)
    g, x = c["gold_food_spans"], c["lexicon_spans"]
    pct = s178.pct
    rates = {"ner_food_covered_by_a_lexicon_span": pct(g - c["gold_food_missed_no_overlap"], g),
             "ner_food_exact_boundary": pct(c["gold_food_exact_boundary"], g),
             "ner_food_missed_by_lexicon": pct(c["gold_food_missed_no_overlap"], g),
             "lexicon_spans_overlapping_ner_food": pct(c["lexicon_overlapping_gold_food"], x),
             "lexicon_spans_no_ner_span": pct(c["lexicon_extra_no_gold_span"], x),
             "lines_lexicon_empty_given_ner_food": pct(c["lines_lexicon_empty_ner_food"], c["lines_with_ner_food"])}
    # s178.compare names the reference "gold"; here the reference is NER output, renamed in the record.
    counts = {k.replace("gold_food", "ner_food").replace("only_gold_", "only_ner_"): v for k, v in sorted(c.items())}
    return {"counts": counts, "rates_pct": rates, "distinct_missed_phrases": len(missed),
            "distinct_extra_phrases": len(extra)}, missed, extra


def _write_list(path: Path, ctr: Counter) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["rank", "phrase", "count"])
        for i, (k, v) in enumerate(sorted(ctr.items(), key=lambda kv: (-kv[1], kv[0]))[:TOP_N], 1):
            w.writerow([i, k, v])
    return {"path": path.as_posix(), "rows": min(len(ctr), TOP_N), "git_ignored": True,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spans", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    from culinarystate.extraction.rung_a_lexicon import load_lexicon, tokens
    lex = load_lexicon(ROOT, cache=False)
    families, inputs = {}, {}
    for sp in sorted(Path(p).expanduser() for p in a.spans):
        fam = family_of(sp)
        inputs[fam] = {"file": sp.name, "sha256": s178.hashlib.sha256(sp.read_bytes()).hexdigest()}
        if sp.stat().st_size == 0:
            families[fam] = {"status": "EMPTY_INPUT_NOT_RUN"}
            continue
        res, missed, extra = run_file(sp, lex, tokens)
        res["derived_lists"] = {n: _write_list(ROOT / DERIVED_DIR / f"{n}_{fam}.csv", ctr)
                                for n, ctr in (("missed_ner_foods", missed), ("extra_lexicon_spans", extra))}
        families[fam] = res
    record = {"record": "NER_VS_RUNGA_MENTION_AGREEMENT", "item": "T3-C09-R1", "tool_version": TOOL_VERSION,
              "labels": LABELS, "approver": "ksh+prv (AI, D-085)", "reference": f"NER_FROZEN_CKPT_{EXPECTED_MODEL}_S174_SPANS",
              "compared": "RUNG_A_LEXICON_GREEDY_LONGEST_MATCH", "lexicon_fingerprint": lex.fingerprint,
              "run_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
              "inputs": inputs, "families": families, "contains_text": False, "contains_ids": False,
              "notes": ["Agreement between two methods; neither is human gold, so no precision/recall of either is claimed.",
                        "TASTEset trained the NER checkpoint: its row is in-domain for NER.",
                        "A missed NER food is a surface the ING/ALIAS registry lacks, or an NER false positive; this record cannot tell which.",
                        "BBC was never NER-tagged (D-003); GUTENBERG_SEGMENT S174 file is empty (no ingredient-line channel)."],
              "scientific_gate_pass": False}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as f:
        f.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v.get("rates_pct", v) for k, v in families.items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
