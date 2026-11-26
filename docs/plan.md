# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

No qualified release. Main is stable, dev is integration. Bootstrap #1 and skills-first Forge knowledge #3 are integrated through /merge and qualified in CI.

## Lane rule

Issue branches target dev. Stable promotion is explicit. Use shared /merge policy.

## Engineering constraints

Follow [shared principles](https://github.com/brainboxemb/meta.cad.solidcraft/blob/main/docs/engineering-principles.md). Avoid GitHub round trips inside model iteration; reuse existing runtime and libraries.

## Active workstreams

### WS1 — local authoring workspace

Issue #6: explicit local workspace, bounded model/source reads and safe Python source editing. Next gate: real MCP tests for listing, native input reads, optimistic source updates, traversal/symlink rejection and HTTP write denial.

### WS2 — CAD execution and conversion

After #6, add Forge compilation and SolidCraft inspect/render capabilities in separate issues. Issue #5 then qualifies the solidcraft-to-forge workflow against real native inputs and generated Forge models. Forge documentation drift remains tracked upstream as brainboxemb/lib.py.solidcraft.forge#210.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #6 | dev | now | Qualify local workspace and source editing |
| #5 | dev | later | Qualify native SolidCraft analysis and Forge conversion after execution tools |

## Recently completed

- Bootstrap #1: protocol, stdio, HTTP, concurrent clients, PNG transport and shared merge/cleanup qualification.
- Knowledge #3: skill_list/skill_reference, forge-modeling and solidcraft-to-forge workflow skills, release-matched Forge references.

## Next checkpoint

Workspace acceptance, then actual Forge compilation and SolidCraft execution. Docker distribution remains optional.
