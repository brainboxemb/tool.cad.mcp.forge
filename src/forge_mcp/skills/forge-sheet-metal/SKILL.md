---
name: forge-sheet-metal
description: Optional Forge knowledge for formed sheet parts requiring thickness rules, bends, flanges, hems or flat patterns. Not for metal material alone.
---

# Forge sheet metal

Use only when the design requires sheet manufacturing semantics. Start with
the common `forge-modeling` contract; do not reread it if already loaded.

Read `references/guide/sheet-metal.html` for the supported Forge workflow.
One active sheet rule owns thickness, bend radius and K-factor; features
inherit the rule. Use a closed Sketch with `Sketch.sheet_metal` for a flat
blank or a finished open sketch chain with `Shape.contour_flange` for a
formed contour. Choose the construction from the design, not from an example.

Resolve exact signatures only for needed features using
`references/api/Sketch.sheet_metal.json` or
`references/api/Shape.<method>.json` (fold, flange, contour_flange, hem,
path_flange, perforate). Do not assume associative topology selections are
supported; follow the guide's documented pick constraints.

Verify the relevant formed geometry, sheet rule, bends and flat-pattern
semantics where required. Use the SolidCraft verification route, not native
geometry authoring. Report unavailable manufacturing evidence explicitly.
