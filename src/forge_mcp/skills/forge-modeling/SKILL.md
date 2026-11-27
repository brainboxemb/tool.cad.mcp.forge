---
name: forge-modeling
description: Author, edit and verify maintainable Python Forge CAD models.
---

# Forge modeling

Use this skill when creating or changing a Python Forge model. The Python source is the maintained design, not native command JSON. The Forge release supplies the API semantics and examples; SolidCraft evaluates the actual geometry.

1. Determine dimensions, reference planes, units, physical components and required output. Read existing project instructions and models before changing them.
2. Read references/cheatsheet.yml and the relevant guide from references/index.json. Read references/api.md for cross-object semantics. For an exact signature or public method read references/api/<Symbol or Symbol.method>.json.
3. Select a nearby example from references/index.json, then read its Python source with skill_reference. Prefer named parameters and native supported features; use patterns and mirrors only when they match the intended geometry.
4. Keep component definitions separate from occurrences; use Forge's documented positioning, support and attachment semantics. Do not invent API methods.
5. Write Python with workspace_write. For interactive local work, read the solidcraft-control skill and use forge_live to compile/apply the maintained Forge source to the running SolidCraft GUI. Inspect the active design, set useful views and retrieve live image evidence there. Use forge_compile + solidcraft_replay/evaluate/snapshot when independent saved/headless evidence is required. Correct the Python source rather than leaving accidental GUI-only geometry edits as design intent.
6. Use both numeric/structural and visual evidence before claiming success. State missing inputs, unsupported features and failed checks; never claim successful CAD verification from source inspection or an image alone.

Knowledge, workspace editing, Forge compilation and live SolidCraft control are separate capabilities. forge_compile and forge_live execute the trusted local Python model and are available only on the local stdio server. Live SolidCraft control requires the running desktop app with its authenticated local control channel enabled. Headless replay, evaluation and snapshot rendering remain available for saved-design evidence. Check environment and tool discovery before attempting unavailable tools. If converting a native design, start with solidcraft-to-forge.


## Target model invariant

The configured model root is the authoritative target and the only writable owner. Never search the surrounding CAD library for a different target model, never choose a similarly named owner, and never switch model roots implicitly. If the configured owner is wrong or missing, stop and report the configuration problem.

Assemblies and subassemblies may depend on other owners in the same configured CAD library. Use `catalog_dependency_list(owner)` and `catalog_dependency_read(owner, path)` only for an exact dependency owner/path already named by the target source, metadata, imports or the user. Dependency access is read-only and must never be used to replace target selection. Forge's own model import context resolves existing `from models...` imports from target source below the catalog `models/` tree; do not invent a second component loader in MCP.
