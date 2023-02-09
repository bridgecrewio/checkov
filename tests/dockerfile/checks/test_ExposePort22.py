import unittest
from pathlib import Path

from checkov.dockerfile.checks.ExposePort22 import check
from checkov.dockerfile.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestExposePort22(unittest.TestCase):
    def test(self):
        #  given
        test_files_dir = Path(__file__).parent / "example_ExposePort22"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "/success/Dockerfile.",
        }
        failing_resources = {
            "/failure/Dockerfile.EXPOSE",
            "/failure_tcp/Dockerfile.EXPOSE",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
