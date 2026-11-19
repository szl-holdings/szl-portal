# Monetization — SZL Holdings estate

Owner-ordered direction: monetize the estate. This document defines the
revenue mechanics, what is already built, and what is owner-gated. Doctrine
applies: no agents make payments, sign agreements, or create accounts; every
activation step below is an owner console action.

## Product surface (already built, in this repo)

1. **`szlholdings` Python SDK** (PyPI) — free, Apache-2.0. Adoption funnel for
   the API tiers below.
2. **Estate inventory API** (FastAPI backend + Cloudflare Worker) — the
   metered surface: live GitHub/HF inventory, alignment matrix, receipt-pinned
   queries.
3. **Investor/dev portal** (Pages) — the storefront.

## Revenue tiers

| Tier | Price | What it includes | Activation |
|---|---|---|---|
| Free | $0 | Public inventory, SDK, portal. Rate-limited. | live once deployed |
| Pro API | monthly subscription | Higher rate limits, alignment live-joins, webhook pushes of estate events | Cloudflare Workers Paid + API keys (KV) |
| Enterprise / data-room | negotiated | Contract evidence, verification reports, SLAs, private evals | owner-signed agreement + private infra |

## Model monetization (Hugging Face aligned)

- Gated model repos: flagship fine-tunes (e.g. Estate-v1 line) move from
  public to **gated** as the release-gate workflow releases qualified
  versions; access control is owner-managed on HF.
- Deployment licensing: GGUF/serving kits licensed separate from weights.
- Receipts as the differentiator: every paid tier ships verifiable provenance
  (DSSE-signed), which is the estate's core market claim — *AI that signs its
  work*.

## Boundary with the x402 lane

The x402 (live payment-per-inference) lane is owned by a parallel lane in
this estate; its receipts are the owner-gated record for per-call monetization.
This portal's tiers are subscription/API-key based and deliberately do not
duplicate or preempt x402 work. Where x402 lands, its seller card links here.

## What is owner-gated (not self-serve)

- Cloudflare paid plan enablement
- Price setting and payment processor accounts
- HF gated-model switches on flagship repos
- Any enterprise agreement
