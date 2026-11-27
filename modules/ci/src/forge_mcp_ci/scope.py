"""Decide whether one central CI run needs released-stack CAD acceptance."""

from __future__ import annotations

from pathlib import Path
import subprocess
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


def _normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def runtime_required(paths: Iterable[str]) -> bool:
    for raw in paths:
        path = _normalize(raw)
        if path in _RUNTIME_FILES or path.startswith(_RUNTIME_PREFIXES):
            return True
    return False


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
    return runtime_for_event(event, paths, manual_full=manual_full), paths


def write_github_output(path: Path, *, runtime: bool) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"runtime={'true' if runtime else 'false'}\n")
