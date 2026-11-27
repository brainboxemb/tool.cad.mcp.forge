# Forge modeling reference

This file is operational guidance for the MCP workflow. Exact API semantics
come from the configured Forge release.

## Minimal model shape

Forge v0.19 examples use a Python class with model fields and `build(self)`.
Numeric model fields become SolidCraft parameters.

```python
class SimpleBox:
    length = 40.0
    width = 30.0
    height = 10.0

    def build(self):
        return Box(self.length, self.width, self.height, anchor=Anchor.BOTTOM)

SimpleBox()
```

Read `references/examples/simple-box.py` for the release-matched source.

## Choose a datum deliberately

- `Anchor.BOTTOM` is useful when Z=0 should be the bottom datum.
- A centred body is useful when mirror/pattern symmetry is the intent.
- For an unfamiliar anchor or placement call, read the exact API signature.
- Do not turn a semantic attachment into XYZ arithmetic just because it is easy
  for one parameter value.

## Sketch + feature pattern

The verified `anchored-holes` example shows:
- an XY sketch;
- an extruded plate;
- a sketch on the plate top;
- a through cut;
- one feature repeated with `rectangular_pattern`.

Use:
- `references/examples/anchored-holes.py`
- `references/api/Sketch.json`
- `references/api/Shape.rectangular_pattern.json`

Do not repeat four equivalent holes as four unrelated source blocks when the
design intent is one patterned feature.

## Direct shapes and CSG

Use `simple-box` and `primitive-csg` as starting examples. Read exact
signatures for `Box`, `Cylinder`, `Hole` and the relevant `Shape`
method. Prefer the public Forge operation that preserves the intended editable
history.

## Nearby verified examples

| Intent | Example |
| --- | --- |
| smallest parameterized body | `simple-box` |
| face-relative holes + pattern | `anchored-holes` |
| direct CSG | `primitive-csg` |
| rectangular feature pattern | `rectangular-pattern` |
| sketch pattern + mirror | `sketch-pattern-mirror` |
| rotated sketch cutter | `rotated-sketch-cutter` |
| hole variants | `hole-family` |
| rounded sketch profile | `rounded-rectangle-sketch` |
| topology-driven edge selection | `topology-face-boundary-box` |

Read examples through
`skill_reference("forge-modeling", "references/examples/<id>.py")`.

## Efficient knowledge lookup

1. Read this file.
2. Read one nearby example.
3. Read one exact API symbol/member when needed.
4. Use `references/api.md` only when cross-object semantics remain unclear.

Do not dump every exported symbol or every example into context.

## MCP build path

```text
workspace_read
  -> workspace_write
  -> forge_compile
  -> solidcraft_replay
  -> solidcraft_analyze
  -> solidcraft_snapshot
```

`forge_compile` writes command JSON below the target's `build/`. That file
is generated evidence, not maintained source.
