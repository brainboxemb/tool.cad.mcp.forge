# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

No qualified release. Main is stable, dev is integration. Bootstrap #1, skills #3, workspace #6, Forge compilation #8 and SolidCraft runtime #9 are integrated through /merge and qualified in CI. The runtime path uses the existing cad-solidcraft:v0.3.6 / SolidCraft 0.49.0 image.

## Lane rule

Issue branches target dev. Stable promotion is explicit. Use shared /merge policy.

## Engineering constraints

Follow [shared principles](https://github.com/brainboxemb/meta.cad.solidcraft/blob/main/docs/engineering-principles.md). Local model iteration must not depend on GitHub. Python/SolidCraft execution remains local-stdio-only until isolated remote execution exists.

## Active workstreams

### WS1 — existing SolidCraft design to Forge

Issue #5: make the solidcraft-to-forge skill executable as an efficient workflow. Add compact input classification and combined native analysis, correct raw .sc handling, then qualify a hand-authored native SolidCraft design against a separately authored Forge Python translation with numeric/structural and visual evidence.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #5 | dev | now | Qualify independent native input analysis and translated Forge match |

## Recently completed

- #1 protocol/repository bootstrap.
- #3 skills and release-matched Forge references.
- #6 bounded local workspace.
- #8 real Forge Python -> SolidCraft command JSON compilation.
- #9 real SolidCraft replay/eval/component inspection/PNG rendering over MCP.

## Next checkpoint

End-to-end existing-design conversion acceptance, then decide the first usable pre-release and client packaging/configuration. Docker distribution remains optional.
