import os
import unittest

from checkov.arm.checks.resource.FunctionAppsAccessibleOverHttps import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestFunctionAppsAccessibleOverHttps(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_FunctionAppsAccessibleOverHttps"
        report = runner.run(root_folder=test_files_dir,runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.Web/sites/config.sites_config_pass",
            "Microsoft.Web/sites/config.sites_config_pass1",
            "Microsoft.Web/sites/slots.sites_pass",
            "Microsoft.Web/sites.sites_pass",
        }
        failing_resources = {
            "Microsoft.Web/sites/config.sites_config_fail",
            "Microsoft.Web/sites/slots.sites_fail",
            "Microsoft.Web/sites.sites_fail",
            "Microsoft.Web/sites/slots.sites_fail1",
            "Microsoft.Web/sites.sites_fail1",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
