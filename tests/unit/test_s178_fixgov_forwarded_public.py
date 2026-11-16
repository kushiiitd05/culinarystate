"""S178 FIX-GOV (GOV-4): a local-mode demo reached through a tunnel or proxy must not serve BBC-derived content.

A request that carries a forwarding header (X-Forwarded-For, Forwarded, X-Forwarded-Host, CF-Connecting-IP, ...), a
non-loopback Host header, no Host header, or comes from a non-loopback peer is treated as public. If public mode is not
active the server answers 503 with a short reason and never calls the context. In public mode it serves as before.

No network and no socket: the handler is driven with an in-memory request (``_FakeSock``). Addresses are documentation
addresses (RFC 5737 / RFC 3849).
"""
from __future__ import annotations

import io
import json
import types

import pytest

from culinarystate.app import server as S
from culinarystate.decision import public_mode as PM


class _FakeSock:
    """Just enough of a socket for StreamRequestHandler: makefile('rb') reads the request, sendall collects the reply."""

    def __init__(self, raw: bytes):
        self._r, self.out = io.BytesIO(raw), bytearray()

    def makefile(self, mode, *a, **k):
        return self._r

    def sendall(self, b):
        self.out += b


class _Ctx:
    def __init__(self, info):
        self._info, self.calls = info, []

    def mode_info(self):
        return self._info

    def respond(self, q, recipe_text=None):
        self.calls.append(q)
        return {"mode": "ANSWER_CORPUS_PATTERN", "answer": "BBC-derived pattern", "demo_mode": self._info}


LOCAL = {"mode": "local", "public": False, "source": "DEFAULT_LOCAL"}
PUBLIC = {"mode": "public", "public": True, "source": "ENV"}


def _call(ctx, method="GET", path="/api/health", headers=None, body=b"", peer="127.0.0.1"):
    hdrs = {"Host": "127.0.0.1:8765"} if headers is None else dict(headers)
    if body:
        hdrs.setdefault("Content-Type", "application/json")
        hdrs["Content-Length"] = str(len(body))
    raw = f"{method} {path} HTTP/1.1\r\n".encode() + "".join(f"{k}: {v}\r\n" for k, v in hdrs.items()).encode() + b"\r\n" + body
    sock = _FakeSock(raw)
    S.make_handler(ctx, per_minute=100)(sock, (peer, 50000), types.SimpleNamespace())
    head, _, payload = bytes(sock.out).partition(b"\r\n\r\n")
    status = int(head.split(b" ", 2)[1])
    return status, payload


ASK = json.dumps({"question": "What can I use instead of butter?"}).encode()


# ------------------------------------------------------------------ pure rule in public_mode
@pytest.mark.parametrize("headers", [
    {"Host": "127.0.0.1:8765", "X-Forwarded-For": "203.0.113.5"},
    {"Host": "127.0.0.1:8765", "Forwarded": "for=203.0.113.5;proto=https"},
    {"Host": "127.0.0.1:8765", "X-Forwarded-Host": "demo.example.org"},
    {"Host": "127.0.0.1:8765", "CF-Connecting-IP": "203.0.113.5"},
    {"Host": "127.0.0.1:8765", "x-forwarded-for": "203.0.113.5"},                   # header names are case-insensitive
    {"Host": "127.0.0.1:8765", "X-Real-IP": "203.0.113.5"},
    {"Host": "demo.example.org"},                                                     # tunnel that keeps the public Host
    {"Host": "203.0.113.9:8765"},
    {},                                                                               # no Host header: fail closed
])
def test_forwarded_or_non_loopback_requests_are_detected(headers):
    assert PM.forwarded_request_signal(headers, "127.0.0.1") is not None


@pytest.mark.parametrize("host", ["127.0.0.1:8765", "localhost:8765", "LOCALHOST", "[::1]:8765", "127.0.0.2", "localhost."])
def test_plain_loopback_requests_are_local(host):
    assert PM.forwarded_request_signal({"Host": host}, "127.0.0.1") is None
    assert PM.forwarded_request_signal({"Host": host}, "::1") is None
    assert PM.forwarded_request_signal({"Host": host}, "::ffff:127.0.0.1") is None


def test_a_non_loopback_peer_is_public_even_without_headers():
    assert PM.forwarded_request_signal({"Host": "127.0.0.1:8765"}, "192.0.2.7") == "NON_LOOPBACK_PEER"
    assert PM.forwarded_request_signal({"Host": "127.0.0.1:8765"}, "2001:db8::5") == "NON_LOOPBACK_PEER"


