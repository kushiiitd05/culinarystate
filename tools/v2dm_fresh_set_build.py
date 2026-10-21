#!/usr/bin/env python3
"""Fresh linker / NIL evaluation set, step 1 (sampling frame, no labels): FOOD/NAME gold mentions from the two CALIBRATION splits (never used for linker selection; v1 TEST not used),
deduplicated by normalised surface, with surfaces of the already-viewed linker query sets excluded. Strata by gallery/ledger relation (deterministic hash order). Output is LOCAL ONLY (git-ignored):
features/v2dm/fresh_link_frame.jsonl. Labels come later from Kush + Parv (independent), with candidates pooled from all systems AFTER the systems are frozen.
  python tools/v2dm_fresh_set_build.py"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))
import e1_e2_calibration as E  # noqa: E402
import e2_signal_calibration as M  # noqa: E402
from build_linker_data import norm  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

TARGET = {"S1_exact_gallery_known": 60, "S5_regional": 40, "S4_ambiguous_generic_head": 60, "S3_head_not_in_ledger(likely novel)": 120, "S6_long_qualified(>=3 tokens)": 40, "S2_alias_like(head in ledger, surface not)": 160}
ORDER = list(TARGET)


def main():
    D = json.load(open(ROOT / "features/linker_data_v2.json"))
    viewed = {q["s"] for p in ("dev_alias", "unseen_alias", "dev", "unseen_concept") for q in D["queries"][p]}
    gallery = {s for s, _ in D["full_gallery_seen_concepts"]}
    led, toks, heads, units = M.ledger_maps()
    head_count = Counter(s.split()[-1] for s in led if s)
    st = LedgerStore()
    regional = {t for a in st.all_latest("ALIAS") if a["status"] == "ACTIVE" and a.get("language") not in (None, "en") for t in norm(a["normalized"]).split()}
    frame = {}
    for ds in ("tasteset", "recipedb3"):
        sp, docs, _ = E.load(ds)
        fl = M.FOOD[ds]
        for text, gold in docs(sp["calibration"]):
            for g in gold:
                s_, e_, lab = g[:3]
                if lab != fl:
                    continue
                w = norm(text[s_:e_])
                if not w or w in viewed or w in frame:
                    continue
                a = text.rfind("\n", 0, s_) + 1
                b = text.find("\n", e_)
                frame[w] = {"mention": w, "dataset": ds, "context": text[a:(b if b >= 0 else len(text))].strip()[:300]}
    rows = []
    for w, r in frame.items():
        t = w.split()
        if w in gallery:
            st_ = "S1_exact_gallery_known"
        elif any(x in regional for x in t) and not all(x in toks for x in t):
            st_ = "S5_regional"
        elif head_count.get(t[-1], 0) >= 8:
            st_ = "S4_ambiguous_generic_head"
        elif t[-1] not in heads:
            st_ = "S3_head_not_in_ledger(likely novel)"
        elif len(t) >= 3:
            st_ = "S6_long_qualified(>=3 tokens)"
        else:
            st_ = "S2_alias_like(head in ledger, surface not)"
        rows.append({**r, "stratum": st_, "hash": hashlib.sha256(("fresh-v1|" + w).encode()).hexdigest()})
    sel = []
    avail = Counter(r["stratum"] for r in rows)
    for s_ in ORDER:
        pool = sorted([r for r in rows if r["stratum"] == s_], key=lambda r: r["hash"])
        sel += pool[:TARGET[s_]]
    outp = ROOT / "features/v2dm/fresh_link_frame.jsonl"
    open(outp, "w").write("\n".join(json.dumps(r) for r in sel) + "\n")
    print("frame mentions", len(frame), "| available per stratum", dict(avail), "| selected", Counter(r["stratum"] for r in sel), "| total", len(sel), "| datasets", Counter(r["dataset"] for r in sel))
    print("frame sha256", hashlib.sha256(open(outp, "rb").read()).hexdigest()[:16])


if __name__ == "__main__":
    main()
