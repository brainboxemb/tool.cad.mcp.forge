# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

No qualified release. Main is stable, dev is integration. Bootstrap #1, skills #3, workspace #6 and real Forge compilation #8 are integrated through /merge and qualified in CI.

## Lane rule

Issue branches target dev. Stable promotion is explicit. Use shared /merge policy.

## Engineering constraints

Follow [shared principles](https://github.com/brainboxemb/meta.cad.solidcraft/blob/main/docs/engineering-principles.md). Local model iteration must not depend on GitHub. Python/SolidCraft execution remains local-stdio-only until isolated remote execution exists.

## Active workstreams

### WS1 — SolidCraft runtime

Issue #9: controlled replay, native model evaluation and PNG snapshots using the existing released SolidCraft runtime. Next gate: compile a real Forge fixture, replay to native .sc, verify measurement evidence and receive a real PNG over MCP inside cad-solidcraft:v0.3.6.

### WS2 — existing design conversion

Issue #5 follows #9: qualify solidcraft-to-forge against a real original native design, author Forge Python independently from observed evidence, and compare generated/native measurements and views.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #9 | dev | now | Qualify real SolidCraft replay/eval/snapshot through MCP |
| #5 | dev | next | Qualify existing native design analysis and translation |

## Recently completed

- #1 protocol/repository bootstrap.
- #3 skills and release-matched Forge references.
- #6 bounded local workspace.
- #8 real Forge Python -> SolidCraft command JSON compilation.

## Next checkpoint

Real SolidCraft runtime acceptance, then the first end-to-end existing-design conversion. Docker distribution remains optional; runtime CI reuses cad-solidcraft:v0.3.6.