def test_refusal_only_when_public_mode_is_off():
    fwd = {"Host": "127.0.0.1:8765", "X-Forwarded-For": "203.0.113.5"}
    assert PM.refusal_for_request(LOCAL, fwd, "127.0.0.1") is not None
    assert PM.refusal_for_request(None, fwd, "127.0.0.1") is not None               # mode unknown: fail closed
    assert PM.refusal_for_request({"mode": "local"}, fwd, "127.0.0.1") is not None  # no "public" key: fail closed
    assert PM.refusal_for_request(PUBLIC, fwd, "127.0.0.1") is None
    assert PM.refusal_for_request(LOCAL, {"Host": "localhost:8765"}, "127.0.0.1") is None
    r = PM.refusal_for_request(LOCAL, fwd, "127.0.0.1")
    assert r["reason"] == "LOCAL_MODE_NOT_PUBLIC" and r["signal"].startswith("FORWARDING_HEADER") and "203.0.113.5" not in json.dumps(r)


# ------------------------------------------------------------------ the server (socket-free test client)
def test_local_mode_with_x_forwarded_for_returns_503_and_never_answers():
    ctx = _Ctx(LOCAL)
    st, body = _call(ctx, "POST", "/api/ask", {"Host": "127.0.0.1:8765", "X-Forwarded-For": "203.0.113.5"}, ASK)
    assert st == 503 and ctx.calls == []
    d = json.loads(body)
    assert d["reason"] == "LOCAL_MODE_NOT_PUBLIC" and "CS_DEMO_PUBLIC=1" in d["error"] and b"BBC-derived pattern" not in body


@pytest.mark.parametrize("path", ["/api/health", "/", "/index.html", "/nope"])
@pytest.mark.parametrize("hdr", [{"Host": "127.0.0.1:8765", "CF-Connecting-IP": "203.0.113.5"}, {"Host": "abc.trycloudflare.example"},
                                 {"Host": "127.0.0.1:8765", "Forwarded": "for=203.0.113.5"}, {"Host": "127.0.0.1:8765", "X-Forwarded-Host": "x.example"}])
def test_local_mode_refuses_every_get_through_a_tunnel(path, hdr):
    st, body = _call(_Ctx(LOCAL), "GET", path, hdr)
    assert st == 503 and b"Local mode" not in body


def test_local_mode_refuses_a_non_loopback_peer():
    ctx = _Ctx(LOCAL)
    st, _ = _call(ctx, "POST", "/api/ask", {"Host": "127.0.0.1:8765"}, ASK, peer="192.0.2.7")
    assert st == 503 and ctx.calls == []


def test_unknown_mode_context_refuses_forwarded_requests():
    class NoMode:
        def respond(self, q, recipe_text=None):
            raise AssertionError("must not be called")
    st, _ = _call(NoMode(), "POST", "/api/ask", {"Host": "127.0.0.1:8765", "X-Forwarded-For": "203.0.113.5"}, ASK)
    assert st == 503


def test_local_mode_still_serves_the_researchers_own_browser():
    ctx = _Ctx(LOCAL)
    st, body = _call(ctx, "POST", "/api/ask", {"Host": "localhost:8765"}, ASK)
    assert st == 200 and ctx.calls == ["What can I use instead of butter?"]
    st, body = _call(ctx, "GET", "/api/health")
    assert st == 200 and json.loads(body)["mode"]["mode"] == "local"
    st, body = _call(ctx, "GET", "/")
    assert st == 200 and b"<title>" in body


def test_public_mode_serves_forwarded_requests():
    ctx = _Ctx(PUBLIC)
    hdr = {"Host": "demo.example.org", "X-Forwarded-For": "203.0.113.5", "CF-Connecting-IP": "203.0.113.5"}
    st, body = _call(ctx, "POST", "/api/ask", hdr, ASK)
    assert st == 200 and json.loads(body)["demo_mode"]["public"] is True
    st, body = _call(ctx, "GET", "/api/health", hdr)
    assert st == 200 and json.loads(body)["mode"]["mode"] == "public"


def test_make_server_binds_the_same_handler():
    srv = S.make_server(("127.0.0.1", 0), _Ctx(LOCAL), per_minute=5)      # bound, never served: no request is made
    try:
        assert issubclass(srv.RequestHandlerClass, S.BaseHTTPRequestHandler)
        assert srv.RequestHandlerClass.__name__ == S.make_handler(_Ctx(LOCAL)).__name__
    finally:
        srv.server_close()
