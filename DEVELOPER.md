# Developer guide

## Repo topology

- **SDK**: `src/szlholdings/` — stdlib-only Python (no runtime dependencies),
  installable, CLI included.
- **API**: `backend/app.py` — FastAPI; adds `fastapi`/`uvicorn`.
- **Edge**: `cloudflare/worker/index.js` — read-only cache-first mirror.
- **Portal**: `frontend/index.html` — dependency-free static page. Works with
  or without the backend (falls back to the receipt-backed static snapshot).

## Install and hack

```bash
pip install -e .            # editable install of szlholdings
pytest                      # network-free smoke tests
szlholdings snapshot --json   # live inventory, machine-readable
```

## PyPI packages of this estate (canonical sources)

| PyPI package | Source repo | Path |
|---|---|---|
| `szlholdings` | `szl-portal` (this repo) | Trusted Publishing, pending owner registration |
| `szl-kernels` | `szl-holdings/szl-kernels` | live on PyPI |
| `szl-provctl` | `szl-holdings/szl-provctl` | live on PyPI |

Release path is identical for all of them: `szl.pypi-release.v2` (build + gate
in CI, publish on GitHub Release via Trusted Publishing, no tokens).

## CI and release

- `.github/workflows/ci.yml` — smoke tests on push/PR.
- `.github/workflows/publish-pypi.yml` — canonical estate release gate
  (build, twine strict check, venv probe, tag binding, PyPI duplicate guard),
  publishes only on a published GitHub Release whose tag equals the version.
  Before the first release, the owner registers the pending publisher on
  pypi.org for `szl-holdings/szl-portal` + workflow + environment `pypi`.

## Adding a new estate surface

Prefer extending this one repo (portal, API, SDK) over spawning new
front-door repos: duplicates/holograms are the estate's known drift risk, and
archived holograms carry "canonical" pointers back here.
