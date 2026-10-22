"""STEP 07I: per-recipe identity features (deterministic; no Python hash(); no model). Used for exact grouping, candidate retrieval and interpretable pair features."""
from __future__ import annotations

import hashlib
import re
import zlib

import numpy as np

PRIME = (1 << 31) - 1
_R = np.random.RandomState(7_070_707)
MH_A = _R.randint(1, PRIME, size=64, dtype=np.int64)
MH_B = _R.randint(0, PRIME, size=64, dtype=np.int64)
STOP_TITLE = {"easy", "quick", "best", "simple", "homemade", "classic", "perfect", "the", "a", "my", "our", "recipe", "recipes", "how", "to", "make", "delicious", "super", "favourite", "favorite", "ultimate", "authentic", "traditional", "old", "fashioned", "style", "and", "with", "of", "in"}


def norm_alnum(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(s or "").lower())


def norm_words(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", str(s or "").lower())


def text_hash(title, ingredient_lines, steps) -> str:
    """normalised-text hash: lower-cased title + ingredient lines + steps with every non-alphanumeric removed"""
    return hashlib.sha256(norm_alnum(title + "|" + "|".join(ingredient_lines) + "|" + "|".join(steps)).encode()).hexdigest()


def title_key(title: str) -> str:
    toks = sorted(w for w in norm_words(title) if w not in STOP_TITLE and not w.isdigit())
    return " ".join(toks)


def shingles(words: list[str], k: int = 4) -> list[int]:
    if len(words) < k:
        return [zlib.crc32(" ".join(words).encode())] if words else []
    return list({zlib.crc32(" ".join(words[i:i + k]).encode()) for i in range(len(words) - k + 1)})


def minhash(hashes: list[int], n: int) -> bytes | None:
    if not hashes:
        return None
    h = np.asarray(hashes, dtype=np.int64) % PRIME
    sig = ((MH_A[:n, None] * h[None, :] + MH_B[:n, None]) % PRIME).min(axis=1).astype(np.uint32)
    return sig.tobytes()


def mh_sim(a: bytes | None, b: bytes | None):
    if a is None or b is None:
        return None
    x, y = np.frombuffer(a, dtype=np.uint32), np.frombuffer(b, dtype=np.uint32)
    return float((x == y).mean())


def bands(sig: bytes | None, rows: int):
    if sig is None:
        return []
    x = np.frombuffer(sig, dtype=np.uint32)
    return [(i, hashlib.md5(x[i * rows:(i + 1) * rows].tobytes()).hexdigest()[:16]) for i in range(len(x) // rows)]
