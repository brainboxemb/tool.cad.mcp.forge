import unittest

from cad_model_branch_cleanup.config import CleanupConfig
from cad_model_branch_cleanup.policy import (
    eligible_post_merge,
    eligible_sweep,
    is_temporary,
    merge_target,
)


CONFIG = CleanupConfig(
    stable="main",
    temporary_prefixes=("issue/", "fix/", "feature/", "docs/", "chore/", "release/"),
)


class PolicyTests(unittest.TestCase):
    def test_main_is_the_only_permanent_branch(self):
        self.assertFalse(is_temporary("main", CONFIG))

    def test_old_permanent_lane_names_are_not_special(self):
        self.assertFalse(is_temporary("dev", CONFIG))
        self.assertFalse(is_temporary("exp", CONFIG))

    def test_allowed_prefix_is_temporary(self):
        self.assertTrue(is_temporary("issue/11-cleanup", CONFIG))

    def test_all_temporary_branches_target_main(self):
        self.assertEqual(merge_target("issue/11-work", CONFIG), "main")
        self.assertEqual(merge_target("release/v1.2.3", CONFIG), "main")

    def test_merged_same_repo_temporary_branch_to_main_is_eligible(self):
        self.assertTrue(
            eligible_post_merge(
                head="fix/7-cleanup",
                base="main",
                same_repository=True,
                merged=True,
                config=CONFIG,
            )
        )

    def test_old_dev_target_is_not_eligible(self):
        self.assertFalse(
            eligible_post_merge(
                head="issue/11-work",
                base="dev",
                same_repository=True,
                merged=True,
                config=CONFIG,
            )
        )

    def test_unmerged_or_open_work_is_not_sweep_eligible(self):
        self.assertFalse(
            eligible_sweep(
                branch="issue/11-work",
                has_open_pr=True,
                has_merged_pr_to_target=True,
                config=CONFIG,
            )
        )
        self.assertFalse(
            eligible_sweep(
                branch="issue/12-unmerged",
                has_open_pr=False,
                has_merged_pr_to_target=False,
                config=CONFIG,
            )
        )


if __name__ == "__main__":
    unittest.main()
