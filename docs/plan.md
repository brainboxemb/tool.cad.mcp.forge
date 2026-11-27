# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

The qualified local Forge MCP baseline is released as `v0.0.3` from stable
`main`. It includes authenticated live SolidCraft GUI/workbench control.

The stable baseline includes:

- FastMCP 2.14.7 with stdio as the normal local client transport;
- Forge/SCPF 0.25.0 at the exact supported release checkout;
- SolidCraft 0.49.0 through the then-qualified CAD runtime;
- skills-first authoring through `forge-modeling`, `solidcraft-control` and
  `solidcraft-to-forge`;
- standalone workbench and exact catalog-owner bindings;
- Forge compile plus live SolidCraft apply/inspect/native command/view/render;
- headless SolidCraft replay, evaluation, component inspection and PNG
  evidence;
- bounded `project.yml` workbench configuration and JSONL live-session
  evidence;
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

The configured target owner is authoritative. AI workflows must not discover or
switch target owners implicitly. Catalog dependency access is exact-path and
read-only; it exists only to support reuse by assemblies/subassemblies.

## Active workstreams

### WS1 — SolidCraft 0.50 runtime adoption

Issue #62 moves the exact SolidCraft baseline to released runtime v0.3.8 /
SolidCraft 0.50.0 while keeping Forge/SCPF v0.25.0 and the v0.0.3 live-control
surface unchanged. The Windows workbench acceptance is currently blocked only
by MCP v0.0.3 still requiring SolidCraft 0.49.0.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #62 | MCP `dev` | now | Qualify SolidCraft 0.50.0 / runtime v0.3.8 and publish MCP v0.0.4 |

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
- #56 added bounded live SolidCraft GUI control, workbench evidence logging and
  the `solidcraft-control` skill; it was released as MCP `v0.0.3`.
- #63 synchronized the stable v0.0.3 release metadata back to permanent
  `dev` without copying the promotion merge commit.

## Next checkpoint

Qualify issue #62 against released CAD runtime `v0.3.8`, promote it to stable
`main`, publish MCP `v0.0.4`, and update the workspace template/concrete
workspace pins. Then rerun the real Windows standalone-workbench doctor and
60 × 20 × 4 mm / Ø8 live SolidCraft demo.

Do not weaken the exact-version doctor check and do not require the user to
downgrade SolidCraft.

