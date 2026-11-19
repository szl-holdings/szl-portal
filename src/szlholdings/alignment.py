"""GitHub <-> Hugging Face alignment matrix.

The canonical owner-curated map lives in the private repo
szl-holdings/szl-asset-registry (asset_map.json, schema szl.asset-registry/v1).
Public consumers get a bundled snapshot plus honest coverage stats; every
mapping row is labeled with its provenance method and is never guessed here.
"""
from __future__ import annotations

import json
from importlib import resources

BUNDLED = "asset_map_snapshot.json"


def load_bundled_map() -> dict:
    """The asset-map snapshot shipped with this package (read-only, dated)."""
    with resources.files("szlholdings").joinpath(BUNDLED).open("r", encoding="utf-8") as f:
        return json.load(f)


def coverage(asset_map: dict) -> dict:
    """Coverage stats computed from an asset map. Fail-closed on shape."""
    assets = asset_map.get("assets")
    if not isinstance(assets, list):
        raise ValueError("asset map has no assets list; refusing to compute coverage")
    mapped = [a for a in assets if a.get("source_repo")]
    unmapped = [a for a in assets if not a.get("source_repo")]
    by_type: dict[str, dict[str, int]] = {}
    for a in assets:
        t = a.get("type", "other")
        slot = by_type.setdefault(t, {"total": 0, "mapped": 0})
        slot["total"] += 1
        if a.get("source_repo"):
            slot["mapped"] += 1
    return {
        "generated": asset_map.get("generated"),
        "total": len(assets),
        "mapped": len(mapped),
        "unmapped": len(unmapped),
        "mapped_pct": round(100.0 * len(mapped) / len(assets), 1) if assets else 0.0,
        "by_type": by_type,
    }


def alignment_matrix(asset_map: dict, repos: list[dict] | None = None) -> list[dict]:
    """Matrix rows: asset -> source repo (with repo metadata when repos given)."""
    by_name = {r.get("name"): r for r in (repos or [])}
    rows = []
    for a in asset_map.get("assets", []):
        src = a.get("source_repo")
        repo = by_name.get(src) if src else None
        rows.append(
            {
                "asset": a.get("id"),
                "asset_type": a.get("type"),
                "source_repo": src,
                "source_url": f"https://github.com/szl-holdings/{src}" if src else None,
                "method": a.get("method", "unmapped"),
                "repo_language": repo.get("language") if repo else None,
                "repo_updated": repo.get("updated_at") if repo else None,
            }
        )
    return rows
