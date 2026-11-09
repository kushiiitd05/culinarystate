#!/usr/bin/env python3
"""S178 CORPUS lane, T3-C05-R1: verb-coverage census of Rung A on the non-BBC instruction text (Food.com, Gutenberg, Wikibooks).

Rung A labels a word ACTION only when the PROC lexicon (ledger PROC canonical names / aliases + the candidate surface-form table,
plus the rule compiler's lemma guess) maps it, so "share of ACTION events mapped to PROC" is 100 % by construction. The useful
question is the other side: of the words that stand in a VERB SLOT (sentence start, or after a comma, then, and, or, to, until,
before, after, an adverb; the rule compiler's `_VERB_SLOT`), how many does Rung A map, and which unmapped words are most frequent?

Definitions (counts only, no recipe text):
  ACTION event      a token for which `RungA._action_at` returns a PROC match (the exact tagging rule of `extract_mentions`, without the
                    numeric-span blocking, which cannot change a word token); split into unique PROC id / ambiguous (several PROC ids) /
                    PROC_LEMMA_GUESS (surface not in the PROC surface table, mapped by the lemma guess).
  verb candidate    a word token in a verb slot that is not a closed-class word (determiner, pronoun, preposition, conjunction,
                    auxiliary, number word, adverb of sequence: CLOSED_CLASS below) and not a lexicon food or tool word.
  sentence-initial  the first word of a sentence (imperative mood: the cleanest verb sample in recipe text).
  mapped / unmapped candidate has / has no ACTION match.
Unmapped words are grouped to a lemma-like key by folding inflections onto a base form that also occurs in the data
(`fold_forms`); `slot_share` = share of the word's occurrences that stand in a verb slot (nouns and adverbs have a low share; verbs high).
No POS tagger is available on this server (no spaCy/torch), so a verb is a slot word; the list contains adverbs, nouns and
fragments, which `slot_share` and `init_share` help filter. The BBC-only list `registry/processes/unmapped_verbs.csv` (spaCy lemmas)
is not comparable (different corpus, POS-tagged); `in_bbc_spacy_list` marks overlap.

TASTEset has no instruction text; BBC is not on this server (D-003). Gutenberg ingredient lines do not exist but its steps do.

Outputs: reports/s178/corpus/verb_coverage_census_v1.{json,md}; reports/s178/corpus/verb_unmapped_top200_<FAMILY>.csv (single words with
counts, min count 20; same kind of list as the committed registry/processes/unmapped_verbs.csv, flagged for the law-6 check in the report).

  nice -n 10 python tools/s178_corpus_verb_census.py --workers 16 [--sample 1000 --seed 20261104]
AI_DRAFTED / PROPOSED. NON_CITABLE. A rule-based coverage count, not an accuracy estimate and not a gold score.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from collections import Counter
from multiprocessing import get_context
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TOOL_VERSION = "s178-corpus-verb-census-0.1.0-draft"
OUT_DIR = "reports/s178/corpus"
FAMILIES = ("FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS")
TOP_N = 200
MIN_COUNT = 20
BBC_LIST = "registry/processes/unmapped_verbs.csv"

CLOSED_CLASS = frozenset("""
a an the this that these those some any each every no all both either neither another other such same
i me my mine we us our ours you your yours he him his she her hers it its they them their theirs one ones who whom whose which what
in on at by for from to of off up down out over under into onto onto upon with without within through across around about against
between among along after before during until till since while when whenever where wherever once if unless though although because as
than so then thus hence therefore also too either else instead otherwise however meanwhile afterwards afterward finally first second
third next last later now soon again just only even still yet already always never often sometimes usually
and or but nor not
is are was were be been being am do does did done doing have has had having can could will would shall should may might must
there here very quite rather more most less least much many few little lot lots enough almost nearly
step steps note notes see serve serves ok okay
one two three four five six seven eight nine ten eleven twelve twenty thirty forty fifty hundred
half quarter whole
gently carefully quickly lightly well briefly slowly thoroughly immediately completely evenly generously firmly roughly finely coarsely loosely
tightly lightly gradually constantly occasionally frequently continuously slightly
""".split())

_RUNG = None


def _init():
    global _RUNG
    from culinarystate.extraction.rung_a import RungA
    _RUNG = RungA()


def count_texts(texts: list[str]) -> dict:
    """Aggregate counts for a list of recipe instruction texts (one string per recipe, steps joined by newlines)."""
    from culinarystate.extraction.rung_a import sentences
    from culinarystate.extraction.rung_a_lexicon import tokens
    from culinarystate.state_graph.rule_compiler import _VERB_SLOT
    rung = _RUNG
    lex = rung.lexicon
    c = Counter()
    unm_slot, unm_init, occ = Counter(), Counter(), Counter()
    by_family, by_proc = Counter(), Counter()
    for raw in texts:
        if not raw or not raw.strip():
            c["texts_empty"] += 1
            continue
        c["texts"] += 1
        for ss, se in sentences(raw):
            c["sentences"] += 1
            toks = tokens(raw[ss:se])
            words = [w for _, _, w in toks]
            c["tokens"] += len(words)
            occ.update(words)
            i = 0
            n = len(toks)
            while i < n:
                hit = rung._action_at(raw, ss, toks, words, i, [])
                prefix = raw[ss:ss + toks[i][0]]
                slot = _VERB_SLOT.search(prefix) is not None
                init = i == 0
                if hit is not None:
                    length, flag = hit
                    ids = lex.proc_ids(" ".join(words[i:i + length])) if length > 1 else lex.proc_ids(words[i])
                    c["action_events"] += 1
                    if flag == "AMBIGUOUS_ACTION":
                        c["action_ambiguous"] += 1
                    elif flag == "PROC_LEMMA_GUESS":
                        c["action_lemma_guess"] += 1
                    else:
                        c["action_unique_exact"] += 1
                    c["action_multiword"] += length > 1
                    if len(ids) == 1:
                        pid = next(iter(ids))
                        by_proc[pid] += 1
                        by_family[lex.proc_info[pid].family] += 1
                    if slot:
                        c["cand_slot"] += 1
                        c["cand_slot_mapped"] += 1
                    if init:
                        c["cand_init"] += 1
                        c["cand_init_mapped"] += 1
                    c["action_in_verb_slot"] += slot
                    c["action_sentence_initial"] += init
                    i += length
                    continue
                w = words[i]
                if slot:
                    if w in CLOSED_CLASS:
                        c["slot_closed_class"] += 1
                    elif lex.food_at(words, i) is not None or lex.tool_at(words, i) is not None:
                        c["slot_food_or_tool_word"] += 1
                    else:
                        c["cand_slot"] += 1
                        unm_slot[w] += 1
                        if init:
                            c["cand_init"] += 1
                            unm_init[w] += 1
                i += 1
    return {"c": c, "unm_slot": unm_slot, "unm_init": unm_init, "occ_unmapped_only": None, "occ": occ,
            "by_family": by_family, "by_proc": by_proc}


def _work(texts):
    return count_texts(texts)


def merge(into: dict, part: dict) -> None:
    for k in ("c", "unm_slot", "unm_init", "occ", "by_family", "by_proc"):
        into[k].update(part[k])


def stream_texts(family: str, sample: int | None, seed: str):
    from culinarystate.extraction import rung_a_measure as M
    from culinarystate.recipes import corpus
    if family == "FOODCOM":
        it = corpus.iter_foodcom()
    elif family == "WIKIBOOKS":
        it = corpus.iter_rec_corpora(families=("WIKIBOOKS",))
    elif family == "GUTENBERG_SEGMENT":
        it = (r for r in corpus.iter_rec_corpora(families=("GUTENBERG_SEGMENT",)) if not r["extra"].get("raw_segment_missing"))
    else:
        raise ValueError(family)
    if sample:
        it = M.seeded_sample(it, seed, sample)
    for rec in it:
        steps = [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]
        yield "\n".join(steps)


def batches(it, n):
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) >= n:
            yield buf
            buf = []
    if buf:
        yield buf


def fold_forms(counts: Counter) -> dict[str, str]:
    """surface -> base form: an inflected form is mapped onto a base that also occurs (the most frequent one if several)."""
    out = {}
    for w in counts:
        cands = []
        if w.endswith("ing") and len(w) > 5:
            b = w[:-3]
            cands += [b, b + "e"] + ([b[:-1]] if len(b) > 2 and b[-1] == b[-2] else [])
        if w.endswith("ied") and len(w) > 4:
            cands.append(w[:-3] + "y")
        if w.endswith("ed") and len(w) > 4:
            b = w[:-2]
            cands += [b, b + "e"] + ([b[:-1]] if len(b) > 2 and b[-1] == b[-2] else [])
        if w.endswith("ies") and len(w) > 4:
            cands.append(w[:-3] + "y")
        if w.endswith("es") and len(w) > 3:
            cands.append(w[:-2])
        if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
            cands.append(w[:-1])
        present = [b for b in cands if b != w and b in counts and len(b) > 2]
        out[w] = max(present, key=lambda b: counts[b]) if present else w
    # one level only: map chains to their final base
    for w in list(out):
        seen = 0
        while out[out[w]] != out[w] and seen < 3:
            out[w] = out[out[w]]
            seen += 1
    return out


def top_unmapped(agg: dict, bbc: set[str]) -> list[dict]:
    folded = fold_forms(agg["unm_slot"])
    by_base_slot, by_base_init, by_base_occ, forms = Counter(), Counter(), Counter(), {}
    for w, n in agg["unm_slot"].items():
        b = folded[w]
        by_base_slot[b] += n
        forms.setdefault(b, set()).add(w)
    for w, n in agg["unm_init"].items():
        by_base_init[folded.get(w, w)] += n
    for b, fs in forms.items():
        by_base_occ[b] = sum(agg["occ"].get(f, 0) for f in fs)
    rows = []
    for rank, (b, n) in enumerate(sorted(by_base_slot.items(), key=lambda kv: (-kv[1], kv[0])), 1):
        if n < MIN_COUNT:
            break
        rows.append({"rank": rank, "lemma": b, "slot_count": n, "sentence_initial_count": by_base_init.get(b, 0),
                     "occurrences_any_position": by_base_occ[b], "slot_share_pct": round(100.0 * n / by_base_occ[b], 1) if by_base_occ[b] else None,
                     "forms_merged": len(forms[b]), "in_bbc_spacy_list": b in bbc})
    return rows


def curve(rows: list[dict], total: int) -> dict:
    out, cum, ks = {}, 0, (1, 10, 50, 100, 200, 500, 1000)
    for i, r in enumerate(rows, 1):
        cum += r["slot_count"]
        if i in ks:
            out[f"top_{i}"] = round(100.0 * cum / total, 2) if total else None
    return out


def pct(a, b):
    return round(100.0 * a / b, 3) if b else None


def family_block(agg: dict, bbc: set[str], proc_info) -> tuple[dict, list[dict]]:
    c = agg["c"]
    rows = top_unmapped(agg, bbc)
    unm_slot_total = sum(agg["unm_slot"].values())
    unm_init_total = sum(agg["unm_init"].values())
    blk = {"status": "READ", "texts_with_steps": c["texts"], "texts_empty": c["texts_empty"], "sentences": c["sentences"], "tokens": c["tokens"],
           "action_events": c["action_events"], "action_events_mapped_to_proc_pct_by_construction": 100.0 if c["action_events"] else None,
           "action_events_unique_exact_surface": c["action_unique_exact"], "action_events_ambiguous_several_proc_ids": c["action_ambiguous"],
           "action_events_proc_lemma_guess": c["action_lemma_guess"], "action_events_multiword": c["action_multiword"],
           "pct_ambiguous": pct(c["action_ambiguous"], c["action_events"]), "pct_lemma_guess": pct(c["action_lemma_guess"], c["action_events"]),
           "action_events_in_a_verb_slot": c["action_in_verb_slot"], "action_events_sentence_initial": c["action_sentence_initial"],
           "events_per_text": round(c["action_events"] / c["texts"], 2) if c["texts"] else None,
           "verb_slot_tokens_closed_class": c["slot_closed_class"], "verb_slot_tokens_lexicon_food_or_tool": c["slot_food_or_tool_word"],
           "verb_candidates_in_slots": c["cand_slot"], "verb_candidates_mapped": c["cand_slot_mapped"],
           "verb_candidates_unmapped": unm_slot_total,
           "pct_verb_slot_candidates_mapped": pct(c["cand_slot_mapped"], c["cand_slot"]),
           "sentence_initial_candidates": c["cand_init"], "sentence_initial_mapped": c["cand_init_mapped"],
           "sentence_initial_unmapped": unm_init_total,
           "pct_sentence_initial_candidates_mapped": pct(c["cand_init_mapped"], c["cand_init"]),
           "distinct_unmapped_surfaces_in_slots": len(agg["unm_slot"]), "distinct_unmapped_lemmas_ge_min_count": len(rows),
           "unmapped_slot_occurrence_coverage_of_top_k_lemma_pct": curve(rows, unm_slot_total),
           "top200_unmapped_lemmas_share_of_unmapped_slot_tokens_pct": pct(sum(r["slot_count"] for r in rows[:TOP_N]), unm_slot_total),
           "actions_by_proc_family": dict(sorted(agg["by_family"].items(), key=lambda kv: -kv[1])),
           "distinct_proc_ids_used": len(agg["by_proc"])}
    return blk, rows[:TOP_N]


def run(root: Path, families, workers: int, sample: int | None, seed: str, out_dir: Path, name: str, batch: int) -> dict:
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.extraction.rung_a_lexicon import LEXICON_VERSION
    from culinarystate.quantity.rc2_dryrun import assert_counts_only
    t0 = time.time()
    bbc = set()
    p = root / BBC_LIST
    if p.is_file():
        with open(p, encoding="utf-8", newline="") as fh:
            bbc = {r["lemma"] for r in csv.DictReader(fh)}
    ref = RungA()
    res = {"record": "VERB_COVERAGE_CENSUS_S178", "tool_version": TOOL_VERSION, "item": "T3-C05-R1",
           "status": "AI_DRAFTED_PROPOSED_COUNTS_ONLY", "contains_recipe_text": False, "contains_recipe_ids": False,
           "counts_as_human_gate": False, "sample_texts_per_family": sample,
           "sample_seed_sha256": hashlib.sha256(seed.encode()).hexdigest() if sample else None,
           "lexicon_version": LEXICON_VERSION, "lexicon_fingerprint": ref.lexicon.fingerprint, "proc_ids_in_lexicon": len(ref.lexicon.proc_info),
           "proc_action_ids_in_lexicon": sum(1 for v in ref.lexicon.proc_info.values() if v.kind == "ACTION"),
           "min_count_for_listing": MIN_COUNT, "closed_class_words": len(CLOSED_CLASS), "families": {}, "workers": workers}
    ctx = get_context("spawn")
    out_dir.mkdir(parents=True, exist_ok=True)
    for fam in families:
        t1 = time.time()
        agg = {"c": Counter(), "unm_slot": Counter(), "unm_init": Counter(), "occ": Counter(), "by_family": Counter(), "by_proc": Counter()}
        with ctx.Pool(workers, initializer=_init) as pool:
            for part in pool.imap_unordered(_work, batches(stream_texts(fam, sample, seed), batch)):
                merge(agg, part)
        blk, rows = family_block(agg, bbc, ref.lexicon.proc_info)
        blk["seconds"] = round(time.time() - t1, 1)
        res["families"][fam] = blk
        suffix = f"_sample{sample}" if sample else ""
        with open(out_dir / f"verb_unmapped_top200_{fam}{suffix}.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["rank", "lemma", "slot_count", "sentence_initial_count", "occurrences_any_position", "slot_share_pct", "forms_merged", "in_bbc_spacy_list"])
            for r in rows:
                w.writerow([r["rank"], r["lemma"], r["slot_count"], r["sentence_initial_count"], r["occurrences_any_position"], r["slot_share_pct"],
                            r["forms_merged"], int(r["in_bbc_spacy_list"])])
        blk["top200_csv_sha256"] = hashlib.sha256((out_dir / f"verb_unmapped_top200_{fam}{suffix}.csv").read_bytes()).hexdigest()
        blk["top200_rows"] = len(rows)
        blk["top200_in_bbc_spacy_list"] = sum(1 for r in rows if r["in_bbc_spacy_list"])
    res["families"]["TASTESET"] = {"status": "NOT_AVAILABLE", "reason": "NO_INSTRUCTION_TEXT"}
    res["families"]["A1_BBC_GOOD_FOOD"] = {"status": "NOT_ON_THIS_SERVER", "reason": "D_003_BBC_DATA_NOT_PRESENT"}
    res["seconds_total"] = round(time.time() - t0, 1)
    assert_counts_only(res)
    suffix = f"_sample{sample}" if sample else ""
    (out_dir / f"{name}{suffix}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / f"{name}{suffix}.md").write_text(md(res, out_dir, suffix), encoding="utf-8")
    return res


def md(res: dict, out_dir: Path, suffix: str) -> str:
    L = ["# Rung A verb-coverage census, non-BBC families (S178, T3-C05-R1)", "",
         "Status: AI_DRAFTED / PROPOSED. Counts only; no recipe text. NON_CITABLE. A rule-based coverage count of a rule-based tagger: not an accuracy "
         f"estimate, not a gold score. Tool `{res['tool_version']}`; lexicon `{res['lexicon_version']}` fingerprint `{res['lexicon_fingerprint'][:16]}` "
         f"({res['proc_action_ids_in_lexicon']} ACTION PROC ids).",
         f"Sample: {res['sample_texts_per_family'] or 'full families'}. See the tool header for the definitions of ACTION event, verb slot, candidate and the closed-class list.", "",
         "## Table by family", "",
         "| family | texts with steps | ACTION events | ambiguous (several PROC ids) | PROC lemma guess | verb-slot candidates | mapped | **% mapped** | sentence-initial candidates | **% mapped** | distinct unmapped lemmas (>= 20) | top-200 share of unmapped slot tokens |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for f, b in res["families"].items():
        if b.get("status") != "READ":
            L.append(f"| {f} | {b['status']} | | | | | | | | | | {b.get('reason', '')} |")
            continue
        L.append(f"| {f} | {b['texts_with_steps']:,} | {b['action_events']:,} | {b['action_events_ambiguous_several_proc_ids']:,} ({b['pct_ambiguous']} %) | "
                 f"{b['action_events_proc_lemma_guess']:,} ({b['pct_lemma_guess']} %) | {b['verb_candidates_in_slots']:,} | {b['verb_candidates_mapped']:,} | "
                 f"**{b['pct_verb_slot_candidates_mapped']}** | {b['sentence_initial_candidates']:,} | **{b['pct_sentence_initial_candidates_mapped']}** | "
                 f"{b['distinct_unmapped_lemmas_ge_min_count']:,} | {b['top200_unmapped_lemmas_share_of_unmapped_slot_tokens_pct']} % |")
    for f, b in res["families"].items():
        if b.get("status") != "READ":
            continue
        L += ["", f"## {f}", "",
              f"{b['texts_with_steps']:,} texts, {b['sentences']:,} sentences, {b['tokens']:,} word tokens; {b['action_events']:,} ACTION events "
              f"({b['events_per_text']} per text; {b['action_events_in_a_verb_slot']:,} in a verb slot, {b['action_events_sentence_initial']:,} sentence-initial; "
              f"{b['action_events_multiword']:,} multi-word), {b['distinct_proc_ids_used']} distinct PROC ids used.",
              f"Verb-slot words excluded: {b['verb_slot_tokens_closed_class']:,} closed-class, {b['verb_slot_tokens_lexicon_food_or_tool']:,} lexicon food/tool words.",
              f"Coverage of the unmapped slot tokens by the top-k lemmas (%): {b['unmapped_slot_occurrence_coverage_of_top_k_lemma_pct']}.",
              f"ACTION events by PROC family: {b['actions_by_proc_family']}.",
              f"Top-200 list: `verb_unmapped_top200_{f}{suffix}.csv` (sha256 `{b['top200_csv_sha256'][:16]}`), {b['top200_in_bbc_spacy_list']} of the {b['top200_rows']} rows also in the BBC spaCy list."]
    L += ["", "## Reading and limits", "",
          "- 100 % of ACTION events map to PROC by construction; the informative numbers are the share of verb-slot candidates that map and the unmapped list.",
          "- No POS tagger on this server: a candidate is a word in a verb slot that is not a closed-class, food or tool word. Unmapped lemmas include adverbs, nouns and "
          "fragments; `slot_share_pct` and `sentence_initial_count` in the CSV help to separate verbs (high) from the rest (low).",
          "- Gutenberg is 19th-century prose: many unmapped slot words are archaic verbs and function words; its sentence-initial share is the least reliable.",
          "- The lists are single words with counts (minimum 20). They are vocabulary, not recipe text; the committed BBC list `registry/processes/unmapped_verbs.csv` is the precedent. Law-6 reviewer to confirm.",
          "- TASTEset has no instruction text; BBC is not on this server (D-003)."]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--sample", type=int, default=None)
    ap.add_argument("--seed", default="20261104")
    ap.add_argument("--batch", type=int, default=500)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--name", default="verb_coverage_census_v1")
    a = ap.parse_args(argv)
    if a.workers > 24:
        ap.error("at most 24 workers (shared server)")
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / OUT_DIR
    res = run(root, [f for f in a.families.split(",") if f], a.workers, a.sample, a.seed, out, a.name, a.batch)
    print(json.dumps({f: {k: b.get(k) for k in ("texts_with_steps", "action_events", "pct_verb_slot_candidates_mapped",
                                                "pct_sentence_initial_candidates_mapped", "seconds")}
                      for f, b in res["families"].items() if b.get("status") == "READ"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
