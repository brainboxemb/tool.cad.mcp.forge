---
name: forge-assemblies
description: Use when composing Forge components, occurrences, attachments, subassemblies or assembly relationships across CAD-library owners.
---

# Forge assemblies

## Overview
Treat an assembly as one writable target owner that composes reusable,
read-only dependency owners. Plan component ownership and attachment semantics
before writing placement code. Reuse component definitions; do not copy their
implementation into the assembly.

Use `forge-checking` alongside this skill.

## Before the first edit
1. Call `environment` and `workspace_status`; confirm the exact assembly or
   subassembly target.
2. Read target `model.yml` and source.
3. Read each dependency only when its exact owner is named by an import, target
   metadata or the user. Use `catalog_dependency_list` then
   `catalog_dependency_read`.
4. Read this skill's `reference.md` and one release-matched assembly example.
5. Plan:
   - component definitions and their owners;
   - occurrence count;
   - which occurrence is the placement reference;
   - semantic anchors/attachment frames;
   - fixed placements that are truly absolute;
   - expected component/occurrence structure after replay.

## Build
- Import reusable models from their existing `models...` owner.
- Use `copy(placement=Placement(...))` for another occurrence of the same
  definition when absolute placement is intentional.
- Use `attach(...)` when the relationship should remain associated with
  anchors or parameter changes.
- Use component-owned anchors for reusable datums. Use assembly-owned anchors
  when the datum only makes sense in the composed assembly.
- Keep the assembly target as the only writable owner.
- Do not create an MCP-side component loader; Forge's model import context
  resolves the catalog's existing `from models...` imports.

## Verify
1. `forge_compile` and `solidcraft_replay`.
2. `solidcraft_analyze`.
3. Use `solidcraft_components` when you need explicit component/occurrence
   structure.
4. `solidcraft_snapshot` from a view that makes placement mistakes visible.
5. Apply `forge-checking`.

Verify both structure and geometry. Two bodies in the correct visual position
are not necessarily two reusable component occurrences.

## Red flags
| Thought | Do instead |
| --- | --- |
| "Copy the component source here" | Import its existing owner. |
| "Search the catalog for a similar part" | Use only an exact owner already named by source/metadata/user. |
| "XYZ placement is simpler" | Use an attachment when the relationship is semantic/associative. |
| "The render shows both parts" | Inspect components/occurrences too. |
