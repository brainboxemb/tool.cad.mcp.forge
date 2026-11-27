# Forge MCP plan

This file is the current source of truth for unfinished work in
`brainboxemb/tool.cad.mcp.forge`.

The repository exposes version-matched Forge authoring knowledge and bounded
local Forge/SolidCraft execution through MCP. Forge owns compilation;
SolidCraft owns CAD execution; existing CAD verification remains the acceptance
owner for CAD behavior.

## Current accepted baseline

The qualified local Forge MCP baseline is released as `v0.0.8` from stable
`main` commit `da720b8001b3e563cd8c1b56de459425979a0404`.

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
`/release` transaction, never to every merged main SHA. `/merge` dispatches one
explicit fast `ci.yml` run with `full=false` after integration because its
Actions-token API merge does not trigger a push workflow. That fast run exists
only to create the exact `main` CI record required by release.

## Active workstreams

### WS1 — complete real Windows MCP acceptance

MCP v0.0.8 is published and consumed by the template/concrete workspace.
Real Windows Codex acceptance has now proven MCP discovery, fast status,
release-matched knowledge access and the generated workbench skill router.
`forge-modeling` now teaches the minimal `scpf/model.py` contract plus generic
Forge idioms without prescribing model-specific geometry, and its native
`Hole` example follows the qualified additive feature-history semantics. The
current gate is to resume the 60 × 20 × 4 mm / Ø8 live SolidCraft
apply/inspect/mutate/view/render demo.

### WS2 — Forge compatibility evolution

Issue #53 remains the next MCP-owned compatibility task after the workspace
checkpoint: define a versioned Forge compatibility catalog and a repeatable
Forge upgrade procedure instead of treating dependency upgrades as ad-hoc
edits.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #95 | MCP/Forge docs | after acceptance | Align SolidCraft command knowledge with the qualified 0.50.0 runtime without silently relabeling 0.49 docs |
| #53 | MCP | later | Define a versioned Forge compatibility catalog and repeatable Forge upgrade procedure |
| #39 | MCP | probably obsolete | Re-evaluate the old Forge-0.19 operational-skills PR against the current v0.25 skill surface before any reuse |
| #42 | external workspace owner | move out | Track workspace-template work in its owning repository rather than this MCP repository |

## Recently completed

- #106 reconciled the stable plan with the published and workspace-adopted MCP `v0.0.8` baseline.
- #103 published and verified MCP `v0.0.8` from exact stable main commit `da720b8001b3e563cd8c1b56de459425979a0404`.
- #96 made `forge-modeling` the real new-model skill and was refined in v0.0.8 so the maintained `scpf/model.py` contract stays separate from generic Forge API idioms; native `Hole` composition now uses `+`.
- #91 removed per-call Forge Git validation from knowledge/reference and compile
  calls; exact checkout validation remains in the explicit doctor gate.
- #88 made version-only release metadata PRs fast while preserving full
  released-stack acceptance in the exact release transaction.
- #84 made initial MCP status probes subprocess-free and advertised read-only
  tool annotations.
- #49 qualified Forge/SCPF v0.25.0 and published MCP v0.0.2.
- #56 added bounded live SolidCraft GUI control and was released as MCP v0.0.3.
- #62 qualified SolidCraft 0.50.0 / CAD runtime v0.3.8.
- #70 removed the permanent dev/promotion lane and made `main` the single
  integration branch.
- #75 made PR CI path-sensitive, moved acceptance fixtures out of workflow
  heredocs and batched runtime plus conversion acceptance into one SolidCraft
  container/venv setup.
- #77 published MCP v0.0.4 from qualified stable `main`.
- #80 moved the stable full released-stack gate from every `main` push into
  the exact repository-local `/release` transaction and consolidated CI
  support under the repository `modules/ci` Python module.

## Next checkpoint

Resume the already-started Windows 60 × 20 × 4 mm / Ø8 live SolidCraft demo
against workspace-pinned MCP v0.0.8. Treat #95 as a separate documentation
alignment task unless the live engine exposes an actual 0.50 command mismatch.

After that checkpoint, continue broad MCP product work from the current issue
order without reintroducing a permanent promotion lane or always-expensive PR
runtime acceptance.
