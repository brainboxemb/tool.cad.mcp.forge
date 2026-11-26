# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

No qualified stable release yet. Main is stable and dev is integration. Dev now contains the qualified protocol, skills-first Forge knowledge, bounded workspace/source editing, Forge compilation, SolidCraft 0.49 replay/analyze/component/snapshot tools, and the independent existing-SolidCraft-to-Forge acceptance workflow. Real CAD acceptance reuses cad-solidcraft:v0.3.6.

## Lane rule

Issue branches target dev. Stable promotion is explicit. Use shared /merge policy.

## Engineering constraints

Follow [shared principles](https://github.com/brainboxemb/meta.cad.solidcraft/blob/main/docs/engineering-principles.md). Model iteration must remain local and independent of GitHub. Python/SolidCraft execution is local-stdio-only until authenticated isolated remote execution exists.

## Active workstreams

### WS1 — usable local client baseline

Issue #13: make the qualified server directly startable from a normal MCP client with explicit workspace/Forge/SolidCraft paths, add a non-CAD doctor readiness gate, pin the qualified FastMCP dependency and document one generic stdio configuration.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #13 | dev | now | Qualify explicit local startup and doctor from the installed command |

## Recently completed

- #1 protocol/repository bootstrap.
- #3 skills and version-matched Forge references.
- #6 bounded workspace/source editing.
- #8 Forge Python compilation.
- #9 real SolidCraft runtime operations and PNG transport.
- #5 independent existing SolidCraft design analysis and Forge translation acceptance.

## Next checkpoint

After #13 is green, promote the first usable local MCP baseline from dev to main. Only then decide version/tag/release packaging. Docker distribution remains optional and is not part of this checkpoint.
