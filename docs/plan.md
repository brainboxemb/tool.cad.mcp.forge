# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

No qualified release. Main is stable, dev is integration. Bootstrap PR #2 merged into dev through /merge; protocol and policy CI passed.

## Lane rule

Issue branches target dev. Stable promotion is explicit. Use shared /merge policy.

## Engineering constraints

Follow [shared principles](https://github.com/brainboxemb/meta.cad.solidcraft/blob/main/docs/engineering-principles.md). Avoid GitHub round trips inside model iteration; reuse existing runtime and libraries.

## Active workstreams

### WS1 — Forge knowledge and CAD acceptance

Issue #3: skills-first knowledge interface, with release-matched local references. Initial search-tool CI failed due to a test helper argument collision; that interface is superseded by skill_list/skill_reference. Next gate: real client acceptance against Forge v0.19.0. Then establish isolated workspace, compilation, direct SolidCraft CLI inspection/rendering and verification in separate issues.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #3 | dev | now | Qualify skill entrypoints and release-matched references |
| #5 | dev | later | Qualify existing SolidCraft design analysis and Forge conversion after workspace and runtime tools |

## Recently completed

Bootstrap #1: protocol, stdio, HTTP, concurrent clients, PNG transport and shared merge/cleanup qualification.

## Next checkpoint

Real Forge knowledge acceptance, followed by CAD execution. Docker distribution is optional deployment packaging, not a prerequisite for local MCP use. Reuse the existing released runtime for CAD CI. No public deployment or new runtime image is assumed.
