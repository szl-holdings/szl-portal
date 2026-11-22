"""Public HF asset -> GitHub discovery hints (NOT producer provenance).

Canonical producer claims require source-revision-bound, independently verified
artifact and deployment receipts. The bundled v1 registry snapshot contains
only historical matching methods (card/name/override), not that evidence.
"""
from __future__ import annotations

import json
import re
from importlib import resources

BUNDLED = "asset_map_snapshot.json"
REPO_NAME = re.compile(r"[A-Za-z0-9._-]+\Z")
METHODS = frozenset(("card", "name", "override", "unmapped"))
KINDS = frozenset(("models", "datasets", "spaces"))


def load_bundled_map() -> dict:
    """Load a historical subset for discovery; never fetch a live asset map."""
    with resources.files("szlholdings").joinpath(BUNDLED).open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate_assets(asset_map: dict) -> list[dict]:
    if type(asset_map) is not dict or type(asset_map.get("assets")) is not list:
        raise ValueError("BUNDLED_ASSET_MAP_UNAVAILABLE")
    assets = asset_map["assets"]
    seen: set[tuple[str, str]] = set()
    for asset in assets:
        if type(asset) is not dict:
            raise ValueError("BUNDLED_ASSET_RECORD_INVALID")
        kind, ident, method, hint = (
            asset.get("type"), asset.get("id"), asset.get("method"), asset.get("source_repo")
        )
        if (kind not in KINDS or type(ident) is not str or not ident.strip()
                or method not in METHODS):
            raise ValueError("BUNDLED_ASSET_IDENTITY_INVALID")
        key = (kind, ident)
        if key in seen:
            raise ValueError("BUNDLED_ASSET_DUPLICATE")
        seen.add(key)
        if method == "unmapped":
            if hint is not None:
                raise ValueError("BUNDLED_UNMAPPED_HAS_HINT")
        elif (type(hint) is not str or not REPO_NAME.fullmatch(hint)
              or hint in (".", "..")):
            raise ValueError("BUNDLED_ASSET_HINT_INVALID")
    return assets


def coverage(asset_map: dict) -> dict:
    """Historical subset counts; intentionally no producer-verified metric."""
    assets = _validate_assets(asset_map)
    mapped = sum(a["method"] != "unmapped" for a in assets)
    by_type: dict[str, dict[str, int]] = {}
    for a in assets:
        kind = a["type"]
        cell = by_type.setdefault(kind, {"total": 0, "mapped": 0})
        cell["total"] += 1
        if a["method"] != "unmapped":
            cell["mapped"] += 1
    return {
        "generated": asset_map.get("generated"),
        "total": len(assets),
        "mapped": mapped,  # Compatibility: discovery-hint count only.
        "unmapped": len(assets) - mapped,
        "mapped_pct": round(100.0 * mapped / len(assets), 1) if assets else 0.0,
        "by_type": by_type,
        "scope": "BUNDLED_HISTORICAL_SUBSET_NOT_FULL_ESTATE",
        "mapped_meaning": "LEGACY_SOURCE_HINT_ONLY_NOT_PRODUCER_VERIFIED",
        "producer_verification": "UNAVAILABLE_NOT_AUDITED_IN_THIS_SCHEMA",
        "current_full_estate_coverage": None,
        "runtime_or_training_admitted": False,
    }


def alignment_matrix(asset_map: dict, repos: list[dict] | None = None) -> list[dict]:
    """Keep v1 consumer keys; distinguish owner hints from producer claims."""
    assets = _validate_assets(asset_map)
    by_name = {r.get("name"): r for r in (repos or []) if type(r) is dict}
    rows = []
    for a in assets:
        hint = a.get("source_repo")
        meta = by_name.get(hint) if hint else None
        rows.append({
            "asset": a["id"],
            "asset_type": a["type"],
            "source_repo": hint,  # Kept for existing consumers; *not* an attested producer.
            "source_url": f"https://github.com/szl-holdings/{hint}" if hint else None,
            "method": a["method"],
            "repo_language": meta.get("language") if meta else None,
            "repo_updated": meta.get("updated_at") if meta else None,
            "legacy_source_hint": hint,
            "source_evidence_state": ("LEGACY_HINT_UNVERIFIED" if hint
                                      else "NO_SOURCE_HINT"),
            "producing_source_repo": None,
            "producing_source_revision": None,
            "producer_verified": False,
            "training_verified": False,
            "authenticated_runtime_verified": False,
            "production_admitted": False,
        })
    return rows
