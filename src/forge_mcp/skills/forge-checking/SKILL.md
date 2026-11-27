---
name: forge-checking
description: Use alongside Forge modeling, editing, assemblies, sheet metal or SolidCraft-to-Forge work to prove that the generated CAD result matches the intended geometry and structure.
---

# Forge checking

## Overview
A Forge source file is not accepted because Python compiled or SolidCraft
replayed it. Check the generated design against invariants derived from the
request and the source. Use compact evidence first and images as additional
evidence.

## Define the checks first
Before the final build, state the invariants that matter:
- expected parameters;
- body count;
- component/occurrence count for assemblies;
- bounding box or key extents;
- volume when it can be calculated usefully;
- expected feature/history presence;
- expected visual orientation or placement.

For a port/conversion, derive these from the original design evidence. For a new
simple part, calculate them from the dimensions when practical.

## Evidence ladder
1. `forge_compile`: source and Forge API are valid.
2. `solidcraft_replay`: generated commands create a SolidCraft design.
3. `solidcraft_analyze`: parameters, body bounds, volume/history and compact
   component evidence.
4. `solidcraft_components`: use when assembly structure needs more detail.
5. `solidcraft_snapshot`: visual evidence from a deliberate matching view.

Use the cheapest evidence that answers the question. Do not request full
measurement payloads unless compact analysis lacks a needed value.

## Compare
- Compare actual parameter values with the requested values.
- Compare body bounds with dimensions you computed.
- Compare volume when a missed cut/join could otherwise look plausible.
- For assemblies, compare occurrence/component structure and then placement in
  a matching image.
- For an existing-design conversion, analyze both original and candidate and
  render the same view.

## Parameter coverage
The current MCP baseline can inspect the resulting parameters but does not
expose a general parameter-variant runner. Do not claim that a parameter range
or every configuration has been tested from a single default build. Report that
gap when range/configuration coverage is required; use the repository's normal
CI/verification workflow where that coverage already exists.

## Failure rules
- Compiler success alone is insufficient.
- Replay success alone is insufficient.
- A visually plausible screenshot is insufficient when numeric evidence exists.
- If a requested property cannot currently be inspected, say so instead of
  inferring it from unrelated evidence.

## Finish
Report the concrete checks that passed, any tolerance used, and every required
check that remained unavailable.
