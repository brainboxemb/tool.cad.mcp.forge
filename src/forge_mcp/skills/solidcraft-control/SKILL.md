---
name: solidcraft-control
description: Operate, inspect and verify the running SolidCraft GUI through the authenticated local control channel.
---

# SolidCraft control

Use this skill when the task requires operating the active SolidCraft desktop session rather than only replaying or inspecting saved `.sc` evidence.

The live SolidCraft session and saved/headless evidence are different things:

- live control changes or inspects the design currently open in SolidCraft;
- headless replay/evaluate/snapshot operates on bounded files below the configured workspace;
- do not claim that a live visual check replaces independent saved-design evidence when the task requires both.

## Start of a live session

1. Call `environment` and confirm the local CAD stack is ready.
2. Read `workspace_status` and stay inside the configured workbench/owner.
3. Call `solidcraft_live_inspect` before changing an existing active design.
4. If the task is a fresh Forge model, use `forge_live(..., new=true)` so the compiled Forge document is applied to a new empty SolidCraft design.
5. Use `solidcraft_live_new` only when intentionally replacing the active GUI design.

SolidCraft must already be running with **Preferences → Assistant → Agents through MCP → Let AI agents connect** enabled. The MCP reuses Forge's authenticated localhost control client and never asks for or exposes the control token.

## Native SolidCraft commands

Use `solidcraft_live_execute(command, params)` for one registered SolidCraft engine command. SolidCraft performs strict parameter validation.

Before guessing a command or parameter shape, read `references/solidcraft-commands.md`.

Common operations:

- `parameters.list` — list user/sketch/feature parameters and dependencies;
- `parameters.change` — change one parameter or a set of existing parameters atomically;
- `component.list` — inspect component structure;
- `model.faces` — inspect native faces of a named body;
- `view.apply` — restore a standard/named view or apply an explicit camera;
- `view.fit`, `view.home`, `view.isometric`, `view.front`, `view.top` — change the live camera;
- `view.visual_style` — select shaded/wireframe display state;
- `select.set` and `select.clear` — manage native selection when a command requires it.

Prefer semantic parameter edits over rebuilding geometry when the design already exposes the intended variable. After every mutation, inspect the result again rather than assuming a successful command produced the intended model.

## Forge and SolidCraft together

For interactive Forge modeling:

1. author or update `scpf/model.py` with `workspace_write`;
2. call `forge_live` to compile Forge source and apply its replay document to the running SolidCraft design;
3. inspect the active design with `solidcraft_live_inspect`;
4. if useful, use native SolidCraft parameter/view commands through `solidcraft_live_execute`;
5. set a useful camera/view;
6. call `solidcraft_live_render` to retrieve model image evidence from the active GUI session;
7. correct the maintained Forge Python source when a change belongs to the design definition rather than leaving an accidental GUI-only edit.

Do not silently turn a GUI-only experimental parameter edit into maintained design intent. If it should persist in the Forge model, update the Forge source and reapply it.

## Visual evidence

`solidcraft_live_render` uses SolidCraft `ui.render`: it renders the active model with the current live camera and returns the PNG as MCP image content. Use view commands first when a specific orientation matters.

The render is also stored below the workspace `build/` tree and the live action is appended to the session evidence log when logging is enabled.

A picture is additional evidence, not the only evidence. Use `solidcraft_live_inspect`, native parameter/component/face queries, or saved-design evaluation for dimensions and structural claims.

## Evidence log

Live workbench actions are logged automatically by the MCP when enabled in `project.yml`. The log contains operation metadata, bounded inputs/results, output paths and hashes. Authentication tokens are never logged.

Do not edit the evidence log manually during the session.

## Failure handling

A control-channel timeout is not proof that SolidCraft did nothing. Inspect the running app before retrying a timed-out mutation.

If the live session is unavailable, report that explicitly. Do not silently substitute headless replay when the task specifically requires operating the running SolidCraft GUI.
