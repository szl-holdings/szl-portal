"""SZL estate inventory API — source-only FastAPI backend.

Upstream source observations are cached for a bounded 60 seconds after a
successful fetch. An expired observation is NEVER served after a failed refresh.
This is not an execution controller, release signer or evidence of deployment.
"""
from __future__ import annotations

from copy import deepcopy
from threading import Lock
from time import monotonic

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from szlholdings.alignment import alignment_matrix, coverage, load_bundled_map
from szlholdings.inventory import estate_snapshot

app = FastAPI(
    title="SZL Holdings estate inventory API",
    version="0.1.0",
    description="Public source-owned GitHub and Hugging Face inventory; freshness is bounded.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

CACHE_TTL_SECONDS = 60
FAILURE_BACKOFF_SECONDS = 10
_cache_lock = Lock()
_cache: dict = {}
_clock = monotonic


@app.middleware("http")
async def _no_store_inventory(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/v1/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Robots-Tag"] = "noindex"
    return response


def _valid_snapshot(value: object) -> bool:
    """A malformed partial source response must never become a green snapshot."""
    if type(value) is not dict:
        return False
    repos, assets, summary = (value.get("repos"), value.get("assets"),
                              value.get("summary"))
    if type(repos) is not list or type(assets) is not dict or type(summary) is not dict:
        return False
    if type(summary.get("github")) is not dict or type(summary.get("huggingface")) is not dict:
        return False
    if type(summary["github"].get("repos_total")) is not int:
        return False
    if summary["github"]["repos_total"] != len(repos):
        return False
    if not repos or any(type(row) is not dict or not isinstance(row.get("name"), str)
                        or not row["name"] for row in repos):
        return False
    for kind in ("models", "datasets", "spaces"):
        rows = assets.get(kind)
        if type(rows) is not list or any(
            type(row) is not dict or not isinstance(row.get("id"), str)
            or not row["id"] for row in rows
        ):
            return False
    return True


def _cached_snapshot() -> dict:
    """Single-flight, monotonic TTL and fail-closed source readback.

    The lock prevents parallel refresh storms. An upstream failure invalidates
    the expired entry and briefly suppresses repeated calls, but never returns
    stale source data or exception text that might contain credentials.
    """
    with _cache_lock:
        stamp = _clock()
        current = _cache.get("snapshot")
        if current is not None and stamp < _cache.get("expires_at", 0.0):
            return deepcopy(current)
        if stamp < _cache.get("retry_after", 0.0):
            raise HTTPException(status_code=503,
                                detail="UPSTREAM_INVENTORY_RETRY_BACKOFF")
        try:
            fresh = estate_snapshot()
            if not _valid_snapshot(fresh):
                raise ValueError("unqualified inventory shape")
        except Exception:
            _cache.clear()
            _cache["retry_after"] = _clock() + FAILURE_BACKOFF_SECONDS
            raise HTTPException(status_code=502,
                                detail="UPSTREAM_INVENTORY_UNAVAILABLE") from None
        _cache.clear()
        _cache["snapshot"] = deepcopy(fresh)
        _cache["expires_at"] = _clock() + CACHE_TTL_SECONDS
        return deepcopy(fresh)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/v1/snapshot")
def snapshot() -> dict:
    return _cached_snapshot()


@app.get("/v1/summary")
def summary() -> dict:
    return _cached_snapshot()["summary"]


@app.get("/v1/alignment")
def alignment(live: bool = False) -> dict:
    amap = load_bundled_map()
    rows = alignment_matrix(amap, _cached_snapshot()["repos"] if live else None)
    return {"coverage": coverage(amap), "rows": rows}


@app.get("/v1/repos")
def repos() -> dict:
    return {"repos": _cached_snapshot()["repos"]}
