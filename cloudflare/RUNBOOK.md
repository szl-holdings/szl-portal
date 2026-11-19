# Cloudflare onboarding runbook — SZL portal

Status of this kit: **everything in this repo is deploy-ready**; the only
missing ingredient is a Cloudflare account + API token, which is owner-gated
(no agent in this estate creates accounts, triggers paid plans, or handles
billing). This runbook is the exact sequence for the owner (or a delegated
operator with owner-provided credentials).

## What deploys where

| Piece | Source | Cloudflare product | Cost |
|---|---|---|---|
| Investor/dev portal | `frontend/` | Pages (static) | free |
| Inventory API | `cloudflare/worker/index.js` | Workers | free tier |
| Full-featured API | `backend/app.py` (FastAPI) | any host (self-host / future) | existing infra |

Nothing here requires a paid plan to go live.

## One-time owner steps (owner-gated)

1. Create/confirm a Cloudflare account for SZL Holdings (owner console action).
2. Create an API token with **Workers Scripts:Edit** and **Pages:Edit**
   (scoped to the account). Keep it in the owner's secret store — never in
   this repo, never in agent memory.
3. From a machine with the token:
   ```bash
   export CLOUDFLARE_API_TOKEN=...   # from the owner's secret store
   export CLOUDFLARE_ACCOUNT_ID=...
   npx wrangler pages deploy frontend --project-name szl-portal
   cd cloudflare && npx wrangler deploy
   ```
4. Optional: attach the `szlholdings.com` / `a-11-oy.com` domains to the
   Pages project in the Cloudflare dashboard (owner console action).

## Free-tier honesty notes

- The Workers free plan serves the read-only inventory endpoints within its
  daily request allowance; bursts beyond that return Cloudflare errors rather
  than invented data. The FastAPI backend remains the full-featured host.
- Both upstreams (GitHub, Hugging Face public APIs) are rate-limited; the
  Worker caches for 15 minutes and the FastAPI backend caches per process.

## Monetization activation gate

Pricing tiers (see `MONETIZATION.md`) activate only when the owner affirmatively
enables a Cloudflare paid feature (Workers Paid for higher limits, KV for API
keys). No agent may enable a paid feature: that is an owner console action.
