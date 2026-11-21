"""Fail-closed, public-only three-kind GitHub-to-Hub inventory tests."""
from __future__ import annotations

from unittest.mock import patch
import unittest

from szlholdings import inventory


class PublicCensusTests(unittest.TestCase):
    def test_public_hf_lists_three_kinds_including_spaces(self):
        seen = []
        def source(url, timeout=30):
            seen.append(url)
            kind = url.split("/api/")[1].split("?")[0]
            return [{"id": f"SZLHOLDINGS/{kind}-fixture", "private": False}]
        with patch.object(inventory, "_get_json", side_effect=source):
            assets = inventory.hf_assets()
        self.assertEqual(set(assets), {"models", "datasets", "spaces"})
        self.assertEqual(assets["spaces"][0]["id"], "SZLHOLDINGS/spaces-fixture")
        self.assertEqual(len(seen), 3)
        self.assertTrue(all("author=SZLHOLDINGS&limit=1000" in u for u in seen))

    def test_empty_response_object_is_not_zero_assets(self):
        with patch.object(inventory, "_get_json", side_effect=[
            [{"id": "SZLHOLDINGS/m"}], {}, [],
        ]):
            with self.assertRaisesRegex(ValueError, "HUB_PUBLIC_CENSUS"):
                inventory.hf_assets()

    def test_limit_exactly_full_is_unknown_not_complete(self):
        full = [{"id": f"SZLHOLDINGS/asset-{i}"} for i in range(1000)]
        with patch.object(inventory, "_get_json", return_value=full):
            with self.assertRaisesRegex(ValueError, "HUB_PUBLIC_CENSUS"):
                inventory.hf_assets()

    def test_other_org_asset_is_denied(self):
        with patch.object(inventory, "_get_json", side_effect=[
            [{"id": "SZLHOLDINGS/one"}], [{"id": "another-org/two"}], [],
        ]):
            with self.assertRaisesRegex(ValueError, "HUB_PUBLIC_CENSUS"):
                inventory.hf_assets()

    def test_github_incomplete_search_does_not_claim_zero(self):
        with patch.object(inventory, "_get_json", return_value={
            "items": [{"name": "repo"}], "incomplete_results": True,
        }):
            with self.assertRaisesRegex(ValueError, "GITHUB_PUBLIC_CENSUS"):
                inventory.github_repos()

    def test_github_missing_pagination_metadata_fails(self):
        with patch.object(inventory, "_get_json", return_value={
            "items": [{"name": "repo"}],
        }):
            with self.assertRaisesRegex(ValueError, "GITHUB_PUBLIC_CENSUS_UNAVAILABLE"):
                inventory.github_repos()

    def test_github_total_count_disagreement_fails(self):
        with patch.object(inventory, "_get_json", return_value={
            "items": [{"name": "repo"}], "total_count": 184,
            "incomplete_results": False,
        }):
            with self.assertRaisesRegex(ValueError, "GITHUB_PUBLIC_CENSUS_INCOMPLETE"):
                inventory.github_repos()

    def test_github_paginated_complete_response_succeeds(self):
        page1 = [{"name": f"repo-{i}"} for i in range(100)]
        page2 = [{"name": "last"}]
        with patch.object(inventory, "_get_json", side_effect=[
            {"items": page1, "total_count": 101, "incomplete_results": False},
            {"items": page2, "total_count": 101, "incomplete_results": False},
        ]) as src:
            repos = inventory.github_repos()
        self.assertEqual(len(repos), 101)
        self.assertEqual(src.call_count, 2)

    def test_summarize_spaces_distinct_from_other_kinds(self):
        repos = [{"name": "repo", "owner": {"login": "szl-holdings"},
                  "archived": False, "language": "Python"}]
        assets = {"models": [{"private": False}], "datasets": [{"private": False}],
                  "spaces": [{"private": False}, {"private": True}]}
        report = inventory.summarize(repos, assets)
        self.assertEqual(report["huggingface"]["spaces_public"], 1)
        self.assertEqual(report["huggingface"]["spaces_private"], 1)
        self.assertEqual(report["github"]["repos_total"], 1)

    def test_source_error_prevents_partial_estate_snapshot(self):
        with patch.object(inventory, "github_repos", return_value=[{"name": "repo"}]), \
             patch.object(inventory, "hf_assets", side_effect=TimeoutError("read failed")):
            with self.assertRaises(TimeoutError):
                inventory.estate_snapshot()
