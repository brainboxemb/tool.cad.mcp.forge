# Developer manual

This document describes how the Forge CAD MCP is maintained. User setup lives
in `docs/windows-vscode-conda.md`; CAD authoring behavior for agents lives in
the packaged skills themselves.

## Repository role

`tool.cad.mcp.forge` owns the AI-facing MCP workflow around Forge. It does
not own Forge's Python CAD API or SolidCraft's CAD engine.

The boundaries are:

- Forge owns Python API semantics, examples, guides and release behavior;
- Forge CAD MCP owns agent workflow, bounded workspace access, compile/runtime
  orchestration and skill delivery;
- SolidCraft owns saved-design execution, inspection and rendering.

## Agent skills

The MCP follows the Agent Skills pattern used by SolidCraft: a task-specific
`SKILL.md` is an operational playbook, not a documentation index. A local
`reference.md` contains the compact task facts the agent should know before it
consults larger release documentation.

Current MCP-owned skills:

| Skill | Responsibility |
| --- | --- |
| `forge-modeling` | build a new Forge model |
| `forge-editing` | change an existing Forge Python model |
| `forge-checking` | prove geometry/structure after build, edit or port |
| `forge-assemblies` | components, occurrences, dependencies and attachments |
| `forge-sheetmetal` | sheet-metal authoring within the supported Forge release |
| `solidcraft-to-forge` | understand an existing SolidCraft design and reconstruct it in Forge |

`forge-checking` is a companion skill. Modeling, editing, assembly,
sheet-metal and conversion work should use it rather than treating successful
compile/replay as acceptance.

## Skill ownership

Operational workflow text belongs in this MCP repository because it names MCP
tools such as `workspace_read`, `forge_compile` and
`solidcraft_analyze`.

Forge-specific facts stay release-matched to the configured Forge checkout:

- exact public API signatures/docstrings;
- guides;
- cheatsheet;
- model examples.

Do not copy those sources into MCP skill files. The skill may explain when to
read them and which verified example demonstrates a pattern.

## Skill file contract

Each skill directory contains:

```text
skills/<skill>/
├── SKILL.md
└── reference.md
```

`SKILL.md` should contain:

1. when the skill applies;
2. before-first-call state checks;
3. a small, efficient tool sequence;
4. editing/build rules;
5. verification requirements;
6. red flags and unsupported assumptions.

`reference.md` should contain stable operational facts and point to exact
release examples/API references where needed.

Do not add another public search-tool family merely to make skills convenient.

## Adding or changing a skill

1. Add/update the skill entry in `src/forge_mcp/skills.py`.
2. Declare the MCP tools the skill expects.
3. Add/update `SKILL.md` and `reference.md`.
4. Prefer examples already present in the supported Forge release.
5. State missing MCP capabilities explicitly instead of pretending they exist.
6. Run package tests against the exact supported Forge checkout.
7. Keep the skill change in the same issue/PR as any MCP tool contract it
   depends on when both must change together.

CI verifies that every declared MCP tool exists and that every packaged skill
and local reference can be read without a Forge checkout. Exact API/example
lookups still require the validated release checkout.

## Bootstrap and Forge checkout

The stable baseline currently accepts an explicit Forge release checkout.
Issue #41 tracks an operator-side `forge-cad-mcp bootstrap` command that will
manage the exact supported Forge checkout and matching `scpf` install.

Bootstrap is intentionally an operator CLI action, not an MCP model-work tool:
an AI editing a CAD model must not be able to replace or update the toolchain
that defines its own API contract.

## Release discipline

The MCP pins the Forge and SolidCraft versions it has actually accepted.
Changing either pin requires the normal issue/branch/PR acceptance path,
including real compile/runtime tests. Do not silently advance a dependency
because a newer version exists.
