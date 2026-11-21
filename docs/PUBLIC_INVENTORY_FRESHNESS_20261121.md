# Public estate inventory — freshness and three-kind Hub coverage

**Owner:** `szl-holdings/szl-portal`. **Status:** Source-only research PR; not an authorized deployment, package release, Cloudflare change, model training run, Space promotion or signer receipt.

## Root cause and bounded correction

The Python portal backend cached its first successful estate snapshot indefinitely, even after the upstream inventory became unavailable. The exception handler sent the original upstream exception text in the HTTP response, which can contain sensitive URLs, paths or credential fragments. Its Hugging Face SDK inventoried models and datasets but **omitted Spaces** while the frontend described a whole-estate inventory.

The updated Python path now:

- Reads public `models`, `datasets`, and `spaces` independently from the `SZLHOLDINGS` author-scoped Hugging Face Hub API; exposes `spaces_public` and `spaces_private` in the summary while preserving existing model/dataset keys. Public listings cannot establish private asset counts, trained model quality, live authenticated rendering, or production readiness.
- Rejects malformed Hub responses, wrong-organization IDs, a fully saturated 1,000-result Hub request (which cannot prove the complete inventory), contradictory GitHub `total_count`, and GitHub search `incomplete_results=true`. Missing evidence becomes an upstream error, **never** a fabricated green zero.
- Uses a monotonic 60-second **completion-based** successful snapshot TTL and a 10-second bounded failure cooldown. A failed refresh destroys the old snapshot; concurrent misses share one producer under a lock. A cached payload is deep-copied before use.
- Returns fixed 502/503 JSON error codes without upstream exception text, plus `Cache-Control: no-store` and `X-Robots-Tag: noindex` on `/v1/*`. Existing `/healthz`, `/v1/snapshot`, `/v1/summary`, `/v1/alignment`, and `/v1/repos` routes remain.

## Evidence boundaries

An anonymous public Hub listing is not a signed receipt and cannot prove deployed byte parity, authenticated UI/data render, fine-tuning, weight lineage, runtime quality, service tenancy, x402 settlement or source-owner admission. The resulting metadata are *observations*, not operational-release permissions.

The Cloudflare Worker under `cloudflare/worker/index.js` is a **separate, owner-gated JavaScript deployment kit**, not evidence the Python backend is deployed or in sync. This PR does not change or publish that kit, DNS, Cloudflare Access, worker versions or payments. A fully Python serving path may be considered only after separate governed placement and source/tenant evidence.

## Verification and review

The new source-only negative fixtures cover successful three-kind inventory; truncated/foreign/malformed asset lists; GitHub incomplete search and total-count disagreements; TTL expiration and recovery; nonleaking 502 errors; bounded 503 backoff; single-flight concurrency; and no-store API semantics. An isolated synthetic Python/FastAPI environment passed **19 tests plus six subtests**, including a reproduction of the previous stale-read and exception-leak behavior. Those are **local fixture tests**, not a production release certificate.

The existing GitHub `ci.yml` installs only the Python SDK and pytest, not FastAPI/httpx. Therefore the HTTP-specific file explicitly skips when optional backend dependencies are absent; that is **not** equivalent to hosted backend qualification. The SDK census tests remain part of the normal CI path. Exact-head GitHub CI, independent non-author approval and deployment-window checks are separate release gates.

BETTERWITHAGE's desktop link was unavailable in this session; no local Ollama Kimi/Ministral, Claude or Perplexity call is claimed. This PR is an independently constructed GPT-6 source proposal, not a multi-model-approved patch.

## Public design peers — concepts only, no code copied

- Python's monotonic clock for bounded TTL: https://docs.python.org/3/library/time.html#time.monotonic
- Backstage's source-controlled Software Catalog ownership: https://backstage.io/docs/features/software-catalog/
- Hugging Face Hub repository pagination and listings: https://huggingface.co/docs/huggingface_hub/guides/search

**HOLD:** No commits to protected main, no model/Space training or deployment, no Cloudflare Worker change, no GPU spending and no release publication from this proposal.
