import unittest
from unittest.mock import patch

from cad_model_merge_policy.__main__ import (
    dispatch_workflow,
    merge_required,
    require_green_ci,
)
from cad_model_merge_policy.policy import MergePolicyError, merge_method


def check(name, status, conclusion, *prs):
    return {
        "name": name,
        "status": status,
        "conclusion": conclusion,
        "pull_requests": [{"number": number} for number in prs],
    }


class MergePolicyTests(unittest.TestCase):
    def test_open_pull_request_requires_merge(self):
        self.assertTrue(merge_required({"state": "open", "merged": False}))

    def test_already_merged_pull_request_is_idempotent_noop(self):
        self.assertFalse(
            merge_required(
                {
                    "state": "closed",
                    "merged": True,
                    "merge_commit_sha": "abc123",
                }
            )
        )

    def test_closed_unmerged_pull_request_is_rejected(self):
        with self.assertRaisesRegex(MergePolicyError, "closed without merge"):
            merge_required({"state": "closed", "merged": False})

    def test_temporary_branches_to_main_are_squashed(self):
        for head in (
            "issue/10-change",
            "fix/11-bug",
            "feature/12-capability",
            "docs/13-guide",
            "chore/14-maintenance",
            "release/v1.2.3",
        ):
            with self.subTest(head=head):
                self.assertEqual(merge_method(head=head, base="main"), "squash")

    def test_permanent_or_old_lane_integrations_are_rejected(self):
        for head, base in (
            ("dev", "main"),
            ("main", "dev"),
            ("exp", "main"),
            ("main", "exp"),
            ("issue/10-change", "dev"),
            ("release/v1.2.3", "dev"),
        ):
            with self.subTest(head=head, base=base), self.assertRaises(MergePolicyError):
                merge_method(head=head, base=base)

    @patch("cad_model_merge_policy.__main__.api")
    def test_green_ci_allows_unrelated_pending_merge_check(self, api):
        api.return_value = {
            "check_runs": [
                check("ci", "completed", "success", 25),
                check("merge", "in_progress", None, 25),
                check("cleanup", "queued", None, 25),
            ]
        }
        require_green_ci("owner/repo", "sha", 25, "token")

    @patch("cad_model_merge_policy.__main__.api")
    def test_pending_ci_blocks_merge(self, api):
        api.return_value = {
            "check_runs": [check("ci", "in_progress", None, 25)]
        }
        with self.assertRaisesRegex(MergePolicyError, "still running"):
            require_green_ci("owner/repo", "sha", 25, "token")

    @patch("cad_model_merge_policy.__main__.api")
    def test_failed_ci_blocks_merge(self, api):
        api.return_value = {
            "check_runs": [check("ci", "completed", "failure", 25)]
        }
        with self.assertRaisesRegex(MergePolicyError, "not green"):
            require_green_ci("owner/repo", "sha", 25, "token")

    @patch("cad_model_merge_policy.__main__.api")
    def test_missing_pr_specific_ci_blocks_merge(self, api):
        api.return_value = {
            "check_runs": [
                check("ci", "completed", "success", 99),
                check("merge", "completed", "success", 25),
            ]
        }
        with self.assertRaisesRegex(MergePolicyError, "no central ci"):
            require_green_ci("owner/repo", "sha", 25, "token")

    @patch("cad_model_merge_policy.__main__.api")
    def test_dispatch_workflow_targets_main(self, api):
        dispatch_workflow("owner/repo", "ci.yml", "main", "token")
        api.assert_called_once_with(
            "owner/repo",
            "actions/workflows/ci.yml/dispatches",
            "token",
            method="POST",
            body={"ref": "main"},
        )

    @patch("cad_model_merge_policy.__main__.api")
    def test_cleanup_workflow_targets_main(self, api):
        dispatch_workflow("owner/repo", "branch-cleanup.yml", "main", "token")
        api.assert_called_once_with(
            "owner/repo",
            "actions/workflows/branch-cleanup.yml/dispatches",
            "token",
            method="POST",
            body={"ref": "main"},
        )


if __name__ == "__main__":
    unittest.main()
