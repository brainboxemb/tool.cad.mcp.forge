# Forge MCP plan

This is the source of truth for unfinished work.

## Current accepted baseline

The qualified local MCP baseline is integrated on `dev`. `main` is still the
pre-product bootstrap baseline and must not be treated as containing the usable
MCP yet.

The qualified development baseline includes:

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

### WS1 — first stable product baseline

Issue #16 owns the explicit `dev -> main` promotion after this plan
reconciliation and a green dev baseline. This promotion does not create a
version tag or GitHub Release.

## Open issue assignment

| Issue | Lane/owner | Status | Next action |
| --- | --- | --- | --- |
| #15 | dev/docs | now | Merge this plan reconciliation and close the issue |
| #16 | dev -> main | next | Promote the qualified local MCP baseline after #15 and green dev CI |

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

## Next checkpoint

Merge #15, verify `dev` remains green, then complete #16 as the first
`dev -> main` product promotion. Decide version/tag/release packaging only
after the stable baseline exists.
