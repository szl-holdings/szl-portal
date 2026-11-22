# Domain Leader Study — szl-portal (estate front door)

OUROBOROS phase-3, cohort-02 tranche-1, Kimi ruling W26-C2T1-KIMI-20261123-ASK (GO). PROPOSE-ONLY study card: documentation only, no implementation in this PR.

## Current state (repo inspection 2026-11-23)
Python repo; description: estate front door: honest link index to the SZL Holdings governed-AI estate; backend, PyPI SDK and Cloudflare mentioned in its scope. No topics set (measured).

## Domain leaders studied
| Leader | What they have | Key sources |
| --- | --- | --- |
| lychee (Rust link checker) | Fast async link-health checking with config-file driven policy, retry/timeout handling, and canonical CI recipes — the reference answer to the front-door honesty question: a link index is only honest if a machine re-verifies it continuously | lychee.cli.rs/overview; lychee.cli.rs/continuous-integration/github (accessed 2026-11-23) |
| OpenTelemetry site build practice | Real large-site operator recipe: scheduled lychee link-checking integration with explicit pass/fail reporting for documentation trees | opentelemetry.io link-checking build docs (accessed 2026-11-23) |

## What the leaders do better
- Link health is CI-enforced, not assumed: a broken index entry fails the build instead of lying to visitors — the exact fail-closed posture the estate preaches.
- Policy lives in a config file (include/exclude, schemes, timeout, retry) so honesty rules are reviewable in-repo.
- Scheduled runs catch link rot between releases rather than at release time only.

## Gaps
- Measured repo state: no topics/license metadata set (mirrors earlier estate NO_TOPICS census class); no documented scheduled link-verification receipt surface for the estate index.

## Ranked #1 absorb proposal (NOT implemented in this PR)
Scheduled lychee pass over the estate link index with a published link-health receipt (checked count, fail list, per-run timestamp), fail-closed on new breaks. Expected benefit: front-door claims become machine-verified; PyPI/Cloudflare destination health becomes continuously proven. Cost/risk: low; docs-content CI only, no runtime change. Validation: one dry run against current index, receipt compared against known-good entries. Rollback: schedule removal, no state mutated.

## Sources
- lychee overview: https://lychee.cli.rs/overview/ (accessed 2026-11-23)
- lychee CI recipes: https://lychee.cli.rs/continuous-integration/github/ (accessed 2026-11-23)
- OTel site link-checking: https://opentelemetry.io/site/build/link-checking/ (accessed 2026-11-23)
