"""Foodoscope (CoSyLab) API client: environment-only credentials, safe GETs, pagination, snapshots with provenance.

Contracts come from PUBLIC client code and issue notes (registry/sources/foodoscope_public_usage_registry.csv), NOT from a verified
call: until we hold our own key every path/parameter below is `UNVERIFIED` and the audit tool must confirm it. The key is read only
from FOODOSCOPE_API_KEY, never logged, never written to a snapshot. Credentials found in public repositories are compromised and
must never be used here.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import requests

VERSION = "foodoscope_client@0.1"
BASES = {"recipedb": "https://api.foodoscope.com/recipe2-api", "flavordb": "https://api.foodoscope.com/flavordb"}
KEY_ENV = "FOODOSCOPE_API_KEY"


class FoodoscopeAuthError(RuntimeError):
    """401/403, or a 400 body saying the ApiKey is missing/invalid."""


@dataclass(frozen=True)
class Config:
    auth_header: str = "bearer"          # "bearer" -> Authorization: Bearer <key>; "x-api-key" -> x-api-key: <key> (both seen in public code)
    timeout_s: float = 30.0
    retries: int = 2                     # safe GETs only: 5xx / timeouts
    backoff_s: float = 1.5
    min_interval_s: float = 2.5          # Starter plan: 25 requests/minute
    snapshot_dir: Path | None = None


class FoodoscopeClient:
    def __init__(self, config: Config | None = None, session: requests.Session | None = None, sleep=time.sleep):
        self.cfg = config or Config()
        self._s = session or requests.Session()
        self._sleep = sleep
        self._last = 0.0
        self._s.headers.update({"Accept": "application/json", "User-Agent": "CulinaryState-Research/0.1 (IIIT Delhi)"})

    def _auth(self) -> dict[str, str]:
        key = os.getenv(KEY_ENV)
        if not key:
            return {}                                        # unauthenticated: the service will say so (400 'ApiKey is not provided')
        return {"Authorization": f"Bearer {key}"} if self.cfg.auth_header == "bearer" else {"x-api-key": key}

    def get(self, api: str, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{BASES[api].rstrip('/')}/{path.lstrip('/')}"
        last_err: Exception | None = None
        for attempt in range(self.cfg.retries + 1):
            wait = self.cfg.min_interval_s - (time.monotonic() - self._last)
            if wait > 0:
                self._sleep(wait)
            self._last = time.monotonic()
            try:
                r = self._s.get(url, params=params, headers=self._auth(), timeout=self.cfg.timeout_s)
            except requests.RequestException as e:           # timeouts / connection resets: retry
                last_err = e
                self._sleep(self.cfg.backoff_s * (attempt + 1))
                continue
            body = None
            try:
                body = r.json()
            except ValueError:
                pass
            err = str(body.get("error", "")) if isinstance(body, dict) else ""
            if r.status_code in (401, 403) or (r.status_code == 400 and "apikey" in err.lower().replace(" ", "")):
                raise FoodoscopeAuthError(f"{r.status_code} from {api}{path}: {err or 'authentication refused'}")
            if r.status_code >= 500:
                last_err = RuntimeError(f"{r.status_code} from {url}")
                self._sleep(self.cfg.backoff_s * (attempt + 1))
                continue
            r.raise_for_status()
            self._snapshot(api, path, params, r.status_code, body if body is not None else r.text)
            return body if body is not None else r.text
        raise RuntimeError(f"GET {api}{path} failed after {self.cfg.retries + 1} attempts: {last_err}")

    def pages(self, api: str, path: str, params: dict[str, Any] | None = None, size: int = 20, max_pages: int = 5) -> Iterator[Any]:
        """Spring-style paging (page, size; response has totalPages), as seen in public FlavorDB client notes. Bounded."""
        for page in range(max_pages):
            body = self.get(api, path, {**(params or {}), "page": page, "size": size})
            yield body
            total = body.get("totalPages") if isinstance(body, dict) else None
            if total is not None and page + 1 >= total:
                return

    def _snapshot(self, api, path, params, status, body) -> None:
        if not self.cfg.snapshot_dir:
            return
        self.cfg.snapshot_dir.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(body, ensure_ascii=False, sort_keys=True)
        rec = {"client": VERSION, "api": api, "path": path, "params": params or {}, "status": status,
               "retrieved_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
               "sha256": hashlib.sha256(payload.encode()).hexdigest(), "body": body}
        (self.cfg.snapshot_dir / f"{api}_{rec['sha256'][:16]}.json").write_text(json.dumps(rec, ensure_ascii=False))

    # --- UNVERIFIED convenience wrappers (paths/params from public code; confirm with our own key) ---
    def recipe_by_title(self, title: str):
        return self.get("recipedb", "/recipe-bytitle/recipeByTitle", {"title": title})

    def recipe(self, recipe_id):
        return self.get("recipedb", f"/search-recipe/{recipe_id}")

    def instructions(self, recipe_id):
        return self.get("recipedb", f"/instructions/{recipe_id}")

    def flavor_entity(self, alias_readable: str, page: int = 0, size: int = 1):
        return self.get("flavordb", "/entities/by-entity-alias-readable",
                        {"entity_alias_readable": alias_readable, "page": page, "size": size})
