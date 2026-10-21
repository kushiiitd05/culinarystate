#!/usr/bin/env python3
"""CulinaryLinkDecision final evaluation set: sampling frame (no labels). Gold FOOD/NAME mentions from the CALIBRATION, DEV and TEST splits of both datasets (mention strings only; no linker training or selection ever used them),
deduplicated by normalised surface; excluded: surfaces of the viewed linker sets and of the previous sealed 441 set. Strata by gallery/ledger relation, deterministic hash order, targets fixed in the protocol; S5 regional unavailable.
Output LOCAL ONLY: features/v2dm/final_link_frame.jsonl"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))
import e1_e2_calibration as E  # noqa: E402
import e2_signal_calibration as M  # noqa: E402
from build_linker_data import norm  # noqa: E402

TARGET = {"S1_exact_gallery_known": 150, "S4_ambiguous_generic_head": 120, "S3_head_not_in_ledger(likely novel)": 180, "S6_long_qualified(>=3 tokens)": 150, "S2_alias_like(head in ledger, surface not)": 250}


def main():
    D = json.load(open(ROOT / "features/linker_data_v2.json"))
    prev = {json.loads(l)["mention"] for l in open(ROOT / "features/v2dm/fresh_link_frame.jsonl")}
    viewed = {q["s"] for p in ("dev_alias", "unseen_alias", "dev", "unseen_concept") for q in D["queries"][p]} | prev
    gallery = {s for s, _ in D["full_gallery_seen_concepts"]}
    led, toks, heads, _ = M.ledger_maps()
    from collections import Counter as C
    head_count = C(s.split()[-1] for s in led if s)
    frame = {}
    for part in ("calibration", "dev", "test"):
        for ds in ("tasteset", "recipedb3"):
            sp, docs, _ = E.load(ds)
            for text, gold in docs(sp[part]):
                for g in gold:
                    s_, e_, lab = g[:3]
                    if lab != M.FOOD[ds]:
                        continue
                    w = norm(text[s_:e_])
                    if not w or w in viewed or w in frame:
                        continue
                    a = text.rfind("\n", 0, s_) + 1
                    b = text.find("\n", e_)
                    frame[w] = {"mention": w, "dataset": ds, "split": part, "context": text[a:(b if b >= 0 else len(text))].strip()[:300]}
    rows = []
    for w, r in frame.items():
        t = w.split()
        if w in gallery:
            st = "S1_exact_gallery_known"
        elif head_count.get(t[-1], 0) >= 8:
            st = "S4_ambiguous_generic_head"
        elif t[-1] not in heads:
            st = "S3_head_not_in_ledger(likely novel)"
        elif len(t) >= 3:
            st = "S6_long_qualified(>=3 tokens)"
        else:
            st = "S2_alias_like(head in ledger, surface not)"
        rows.append({**r, "stratum": st, "hash": hashlib.sha256(("final-v1|" + w).encode()).hexdigest()})
    avail = Counter(r["stratum"] for r in rows)
    sel = []
    for s_ in TARGET:
        sel += sorted([r for r in rows if r["stratum"] == s_], key=lambda r: r["hash"])[:TARGET[s_]]
    p = ROOT / "features/v2dm/final_link_frame.jsonl"
    open(p, "w").write("\n".join(json.dumps(r) for r in sel) + "\n")
    print("frame", len(frame), "available", dict(avail), "selected", dict(Counter(r["stratum"] for r in sel)), "total", len(sel), "splits", dict(Counter(r["split"] for r in sel)), "datasets", dict(Counter(r["dataset"] for r in sel)))
    print("frame sha256", hashlib.sha256(open(p, "rb").read()).hexdigest()[:16])


if __name__ == "__main__":
    main()
