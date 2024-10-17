import unittest
from pathlib import Path

from checkov.arm.checks.resource.FunctionAppHttpVersionLatest import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestFunctionAppHttpVersionLatest(unittest.TestCase):

    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_FunctionAppHttpVersionLatest"
        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        # then
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Web/sites/slots.pass",
            "Microsoft.Web/sites.pass2",

        }
        failing_resources = {
            "Microsoft.Web/sites/slots.fail",
            "Microsoft.Web/sites.fail2"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)
