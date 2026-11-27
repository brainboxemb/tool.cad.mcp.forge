# Forge editing reference

## Baseline first

For an existing target, capture:
- source SHA-256;
- compile/replay success;
- parameters and body bounds from `solidcraft_analyze`;
- component/occurrence structure when relevant;
- one matching render view for visual work.

This lets the agent prove the requested delta instead of merely producing a
different model.

## Source ownership

The target owner is writable. Imported CAD-library owners are read-only. When
source contains an import such as:

```python
from models.components.some_part.scpf.model import SomePart
```

inspect that exact dependency through the catalog dependency tools. Do not
enumerate sibling owners to guess what the user meant.

## Existing constructs

Use exact release references before changing unfamiliar code:
- model fields and shapes: `references/api/<Symbol>.json`;
- feature method: `references/api/Shape.<method>.json`;
- nearby implementation: `references/examples/<id>.py`.

Useful examples include `anchored-holes`, `parametric-attach`,
`corner-anchor`, `assembly-owned-anchor` and the sheet-metal examples.

## Failed compile

A failed `forge_compile` is source-level evidence. Fix the source named by the
diagnostic. Do not:
- edit `build/solidcraft.json`;
- weaken the model merely to make it compile;
- replace an unknown Forge call with guessed syntax.

## Visual comparison

Use the same camera/view for before/after snapshots. Visual evidence is useful
for placement, silhouette and orientation; it does not replace checks of
parameters, body bounds, volume or component structure.
