import unittest
import os
from checkov.arm.checks.resource.AzureDefenderOnKubernetes import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestAzureDefenderOnKubernetes(unittest.TestCase):
    def test_summary(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        # given
        test_files_dir = current_dir + "/example_AzureDefenderOnKubernetes"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()
        passing_resources = {
            "Microsoft.Security/pricings.KubernetesService",
            "Microsoft.Security/pricings.KeyVaults",
            "Microsoft.Security/pricings.SqlServerVirtualMachines",
        }
        failing_resources = {
            "Microsoft.Security/pricings.KubernetesService",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()
