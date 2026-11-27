# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

The qualified local Forge MCP baseline is released as `v0.0.2` from stable
`main` commit `3d09d3f2b0b6ff4aab832a56a827b31513753b99`. Release workflow
run `46032398960` succeeded after stable main qualification.

The stable baseline includes:

- FastMCP 2.14.7 with stdio as the normal local client transport;
- Forge/SCPF 0.25.0 at the exact supported release checkout;
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

### WS1 — live SolidCraft workbench control

The next MCP capability extends the trusted local stdio workflow from
headless/file-oriented SolidCraft evidence to deliberate control of the running
SolidCraft GUI through Forge's existing authenticated `scpf.live` control
client. The MCP must keep Forge authoring and SolidCraft control distinct while
letting one workbench session compile/apply Forge source, inspect the active
design, run native SolidCraft commands, change parameters/views and capture
live evidence.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #56 | MCP `dev` | now | Add bounded live SolidCraft GUI tools, session evidence logging and the SolidCraft-control skill |

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
- #49 qualified Forge/SCPF `v0.25.0`, promoted it to stable `main`, and
  published MCP `v0.0.2`.

## Next checkpoint

Add and qualify live SolidCraft workbench control against the existing
Forge/SCPF `v0.25.0` + SolidCraft `0.49.0` baseline, then publish the next
MCP release and update the workspace template/consumer pins. The first operator
demo is a standalone local workbench, not a catalog model.

Do not add a Docker distribution merely to publish the MCP.
