---
name: solidcraft-control
description: Execute Forge designs, inspect the active SolidCraft session, test parameters and control the camera/render. Not a geometry authoring skill.
---

# SolidCraft control

Forge owns the maintained geometry. Use SolidCraft to execute and verify it.
No full SolidCraft command reference is required for the normal Forge workflow.

## Normal live workflow

SolidCraft must be running with its assistant connection enabled. The MCP
uses the authenticated local connection; never ask for or expose its token.

1. For a fresh Forge model, use `forge_live(source_path="scpf/model.py", new=True)`
   (or the configured source default). This compiles and applies the design
   to a new active document. Do not separately compile unless needed.
2. Use `solidcraft_live_inspect` for the active parameters, body names and
   timeline summary. Request `measure=True` for geometry measurements and
   `sketch_counts=True` when relevant. Inspect before changing an existing
   active design, not before a fresh apply unless needed to protect user work.
3. When native parameter behavior must be tested, change an existing parameter
   and inspect again.
4. Set a useful camera if needed, then call `solidcraft_live_render` for the
   current-camera image.

Use `environment` or `workspace_status` only if readiness or target identity
is unresolved. Do not repeat known startup checks.

## Small native command vocabulary

Use `solidcraft_live_execute(command, params)` only when a dedicated tool
does not cover the operational question.

| Intent | Command |
| --- | --- |
| List existing parameters when inspection is insufficient | `parameters.list` |
| Test one existing parameter | `parameters.change`, params `{"name": "<existing name>", "expression": <value>}` |
| Standard camera | `view.isometric`, `view.front`, `view.top`, `view.fit` as needed |
| Additional structure or face evidence | `component.list`, `model.faces` only when necessary |

Use the installed command contract; do not guess unfamiliar parameter shapes.
The full `references/solidcraft-commands.md` currently describes 0.49.0,
not the running 0.50.0 baseline. It is not authoritative for new 0.50 syntax.
If necessary knowledge is unavailable, report the gap rather than retrieving
the entire command set by default or guessing commands.

Do not use native geometry-creation/modification commands to correct a Forge
design. Change Python source and reapply. A GUI parameter test is not a source
change; persist it in Forge only if it represents requested design intent.

## Verification and evidence

Use numeric/structural evidence and a suitable visual view. An image or tool
success alone does not establish dimensional correctness. Use saved replay,
evaluation and snapshots when independent saved evidence is required.
Live actions and renders are persisted under the configured `build/` evidence
paths when logging is enabled. Do not edit the evidence log.

A timed-out mutation may have applied; inspect before retrying. If live control
is unavailable, report it rather than silently switching to headless execution
when the user requested the GUI.
