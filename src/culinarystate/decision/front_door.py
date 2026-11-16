"""Front door (S171, D-075 M4): SSOT §39 router -> branch handler, with explicit abstention for unbuilt branches.

Handlers are injected (``{"TRANSFORMATION": f(q, recipe_text=None), "RELATIONSHIP": f(q), ...}``) so this module loads
no ledger. A branch without a handler abstains with ABSTAIN_NOT_BUILT; MULTIMODAL is ABSTAIN_UNSUPPORTED; UNKNOWN
or MALFORMED asks. A handler error becomes ABSTAIN_ERROR carrying the exception class only. Output is DEMO_ONLY and
never citable (EVD rows are E3, unverified).
"""
from __future__ import annotations

from typing import Callable, Mapping

from culinarystate.decision import query_router as QR
from culinarystate.decision import safety as SF

LABELS = ("DEMO_ONLY", "NON_CITABLE", "EVIDENCE_E3_UNVERIFIED")
MESSAGES = {
    "MULTIMODAL": "Images, audio and video are not supported yet, so I can't judge this.",
    "NOT_BUILT": "This kind of question ({branch}) is not wired up yet, so I won't guess an answer.",
    "ASK": "I couldn't tell what you're asking. Please name the food, the process and what you care about "
           "(for example vitamin C, texture or colour).",
    "ERROR": "Something failed while answering, so I'm not giving an answer.",
    "SAFETY": SF.MESSAGE,
}


def _out(route: dict, mode: str, answer: str, **extra) -> dict:
    return {"route": route, "mode": mode, "answer": answer, "cited": list(extra.pop("cited", [])),
            "labels": list(LABELS), "citable": False, **extra}


def respond(query: str, *, handlers: Mapping[str, Callable], recipe_text: str | None = None) -> dict:
    route = QR.route(query)
    b = route["branch"]
    if b == "SAFETY":                       # S176: refuse and refer; no handler is consulted, no number is produced
        return _out(route, "ABSTAIN_SAFETY", MESSAGES["SAFETY"], reason=SF.REASON, referral=list(SF.REFERRAL))
    if b == "MULTIMODAL":
        return _out(route, "ABSTAIN_UNSUPPORTED", MESSAGES["MULTIMODAL"])
    if b in ("UNKNOWN", "MALFORMED"):
        return _out(route, "ASK", MESSAGES["ASK"])
    h = handlers.get(b)
    if h is None:
        return _out(route, "ABSTAIN_NOT_BUILT", MESSAGES["NOT_BUILT"].format(branch=b.lower()))
    try:
        res = h(query, recipe_text=recipe_text) if b == "TRANSFORMATION" else h(query)
    except Exception as exc:  # noqa: BLE001 - never leak handler internals to the user
        return _out(route, "ABSTAIN_ERROR", MESSAGES["ERROR"], error_class=type(exc).__name__)
    return _out(route, res.get("mode", "ANSWER"), res.get("answer", ""), cited=res.get("cited", []),
                detail={k: v for k, v in res.items() if k not in ("mode", "answer", "cited")})
