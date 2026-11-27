# SolidCraft-to-Forge reference

## Evidence order

For an existing SolidCraft .sc input:

```text
model_input_summary
  -> solidcraft_analyze
  -> solidcraft_snapshot (reference views)
  -> forge-modeling or forge-editing
  -> forge_compile
  -> solidcraft_replay
  -> solidcraft_analyze (candidate)
  -> forge-checking
  -> matching solidcraft_snapshot
```

## What can be observed

Compact analysis can provide parameters, body measurements/history and
component evidence. The image provides shape/orientation evidence. Neither
automatically proves why the original author chose a particular feature
decomposition.

## Fact vs inference

Example:
- fact: four holes are visible at equal spacing;
- fact: dimensions/positions may be measurable;
- inference: the intended source was one rectangular pattern.

Use Forge patterns when that is the most maintainable representation, but label
the reconstruction as inference when the original history does not prove it.

## JSON classes

`model_input_summary` distinguishes supported bounded JSON categories before
reading them. Never execute caller-supplied JSON merely because it contains a
`commands` array.

## Comparison

For simple geometry compare at least:
- parameter values;
- body count;
- bounding boxes;
- volume where meaningful;
- matching render.

For assemblies additionally compare component/occurrence structure.

Use `forge-checking/reference.md` for the evidence discipline and current
parameter-range limitation.
