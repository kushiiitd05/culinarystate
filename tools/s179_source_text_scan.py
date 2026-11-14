#!/usr/bin/env python3
"""Local normalized word-window comparison; output hashes only, never source excerpts.

This limited exact-match check cannot certify paraphrases, images, unprovided sources,
or final artifacts that have not been supplied. It never grants release clearance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


def source_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from source_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from source_strings(child)


def _windows(text, window):
    words = re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold())
    for start in range(len(words) - window + 1):
        yield hashlib.sha256(" ".join(words[start:start + window]).encode()).hexdigest()


def scan(sources, artifacts, *, window):
    if type(window) is not int or window <= 0:
        raise ValueError("window must be a positive integer")
    index = defaultdict(set)
    for path, texts in sources.items():
        for text in texts:
            for digest in _windows(text, window):
                index[digest].add(path)
    findings = []
    for path, text in sorted(artifacts.items()):
        for digest in sorted(set(_windows(text, window)) & index.keys()):
            findings.append({"artifact": path, "window_sha256": digest,
                             "source_paths": sorted(index[digest])})
    return {"record": "LIMITED_LOCAL_SOURCE_TEXT_SCAN", "window_words": window,
            "normalization": "NFKC_CASEFOLD_UNICODE_WORDS", "matched_windows": len(findings),
            "source_files": len(sources), "artifact_files": len(artifacts),
            "unique_source_windows": len(index), "findings": findings,
            "status": "POTENTIAL_SOURCE_TEXT_MATCHES" if findings else "NO_MATCHES_IN_SUPPLIED_SOURCES_ONLY",
            "release_clearance": False,
            "limitations": ["Supplied sources/artifacts only; absent corpora and later edits are not checked.",
                            "No paraphrase, short-excerpt, OCR or image detection.",
                            "Window size is a disclosed engineering setting, not a legal or scientific threshold."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-jsonl", action="append", default=[], type=Path)
    parser.add_argument("--source-text", action="append", default=[], type=Path)
    parser.add_argument("--artifact", action="append", required=True, type=Path)
    parser.add_argument("--window", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    sources = {}
    for path in args.source_jsonl:
        sources[str(path)] = [text for line in path.read_text().splitlines() if line.strip()
                              for text in source_strings(json.loads(line))]
    for path in args.source_text:
        sources[str(path)] = [path.read_text()]
    if not sources:
        parser.error("at least one source is required")
    report = scan(sources, {str(p): p.read_text() for p in args.artifact}, window=args.window)
    report["input_sha256"] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in args.source_jsonl + args.source_text + args.artifact}
    report["tool_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with args.out.open("x") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"], "matches:", report["matched_windows"], "release_clearance=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
