# Portal alignment: legacy hints are not verified producers

**Source owner:** `szl-holdings/szl-portal`. **Scope:** public source-only SDK / API consumer. No asset, dataset, model, Space, Cloudflare, DNS, credential, package, or training mutation.

## Current problem

The portal ships `src/szlholdings/asset_map_snapshot.json`, a dated **2026-11-15 public subset of 58 assets**. Its own frozen note cites **390** assets / 222 linked in the older registry, while the independently newer `szl-asset-registry` ledger reported **666** total assets / 648 linked. These different denominators cannot be merged or silently substituted. `coverage().mapped_pct` over the bundled subset is not a current organization-wide alignment metric.

The legacy map's `source_repo` and `method` fields are useful **discovery hints**, not evidence that a repository produced particular model weights, a dataset, or a live application. In particular, the asset registry's review proposals [#15](https://github.com/szl-holdings/szl-asset-registry/pull/15) and [#16](https://github.com/szl-holdings/szl-asset-registry/pull/16) independently identify large cohorts of card-generator links (including `estate-cards`) that cannot establish a producer identity.

## Strictly additive Python consumer contract

- Retain existing `source_repo`, `source_url`, `method`, `mapped`, `unmapped`, `mapped_pct` and `by_type` values for legacy consumer compatibility. These are **hint** counts, not attestations.
- Add `scope=BUNDLED_HISTORICAL_SUBSET_NOT_FULL_ESTATE`, `mapped_meaning=LEGACY_SOURCE_HINT_ONLY_NOT_PRODUCER_VERIFIED`, `producer_verification=UNAVAILABLE_NOT_AUDITED_IN_THIS_SCHEMA`, and `current_full_estate_coverage=null`. Do not pretend 0 observed proofs means no actual training or production evidence exists elsewhere.
- Each row gets `legacy_source_hint` and `source_evidence_state` without inventing `producing_source_repo` or `producing_source_revision`. Both remain null, and `producer_verified`, `training_verified`, `authenticated_runtime_verified`, and `production_admitted` remain false.
- Check each asset's kind and unique composite identity, the declared mapping method and bounded GitHub repository name grammar before constructing a source hyperlink. Recognize legitimate `.github` organization governance repository hints while rejecting traversal, URL schemes, malformed names and duplicate assets.

The **canonical production proof path** remains separate: owner-reviewed exact GitHub source revision; immutable Hugging Face model/dataset/Space artifact byte digest; verified source or build attestation; for models, license/rights, weight hash, training and held-out evaluation; for Spaces, authenticated runtime/data rendering; explicit deployment identity and admission. This PR establishes **none** of those facts.

## Deterministic checks and non-goals

Synthetic Python negative controls validate all three mapping methods, cross-kind identities, invalid URLs, duplicate records, `.github` and non-promotion of model/runtime claims. An additional existing-bundle contract validates the actual dated snapshot and its legacy rows.

No independent desktop Kimi/Ministral review is claimed: BETTERWITHAGE's connected Desktop Commander returned `link_id must identify an eligible linked account`. No Claude/Perplexity/Astra execution is asserted. Model agreement cannot grant source or merge authority.

Public references used for concept separation, **not code**:

- [Backstage catalog owner relationships](https://backstage.io/docs/features/software-catalog/well-known-relations/) distinguish discovery/ownership from automated authorization.
- [SLSA provenance](https://slsa.dev/spec/v1.2/provenance) requires verifiable where, when, and how an artifact was produced; a repository link alone is not such proof.

**HOLD:** Independent human review, exact-head required CI and safe consuming-UI semantics must be checked before merging. The draft source PR does not change the registry's authoritative records, Hub content, public product routes or deployment state.
