# Agent guidance

Read docs/requirements.md, docs/design.md and docs/plan.md before implementation. Follow the shared documentation and engineering conventions in brainboxemb/meta.cad.solidcraft. Maintained engineering text is English.

Use one issue, work branch and PR per logical change. Integrate into dev; promote dev to main only explicitly. Use the shared merge-policy workflow and /merge, never a direct merge fallback. Until that policy is installed, do not merge.

Keep MCP thin: Forge owns compilation, SolidCraft CLI owns CAD execution, CAD verification owns checks. Do not introduce a direct SCPC dependency or proxy the existing SolidCraft MCP. AI authors Python Forge source.
