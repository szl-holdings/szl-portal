"""Live public inventory of the SZL estate: GitHub org + Hugging Face org.

Only public, unauthenticated endpoints are used. Fail-closed: transport
failures raise; nothing is ever filled with fabricated placeholder data.
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
    """All public repositories of the org (paginated GitHub search API)."""
    repos, page = [], 1
    while True:
        data = _get_json(
            f"https://api.github.com/search/repositories?q=org:{org}+fork:true"
            f"&per_page=100&page={page}"
        )
        batch = data.get("items", [])
        repos.extend(batch)
        if len(batch) < 100 or page >= 10:
            break
        page += 1
    return repos


def hf_assets(org: str = HF_ORG) -> dict[str, list[dict]]:
    """Public models and datasets of the HF org (Hub API)."""
    out = {}
    for kind in ("models", "datasets"):
        url = f"https://huggingface.co/api/{kind}?author={org}&limit=1000"
        rows = _get_json(url) or []
        out[kind] = [
            {
                "id": r.get("id"),
                "private": bool(r.get("private", False)),
                "downloads": r.get("downloads", 0),
                "likes": r.get("likes", 0),
                "last_modified": r.get("lastModified"),
            }
            for r in rows
        ]
    return out


def summarize(repos: list[dict], assets: dict[str, list[dict]]) -> dict:
    """Pure summary math — network-free, unit-testable."""
    active = [r for r in repos if not r.get("archived")]
    langs: dict[str, int] = {}
    for r in repos:
        lang = r.get("language") or "Other"
        langs[lang] = langs.get(lang, 0) + 1
    pub_models = [m for m in assets.get("models", []) if not m["private"]]
    pub_datasets = [d for d in assets.get("datasets", []) if not d["private"]]
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
            "models_private": len(assets.get("models", [])) - len(pub_models),
            "datasets_private": len(assets.get("datasets", [])) - len(pub_datasets),
        },
    }


def estate_snapshot(org_github: str = GITHUB_ORG, org_hf: str = HF_ORG) -> dict:
    """Live snapshot: GitHub repos + HF assets + summary. Fail-closed."""
    repos = github_repos(org_github)
    hf = hf_assets(org_hf)
    return {"summary": summarize(repos, hf), "repos": repos, "assets": hf}
