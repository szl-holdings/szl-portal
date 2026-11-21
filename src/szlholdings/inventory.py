"""Live public inventory of the SZL estate: GitHub and Hugging Face.

Only public unauthenticated metadata endpoints are used. Fail closed on
truncated or malformed source lists; a missing dimension is never zero assets.
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone

GITHUB_ORG = "szl-holdings"
HF_ORG = "SZLHOLDINGS"
_UA = "szlholdings-sdk/0.1 (+https://github.com/szl-holdings/szl-portal)"


def _get_json(url: str, timeout: int = 30):
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def github_repos(org: str = GITHUB_ORG) -> list[dict]:
    """All public repositories; never promote incomplete search output."""
    repos, page = [], 1
    while True:
        data = _get_json(
            f"https://api.github.com/search/repositories?q=org:{org}+fork:true"
            f"&per_page=100&page={page}"
        )
        if (type(data) is not dict or data.get("incomplete_results") is True
                or type(data.get("items")) is not list):
            raise ValueError("GITHUB_PUBLIC_CENSUS_UNAVAILABLE")
        batch = data["items"]
        if any(type(row) is not dict or not isinstance(row.get("name"), str)
               or not row["name"] for row in batch):
            raise ValueError("GITHUB_PUBLIC_CENSUS_UNAVAILABLE")
        repos.extend(batch)
        if len(batch) < 100:
            if (type(data.get("total_count")) is int
                    and data["total_count"] != len(repos)):
                raise ValueError("GITHUB_PUBLIC_CENSUS_INCOMPLETE")
            break
        if page >= 10:
            raise ValueError("GITHUB_PUBLIC_CENSUS_PAGINATION_BOUND")
        page += 1
    return repos


def hf_assets(org: str = HF_ORG) -> dict[str, list[dict]]:
    """Public models, datasets and Spaces from one exact Hub author.

    The Hub API returns at most the requested limit. An exactly full page is
    not evidence that the inventory ended, so it cannot be reported complete.
    """
    out = {}
    for kind in ("models", "datasets", "spaces"):
        url = f"https://huggingface.co/api/{kind}?author={org}&limit=1000"
        rows = _get_json(url)
        if (type(rows) is not list or len(rows) >= 1000
                or any(type(r) is not dict or not isinstance(r.get("id"), str)
                       or not r["id"].startswith(org + "/") for r in rows)):
            raise ValueError("HUB_PUBLIC_CENSUS_UNAVAILABLE_OR_TRUNCATED")
        out[kind] = [
            {
                "id": r["id"],
                "private": bool(r.get("private", False)),
                "downloads": r.get("downloads", 0),
                "likes": r.get("likes", 0),
                "last_modified": r.get("lastModified"),
            }
            for r in rows
        ]
    return out


def summarize(repos: list[dict], assets: dict[str, list[dict]]) -> dict:
    """Pure source summary math, no model training/readiness implication."""
    active = [r for r in repos if not r.get("archived")]
    langs: dict[str, int] = {}
    for r in repos:
        lang = r.get("language") or "Other"
        langs[lang] = langs.get(lang, 0) + 1
    pub_models = [m for m in assets.get("models", []) if not m["private"]]
    pub_datasets = [d for d in assets.get("datasets", []) if not d["private"]]
    pub_spaces = [s for s in assets.get("spaces", []) if not s["private"]]
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "github": {
            "org": repos[0]["owner"]["login"] if repos and "owner" in repos[0] else None,
            "repos_total": len(repos),
            "repos_active": len(active),
            "repos_archived": len(repos) - len(active),
            "languages": dict(sorted(langs.items(), key=lambda kv: -kv[1])),
        },
        "huggingface": {
            "org": HF_ORG,
            "models_public": len(pub_models),
            "datasets_public": len(pub_datasets),
            "spaces_public": len(pub_spaces),
            "models_private": len(assets.get("models", [])) - len(pub_models),
            "datasets_private": len(assets.get("datasets", [])) - len(pub_datasets),
            "spaces_private": len(assets.get("spaces", [])) - len(pub_spaces),
        },
    }


def estate_snapshot(org_github: str = GITHUB_ORG, org_hf: str = HF_ORG) -> dict:
    """Public source snapshot; fail closed if any required dimension fails."""
    repos = github_repos(org_github)
    hf = hf_assets(org_hf)
    return {"summary": summarize(repos, hf), "repos": repos, "assets": hf}
