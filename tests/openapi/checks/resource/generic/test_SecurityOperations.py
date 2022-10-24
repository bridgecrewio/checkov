import os
import unittest

from checkov.openapi.checks.resource.generic.SecurityOperations import check
from checkov.openapi.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestSecurityOperations(unittest.TestCase):
    def test_summary(self):
        # given
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_SecurityOperations"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "/pass1.yaml",
            "/pass1.json",
            "/pass2.yaml",
            "/pass2.json",
        }
        failing_resources = {
            "/fail1.yaml",
            "/fail1.json",
            "/fail2.yaml",
            "/fail2.json",
            "/fail3.yaml",
            "/fail3.json",
            "/fail4.yaml",
            "/fail4.json",
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
