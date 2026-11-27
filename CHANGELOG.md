# Changelog

All notable changes to Forge CAD MCP are recorded here.

The project follows semantic versioning. Forge/SCPF and SolidCraft runtime
compatibility are qualified separately and documented for each release.

## [Unreleased]

## [0.0.9] - 2026-11-27

### Fixed

- Isolate Forge compiler subprocess stdin from the MCP stdio protocol stream so
  real Windows `forge_compile` / `forge_live` calls cannot inherit the server's
  protocol input handle and stall until the bounded compile timeout.
- Add released-Forge regression coverage for the 60 × 20 × 4 mm plate with a
  centered Ø8 through-hole authoring path.

### Compatibility

- Forge/SCPF 0.25.0.
- SolidCraft 0.50.0 through `ghcr.io/brainboxemb/cad-solidcraft:v0.3.8`
  and the authenticated local GUI control channel.
- Python 3.11+.

## [0.0.8] - 2026-11-27

### Changed

- Keep `forge-modeling` focused on the maintained `scpf/model.py` authoring
  contract plus a small set of generic Forge idioms, rather than prescribing
  geometry recipes for individual models.
- Clarify `Anchor`, `Faces`, explicit `Sketch` and version-matched
  `skill_reference` usage for new-model agents.
- Correct the native `Hole` example: add the hole feature to design history
  with `+`; the feature itself removes material.

### Compatibility

- Forge/SCPF 0.25.0.
- SolidCraft 0.50.0 through `ghcr.io/brainboxemb/cad-solidcraft:v0.3.8`
  and the authenticated local GUI control channel.
- Python 3.11+.

## [0.0.7] - 2026-11-27

### Changed

- Make `forge-modeling` the explicit new-model skill for starting a
  maintainable `scpf/model.py`.
- Document the root model contract, parameter naming rules and the
  `build()` / explicit root-instance pattern.
- Add qualified worked examples for a basic plate and a centred through-hole.
- Compile the Python examples from the bundled skill in package CI so skill
  examples cannot silently drift from Forge/SCPF 0.25.0.

### Compatibility

- Forge/SCPF 0.25.0.
- SolidCraft 0.50.0 through `ghcr.io/brainboxemb/cad-solidcraft:v0.3.8`
  and the authenticated local GUI control channel.
- Python 3.11+.

## [0.0.6] - 2026-11-27

### Changed

- Remove per-call Forge Git validation from knowledge/reference reads and
  `forge_compile`.
- Keep exact Forge tag and clean-checkout qualification in the explicit
  operator `doctor` gate.
- Add regression coverage proving parallel skill-reference reads and compile
  do not invoke Git validation.

### Compatibility

- Forge/SCPF 0.25.0.
- SolidCraft 0.50.0 through `ghcr.io/brainboxemb/cad-solidcraft:v0.3.8`
  and the authenticated local GUI control channel.
- Python 3.11+.

## [0.0.5] - 2026-11-27

### Changed

- Make the MCP `environment` status call subprocess-free so initial client
  readiness checks no longer run Git validation or `solidcraft-cli --version`.
- Keep exact Forge checkout and SolidCraft version qualification in the
  explicit operator `doctor` gate.
- Advertise genuinely read-only status, knowledge and workspace inspection
  tools with MCP `readOnlyHint` metadata.

### Compatibility

- Forge/SCPF 0.25.0.
- SolidCraft 0.50.0 through `ghcr.io/brainboxemb/cad-solidcraft:v0.3.8`
  and the authenticated local GUI control channel.
- Python 3.11+.

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
