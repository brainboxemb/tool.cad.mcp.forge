"""Release transaction orchestration."""

from __future__ import annotations

from pathlib import Path

from .github import GitHub
from .policy import ReleasePolicyError, parse_command, validate_source


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
        f"Published and verified `{tag}` at `{target_sha}`: {url}",
    )
    return tag, url
