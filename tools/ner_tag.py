#!/usr/bin/env python3
"""Tag ingredient lines with the runtime encoder NER, or replay its TASTEset test score (§257B deterministic replay).

  /opt/anaconda3/envs/recsys_env/bin/python tools/ner_tag.py "2 cups finely chopped fresh spinach"
  /opt/anaconda3/envs/recsys_env/bin/python tools/ner_tag.py --replay      # TASTEset test split (seed 7)
Model: data/interim/models/ner/deberta-v3-base_crf (pulled from the A100; git-ignored). The replay must match the
score in its tagger.json (trained on the server) within rounding, else the runtime path differs from training.
"""
import argparse
import json
import random
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ner.encoder_tagger import EncoderTagger  # noqa: E402
from culinarystate.scoring.metrics import corpus_span_scores  # noqa: E402

MODEL = ROOT / "data" / "interim" / "models" / "ner" / "deberta-v3-base_crf"
TASTE = ROOT / "data" / "raw" / "tasteset" / "TASTEset.csv"


def test_docs() -> list:
    d = pd.read_csv(TASTE)
    docs = [(r.ingredients, [(e["start"], e["end"], e["type"]) for e in json.loads(r.ingredients_entities)])
            for r in d.itertuples()]
    ids = list(range(len(docs)))
    random.Random(7).shuffle(ids)                       # same split as gpu/ner_tasteset/train_ner.py
    return [docs[i] for i in sorted(ids[int(0.85 * len(docs)):])]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?")
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--model", default=str(MODEL))
    a = ap.parse_args()
    t = EncoderTagger(a.model)
    if a.replay:
        pairs = [(gold, t.tag(text)) for text, gold in test_docs()]
        f1 = corpus_span_scores(pairs, "exact")["micro"]["f1"]
        print(json.dumps({"replay_test_exact_f1": f1, "trained_test_exact_f1": t.meta["test_exact_f1"],
                          "device": t.dev, "n": len(pairs)}))
        return
    print(json.dumps([{"start": s, "end": e, "label": lab, "text": a.text[s:e]} for s, e, lab in t.tag(a.text)]))


if __name__ == "__main__":
    main()
