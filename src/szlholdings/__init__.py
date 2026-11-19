"""szlholdings — live estate inventory + alignment for szl-holdings / SZLHOLDINGS.

Fail-closed by design: every live call raises on transport errors instead of
returning empty partial data, and alignment claims are labeled by provenance
method (card / name / override / unmapped), never guessed.
"""
__version__ = "0.1.0"

from .inventory import estate_snapshot, github_repos, hf_assets, summarize
from .alignment import alignment_matrix, coverage

__all__ = [
    "__version__",
    "estate_snapshot",
    "github_repos",
    "hf_assets",
    "summarize",
    "alignment_matrix",
    "coverage",
]
