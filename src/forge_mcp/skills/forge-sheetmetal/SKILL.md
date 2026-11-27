---
name: forge-sheetmetal
description: Use when building or changing a Forge sheet-metal part using sheet_metal, fold, flange, contour_flange, hem, path_flange or perforate.
---

# Forge sheet metal

## Overview
Sheet-metal intent includes manufacturing parameters as well as visible shape.
Establish thickness, bend radius, K-factor/rule and the intended bend/flange
geometry before authoring. Never invent manufacturing values that the user or
project has not supplied.

Use `forge-checking` alongside this skill.

## Before the first edit
1. Call `environment` and `workspace_status`.
2. Read target `model.yml` and existing source.
3. Read this skill's `reference.md`.
4. Read the exact v0.19 example for the operation you need.
5. Write down:
   - thickness;
   - bend radius;
   - K-factor/rule;
   - blank/profile dimensions;
   - bend/flange/hem parameters;
   - expected overall extents and body count.

If a manufacturing parameter is unknown, ask/report it instead of silently
choosing a shop value.

## Author
- Start a flat sheet with `Sketch.sheet_metal(...)` when that matches the
  design.
- Use `fold`, `flange`, `contour_flange`, `hem`, `path_flange` or
  `perforate` only according to the release example/API.
- Keep material-rule values parameterized when the model exposes them.
- Use exact edge/line geometry from the model; do not replace a sheet-metal
  feature with generic solid CSG merely to make the visible shape similar.

## Verify
Compile, replay, analyze and render, then apply `forge-checking`.
Check overall extents, body count, feature/history evidence and visible bend
orientation.

The current MCP does not expose a dedicated flat-pattern/bend-table inspection
tool. If manufacturing acceptance requires those outputs, report that gap
rather than claiming them from a 3D render.

## Red flags
| Thought | Do instead |
| --- | --- |
| "Use K=0.5; that's common" | Use the project/user rule or report it missing. |
| "A box looks like the folded part" | Preserve sheet-metal features. |
| "The bend looks 90 degrees" | Check source parameter/history plus geometry evidence. |
| "3D checks prove the flat pattern" | Report flat-pattern verification unavailable in the current MCP. |
