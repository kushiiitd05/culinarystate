import json
from unittest.mock import MagicMock

import pytest
import requests

from culinarystate.sources.foodoscope_client import Config, FoodoscopeAuthError, FoodoscopeClient


def _resp(status, body):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = body
    r.text = json.dumps(body)
    r.raise_for_status.side_effect = None if status < 400 else requests.HTTPError(str(status))
    return r


def _client(responses, **cfg):
    s = MagicMock()
    s.headers = {}
    s.get.side_effect = responses
    return FoodoscopeClient(Config(min_interval_s=0, retries=2, backoff_s=0, **cfg), session=s, sleep=lambda _: None), s


def test_key_only_from_env_and_never_in_snapshot(tmp_path, monkeypatch):
    monkeypatch.setenv("FOODOSCOPE_API_KEY", "SECRET-VALUE-123")
    c, s = _client([_resp(200, {"ok": 1})], snapshot_dir=tmp_path)
    assert c.get("recipedb", "/recipe/recipeofday") == {"ok": 1}
    assert s.get.call_args.kwargs["headers"] == {"Authorization": "Bearer SECRET-VALUE-123"}
    assert "SECRET-VALUE-123" not in "".join(p.read_text() for p in tmp_path.iterdir())


def test_x_api_key_mode_and_no_key_sends_no_header(monkeypatch):
    monkeypatch.setenv("FOODOSCOPE_API_KEY", "k")
    c, s = _client([_resp(200, {})], auth_header="x-api-key")
    c.get("flavordb", "/x")
    assert s.get.call_args.kwargs["headers"] == {"x-api-key": "k"}
    monkeypatch.delenv("FOODOSCOPE_API_KEY")
    c, s = _client([_resp(200, {})])
    c.get("flavordb", "/x")
    assert s.get.call_args.kwargs["headers"] == {}


def test_missing_key_400_and_403_raise_auth_error():
    c, _ = _client([_resp(400, {"error": "ApiKey is not provided"})])
    with pytest.raises(FoodoscopeAuthError):
        c.get("recipedb", "/x")
    c, _ = _client([_resp(403, {})])
    with pytest.raises(FoodoscopeAuthError):
        c.get("recipedb", "/x")


def test_retries_5xx_then_succeeds_and_gives_up():
    c, s = _client([_resp(502, {}), _resp(200, {"v": 1})])
    assert c.get("recipedb", "/x") == {"v": 1} and s.get.call_count == 2
    c, s = _client([_resp(500, {})] * 3)
    with pytest.raises(RuntimeError):
        c.get("recipedb", "/x")
    assert s.get.call_count == 3


def test_pagination_stops_at_total_pages():
    c, s = _client([_resp(200, {"totalPages": 2, "content": [1]}), _resp(200, {"totalPages": 2, "content": [2]}), _resp(200, {})])
    assert len(list(c.pages("flavordb", "/entities/by-entity-alias-readable", {"entity_alias_readable": "grapefruit"}))) == 2
    assert s.get.call_count == 2
