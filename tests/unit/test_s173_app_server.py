"""S173 / M6: stdlib demo server — validation, rate limit, JSON API, static page. Fake context, no ledgers."""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

from culinarystate.app import server as S


class FakeCtx:
    def __init__(self):
        self.calls = []

    def respond(self, q, recipe_text=None):
        self.calls.append((q, recipe_text))
        return {"route": {"branch": "TRANSFORMATION"}, "mode": "ANSWER", "answer": "x [EVD-000001]",
                "cited": ["EVD-000001"], "labels": ["DEMO_ONLY"], "citable": False}


def test_validate_accepts_and_trims():
    q, r = S.validate({"question": "  Does boiling destroy vitamin C?  ", "recipe_text": "Boil it."})
    assert q == "Does boiling destroy vitamin C?" and r == "Boil it."
    assert S.validate({"question": "Why?"})[1] is None


@pytest.mark.parametrize("payload", [{}, {"question": 3}, {"question": "x" * 501}, {"question": "ok", "recipe_text": "y" * 6001},
                                     {"question": "ok", "recipe_text": ["no"]}])
def test_validate_rejects_bad_payloads(payload):
    with pytest.raises(S.BadRequest):
        S.validate(payload)


def test_rate_limiter_blocks_after_budget():
    rl = S.RateLimiter(per_minute=3)
    assert [rl.allow("1.2.3.4", now=0.0) for _ in range(4)] == [True, True, True, False]
    assert rl.allow("1.2.3.4", now=61.0) and rl.allow("5.6.7.8", now=0.0)


@pytest.fixture
def live():
    ctx = FakeCtx()
    srv = S.make_server(("127.0.0.1", 0), ctx, per_minute=100)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}", ctx
    srv.shutdown()


def _post(url, body):
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(req, timeout=5)


def test_live_ask_health_page_and_errors(live):
    base, ctx = live
    with _post(base + "/api/ask", json.dumps({"question": "Does boiling destroy vitamin C?"}).encode()) as r:
        out = json.loads(r.read())
    assert out["mode"] == "ANSWER" and out["citable"] is False and ctx.calls == [("Does boiling destroy vitamin C?", None)]
    with urllib.request.urlopen(base + "/api/health", timeout=5) as r:
        assert json.loads(r.read())["status"] == "ok"
    with urllib.request.urlopen(base + "/", timeout=5) as r:
        page = r.read().decode()
        assert "<title>" in page and r.headers["Content-Security-Policy"]
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(base + "/api/ask", b"not json")
    assert e.value.code == 400
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(base + "/nope", timeout=5)
    assert e.value.code == 404


def test_handler_error_is_500_without_detail(live):
    base, ctx = live
    ctx.respond = lambda q, recipe_text=None: (_ for _ in ()).throw(RuntimeError("secret"))
    with pytest.raises(urllib.error.HTTPError) as e:
        _post(base + "/api/ask", json.dumps({"question": "x"}).encode())
    assert e.value.code == 500 and b"secret" not in e.value.read()
