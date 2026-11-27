---
name: forge-editing
description: Use when changing, fixing or extending an existing Python Forge model in the configured target owner.
---

# Forge editing

## Overview
Map the existing source and establish a geometry baseline before changing it.
Prefer the smallest source change that preserves the model's existing
parameters, component boundaries and design intent. Do not rebuild a working
model from scratch merely because a different implementation would be easier.

Use `forge-checking` alongside this skill.

## Map the target
1. Call `environment` and `workspace_status`.
2. Call `workspace_list`; read `model.yml` and the Python source with
   `workspace_read`.
3. Follow imports. For an exact component owner already named by the source or
   user, use `catalog_dependency_list` and `catalog_dependency_read`.
   Dependencies are read-only.
4. Read `reference.md` and exact Forge API references for the source constructs
   you are about to change.
5. Establish a baseline with `forge_compile`, `solidcraft_replay`,
   `solidcraft_analyze` and, when useful, `solidcraft_snapshot`.

If the baseline itself fails, separate the existing failure from the requested
change before editing.

## Change
- Change maintained Python only.
- Preserve existing parameter names unless the requested design change requires
  a public parameter change.
- Preserve reusable component ownership. Do not copy dependency source into the
  target to make an edit possible.
- Keep patterns/mirrors/attachments as relationships when they already express
  the design intent.
- Use the SHA-256 from `workspace_read` in `workspace_write`.
- Make one coherent edit, then compile. Do not issue a stream of one-line edits
  unless a failure has isolated one specific line.

If the requested fix actually belongs in a dependency owner, stop and report
that ownership boundary instead of editing the dependency through this target.

## Verify the delta
Run `forge-checking` with both the baseline and the changed result in mind.
Check:
- intended dimensions changed by the expected amount;
- unrelated body/component counts stayed stable;
- the same render view shows only the intended visible change;
- compilation/replay introduced no new errors.

## Red flags
| Thought | Do instead |
| --- | --- |
| "Rewrite the whole file cleanly" | Preserve the working structure and make the smallest coherent change. |
| "Change the imported component here" | Report the dependency owner; it is read-only. |
| "A compile failure means the API is broken" | Read the exact release signature/example first. |
| "The picture improved" | Compare baseline and changed geometry evidence too. |
