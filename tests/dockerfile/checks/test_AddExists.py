import os
import unittest

from checkov.dockerfile.checks.AddExists import check
from checkov.dockerfile.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestAddExists(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_AddExists"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        failing_resources = {"/failure/Dockerfile.ADD"}

        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
