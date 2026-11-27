# Release procedure

Forge CAD MCP releases are published only from stable `main` through the
repository-local release transaction.

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

Release metadata may use a temporary `release/*` branch to `main` when it is
not part of the product-change PR. The release command itself never changes
source.

## Publish

Use a normal release-tracking issue and comment:

~~~text
/release vX.Y.Z <exact-40-character-main-sha>
~~~

The repository release workflow is intentionally self-contained:

1. checks out stable `main`;
2. runs repository-local release preflight;
3. parses the exact release request and requires the repository owner;
4. validates `pyproject.toml` and the matching dated changelog section;
5. verifies the requested SHA is current stable `main`, has green central
   `ci`, and exactly matches the local checkout;
6. checks out the qualified Forge release and installs the acceptance
   dependencies;
7. runs `scripts/run_released_stack_acceptance.sh`, which compiles the
   maintained fixtures and executes runtime plus existing-design conversion
   acceptance in one SolidCraft v0.50.0 / CAD runtime v0.3.8 container and one
   container virtual environment;
8. reruns the cheap release-state validation to ensure `main` did not move;
9. creates or verifies the annotated `vX.Y.Z` tag;
10. creates or verifies the GitHub Release and records it on the triggering
    issue.

No tag or GitHub Release is created if released-stack acceptance fails.

Release parsing, validation, tagging and GitHub Release publication are owned by
this repository. The workflow does not call an external release publisher.

Do not create normal release tags manually.
