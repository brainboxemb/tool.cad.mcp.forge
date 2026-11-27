# Release procedure

Forge CAD MCP releases are published only from stable `main` through the
repository-local Python release module.

## Prepare the release

Normal product changes use one temporary work branch and PR directly to
`main`, integrated through the repository `/merge` policy. There is no
permanent development/promotion branch.

Before publication:

1. set `project.version` in `pyproject.toml`;
2. add a dated matching section to `CHANGELOG.md`;
3. integrate the release state to `main`;
4. require the central `ci` check on that exact `main` SHA to be green.

An ordinary push to `main` runs fast CI only. It does not rerun SolidCraft
released-stack acceptance merely because a PR was merged.

## Publish

Use a normal release-tracking issue and comment:

~~~text
/release vX.Y.Z <exact-40-character-main-sha>
~~~

The GitHub workflow is intentionally thin: it checks out stable `main`, sets
up Python, checks out the qualified Forge release, then invokes
`python -m forge_mcp_release` exactly once.

The Python release transaction then:

1. validates the exact release command, repository owner and release metadata;
2. verifies the requested SHA is current `main`, has green central `ci`, and
   exactly matches the local checkout;
3. installs the MCP package and qualified Forge cadlib needed by acceptance;
4. invokes the released-stack acceptance owned by `modules/ci`;
5. reruns the cheap current-main/CI validation before publication;
6. creates or verifies the annotated `vX.Y.Z` tag;
7. creates or verifies the GitHub Release and records it on the triggering
   issue.

The acceptance module compiles the maintained fixtures and executes runtime plus
existing-design conversion acceptance in one SolidCraft 0.50.0 / CAD runtime
v0.3.8 container and one container virtual environment. No tag or GitHub
Release is created if that acceptance fails.

There is no shell-script orchestration layer between GitHub Actions and the
Python modules.

Do not create normal release tags manually.
