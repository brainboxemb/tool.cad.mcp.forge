# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

The first usable local Forge MCP baseline is stable on `main` at
`80e03b6395f53cfe7c69f08c56612b9914e29536`. Stable qualification run
`45781197700` passed the package, real SolidCraft runtime, existing-design
conversion and repository-policy gates.

The stable baseline includes:

- FastMCP 2.14.7 with stdio as the normal local client transport;
- Forge/SCPF 0.19.0 at the exact supported release checkout;
- SolidCraft 0.49.0, accepted through
  `ghcr.io/brainboxemb/cad-solidcraft:v0.3.6`;
- skills-first authoring through `forge-modeling` and
  `solidcraft-to-forge`;
- bounded local workspace reads/source writes;
- Forge Python -> SolidCraft command JSON compilation;
- SolidCraft replay, compact native analysis, component inspection and PNG
  rendering through MCP;
- independent existing-SolidCraft -> Forge workflow acceptance;
- explicit local startup arguments and a non-CAD `doctor` readiness gate.

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

## Active workstreams

### WS1 — stable promotion of explicit target/dependency binding

The qualified dev baseline now binds one exact writable target owner inside one
configured CAD-library checkout. Assemblies and subassemblies may inspect exact
dependency owners elsewhere in that same catalog read-only, and Forge
compilation resolves existing `from models...` imports against the catalog
root. AI workflows may not discover or switch target models implicitly. The
Windows VS Code + Conda guide uses the same three-checkout setup.

## Open issue assignment

No unfinished implementation work is assigned before the next checkpoint.

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
- #26 explicit writable target owner plus read-only CAD-library dependency access.

## Next checkpoint

Open a clean qualified `dev -> main` promotion with no source changes. After
that stable promotion, decide the first version/tag/release packaging from the
new `main` baseline. Do not add a Docker distribution merely to publish the MCP.
