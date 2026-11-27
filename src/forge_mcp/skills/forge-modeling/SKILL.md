---
name: forge-modeling
description: Use when building a new part, bracket, enclosure, plate or other feature-based CAD model in Python Forge through the Forge CAD MCP.
---

# Forge modeling

## Overview
Work the design out as parameters and expected geometry first. Then author the
maintained Python source in a few coherent stages, compile with Forge, replay in
SolidCraft and check the result against numbers and structure you expected
before looking at the final render. Do not explore the whole Forge API when an
exact reference or nearby example is enough.

Use `forge-checking` alongside this skill.

## Before the first edit
1. Call `environment`. Stop if `cad_ready` is false.
2. Call `workspace_status`. The reported target owner is authoritative.
3. Call `workspace_list` and read `model.yml` plus existing Python source
   when present. If the task is primarily a change to an existing model, switch
   to `forge-editing`.
4. Read this skill's `reference.md`. Then use
   `references/index.json` only to locate the exact Forge example or API
   symbol you need.
5. Write down:
   - driving dimensions and units;
   - origin/datum and intended anchors;
   - feature order;
   - reusable component boundaries;
   - expected body/component count;
   - expected bounding box and any volume or placement values you can compute.

## Author
- Python Forge source is the design. Generated command JSON and SolidCraft
  files are evidence/build artifacts; never patch them.
- Prefer explicit model fields for user-facing parameters. Keep derived values
  derived instead of copying numbers.
- Prefer a Forge feature, sketch pattern or body pattern when the design intent
  is a repeated feature. Do not duplicate source merely to make repeated
  geometry.
- Use anchors/attachments for semantic placement when the relationship should
  survive parameter changes. Use fixed `Placement` only when an absolute pose
  is the design intent.
- Keep reusable components separate from occurrences. For multi-owner work load
  `forge-assemblies`.
- Read an exact API signature with
  `skill_reference(..., "references/api/<Symbol or Symbol.method>.json")`
  before using an unfamiliar method. Never invent a convenience method.

## Iterate
1. Read the current source with `workspace_read` and keep its SHA-256.
2. Write one coherent source change with `workspace_write`; replacing an
   existing file must use that SHA-256.
3. Run `forge_compile`.
4. If compilation fails, fix the Python source. Do not edit the generated JSON.
5. Run `solidcraft_replay`.
6. Use `solidcraft_analyze` for compact geometry/history/component evidence.
7. Use `solidcraft_snapshot` only after numeric/structural checks, or earlier
   when the task itself is visual.

Avoid tiny edit/compile cycles when one coherent source edit can express the
whole stage.

## Verify
Follow `forge-checking`. At minimum:
- compile succeeds;
- replay succeeds;
- no unexpected body/component count appears;
- bounding box and important dimensions match the design calculation;
- the final image agrees with the intended shape.

A successful compiler or replay is not proof that a cut, attachment or pattern
landed where intended.

## Finish
Leave the maintained Python readable and parameterized. Report unsupported
features, assumptions and checks that could not be performed.

## Red flags
| Thought | Do instead |
| --- | --- |
| "Read all API docs first" | Read `reference.md`, one nearby example and exact API signatures. |
| "Compile succeeded, so the model is correct" | Run `forge-checking` against geometry/structure. |
| "The JSON is almost right; patch it" | Correct Python and compile again. |
| "Copy this component into the assembly" | Load `forge-assemblies` and reuse its owner read-only. |
| "The screenshot looks close enough" | Check the numeric/structural invariants first. |

## Target invariant
The configured target owner is the only writable owner. Never search the CAD
library for a different target and never switch target owners implicitly.
