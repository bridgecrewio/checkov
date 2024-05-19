import unittest
from pathlib import Path

from checkov.arm.checks.resource.FunctionAppMinTLSVersion import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestFunctionAppMinTLSVersion(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_FunctionAppMinTLSVersion"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Web/sites.pass",
            "Microsoft.Web/sites.pass2",
            "Microsoft.Web/sites/slots.pass3",
            "Microsoft.Web/sites/slots.pass4",
        }
        failing_resources = {
            "Microsoft.Web/sites.fail",
            "Microsoft.Web/sites/slots.fail2",
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
