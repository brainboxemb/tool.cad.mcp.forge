"""Pure release policy and metadata validation."""

from __future__ import annotations

from pathlib import Path
import re
import tomllib


_COMMAND = re.compile(
    r"^/release v((?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)) ([0-9a-f]{40})$"
)


class ReleasePolicyError(RuntimeError):
    """Release request or repository metadata is invalid."""


def parse_command(command: str) -> tuple[str, str]:
    match = _COMMAND.fullmatch(command.strip())
    if match is None:
        raise ReleasePolicyError(
            "release command must be exactly /release vX.Y.Z <40-char-sha>"
        )
    return match.group(1), match.group(2)


def release_notes(changelog: str, version: str) -> str:
    unreleased = changelog.find("## [Unreleased]")
    if unreleased < 0:
        raise ReleasePolicyError("CHANGELOG.md has no [Unreleased] section")

    heading = re.compile(
        rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
        re.MULTILINE,
    )
    match = heading.search(changelog)
    if match is None:
        raise ReleasePolicyError(
            f"CHANGELOG.md has no dated [{version}] section"
        )
    if match.start() < unreleased:
        raise ReleasePolicyError(
            f"[{version}] must follow the [Unreleased] section"
        )

    next_heading = re.compile(r"^## \[", re.MULTILINE).search(
        changelog, match.end()
    )
    end = next_heading.start() if next_heading else len(changelog)
    notes = changelog[match.start():end].strip()
    if not re.search(r"^### ", notes, re.MULTILINE):
        raise ReleasePolicyError(
            f"CHANGELOG.md [{version}] section has no release content"
        )
    return notes + "\n"


def validate_source(root: Path, version: str) -> str:
    pyproject = tomllib.loads(
        (root / "pyproject.toml").read_text(encoding="utf-8")
    )
    project = pyproject.get("project")
    if not isinstance(project, dict):
        raise ReleasePolicyError("pyproject.toml has no [project] table")

    package_name = project.get("name")
    package_version = project.get("version")
    if package_name != "forge-cad-mcp":
        raise ReleasePolicyError(f"unexpected package name: {package_name!r}")
    if package_version != version:
        raise ReleasePolicyError(
            f"package version mismatch: expected {version}, found {package_version}"
        )

    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    return release_notes(changelog, version)
