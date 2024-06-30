import os
import unittest

from checkov.arm.checks.resource.AutomationEncrypted import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestAutomationEncrypted(unittest.TestCase):
    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_AutomationEncrypted"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Automation/automationAccounts/variables.pass",
        }

        failing_resources = {
            "Microsoft.Automation/automationAccounts/variables.fail",
            "Microsoft.Automation/automationAccounts/variables.fail1",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)
