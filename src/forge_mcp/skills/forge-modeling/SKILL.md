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
5. Write Python with workspace_write. Compile it with forge_compile, which writes SolidCraft command JSON below build/ without starting SolidCraft. Replay generated JSON with solidcraft_replay, inspect geometry/parameters/history with solidcraft_evaluate, and request matching visual views with solidcraft_snapshot. Use both numeric and visual evidence before claiming success. Use numeric evidence in addition to images. Correct the Python source rather than patching generated artifacts.
6. State missing inputs, unsupported features and failed checks; never claim successful CAD verification from source inspection alone.

Knowledge, workspace editing and Forge compilation are separate capabilities. forge_compile executes the trusted local Python model and is available only on the local stdio server. SolidCraft replay, evaluation and snapshot rendering are available on the trusted local stdio server. Check environment and tool discovery before attempting unavailable tools. If converting a native design, start with solidcraft-to-forge.


## Target owner and dependency owners

The configured target owner is authoritative for edits and build outputs. Never
search the surrounding catalog for a new target, choose a similarly named
owner, or switch owners implicitly.

Assemblies and subassemblies may reuse components from other owners in the same
CAD library. When the target source contains an explicit import such as
`models.components.simple_mft...`, use `library_read_owner` or
`library_list_owner` with that exact owner path to inspect the dependency.
Those library tools are read-only. Do not modify a dependency owner unless the
user starts a session with that owner as the configured target.
