"""Classify whether a CI run needs released SolidCraft acceptance."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
from typing import Iterable


_RUNTIME_FILES = frozenset(
    {
        ".github/workflows/ci.yml",
        ".github/workflows/release.yml",
        "pyproject.toml",
        "scripts/ci_scope.py",
        "scripts/prepare_acceptance.py",
        "scripts/run_released_stack_acceptance.sh",
        "tests/test_compiler.py",
        "tests/test_conversion.py",
        "tests/test_runtime.py",
    }
)
_RUNTIME_PREFIXES = (
    "src/forge_mcp/",
    "tests/fixtures/",
)


def _normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def runtime_required(paths: Iterable[str]) -> bool:
    """Return whether changed paths can affect compile/runtime/package acceptance."""

    for raw in paths:
        path = _normalize(raw)
        if path in _RUNTIME_FILES or path.startswith(_RUNTIME_PREFIXES):
            return True
    return False


def changed_paths(base: str, head: str) -> tuple[str, ...]:
    """Return paths changed between exact pull-request base and head SHAs."""

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
    """PRs are path-sensitive; post-merge pushes and default dispatches are fast."""

    if event == "pull_request":
        return runtime_required(paths)
    if event == "workflow_dispatch":
        return manual_full
    return False


def _bool(value: str) -> bool:
    return value.strip().lower() == "true"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    parser.add_argument("--manual-full", default="false")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    paths = changed_paths(args.base, args.head) if args.event == "pull_request" else ()
    required = runtime_for_event(
        args.event,
        paths,
        manual_full=_bool(args.manual_full),
    )

    print(f"released_stack_acceptance={'required' if required else 'skipped'}")
    for path in paths:
        print(path)

    if args.github_output is not None:
        with args.github_output.open("a", encoding="utf-8") as stream:
            stream.write(f"runtime={'true' if required else 'false'}\n")


if __name__ == "__main__":
    main()
