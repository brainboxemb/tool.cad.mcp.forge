# Forge MCP handoff

Repository: `brainboxemb/tool.cad.mcp.forge`.

This document is the easy-to-find handoff entrypoint for a new work session.
The copyable message below is deliberately an entrypoint, not a second plan.
Current work always comes from live GitHub state and `docs/plan.md`.

Shared SolidCraft/CAD documentation conventions live in
`brainboxemb/meta.cad.solidcraft`.

## Handoff message

Copy the complete text block below into a new chat.

~~~text
You are continuing work on brainboxemb/tool.cad.mcp.forge.

Repository role:

- expose version-matched Forge Python authoring knowledge and bounded execution through MCP;
- keep Forge compilation, SolidCraft CAD execution and CAD verification in their owning layers;
- do not proxy SolidCraft MCP or duplicate CAD/compiler logic in this repository.

Use this handoff only as the entrypoint. Do not treat copied handoff text as
fresher than GitHub or the repository plan.

Start by:

1. inspecting the current issues, pull requests and branches;
2. reading AGENTS.md;
3. reading docs/plan.md;
4. treating docs/plan.md as the source of truth for unfinished work;
5. following the current work order from the plan rather than old handoff text;
6. creating an issue before implementation when the logical change has none;
7. keeping one logical change to one temporary branch and one PR;
8. updating requirements/design when behavior or architecture changes;
9. reconciling the plan after merge or release.

Durable working rules:

- main is the only permanent product/source branch; temporary work branches target main directly;
- integrate only through the repository /merge policy with green central PR CI;
- Forge owns compilation; invoke additional SolidCraft CLI/control operations directly and reuse existing CAD verification;
- keep the MCP thin and local-stdio execution bounded.

Shared document structures live in brainboxemb/meta.cad.solidcraft:
templates/docs/plan.md and templates/docs/handoff.md.
~~~

## Template guidance

The text block above is the actual handoff message. Current versions, SHAs,
active issue status and next actions belong in GitHub and `docs/plan.md`, not
in this handoff.
