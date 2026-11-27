# Forge checking reference

## Compact checks

`solidcraft_analyze` is the default evidence call. It combines compact
measurement/history data with component evidence. Use `solidcraft_evaluate`
or `solidcraft_components` only when their more detailed result is needed.

Typical invariants:

| Design | Useful checks |
| --- | --- |
| simple solid | parameters, body count, bbox, volume |
| cut/hole model | bbox unchanged where expected, volume reduced, feature/history present |
| pattern | expected count/extent plus visual spacing |
| assembly | component/occurrence names/counts, placements, render |
| conversion | original vs candidate parameters, bbox, volume, structure, matching view |

## Screenshot discipline

A snapshot is especially useful for:
- left/right or front/back orientation;
- spacing of symmetric features;
- assembly placement;
- silhouette/radii that compact measurements do not identify.

Use the same camera for comparisons. Do not use a screenshot to estimate an
exact dimension that analysis already exposes numerically.

## Tolerances

Do not invent a universal tolerance. Use exact requested values where the
engine reports them exactly; otherwise state the tolerance chosen for the
specific comparison and why.

## Current limitation

The MCP does not yet expose a general parameter/configuration variant executor.
A default model that passes checking proves the default state only. It does not
prove all allowed parameter values.
