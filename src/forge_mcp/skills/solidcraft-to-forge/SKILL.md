---
name: solidcraft-to-forge
description: Use when translating an existing SolidCraft .sc design or supported SolidCraft evidence into maintainable, checked Python Forge source.
---

# Existing SolidCraft design to Forge

## Overview
Treat the SolidCraft design as evidence of geometry and structure, not as a
command stream to copy line-for-line. Observe the source design, reconstruct
its modeling intent, author idiomatic Forge Python and prove the candidate
against the original. Preserve the original unchanged.

Load `forge-modeling` for new target source, `forge-editing` when target
Forge source already exists, and always use `forge-checking`.

## Understand the input
1. Call `environment` and `workspace_status`.
2. Classify the supplied input with `model_input_summary`.
3. For an .sc design, start with `solidcraft_analyze` and render deliberate
   reference views with `solidcraft_snapshot`.
4. Use `solidcraft_evaluate` or `solidcraft_components` only when compact
   analysis does not contain a required detail.
5. JSON is evidence only after its schema is identified. A command document,
   measurement result and command-result envelope are not interchangeable.

Capture:
- parameters and units;
- body/component/occurrence structure;
- feature/history evidence;
- bounding boxes and useful volumes;
- visible placement/orientation;
- uncertainty where SolidCraft evidence does not expose original design intent.

## Reconstruct intent
Identify which observed geometry should become:
- one parameterized component;
- a sketch/feature;
- a pattern/mirror;
- a reusable dependency;
- an attachment or occurrence placement.

Separate observed fact from inference. Never invent an unobserved dimension just
to make Forge source compile.

## Author
Read the appropriate Forge skill and exact release references. Write
maintainable Python rather than reproducing every SolidCraft command. Keep
original files unchanged and edit only target Python source.

## Compare
1. Compile/replay the Forge candidate.
2. Analyze original and candidate.
3. Compare the invariants defined in `forge-checking`.
4. Render matching views.
5. Iterate on Python until required differences are resolved or explicitly
   documented.

If only JSON is available and no SolidCraft geometry can be recovered, state
that a geometric comparison is unavailable.

## Red flags
| Thought | Do instead |
| --- | --- |
| "Translate every SolidCraft command" | Reconstruct the higher-level Forge design intent. |
| "The screenshot is close" | Compare original/candidate numeric and structural evidence. |
| "This missing dimension is probably 20 mm" | Mark it unknown; do not invent it. |
| "Modify the original to make comparison easier" | Preserve the original unchanged. |
