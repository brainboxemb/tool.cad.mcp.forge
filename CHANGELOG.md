# Changelog

All notable changes to Forge CAD MCP are recorded here.

The project follows semantic versioning. Forge/SCPF and SolidCraft runtime
compatibility are qualified separately and documented for each release.

## [Unreleased]

## [0.0.4] - 2026-11-27

### Changed

- Move the exact SolidCraft baseline from 0.49.0 to current stable 0.50.0.
- Qualify replay, native evaluation/component inspection, PNG rendering and
  existing-design conversion against immutable CAD runtime v0.3.8.
- Keep Forge/SCPF pinned to v0.25.0 and preserve the v0.0.3 live SolidCraft
  control/tool/skill surface.

### Compatibility

- Forge/SCPF 0.25.0.
- SolidCraft 0.50.0 through `ghcr.io/brainboxemb/cad-solidcraft:v0.3.8`
  and the authenticated local GUI control channel.
- Python 3.11+.

## [0.0.3] - 2026-11-27

### Added

- Add authenticated live SolidCraft GUI control for trusted local stdio
  workbenches: create a new active design, compile/apply Forge source, execute
  native SolidCraft engine commands, inspect the active document and return a
  current-camera model render through MCP.
- Add the `solidcraft-control` skill and teach `forge-modeling` to use the
  live GUI path for interactive iteration while retaining headless evidence.
- Add optional local `project.yml` workbench configuration plus bounded
  `build/session.jsonl` action/evidence logging with render/replay hashes.

### Compatibility

- Forge/SCPF 0.25.0.
- SolidCraft 0.49.0 through the qualified CAD runtime image and authenticated
  local GUI control channel.
- Python 3.11+.

## [0.0.2] - 2026-11-27

### Changed

- Move the qualified Forge/SCPF baseline from 0.19.0 to the active CAD
  development release v0.25.0.
- Validate the local Forge source checkout against the immutable v0.25.0 tag
  instead of embedding its commit SHA in MCP source.
- Run package, real SolidCraft runtime and existing-design conversion
  acceptance against the same tagged Forge release.

### Compatibility

- Forge/SCPF 0.25.0.
- SolidCraft 0.49.0 through the qualified CAD runtime image.
- Python 3.11+.

## [0.0.1] - 2026-11-27

### Added

- First qualified local Forge CAD MCP baseline using FastMCP 2.14.7 and stdio
  as the normal local assistant transport.
- Skills-first Forge authoring and SolidCraft-to-Forge conversion workflows.
- Bounded model-owner source access, Forge compilation, SolidCraft replay,
  analysis, component inspection and PNG rendering.
- Explicit CAD-library/model-owner binding with read-only access to exact
  dependency owners.
- Local doctor/environment readiness checks and repository merge/cleanup
  governance.

### Compatibility

- Forge/SCPF 0.19.0.
- SolidCraft 0.49.0 through the qualified CAD runtime image.
- Python 3.11+.
