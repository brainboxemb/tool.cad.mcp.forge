import unittest
from unittest.mock import patch

from forge_mcp_ci.scope import (
    _project_version_only_changed,
    classify,
    runtime_for_event,
    runtime_required,
)


class ScopeTests(unittest.TestCase):
    def test_docs_and_repository_policy_changes_skip_released_stack(self):
        self.assertFalse(
            runtime_required(
                [
                    "docs/plan.md",
                    "AGENTS.md",
                    "README.md",
                    "ci.yml",
                    "modules/merge-policy/src/cad_model_merge_policy/policy.py",
                ]
            )
        )

    def test_runtime_changes_require_released_stack(self):
        for path in (
            "src/forge_mcp/runtime.py",
            "src/forge_mcp/skills/forge-modeling/SKILL.md",
            "pyproject.toml",
            ".github/workflows/ci.yml",
            ".github/workflows/release.yml",
            "modules/ci/src/forge_mcp_ci/acceptance.py",
            "modules/ci/fixtures/acceptance_box.py",
            "tests/fixtures/existing-box.json",
            "tests/test_compiler.py",
            "tests/test_runtime.py",
            "tests/test_conversion.py",
        ):
            with self.subTest(path=path):
                self.assertTrue(runtime_required([path]))

    def test_release_metadata_version_only_diff_skips_released_stack(self):
        before = """[project]\nname = "forge-cad-mcp"\nversion = "0.0.4"\ndependencies = ["fastmcp==2.14.7"]\n"""
        after = """[project]\nname = "forge-cad-mcp"\nversion = "0.0.5"\ndependencies = ["fastmcp==2.14.7"]\n"""
        self.assertTrue(_project_version_only_changed(before, after))
        with patch(
            "forge_mcp_ci.scope.changed_paths",
            return_value=("CHANGELOG.md", "pyproject.toml"),
        ), patch(
            "forge_mcp_ci.scope._file_at_ref",
            side_effect=(before, after),
        ):
            required, paths = classify(
                event="pull_request",
                base="a" * 40,
                head="b" * 40,
            )
        self.assertFalse(required)
        self.assertEqual(paths, ("CHANGELOG.md", "pyproject.toml"))

    def test_release_metadata_dependency_change_still_requires_released_stack(self):
        before = """[project]\nname = "forge-cad-mcp"\nversion = "0.0.4"\ndependencies = ["fastmcp==2.14.7"]\n"""
        after = """[project]\nname = "forge-cad-mcp"\nversion = "0.0.5"\ndependencies = ["fastmcp==2.15.0"]\n"""
        self.assertFalse(_project_version_only_changed(before, after))
        with patch(
            "forge_mcp_ci.scope.changed_paths",
            return_value=("CHANGELOG.md", "pyproject.toml"),
        ), patch(
            "forge_mcp_ci.scope._file_at_ref",
            side_effect=(before, after),
        ):
            required, _ = classify(
                event="pull_request",
                base="a" * 40,
                head="b" * 40,
            )
        self.assertTrue(required)

    def test_main_push_and_default_manual_dispatch_skip_released_stack(self):
        self.assertFalse(runtime_for_event("push"))
        self.assertFalse(runtime_for_event("workflow_dispatch"))

    def test_explicit_manual_full_dispatch_runs_released_stack(self):
        self.assertTrue(runtime_for_event("workflow_dispatch", manual_full=True))

    def test_pull_request_scope_uses_changed_paths(self):
        self.assertFalse(runtime_for_event("pull_request", ["docs/design.md"]))
        self.assertTrue(
            runtime_for_event("pull_request", ["src/forge_mcp/compiler.py"])
        )


if __name__ == "__main__":
    unittest.main()
