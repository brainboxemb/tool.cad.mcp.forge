# Forge sheet-metal reference

Use the release-matched example closest to the operation:

| Operation | Example |
| --- | --- |
| flat sheet + fold | `sheet-fold` |
| edge flange | `sheet-edge-flange` |
| contour flange | `sheet-contour-flange` |
| hem | `sheet-hem` |
| path flange | `sheet-path-flange` |
| whole-sheet perforation | `sheet-perforate` |

The verified examples keep `thickness`, `bend_radius` and `k_factor` as
model parameters and pass them into the sheet rule.

## Flat sheet

The v0.19 examples create a closed sketch and call:

```python
sheet = blank.sheet_metal(
    thickness=self.thickness,
    bend_radius=self.bend_radius,
    k_factor=self.k_factor,
    rule_name="...",
)
```

Read the exact `Sketch.sheet_metal` signature before changing options.

## Fold

`sheet-fold` creates a straight sketch line and calls `sheet.fold` with the
line, angle and fixed-side point.

## Edge flange

`sheet-edge-flange` calls `sheet.flange` with an edge pick, height and
angle.

## Contour/path flange

Use the corresponding release example. These use finished open sketch chains;
do not infer the chain API from a different sketch feature.

## Hem/perforate

Use `sheet-hem` and `sheet-perforate` respectively. Do not emulate a
perforation field with hundreds of independent hole cuts when the sheet
operation represents the intent.

## Checking limit

3D replay/analyze/snapshot is available. Dedicated flat-pattern and bend-table
inspection is not currently exposed by Forge CAD MCP.
