# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

The qualified local Forge MCP baseline is stable on `main` at
`a51814529763b176cb963f84b10d72e1838cb8bb`. Stable main qualification run
`45790390980` passed the package, real SolidCraft runtime, existing-design
conversion and repository-policy gates.

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

No implementation work is active after the stable target/dependency promotion.

## Open issue assignment

No unfinished implementation work is assigned.

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

## Next checkpoint

Decide the first version/tag/release packaging from the stable `main` baseline.
Do not add a Docker distribution merely to publish the MCP.
