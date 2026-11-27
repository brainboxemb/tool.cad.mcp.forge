from pathlib import Path
import tempfile
import unittest

from forge_mcp_release.policy import (
    ReleasePolicyError,
    parse_command,
    validate_source,
)


SHA = "a" * 40


class ReleasePolicyTests(unittest.TestCase):
    def _root(self, path: Path, version: str = "0.0.1") -> Path:
        (path / "pyproject.toml").write_text(
            f'[project]\nname = "forge-cad-mcp"\nversion = "{version}"\n',
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

    def test_parse_exact_release_command(self):
        self.assertEqual(
            parse_command(f"/release v0.0.1 {SHA}"),
            ("0.0.1", SHA),
        )

    def test_rejects_non_exact_release_command(self):
        with self.assertRaisesRegex(ReleasePolicyError, "must be exactly"):
            parse_command(f"release 0.0.1 {SHA}")

    def test_validate_source_returns_release_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp))
            notes = validate_source(root, "0.0.1")
            self.assertIn("## [0.0.1] - 2026-11-27", notes)
            self.assertIn("- First release.", notes)

    def test_validate_source_rejects_version_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._root(Path(tmp), version="0.0.2")
            with self.assertRaisesRegex(ReleasePolicyError, "version mismatch"):
                validate_source(root, "0.0.1")


if __name__ == "__main__":
    unittest.main()
