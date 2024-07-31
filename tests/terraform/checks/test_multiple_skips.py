import os
import unittest
from pathlib import Path
from unittest.mock import patch

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestMultipleSkips(unittest.TestCase):
    @patch.dict(os.environ, {'CHECKOV_ALLOW_SKIP_MULTIPLE_ONE_LINE': 'True'})
    def test(self) -> None:
        # given
        test_files_dir = Path(__file__).parent / "a_example_skip"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[]))

        # then
        summary = report.get_summary()

        skipped_resources = {
            "azurerm_storage_account.default": 1,
            "azurerm_storage_account.skip_invalid": 1,
            "azurerm_storage_account.skip_more_than_one": 2,
            "azurerm_storage_account.skip_all_checks": 3,
        }

        for skipped_check in report.skipped_checks:
            resource = skipped_check.resource  # Access resource attribute directly
            if resource in skipped_resources:
                skipped_resources[resource] -= 1

        for resource, count in skipped_resources.items():
            self.assertEqual(count, 0, f"{resource} did not skip the expected number of checks")

        self.assertEqual(summary["passed"], 16)
        self.assertEqual(summary["failed"], 33)
        self.assertEqual(summary["skipped"], 7)
        self.assertEqual(summary["parsing_errors"], 0)


if __name__ == "__main__":
    unittest.main()
