from pathlib import Path
import unittest


class ReleaseWorkflowContractTests(unittest.TestCase):
    def test_workflow_uses_repository_local_release_module(self):
        root = Path(__file__).resolve().parents[3]
        workflow = (root / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("startsWith(github.event.comment.body, '/release ')", workflow)
        self.assertIn("ref: main", workflow)
        self.assertIn("PYTHONPATH: modules/release/src", workflow)
        self.assertIn("python -m forge_mcp_release", workflow)
        self.assertNotIn("tool.py.lib.ci", workflow)
        self.assertNotIn("reusable-release.yml", workflow)


if __name__ == "__main__":
    unittest.main()
