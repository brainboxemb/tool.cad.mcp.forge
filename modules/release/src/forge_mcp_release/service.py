"""Release transaction orchestration."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from typing import Callable

from .github import GitHub
from .policy import ReleasePolicyError, parse_command, validate_source


def _validated_request(
    *,
    repository: str,
    command: str,
    actor: str,
    owner: str,
    token: str,
    source_root: Path,
):
    if actor != owner:
        raise ReleasePolicyError("only the repository owner may publish a release")

    version, target_sha = parse_command(command)
    tag = f"v{version}"
    notes = validate_source(source_root, version)

    github = GitHub(repository, token)
    current_main = github.main_sha()
    if current_main != target_sha:
        raise ReleasePolicyError(
            f"release SHA is not current main: {target_sha} != {current_main}"
        )
    if not github.central_ci_is_green(target_sha):
        raise ReleasePolicyError(
            "release SHA has no successful latest central ci check"
        )
    return tag, target_sha, notes, github


def _source_head(source_root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReleasePolicyError("cannot validate checked-out release source") from exc


def preflight(
    *,
    repository: str,
    command: str,
    actor: str,
    owner: str,
    token: str,
    source_root: Path,
) -> tuple[str, str]:
    tag, target_sha, _, _ = _validated_request(
        repository=repository,
        command=command,
        actor=actor,
        owner=owner,
        token=token,
        source_root=source_root,
    )
    local_head = _source_head(source_root)
    if local_head != target_sha:
        raise ReleasePolicyError(
            f"checked-out source is not release SHA: {local_head} != {target_sha}"
        )
    return tag, target_sha


def _install_acceptance_dependencies(
    source_root: Path,
    forge_source_root: Path,
) -> None:
    cadlib = forge_source_root / "cadlib"
    if not cadlib.is_dir():
        raise ReleasePolicyError(f"Forge cadlib not found: {cadlib}")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", str(source_root), str(cadlib)],
        cwd=source_root,
        check=True,
    )


def publish(
    *,
    repository: str,
    command: str,
    actor: str,
    owner: str,
    issue_number: int,
    token: str,
    source_root: Path,
) -> tuple[str, str]:
    tag, target_sha, notes, github = _validated_request(
        repository=repository,
        command=command,
        actor=actor,
        owner=owner,
        token=token,
        source_root=source_root,
    )

    existing_target = github.tag_target(tag)
    if existing_target is None:
        github.create_annotated_tag(tag, target_sha)
    elif existing_target != target_sha:
        raise ReleasePolicyError(
            f"existing tag {tag} points to {existing_target}, not {target_sha}"
        )

    release = github.release_for_tag(tag)
    if release is None:
        release = github.create_release(tag, target_sha, notes)

    url = release.get("html_url")
    if not isinstance(url, str) or not url:
        raise ReleasePolicyError("GitHub Release has no html_url")

    github.comment(
        issue_number,
        f"Published and verified {tag} at {target_sha}: {url}",
    )
    return tag, url


def transaction(
    *,
    repository: str,
    command: str,
    actor: str,
    owner: str,
    issue_number: int,
    token: str,
    source_root: Path,
    forge_source_root: Path,
    acceptance: Callable[[], None] | None = None,
    install_dependencies: Callable[[Path, Path], None] = _install_acceptance_dependencies,
) -> tuple[str, str]:
    preflight(
        repository=repository,
        command=command,
        actor=actor,
        owner=owner,
        token=token,
        source_root=source_root,
    )
    install_dependencies(source_root, forge_source_root)

    previous_forge_root = os.environ.get("FORGE_SOURCE_ROOT")
    os.environ["FORGE_SOURCE_ROOT"] = str(forge_source_root)
    try:
        if acceptance is None:
            from forge_mcp_ci.acceptance import run as acceptance
        acceptance()
    finally:
        if previous_forge_root is None:
            os.environ.pop("FORGE_SOURCE_ROOT", None)
        else:
            os.environ["FORGE_SOURCE_ROOT"] = previous_forge_root

    return publish(
        repository=repository,
        command=command,
        actor=actor,
        owner=owner,
        issue_number=issue_number,
        token=token,
        source_root=source_root,
    )
