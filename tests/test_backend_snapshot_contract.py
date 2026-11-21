"""Network-free FastAPI freshness, error-redaction and single-flight tests.

The public SDK-only CI environment does not install backend dependencies.
Skip only these HTTP-specific tests when FastAPI/httpx are absent; an operator
must independently run them with backend/requirements.txt installed.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import threading
import time
import unittest
from unittest.mock import patch

import pytest
pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient
from backend import app as api


def sample():
    return {
        "summary": {
            "generated_utc": "2026-11-21T00:00:00Z",
            "github": {"org": "szl-holdings", "repos_total": 2,
                       "repos_active": 2},
            "huggingface": {"org": "SZLHOLDINGS", "models_public": 1,
                            "datasets_public": 1, "spaces_public": 1},
        },
        "repos": [{"name": "a11oy", "archived": False},
                  {"name": "killinchu", "archived": False}],
        "assets": {
            "models": [{"id": "SZLHOLDINGS/Khipu"}],
            "datasets": [{"id": "SZLHOLDINGS/receipts"}],
            "spaces": [{"id": "SZLHOLDINGS/a11oy"}],
        },
    }


class InventoryCacheTests(unittest.TestCase):
    def setUp(self):
        api._cache.clear()
        self.tick = [100.0]
        clock = patch.object(api, "_clock", lambda: self.tick[0])
        clock.start()
        self.addCleanup(clock.stop)
        self.addCleanup(api._cache.clear)
        self.client = TestClient(api.app)

    def test_expired_cache_failure_never_returns_stale_or_secret_text(self):
        with patch.object(api, "estate_snapshot", side_effect=[
            sample(), RuntimeError("token=SECRET_VALUE"),
        ]) as source:
            self.assertEqual(self.client.get("/v1/snapshot").status_code, 200)
            self.tick[0] = 161.0
            reply = self.client.get("/v1/snapshot")
        self.assertEqual(source.call_count, 2)
        self.assertEqual(reply.status_code, 502)
        self.assertEqual(reply.json()["detail"], "UPSTREAM_INVENTORY_UNAVAILABLE")
        self.assertNotIn("SECRET_VALUE", reply.text)
        self.assertEqual(reply.headers["Cache-Control"], "no-store")
        self.assertNotIn("snapshot", api._cache)

    def test_failure_backoff_and_recovery_do_not_mask_errors(self):
        with patch.object(api, "estate_snapshot", side_effect=[
            OSError("PRIVATE_PATH"), sample(),
        ]) as source:
            self.assertEqual(self.client.get("/v1/repos").status_code, 502)
            self.tick[0] = 105
            throttled = self.client.get("/v1/repos")
            self.assertEqual(throttled.status_code, 503)
            self.assertNotIn("PRIVATE_PATH", throttled.text)
            self.tick[0] = 110.01
            self.assertEqual(self.client.get("/v1/repos").status_code, 200)
        self.assertEqual(source.call_count, 2)

    def test_fresh_snapshot_shared_then_refreshed_at_ttl_boundary(self):
        first, second = sample(), sample()
        second["summary"]["generated_utc"] = "2026-11-21T00:01:00Z"
        with patch.object(api, "estate_snapshot", side_effect=[first, second]) as source:
            a = self.client.get("/v1/snapshot")
            self.tick[0] = 159.999
            b = self.client.get("/v1/snapshot")
            self.tick[0] = 160.0
            c = self.client.get("/v1/snapshot")
        self.assertEqual(source.call_count, 2)
        self.assertEqual(a.json(), b.json())
        self.assertNotEqual(a.json(), c.json())

    def test_caller_mutation_does_not_poison_cached_payload(self):
        with patch.object(api, "estate_snapshot", return_value=sample()) as source:
            first = api._cached_snapshot()
            first["repos"][0]["name"] = "CHANGED"
            later = api._cached_snapshot()
        self.assertEqual(later["repos"][0]["name"], "a11oy")
        self.assertEqual(source.call_count, 1)

    def test_partial_inventory_never_becomes_green(self):
        invalid = [None, {}, {**sample(), "repos": []},
                   {**sample(), "assets": {"models": [], "datasets": []}},
                   {**sample(), "summary": {"github": {"repos_total": True},
                                            "huggingface": {}}}]
        for candidate in invalid:
            with self.subTest(candidate=candidate):
                api._cache.clear()
                with patch.object(api, "estate_snapshot", return_value=candidate):
                    reply = self.client.get("/v1/snapshot")
                self.assertEqual(reply.status_code, 502)
                self.assertNotIn("snapshot", api._cache)

    def test_parallel_cache_misses_share_one_upstream_fetch(self):
        calls = [0]
        lock = threading.Lock()
        def source():
            with lock:
                calls[0] += 1
            time.sleep(0.02)
            return sample()
        with patch.object(api, "estate_snapshot", side_effect=source):
            with ThreadPoolExecutor(max_workers=8) as pool:
                reports = list(pool.map(lambda _: api._cached_snapshot(), range(8)))
        self.assertEqual(calls[0], 1)
        self.assertTrue(all(len(r["repos"]) == 2 for r in reports))

    def test_existing_routes_retained_with_no_store(self):
        with patch.object(api, "estate_snapshot", return_value=sample()):
            responses = (self.client.get("/v1/snapshot"),
                         self.client.get("/v1/summary"),
                         self.client.get("/v1/repos"),
                         self.client.get("/v1/alignment?live=true"))
        self.assertTrue(all(r.status_code == 200 for r in responses))
        for response in responses:
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            self.assertEqual(response.headers["X-Robots-Tag"], "noindex")

    def test_health_endpoint_requires_no_upstream_access(self):
        with patch.object(api, "estate_snapshot",
                          side_effect=AssertionError("unexpected provider call")):
            result = self.client.get("/healthz")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json(), {"status": "ok"})
