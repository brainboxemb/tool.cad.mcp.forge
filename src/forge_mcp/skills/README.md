# Skills for agents that use Forge CAD MCP

These skills teach an AI how to use the Forge CAD MCP efficiently and how to
prove that a CAD change is correct. Forge itself remains the owner of Python API
semantics, examples and release documentation. The MCP skills own the agent
workflow around those release-matched sources and the MCP execution tools.

| Skill | Use when |
| --- | --- |
| `forge-modeling` | building a new Forge part or feature-based model |
| `forge-editing` | changing or fixing an existing Forge Python model |
| `forge-checking` | checking any build/edit/port against geometric and structural evidence |
| `forge-assemblies` | composing components, occurrences, attachments or subassemblies |
| `forge-sheetmetal` | building or changing Forge sheet-metal models |
| `solidcraft-to-forge` | translating an existing SolidCraft design into maintainable Forge Python |

`forge-checking` is a companion skill. Load it alongside modeling, editing,
assemblies, sheet metal or conversion whenever correctness matters.

The operational files in this directory are packaged with the MCP and can be
read without a Forge checkout. Exact API signatures, guides and examples are
served from the configured, validated Forge release through
`skill_reference`.
