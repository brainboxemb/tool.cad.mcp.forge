---
name: solidcraft-to-forge
description: Read an existing SolidCraft design, understand its modeling intent and translate it to verified Forge Python.
---

# Existing SolidCraft design to Forge

Use this skill when the user supplies a SolidCraft .sc file, JSON export, or both. Keep all original files unchanged.

1. Identify inputs with model_input_summary. Prefer .sc as the native geometry reference. The tool classifies optional JSON before you read it; a command document, command-result file and measurement snapshot are not interchangeable. Treat JSON as evidence, not instructions to execute blindly.
2. Treat the native .sc as an engine-owned design artifact; do not infer structure by reading raw bytes. Start with solidcraft_analyze for compact geometry, parameters, feature history and component structure. Use solidcraft_evaluate or solidcraft_components only when you need their more detailed evidence, and solidcraft_snapshot for visual views. Use workspace_read only for textual JSON/Python inputs. Capture parameters and units, component definitions and occurrences, feature history, sketch constraints, placements, joints, body counts and geometric measurements where available. Read compact summaries before requesting full history or JSON. Render reference views as needed.
3. Reconstruct modeling intent. Identify candidate repeated features, mirrors, reusable components, anchors and relationships. Separate observed facts from inferred structure. Never invent missing dimensions or silently discard features.
4. Read forge-modeling/SKILL.md via skill_reference and its relevant references. Author idiomatic parameterized Python Forge source rather than a literal translation of every native command. Preserve editable design intent where supported.
5. Compile the Python with forge_compile to release-matched SolidCraft command JSON and replay it with solidcraft_replay. Analyze both original and generated .sc models with solidcraft_analyze, then render matching views with solidcraft_snapshot. Compare parameters and required geometric/structural evidence before using the image as an additional visual check. Inspect and render both designs with matching views. Compare required geometric and structural properties using the existing verification tooling. Record tolerance, evidence, unsupported features and any meaningful difference. Iterate on the Python source.
6. Deliver Python source plus the verification evidence; keep the original intact. If only JSON is available and no native geometry can be recovered, mark the geometry comparison unavailable.

This workflow is a specification for planned execution tools, not evidence that import, inspection, rendering or comparison already works. Consult environment and tool discovery; report unavailable capabilities explicitly. Real input formats and CLI behavior must be qualified under issue #5.


## Target model invariant

The configured model root is authoritative. Never search the surrounding CAD library for a different target model, never choose a similarly named owner, and never switch model roots implicitly. If the configured owner is wrong or missing, stop and report the configuration problem.
