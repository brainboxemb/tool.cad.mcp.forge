# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

New repository; no qualified release. Main is stable, dev is integration.

## Lane rule

Issue branches target dev. Stable promotion is explicit. Shared merge policy must be installed before integration.

## Engineering constraints

Follow [shared principles](https://github.com/brainboxemb/meta.cad.solidcraft/blob/main/docs/engineering-principles.md). Avoid GitHub round trips inside model iteration; reuse existing runtime and libraries.

## Active workstreams

### WS1 — bootstrap

Issue #1: establish protocol smoke test and shared CI/merge conventions. Initial and extended protocol CI passed (runs 45770916868 and 45771379444). Shared merge and cleanup policy seeded on main and dev; next gate: qualify policy tests and integrate PR #2 through /merge.

### WS2 — CAD acceptance

Issue #3 is next: expose version-matched API knowledge and examples through MCP. Then establish isolated workspace, compilation, direct SolidCraft CLI inspection/rendering and verification in separate issues.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #1 | dev | now | Qualify shared policy and integrate PR #2 via /merge |
| #3 | dev | next | Expose installed Forge API and version-matched documentation |

## Recently completed

Repository and development branches created.

## Next checkpoint

Bootstrap integration via /merge, then Forge knowledge acceptance; no release until real CAD integration is demonstrated.
