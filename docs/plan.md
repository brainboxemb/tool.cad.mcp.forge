# Forge MCP plan

This file is the current source of truth for unfinished work in
`brainboxemb/tool.cad.mcp.forge`.

The repository exposes version-matched Forge authoring knowledge and bounded
local Forge/SolidCraft execution through MCP. Forge owns compilation;
SolidCraft owns CAD execution; existing CAD verification remains the acceptance
owner for CAD behavior.

## Current accepted baseline

The qualified local Forge MCP baseline is released as `v0.0.4` from stable
`main` commit `2502eb7878b030460e5fbbcfca286e3794861960`.

The accepted stack is:

- FastMCP 2.14.7 with stdio as the normal local client transport;
- Forge/SCPF 0.25.0 from the exact supported release checkout;
- SolidCraft 0.50.0 through CAD runtime v0.3.8;
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

`main` is the only permanent source/product lane.

Each logical change uses one temporary issue/fix/feature/docs/chore branch and
one PR directly to `main`. Release metadata may use a temporary `release/*`
branch to `main`. All accepted integrations use `/merge` and require the
central PR CI check. Temporary branches are removed after merge.

There is no permanent `dev` or `exp` integration lane.

## Engineering constraints

Follow the shared principles in
`brainboxemb/meta.cad.solidcraft/docs/engineering-principles.md`.

Generated Python and SolidCraft execution remain local-stdio-only. Streamable
HTTP stays a loopback/read-only development transport until authentication,
isolated workspaces and sandboxed execution exist.

The configured target owner is authoritative. AI workflows must not discover or
switch target owners implicitly. Catalog dependency access is exact-path and
read-only; it exists only to support reuse by assemblies/subassemblies.

Development-cycle cost is architectural. Normal PRs use one CI path.
Documentation/repository-policy-only PRs do not start SolidCraft; runtime-
sensitive PRs use at most one released CAD runtime container. Ordinary
`main` pushes run fast CI only. Complete released-stack acceptance belongs to
runtime-sensitive PRs, explicit manual `full=true` diagnosis and the exact
`/release` transaction, never to every merged main SHA. `/merge` dispatches one\nexplicit fast `ci.yml` run with `full=false` after integration because its\nActions-token API merge does not trigger a push workflow. That fast run exists\nonly to create the exact `main` CI record required by release.

## Active workstreams

### WS1 — consume the v0.0.4 / SolidCraft 0.50 baseline

MCP v0.0.4 is published. The remaining checkpoint is to update the workspace
template/concrete workspace pins and rerun the real Windows standalone
workbench acceptance against the released stack.

### WS2 — Forge compatibility evolution

Issue #53 remains the next MCP-owned compatibility task after the workspace
checkpoint: define a versioned Forge compatibility catalog and a repeatable
Forge upgrade procedure instead of treating dependency upgrades as ad-hoc
edits.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #84 | MCP | now | Make initial MCP status probes subprocess-free and correctly annotate read-only tools |
| #53 | MCP | later | Define a versioned Forge compatibility catalog and repeatable Forge upgrade procedure |
| #39 | MCP | probably obsolete | Re-evaluate the old Forge-0.19 operational-skills PR against the current v0.25 skill surface before any reuse |
| #41 | MCP | effectively complete | Confirm the accepted explicit workspace/toolchain contract covers the requested behavior, then close |
| #42 | external workspace owner | move out | Track workspace-template work in its owning repository rather than this MCP repository |

## Recently completed

- #49 qualified Forge/SCPF v0.25.0 and published MCP v0.0.2.
- #56 added bounded live SolidCraft GUI control and was released as MCP v0.0.3.
- #62 qualified SolidCraft 0.50.0 / CAD runtime v0.3.8.
- #70 removed the permanent dev/promotion lane and made `main` the single
  integration branch.
- #75 made PR CI path-sensitive, moved acceptance fixtures out of workflow
  heredocs and batched runtime plus conversion acceptance into one SolidCraft
  container/venv setup.
- #77 published MCP v0.0.4 from qualified stable `main`.
- #80 moved the stable full released-stack gate from every `main` push into\n  the exact repository-local `/release` transaction and consolidated CI\n  support under the repository `modules/ci` Python module.

## Next checkpoint

Update the workspace template and concrete workspace to MCP v0.0.4, then rerun
the real Windows standalone-workbench `doctor` and the 60 x 20 x 4 mm /
diameter-8 live SolidCraft demo.

After that checkpoint, continue broad MCP product work from the current issue
order without reintroducing a permanent promotion lane or always-expensive PR
runtime acceptance.
