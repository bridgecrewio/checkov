import os
import unittest

from checkov.openapi.checks.resource.generic.ClearTextAPIKey import check
from checkov.openapi.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestClearTextAPIKey(unittest.TestCase):
    def test_summary(self):
        # given
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_ClearTextAPIKey"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "/pass.yaml",
            "/pass.json",
            "/pass2.yaml",
            "/pass2.json",
            "/pass3.yaml",
            "/pass3.json",
            "/pass4.yaml",
            "/pass4.json",
            "/pass5.yaml",
            "/pass5.json",
            "/pass6.yaml",
            "/pass6.json",
        }
        failing_resources = {
            "/fail.yaml",
            "/fail.json",
            "/fail2.yaml",
            "/fail2.json",
            "/fail3.yaml",
            "/fail3.json",
            "/fail4.yaml",
            "/fail4.json",
            "/fail5.yaml",
            "/fail5.json",
        }

        passed_check_resources = {c.file_path for c in report.passed_checks}
        failed_check_resources = {c.file_path for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()