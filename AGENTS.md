# Agent guidance

Read docs/requirements.md, docs/design.md and docs/plan.md before implementation. Follow the shared documentation and engineering conventions in brainboxemb/meta.cad.solidcraft. Maintained engineering text is English.

Use one issue, temporary work branch and PR per logical change. Target `main` directly. Integrate only through the repository merge-policy workflow and `/merge`; never use a direct merge fallback. `main` is the only permanent product/source lane.

Keep MCP thin: Forge owns compilation, SolidCraft CLI owns CAD execution, CAD verification owns checks. Do not introduce a direct SCPC dependency or proxy the existing SolidCraft MCP. AI authors Python Forge source.
