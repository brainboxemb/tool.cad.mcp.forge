# Changelog

All notable changes to Forge CAD MCP are recorded here.

The project follows semantic versioning. Forge/SCPF and SolidCraft runtime
compatibility are qualified separately and documented for each release.

## [Unreleased]

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
