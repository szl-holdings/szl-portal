# SZL Holdings — investor brief (evidence-backed)

**What we build:** governed AI decision infrastructure — systems whose every
action is deny-by-default, fail-closed, and ships a cryptographically
verifiable receipt. "AI that signs its work" is a product category and a
verification standard, not a slogan.

## The measured estate (as of the 2026-11-15 canonical census)

- **167 GitHub repositories** in `szl-holdings` — flagship products
  (a11oy command center, szl-router, killinchu counter-UAS reference), kernels,
  benchmarks, formal verification (Lean 4 + Mathlib), and full CI/provenance
  tooling. Archived repos are retained deliberately as honesty markers with
  canonical pointers.
- **390 Hugging Face assets** under `SZLHOLDINGS` — fine-tuned models, SFT/eval
  corpora, evaluation receipt stores, live Spaces (public count 73 models /
  24 datasets and growing; private assets shown as private, never hidden).
- **222 of 390 assets** carry a canonical mapping to their GitHub source
  (provenance method labeled: `card` / `name` / `override`). The map is a
  maintained artifact, not marketing copy.
- **2 packages live on PyPI** (`szl-kernels`, `szl-provctl`) via tokenless
  Trusted Publishing with PEP 740 attestations; `szlholdings` (this repo) is
  next in the same pipeline.
- **Frontier R&D is disciplined:** the flagship54 program trains candidate
  models under pre-registered criteria with mechanical verdicts posted
  publicly (issue #348); negative results are published as receipts (v1: NOT
  QUALIFIED, disclosed) — the qualification bar is not negotiable and not
  gamed.

## Why this matters commercially

1. **Regulatory tailwind:** governed, auditable AI is becoming a procurement
   requirement (defense, finance, clinical). The estate's receipt
   infrastructure (DSSE/SLSA-aligned, Lean-formalized invariants) is exactly
   the evidence layer buyers cannot fake after the fact.
2. **Demonstrated depth:** formal verification, kernel engineering, honest
   benchmarking, and a falsifiable eval protocol — the hard parts are already
   built and published.
3. **Monetization is designed, not bolted on:** see `MONETIZATION.md` —
   free/Pro/enterprise tiers over the inventory API, gated model distribution,
   and receipt-backed SLAs. Activation is owner-gated (accounts/billing), the
   software is deploy-ready (Cloudflare kit in `cloudflare/`).

## Where to look

- Portal: this repo (`frontend/`) — deployable to Cloudflare Pages.
- Product: [a11oy](https://github.com/szl-holdings/a11oy) — governed command center.
- Router: [szl-router](https://github.com/szl-holdings/szl-router) — sovereign inference routing.
- Frontier program: [frontier-54-runs](https://github.com/szl-holdings/frontier-54-runs) — pre-registered eval protocol.
- Alignment data: [ALIGNMENT.md](ALIGNMENT.md) — the map, with provenance.

## Honesty note

Numbers above are reproduced from the estate's own canonical census artifacts.
Anything not measured is stated as such. Nothing in this brief is projected
revenue or fabricated traction.
