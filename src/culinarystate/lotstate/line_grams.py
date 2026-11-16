"""Step 2: ingredient line -> (ING, grams interval, basis).

Basis codes (``values.LINE_BASES``):
- ``STATED_MASS``  the text states a mass unit (g, kg, oz, lb, mg, package-stated mass): exact interval from the rc2
                   grammar (Q0). Layer 1, TEXT_STATED.
- ``SR_PORTION``   a volume or count converted with USDA SR Legacy ``food_portion`` weights of the ING's PROPOSED SR match.
                   PROPOSED basis (packet Q9), Q-level ``Q2_PROPOSED`` (below stated mass). Layer 2 style assumption:
                   ASSUMED_DEFAULT. The grams are an INTERVAL whenever the SR portions disagree (for example "1 onion"
                   spans the small to large SR item weights; "1 cup onion" spans the SR cup densities of every prep
                   state, unless the line names one). Never a point from a guess.
- ``UNKNOWN``      everything else; the reason is a code (NO_QUANTITY, QUALITATIVE, PACKAGE, NO_SR_MATCH, ...).

Rules kept from rc2: no gram without a trace; a line whose quantity has no unit gets no volume or count conversion
when the source is known to drop units (``unit_stripped_source``, Food.com): a bare number there is not a count.
The legacy parser and the rc2 module are untouched; the only pre-processing is U+2044 (fraction slash) -> '/'.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Mapping

from culinarystate.quantity.rc2_grounding import GroundingContext, ground_quantity_rc2
from culinarystate.quantity.units import lookup

from . import values as V
from .intervals import frac
from .sr_legacy import COUNT_UNIT_KEYS, SRLegacy

PREP_WORDS = ("chopped", "sliced", "diced", "shredded", "grated", "crushed", "mashed", "packed", "melted", "cubed",
              "minced", "ground", "sifted", "whole", "pureed", "puree", "halved", "peeled", "cooked", "raw", "dried",
              "powdered", "crumbled", "pieces", "slices", "cubes")
SIZE_ORDER = ("small", "medium", "large")
BAND_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
REASONS = ("STATED_MASS", "SR_VOLUME_DENSITY", "SR_COUNT_PORTION", "NO_QUANTITY", "QUALITATIVE", "PACKAGE_OR_REGIONAL",
           "UNSUPPORTED_EXPRESSION", "LOCALE_AMBIGUOUS", "NO_SR_MATCH", "NO_SR_PORTION", "FOODCOM_UNIT_STRIPPED",
           "FOODCOM_QP_LENGTH_MISMATCH", "ROUTE_OTHER", "EXCEPTION")


@dataclass(frozen=True)
class LineResult:
    basis: str                                   # STATED_MASS | SR_PORTION | UNKNOWN
    grams: tuple[Fraction, Fraction] | None
    q_level: str
    reason: str
    flags: tuple[str, ...] = ()
    fdc_id: int | None = None
    band: str = "NONE"
    ambiguous: bool = False                      # grams is a non-degenerate interval because of portion ambiguity

    def usable_grams(self, min_band: str) -> tuple[Fraction, Fraction] | None:
        """Grams, but an SR_PORTION conversion only when its SR match meets the band floor."""
        if self.grams is None:
            return None
        if self.basis == V.BASIS_SR_PORTION and BAND_RANK.get(self.band, 0) < BAND_RANK[min_band]:
            return None
        return self.grams

    def to_json(self) -> dict:
        d = {"basis": self.basis, "q_level": self.q_level, "reason": self.reason, "flags": list(self.flags),
             "sr_band": self.band, "ambiguous": self.ambiguous}
        if self.grams is not None:
            lo, hi = self.grams
            d["grams_low"], d["grams_high"] = float(lo), float(hi)
            d["grams_exact"] = [str(lo), str(hi)]
        if self.fdc_id is not None:
            d["fdc_id"] = self.fdc_id
        return d


def normalise_text(text: str) -> str:
    return (text or "").replace("⁄", "/").replace("∕", "/")


def _chan(ch: Mapping) -> tuple[Fraction, Fraction] | None:
    if ch.get("status") == "MEASURED":
        v = frac(ch["value"])
        return v, v
    if ch.get("status") == "RANGE":
        return frac(ch["low"]), frac(ch["high"])
    return None


def _prep_words(text: str) -> set[str]:
    low = text.lower()
    return {w for w in PREP_WORDS if re.search(rf"\b{w}", low)}


def resolve_line(text: str, *, schema: Mapping, context: GroundingContext, sr: SRLegacy | None, fdc_id: int | None,
                 band: str = "NONE", unit_stripped_source: bool = False, qp_mismatch: bool = False) -> LineResult:
    """Ground one ingredient line. ``fdc_id`` / ``band`` are the ING's PROPOSED SR match (AI_DRAFTED), if any."""
    flags: list[str] = []
    if qp_mismatch:
        return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, "FOODCOM_QP_LENGTH_MISMATCH", ("QUANTITY_NOT_PAIRED",))
    txt = normalise_text(text)
    try:
        r = ground_quantity_rc2(txt, context, schema=schema)
    except Exception:  # noqa: BLE001 - reported by code only
        return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, "EXCEPTION")
    if r.exact_mass is not None and r.mass_route in ("AST_EXACT_PHYSICAL", "AST_PACKAGE_SOURCE_STATED",
                                                     "PARENTHETICAL_SOURCE_STATED"):
        lo, hi = r.exact_mass
        return LineResult(V.BASIS_STATED_MASS, (frac(lo), frac(hi)), V.Q_STATED_MASS, "STATED_MASS",
                          tuple(r.flags), fdc_id, band, ambiguous=lo != hi)
    rec = r.record
    parsed = rec["parsed"]
    vol, cnt = _chan(rec["volume_ml"]), _chan(rec["count"])
    unit_raw = parsed.get("unit_raw")
    if r.mass_route in ("NO_QUANTITY",):
        return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, "NO_QUANTITY", tuple(r.flags), fdc_id, band)
    if r.mass_route == "QUALITATIVE":
        return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, "QUALITATIVE", tuple(r.flags), fdc_id, band)
    if unit_stripped_source and unit_raw is None and (cnt is not None or vol is not None):
        return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, "FOODCOM_UNIT_STRIPPED", ("BARE_NUMBER_NOT_A_COUNT",),
                          fdc_id, band)
    if vol is None and cnt is None:
        reason = ("LOCALE_AMBIGUOUS" if r.unit_resolution == "VOLUME_LOCALE_AMBIGUOUS" else
                  "PACKAGE_OR_REGIONAL" if r.unit_resolution in ("PACKAGE", "REGIONAL_NO_STANDARD") else
                  "UNSUPPORTED_EXPRESSION" if r.mass_route in ("UNSUPPORTED_EXPRESSION", "OPEN_OR_UNAVAILABLE_OPERAND")
                  else "ROUTE_OTHER")
        return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, reason, tuple(r.flags), fdc_id, band)
    if fdc_id is None or sr is None:
        return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, "NO_SR_MATCH", tuple(r.flags), fdc_id, band)
    prep = _prep_words(txt)
    if vol is not None:
        ports = sr.volume_portions(fdc_id)
        chosen = [p for p in ports if set(p.descriptor.split()) & prep] if prep else []
        if prep and not chosen:
            flags.append("PORTION_STATE_NOT_MATCHED")
        chosen = chosen or ports
        if not chosen:
            return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, "NO_SR_PORTION", tuple(r.flags), fdc_id, band)
        d_lo, d_hi = min(p.g_per_ml for p in chosen), max(p.g_per_ml for p in chosen)
        g = (vol[0] * d_lo, vol[1] * d_hi)
        return LineResult(V.BASIS_SR_PORTION, g, V.Q_SR_PORTION, "SR_VOLUME_DENSITY", (*r.flags, *flags), fdc_id, band,
                          ambiguous=g[0] != g[1])
    unit_key = rec["count"].get("unit")
    avail = sr.count_portions(fdc_id)
    if unit_key in (None, "item") and unit_raw is None:     # "2 garlic cloves": the count unit is a word of the line
        for w in re.findall(r"[a-z]+", txt.lower()):
            u = lookup(w)
            if u is not None and u.key in COUNT_UNIT_KEYS and any(p.unit_key == u.key for p in avail):
                unit_key = u.key
                flags.append("COUNT_UNIT_FROM_TEXT")
                break
    ports = [p for p in avail if p.unit_key == ("item" if unit_key in (None, "item") else unit_key)]
    size = parsed.get("size")
    if size:
        sized = [p for p in ports if p.size == size]
        if sized:
            ports = sized
        else:
            flags.append("SIZE_NOT_IN_SR")
    if not ports:
        return LineResult(V.BASIS_UNKNOWN, None, V.Q_UNKNOWN, "NO_SR_PORTION", tuple(r.flags), fdc_id, band)
    w_lo, w_hi = min(p.grams_per_unit for p in ports), max(p.grams_per_unit for p in ports)
    g = (cnt[0] * w_lo, cnt[1] * w_hi)
    return LineResult(V.BASIS_SR_PORTION, g, V.Q_SR_PORTION, "SR_COUNT_PORTION", (*r.flags, *flags), fdc_id, band,
                      ambiguous=g[0] != g[1])
