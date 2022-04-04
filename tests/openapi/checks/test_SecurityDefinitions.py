import unittest
from pathlib import Path

from checkov.openapi.checks.resource.SecurityDefinitions import check
from checkov.openapi.runner import Runner
from checkov.runner_filter import RunnerFilter


class SecurityDefinitions(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_SecurityDefinitions"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "/example_SecurityDefinitions/pass1.yaml",
            "/example_SecurityDefinitions/pass1.json",
        }
        failing_resources = {
            "/example_SecurityDefinitions/fail1.yaml",
            "/example_SecurityDefinitions/fail1.json",
            "/example_SecurityDefinitions/fail2.yaml",
            "/example_SecurityDefinitions/fail2.json",
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
