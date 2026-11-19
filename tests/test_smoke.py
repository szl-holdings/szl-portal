"""Network-free smoke tests for the szlholdings SDK."""

from szlholdings.alignment import coverage
from szlholdings.inventory import summarize


def test_summarize_counts():
    repos = [
        {"name": "a", "language": "Python", "archived": False},
        {"name": "b", "language": "Python", "archived": True},
        {"name": "c", "language": None, "archived": False},
    ]
    assets = {
        "models": [{"id": "m1", "private": False}, {"id": "m2", "private": True}],
        "datasets": [{"id": "d1", "private": False}],
    }
    s = summarize(repos, assets)
    assert s["github"]["repos_total"] == 3
    assert s["github"]["repos_active"] == 2
    assert s["github"]["repos_archived"] == 1
    assert s["github"]["languages"]["Python"] == 2
    assert s["github"]["languages"]["Other"] == 1
    assert s["huggingface"]["models_public"] == 1
    assert s["huggingface"]["models_private"] == 1
    assert s["huggingface"]["datasets_public"] == 1


def test_coverage_math():
    amap = {"generated": "test", "assets": [
        {"id": "x", "type": "models", "source_repo": "r1", "method": "card"},
        {"id": "y", "type": "models", "source_repo": None, "method": "unmapped"},
        {"id": "z", "type": "datasets", "source_repo": "r2", "method": "name"},
    ]}
    c = coverage(amap)
    assert c["total"] == 3 and c["mapped"] == 2 and c["unmapped"] == 1
    assert c["mapped_pct"] == 66.7
    assert c["by_type"]["models"]["mapped"] == 1
    assert c["by_type"]["datasets"]["total"] == 1


def test_bundled_map_loads_static():
    from szlholdings.alignment import load_bundled_map, alignment_matrix
    amap = load_bundled_map()
    assert isinstance(amap.get("assets"), list) and amap["assets"], "bundled map must not be empty"
    rows = alignment_matrix(amap)
    assert all("method" in r for r in rows)
