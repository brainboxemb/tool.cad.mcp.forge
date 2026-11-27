from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from forge_mcp_release.policy import ReleasePolicyError
from forge_mcp_release.service import publish


SHA = "a" * 40


class FakeGitHub:
    tag = None
    release = None
    comments = []

    def __init__(self, repository, token):
        self.repository = repository
        self.token = token

    def main_sha(self):
        return SHA

    def central_ci_is_green(self, sha):
        return sha == SHA

    def tag_target(self, tag):
        return self.__class__.tag

    def create_annotated_tag(self, tag, target_sha):
        self.__class__.tag = target_sha

    def release_for_tag(self, tag):
        return self.__class__.release

    def create_release(self, tag, target_sha, notes):
        self.__class__.release = {
            "html_url": f"https://example.invalid/releases/{tag}"
        }
        return self.__class__.release

    def comment(self, issue_number, body):
        self.__class__.comments.append((issue_number, body))


class ReleaseServiceTests(unittest.TestCase):
    def setUp(self):
        FakeGitHub.tag = None
        FakeGitHub.release = None
        FakeGitHub.comments = []

    def _root(self, path: Path) -> Path:
        (path / "pyproject.toml").write_text(
            '[project]\nname = "forge-cad-mcp"\nversion = "0.0.1"\n',
            encoding="utf-8",
        )
        (path / "CHANGELOG.md").write_text(
            "# Changelog\n\n"
            "## [Unreleased]\n\n"
            "## [0.0.1] - 2026-11-27\n\n"
            "### Added\n\n- First release.\n",
            encoding="utf-8",
        )
        return path

    @patch("forge_mcp_release.service.GitHub", FakeGitHub)
    def test_publish_is_idempotent_for_correct_tag_and_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            tag, url = publish(
                repository="brainboxemb/tool.cad.mcp.forge",
                command=f"/release v0.0.1 {SHA}",
                actor="brainboxemb",
                owner="brainboxemb",
                issue_number=45,
                token="token",
                source_root=root,
            )
            self.assertEqual(tag, "v0.0.1")
            self.assertTrue(url.endswith("/v0.0.1"))

            tag2, url2 = publish(
                repository="brainboxemb/tool.cad.mcp.forge",
                command=f"/release v0.0.1 {SHA}",
                actor="brainboxemb",
                owner="brainboxemb",
                issue_number=45,
                token="token",
                source_root=root,
            )
            self.assertEqual((tag2, url2), (tag, url))

    @patch("forge_mcp_release.service.GitHub", FakeGitHub)
    def test_publish_rejects_wrong_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            with self.assertRaisesRegex(ReleasePolicyError, "only the repository owner"):
                publish(
                    repository="brainboxemb/tool.cad.mcp.forge",
                    command=f"/release v0.0.1 {SHA}",
                    actor="someone",
                    owner="brainboxemb",
                    issue_number=45,
                    token="token",
                    source_root=root,
                )


if __name__ == "__main__":
    unittest.main()
