# Release procedure

Forge CAD MCP releases are published only from qualified stable `main`.

## Prepare the release

Normal product changes use one temporary work branch and PR directly to
`main`, integrated through the repository `/merge` policy. There is no
permanent development/promotion branch.

Before publication:

1. set `project.version` in `pyproject.toml`;
2. add a dated matching section to `CHANGELOG.md`;
3. integrate the release state to `main`;
4. verify the central `ci` check on that exact `main` SHA is green.

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
2. runs the repository-local `modules/release` Python capability;
3. parses the exact release request and requires the repository owner;
4. validates `pyproject.toml` and the matching dated changelog section;
5. verifies the requested SHA is the current stable `main` head;
6. requires the latest central `ci` check on that SHA to be successful;
7. creates or verifies the immutable annotated `vX.Y.Z` tag;
8. creates or verifies the GitHub Release and records it on the triggering issue.

Release parsing, validation, tagging and GitHub Release publication are owned by
this repository. The workflow does not call an external release publisher.

Do not create normal release tags manually.
