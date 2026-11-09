"""Public mode for the hosted demo (S177, lane SCIFIX-ROUTER; FINAL-GOV review row 2). DEMO_ONLY, NON_CITABLE.

The recipe-corpus knowledge-graph edges the demo reads (substitutions, "what comes next", process candidates, typical
durations, tool requirements) are co-occurrence aggregates. Most of them were computed from the BBC Good Food corpus,
which is third-party, local-research-only data (D-003, registry LOCAL_RESEARCH_ONLY): fine for a local demo on the
researcher's own machine (deployment plan H-2), not for anything hosted. The SU-EATABLE carbon figures have an UNVERIFIED
upstream licence and the deployment plan excludes them from anything public. Public mode therefore

  * drops every KGE edge that is BBC-derived BEFORE any candidate is generated, and
  * empties the carbon figures.

An edge is BBC-derived when its ``corpus_ids`` or ``support.by_source_family`` include ``BBCGF-A1`` (the FINAL-GOV
rule) or, for edges that carry neither field (the PROC_TYPICAL_DURATION edges), its ``provenance.source_ids`` include the
BBC source record ``SRC-000002`` (an extension of the FINAL-GOV wording: without it all 39 duration edges would stay).

Switch (first match wins): explicit argument / command-line flag, then environment ``CS_DEMO_PUBLIC`` (1 / true / yes /
on / public = ON; 0 / false / no / off / local = OFF; any other value fails closed to ON), then automatic: ON for a hosted
build (``CS_DEMO_HOSTED`` or a platform marker such as ``PORT``, ``SPACE_ID``, ``K_SERVICE``, or a server bound to a
non-loopback address), OFF for local use on the Mac. If you tunnel a local demo to the public, set ``CS_DEMO_PUBLIC=1``.

Counts and codes only; no recipe text.
"""
from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

ENV_PUBLIC = "CS_DEMO_PUBLIC"
BBC_CORPUS_ID = "BBCGF-A1"
BBC_SOURCE_ID = "SRC-000002"       # SRC ledger record of the BBC Good Food corpus (third-party copyright)
HOSTED_MARKERS = ("CS_DEMO_HOSTED", "PORT", "SPACE_ID", "K_SERVICE", "FLY_APP_NAME", "RENDER", "DYNO",
                  "RAILWAY_ENVIRONMENT", "WEBSITE_SITE_NAME")
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1", "")
_TRUE = ("1", "true", "yes", "on", "public")
_FALSE = ("0", "false", "no", "off", "local")
CARBON_PREDICATE = "ING_CARBON_FOOTPRINT"


@dataclass(frozen=True)
class Mode:
    public: bool
    source: str          # ARGUMENT | ENV | ENV_INVALID_FAIL_CLOSED | HOSTED_MARKER | NON_LOOPBACK_HOST | DEFAULT_LOCAL

    @property
    def name(self) -> str:
        return "public" if self.public else "local"


def parse_flag(value: str | None) -> bool | None:
    """True / False for a recognised value, None for an unset or empty one; raises ValueError for anything else."""
    if value is None or not value.strip():
        return None
    v = value.strip().lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise ValueError(f"unrecognised {ENV_PUBLIC} value")


def resolve(explicit: bool | None = None, *, env: Mapping[str, str] | None = None, host: str | None = None) -> Mode:
    """The mode in force (see the module docstring for the precedence)."""
    env = os.environ if env is None else env
    if explicit is not None:
        return Mode(bool(explicit), "ARGUMENT")
    try:
        flag = parse_flag(env.get(ENV_PUBLIC))
    except ValueError:
        return Mode(True, "ENV_INVALID_FAIL_CLOSED")      # an unreadable switch never opens the BBC-derived data
    if flag is not None:
        return Mode(flag, "ENV")
    if any(env.get(k) for k in HOSTED_MARKERS):
        return Mode(True, "HOSTED_MARKER")
    if host is not None and host not in LOOPBACK_HOSTS:
        return Mode(True, "NON_LOOPBACK_HOST")
    return Mode(False, "DEFAULT_LOCAL")


def is_bbc_derived(edge: Mapping[str, Any]) -> bool:
    """True when the edge's corpus ids or per-family support name BBCGF-A1 (or, with neither field, its source ids name
    the BBC source record). A key present with a zero count still counts: the edge was computed over BBC recipes."""
    if BBC_CORPUS_ID in (edge.get("corpus_ids") or ()):
        return True
    support = edge.get("support") or {}
    if BBC_CORPUS_ID in (support.get("by_source_family") or {}):
        return True
    if edge.get("corpus_ids") is None and support.get("by_source_family") is None:
        return BBC_SOURCE_ID in ((edge.get("provenance") or {}).get("source_ids") or ())
    return False


def filter_edges(edges: Iterable[Mapping[str, Any]], public: bool) -> tuple[list, Counter]:
    """(kept edges, dropped counts by predicate). Local mode keeps everything. Public mode drops BBC-derived edges and
    every carbon edge (the carbon figures are emptied whatever their corpus)."""
    kept: list = []
    dropped: Counter = Counter()
    for e in edges:
        if public and (e.get("predicate") == CARBON_PREDICATE or is_bbc_derived(e)):
            dropped[e.get("predicate") or "UNKNOWN_PREDICATE"] += 1
        else:
            kept.append(e)
    return kept, dropped


def describe(mode: Mode, dropped: Mapping[str, int] | None = None) -> dict:
    """What the page and every response say about the mode in force (codes and counts only)."""
    return {"mode": mode.name, "public": mode.public, "source": mode.source,
            "bbc_derived_edges": "EXCLUDED" if mode.public else "INCLUDED_LOCAL_ONLY",
            "carbon_figures": "EXCLUDED" if mode.public else "INCLUDED_LOCAL_ONLY",
            "dropped_edges_by_predicate": dict(sorted((dropped or {}).items()))}
