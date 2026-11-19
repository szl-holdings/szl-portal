"""SZL estate inventory API — FastAPI backend for the portal frontend.

Run:  pip install -r backend/requirements.txt
      uvicorn backend.app:app --host 0.0.0.0 --port 8080
Fail-closed by construction: the SDK raises on transport errors, and this API
surfaces those errors (502) rather than serving partial or invented data.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from szlholdings.alignment import alignment_matrix, coverage, load_bundled_map
from szlholdings.inventory import estate_snapshot

app = FastAPI(
    title="SZL Holdings estate inventory API",
    version="0.1.0",
    description="Live public inventory of the szl-holdings GitHub org and the "
                "SZLHOLDINGS Hugging Face org, with the canonical alignment matrix.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

_cache: dict = {}


def _cached_snapshot() -> dict:
    if "snapshot" not in _cache:
        try:
            _cache["snapshot"] = estate_snapshot()
        except Exception as exc:  # fail closed: never serve invented data
            raise HTTPException(status_code=502, detail=f"upstream inventory fetch failed: {exc}")
    return _cache["snapshot"]


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/v1/snapshot")
def snapshot() -> dict:
    """Live estate snapshot (GitHub repos + HF assets + summary)."""
    return _cached_snapshot()


@app.get("/v1/summary")
def summary() -> dict:
    """Summary card only (cheap for the frontend landing load)."""
    return _cached_snapshot()["summary"]


@app.get("/v1/alignment")
def alignment(live: bool = False) -> dict:
    """HF asset -> GitHub source matrix. `live=True` joins live repo metadata."""
    amap = load_bundled_map()
    rows = alignment_matrix(amap, _cached_snapshot()["repos"] if live else None)
    return {"coverage": coverage(amap), "rows": rows}


@app.get("/v1/repos")
def repos() -> dict:
    return {"repos": _cached_snapshot()["repos"]}
