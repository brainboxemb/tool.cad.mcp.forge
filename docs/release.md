# Release procedure

Forge CAD MCP releases are published only from qualified stable `main`.

## Prepare the release

Normal product changes integrate through `dev` and reach `main` through the
repository `/merge` policy.

Before publication:

1. set `project.version` in `pyproject.toml`;
2. add a dated matching section to `CHANGELOG.md`;
3. integrate the release state to `main`;
4. verify the central `ci` check on that exact `main` SHA is green.

Release metadata and product changes may be reviewed together when appropriate,
but the release command itself never changes source.

## Publish

Use a normal release-tracking issue and comment:

~~~text
/release vX.Y.Z <exact-40-character-main-sha>
~~~

The repository release workflow:

1. parses the exact release request;
2. requires a successful central `ci` check for the requested SHA;
3. delegates publication to the released
   `brainboxemb/tool.py.lib.ci` reusable release workflow;
4. validates `pyproject.toml` and the matching dated changelog section;
5. verifies the requested SHA is the current stable `main` head;
6. creates or verifies the immutable `vX.Y.Z` tag and GitHub Release;
7. records the published release on the triggering issue.

Do not create normal release tags manually.
