"""Network-free negative controls for the source-hint versus producer boundary."""
import pytest

from szlholdings.alignment import (
    alignment_matrix, coverage, load_bundled_map,
)


def fixture():
    return {"generated": "2026-11-15", "assets": [
        {"id": "SZLHOLDINGS/m1", "type": "models", "method": "name", "source_repo": "a11oy"},
        {"id": "SZLHOLDINGS/d1", "type": "datasets", "method": "card", "source_repo": "estate-cards"},
        {"id": "SZLHOLDINGS/s1", "type": "spaces", "method": "override", "source_repo": "killinchu"},
        {"id": "SZLHOLDINGS/s2", "type": "spaces", "method": "unmapped", "source_repo": None},
    ]}


def test_legacy_counts_remain_discovery_counts_not_current_estate_totals():
    stats = coverage(fixture())
    assert (stats["total"], stats["mapped"], stats["unmapped"], stats["mapped_pct"]) == (4, 3, 1, 75.0)
    assert stats["scope"] == "BUNDLED_HISTORICAL_SUBSET_NOT_FULL_ESTATE"
    assert stats["current_full_estate_coverage"] is None
    assert stats["producer_verification"] == "UNAVAILABLE_NOT_AUDITED_IN_THIS_SCHEMA"
    assert stats["runtime_or_training_admitted"] is False


@pytest.mark.parametrize("method", ["name", "card", "override"])
def test_no_mapping_method_proves_producing_source(method):
    amap = {"assets": [
        {"id": "SZLHOLDINGS/foo", "type": "models", "method": method, "source_repo": "a11oy"}
    ]}
    row = alignment_matrix(amap, [{"name": "a11oy", "language": "Python"}])[0]
    assert row["source_repo"] == "a11oy"  # Keep v1 compatibility.
    assert row["repo_language"] == "Python"
    assert row["source_evidence_state"] == "LEGACY_HINT_UNVERIFIED"
    assert row["producing_source_repo"] is None
    assert row["producing_source_revision"] is None
    assert row["producer_verified"] is False
    assert row["training_verified"] is False
    assert row["authenticated_runtime_verified"] is False
    assert row["production_admitted"] is False


def test_unmapped_asset_has_no_producer_claim_or_link():
    row = alignment_matrix(fixture())[-1]
    assert row["source_repo"] is None
    assert row["source_evidence_state"] == "NO_SOURCE_HINT"
    assert row["source_url"] is None
    assert row["producer_verified"] is False


@pytest.mark.parametrize("bad", ["javascript:alert(1)", "../../bad", "bad/name", "..", "", None, True])
def test_invalid_hint_never_becomes_an_untrusted_github_link(bad):
    m = {"assets": [{"id": "SZLHOLDINGS/foo", "type": "models",
                    "method": "card", "source_repo": bad}]}
    with pytest.raises(ValueError):
        alignment_matrix(m)
    with pytest.raises(ValueError):
        coverage(m)


def test_duplicate_same_kind_asset_identity_is_denied():
    m = fixture()
    m["assets"].append(dict(m["assets"][0]))
    with pytest.raises(ValueError, match="DUPLICATE"):
        coverage(m)


def test_cross_kind_names_can_be_independently_mapped():
    m = fixture()
    m["assets"].append({"id": "SZLHOLDINGS/m1", "type": "datasets",
                        "method": "card", "source_repo": "a11oy"})
    assert coverage(m)["total"] == 5


def test_invalid_map_structure_is_not_a_green_empty_result():
    for bad in (None, {}, {"assets": None}, {"assets": ["not-a-record"]}):
        with pytest.raises(ValueError):
            coverage(bad)


def test_org_governance_dot_github_is_a_valid_but_unverified_hint():
    m = {"assets": [{"id": "SZLHOLDINGS/doctrine-v11", "type": "datasets",
                     "method": "card", "source_repo": ".github"}]}
    row = alignment_matrix(m)[0]
    assert row["source_url"] == "https://github.com/szl-holdings/.github"
    assert row["producer_verified"] is False


def test_actual_bundled_subset_is_valid_but_not_a_current_census():
    """Runs on the repo's real, dated source snapshot in hosted SDK CI."""
    snap = load_bundled_map()
    stat = coverage(snap)
    rows = alignment_matrix(snap)
    assert len(rows) == stat["total"] == len(snap["assets"])
    assert stat["scope"] == "BUNDLED_HISTORICAL_SUBSET_NOT_FULL_ESTATE"
    assert all(row["producer_verified"] is False for row in rows)
    assert all(row["production_admitted"] is False for row in rows)
    assert any(row["source_repo"] == ".github" for row in rows)
