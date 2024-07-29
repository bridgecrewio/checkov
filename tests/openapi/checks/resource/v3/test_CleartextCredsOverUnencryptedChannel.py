import os
import unittest

from checkov.openapi.checks.resource.v3.CleartextOverUnencryptedChannel import check
from checkov.openapi.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestCleartextCredsOverUnencryptedChannel(unittest.TestCase):
    def test_summary(self):
        # given
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/example_CleartextCredsOverUnencryptedChannel"

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
        }
        failing_resources = {
            "/fail.yaml",
            "/fail.json",
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
