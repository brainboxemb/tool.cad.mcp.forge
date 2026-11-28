---
name: forge-modeling
description: Author or modify maintained Forge Python models; load specialized knowledge only when the design requires it.
---

# Forge modeling

Forge is the modeling API. SolidCraft executes and verifies the model. Author
geometry and design relationships in Python, normally `scpf/model.py`; do not
author SolidCraft command JSON or direct geometry commands. The compiler owns
the mapping to SolidCraft.

## Start

- Understand the requested dimensions, datum, shape, editable relationships and
  physical parts. Select a construction from the requirements, not a worked
  example. Ask only about missing requirements that materially affect the design.
- Confirm the configured writable target with `workspace_status` if not
  already known. If source existence is unknown, list the owner root rather
  than assuming `scpf/` exists. Read existing source before changing it.
- Use the lowest sufficient knowledge level below. Do not fetch references
  merely because they are available.

## Starting a new `scpf/model.py`

Import public SCPF names, define a model class, declare its dimensions and
return the final Shape or assembly from `build()`. One public class with
`build()` can be discovered automatically; with several public model classes,
select the root explicitly. An explicit final constructor is a useful convention.

```python
from scpf import Anchor, Cylinder


class SpacerBlank:
    diameter = 26.0
    height = 13.0

    def build(self):
        return Cylinder(d=self.diameter, h=self.height, anchor=Anchor.BOTTOM)


SpacerBlank()
```

This example teaches the file contract only. No `main()` or `show()` is
required; a plain class is sufficient.

- Lower-case numeric class fields represent editable model parameters.
- Leading-underscore fields are build-time inputs; UPPER_CASE numeric fields
  are fixed constants, not published parameters.
- Use `self.<field>` and supported symbolic arithmetic for dependent
  dimensions. Do not flatten editable inputs with `pv()` or `float()`.
  General Python computation is not automatically parametric.

## Level 1 — common authoring knowledge

Use this entrypoint alone when it supplies the semantics and syntax needed.
Lengths are in millimetres. Choose the datum instead of manually compensating
for an anchor.

| Intent | Forge vocabulary |
| --- | --- |
| Basic solid | `Box(length, width, height)` (X, Y, Z); `Cylinder(d=diameter, h=height, axis=Axis.Z)`; `Sphere(radius)`. All default to CENTER; use `anchor=Anchor.BOTTOM` for a Z-bottom datum where applicable. |
| Geometric placement | `shape.at(x, y, z, anchor=Anchor.CENTER)` places a supported primitive datum. `shape.at(target)` aligns centers, not faces. |
| Combine solid geometry | `a + b`, `a - b`, `a & b` join, cut, intersect supported operands. Support depends on the operand types. |
| Face and datum selection | TOP/BOTTOM are +Z/-Z, LEFT/RIGHT are -X/+X, FRONT/BACK are -Y/+Y. `Faces` selects faces; `Anchor` selects placement datums. |
| Hole feature | `Hole(d=diameter, depth=Depth.THROUGH_ALL)` expresses a through-hole. For a simple TOP-face hole, apply `body + hole.on(body, face=Faces.TOP)`; the feature itself removes material. Read the relevant reference for directional, blind or advanced hole-family placement. |
| Explicit 2D intent | Use `with Sketch(plane="XY") as profile:` and author `Rectangle2D(width, depth)`, `Circle2D(d=diameter)` or another supported profile inside it. After leaving the context, `profile.extrude(distance)` creates 3D geometry. Negative distance reverses direction; `sym=True` extrudes symmetrically. A face-attached sketch uses `Sketch(on=body, parent=Anchor.TOP)`; consult its contract for region selection and cuts. |
| Edge treatment | `body.fillet(radius, edges=Edges.VERTICAL)` or `body.chamfer(distance, edges=Edges.from_faces(Faces.TOP))` on supported bodies. Choose a selector matching the intended edges. |
| Separate physical parts | A Shape is geometry, not an occurrence. Use component/assembly definitions, occurrence Placement and attachment for separate physical parts. Consult the assembly guides when needed. |

These are independent API idioms, not a recipe or a mandatory sequence.

## Level 2 — resolve a specific API question

When a signature, supported operand, selector or placement rule is uncertain,
call `skill_reference` with skill `forge-modeling` and the exact file:

- `references/api/Box.json`, `references/api/Hole.json`,
  `references/api/Sketch.json` for constructors;
- `references/api/Shape.on.json`,
  `references/api/Shape.rectangular_pattern.json`,
  `references/api/Sketch.extrude.json` for methods.

These API paths are virtual references, not files in the checkout. The MCP
constructs the JSON response directly from the installed public Python API
(signature, docstring and exposed members). Guides and examples are actual
Forge checkout files. Read only unresolved
symbols. For discovery, use `references/index.json` or
`references/cheatsheet.yml` only if you cannot identify a relevant symbol.
The full `references/api.md` is not a prerequisite; reserve it for broad
API questions. Never guess unsupported API.

## Level 3 — topic-specific knowledge

If an unfamiliar construction needs more than a signature, select the relevant
topic. These are optional routes, not a reading checklist.

| Trigger in the design | Read only when relevant |
| --- | --- |
| Complex profiles, region selection, sketch patterns | `references/guide/geometry.html` |
| Advanced holes, edge features, shells or feature patterns | `references/guide/features.html` |
| Relative placement or attachment | `references/guide/transformations.html` |
| Shared parameters, symbolic math or reusable definitions | `references/guide/model-objects.html` |
| Separate parts, joints or assembly reuse | `references/guide/assembly-basics.html` or `references/guide/components.html` |
| Folded sheet, flange, hem, flat pattern or sheet manufacturing rule | Skill `forge-sheet-metal` |
| Specialized enclosure lip, snap-fit, screw boss or support rest | Skill `forge-plastics` |
| Engineering drawing requested | `references/guide/drawings.html` |

A metal material alone does not require sheet-metal modeling; plastic material
or 3D printing alone does not require plastic-specific features. If the task
does not require a topic, skip it. The optional skills are not prerequisites
for ordinary modeling.

If a selected guide or skill is insufficient, read the exact API reference
or use `references/index.json` to find one relevant qualified example
(`references/examples/<model-id>.py`). Use examples to establish supported
idioms, not to choose the user's geometry. Stop loading knowledge as soon as
the current design question is resolved. All Forge knowledge must come through
`skill_reference`, not shell, checkout browsing, GitHub or web search.

## Build and verify

- Create source with `workspace_write`; it creates missing parent directories.
  When replacing source, use the SHA-256 from `workspace_read` as
  `expected_sha256`.
- For live work, read `solidcraft-control` when needed and use `forge_live`
  to compile/apply. For saved evidence use `forge_compile` and headless
  replay/evaluate/snapshot. Do not compile separately before a normal live apply.
- Check dimensions, placements, parameters and structure against the request;
  retrieve useful visual evidence. Test parameter mutation when requested or
  when needed to verify associativity.
- Change design intent in Forge source. Use SolidCraft for execution,
  inspection, parameter testing, view and rendering only. Report missing
  knowledge or execution failures instead of switching CAD routes.

## Owner boundaries

The configured owner is the only writable target. Never discover or switch
owners implicitly. Read explicitly referenced catalog dependencies only through
`catalog_dependency_list(owner)` and `catalog_dependency_read(owner, path)`.
For an existing SolidCraft design supplied for conversion use
`solidcraft-to-forge` instead.
