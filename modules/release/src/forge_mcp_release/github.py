"""Minimal GitHub REST client for repository-local release publication."""

from __future__ import annotations

import json
from urllib import error, parse, request

from .policy import ReleasePolicyError


class GitHub:
    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.token = token

    def api(self, path: str, *, method: str = "GET", body=None, allow_404=False):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = request.Request(
            f"https://api.github.com/repos/{self.repository}/{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with request.urlopen(req) as response:
                if response.status == 204:
                    return None
                return json.load(response)
        except error.HTTPError as exc:
            if allow_404 and exc.code == 404:
                return None
            detail = exc.read().decode("utf-8", errors="replace")
            raise ReleasePolicyError(
                f"GitHub API {exc.code}: {detail}"
            ) from exc

    def main_sha(self) -> str:
        return self.api("git/ref/heads/main")["object"]["sha"]

    def central_ci_is_green(self, sha: str) -> bool:
        checks = self.api(f"commits/{sha}/check-runs").get("check_runs", [])
        central = [check for check in checks if check.get("name") == "ci"]
        if not central:
            return False
        newest = max(central, key=lambda check: check.get("id", 0))
        return (
            newest.get("status") == "completed"
            and newest.get("conclusion") == "success"
        )

    def tag_target(self, tag: str) -> str | None:
        ref = self.api(
            f"git/ref/tags/{parse.quote(tag, safe='')}",
            allow_404=True,
        )
        if ref is None:
            return None
        obj = ref["object"]
        if obj.get("type") == "commit":
            return obj["sha"]
        if obj.get("type") == "tag":
            annotated = self.api(f"git/tags/{obj['sha']}")
            target = annotated.get("object", {})
            if target.get("type") != "commit":
                raise ReleasePolicyError(
                    f"tag {tag} does not resolve directly to a commit"
                )
            return target["sha"]
        raise ReleasePolicyError(f"unsupported tag object type for {tag}")

    def create_annotated_tag(self, tag: str, target_sha: str) -> None:
        tag_object = self.api(
            "git/tags",
            method="POST",
            body={
                "tag": tag,
                "message": f"{tag} release",
                "object": target_sha,
                "type": "commit",
            },
        )
        self.api(
            "git/refs",
            method="POST",
            body={"ref": f"refs/tags/{tag}", "sha": tag_object["sha"]},
        )

    def release_for_tag(self, tag: str):
        return self.api(
            f"releases/tags/{parse.quote(tag, safe='')}",
            allow_404=True,
        )

    def create_release(self, tag: str, target_sha: str, notes: str):
        return self.api(
            "releases",
            method="POST",
            body={
                "tag_name": tag,
                "target_commitish": target_sha,
                "name": tag,
                "body": notes,
                "draft": False,
                "prerelease": False,
            },
        )

    def comment(self, issue_number: int, body: str) -> None:
        self.api(
            f"issues/{issue_number}/comments",
            method="POST",
            body={"body": body},
        )
