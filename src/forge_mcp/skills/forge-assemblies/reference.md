# Forge assemblies reference

## Verified v0.19 patterns

### Reuse another occurrence
`references/examples/components.py` shows:
- one component definition;
- another occurrence via `copy(placement=Placement(...))`.

Use exact references:
- `references/api/Placement.json`
- `references/api/Shape.copy.json` when exported on the release API.

### Associative attachment
`references/examples/parametric-attach.py` uses `attach` with parent and
child anchors plus a parameterized gap.

`references/examples/corner-anchor.py` shows corner-to-corner attachment.

### Assembly-owned datum
`references/examples/assembly-owned-anchor.py` shows a named datum on a
finished assembly with `with_anchor`, then reuses that datum for another
attachment.

### As-built relationship
`references/examples/as-built-attach.py` preserves an already declared child
pose while adding an attachment relationship.

### Revolute relationship
`references/examples/revolute-joint.py` shows `@component`, `@assembly`,
`AnchorFrame` and a bounded revolute attachment. Use this example only when
the user actually wants a moving relationship.

## Dependency boundary

Target:
```text
models/assemblies/my_assembly/      read + write
```

Dependencies:
```text
models/components/part_a/           read-only
models/subassemblies/frame/         read-only
```

Use:
```text
catalog_dependency_list(owner)
catalog_dependency_read(owner, path)
```

Both calls require the exact owner. They deliberately do not provide fuzzy
catalog search.

## Structural verification

Use `solidcraft_components` when the key question is whether reusable
definitions/occurrences survived compilation. Use a snapshot for pose and
orientation. Use both when correctness depends on both.
