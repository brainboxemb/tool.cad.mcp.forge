# Forge MCP plan

This file is the current source of truth for unfinished work in
`brainboxemb/tool.cad.mcp.forge`.

The repository exposes version-matched Forge authoring knowledge and bounded
local Forge/SolidCraft execution through MCP. Forge owns compilation;
SolidCraft owns CAD execution; existing CAD verification remains the acceptance
owner for CAD behavior.

## Current accepted baseline

The latest published MCP release is `v0.0.3`. Current `main` is prepared as
`0.0.4` and contains the qualified SolidCraft 0.50.0 baseline from issue #62.

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

Development-cycle cost is architectural: a normal source change should require
one PR qualification path, not a second permanent-lane promotion of the same
content. Expensive CAD/runtime acceptance is a separate CI-design concern and
must be simplified independently.

## Active workstreams

### WS1 — publish and consume the 0.50 baseline

The SolidCraft 0.50.0 source/runtime compatibility change is on `main` as
package version 0.0.4. The remaining checkpoint is publication of v0.0.4,
workspace/template pin updates and the real Windows standalone-workbench
acceptance.

### WS2 — CI feedback-loop cleanup

The current central CI still performs package tests, fixture construction, wheel
building, two separate SolidCraft container/venv acceptance runs and repository
policy tests in one serial job. Redesign that feedback loop separately; do not
hide it inside feature work.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #53 | MCP | later | Define a versioned Forge compatibility catalog and repeatable Forge upgrade procedure |
| #39 | MCP | probably obsolete | Re-evaluate the old Forge-0.19 operational-skills PR against the current v0.25 skill surface before any reuse |
| #41 | MCP | effectively complete but still open | Close after confirming the accepted explicit workspace/toolchain contract covers the requested behavior |
| #42 | external workspace owner | probably obsolete here | Track workspace-template work in its owning repository rather than this MCP repository |
| #43 | MCP | effectively complete but still open | Close; superseded by repository-local release issue #45 |
| #45 | MCP | effectively complete but still open | Close; repository-local release capability is already accepted |
| #54 | MCP | effectively complete but still open | Close; v0.0.2 plan reconciliation was merged in PR #55 |
| #62 | MCP | effectively complete but still open | Close after v0.0.4 publication checkpoint is recorded |
| #63 | MCP | effectively complete but still open | Close; v0.0.3 release metadata was synchronized in PR #64 |

## Recently completed

- #49 qualified Forge/SCPF v0.25.0 and published MCP v0.0.2.
- #56 added bounded live SolidCraft GUI control and was released as MCP v0.0.3.
- #62 qualified SolidCraft 0.50.0 / CAD runtime v0.3.8 and placed the 0.0.4
  source baseline on `main`.
- #70 removes the unnecessary permanent dev/promotion lane and makes `main`
  the single integration branch.

## Next release/checkpoint

Publish MCP v0.0.4 from qualified `main`, update the workspace
template/concrete workspace pins, and rerun the real Windows standalone
workbench doctor plus the 60 x 20 x 4 mm / diameter-8 live SolidCraft demo.

After that, take the CI feedback-loop cleanup as the next repository
infrastructure change before adding another broad capability.
