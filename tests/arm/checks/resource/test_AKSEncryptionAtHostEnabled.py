import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.arm.runner import Runner
from checkov.arm.checks.resource.AKSEncryptionAtHostEnabled import check


class TestAKSEncryptionAtHostEnabled(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_AKSEncryptionAtHostEnabled")
        report = runner.run(root_folder=test_files_dir,
                            runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'Microsoft.ContainerService/managedClusters.pass',
            'Microsoft.ContainerService/managedClusters/agentPools.passA'
        }
        failing_resources = {
            'Microsoft.ContainerService/managedClusters.fail1',
            'Microsoft.ContainerService/managedClusters.fail2',
            'Microsoft.ContainerService/managedClusters/agentPools.failA1',
            'Microsoft.ContainerService/managedClusters/agentPools.failA2',
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
