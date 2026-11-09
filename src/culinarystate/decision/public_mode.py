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

Per-request guard (S178 FIX-GOV, GOV-4): a server bound to 127.0.0.1 behind a tunnel (cloudflared, ngrok, ssh -R, a
reverse proxy) still resolves to local mode, so the switch alone fails open for that route. ``forwarded_request_signal``
therefore treats a request as public when it carries a forwarding header (``X-Forwarded-For``, ``Forwarded``,
``X-Forwarded-Host``, ``CF-Connecting-IP`` and the others in ``FORWARDING_HEADERS``), a Host header that is not a loopback
name or address, no Host header at all, or comes from a non-loopback peer. ``refusal_for_request`` returns the 503 body
the server sends when such a request meets a context whose mode is not public (or unknown: fail closed). The
researcher's own browser on the same machine (Host ``localhost`` / ``127.0.0.1`` / ``[::1]``, loopback peer, no
forwarding header) is served as before.

Counts and codes only; no recipe text.
"""
from __future__ import annotations

import ipaddress
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
# Headers a proxy or tunnel adds (lower-case; HTTP header names are case-insensitive). Any one of them marks the request public.
FORWARDING_HEADERS = ("x-forwarded-for", "forwarded", "x-forwarded-host", "x-forwarded-proto", "x-forwarded-server",
                      "cf-connecting-ip", "cf-ray", "true-client-ip", "x-real-ip", "x-original-host", "via")
LOOPBACK_NAMES = ("localhost",)
REFUSAL_REASON = "LOCAL_MODE_NOT_PUBLIC"
REFUSAL_MESSAGE = ("This demo runs in local mode, which is for the researcher's own machine only, so it does not answer "
                   "requests that come through a tunnel, proxy or another computer. To share it, restart it in public mode "
                   "(CS_DEMO_PUBLIC=1 or --public).")


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


# ------------------------------------------------------------------ per-request guard (GOV-4)
def _is_loopback_address(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value.strip().strip("[]").split("%", 1)[0])
    except ValueError:
        return False
    mapped = getattr(ip, "ipv4_mapped", None)
    return bool(ip.is_loopback or (mapped is not None and mapped.is_loopback))


def _host_name(host_header: str) -> str:
    """The name or address part of a Host header ('127.0.0.1:8765' -> '127.0.0.1', '[::1]:8765' -> '::1')."""
    h = host_header.strip().lower()
    if h.startswith("["):
        return h[1:h.find("]")] if "]" in h else h[1:]
    if h.count(":") == 1:
        h = h.split(":", 1)[0]
    return h.rstrip(".")


def _header_map(headers: Any) -> dict[str, str]:
    items = headers.items() if hasattr(headers, "items") else headers
    return {str(k).strip().lower(): str(v) for k, v in items}


def forwarded_request_signal(headers: Any, peer: str | None) -> str | None:
    """A code saying why this request must be treated as public, or None for a plain request from this machine.

    ``headers``: a mapping or ``email.message.Message`` (the http.server headers); ``peer``: the TCP peer address.
    Codes: FORWARDING_HEADER:<name> | MISSING_HOST_HEADER | NON_LOOPBACK_HOST_HEADER | NON_LOOPBACK_PEER.
    """
    h = _header_map(headers)
    for name in FORWARDING_HEADERS:
        if name in h:
            return f"FORWARDING_HEADER:{name}"
    if peer is not None and not _is_loopback_address(peer):
        return "NON_LOOPBACK_PEER"
    host = h.get("host")
    if host is None or not host.strip():
        return "MISSING_HOST_HEADER"          # fail closed: a browser always sends Host
    name = _host_name(host)
    if name in LOOPBACK_NAMES or _is_loopback_address(name):
        return None
    return "NON_LOOPBACK_HOST_HEADER"


def refusal_for_request(mode_info: Mapping[str, Any] | None, headers: Any, peer: str | None) -> dict | None:
    """The 503 body when a public-looking request meets a context that is not in public mode (unknown mode = not public)."""
    public = bool(mode_info.get("public")) if isinstance(mode_info, Mapping) else False
    if public:
        return None
    signal = forwarded_request_signal(headers, peer)
    if signal is None:
        return None
    return {"error": REFUSAL_MESSAGE, "reason": REFUSAL_REASON, "signal": signal,
            "mode": (mode_info or {}).get("mode", "unknown") if isinstance(mode_info, Mapping) else "unknown"}
