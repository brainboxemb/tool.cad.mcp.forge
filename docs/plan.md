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

Issue #1: establish protocol smoke test and shared CI/merge conventions. Initial in-process protocol CI passed (run 45770916868). Extended subprocess stdio, concurrent Streamable HTTP and image decoding tests pending CI. Next gate: pass extended tests, then install the shared merge-policy bootstrap on the default branch.

### WS2 — CAD acceptance

After bootstrap, establish Forge version-matched knowledge, isolated workspace, compilation, direct SolidCraft CLI inspection/rendering and verification. Create separate implementation issues before work.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #1 | dev | now | Qualify protocol and install shared CI/merge policy |

## Recently completed

Repository and development branches created.

## Next checkpoint

Extended transport and image acceptance, then shared merge-policy integration; no release until real CAD integration is demonstrated.
