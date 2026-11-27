from pathlib import Path
import unittest


class ReleaseWorkflowContractTests(unittest.TestCase):
    def test_workflow_is_thin_python_module_adapter(self):
        root = Path(__file__).resolve().parents[3]
        workflow = (root / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("startsWith(github.event.comment.body, '/release ')", workflow)
        self.assertIn("github.actor == github.repository_owner", workflow)
        self.assertIn("ref: main", workflow)
        self.assertIn("repository: brainboxemb/lib.py.solidcraft.forge", workflow)
        self.assertIn("PYTHONPATH: modules/release/src:modules/ci/src", workflow)
        self.assertEqual(workflow.count("python -m forge_mcp_release"), 1)
        self.assertNotIn("scripts/", workflow)
        self.assertNotIn("python -m pip install", workflow)
        self.assertNotIn("docker run", workflow)


if __name__ == "__main__":
    unittest.main()
