"""Decide whether one central CI run needs released-stack CAD acceptance."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import tomllib
from typing import Iterable


_RUNTIME_FILES = frozenset(
    {
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
        "pyproject.toml",
        "tests/test_compiler.py",
        "tests/test_conversion.py",
        "tests/test_runtime.py",
    }
)
_RUNTIME_PREFIXES = (
    "modules/ci/",
    "src/forge_mcp/",
    "tests/fixtures/",
)
_RELEASE_METADATA_FILES = frozenset({"CHANGELOG.md", "pyproject.toml"})


def _normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def runtime_required(paths: Iterable[str]) -> bool:
    for raw in paths:
        path = _normalize(raw)
        if path in _RUNTIME_FILES or path.startswith(_RUNTIME_PREFIXES):
            return True
    return False


def _file_at_ref(ref: str, path: str) -> str:
    return subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _project_version_only_changed(before: str, after: str) -> bool:
    before_data = tomllib.loads(before)
    after_data = tomllib.loads(after)
    before_project = before_data.get("project")
    after_project = after_data.get("project")
    if not isinstance(before_project, dict) or not isinstance(after_project, dict):
        return False

    before_version = before_project.get("version")
    after_version = after_project.get("version")
    if not isinstance(before_version, str) or not isinstance(after_version, str):
        return False
    if before_version == after_version:
        return False

    before_rest = deepcopy(before_data)
    after_rest = deepcopy(after_data)
    before_rest["project"].pop("version", None)
    after_rest["project"].pop("version", None)
    return before_rest == after_rest


def release_metadata_only(base: str, head: str, paths: Iterable[str]) -> bool:
    normalized = frozenset(_normalize(path) for path in paths)
    if normalized != _RELEASE_METADATA_FILES:
        return False
    return _project_version_only_changed(
        _file_at_ref(base, "pyproject.toml"),
        _file_at_ref(head, "pyproject.toml"),
    )


def changed_paths(base: str, head: str) -> tuple[str, ...]:
    if not base or not head:
        raise ValueError("pull-request scope requires exact base and head SHAs")
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(path for path in result.stdout.splitlines() if path.strip())


def runtime_for_event(
    event: str,
    paths: Iterable[str] = (),
    *,
    manual_full: bool = False,
) -> bool:
    if event == "pull_request":
        return runtime_required(paths)
    if event == "workflow_dispatch":
        return manual_full
    return False


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def classify(
    *,
    event: str,
    base: str = "",
    head: str = "",
    manual_full: bool = False,
) -> tuple[bool, tuple[str, ...]]:
    paths = changed_paths(base, head) if event == "pull_request" else ()
    if event == "pull_request" and release_metadata_only(base, head, paths):
        return False, paths
    return runtime_for_event(event, paths, manual_full=manual_full), paths


def write_github_output(path: Path, *, runtime: bool) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"runtime={'true' if runtime else 'false'}\n")
