# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

No qualified release. Main is stable, dev is integration. Bootstrap #1, skills knowledge #3 and bounded workspace #6 are integrated through /merge and qualified in CI.

## Lane rule

Issue branches target dev. Stable promotion is explicit. Use shared /merge policy.

## Engineering constraints

Follow [shared principles](https://github.com/brainboxemb/meta.cad.solidcraft/blob/main/docs/engineering-principles.md). Local model iteration must not depend on GitHub. Python execution remains local-stdio-only until isolated remote execution exists.

## Active workstreams

### WS1 — Forge compilation

Issue #8: compile one workspace Python Forge model through the released scpf CLI to generated SolidCraft command JSON under build/. Next gate: real successful compile, structured model-error evidence and transport/output-boundary tests.

### WS2 — SolidCraft execution and conversion

Issue #9 follows: replay generated JSON into native .sc, inspect/evaluate and render via existing SolidCraft runtime/verification contracts. Issue #5 then qualifies solidcraft-to-forge against a real original design and independently authored Forge model.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #8 | dev | now | Qualify real local Forge compilation |
| #9 | dev | next | Add bounded SolidCraft replay, inspect/eval and snapshots |
| #5 | dev | later | Qualify native SolidCraft analysis and Forge conversion after #9 |

## Recently completed

- Bootstrap #1: protocol and repository policy.
- Knowledge #3: skills and release-matched Forge references.
- Workspace #6: bounded source/native reads and protected Python source edits.

## Next checkpoint

Real Forge compile acceptance, then actual SolidCraft execution/rendering. Docker distribution remains optional.
