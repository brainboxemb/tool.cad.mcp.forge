# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

The qualified local Forge MCP baseline is released as `v0.0.1` from stable
`main` commit `5db8d61e292683a6e5aa1f6758a201663bb447fc`. Stable main
qualification run `46029948156` passed the package, real SolidCraft runtime,
existing-design conversion and repository-policy gates.

The stable baseline includes:

- FastMCP 2.14.7 with stdio as the normal local client transport;
- Forge/SCPF 0.19.0 at the exact supported release checkout;
- SolidCraft 0.49.0, accepted through
  `ghcr.io/brainboxemb/cad-solidcraft:v0.3.6`;
- skills-first authoring through `forge-modeling` and
  `solidcraft-to-forge`;
- a three-checkout local setup: Forge MCP, exact Forge release and CAD library;
- one explicit target owner inside the CAD library as the only writable
  workspace/build/runtime scope;
- exact read-only dependency-owner access for assemblies/subassemblies;
- Forge compilation with the configured CAD-library root available for existing
  `from models...` imports;
- Forge Python -> SolidCraft command JSON compilation;
- SolidCraft replay, compact native analysis, component inspection and PNG
  rendering through MCP;
- independent existing-SolidCraft -> Forge workflow acceptance;
- explicit local startup arguments and a non-CAD `doctor` readiness gate;
- a Windows + VS Code + Conda setup guide matching the stable configuration.

Local model iteration is independent of GitHub after setup. No MCP-specific
Docker image is required.

## Lane rule

Issue branches target `dev`. Stable product promotion is explicit
`dev -> main`. Use the shared `/merge` policy for every integration.

## Engineering constraints

Follow the shared principles in
`brainboxemb/meta.cad.solidcraft/docs/engineering-principles.md`.

Generated Python and SolidCraft execution remain local-stdio-only. Streamable
HTTP stays a loopback/read-only development transport until authentication,
isolated workspaces and sandboxed execution exist.

The configured target owner is authoritative. AI workflows must not discover or
switch target owners implicitly. Catalog dependency access is exact-path and
read-only; it exists only to support reuse by assemblies/subassemblies.

## Active workstreams

### WS1 — Forge v0.25.0 compatibility

Issue #49 moves the version-matched MCP baseline to the same Forge release used
by the active CAD development catalog. CI and local knowledge use the immutable
`v0.25.0` tag rather than embedding its commit SHA. Existing runtime,
conversion and repository-policy acceptance remain mandatory.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #49 | MCP `dev` | now | Qualify Forge `v0.25.0`, promote the accepted checkpoint, then publish MCP `v0.0.2` |

## Recently completed

- #1 protocol/repository bootstrap and merge/cleanup policy.
- #3 skills-first, version-matched Forge knowledge.
- #6 bounded local workspace/source editing.
- #8 Forge Python compilation.
- #9 real SolidCraft replay/eval/component inspection/PNG rendering.
- #5 independent existing SolidCraft design analysis and Forge translation
  acceptance.
- #13 explicit local-client startup, doctor readiness and qualified FastMCP
  pin.
- #16 first qualified `dev -> main` product promotion.
- #21 one-time bootstrap CI alignment required to remove the initial
  add/add workflow conflict before #16.
- #25 Windows VS Code + Conda local setup guide.
- #26 explicit writable target owner plus read-only CAD-library dependency
  access.
- #35 qualified stable promotion of the target/dependency baseline.
- #43 initial governed release adapter; superseded by #45 before stable promotion
  because publication ownership must remain repository-local.
- #45 repository-local release capability under `modules/release`.
- #48 published and verified the first MCP release, `v0.0.1`.

## Next checkpoint

Complete #49 against Forge `v0.25.0`, then publish MCP `v0.0.2` through
the repository-local release workflow. After that, update the workspace
dependency contract to MCP `v0.0.2` plus Forge `v0.25.0` release tags.

Do not add a Docker distribution merely to publish the MCP.
