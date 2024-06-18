import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.arm.runner import Runner
from checkov.arm.checks.resource.AzureContainerInstanceEnvVarSecureValueType import check


class TestAzureContainerInstanceEnvVarSecureValueType(unittest.TestCase):
    def test_summary(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "example_AzureContainerInstanceEnvVarSecureValueType")

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        summary = report.get_summary()

        passing_resources = {
            'Microsoft.ContainerInstance/containerGroups.pass_1',
            'Microsoft.ContainerInstance/containerGroups.pass_2',
        }
        failing_resources = {
            'Microsoft.ContainerInstance/containerGroups.fail_1',
            'Microsoft.ContainerInstance/containerGroups.fail_2',
        }
        skipped_resources = {}

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], len(skipped_resources))
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()

