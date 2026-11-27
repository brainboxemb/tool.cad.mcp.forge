from pathlib import Path

import pytest

import release


def _root(tmp_path: Path, *, version: str = "0.0.1") -> Path:
    (tmp_path / "pyproject.toml").write_text(
        f'''[project]
name = "forge-cad-mcp"
version = "{version}"
''',
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text(
        """# Changelog

## [Unreleased]

## [0.0.1] - 2026-11-27

### Added

- First release.
""",
        encoding="utf-8",
    )
    return tmp_path


def test_release_validator_writes_matching_notes(tmp_path):
    root = _root(tmp_path)
    notes = tmp_path / "notes.md"

    release.validate("0.0.1", "a" * 40, notes, root=root)

    text = notes.read_text(encoding="utf-8")
    assert text.startswith("## [0.0.1] - 2026-11-27")
    assert "- First release." in text


def test_release_validator_rejects_package_version_mismatch(tmp_path):
    root = _root(tmp_path, version="0.0.2")
    with pytest.raises(SystemExit, match="package version mismatch"):
        release.validate("0.0.1", "a" * 40, tmp_path / "notes.md", root=root)


def test_release_validator_rejects_non_exact_sha(tmp_path):
    root = _root(tmp_path)
    with pytest.raises(SystemExit, match="40 lowercase hex"):
        release.validate("0.0.1", "abc", tmp_path / "notes.md", root=root)


def test_release_validator_requires_dated_changelog_section(tmp_path):
    root = _root(tmp_path)
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match=r"no dated \[0\.0\.1\] section"):
        release.validate("0.0.1", "a" * 40, tmp_path / "notes.md", root=root)


def test_release_workflow_delegates_publication_and_gates_ci():
    root = Path(__file__).resolve().parents[1]
    workflow = (root / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )

    assert "startsWith(github.event.comment.body, '/release ')" in workflow
    assert "commits/{sha}/check-runs" in workflow
    assert 'check.get("name") == "ci"' in workflow
    assert 'newest.get("conclusion") != "success"' in workflow
    assert (
        "brainboxemb/tool.py.lib.ci/.github/workflows/"
        "reusable-release.yml@58ead6897a4ac8cafef22a3c1f834491bf61568d"
        in workflow
    )
    assert "stable_ref: main" in workflow
    assert "validator_path: release.py" in workflow
