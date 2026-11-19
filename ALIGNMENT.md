# GitHub ↔ Hugging Face alignment (canonical snapshot 2026-11-15)

Source of truth: `szl-holdings/szl-asset-registry` (`asset_map.json`, schema
`szl.asset-registry/v1`, owner-curated, generated 2026-11-15). This document
is its public snapshot. The SDK ships a machine-readable copy in
`src/szlholdings/asset_map_snapshot.json`. Nothing in the map is guessed;
rows that lack a known source are `unmapped` — shown, not hidden.

## Coverage (canonical, 2026-11-15)

| Metric | Value |
|---|---|
| Total HF assets (models + datasets + spaces) | 390 |
| Mapped to a GitHub source repo | 222 (56.9%) |
| Unmapped | 168 |
| Mapping methods | card-linked 159 · exact-name 57 · owner override 6 |

Unmapped families are dominated by run-artifact stores (training/diagnostic
artifacts, 8), laptop LoRA training runs (21), candidate/eval staging (29),
and corpus benchmarks (18) — expected: those are evidence, not products.

## Flagship rows (all verbatim from the canonical map)

| Hugging Face asset | GitHub source | Method |
|---|---|---|
| SZLHOLDINGS/A11OY-MINI (model) | a11oy | name |
| SZLHOLDINGS/governed-agent-bench (dataset) | a11oy | card |
| SZLHOLDINGS/KILLINCHU-EYE (model) | killinchu | name |
| SZLHOLDINGS/killinchu-osint-corpus (dataset) | killinchu | card |
| SZLHOLDINGS/frontier-54-runs (dataset) | szl-gpu-bridge | override |
| SZLHOLDINGS/szl-training-receipts (dataset) | szl-gpu-bridge | card |
| SZLHOLDINGS/szl-brain (model, private) | szl-gpu-bridge | card |
| SZLHOLDINGS/szl-kernels (model) | szl-kernels | name |
| SZLHOLDINGS/szl-govsign / szl-provctl / szl-blocked / szl-nemo / szl-invariants / szl-formulas / szl-ouroboros / szl-lambda-gate / szl-governed-norm (models) | same-name repos | name |
| SZLHOLDINGS/WILLAY, chaski, forge-v3, SZL-Nemotron-Mini-4B-Estate-v1 (models) | szl-forge | card |
| SZLHOLDINGS/SZL-Khipu-1.5B line (models) | szl-khipu / szl-atelier | name / card |
| SZLHOLDINGS/lean-theorem-tree, thesis-v18-formal-verification (datasets) | lutar-lean | card |
| SZLHOLDINGS/governed-receipts-bench, energy-attested-runs (datasets) | governed-receipt-spec | card |
| SZLHOLDINGS/szl-bench-suite (Space) | frontier-bench | card |
| SZLHOLDINGS/vault-artifacts (dataset, private) | platform | card |
| SZLHOLDINGS/canonical-formulas-v1, doctrine-v10-v11 (datasets) | .github | card |

(56 rows shipped in the SDK snapshot; the full 390-row registry is in the
private registry repo, and the pyproject-adjacent tool re-snapshots it on
demand.)

## Known limits (stated, not hidden)

- The space count lives in the canonical registry but the public Hub API does
  not enumerate Spaces in this SDK's live inventory yet (`models`/`datasets`
  only); Spaces appear in the bundled snapshot map.
- This snapshot ages; canonical map regeneration is an owner-side script in
  the registry repo. The SDK prints the snapshot's generation date on every
  coverage call.
