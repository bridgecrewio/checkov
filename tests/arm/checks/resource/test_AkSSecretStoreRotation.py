from checkov.arm.checks.resource.AkSSecretStoreRotation import check
import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.arm.runner import Runner


class TestAKSSecretStoreRotation(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_AkSSecretStoreRotation")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'Microsoft.ContainerService/managedClusters.pass',
        }
        failing_resources = {
            'Microsoft.ContainerService/managedClusters.fail',
            'Microsoft.ContainerService/managedClusters.fail1',
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
